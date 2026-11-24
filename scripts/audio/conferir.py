# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Transcreve a narração (ElevenLabs scribe) e compara com a fala do roteiro.

Pega marca pronunciada errado, palavra engolida e número trocado. Salva os tempos de cada
palavra em audio/<id>.stt.json (usados pelas legendas).

Uso: python conferir.py [--cenas c03,c05] [--limite 0.9]
"""
import argparse
import difflib
import os
import re
import sys
import unicodedata

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import PROJ, banner, carregar_roteiro, cenas_com_fala, chave_elevenlabs, filtro_cenas, gravar_json  # noqa: E402

NUM = {"zero": "0", "um": "1", "uma": "1", "dois": "2", "duas": "2", "três": "3", "quatro": "4", "cinco": "5", "seis": "6",
       "sete": "7", "oito": "8", "nove": "9", "dez": "10", "vinte": "20", "trinta": "30", "quarenta": "40", "cinquenta": "50"}


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    pal = re.findall(r"[a-z0-9]+", t)
    return [NUM.get(p, p) for p in pal]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cenas", default="")
    ap.add_argument("--limite", type=float, default=0.9)
    a = ap.parse_args()
    banner("conferir")
    chave = chave_elevenlabs()
    so = filtro_cenas(a.cenas)
    resumo = {}
    for c in cenas_com_fala(carregar_roteiro()):
        if so and c["id"] not in so:
            continue
        arq = os.path.join(PROJ, "audio", c["id"] + ".mp3")
        if not os.path.exists(arq):
            continue
        r = requests.post("https://api.elevenlabs.io/v1/speech-to-text", headers={"xi-api-key": chave},
                          data={"model_id": "scribe_v1", "language_code": "por", "timestamps_granularity": "word"},
                          files={"file": open(arq, "rb")}, timeout=300)
        if not r.ok:
            print("✗ %s %s" % (c["id"], r.text[:200]))
            continue
        d = r.json()
        palavras = [{"t": w["text"], "ini": w["start"], "fim": w["end"]} for w in d.get("words", []) if w.get("type") == "word"]
        gravar_json("audio/%s.stt.json" % c["id"], {"texto": d.get("text", ""), "palavras": palavras})
        esperado, ouvido = norm(c["fala"]), norm(d.get("text", ""))
        sm = difflib.SequenceMatcher(None, esperado, ouvido)
        dif = [("%s → %s" % (" ".join(esperado[i1:i2]) or "∅", " ".join(ouvido[j1:j2]) or "∅"))
               for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
        resumo[c["id"]] = {"similaridade": round(sm.ratio(), 3), "diferencas": dif}
        marca = "✓" if sm.ratio() >= a.limite else "!"
        print("%s %s %.0f%%%s" % (marca, c["id"], sm.ratio() * 100, ("  " + " | ".join(dif[:6])) if dif else ""), flush=True)
    gravar_json("qa/conferencia_audio.json", resumo)


if __name__ == "__main__":
    main()
