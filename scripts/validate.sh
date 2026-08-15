#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
module_dir="$repo_dir/insitu_sales_connector"

python3 "$repo_dir/scripts/validate_module.py" "$module_dir"
