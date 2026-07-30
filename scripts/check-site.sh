#!/usr/bin/env bash

set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "${script_dir}/.." && pwd)"
site_output="${repo_root}/_site"

required_files=(
  "index.html"
  "404.html"
  "robots.txt"
  "sitemap.xml"
  "manifest.webmanifest"
  "assets/css/main.css"
  "assets/js/main.js"
  "assets/images/book-cover.webp"
  "assets/images/og-card.png"
  "downloads/sat-book.pdf"
  "downloads/sat-book-v1.0.0.pdf"
  "downloads/SHA256SUMS"
  ".nojekyll"
)

for relative_path in "${required_files[@]}"; do
  if [[ ! -e "${site_output}/${relative_path}" ]]; then
    printf 'Missing site output: %s\n' "${relative_path}" >&2
    exit 1
  fi
done

python3 "${script_dir}/check-site.py" "${site_output}"
"${script_dir}/check-pdf.sh" "${site_output}/downloads/sat-book.pdf"

if command -v rg >/dev/null 2>&1; then
  if rg -n 'href="/(?!satlab)|src="/(?!satlab)' "${site_output}" --glob '*.html' --pcre2; then
    printf '%s\n' 'Found a root-relative link outside /satlab/.' >&2
    exit 1
  fi
  if rg -n '\{\{[^}]+\}\}|TODO|PLACEHOLDER' "${site_output}" --glob '*.html' --glob '*.css' --glob '*.js'; then
    printf '%s\n' 'Found an unresolved site placeholder.' >&2
    exit 1
  fi
else
  python3 -c "
import sys, re, glob, os
site = sys.argv[1]
for root, dirs, files in os.walk(site):
    for f in files:
        if f.endswith(('.html', '.css', '.js')):
            p = os.path.join(root, f)
            content = open(p, encoding='utf-8').read()
            if f.endswith('.html'):
                if re.search(r'href=\"/(?!satlab)|src=\"/(?!satlab)', content):
                    print(f'Root relative link outside /satlab/ in {p}')
                    sys.exit(1)
            if re.search(r'\{\{[^}]+\}\}|TODO|PLACEHOLDER', content):
                print(f'Placeholder found in {p}')
                sys.exit(1)
" "${site_output}"
fi

printf '%s\n' 'Static site validation completed successfully.'
