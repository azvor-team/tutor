# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Gera a narração de cada cena na ElevenLabs e audio/duracoes.json.

- previous_text/next_text com as falas vizinhas mantêm a entonação contínua entre cenas.
- grafia_fonetica (config) troca palavras só no texto enviado à voz (ex.: "Zenvix" -> "Zénvics").
- Cenas já geradas são puladas; use --forcar para refazer.

Uso: python narrar.py [--cenas c03,c05] [--forcar] [--vozes]
"""
import argparse
import os
import re
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import PROJ, banner, carregar_config, carregar_roteiro, cenas_com_fala, chave_elevenlabs, filtro_cenas, gravar_json  # noqa: E402

API = "https://api.elevenlabs.io"


def fonetica(txt, mapa):
    for k, v in (mapa or {}).items():
        txt = re.sub(r"(?<!\w)%s(?!\w)" % re.escape(k), v, txt)
    return txt


def duracao(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 3)


def listar_vozes(chave):
    r = requests.get(API + "/v2/voices?page_size=100", headers={"xi-api-key": chave}, timeout=60)
    for v in r.json().get("voices", []):
        lb = v.get("labels") or {}
        print(v["voice_id"], "·", v["name"][:40], "·", v.get("category"), "·", lb.get("language"), lb.get("accent"), lb.get("gender"))
    s = requests.get(API + "/v1/user/subscription", headers={"xi-api-key": chave}, timeout=60).json()
    print("plano:", s.get("tier"), "· caracteres usados", s.get("character_count"), "de", s.get("character_limit"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cenas", default="")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--vozes", action="store_true", help="lista as vozes da conta e sai")
    a = ap.parse_args()
    banner("narrar")
    chave = chave_elevenlabs()
    if a.vozes:
        return listar_vozes(chave)
    cfg = carregar_config()
    n = cfg["narracao"]
    if not n.get("voz"):
        sys.exit("Defina narracao.voz na config (use --vozes para listar).")
    cenas = cenas_com_fala(carregar_roteiro())
    so = filtro_cenas(a.cenas)
    pasta = os.path.join(PROJ, "audio")
    os.makedirs(pasta, exist_ok=True)
    falas = [fonetica(c["fala"], n.get("grafia_fonetica")) for c in cenas]
    usados = 0
    for i, c in enumerate(cenas):
        arq = os.path.join(pasta, c["id"] + ".mp3")
        if (so and c["id"] not in so) or (os.path.exists(arq) and not a.forcar and not so):
            continue
        corpo = {"text": falas[i], "model_id": n["modelo"], "language_code": n["idioma"],
                 "voice_settings": {"stability": n["estabilidade"], "similarity_boost": n["similaridade"],
                                    "style": n["estilo"], "use_speaker_boost": True, "speed": n["velocidade"]}}
        if not n["modelo"].startswith("eleven_v3"):
            if i > 0:
                corpo["previous_text"] = falas[i - 1]
            if i < len(cenas) - 1:
                corpo["next_text"] = falas[i + 1]
        r = requests.post("%s/v1/text-to-speech/%s?output_format=%s" % (API, n["voz"], n["formato"]),
                          json=corpo, headers={"xi-api-key": chave}, timeout=300)
        if r.status_code != 200:
            sys.exit("%s: %s %s" % (c["id"], r.status_code, r.text[:300]))
        open(arq, "wb").write(r.content)
        usados += len(falas[i])
        print("✓ %s %.1fs" % (c["id"], duracao(arq)), flush=True)
    dur = {c["id"]: duracao(os.path.join(pasta, c["id"] + ".mp3")) for c in cenas if os.path.exists(os.path.join(pasta, c["id"] + ".mp3"))}
    gravar_json("audio/duracoes.json", dur)
    print("total %.1fs · %d caracteres enviados" % (sum(dur.values()), usados))


if __name__ == "__main__":
    main()
