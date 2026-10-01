#!/usr/bin/env bash
# history-prefix-search uninstaller
# Usage: ./uninstall.sh
set -euo pipefail

START="# >>> history-prefix-search >>>"
END="# <<< history-prefix-search <<<"

remove_block() {
  local file="$1" tmp
  [ -f "$file" ] || return 0
  if ! grep -qF "$START" "$file"; then echo "Nothing to remove in $file"; return 0; fi
  tmp="$(mktemp)"
  awk -v s="$START" -v e="$END" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$file" > "$tmp"
  cat "$tmp" > "$file"; rm -f "$tmp"
  echo "Removed from $file"
}

remove_block "$HOME/.inputrc"
remove_block "$HOME/.zshrc"

echo
echo "Done. Open a NEW terminal. To reset the current one (bash), run:"
echo "  bind '\"\\e[A\": previous-history'; bind '\"\\e[B\": next-history'"
echo "  bind '\"\\eOA\": previous-history'; bind '\"\\eOB\": next-history'"
