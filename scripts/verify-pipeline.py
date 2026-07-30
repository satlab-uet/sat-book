#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path


EXPECTED_ARCHIVE_FILES = (
    "book/main.tex",
    "book/satbook.sty",
    "book/vietnamese.lbx",
    "book/references.bib",
    "book/README.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def book_source_digest(repo_root: Path) -> str:
    book_dir = repo_root / "book"
    source_paths = sorted(
        path
        for path in book_dir.rglob("*")
        if path.is_file() and path.suffix in {".tex", ".sty", ".lbx", ".bib"}
    )
    if not source_paths:
        raise FileNotFoundError(f"No LaTeX source found in {book_dir}")

    digest = hashlib.sha256()
    for source_path in source_paths:
        relative_path = source_path.relative_to(repo_root).as_posix()
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def fail(message: str) -> None:
    print(f"[X] {message}", file=sys.stderr)
    raise SystemExit(1)


def verify_pdf_copies(repo_root: Path) -> str:
    build_pdf = repo_root / "build" / "main.pdf"
    download_dir = repo_root / "_site" / "downloads"
    pdf_paths = (
        build_pdf,
        download_dir / "sat-book.pdf",
        download_dir / "sat-book-v1.0.0.pdf",
    )
    for path in pdf_paths:
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"Missing or empty PDF: {path}")

    expected_hash = sha256(build_pdf)
    for path in pdf_paths[1:]:
        if sha256(path) != expected_hash:
            fail(f"Published PDF does not match build output: {path}")
    print(f"[✓] Published PDF copies match build/main.pdf: {expected_hash}")
    return expected_hash


def verify_source_archive(repo_root: Path) -> str:
    archive_path = repo_root / "_site" / "downloads" / "sat-book-tex.zip"
    if not archive_path.is_file() or archive_path.stat().st_size == 0:
        fail(f"Missing or empty LaTeX source archive: {archive_path}")

    expected_files = list(EXPECTED_ARCHIVE_FILES)
    expected_files.extend(
        path.relative_to(repo_root).as_posix()
        for path in sorted((repo_root / "book" / "chapters").glob("*.tex"))
    )

    with zipfile.ZipFile(archive_path) as archive:
        archive_names = set(archive.namelist())
        for relative_path in expected_files:
            archive_name = f"sat-book-source/{relative_path}"
            if archive_name not in archive_names:
                fail(f"Source archive is missing {relative_path}")
            if archive.read(archive_name) != (repo_root / relative_path).read_bytes():
                fail(f"Archived source is stale: {relative_path}")

    archive_hash = sha256(archive_path)
    print(f"[✓] LaTeX archive contains the current repository sources: {archive_hash}")
    return archive_hash


def verify_html_source_digest(repo_root: Path) -> str:
    reader_path = repo_root / "_site" / "read.html"
    if not reader_path.is_file():
        fail(f"Generated HTML reader is missing: {reader_path}")

    html_text = reader_path.read_text(encoding="utf-8")
    match = re.search(
        r'<meta name="sat-book-source-sha256" content="([0-9a-f]{64})">',
        html_text,
    )
    if not match:
        fail("Generated HTML reader has no LaTeX source digest")

    expected_digest = book_source_digest(repo_root)
    if match.group(1) != expected_digest:
        fail("Generated HTML reader does not match the current LaTeX source")

    for chapter_number in range(1, 13):
        if f'id="chap-{chapter_number}"' not in html_text:
            fail(f"Generated HTML reader is missing chapter {chapter_number}")

    print(f"[✓] HTML reader matches the current LaTeX source: {expected_digest}")
    return expected_digest


def verify_checksums(repo_root: Path, expected_hashes: tuple[str, ...]) -> None:
    checksum_path = repo_root / "_site" / "downloads" / "SHA256SUMS"
    if not checksum_path.is_file():
        fail(f"Checksum manifest is missing: {checksum_path}")
    checksum_text = checksum_path.read_text(encoding="utf-8")
    for expected_hash in expected_hashes:
        if expected_hash not in checksum_text:
            fail(f"SHA256SUMS is missing hash {expected_hash}")
    print("[✓] SHA256SUMS covers the current PDF and LaTeX archive.")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    pdf_hash = verify_pdf_copies(repo_root)
    archive_hash = verify_source_archive(repo_root)
    verify_html_source_digest(repo_root)
    verify_checksums(repo_root, (pdf_hash, archive_hash))
    print("End-to-end publication pipeline verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
