#!/usr/bin/env bash
# Sandbox test: runs install/uninstall in a temporary HOME.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export HOME="$(mktemp -d)"
echo "existing line" > "$HOME/.zshrc"

./install.sh --all >/dev/null
./install.sh --all >/dev/null   # second run must not duplicate
[ "$(grep -c '>>> history-prefix-search' "$HOME/.inputrc")" -eq 1 ] || { echo "FAIL: duplicate (.inputrc)"; exit 1; }
[ "$(grep -c '>>> history-prefix-search' "$HOME/.zshrc")" -eq 1 ]   || { echo "FAIL: duplicate (.zshrc)"; exit 1; }

./uninstall.sh >/dev/null
if grep -q 'history-prefix-search' "$HOME/.inputrc" "$HOME/.zshrc"; then echo "FAIL: not removed"; exit 1; fi
grep -q 'existing line' "$HOME/.zshrc" || { echo "FAIL: user content lost"; exit 1; }
echo "All tests passed."
