#!/usr/bin/env bash
# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Envia a chave da ElevenLabs para a VPS sem exibi-la (pipe direto, permissão 600).
#   enviar_segredo.sh <ssh_host> <arquivo_com_a_chave> [VARIAVEL=ELEVENLABS_API_KEY] [raiz=/root/tutor]
# O arquivo pode ser um .env (VARIAVEL=valor) ou conter só a chave.
set -euo pipefail
HOST="${1:?host}"; ARQ="${2:?arquivo}"; VAR="${3:-ELEVENLABS_API_KEY}"; RAIZ="${4:-/root/tutor}"
valor() { if grep -q "^$VAR=" "$ARQ"; then grep -E "^$VAR=" "$ARQ" | head -1 | cut -d= -f2-; else head -1 "$ARQ"; fi | tr -d '\r\n"'"'"; }
ssh "$HOST" "mkdir -p '$RAIZ/segredos' && chmod 700 '$RAIZ/segredos' && umask 077 && cat > '$RAIZ/segredos/elevenlabs.key'" < <(valor)
ssh "$HOST" "printf 'chave recebida: %s caracteres\n' \$(wc -c < '$RAIZ/segredos/elevenlabs.key')"
