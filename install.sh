#!/usr/bin/env bash
# history-prefix-search installer
# Usage: ./install.sh [--bash] [--zsh] [--all]
set -euo pipefail

START="# >>> history-prefix-search >>>"
END="# <<< history-prefix-search <<<"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_block() {
  local file="$1" snippet="$2"
  touch "$file"
  if grep -qF "$START" "$file"; then
    echo "Already installed in $file - skipping."
    return
  fi
  if [ -s "$file" ]; then cp "$file" "$file.hps.bak"; fi
  { printf '\n%s\n' "$START"; cat "$snippet"; printf '%s\n' "$END"; } >> "$file"
  echo "Installed in $file"
}

want_bash=0; want_zsh=0
if [ $# -eq 0 ]; then
  if command -v bash >/dev/null; then want_bash=1; fi
  if command -v zsh  >/dev/null; then want_zsh=1; fi
else
  for arg in "$@"; do
    case "$arg" in
      --bash) want_bash=1 ;;
      --zsh)  want_zsh=1 ;;
      --all)  want_bash=1; want_zsh=1 ;;
      -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
      *) echo "Unknown option: $arg" >&2; exit 1 ;;
    esac
  done
fi

if [ "$want_bash" -eq 1 ]; then install_block "$HOME/.inputrc" "$DIR/bash/inputrc.snippet"; fi
if [ "$want_zsh"  -eq 1 ]; then install_block "$HOME/.zshrc"   "$DIR/zsh/history-prefix-search.zsh"; fi

echo
echo "Done. Open a NEW terminal, type a prefix (e.g. 'su') and press Up."
