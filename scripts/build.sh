#!/usr/bin/env sh
# Vercel build. Production builds use the baseURL in config/production/hugo.toml;
# preview and development builds use the deployment's own URL, so links inside a
# preview stay inside that preview instead of pointing at the live domain.
set -e

pip3 install --quiet --disable-pip-version-check --break-system-packages -r scripts/requirements.txt \
  || pip3 install --quiet --disable-pip-version-check -r scripts/requirements.txt

python3 scripts/validate.py

if [ "$VERCEL_ENV" = "production" ] || [ -z "$VERCEL_URL" ]; then
  hugo --minify --gc
else
  hugo --minify --gc --baseURL "https://$VERCEL_URL/"
fi
