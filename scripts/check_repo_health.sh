#!/usr/bin/env bash
set -euo pipefail

# リポジトリ直下で実行されても、scripts配下で実行されても動くようにする
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required_files=(
  "guideline.md"
  "progress_log.md"
  "idea_note.md"
  "coding-style.md"
)

recommended_files=(
  "README.md"
)

missing_required=0

echo "== Required files =="
for f in "${required_files[@]}"; do
  if [ -f "$f" ]; then
    echo "OK: $f"
  else
    echo "MISSING: $f"
    missing_required=1
  fi
done

echo
echo "== Recommended files =="
for f in "${recommended_files[@]}"; do
  if [ -f "$f" ]; then
    echo "OK: $f"
  else
    echo "WARN: $f (recommended)"
  fi
done

echo
if [ "$missing_required" -ne 0 ]; then
  echo "Result: NG (required files missing)"
  exit 1
else
  echo "Result: OK"
fi
