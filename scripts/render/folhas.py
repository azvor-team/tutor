# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Folhas de contato para revisar as cenas gravadas: 3 quadros por cena (15%, 50%, 85% da
fala), etiquetados, em mosaicos de 12 (qa/folha_N.png). Também imprime o relatório da
gravação (erros por cena e requisições bloqueadas).

Uso: python folhas.py [--cenas c03,c05]
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import PROJ, banner, carregar_config, carregar_roteiro, filtro_cenas, ler_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cenas", default="")
    a = ap.parse_args()
    banner("folhas")
    cfg = carregar_config()
    lead = float(cfg["video"]["lead"])
    dur = ler_json("audio/duracoes.json", {}) or {}
    so = filtro_cenas(a.cenas)
    qa = os.path.join(PROJ, "qa")
    tmp = os.path.join(qa, "_quadros")
    os.makedirs(tmp, exist_ok=True)
    quadros = []
    for c in carregar_roteiro()["cenas"]:
        cid = c["id"]
        arq = os.path.join(PROJ, "clips", cid + ".mkv")
        if (so and cid not in so) or not os.path.exists(arq):
            continue
        st = float(open(os.path.join(PROJ, "clips", cid + ".start")).read())
        d = float(dur.get(cid, c.get("duracao", 5)))
        for f in (0.15, 0.5, 0.85):
            out = os.path.join(tmp, "%s_%02d.png" % (cid, int(f * 100)))
            rot = "%s %d%%" % (cid, f * 100)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "%.2f" % (st + lead + d * f), "-i", arq, "-frames:v", "1",
                            "-vf", "scale=640:-1,drawtext=text='%s':expansion=none:x=10:y=10:fontsize=22:fontcolor=white:box=1:boxcolor=0x0A1030@0.85:boxborderw=6" % rot,
                            out])
            quadros.append(out)
    for k in range(0, len(quadros), 12):
        lote = quadros[k:k + 12]
        args = sum([["-i", q] for q in lote], [])
        lay = "|".join("%d_%d" % ((i % 3) * 640, (i // 3) * 360) for i in range(len(lote)))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + args +
                       ["-filter_complex", "xstack=inputs=%d:layout=%s:fill=black" % (len(lote), lay),
                        os.path.join(qa, "folha_%d.png" % (k // 12))], check=True)
        print("✓ qa/folha_%d.png" % (k // 12))
    rel = ler_json("clips/relatorio.json", {}) or {}
    for cid, r in (rel.get("cenas") or {}).items():
        for e in r.get("erros", []):
            print("! %s: %s" % (cid, e))
    bl = rel.get("bloqueados", [])
    print("escritas bloqueadas: %d · hosts: %s" % (len(bl), ", ".join(sorted({x.split("/")[2] for x in bl if "//" in x})) or "nenhum"))


if __name__ == "__main__":
    main()
