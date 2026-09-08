#!/usr/bin/env sh
#
# Entry point for every check this repository runs, in the order that fails
# fastest. CI calls the same subcommands, so a green build here means a green
# build there.
#
# Usage:  ./check.sh [validate|snippets|catalog|catalog-check|test|typecheck|stats|all]
#
# Requires: python3 with jsonschema. `typecheck` additionally needs `npm ci`.

set -eu

cd "$(dirname "$0")"

validate() {
  echo "==> validating records"
  python3 tools/validate.py
}

snippets() {
  # A snippet that no longer runs is a snippet whose recorded `observed`
  # value can no longer be reproduced, which invalidates its finding.
  echo "==> running every Python snippet"
  for f in snippets/python/*.py; do
    printf '    %s ... ' "$f"
    python3 "$f" >/dev/null
    echo ok
  done
}

catalog() {
  echo "==> rendering docs/CATALOG.md"
  python3 tools/catalog.py
}

catalog_check() {
  echo "==> checking docs/CATALOG.md is current"
  python3 tools/catalog.py --check
}

test_suite() {
  echo "==> running tests"
  python3 -m unittest discover -s tests -q
}

typecheck() {
  echo "==> typechecking snippets under strict"
  npx tsc --noEmit
  echo "    ok"
}

stats() {
  echo "==> dataset composition"
  python3 tools/stats.py
}

case "${1:-all}" in
  validate)      validate ;;
  snippets)      snippets ;;
  catalog)       catalog ;;
  catalog-check) catalog_check ;;
  test)          test_suite ;;
  typecheck)     typecheck ;;
  stats)         stats ;;
  all)           validate; catalog_check; snippets; test_suite; typecheck ;;
  *)
    echo "unknown target: $1" >&2
    echo "usage: $0 [validate|snippets|catalog|catalog-check|test|typecheck|stats|all]" >&2
    exit 2
    ;;
esac
