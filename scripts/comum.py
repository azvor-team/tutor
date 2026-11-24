# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Funções comuns: caminhos, configuração do projeto e assinatura do produto."""
import copy
import json
import os
import sys

try:
    import yaml
except ImportError:  # o container sempre tem pyyaml; fora dele, só JSON
    yaml = None

PROJ = os.environ.get("TUTOR_PROJ", "/work")
SKILL = os.environ.get("TUTOR_SKILL", "/skill")
SEGREDOS = os.environ.get("TUTOR_SEGREDOS", "/run/segredos")

_A = "QVpWVC1UVVRPUi05QzQx"  # identificador de procedência
AZVOR = {
    "produto": "Tutor™ by Azvor",
    "versao": "1.0.0",
    "licenca": "AZVOR-NR-1.0",
    "site": "https://azvor.com.br",
    "contato": "elias.macedo@azvor.com.br",
    "id": __import__("base64").b64decode(_A).decode(),
}

PADRAO = {
    "projeto": "tutorial",
    "sistema": {"url": "", "rotas": [], "pronto_padrao": None},
    "sessao": {"tipo": "nenhum", "arquivo": "sessao.json"},
    "seguranca": {
        "bloquear_escrita": True,
        "permitir": ["/auth/refresh", "/token/refresh"],
        "botoes_proibidos": ["Enviar", "Publicar", "Salvar", "Confirmar", "Ativar", "Excluir",
                             "Apagar", "Disparar", "Pagar", "Finalizar", "Assumir", "Aprovar"],
    },
    "privacidade": {"rotas": [], "chaves_nome": [], "mascarar_telefones": True, "cache_rotas": []},
    "video": {
        "escala": 1.25, "largura": 1920, "altura": 1080, "fps": 30,
        "cor_destaque": "#1D4E9E",
        "lead": 0.6, "tail": 0.9, "transicao": 0.4,
        "intro": {"ativa": True, "titulo": "", "subtitulo": "", "logo": "", "cor": "#1D4E9E", "duracao": 5.2},
        "assinatura": {"logo": "", "altura": 54, "opacidade": 0.92, "posicao": "inferior_direito", "margem": 36},
        "cartela": {"ativa": True, "duracao": 3.4},
        "legendas": "arquivo",   # nenhum | arquivo | faixa
        "crf": 18,
    },
    "narracao": {
        "voz": "", "modelo": "eleven_v4", "idioma": "pt", "formato": "mp3_44100_128",
        "estabilidade": 0.5, "similaridade": 0.8, "estilo": 0.15, "velocidade": 1.0,
        "grafia_fonetica": {},
    },
}


def _mesclar(base, extra):
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _mesclar(out[k], v)
        else:
            out[k] = v
    return out


def carregar_config(caminho=None):
    caminho = caminho or next((os.path.join(PROJ, n) for n in ("tutor.config.yaml", "tutor.config.yml", "tutor.config.json")
                               if os.path.exists(os.path.join(PROJ, n))), None)
    if not caminho:
        sys.exit("tutor.config.yaml não encontrado em %s" % PROJ)
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f) if caminho.endswith(".json") else yaml.safe_load(f)
    return _mesclar(PADRAO, dados)


def ler_json(nome, padrao=None):
    p = nome if os.path.isabs(nome) else os.path.join(PROJ, nome)
    if not os.path.exists(p):
        return padrao
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def gravar_json(nome, dados):
    p = nome if os.path.isabs(nome) else os.path.join(PROJ, nome)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(dados, dict):
        dados = {"_gerado_por": "%s %s" % (AZVOR["produto"], AZVOR["versao"]), **dados}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return p


def carregar_roteiro():
    r = ler_json("roteiro.json")
    if not r:
        sys.exit("roteiro.json não encontrado em %s" % PROJ)
    return r


def cenas_com_fala(roteiro):
    return [c for c in roteiro["cenas"] if c.get("fala")]


def filtro_cenas(arg):
    return set(x.strip() for x in arg.split(",") if x.strip()) if arg else set()


def chave_elevenlabs():
    p = os.path.join(SEGREDOS, "elevenlabs.key")
    if not os.path.exists(p):
        sys.exit("Chave da ElevenLabs não encontrada (%s). Use scripts/vps/enviar_segredo.sh." % p)
    return open(p).read().strip()


def banner(etapa):
    print("▸ %s · %s · %s" % (AZVOR["produto"], etapa, AZVOR["site"]), flush=True)
