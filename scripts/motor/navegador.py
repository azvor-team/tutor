# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Abre o Chromium da gravação: escala, janela, sessão, bloqueio de escrita, cursor e anonimizador."""
import glob
import json
import os
import re

from playwright.sync_api import sync_playwright  # noqa: F401  (reexportado)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import AZVOR, PROJ, SEGREDOS  # noqa: E402

AQUI = os.path.dirname(__file__)
BARRA_NAVEGADOR_DIP = 92  # barra de abas + endereço do Chromium do Playwright (--kiosk é ignorado)


def _ler(nome):
    return open(os.path.join(AQUI, nome), encoding="utf-8").read()


def _sessao(cfg):
    s = cfg["sessao"]
    if s.get("tipo", "nenhum") == "nenhum":
        return {}
    for base in (SEGREDOS, PROJ):
        p = os.path.join(base, s.get("arquivo", "sessao.json"))
        if os.path.exists(p):
            return json.load(open(p))
    raise SystemExit("Sessão '%s' configurada, mas %s não existe. Veja references/09." % (s["tipo"], s.get("arquivo")))


def montar(p, cfg, headless=False):
    """Retorna (browser, contexto, bloqueados)."""
    v = cfg["video"]
    escala = float(v["escala"])
    larg, alt = round(v["largura"] / escala), round(v["altura"] / escala)
    args = ["--window-position=0,0", "--force-device-scale-factor=%s" % escala,
            "--window-size=%d,%d" % (larg, alt + BARRA_NAVEGADOR_DIP), "--hide-scrollbars", "--lang=pt-BR",
            "--disable-features=Translate", "--no-first-run", "--disable-infobars"]
    b = p.chromium.launch(headless=headless, args=args, ignore_default_args=["--enable-automation"])
    if headless:
        ctx = b.new_context(viewport={"width": larg, "height": alt}, device_scale_factor=escala,
                            locale="pt-BR", timezone_id="America/Sao_Paulo", service_workers="block")
    else:
        ctx = b.new_context(no_viewport=True, locale="pt-BR", timezone_id="America/Sao_Paulo", service_workers="block")

    ses = _sessao(cfg)
    if ses.get("cookies"):
        ctx.add_cookies(ses["cookies"])
    if ses.get("localStorage"):
        itens = ";".join("localStorage.setItem(%s,%s)" % (json.dumps(k), json.dumps(val)) for k, val in ses["localStorage"].items())
        ctx.add_init_script("try{%s}catch(e){}" % itens)

    publico = {"cor": v["cor_destaque"], "privacidade": cfg["privacidade"], "produto": AZVOR["produto"]}
    ctx.add_init_script("window.__TUTOR_CFG=%s;" % json.dumps(publico, ensure_ascii=False))
    ctx.add_init_script(_ler("cursor.js"))
    ctx.add_init_script(_ler("anonimizador.js"))
    for demo in sorted(glob.glob(os.path.join(PROJ, "demo", "*.js"))):
        ctx.add_init_script(open(demo, encoding="utf-8").read())

    bloqueados = []
    seg = cfg["seguranca"]
    permitir = [re.compile(re.escape(x)) for x in seg.get("permitir", [])]

    def guarda(route, req):
        if seg.get("bloquear_escrita", True) and req.method not in ("GET", "HEAD", "OPTIONS") \
                and not any(r.search(req.url) for r in permitir):
            bloqueados.append("%s %s" % (req.method, req.url[:160]))
            return route.abort()
        return route.continue_()

    ctx.route("**/*", guarda)
    return b, ctx, bloqueados
