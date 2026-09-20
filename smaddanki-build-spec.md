# Build spec — smaddanki.com

For Claude Code. Build a Hugo static site, deployed to Vercel.

## Non-negotiables

- Hugo, `hugo new site`. No Hugo Modules, no git submodules, no installed theme.
- Start from **hugo-paper** as a source of typography and base CSS only: copy its `layouts/` and `assets/` into this repo, delete what is unused, and treat the result as our own code. There is no parent theme and no upstream to sync. Do not use `theme = "paper"` in config.
- Every page statically generated. No client-side fetching of content.
- No JavaScript except where interaction genuinely requires it. Target zero JS on article pages.
- Content is markdown in `content/`. Front matter is the only metadata source.
- Slugs never change after publication. Any change requires a redirect entry.
- Do not add: site search, comments, tag clouds, related-post algorithms, share buttons, view counters, cover images, an archive page, pagination on pillar pages.

## URL structure

```
/                               home
/writing/                       index of the five pillars
/writing/<slug>/                every article, all three types
/labs/                          index of type: lab (links to canonical /writing/ URLs)
/library/                       library index
/library/<slug>/                library artefact pages
/definitions/                   three owned terms, each with a stable anchor
/what-you-show-the-auditor/     aggregate of every auditor block
/corrections/                   corrections log
/about/
/agent-data-layer/              pillar
/silent-failure-problem/        pillar
/agent-risk-and-controls/       pillar
/real-tco-of-agents/            pillar
/changing-data-function/        pillar
```

Pillar pages sit at the root. Implement as a `pillar` taxonomy with a `url:` override in each term's `_index.md`. Articles live under `/writing/` regardless of type; `/labs/` is an index only, never a second canonical URL.

## Front matter schema

Every article:

```yaml
title:          # conversational, used in nav and cards
h1:             # full sentence, search-bearing, may differ from title
definition:     # ONE sentence, no preamble. Rendered directly under the h1.
date:
lastReviewed:   # separate from date
type:           # perspective | blueprint | lab
pillar:         # one of the five slugs, exactly one
tags: []        # zero or more, from the controlled list below
summary:        # for cards and meta description
draft:
```

Lab pieces add:

```yaml
lab:
  runDate:
  models: []        # names and versions
  schemaVersion:
  harness:          # repo URL
```

Library artefacts add:

```yaml
library:
  kind:             # tool | mcp | skill | persona
  version:
  checkedAgainst:   # e.g. "MCP spec 2026-06-18, schema v2"
  repo:
```

Fail the build if `h1`, `definition`, `type` or `pillar` is missing on an article. A missing definition sentence is the single most costly omission on this site.

## Tags

Tags are a controlled vocabulary, not free text. Hold the list in `data/tags.yaml` with a display name and one-line description per tag. **Fail the build on any tag not in that file** — typos and near-duplicates (`mcp` / `MCP` / `mcp-servers`) are the failure mode this prevents.

Tags are orthogonal to pillars by design. No tag may map one-to-one onto a pillar. They exist to detect an emerging sixth section: when a tag reaches roughly fifteen articles with a distinct reader, it becomes a candidate for promotion.

Starting list:

```
semantic-layer        metric-definitions    ml-models         feature-store
mcp                   tool-design           skills            personas
evaluation            drift                 lineage           delegated-identity
audit-evidence        cost-attribution      financial-services
```

Rendering rules:

- A tag page renders only once the tag holds **three or more** published articles. Below that the tag is recorded in front matter but produces no page, and the tag is shown as plain text rather than a link. This avoids near-empty index pages.
- Tag pages are reverse-chronological. They are utility pages, unlike pillar pages.
- Tags appear at the foot of articles and on pillar pages. **Never in the navigation.**
- Tag pages carry `noindex`. Pillar pages are the citation targets; tag pages would compete with them for the same content.
- Expose a build-time report of tag counts (`hugo` output or a small script) so the promotion threshold can be checked without counting by hand.

## Layouts

- `single` variants per `type` via `layouts/writing/`: perspective (single column, no TOC), blueprint (sticky TOC desktop, collapsible mobile, numbered H2s), lab (methodology block above the fold, results before method).
- Pillar term pages: definition at top, then articles grouped under sub-headings defined in the term's `_index.md` front matter. Explicitly not reverse-chronological and not paginated.
- `/writing/` index: the five pillars, each with its question and definition. Not a feed.
- `/labs/` and `/library/`: simple indexes.
- Home: positioning statement, five pillars with questions, three recent pieces, subscribe.

## Shortcodes

Build these before writing any content, even as unstyled placeholders:

- `auditor` — the recurring Blueprint end block. Renders with a stable `id` so it can be deep-linked and aggregated.
- `cite` — pre-formatted citation from front matter plus canonical URL, with a copy button (the one permitted piece of JS).
- `methodology` — renders the `lab` front matter block.
- `reviewed` — renders `lastReviewed` with a changelog disclosure.
- `definition` — the owned-term definition, used on `/definitions/` and inline on first use in an article. Wording must come from one source file so it is identical everywhere.
- `correction` — inline notice on a corrected article, also fed to `/corrections/`.
- `figure` — SVG diagram with caption, permalink anchor and download link.
- `subscribe` — email capture form. Posts directly to the ESP's public endpoint. No secrets in the repo.

`/what-you-show-the-auditor/` is generated by collecting every page containing the `auditor` shortcode.

## SEO and GEO

- Canonical URL on every page. `metaDataBase`-equivalent via `baseURL`.
- JSON-LD in `layouts/partials/`: Article (headline, author, datePublished, dateModified), Person, Organization, with `sameAs` to the LinkedIn profile. One name, one bio across everything.
- `robots.txt` explicitly allowing GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Bingbot.
- `sitemap.xml`, and RSS as **full text**, not summaries, at `/feed.xml`.
- `llms.txt` listing pillar and definition pages.
- `dateModified` emitted from `lastReviewed`, not from file mtime.
- Preview deploys must emit `noindex`. Gate on Vercel's environment variable.
- The `*.vercel.app` production alias 301s to smaddanki.com.

## Performance and accessibility

- Self-hosted fonts, subset, `font-display: swap`. No external font requests.
- Green Core Web Vitals on mobile.
- Tables and code blocks scroll inside their own container; the page body never scrolls sideways.
- Light and dark mode via `prefers-color-scheme`, with an explicit background on body.
- Headings in document order, real contrast ratios, keyboard navigable.

## Vercel

- Pin `HUGO_VERSION` as an environment variable. Do not rely on Vercel's default.
- Build command `hugo --minify`, output `public`.
- Commit a `vercel.json` holding redirects. Every retired slug gets a 301.

## Navigation

Primary: Writing · Labs · Library, plus Subscribe as a visually distinct control.

Footer: all five pillars by name, Definitions, the auditor index, Corrections, RSS, privacy notice, and "Smaddanki LTD" as the legal entity.

## Build order

1. Site skeleton and config. Vendor hugo-paper's layouts and assets, strip what is unused.
2. Content types, `data/tags.yaml`, front matter and tag validation.
3. All eight shortcodes as working placeholders.
4. Blueprint single layout. Everything else inherits from it.
5. Perspective and Lab layouts.
6. Pillar term pages and `/writing/`.
7. Home, About, Definitions.
8. SEO partials, robots, sitemap, RSS, llms.txt.
9. `/labs/`, `/library/`, `/corrections/`, `/what-you-show-the-auditor/`, tag pages.

Styling stays close to Paper's defaults at this stage. Visual design arrives separately; build the structure so a stylesheet can be replaced without touching layouts.

## Acceptance

- Three sample articles, one per type, render correctly.
- Build fails when a required front matter field is missing.
- Build fails on a tag absent from `data/tags.yaml`.
- A tag with fewer than three articles produces no page and renders as plain text.
- RSS validates and carries full text.
- Structured data passes a rich-results test.
- Canonical tags correct on three sampled pages; tag pages carry `noindex`.
- No page ships JavaScript other than the copy button.
- Lighthouse mobile: performance and accessibility both green.
- No reference to a parent theme anywhere in config.
