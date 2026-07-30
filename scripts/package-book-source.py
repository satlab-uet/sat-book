#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT_SOURCE_FILES = (
    "main.tex",
    "satbook.sty",
    "vietnamese.lbx",
    "references.bib",
    "README.md",
)


def source_files(repo_root: Path) -> list[Path]:
    book_dir = repo_root / "book"
    files = [book_dir / name for name in ROOT_SOURCE_FILES]
    files.extend(sorted((book_dir / "chapters").glob("*.tex")))

    missing = [path for path in files if not path.is_file()]
    if missing:
        formatted = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing book source files: {formatted}")
    return files


def zip_timestamp() -> tuple[int, int, int, int, int, int]:
    epoch_text = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch_text and epoch_text.isdigit():
        timestamp = datetime.fromtimestamp(int(epoch_text), tz=timezone.utc)
    else:
        timestamp = datetime(2026, 7, 30, tzinfo=timezone.utc)

    # ZIP timestamps cannot represent years before 1980.
    year = max(timestamp.year, 1980)
    return (
        year,
        timestamp.month,
        timestamp.day,
        timestamp.hour,
        timestamp.minute,
        timestamp.second,
    )


def build_archive(repo_root: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = zip_timestamp()

    with zipfile.ZipFile(
        output_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for source_path in source_files(repo_root):
            relative_path = source_path.relative_to(repo_root)
            archive_path = Path("sat-book-source") / relative_path
            entry = zipfile.ZipInfo(archive_path.as_posix(), date_time=timestamp)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, source_path.read_bytes())

        for repository_file in ("CITATION.cff", "LICENSE"):
            source_path = repo_root / repository_file
            if not source_path.is_file():
                continue
            archive_path = Path("sat-book-source") / repository_file
            entry = zipfile.ZipInfo(archive_path.as_posix(), date_time=timestamp)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, source_path.read_bytes())


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    default_output = repo_root / "_site" / "downloads" / "sat-book-tex.zip"
    output_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_output

    try:
        build_archive(repo_root, output_path)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    print(f"Packaged current LaTeX source: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
