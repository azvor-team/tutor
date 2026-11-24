#!/usr/bin/env bash
# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Roda na máquina do usuário: só envia arquivos de texto/imagem para a VPS (nada é executado aqui).
#   enviar.sh <ssh_host> <pasta_local_do_projeto> [raiz_remota=/root/tutor]
set -euo pipefail
HOST="${1:?host ssh}"; LOCAL="${2:?pasta do projeto}"; RAIZ="${3:-/root/tutor}"
SKILL="$(cd "$(dirname "$0")/../.." && pwd)"
NOME="$(basename "$LOCAL")"
ssh "$HOST" "mkdir -p '$RAIZ/skill' '$RAIZ/projetos/$NOME' '$RAIZ/segredos' && chmod 700 '$RAIZ' '$RAIZ/segredos'"
rsync -az --delete --exclude '.git' --exclude 'evals' --exclude '*.mp4' "$SKILL/" "$HOST:$RAIZ/skill/"
rsync -az --exclude 'audio' --exclude 'clips' --exclude 'out' --exclude 'qa' --exclude 'descoberta' "$LOCAL/" "$HOST:$RAIZ/projetos/$NOME/"
echo "✓ skill e projeto '$NOME' enviados para $HOST:$RAIZ"
