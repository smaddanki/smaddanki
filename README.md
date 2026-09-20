# smaddanki.com

Hugo static site, deployed to Vercel. Built from the spec in
[smaddanki-build-spec.md](smaddanki-build-spec.md).

There is no Hugo theme, no module and no submodule. `layouts/` and `assets/` are
this repo's own code.

## Running locally

```sh
brew install hugo          # 0.166.0, pinned in vercel.json
python3 -m pip install -r requirements.txt
python3 scripts/validate.py && hugo server
```

## Writing

Articles are markdown in `content/writing/`, one file per piece, regardless of
type. The filename becomes the slug and **must not change after publication** —
a rename needs a 301 in `vercel.json`.

Required front matter: `title`, `h1`, `definition`, `date`, `lastReviewed`,
`type`, `pillar`, `summary`. `type` is one of `perspective`, `blueprint`, `lab`.
`pillar` is exactly one of the five slugs. Lab pieces also need a `lab:` block.

## Validation

`scripts/validate.py` runs before every build, locally and on Vercel. It fails
the build on missing required front matter and on any tag absent from
`data/tags.yaml`. It also writes `content/tags/<tag>/_index.md` for each tag,
marking tags below three published articles as `render: never` so they produce
no page.

Tag counts, for checking the promotion threshold:

```sh
python3 scripts/validate.py --report
```

## Editing definitions

Owned-term wording lives only in `data/definitions.yaml`. Both `/definitions/`
and the inline `{{< definition >}}` shortcode read from it, so the sentence is
identical everywhere.
