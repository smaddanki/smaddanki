# smaddanki.com

A Hugo site built on [Doks](https://doks.thulite.io/), deployed to Vercel.
Built from the spec in [docs/build-spec.md](docs/build-spec.md).

Doks is a real upstream dependency, installed from npm and mounted through Hugo
modules (`src/config/_default/module.toml`). Nothing is vendored. **Never edit
anything under `node_modules/`** — override it instead, by putting a file at the
same path under `src/layouts/`.

## Running locally

Requires Node 24 (Doks' `engines` floor) and Hugo 0.166.

```sh
nvm use                      # reads .nvmrc
brew install hugo
npm install
python3 -m pip install -r scripts/requirements.txt

python3 scripts/validate.py && npm run dev
```

Hugo's config lives at `src/config`, not the default `config`, so every hugo
invocation needs `--configDir src/config`. The npm scripts already pass it —
prefer `npm run dev` and `npm run build` over calling `hugo` directly.

## Layout

The site source lives under `src/`, wired up through the mounts in
`src/config/_default/module.toml`. Only tooling and metadata sit at the root.

```
src/content/writing/      ← articles go here, one file per piece, all three types
src/content/library/      ← library artefacts go here
src/content/categories/   one folder per category; touched only when adding one
src/content/pages/        standalone pages (privacy, definitions, …)
src/data/                 tags.yaml, definitions.yaml, library.yaml
src/archetypes/           front matter templates used by `npm run create`
src/layouts/              our overrides of Doks
src/config/               Hugo config, passed with --configDir
src/generated/tags/       written by validate.py — not authored, do not edit
scripts/                  validate.py, build.sh, requirements.txt
docs/build-spec.md        the spec this site is built from
```

## Where to author

Almost always `src/content/writing/`. Start a piece with:

```sh
npm run create -- writing/my-new-piece.md
```

That fills in the whole front matter schema from `src/archetypes/writing.md`,
with `draft: true`, so nothing publishes until you clear it. A library artefact
is the same with `library/my-thing.md`.

The filename becomes the slug, so name it deliberately — see Writing below.

Two folders exist that are **not** for authoring:

- `src/content/categories/` holds the category pages themselves — each one's
  title and definition. Hugo requires taxonomy term content to live at
  `content/<plural>/<term>/_index.md`, which is why it sits beside `writing/`.
  Add a folder here only when you want a new category; the directory is the
  single source of valid `categories:` values, and the build fails on a slug
  with no page.
- `src/generated/tags/` is written by `scripts/validate.py` on every build. It
  is mounted into the site at `content/tags`, so it is out of the way.

## Writing

The filename becomes the slug and **must not change after publication** — a
rename needs a 301 in `vercel.json`.

Required front matter: `title`, `h1`, `definition`, `date`, `lastReviewed`,
`type`, `categories`, `summary`. `type` is one of `perspective`, `blueprint`, `lab`,
and selects the layout. `categories` takes exactly one slug (Hugo keys taxonomy front matter by the plural name), and it must have a page under `src/content/categories/`. Lab pieces
also need a `lab:` block; library artefacts a `library:` block.

## Validation

`scripts/validate.py` runs before every build, locally and on Vercel. It fails
the build on missing required front matter, on any tag absent from
`src/data/tags.yaml`, and on a `library.kind` absent from `src/data/library.yaml`. It
also writes `src/content/tags/<tag>/_index.md` for each tag, marking tags below
three published articles as `render: never` so they produce no page.

Tag counts, for checking the promotion threshold:

```sh
python3 scripts/validate.py --report
```

## Deploying

Vercel runs `scripts/build.sh`. Production builds use the `baseURL` in
`config/production/hugo.toml`; preview builds use the deployment's own URL, so
links inside a preview stay inside it.

## Still placeholder

- Category definitions, in `src/content/categories/*/_index.md`.
- The three owned terms in `src/data/definitions.yaml`.
- Article bodies, and the four library artefacts.
- `params.linkedin` and `params.subscribeEndpoint` in `src/config/_default/params.toml`.
- The favicon, app icon and `src/static/cover.png` are plain "S" monograms standing
  in for a real mark.
