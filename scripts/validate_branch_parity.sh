#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

if (( $# > 0 )); then
  refs=("$@")
else
  refs=(origin/16.0 origin/17.0 origin/18.0 origin/19.0 HEAD)
fi

base_ref="${refs[0]}"
git rev-parse --verify "$base_ref^{commit}" >/dev/null

for candidate_ref in "${refs[@]:1}"; do
  git rev-parse --verify "$candidate_ref^{commit}" >/dev/null
  git diff --exit-code "$base_ref" "$candidate_ref" -- \
    . ':(exclude)insitu_sales_connector/__manifest__.py'
done

echo "validated maintained branch parity across: ${refs[*]}"
