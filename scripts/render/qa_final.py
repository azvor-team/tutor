# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""QA do MP4 final: formato, duração, loudness e mosaico de quadros-chave (qa/final.png)."""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import PROJ, banner, carregar_config, gravar_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="")
    a = ap.parse_args()
    banner("qa")
    cfg = carregar_config()
    video = os.path.join(PROJ, a.video or "out/%s.mp4" % cfg["projeto"])
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
                                      "-of", "json", video], capture_output=True, text=True).stdout)
    dur = float(info["format"]["duration"])
    lufs = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", lufs)
    integrado = float(m[-1]) if m else None
    pontos = [2.5] + [dur * f for f in (0.2, 0.4, 0.6, 0.8)] + [dur - 1.5]
    qa = os.path.join(PROJ, "qa")
    os.makedirs(qa, exist_ok=True)
    arqs = []
    for i, t in enumerate(pontos):
        p = os.path.join(qa, "_final_%d.png" % i)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "%.2f" % t, "-i", video, "-frames:v", "1", "-vf", "scale=960:-1", p])
        arqs.append(p)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + sum([["-i", x] for x in arqs], []) +
                   ["-filter_complex", "xstack=inputs=6:layout=0_0|960_0|0_540|960_540|0_1080|960_1080", os.path.join(qa, "final.png")])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    mudo = integrado is not None and integrado < -60
    ok = v["width"] == cfg["video"]["largura"] and v["height"] == cfg["video"]["altura"] and (mudo or (integrado is not None and abs(integrado + 16) < 1.5))
    rel = {"video": video, "duracao_s": round(dur, 1), "tamanho_mb": round(int(info["format"]["size"]) / 1e6, 1),
           "resolucao": "%dx%d" % (v["width"], v["height"]), "codecs": [s["codec_name"] for s in info["streams"]],
           "loudness_lufs": integrado, "sem_narracao": mudo, "aprovado": ok}
    gravar_json("qa/final.json", rel)
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    print("mosaico: qa/final.png")


if __name__ == "__main__":
    main()
