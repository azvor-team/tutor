# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Valida o roteiro.json antes de gastar narração e gravação.

Erros (bloqueiam): âncora fora da fala, padrão desconhecido, parâmetro obrigatório
faltando, clique em botão de disparo sem "permitido", ids repetidos.
Avisos: alvo não encontrado no mapa da tela, ritmo apertado, cena longa ou curta.

Uso: python validar_roteiro.py   (sai com código 1 se houver erro)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import banner, carregar_config, carregar_roteiro, gravar_json, ler_json  # noqa: E402

PPM = 150  # palavras por minuto medidas na narração pt-BR
OBRIGATORIOS = {
    "apontar": ["alvo"], "destacar": ["alvo"], "clicar": ["alvo"], "rolar_ate": [], "trocar_aba": ["aba"],
    "pesquisar": ["campo", "termo"], "filtrar": ["filtro", "opcao"], "selecionar": ["campo", "opcao"],
    "abrir_detalhe": [], "fechar_detalhe": [], "preencher_formulario": ["campos"], "ate_o_disparo": ["botao"],
    "percorrer": ["itens"], "navegar_menu": ["item"], "paginar": [], "digitar": ["texto"], "tecla": ["tecla"],
    "esperar": [], "mover_para": ["x", "y"], "navegar": ["url"],
}


def textos_do_alvo(alvo):
    if isinstance(alvo, str):
        return [alvo]
    if isinstance(alvo, dict):
        return [alvo[k] for k in ("texto", "rotulo", "placeholder") if alvo.get(k)]
    return []


def main():
    banner("validar")
    cfg = carregar_config()
    rot = carregar_roteiro()
    mapa = ler_json("descoberta/mapa.json", {}) or {}
    proibidos = [p.lower() for p in cfg["seguranca"]["botoes_proibidos"]]
    duracoes = {k: v for k, v in (ler_json("audio/duracoes.json", {}) or {}).items() if not k.startswith("_")}
    erros, avisos, ids = [], [], set()
    total = 0.0
    tela_atual = None
    for c in rot.get("cenas", []):
        cid = c.get("id") or "?"
        if cid in ids:
            erros.append("%s: id repetido" % cid)
        ids.add(cid)
        fala = c.get("fala", "")
        tela_atual = c.get("tela") or tela_atual
        palavras = len(fala.split())
        dur = duracoes.get(cid) or (palavras * 60.0 / PPM if fala else float(c.get("duracao", 5)))
        total += dur
        if fala and not (8 <= dur <= 45):
            avisos.append("%s: fala de ~%.0fs (ideal 10–40s)" % (cid, dur))
        textos_tela = set()
        if tela_atual and tela_atual in mapa.get("telas", {}):
            for e in mapa["telas"][tela_atual].get("elementos", []):
                for k in ("texto", "rotulo", "placeholder", "titulo"):
                    if e.get(k):
                        textos_tela.add(e[k].lower())
        ultimo, tempos = -1, []
        for i, p in enumerate(c.get("passos", [])):
            ref = "%s passo %d (%s)" % (cid, i + 1, p.get("fazer"))
            fz = p.get("fazer")
            if fz not in OBRIGATORIOS:
                erros.append("%s: padrão desconhecido" % ref)
                continue
            for req in OBRIGATORIOS[fz]:
                if req not in p:
                    erros.append("%s: falta '%s'" % (ref, req))
            q = p.get("quando", 0)
            if isinstance(q, str):
                pos = fala.find(q)
                if pos < 0:
                    erros.append("%s: âncora '%s' não está na fala" % (ref, q))
                    continue
                t = dur * pos / max(1, len(fala))
                if pos < ultimo:
                    avisos.append("%s: âncora fora de ordem (o motor reordena)" % ref)
                ultimo = pos
            else:
                t = float(q)
            tempos.append(t)
            if fz == "clicar" and not p.get("permitido"):
                for t_ in textos_do_alvo(p.get("alvo")):
                    if any(re.search(r"(^|\b)%s(\b|$)" % re.escape(x), t_.lower()) for x in proibidos):
                        erros.append("%s: clique em '%s' é disparo. Use ate_o_disparo ou justifique com permitido" % (ref, t_))
            if textos_tela:
                alvos = []
                for k in ("alvo", "campo", "filtro"):
                    alvos += textos_do_alvo(p.get(k))
                if fz == "trocar_aba":
                    alvos.append(p.get("aba", ""))
                if fz == "ate_o_disparo":
                    alvos += textos_do_alvo(p.get("botao"))
                for t_ in alvos:
                    if t_ and not any(t_.lower() in x for x in textos_tela):
                        avisos.append("%s: '%s' não aparece no mapa de %s (pode estar em gaveta/modal)" % (ref, t_, tela_atual))
        tempos.sort()
        for a_, b_ in zip(tempos, tempos[1:]):
            if b_ - a_ < 0.4:
                avisos.append("%s: passos a menos de 0,4s um do outro" % cid)
                break
    rel = {"erros": erros, "avisos": avisos, "cenas": len(ids), "duracao_estimada_s": round(total, 1)}
    gravar_json("qa/validacao.json", rel)
    for e in erros:
        print("✗", e)
    for a_ in avisos:
        print("!", a_)
    print("%d cenas · ~%.0f min %.0f s · %d erros · %d avisos" % (len(ids), total // 60, total % 60, len(erros), len(avisos)))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
