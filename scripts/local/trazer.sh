#!/usr/bin/env bash
# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Traz da VPS o vídeo final, as legendas e as imagens de QA.
#   trazer.sh <ssh_host> <projeto> <pasta_destino> [raiz=/root/tutor]
set -euo pipefail
HOST="${1:?host}"; NOME="${2:?projeto}"; DEST="${3:?destino}"; RAIZ="${4:-/root/tutor}"
mkdir -p "$DEST"
rsync -az --include '*.mp4' --include '*.srt' --exclude '_*' "$HOST:$RAIZ/projetos/$NOME/out/" "$DEST/"
rsync -az --include 'folha_*.png' --include 'final.png' --include '*.json' --exclude '*' "$HOST:$RAIZ/projetos/$NOME/qa/" "$DEST/qa/" 2>/dev/null || true
ls -la "$DEST"
