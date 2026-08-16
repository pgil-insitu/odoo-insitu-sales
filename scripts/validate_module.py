#!/usr/bin/env python3
"""Dependency-free structural checks for the Odoo Online data module."""

from __future__ import annotations

import ast
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_MANIFEST_KEYS = {
    "name",
    "version",
    "depends",
    "data",
    "license",
    "installable",
}
SUPPORTED_ODOO_MAJORS = {"16.0", "17.0", "18.0", "19.0"}
ALLOWED_PYTHON_FILES = {"__init__.py", "__manifest__.py"}
REQUIRED_ACTION_URLS = {
    "https://app.insitusales.com/",
    "https://www.insitusales.com/en/integrations/odoo-integration/",
}
REQUIRED_MANIFEST_IMAGES = {
    "static/description/cover.png",
    "static/description/field-invoice-printing.png",
    "static/description/odoo-installed-app.png",
    "static/description/sync-map.png",
}
FORBIDDEN_DESCRIPTION_TAGS = {"script", "iframe", "object", "embed"}


class DescriptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[tuple[str, str]] = []
        self.links: list[str] = []
        self.forbidden_tags: set[str] = set()
        self.event_attributes: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attrs_by_name = dict(attrs)
        if tag in FORBIDDEN_DESCRIPTION_TAGS:
            self.forbidden_tags.add(tag)
        self.event_attributes.extend(
            name for name, _ in attrs if name.lower().startswith("on")
        )
        if tag == "img":
            self.images.append(
                (attrs_by_name.get("src") or "", attrs_by_name.get("alt") or "")
            )
        if tag == "a":
            self.links.append(attrs_by_name.get("href") or "")


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def main() -> None:
    module_dir = Path(sys.argv[1]).resolve()
    manifest_path = module_dir / "__manifest__.py"
    manifest = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))

    missing_keys = REQUIRED_MANIFEST_KEYS - manifest.keys()
    if missing_keys:
        fail(f"manifest keys missing: {sorted(missing_keys)}")
    manifest_major = ".".join(manifest["version"].split(".")[:2])
    if manifest_major not in SUPPORTED_ODOO_MAJORS:
        fail(
            "manifest version must target a supported Odoo release: "
            + ", ".join(sorted(SUPPORTED_ODOO_MAJORS))
        )
    if len(sys.argv) > 2 and manifest_major != sys.argv[2]:
        fail(
            f"manifest targets Odoo {manifest_major}, expected {sys.argv[2]}"
        )
    if manifest["license"] != "Other OSI approved licence":
        fail("manifest must identify the repository's Apache-2.0 license")
    if manifest.get("support") != "support@insitusales.com":
        fail("manifest support requests must route to support@insitusales.com")
    if manifest["depends"] != ["base"]:
        fail("Odoo Online launcher must depend only on base")
    if manifest["data"] != ["views/insitu_menus.xml"]:
        fail("data module must load only the launcher actions and menus")
    manifest_images = set(manifest.get("images", []))
    if manifest_images != REQUIRED_MANIFEST_IMAGES:
        fail(
            "manifest images must match the maintained Marketplace gallery: "
            + ", ".join(sorted(REQUIRED_MANIFEST_IMAGES))
        )

    for relative_path in manifest["data"]:
        path = module_dir / relative_path
        if not path.is_file():
            fail(f"manifest data file does not exist: {relative_path}")

    xml_paths = sorted(module_dir.rglob("*.xml"))
    for path in xml_paths:
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            fail(f"invalid XML in {path.relative_to(module_dir)}: {exc}")

    python_paths = sorted(module_dir.rglob("*.py"))
    runtime_python_paths = [
        path
        for path in python_paths
        if path.relative_to(module_dir).as_posix() not in ALLOWED_PYTHON_FILES
    ]
    if runtime_python_paths:
        fail(
            "Odoo Online data modules cannot include runtime Python: "
            + ", ".join(
                path.relative_to(module_dir).as_posix()
                for path in runtime_python_paths
            )
        )
    for path in python_paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            fail(f"invalid Python in {path.relative_to(module_dir)}: {exc}")

    if (module_dir / "__init__.py").read_text(encoding="utf-8").strip():
        fail("data-module __init__.py must remain empty")

    menu_path = module_dir / "views" / "insitu_menus.xml"
    menu_text = menu_path.read_text(encoding="utf-8")
    missing_urls = REQUIRED_ACTION_URLS - {
        url for url in REQUIRED_ACTION_URLS if url in menu_text
    }
    if missing_urls:
        fail(f"launcher actions missing URLs: {sorted(missing_urls)}")
    menu_tree = ET.parse(menu_path)
    root_menu = menu_tree.find(".//menuitem[@id='menu_insitu_root']")
    if root_menu is None or root_menu.get("action") != "action_open_insitu_sales":
        fail("top-level inSitu Sales menu must launch the authenticated app")

    listing_text = (
        module_dir / "static" / "description" / "index.html"
    ).read_text(encoding="utf-8")
    for required_text in (
        "Odoo Online compatible",
        "Python-free data module",
        "Integration &gt; Odoo",
        "Username",
        "Password or API key",
        "Database Name",
        "Company",
        "mailto:support@insitusales.com",
        "Email Support",
        "Use a dedicated integration user",
        "The installed module stores no credentials",
    ):
        if required_text not in listing_text:
            fail(f"marketplace description missing: {required_text}")

    description_dir = module_dir / "static" / "description"
    parser = DescriptionParser()
    parser.feed(listing_text)
    if parser.forbidden_tags:
        fail(
            "marketplace description contains forbidden tags: "
            + ", ".join(sorted(parser.forbidden_tags))
        )
    if parser.event_attributes:
        fail(
            "marketplace description contains JavaScript event attributes: "
            + ", ".join(sorted(set(parser.event_attributes)))
        )
    for src, alt in parser.images:
        if not src:
            fail("marketplace description contains an image without src")
        if not alt.strip():
            fail(f"marketplace image is missing alt text: {src}")
        parsed_src = urlparse(src)
        if parsed_src.scheme or parsed_src.netloc or src.startswith("//"):
            fail(f"marketplace image must be packaged locally: {src}")
        image_path = (description_dir / parsed_src.path).resolve()
        if description_dir.resolve() not in image_path.parents:
            fail(f"marketplace image escapes static/description: {src}")
        if not image_path.is_file() or image_path.stat().st_size == 0:
            fail(f"marketplace image is missing: {src}")

    for href in parser.links:
        if not href:
            fail("marketplace description contains a link without href")
        if href.startswith("#") or href.lower().startswith("mailto:"):
            continue
        parsed_href = urlparse(href)
        if parsed_href.scheme or parsed_href.netloc or href.startswith("//"):
            fail(f"marketplace description contains a prohibited external link: {href}")
        link_path = (description_dir / parsed_href.path).resolve()
        if description_dir.resolve() not in link_path.parents:
            fail(f"marketplace link escapes static/description: {href}")
        if not link_path.is_file():
            fail(f"marketplace local link is missing: {href}")

    required_assets = [
        module_dir / "static" / "description" / "icon.png",
        module_dir / "static" / "description" / "cover.png",
        module_dir / "static" / "description" / "index.html",
    ]
    for path in required_assets:
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"marketplace asset is missing: {path.relative_to(module_dir)}")

    for relative_path in manifest_images:
        path = module_dir / relative_path
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"manifest image is missing: {relative_path}")
        if path.suffix.lower() == ".png" and path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"manifest image has a .png extension but is not PNG: {relative_path}")

    repo_dir = module_dir.parent
    for relative_path in (
        "CHANGELOG.md",
        "SECURITY.md",
        "SUPPORT.md",
        "docs/odoo-api-roadmap.md",
    ):
        path = repo_dir / relative_path
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"repository documentation is missing: {relative_path}")

    changelog_text = (repo_dir / "CHANGELOG.md").read_text(encoding="utf-8")
    if manifest["version"] not in changelog_text:
        fail(f"changelog is missing manifest version: {manifest['version']}")

    print(
        f"validated {module_dir.name}: Python-free runtime, "
        f"{len(xml_paths)} XML data file, launcher URLs and marketplace "
        "assets present"
    )


if __name__ == "__main__":
    main()
