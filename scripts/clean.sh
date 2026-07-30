#!/usr/bin/env bash

set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "${script_dir}/.." && pwd)"
build_dir="${repo_root}/build"

if [[ "${build_dir}" != "${repo_root}/build" || "${build_dir}" == "/" ]]; then
  printf 'Refusing to clean unexpected path: %s\n' "${build_dir}" >&2
  exit 1
fi

if [[ -d "${build_dir}" ]]; then
  rm -rf -- "${build_dir}"
fi

printf 'Removed generated build directory: %s\n' "${build_dir}"
