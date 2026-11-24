# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Monta o vídeo final: intro → cenas (com narração) → cartela, com transições, logo de
assinatura (white label, opcional), loudness -16 LUFS e legendas (.srt) a partir da
transcrição com tempos.

Uso: python render.py [--saida out/tutorial.mp4]
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import AZVOR, PROJ, banner, carregar_config, carregar_roteiro, gravar_json, ler_json  # noqa: E402


def start(nome):
    return float(open(os.path.join(PROJ, "clips", nome + ".start")).read())


def srt_tempo(s):
    h, r = divmod(max(0.0, s), 3600)
    m, s = divmod(r, 60)
    return "%02d:%02d:%06.3f" % (h, m, s)


def gerar_legendas(segs, offsets, lead, caminho):
    linhas, n = [], 1
    for (nome, _, _, audio), off in zip(segs, offsets):
        if not audio:
            continue
        stt = ler_json("audio/%s.stt.json" % nome)
        if not stt:
            continue
        bloco, ini = [], None
        palavras = stt["palavras"]
        for i, w in enumerate(palavras):
            ini = w["ini"] if ini is None else ini
            bloco.append(w["t"])
            fim = w["fim"]
            txt = " ".join(bloco)
            prox = palavras[i + 1] if i + 1 < len(palavras) else None
            quebra = len(txt) > 70 or (fim - ini) > 4.0 or txt.endswith((".", "?", "!")) or prox is None \
                or (prox and prox["ini"] - fim > 0.6)
            if quebra:
                t0, t1 = off + lead + ini, off + lead + fim
                linhas.append("%d\n%s --> %s\n%s\n" % (n, srt_tempo(t0).replace(".", ","), srt_tempo(t1).replace(".", ","), txt))
                n += 1
                bloco, ini = [], None
    if linhas:
        open(caminho, "w", encoding="utf-8").write("\n".join(linhas))
        return caminho
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default="")
    a = ap.parse_args()
    banner("render")
    cfg = carregar_config()
    rot = carregar_roteiro()
    v = cfg["video"]
    lead, tail, X = float(v["lead"]), float(v["tail"]), float(v["transicao"])
    dur = {k: x for k, x in (ler_json("audio/duracoes.json", {}) or {}).items() if not k.startswith("_")}
    os.makedirs(os.path.join(PROJ, "out"), exist_ok=True)
    saida = os.path.join(PROJ, a.saida or "out/%s.mp4" % cfg["projeto"])
    clip = lambda n: os.path.join(PROJ, "clips", n + ".mkv")  # noqa: E731

    segs = []  # (nome, inicio_no_arquivo, duracao, audio|None)
    if v["intro"].get("ativa") and os.path.exists(clip("intro")):
        segs.append(("intro", start("intro") + 0.1, float(v["intro"]["duracao"]), None))
    for c in rot["cenas"]:
        if not os.path.exists(clip(c["id"])):
            print("  ! %s sem clipe, ficou de fora" % c["id"])
            continue
        d = dur.get(c["id"], float(c.get("duracao", 5)))
        audio = os.path.join(PROJ, "audio", c["id"] + ".mp3") if c.get("fala") else None
        segs.append((c["id"], start(c["id"]), lead + d + tail, audio))
    if not segs:
        sys.exit("Nada para montar: grave as cenas primeiro.")

    ins, filt = [], []
    for i, (nome, ini, d, _) in enumerate(segs):
        ins += ["-ss", "%.3f" % ini, "-t", "%.3f" % d, "-i", clip(nome)]
        filt.append("[%d:v]setpts=PTS-STARTPTS,fps=%d,format=yuv420p,settb=AVTB[v%d]" % (i, v["fps"], i))
    n = len(segs)
    durs = [s[2] for s in segs]
    cart = v["cartela"]
    if cart.get("ativa") and segs[0][0] == "intro":
        quadro = os.path.join(PROJ, "out", "_cartela.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "%.3f" % (start("intro") + 4.2), "-i", clip("intro"),
                        "-frames:v", "1", quadro], check=True)
        cd = float(cart["duracao"])
        ins += ["-loop", "1", "-t", "%.2f" % cd, "-i", quadro]
        filt.append("[%d:v]fps=%d,format=yuv420p,settb=AVTB,fade=t=out:st=%.2f:d=0.8:color=white[v%d]" % (n, v["fps"], cd - 0.8, n))
        durs.append(cd)
        n += 1
    prox = n

    offsets, cur, total = [0.0], "v0", durs[0]
    for i in range(1, n):
        off = total - X
        offsets.append(off)
        filt.append("[%s][v%d]xfade=transition=fade:duration=%.2f:offset=%.3f[x%d]" % (cur, i, X, off, i))
        cur, total = "x%d" % i, off + durs[i]

    ass = v["assinatura"]
    logo = os.path.join(PROJ, ass["logo"]) if ass.get("logo") else ""
    if logo and os.path.exists(logo):
        ins += ["-loop", "1", "-i", logo]
        m = int(ass.get("margem", 36))
        pos = {"inferior_direito": "W-w-%d:H-h-%d", "inferior_esquerdo": "%d:H-h-%d", "superior_direito": "W-w-%d:%d",
               "superior_esquerdo": "%d:%d"}[ass.get("posicao", "inferior_direito")] % (m + 4, m)
        filt.append("[%d:v]scale=-1:%d,format=rgba,colorchannelmixer=aa=%.2f[lg]" % (prox, int(ass["altura"]), float(ass["opacidade"])))
        filt.append("[%s][lg]overlay=%s:shortest=1:format=auto[vout]" % (cur, pos))
        prox += 1
    else:
        filt.append("[%s]null[vout]" % cur)

    amix = []
    for i, (nome, _, _, audio) in enumerate(segs):
        if not audio:
            continue
        ins += ["-i", audio]
        ms = int(round((offsets[i] + lead) * 1000))
        filt.append("[%d:a]aresample=48000,adelay=%d|%d[a%d]" % (prox, ms, ms, prox))
        amix.append("[a%d]" % prox)
        prox += 1
    if amix:
        filt.append("%samix=inputs=%d:normalize=0:dropout_transition=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout]"
                    % ("".join(amix), len(amix)))
    else:
        ins += ["-f", "lavfi", "-t", "%.2f" % total, "-i", "anullsrc=r=48000:cl=stereo"]
        filt.append("[%d:a]anull[aout]" % prox)
        prox += 1

    srt = None
    if v.get("legendas", "arquivo") != "nenhum":
        srt = gerar_legendas(segs, offsets, lead, os.path.splitext(saida)[0] + ".srt")
    extra_sub = []
    if srt and v.get("legendas") == "faixa":
        ins += ["-i", srt]
        extra_sub = ["-map", "%d:s" % prox, "-c:s", "mov_text", "-metadata:s:s:0", "language=por"]

    meta = ["-metadata", "title=%s" % (rot.get("titulo") or cfg["projeto"]),
            "-metadata", "comment=Produzido com %s · %s · %s" % (AZVOR["produto"], AZVOR["site"], AZVOR["id"]),
            "-metadata", "encoder=%s %s" % (AZVOR["produto"], AZVOR["versao"])]
    cmd = ["ffmpeg", "-loglevel", "error", "-stats", "-y"] + ins + [
        "-filter_complex", ";".join(filt), "-map", "[vout]", "-map", "[aout]"] + extra_sub + [
        "-t", "%.3f" % total, "-c:v", "libx264", "-preset", "slow", "-crf", str(v["crf"]), "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"] + meta + [saida]
    print("montando %d segmentos · %.1fs previstos" % (n, total), flush=True)
    subprocess.run(cmd, check=True)
    gravar_json("out/linha_do_tempo.json", {"segmentos": [{"nome": s[0], "inicio": round(o, 3), "duracao": round(s[2], 3)}
                                                          for s, o in zip(segs, offsets)], "duracao": round(total, 3)})
    print("✓", saida, ("· legendas %s" % srt) if srt else "")


if __name__ == "__main__":
    main()
