#!/usr/bin/env bash

set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(CDPATH= cd -- "${script_dir}/.." && pwd)"
build_dir="${repo_root}/build"
site_dir="${repo_root}/_site"

for generated_dir in "${build_dir}" "${site_dir}"; do
  case "${generated_dir}" in
    "${repo_root}/build"|"${repo_root}/_site")
      ;;
    *)
      printf 'Refusing to clean unexpected path: %s\n' "${generated_dir}" >&2
      exit 1
      ;;
  esac

  if [[ -L "${generated_dir}" ]]; then
    printf 'Refusing to clean a symbolic link: %s\n' "${generated_dir}" >&2
    exit 1
  fi

  if [[ -d "${generated_dir}" ]]; then
    find "${generated_dir}" -mindepth 1 -delete
    rmdir "${generated_dir}"
  elif [[ -e "${generated_dir}" ]]; then
    printf 'Refusing to clean a non-directory path: %s\n' "${generated_dir}" >&2
    exit 1
  fi

  printf 'Removed generated directory: %s\n' "${generated_dir}"
done
