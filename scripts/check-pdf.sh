#!/usr/bin/env bash

set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "${script_dir}/.." && pwd)"
pdf_path="${1:-${repo_root}/build/main.pdf}"
expected_pages="${EXPECTED_PAGES:-106}"
expected_title="Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp"
expected_authors="Tô Văn Khánh; Kiều Văn Tuyên; Trương Xuân Hiếu; Vũ Thanh Hương; Đào Xuân Nghĩa; Nguyễn Kim Trung Đức"

if [[ ! -s "${pdf_path}" ]]; then
  printf 'PDF is missing or empty: %s\n' "${pdf_path}" >&2
  exit 1
fi

for command_name in pdfinfo pdffonts pdftotext; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "${command_name}" >&2
    exit 1
  fi
done

pdf_metadata="$(pdfinfo "${pdf_path}")"
actual_pages="$(
  printf '%s\n' "${pdf_metadata}" |
    awk -F ':' '/^Pages:/ {gsub(/[[:space:]]/, "", $2); print $2}'
)"

if [[ "${actual_pages}" != "${expected_pages}" ]]; then
  printf 'Unexpected page count: expected %s, got %s\n' \
    "${expected_pages}" "${actual_pages}" >&2
  exit 1
fi

if ! printf '%s\n' "${pdf_metadata}" |
  grep -F "Title:           ${expected_title}" >/dev/null; then
  printf 'PDF title metadata does not match the approved title.\n' >&2
  exit 1
fi

if ! printf '%s\n' "${pdf_metadata}" |
  grep -F "Author:          ${expected_authors}" >/dev/null; then
  printf 'PDF author metadata does not match the approved author list.\n' >&2
  exit 1
fi

if ! pdftotext -f 1 -l 1 "${pdf_path}" - |
  grep -F "Biểu diễn SAT tối ưu" >/dev/null; then
  printf 'The approved title was not extractable from the title page.\n' >&2
  exit 1
fi

if ! pdffonts "${pdf_path}" |
  awk '
    NR > 2 && $(NF - 4) != "yes" {
      print "Font is not embedded: " $0 > "/dev/stderr"
      failed = 1
    }
    END { exit failed }
  '; then
  exit 1
fi

log_path="${pdf_path%.pdf}.log"
if [[ -f "${log_path}" ]]; then
  error_pattern='undefined references|undefined citations|Citation .* undefined|There were undefined|Please \\(re\\)run Biber|Empty bibliography|Input index file .* not found|Usage: makeindex|LaTeX Error|Emergency stop|Fatal error'
  if grep -Eiq "${error_pattern}" "${log_path}"; then
    printf 'Build log contains unresolved references, citations, or fatal errors:\n' >&2
    grep -Ein "${error_pattern}" "${log_path}" >&2
    exit 1
  fi
fi

printf 'PDF checks passed: %s pages, approved metadata, extractable text, embedded fonts, no unresolved references/citations or fatal log errors.\n' \
  "${actual_pages}"
