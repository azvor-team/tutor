# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
"""ADAPTADOR DE SESSÃO · exemplo para backends Python (FastAPI/Django) com JWT.

Só use com OK explícito do dono do sistema: gera um token temporário para um usuário
neutro (ex.: "Admin Demo"), sem senha. Rode DENTRO do container da API, na VPS:

  docker exec -i <container_api> python - < sessao_jwt_backend.py > <raiz>/segredos/sessao.json
  chmod 600 <raiz>/segredos/sessao.json

Ajuste os três pontos marcados com AJUSTE. Ao terminar o vídeo: pipeline.sh <proj> limpar.
"""
import asyncio
import json
import uuid

from app.auth import create_access_token, create_refresh_token   # AJUSTE: funções do projeto
from app.db import SessionLocal                                  # AJUSTE: sessão do banco
from app.models import User                                      # AJUSTE: modelo de usuário

USUARIO_ID = "00000000-0000-0000-0000-000000000000"                  # usuário neutro escolhido com o dono
CHAVE_ACCESS, CHAVE_REFRESH = "app_access_token", "app_refresh_token"  # chaves do localStorage do front


async def main():
    async with SessionLocal() as db:
        u = await db.get(User, uuid.UUID(USUARIO_ID))
        print(json.dumps({"localStorage": {CHAVE_ACCESS: create_access_token(user=u), CHAVE_REFRESH: create_refresh_token(user=u)}}))

asyncio.run(main())
