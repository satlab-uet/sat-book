#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ElementTree
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.images_without_alt: list[str] = []
        self.h1_count = 0
        self.lang: str | None = None
        self.has_title = False
        self.has_viewport = False
        self.has_description = False
        self.json_ld_documents: list[str] = []
        self._json_ld_chunks: list[str] | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.has_title = True
        if tag == "meta":
            if attributes.get("name") == "viewport":
                self.has_viewport = True
            if attributes.get("name") == "description":
                self.has_description = True
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._json_ld_chunks = []
        if "id" in attributes and attributes["id"]:
            self.ids.append(attributes["id"])
        if tag == "a" and attributes.get("href"):
            self.references.append(("href", attributes["href"]))
        if tag in {"img", "script"} and attributes.get("src"):
            self.references.append(("src", attributes["src"]))
        if tag == "link" and attributes.get("href"):
            self.references.append(("href", attributes["href"]))
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt.append(attributes.get("src", "<unknown>"))

    def handle_data(self, data: str) -> None:
        if self._json_ld_chunks is not None:
            self._json_ld_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_ld_chunks is not None:
            self.json_ld_documents.append("".join(self._json_ld_chunks))
            self._json_ld_chunks = None


def local_target(
    site_root: Path, page_path: Path, reference: str
) -> tuple[Path | None, str | None]:
    split = urlsplit(reference)
    if split.scheme or split.netloc or reference.startswith(("mailto:", "tel:", "data:")):
        return None, None

    fragment = split.fragment or None
    path_text = unquote(split.path)

    if not path_text:
        return page_path, fragment

    if path_text.startswith("/sat-book/"):
        path_text = path_text.removeprefix("/sat-book/")
        target = site_root / path_text
    elif path_text == "/sat-book":
        target = site_root
    elif path_text.startswith("/"):
        return None, fragment
    else:
        target = page_path.parent / path_text

    if target.is_dir():
        target = target / "index.html"
    return target.resolve(), fragment


def main() -> int:
    site_root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    if not site_root.is_dir():
        print(f"Site directory does not exist: {site_root}", file=sys.stderr)
        return 1

    html_files = sorted(site_root.rglob("*.html"))
    if not html_files:
        print("No HTML files found.", file=sys.stderr)
        return 1

    root_index = (site_root / "index.html").resolve()
    parsed_pages: dict[Path, PageParser] = {}
    errors: list[str] = []

    for html_path in html_files:
        parser = PageParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        parsed_pages[html_path.resolve()] = parser

        if parser.lang != "vi":
            errors.append(f"{html_path}: expected html lang='vi'")
        if parser.h1_count != 1:
            errors.append(f"{html_path}: expected one h1, found {parser.h1_count}")
        if not parser.has_title:
            errors.append(f"{html_path}: missing title")
        if not parser.has_viewport:
            errors.append(f"{html_path}: missing viewport metadata")
        if html_path.resolve() == root_index and not parser.has_description:
            errors.append(f"{html_path}: missing description metadata")
        if html_path.resolve() == root_index and not parser.json_ld_documents:
            errors.append(f"{html_path}: missing JSON-LD metadata")
        for index, document in enumerate(parser.json_ld_documents, start=1):
            try:
                json.loads(document)
            except json.JSONDecodeError as error:
                errors.append(
                    f"{html_path}: invalid JSON-LD document {index}: {error}"
                )
        duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicates:
            errors.append(f"{html_path}: duplicate ids: {', '.join(duplicates)}")
        for image in parser.images_without_alt:
            errors.append(f"{html_path}: image without alt: {image}")

    for html_path, parser in parsed_pages.items():
        for attribute, reference in parser.references:
            target, fragment = local_target(site_root, html_path, reference)
            if target is None:
                continue
            if not target.is_relative_to(site_root):
                errors.append(
                    f"{html_path}: local reference escapes site root {reference!r}"
                )
                continue
            if not target.exists():
                errors.append(
                    f"{html_path}: broken {attribute} reference {reference!r}"
                )
                continue
            if fragment and target.suffix == ".html":
                target_parser = parsed_pages.get(target)
                if target_parser and fragment not in target_parser.ids:
                    errors.append(
                        f"{html_path}: missing fragment #{fragment} in {target}"
                    )

    manifest_path = site_root / "manifest.webmanifest"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{manifest_path}: invalid web manifest: {error}")
    else:
        for icon in manifest.get("icons", []):
            reference = icon.get("src")
            if not reference:
                errors.append(f"{manifest_path}: icon is missing src")
                continue
            target, _ = local_target(site_root, site_root / "index.html", reference)
            if target is not None:
                if not target.is_relative_to(site_root):
                    errors.append(
                        f"{manifest_path}: icon escapes site root {reference!r}"
                    )
                elif not target.exists():
                    errors.append(f"{manifest_path}: missing icon {reference!r}")

    sitemap_path = site_root / "sitemap.xml"
    try:
        sitemap = ElementTree.parse(sitemap_path)
    except (OSError, ElementTree.ParseError) as error:
        errors.append(f"{sitemap_path}: invalid sitemap XML: {error}")
    else:
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [
            element.text
            for element in sitemap.findall(".//sm:loc", namespace)
            if element.text
        ]
        expected_location = "https://satlab-uet.github.io/sat-book/"
        if expected_location not in locations:
            errors.append(
                f"{sitemap_path}: missing canonical URL {expected_location}"
            )

    if errors:
        print("Site checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Site checks passed: {len(html_files)} HTML pages, "
        "valid local references, metadata, headings, ids, and image alternatives."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
