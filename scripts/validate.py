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
SRC = ROOT / "src"
CONTENT = SRC / "content"
TAGS_FILE = SRC / "data" / "tags.yaml"
TAGS_DIR = SRC / "generated" / "tags"

THRESHOLD = 3
TYPES = {"perspective", "blueprint", "lab"}
CATEGORIES_DIR = SRC / "content" / "categories"
REQUIRED = ("h1", "definition", "type", "categories", "title", "date", "summary")
LIBRARY_FILE = SRC / "data" / "library.yaml"

FM = re.compile(r"\A---\n(.*?)\n---\s*\n", re.S)


class BadFrontMatter(Exception):
    """Front matter that is not parseable YAML."""


def front_matter(path):
    m = FM.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        # A value holding a colon is the usual cause; report it rather than
        # dumping a traceback on whoever is writing the post.
        raise BadFrontMatter(str(exc).replace("\n", " ")) from None


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

    cats = categories()
    category = fm.get("categories")
    if isinstance(category, list):
        errors.append(f"{where}: `categories` takes exactly one slug, not a list")
    elif category and category not in cats:
        errors.append(
            f"{where}: categories `{category}` has no page under "
            f"src/content/categories/ — known: {sorted(cats)}"
        )

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


def categories():
    """Category slugs, taken from the term pages themselves so there is one source."""
    if not CATEGORIES_DIR.exists():
        return set()
    return {d.name for d in CATEGORIES_DIR.iterdir()
            if d.is_dir() and (d / "_index.md").exists()}


def library_kinds():
    """The kinds declared in data/library.yaml, which also drives /library/."""
    data = yaml.safe_load(LIBRARY_FILE.read_text(encoding="utf-8")) or {}
    return {k["key"] for k in data.get("kinds", [])}


def check_library(path, fm, errors):
    where = path.relative_to(ROOT)
    lib = fm.get("library") or {}
    if not lib:
        errors.append(f"{where}: library artefact missing the `library` block")
        return
    for field in ("kind", "version", "checkedAgainst", "repo"):
        if not lib.get(field):
            errors.append(f"{where}: library artefact missing `library.{field}`")
    kinds = library_kinds()
    if lib.get("kind") and lib["kind"] not in kinds:
        errors.append(f"{where}: library.kind `{lib['kind']}` is not one of {sorted(kinds)}")


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
            # `render: never` suppresses the page; `list: never` would also drop
            # the term from site.Taxonomies, zeroing every count.
            body["build"] = {"render": "never"}
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
        try:
            fm = front_matter(path)
        except BadFrontMatter as exc:
            errors.append(f"{path.relative_to(ROOT)}: front matter is not valid YAML — {exc}")
            continue
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
        try:
            fm = front_matter(path)
        except BadFrontMatter as exc:
            errors.append(f"{path.relative_to(ROOT)}: front matter is not valid YAML — {exc}")
            continue
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
