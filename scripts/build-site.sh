#!/usr/bin/env bash

set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "${script_dir}/.." && pwd)"
site_source="${repo_root}/site"
site_output="${repo_root}/_site"
pdf_source="${repo_root}/build/main.pdf"
version="1.0.0"

if [[ ! -d "${site_source}" ]]; then
  printf 'Site source directory is missing: %s\n' "${site_source}" >&2
  exit 1
fi

if [[ ! -s "${pdf_source}" ]]; then
  printf 'Built PDF is missing: %s\n' "${pdf_source}" >&2
  printf '%s\n' 'Run make book before building the site.' >&2
  exit 1
fi

# Ensure HTML book edition is generated
python3 "${script_dir}/generate-html-book.py"

if [[ "${site_output}" != "${repo_root}/_site" || "${site_output}" == "/" ]]; then
  printf 'Refusing to prepare unexpected path: %s\n' "${site_output}" >&2
  exit 1
fi

if [[ -L "${site_output}" ]]; then
  printf 'Refusing to replace a symbolic link: %s\n' "${site_output}" >&2
  exit 1
fi

if [[ -d "${site_output}" ]]; then
  find "${site_output}" -mindepth 1 -delete
elif [[ -e "${site_output}" ]]; then
  printf 'Refusing to replace a non-directory path: %s\n' "${site_output}" >&2
  exit 1
fi

mkdir -p "${site_output}/downloads"
cp -R "${site_source}/." "${site_output}/"
cp "${pdf_source}" "${site_output}/downloads/sat-book.pdf"
cp "${pdf_source}" "${site_output}/downloads/sat-book-v${version}.pdf"

(
  cd "${site_output}/downloads"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "sat-book.pdf" "sat-book-v${version}.pdf" > SHA256SUMS
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "sat-book.pdf" "sat-book-v${version}.pdf" > SHA256SUMS
  else
    printf '%s\n' 'Neither sha256sum nor shasum is available.' >&2
    exit 1
  fi
)

: > "${site_output}/.nojekyll"

printf 'Built static site: %s\n' "${site_output}"
