#!/usr/bin/env bash
# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Orquestrador na VPS. Tudo roda dentro do container azvor-tutor:1.
#   pipeline.sh -        setup
#   pipeline.sh <proj>   descobrir|validar|narrar|conferir|gravar|folhas|render|qa|tudo|limpar  [opções]
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$AQUI/../.." && pwd)"
RAIZ="${TUTOR_RAIZ:-$(cd "$SKILL/.." && pwd)}"
IMG="${TUTOR_IMAGEM:-azvor-tutor:1}"
PROJETO="${1:?uso: pipeline.sh <projeto|-> <etapa> [opções]}"
ETAPA="${2:?informe a etapa}"
shift 2
PROJ="$RAIZ/projetos/$PROJETO"

rodar() {
  docker run --rm --init --ipc=host \
    -e TUTOR_PROJ=/work -e TUTOR_SKILL=/skill -e TUTOR_SEGREDOS=/run/segredos \
    -v "$PROJ:/work" -v "$SKILL:/skill:ro" -v "$RAIZ/segredos:/run/segredos:ro" \
    -w /skill/scripts "$IMG" "$@"
}

case "$ETAPA" in
  setup)
    mkdir -p "$RAIZ/projetos" "$RAIZ/segredos" && chmod 700 "$RAIZ" "$RAIZ/segredos"
    docker build -q -t "$IMG" "$SKILL/scripts/vps" >/dev/null
    docker run --rm --init --ipc=host "$IMG" python -c "from playwright.sync_api import sync_playwright as s
with s() as p:
    b = p.chromium.launch(); print('chromium ok', b.version); b.close()"
    echo "✓ Tutor pronto em $RAIZ (imagem $IMG)" ;;
  descobrir) rodar python descoberta/crawler.py "$@" ;;
  validar)   rodar python roteiro/validar_roteiro.py "$@" ;;
  narrar)    rodar python audio/narrar.py "$@" ;;
  conferir)  rodar python audio/conferir.py "$@" ;;
  gravar)    rodar python motor/executar.py "$@" ;;
  folhas)    rodar python render/folhas.py "$@" ;;
  render)    rodar python render/render.py "$@" ;;
  qa)        rodar python render/qa_final.py "$@" ;;
  tudo)
    rodar python roteiro/validar_roteiro.py
    rodar python audio/narrar.py
    rodar python audio/conferir.py
    rodar python motor/executar.py
    rodar python render/folhas.py
    rodar python render/render.py
    rodar python render/qa_final.py ;;
  limpar)
    # apaga sessões e temporários; mantém áudio, clipes e vídeo para regravações rápidas
    for f in "$RAIZ/segredos/sessao.json" "$PROJ/sessao.json"; do [ -f "$f" ] && shred -u "$f"; done
    rm -rf "$PROJ/_intro" "$PROJ/qa/_quadros" "$PROJ/out/_cartela.png"
    echo "✓ sessão e temporários removidos" ;;
  *) echo "etapa desconhecida: $ETAPA" >&2; exit 2 ;;
esac
