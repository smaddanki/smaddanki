#!/usr/bin/env python3
"""Front matter and tag validation, plus tag-page gating.

Runs before `hugo`. Exits non-zero on any violation, so the Vercel build fails
rather than publishing a page with a missing definition sentence.

Also writes content/tags/<tag>/_index.md for every tag in the vocabulary,
marking the ones below the rendering threshold as `render: never` so they
produce no page. Tags below the threshold still render as plain text in
layouts, which read the same threshold from site params.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TAGS_FILE = ROOT / "data" / "tags.yaml"
TAGS_DIR = CONTENT / "tags"

THRESHOLD = 3
TYPES = {"perspective", "blueprint", "lab"}
PILLARS = {
    "agent-data-layer",
    "silent-failure-problem",
    "agent-risk-and-controls",
    "real-tco-of-agents",
    "changing-data-function",
}
REQUIRED = ("h1", "definition", "type", "pillar", "title", "date", "summary")
LIBRARY_KINDS = {"tool", "mcp", "skill", "persona"}

FM = re.compile(r"\A---\n(.*?)\n---\s*\n", re.S)


def front_matter(path):
    m = FM.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    return yaml.safe_load(m.group(1)) or {}


def check_article(path, fm, vocab, errors):
    where = path.relative_to(ROOT)

    for field in REQUIRED:
        if not fm.get(field):
            errors.append(f"{where}: missing required front matter `{field}`")

    if fm.get("definition") and "\n" in str(fm["definition"]).strip():
        errors.append(f"{where}: `definition` must be a single sentence on one line")

    kind = fm.get("type")
    if kind and kind not in TYPES:
        errors.append(f"{where}: type `{kind}` is not one of {sorted(TYPES)}")

    pillar = fm.get("pillar")
    if isinstance(pillar, list):
        errors.append(f"{where}: `pillar` takes exactly one slug, not a list")
    elif pillar and pillar not in PILLARS:
        errors.append(f"{where}: pillar `{pillar}` is not one of {sorted(PILLARS)}")

    if not fm.get("lastReviewed"):
        errors.append(f"{where}: missing `lastReviewed` (dateModified is emitted from it)")

    for tag in fm.get("tags") or []:
        if tag not in vocab:
            errors.append(
                f"{where}: tag `{tag}` is not in data/tags.yaml — "
                "add it there deliberately or fix the typo"
            )

    if kind == "lab":
        lab = fm.get("lab") or {}
        for field in ("runDate", "models", "schemaVersion", "harness"):
            if not lab.get(field):
                errors.append(f"{where}: lab piece missing `lab.{field}`")


def check_library(path, fm, errors):
    where = path.relative_to(ROOT)
    lib = fm.get("library") or {}
    if not lib:
        errors.append(f"{where}: library artefact missing the `library` block")
        return
    for field in ("kind", "version", "checkedAgainst", "repo"):
        if not lib.get(field):
            errors.append(f"{where}: library artefact missing `library.{field}`")
    if lib.get("kind") and lib["kind"] not in LIBRARY_KINDS:
        errors.append(f"{where}: library.kind `{lib['kind']}` is not one of {sorted(LIBRARY_KINDS)}")


def write_tag_pages(vocab, counts):
    """One _index.md per vocabulary tag; below-threshold tags render nothing."""
    TAGS_DIR.mkdir(parents=True, exist_ok=True)
    keep = set()
    for tag, meta in vocab.items():
        count = counts.get(tag, 0)
        rendered = count >= THRESHOLD
        body = {
            "title": meta.get("name", tag),
            "description": meta.get("description", ""),
            "articleCount": count,
        }
        if not rendered:
            body["build"] = {"render": "never", "list": "never"}
        out = TAGS_DIR / tag / "_index.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        text = "---\n" + yaml.safe_dump(body, sort_keys=False) + "---\n"
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            out.write_text(text, encoding="utf-8")
        keep.add(tag)

    for stale in TAGS_DIR.iterdir() if TAGS_DIR.exists() else []:
        if stale.is_dir() and stale.name not in keep:
            for f in sorted(stale.rglob("*"), reverse=True):
                f.unlink() if f.is_file() else f.rmdir()
            stale.rmdir()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print tag counts and exit")
    args = ap.parse_args()

    vocab = yaml.safe_load(TAGS_FILE.read_text(encoding="utf-8")) or {}
    errors = []
    counts = Counter()

    for path in sorted(CONTENT.glob("writing/**/*.md")):
        if path.name == "_index.md":
            continue
        fm = front_matter(path)
        if fm is None:
            errors.append(f"{path.relative_to(ROOT)}: no YAML front matter")
            continue
        if fm.get("draft"):
            continue
        check_article(path, fm, vocab, errors)
        counts.update(fm.get("tags") or [])

    for path in sorted(CONTENT.glob("library/**/*.md")):
        if path.name == "_index.md":
            continue
        fm = front_matter(path)
        if fm is None or fm.get("draft"):
            continue
        check_library(path, fm, errors)

    if args.report:
        width = max((len(t) for t in vocab), default=0)
        print(f"{'tag':<{width}}  count  page")
        for tag in vocab:
            n = counts.get(tag, 0)
            print(f"{tag:<{width}}  {n:>5}  {'yes' if n >= THRESHOLD else 'no'}")
        promote = [t for t, n in counts.items() if n >= 15]
        if promote:
            print("\nAt promotion threshold (~15):", ", ".join(sorted(promote)))
        return 0

    write_tag_pages(vocab, counts)

    if errors:
        print("Content validation failed:\n", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s).", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
