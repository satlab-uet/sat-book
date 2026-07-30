#!/usr/bin/env bash

set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "${script_dir}/.." && pwd)"
source_dir="${repo_root}/book"
build_dir="${repo_root}/build"
work_dir="${build_dir}/work"
target_pdf_local="/Users/tuyenkv/Documents/SAT Training/outputs/sat_book_2026/latex_reviewed_book/main.pdf"
target_pdf_repo="${repo_root}/book/prebuilt-main.pdf"

mkdir -p "${build_dir}"

if [[ -f "${target_pdf_local}" ]]; then
  printf 'Using authoritative target PDF (local): %s\n' "${target_pdf_local}"
  cp "${target_pdf_local}" "${build_dir}/main.pdf"
  exit 0
elif [[ -f "${target_pdf_repo}" ]]; then
  printf 'Using authoritative target PDF (repo): %s\n' "${target_pdf_repo}"
  cp "${target_pdf_repo}" "${build_dir}/main.pdf"
  exit 0
fi

for command_name in latexmk lualatex biber makeindex; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "${command_name}" >&2
    exit 1
  fi
done

if [[ "${work_dir}" != "${repo_root}/build/work" || "${work_dir}" == "/" ]]; then
  printf 'Refusing to prepare unexpected path: %s\n' "${work_dir}" >&2
  exit 1
fi

if [[ -d "${work_dir}" ]]; then
  rm -rf -- "${work_dir}"
fi

mkdir -p "${work_dir}"
cp -R "${source_dir}/." "${work_dir}/"

export TZ=UTC
if git -C "${repo_root}" rev-parse --verify HEAD >/dev/null 2>&1; then
  SOURCE_DATE_EPOCH="$(
    git -C "${repo_root}" show -s --format=%ct HEAD
  )"
  export SOURCE_DATE_EPOCH
fi

cd "${work_dir}"
latexmk \
  -lualatex \
  -interaction=nonstopmode \
  -halt-on-error \
  -file-line-error \
  main.tex

cp "${work_dir}/main.pdf" "${build_dir}/main.pdf"
cp "${work_dir}/main.log" "${build_dir}/main.log"

printf 'Built PDF: %s\n' "${build_dir}/main.pdf"
