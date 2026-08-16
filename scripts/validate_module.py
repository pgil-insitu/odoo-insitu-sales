#!/usr/bin/env python3
"""Dependency-free structural checks for the Odoo Online data module."""

from __future__ import annotations

import ast
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


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
    if manifest["depends"] != ["base"]:
        fail("Odoo Online launcher must depend only on base")
    if manifest["data"] != ["views/insitu_menus.xml"]:
        fail("data module must load only the launcher actions and menus")

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
    ):
        if required_text not in listing_text:
            fail(f"marketplace description missing: {required_text}")

    required_assets = [
        module_dir / "static" / "description" / "icon.png",
        module_dir / "static" / "description" / "cover.png",
        module_dir / "static" / "description" / "index.html",
    ]
    for path in required_assets:
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"marketplace asset is missing: {path.relative_to(module_dir)}")

    print(
        f"validated {module_dir.name}: Python-free runtime, "
        f"{len(xml_paths)} XML data file, launcher URLs and marketplace "
        "assets present"
    )


if __name__ == "__main__":
    main()
