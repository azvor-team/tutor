# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Visita as rotas do módulo e gera descoberta/mapa.json + um print por tela.

Para cada tela registra os elementos visíveis que importam num tutorial: menus, abas,
botões, campos (com rótulo e placeholder), selects, tabelas, títulos de cards, contêineres
roláveis e botões de risco (que disparam algo). O mapa é a base para escrever o roteiro.

Uso: python crawler.py [--rotas /a,/b] [--espera 6]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import PROJ, banner, carregar_config, gravar_json  # noqa: E402
from motor.navegador import montar, sync_playwright  # noqa: E402

EXTRAIR_JS = r"""() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0'; };
  const txt = (e) => (e.innerText || e.value || '').replace(/\s+/g, ' ').trim().slice(0, 90);
  const rotulo = (e) => {
    if (e.getAttribute('aria-label')) return e.getAttribute('aria-label');
    if (e.id) { const l = document.querySelector(`label[for="${CSS.escape(e.id)}"]`); if (l) return txt(l); }
    const l = e.closest('label'); if (l) return txt(l).slice(0, 60);
    return null;
  };
  const papel = (e) => e.getAttribute('role') || ({A:'link', BUTTON:'button', INPUT:'textbox', SELECT:'combobox', TEXTAREA:'textbox',
    H1:'heading', H2:'heading', H3:'heading', TH:'columnheader', NAV:'navigation', TABLE:'table'})[e.tagName] || e.tagName.toLowerCase();
  const sel = 'a,button,input,select,textarea,[role=tab],[role=button],[role=menuitem],[role=link],[role=checkbox],[role=switch],[role=combobox],h1,h2,h3,th,[title]';
  const out = [], vistos = new Set();
  for (const e of document.querySelectorAll(sel)) {
    if (!vis(e) || e.closest('[data-azvor]')) continue;
    const r = e.getBoundingClientRect();
    const item = { papel: papel(e), texto: txt(e) || null, rotulo: rotulo(e), placeholder: e.getAttribute('placeholder'),
      tipo: e.getAttribute('type'), titulo: e.getAttribute('title'), na_nav: !!e.closest('nav,aside'),
      x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height) };
    if (e.tagName === 'SELECT') item.opcoes = [...e.options].map(o => o.text).slice(0, 25);
    const k = item.papel + '|' + item.texto + '|' + item.rotulo + '|' + item.placeholder;
    if (vistos.has(k)) continue; vistos.add(k);
    if (!item.texto && !item.rotulo && !item.placeholder && !item.titulo) continue;
    out.push(item);
  }
  const rolaveis = [...document.querySelectorAll('*')].filter(e => e.scrollHeight > e.clientHeight + 20 && /auto|scroll/.test(getComputedStyle(e).overflowY))
    .map(e => ({ tag: e.tagName.toLowerCase(), classe: (e.className || '').toString().slice(0, 60), altura_total: e.scrollHeight, altura_visivel: e.clientHeight }));
  const tabelas = [...document.querySelectorAll('table')].filter(vis).map(t => ({ colunas: [...t.querySelectorAll('th')].map(txt), linhas: t.querySelectorAll('tbody tr').length }));
  return { titulo: document.title, h1: [...document.querySelectorAll('h1,h2')].filter(vis).map(txt).slice(0, 8), elementos: out, rolaveis, tabelas };
}"""


def slug(rota):
    return re.sub(r"[^a-z0-9]+", "_", rota.lower()).strip("_") or "inicio"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rotas", default="")
    ap.add_argument("--espera", type=float, default=6.0)
    a = ap.parse_args()
    banner("descobrir")
    cfg = carregar_config()
    rotas = [r for r in a.rotas.split(",") if r] or cfg["sistema"]["rotas"]
    if not rotas:
        sys.exit("Nenhuma rota em sistema.rotas da config.")
    proibidos = [p.lower() for p in cfg["seguranca"]["botoes_proibidos"]]
    pasta = os.path.join(PROJ, "descoberta")
    os.makedirs(pasta, exist_ok=True)
    mapa = {"url": cfg["sistema"]["url"], "telas": {}}
    with sync_playwright() as p:
        b, ctx, bloqueados = montar(p, cfg, headless=True)
        pg = ctx.new_page()
        base = cfg["sistema"]["url"].rstrip("/")
        for rota in rotas:
            url = rota if rota.startswith("http") else base + rota
            try:
                pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                pg.wait_for_timeout(int(a.espera * 1000))
                pg.screenshot(path=os.path.join(pasta, slug(rota) + ".png"))
                pg.screenshot(path=os.path.join(pasta, slug(rota) + "_inteira.png"), full_page=True)
                dados = pg.evaluate(EXTRAIR_JS)
                dados["url_final"] = pg.url
                dados["risco"] = [e for e in dados["elementos"] if e["papel"] in ("button", "link") and e.get("texto")
                                  and any(re.search(r"(^|\b)%s" % re.escape(x), e["texto"].lower()) for x in proibidos)]
                mapa["telas"][rota] = dados
                print("✓ %s · %d elementos · %d de risco" % (rota, len(dados["elementos"]), len(dados["risco"])), flush=True)
            except Exception as e:
                mapa["telas"][rota] = {"erro": str(e).splitlines()[0][:200]}
                print("✗ %s · %s" % (rota, str(e).splitlines()[0][:160]), flush=True)
        mapa["bloqueados"] = list(bloqueados)
        b.close()
    print("mapa:", gravar_json("descoberta/mapa.json", mapa))


if __name__ == "__main__":
    main()
