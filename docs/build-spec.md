# Build spec — smaddanki.com

For Claude Code. Build a Hugo static site, deployed to Vercel.

## Non-negotiables

- Hugo, built on **Doks** (`@thulite/doks-core`), installed from npm and mounted through Hugo modules. Doks is a real upstream dependency: it is pinned in `package.json` and updated deliberately, not vendored.
- Our own code lives under `src/` — `src/layouts/`, `src/assets/`, `src/config/`, `src/content/`, `src/data/`, `src/static/` — wired up through the mounts in `src/config/_default/module.toml`. Hugo needs `--configDir src/config`; use the npm scripts. Never edit anything under `node_modules/`; override it at the same path under `src/layouts/`.
- Every page statically generated. No client-side fetching of *content*. Doks' FlexSearch index is the one exception, and it is generated at build time.
- Keep JavaScript to what Doks ships, the citation copy button, and the filters on `/writing/`. Every one of those degrades to working HTML. Do not add more.
- Content is markdown in `src/content/`. Front matter is the only metadata source.
- Slugs never change after publication. Any change requires a redirect entry.
- Do not add: comments, tag clouds, related-post algorithms, share buttons, view counters, cover images, pagination on category pages.
- Site search comes with Doks and is kept. The home page is an archive for now; there is no About page.

## URL structure

```
/                               home
/writing/                       index of the categories
/writing/<slug>/                every article, all three types
/labs/                          index of type: lab (links to canonical /writing/ URLs)
/library/                       library index
/library/<slug>/                library artefact pages
/definitions/                   three owned terms, each with a stable anchor
/subscribe/                     email capture
/corrections/                   corrections log
/categories/                    category index
/categories/<slug>/             one page per category
```

Categories live under `/categories/`. Implement as a `category` taxonomy; the term pages under `src/content/categories/` are the single source of valid slugs, and validation reads that directory. Articles live under `/writing/` regardless of type; `/labs/` is an index only, never a second canonical URL.

## Front matter schema

Every article:

```yaml
title:          # conversational, used in nav and cards
h1:             # full sentence, search-bearing, may differ from title
definition:     # ONE sentence, no preamble. Rendered directly under the h1.
date:
lastReviewed:   # separate from date
type:           # perspective | blueprint | lab
categories:     # exactly one slug, must have a page under src/content/categories/
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

Fail the build if `h1`, `definition`, `type` or `categories` is missing on an article. A missing definition sentence is the single most costly omission on this site.

## Tags

Tags are a controlled vocabulary, not free text. Hold the list in `src/data/tags.yaml` with a display name and one-line description per tag. **Fail the build on any tag not in that file** — typos and near-duplicates (`mcp` / `MCP` / `mcp-servers`) are the failure mode this prevents.

Tags are orthogonal to categories by design. No tag may map one-to-one onto a category. They exist to detect an emerging sixth section: when a tag reaches roughly fifteen articles with a distinct reader, it becomes a candidate for promotion.

Starting list:

```
semantic-layer        metric-definitions    ml-models         feature-store
mcp                   tool-design           skills            personas
evaluation            drift                 lineage           delegated-identity
audit-evidence        cost-attribution      financial-services
```

Rendering rules:

- A tag page renders only once the tag holds **three or more** published articles. Below that the tag is recorded in front matter but produces no page, and the tag is shown as plain text rather than a link. This avoids near-empty index pages.
- Tag pages are reverse-chronological. They are utility pages, unlike category pages.
- Tags appear at the foot of articles and on category pages. **Never in the navigation.**
- Articles carry previous/next links in date order: previous is the older piece, next the newer one.
- Tag pages carry `noindex`. Category pages are the citation targets; tag pages would compete with them for the same content.
- Expose a build-time report of tag counts (`hugo` output or a small script) so the promotion threshold can be checked without counting by hand.

## Layouts

- `single` variants per `type`, selected by Hugo's type lookup (`src/layouts/perspective/`, `src/layouts/blueprint/`, `src/layouts/lab/`), all rendering one shared `_partials/article.html`: perspective (single column, no TOC), blueprint (Doks' sticky desktop TOC and collapsible mobile TOC, numbered H2s), lab (methodology block above the fold, results before method).
- Category term pages: definition at top, then articles grouped under sub-headings defined in the term's `_index.md` front matter. Explicitly not reverse-chronological and not paginated.
- `/writing/` index: every published article, most recent first, with dropdown filters for type, category and tag across the top. The dropdowns are `<details>`, so they open without JavaScript, and every item is a real link to the page showing the same subset; the script narrows the list in place and keeps `?type=`, `?category=` and `?tag=` in the URL so a filtered view can be shared.
- `/labs/`: a simple index.
- `/library/`: a directory. Kind filters across the top, then a card grid grouped by kind. Kinds, their order, icon and colour live in `src/data/library.yaml`, which also drives validation. Cards use Doks' `.card` and `.card-icon`, so only the filters and grid are ours.
- Home: the ten most recent articles, most recent first, then a link through to `/writing/`. Subscribe lives in the navbar, not on the page. No visible page header — the site name is in the navbar, and the h1 is present but visually hidden. The positioning-statement home page arrives with the visual design.

## Shortcodes

Build these before writing any content, even as unstyled placeholders:

- `cite` — citation block: the prose form, then BibTeX with a copy button (the one permitted piece of JS). Both built from front matter plus the canonical URL. The BibTeX key defaults to surname + year + first word of the slug; override with `citeKey` in front matter.
- `methodology` — renders the `lab` front matter block.
- `reviewed` — renders `lastReviewed` with a changelog disclosure.
- `definition` — the owned-term definition, used on `/definitions/` and inline on first use in an article. Wording must come from one source file so it is identical everywhere.
- `correction` — inline notice on a corrected article, also fed to `/corrections/`.
- `figure` — SVG diagram with caption, permalink anchor and download link.
- `subscribe` — email capture form. Posts directly to the ESP's public endpoint. No secrets in the repo.

## SEO and GEO

- Canonical URL on every page. `metaDataBase`-equivalent via `baseURL`.
- Meta description comes from the page's own `definition` sentence, falling back to `summary` and then the site description. No page ships an empty or duplicated one.
- JSON-LD via `@thulite/seo`, extended in `src/layouts/_partials/head/custom-head.html` where it falls short: Article (headline, author, datePublished, dateModified), Person, Organization, with `sameAs` to the LinkedIn profile. One name, one bio across everything.
- `robots.txt` explicitly allowing GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Bingbot.
- `sitemap.xml`, and RSS as **full text**, not summaries, at `/feed.xml`.
- `llms.txt` listing category and definition pages.
- `dateModified` emitted from `lastReviewed`, not from file mtime.
- Preview deploys must emit `noindex`. Gate on Vercel's environment variable.
- The `*.vercel.app` production alias 301s to smaddanki.com.

## Performance and accessibility

- Self-hosted fonts, subset, `font-display: swap`. No external font requests. Satisfied by Doks, which bundles Jost as woff2; verified no external font requests in the build.
- Green Core Web Vitals on mobile.
- Tables and code blocks scroll inside their own container; the page body never scrolls sideways.
- Light, dark and auto via Doks' colour-mode toggle (`params.doks.colorMode`).
- Headings in document order, real contrast ratios, keyboard navigable.

## Vercel

- Pin `HUGO_VERSION` as an environment variable. Do not rely on Vercel's default. Node is pinned to 24 in `.nvmrc` and `package.json` engines; Doks requires it.
- Install `npm install`; build `python3 scripts/validate.py && npm run build`; output `public`.
- Commit a `vercel.json` holding redirects. Every retired slug gets a 301.

## Navigation

Primary: Writing · Labs · Library, plus Subscribe as a visually distinct control in the navbar, next to the colour-mode toggle. It uses Doks' built-in `navBarButton` rather than an override of its 250-line header partial, and links to `/subscribe/`, which carries the form.

Footer: Categories, Definitions, Corrections, RSS, privacy notice, and "Smaddanki LTD" as the legal entity.

## Build order

1. Site skeleton and config. Install Doks, merge our config into `config/_default/`.
2. Content types, `data/tags.yaml`, front matter and tag validation.
3. All eight shortcodes as working placeholders.
4. Blueprint single layout. Everything else inherits from it.
5. Perspective and Lab layouts.
6. Pillar term pages and `/writing/`.
7. Home, About, Definitions.
8. SEO partials, robots, sitemap, RSS, llms.txt.
9. `/labs/`, `/library/`, `/corrections/`, tag pages.

Styling stays close to Doks' defaults at this stage. Visual design arrives separately; customisation goes in `src/assets/scss/common/_variables-custom.scss` and `_custom.scss` so Doks can be upgraded without conflict.

## Acceptance

- Three sample articles, one per type, render correctly.
- Build fails when a required front matter field is missing.
- Build fails on a tag absent from `src/data/tags.yaml`.
- A tag with fewer than three articles produces no page and renders as plain text.
- RSS validates and carries full text.
- Structured data passes a rich-results test.
- Canonical tags correct on three sampled pages; tag pages carry `noindex`.
- Lighthouse mobile: performance and accessibility both green.
- `npm update` to a new Doks minor version does not break the build.
