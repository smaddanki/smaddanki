# smaddanki.com

A Hugo site built on [Doks](https://doks.thulite.io/), deployed to Vercel.
Built from the spec in [smaddanki-build-spec.md](smaddanki-build-spec.md).

Doks is a real upstream dependency, installed from npm and mounted through Hugo
modules (`config/_default/module.toml`). Nothing is vendored. **Never edit
anything under `node_modules/`** — override it instead, by putting a file at the
same path under `layouts/`.

## Running locally

Requires Node 24 (Doks' `engines` floor) and Hugo 0.166.

```sh
nvm use                      # reads .nvmrc
brew install hugo
npm install
python3 -m pip install -r requirements.txt

python3 scripts/validate.py && hugo server
```

## Layout

```
content/writing/      articles, one file per piece, all three types
content/library/      library artefacts
content/pillar/       the five pillar term pages, each with a url: override
data/tags.yaml        controlled tag vocabulary
data/definitions.yaml owned-term wording, the single source
data/library.yaml     artefact kinds, their order, icon and colour
layouts/              our overrides of Doks
scripts/validate.py   front matter and tag validation, run before every build
scripts/build.sh      the Vercel build
```

## Writing

The filename becomes the slug and **must not change after publication** — a
rename needs a 301 in `vercel.json`.

Required front matter: `title`, `h1`, `definition`, `date`, `lastReviewed`,
`type`, `pillar`, `summary`. `type` is one of `perspective`, `blueprint`, `lab`,
and selects the layout. `pillar` is exactly one of the five slugs. Lab pieces
also need a `lab:` block; library artefacts a `library:` block.

## Validation

`scripts/validate.py` runs before every build, locally and on Vercel. It fails
the build on missing required front matter, on any tag absent from
`data/tags.yaml`, and on a `library.kind` absent from `data/library.yaml`. It
also writes `content/tags/<tag>/_index.md` for each tag, marking tags below
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

- Pillar questions and definitions, in `content/pillar/*/_index.md`.
- The three owned terms in `data/definitions.yaml`.
- Article bodies, and the four library artefacts.
- `params.linkedin` and `params.subscribeEndpoint` in `config/_default/params.toml`.
- The favicon, app icon and `static/cover.png` are plain "S" monograms standing
  in for a real mark.
