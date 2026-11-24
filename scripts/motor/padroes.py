# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Biblioteca de padrões de interação.

Cada padrão é um método de `Motor` com o mesmo nome do campo `fazer` do roteiro.
Os alvos são descritos por significado (texto, papel, rótulo, placeholder, contexto),
nunca por coordenada. Detalhes e exemplos: references/04-padroes.md.
"""
import json
import math
import re

PADROES = {}


def padrao(fn):
    PADROES[fn.__name__] = fn
    return fn


class PassoProibido(Exception):
    pass


_CARD_JS = """(el) => {
  let e = el;
  for (let i = 0; i < 9 && e && e !== document.body; i++) {
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    const borda = parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== 'none';
    if (parseFloat(s.borderTopLeftRadius) >= 6 && borda && r.width > 120 && r.height > 50) break;
    e = e.parentElement;
  }
  const r = (e && e !== document.body ? e : el).getBoundingClientRect();
  return {x: r.x, y: r.y, width: r.width, height: r.height};
}"""

_SPOT_JS = """([b, secs, pad, cor]) => {
  const d = document.createElement('div');
  d.setAttribute('data-azvor', 'tutor-destaque');
  Object.assign(d.style, {position:'fixed', left:(b.x-pad)+'px', top:(b.y-pad)+'px', width:(b.width+2*pad)+'px', height:(b.height+2*pad)+'px',
    borderRadius:'12px', boxShadow:`0 0 0 3px ${cor}d9, 0 0 0 9px ${cor}2e, 0 0 0 4000px rgba(15,23,42,.10)`,
    zIndex:2147483640, pointerEvents:'none', opacity:'0', transition:'opacity .35s ease'});
  document.documentElement.appendChild(d);
  requestAnimationFrame(() => requestAnimationFrame(() => d.style.opacity = '1'));
  setTimeout(() => { d.style.opacity = '0'; setTimeout(() => d.remove(), 400); }, secs * 1000);
}"""

_ROLAR_JS = """([el, y, ms, off, sel]) => {
  const rolavel = (e) => e && e.scrollHeight > e.clientHeight + 20 && /auto|scroll/.test(getComputedStyle(e).overflowY);
  let S = null;
  if (sel) S = document.querySelector(sel);
  if (!S && el) { let e = el.parentElement; while (e && !rolavel(e)) e = e.parentElement; S = e; }
  if (!S) {
    const c = [...document.querySelectorAll('div,main,section,nav')].filter(rolavel);
    c.sort((a, b) => b.clientWidth * b.clientHeight - a.clientWidth * a.clientHeight);
    S = c[0] && c[0].clientHeight > window.innerHeight * 0.5 ? c[0] : document.scrollingElement;
  }
  const topo = S === document.scrollingElement ? 0 : S.getBoundingClientRect().top;
  const alvo = el ? S.scrollTop + el.getBoundingClientRect().top - topo - off : y;
  const fim = Math.max(0, Math.min(S.scrollHeight - S.clientHeight, alvo));
  const ini = S.scrollTop, t0 = performance.now();
  return new Promise(res => { const f = (t) => { const k = Math.min(1, (t - t0) / ms); const e = 0.5 - 0.5 * Math.cos(Math.PI * k);
    S.scrollTop = ini + (fim - ini) * e; if (k < 1) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); });
}"""


def _ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


class Motor:
    def __init__(self, pg, cfg):
        self.pg = pg
        self.cfg = cfg
        self.cor = cfg["video"]["cor_destaque"]
        self.pos = [700.0, 420.0]
        self.proibidos = [p.lower() for p in cfg["seguranca"]["botoes_proibidos"]]
        self.vw = cfg["video"]["largura"] / cfg["video"]["escala"]
        self.vh = cfg["video"]["altura"] / cfg["video"]["escala"]

    # ---------- resolução de alvos ----------
    def resolver(self, alvo, escopo=None):
        pg = escopo or self.pg
        if isinstance(alvo, str):
            alvo = {"texto": alvo}
        if alvo.get("contexto") and escopo is None:
            ctx = self.resolver({"texto": alvo["contexto"]})
            caixa = ctx.locator("xpath=ancestor::*[self::section or self::form or self::article or contains(@class,'card') "
                                "or contains(@class,'rounded') or @role='dialog'][1]")
            sub = {k: v for k, v in alvo.items() if k != "contexto"}
            return self.resolver(sub, escopo=caixa)
        exato = bool(alvo.get("exato", False))
        if alvo.get("seletor"):
            loc = pg.locator(alvo["seletor"])
        elif alvo.get("papel") and alvo.get("texto"):
            loc = pg.get_by_role(alvo["papel"], name=alvo["texto"], exact=exato)
        elif alvo.get("rotulo"):
            loc = pg.get_by_label(alvo["rotulo"], exact=exato)
        elif alvo.get("placeholder"):
            loc = pg.get_by_placeholder(alvo["placeholder"], exact=exato)
        elif alvo.get("papel"):
            loc = pg.get_by_role(alvo["papel"])
        elif alvo.get("texto"):
            # filtra por visível: <option> e itens responsivos ocultos também casam com o texto
            loc = pg.locator("internal:text=%s%s >> visible=true" % (json.dumps(alvo["texto"]), "s" if exato else "i"))
        else:
            raise ValueError("alvo sem texto/papel/rotulo/placeholder/seletor: %r" % alvo)
        return loc.nth(int(alvo.get("indice", 0)))

    def caixa(self, loc, card=False):
        loc.wait_for(state="visible", timeout=6000)
        if card:
            return loc.evaluate(_CARD_JS)
        b = loc.bounding_box()
        if not b:
            raise RuntimeError("elemento sem caixa visível")
        return b

    def _garantir_visivel(self, loc):
        b = self.caixa(loc)
        if b["y"] < 60 or b["y"] + min(b["height"], 80) > self.vh - 20:
            self.rolar_ate(loc, deslocamento=110, segundos=0.9)

    # ---------- primitivas ----------
    def mover(self, x, y, segundos=0.7):
        x0, y0 = self.pos
        n = max(2, int(segundos * 60))
        for i in range(1, n + 1):
            e = _ease(i / n)
            self.pg.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            self.pg.wait_for_timeout(int(1000 * segundos / n))
        self.pos = [x, y]

    def _checar_proibido(self, loc, permitido):
        if permitido:
            return
        try:
            txt = (loc.inner_text(timeout=2000) or "").strip().lower()
        except Exception:
            txt = ""
        if any(re.search(r"(^|\b)%s(\b|$)" % re.escape(p), txt) for p in self.proibidos):
            raise PassoProibido("clique recusado em '%s' (botão de disparo). Use ate_o_disparo." % txt[:60])

    # ---------- padrões ----------
    @padrao
    def apontar(self, alvo, segundos=0.7, dx=0.5, dy=0.5, rolar=True):
        loc = self.resolver(alvo)
        if rolar:
            self._garantir_visivel(loc)
        b = self.caixa(loc)
        self.mover(b["x"] + b["width"] * dx, b["y"] + b["height"] * dy, segundos)
        return loc

    @padrao
    def destacar(self, alvo, segundos=2.5, margem=6, card=False, apontar=False):
        loc = self.resolver(alvo)
        if apontar:
            self.apontar(alvo, 0.6)
        b = self.caixa(loc, card=card)
        self.pg.evaluate(_SPOT_JS, [b, segundos, margem, self.cor])

    @padrao
    def clicar(self, alvo, segundos=0.6, dx=0.5, dy=0.5, permitido=False):
        loc = self.resolver(alvo)
        self._checar_proibido(loc, permitido)
        self.apontar(alvo, segundos, dx, dy)
        self.pg.wait_for_timeout(120)
        self.pg.mouse.down()
        self.pg.wait_for_timeout(90)
        self.pg.mouse.up()

    @padrao
    def rolar_ate(self, alvo=None, deslocamento=90, segundos=1.2, conteiner=None, y=None):
        if alvo is not None and not isinstance(alvo, (int, float)):
            loc = alvo if hasattr(alvo, "element_handle") else self.resolver(alvo)
            h = loc.element_handle(timeout=15000)
            self.pg.evaluate(_ROLAR_JS, [h, None, segundos * 1000, deslocamento, conteiner])
        else:
            self.pg.evaluate(_ROLAR_JS, [None, y if y is not None else (alvo or 0), segundos * 1000, 0, conteiner])

    @padrao
    def trocar_aba(self, aba, segundos=0.5):
        for alvo in ({"papel": "tab", "texto": aba}, {"papel": "button", "texto": aba}, {"texto": aba}):
            try:
                self.resolver(alvo).wait_for(state="visible", timeout=1500)
            except Exception:
                continue
            self.clicar(alvo, segundos)
            self.pg.wait_for_timeout(500)
            return
        raise RuntimeError("aba '%s' não encontrada" % aba)

    @padrao
    def pesquisar(self, campo, termo, atraso=95, limpar=True):
        self.clicar(campo, 0.7)
        if limpar:
            self.pg.keyboard.press("Control+A")
            self.pg.keyboard.press("Backspace")
        self.pg.keyboard.type(termo, delay=atraso)
        self.pg.wait_for_timeout(600)

    @padrao
    def filtrar(self, filtro, opcao, segundos=0.6):
        self.clicar(filtro, segundos)
        self.pg.wait_for_timeout(450)
        self.clicar({"texto": opcao, "exato": True} if isinstance(opcao, str) else opcao, segundos)
        self.pg.wait_for_timeout(500)

    @padrao
    def selecionar(self, campo, opcao, segundos=0.6):
        loc = self.resolver(campo)
        tag = loc.evaluate("e => e.tagName")
        if tag == "SELECT":
            self.apontar(campo, segundos)
            loc.select_option(label=opcao)
        else:
            self.filtrar(campo, opcao, segundos)

    @padrao
    def abrir_detalhe(self, linha=0, tabela="tbody tr", segundos=0.9):
        alvo = {"seletor": tabela, "indice": linha} if isinstance(linha, int) else {"texto": linha}
        self.clicar(alvo, segundos, dx=0.2)
        self.pg.wait_for_timeout(700)

    @padrao
    def fechar_detalhe(self):
        self.pg.keyboard.press("Escape")
        self.pg.wait_for_timeout(400)

    @padrao
    def preencher_formulario(self, campos, contexto=None, atraso=70):
        for rotulo, valor in campos.items():
            alvo = {"rotulo": rotulo}
            if contexto:
                alvo["contexto"] = contexto
            try:
                self.resolver(alvo).wait_for(state="visible", timeout=1500)
            except Exception:
                alvo = {"placeholder": rotulo, **({"contexto": contexto} if contexto else {})}
                try:
                    self.resolver(alvo).wait_for(state="visible", timeout=1500)
                except Exception:
                    # rótulo solto ao lado do campo: pega o primeiro input depois do texto
                    alvo = {"seletor": "xpath=//*[normalize-space(text())=%s]/following::input[1]" % json.dumps(rotulo)}
            self.clicar(alvo, 0.5)
            self.pg.keyboard.press("Control+A")
            self.pg.keyboard.type(str(valor), delay=atraso)
            self.pg.wait_for_timeout(250)

    @padrao
    def ate_o_disparo(self, botao, segundos=3.5):
        """Leva o cursor ao botão final, destaca e para. Nunca clica."""
        alvo = {"papel": "button", "texto": botao} if isinstance(botao, str) else botao
        self.apontar(alvo, 0.9)
        self.destacar(alvo, segundos, margem=6)

    @padrao
    def percorrer(self, itens, segundos=0.7, pausa=0.5, destacar=False, card=False):
        for it in itens:
            self.apontar(it, segundos)
            if destacar:
                self.destacar(it, max(1.2, pausa + segundos), card=card)
            self.pg.wait_for_timeout(int(pausa * 1000))

    @padrao
    def navegar_menu(self, item, clicar=True, conteiner="nav", segundos=0.6):
        alvo = {"texto": item, "exato": True}
        loc = self.resolver(alvo)
        try:
            self.rolar_ate(loc, deslocamento=200, segundos=0.6, conteiner=conteiner)
        except Exception:
            pass
        if clicar:
            self.clicar(alvo, segundos)
        else:
            self.apontar(alvo, segundos, rolar=False)
            self.destacar(alvo, 1.3, margem=4)

    @padrao
    def paginar(self, direcao="proxima"):
        self.clicar({"texto": "Próxima" if direcao.startswith("p") else "Anterior"})
        self.pg.wait_for_timeout(600)

    @padrao
    def digitar(self, texto, atraso=90):
        self.pg.keyboard.type(texto, delay=atraso)

    @padrao
    def tecla(self, tecla):
        self.pg.keyboard.press(tecla)

    @padrao
    def esperar(self, segundos=1.0):
        self.pg.wait_for_timeout(int(segundos * 1000))

    @padrao
    def mover_para(self, x, y, segundos=1.0):
        self.mover(x, y, segundos)

    @padrao
    def navegar(self, url):
        base = self.cfg["sistema"]["url"].rstrip("/")
        self.pg.goto(url if url.startswith("http") else base + url, wait_until="domcontentloaded")

    def executar(self, passo):
        p = dict(passo)
        fazer = p.pop("fazer")
        for k in ("quando", "nota", "id"):
            p.pop(k, None)
        if fazer not in PADROES:
            raise ValueError("padrão desconhecido: %s" % fazer)
        return PADROES[fazer](self, **p)
