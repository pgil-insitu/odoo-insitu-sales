#!/usr/bin/env python3
"""Dependency-free structural checks for the Odoo addon."""

from __future__ import annotations

import ast
import csv
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
    for path in python_paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            fail(f"invalid Python in {path.relative_to(module_dir)}: {exc}")

    access_path = module_dir / "security" / "ir.model.access.csv"
    with access_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or any(not row.get("model_id:id") for row in rows):
        fail("access-control CSV is empty or malformed")

    required_assets = [
        module_dir / "static" / "description" / "icon.png",
        module_dir / "static" / "description" / "cover.png",
        module_dir / "static" / "description" / "index.html",
    ]
    for path in required_assets:
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"marketplace asset is missing: {path.relative_to(module_dir)}")

    print(
        f"validated {module_dir.name}: {len(python_paths)} Python files, "
        f"{len(xml_paths)} XML files, {len(rows)} ACL entries, "
        "marketplace assets present"
    )


if __name__ == "__main__":
    main()
