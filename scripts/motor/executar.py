# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Proibida a venda, sublicença ou reempacotamento. Parcerias: elias.macedo@azvor.com.br
"""Executa o roteiro.json e grava cada cena em clips/<id>.mkv, sincronizada com a narração.

Uso (dentro do container):  python executar.py [--cenas c03,c05] [--sem-intro]
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from comum import AZVOR, PROJ, banner, carregar_config, carregar_roteiro, filtro_cenas, gravar_json, ler_json  # noqa: E402
from motor.navegador import montar, sync_playwright  # noqa: E402
from motor.padroes import Motor, PassoProibido  # noqa: E402

CLIPS = os.path.join(PROJ, "clips")
TELA_X = ":99"


def subir_xvfb(cfg):
    if os.environ.get("DISPLAY"):
        return None
    v = cfg["video"]
    alt_fis = math.ceil((v["altura"] / v["escala"] + 92) * v["escala"]) + 20
    proc = subprocess.Popen(["Xvfb", TELA_X, "-screen", "0", "%dx%dx24" % (v["largura"], alt_fis), "-nolisten", "tcp"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.environ["DISPLAY"] = TELA_X
    time.sleep(1.0)
    return proc


class Gravador:
    """ffmpeg x11grab com o instante exato do 1º quadro (lido do stderr) para sincronizar com a fala."""

    def __init__(self, cfg, offset_y):
        self.cfg, self.offset_y = cfg, offset_y

    def iniciar(self, arquivo, duracao):
        v = self.cfg["video"]
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "info", "-nostats", "-y", "-use_wallclock_as_timestamps", "1",
               "-f", "x11grab", "-draw_mouse", "0", "-framerate", str(v["fps"]), "-video_size", "%dx%d" % (v["largura"], v["altura"]),
               "-i", "%s.0+0,%d" % (os.environ.get("DISPLAY", TELA_X), self.offset_y), "-t", "%.2f" % (duracao + 2.5),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-pix_fmt", "yuv420p",
               "-metadata", "comment=%s %s" % (AZVOR["produto"], AZVOR["id"]), arquivo]
        self.proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
        self.inicio = None

        def ler():
            for linha in self.proc.stderr:
                m = re.search(r"start: ([0-9.]+)", linha)
                if m and self.inicio is None:
                    self.inicio = float(m.group(1))
        threading.Thread(target=ler, daemon=True).start()
        time.sleep(1.2)
        t0 = time.time()
        return t0, (t0 - self.inicio) if self.inicio else 0.9

    def esperar(self):
        self.proc.wait()


def ancora(cena, quando, dur, lead):
    if isinstance(quando, (int, float)):
        return lead + float(quando)
    fala = cena.get("fala", "")
    i = fala.find(quando)
    if i < 0:
        raise ValueError("âncora '%s' não está na fala de %s" % (quando, cena["id"]))
    return lead + dur * i / max(1, len(fala))


def preparar_tela(motor, cfg, cena, roteiro):
    """Navega até a tela da cena (ou da cena anterior com tela, se esta continua a anterior)."""
    pg = motor.pg
    tela, pronto = cena.get("tela"), cena.get("pronto_quando")
    if not tela:
        idx = roteiro["cenas"].index(cena)
        for ant in reversed(roteiro["cenas"][:idx]):
            if ant.get("tela"):
                tela, pronto = ant["tela"], ant.get("pronto_quando")
                break
    if not tela:
        return
    base = cfg["sistema"]["url"].rstrip("/")
    destino = tela if tela.startswith("http") else base + tela
    if cena.get("tela") or pg.url in ("about:blank", "") or not pg.url.startswith(destino.split("#")[0]):
        pg.goto(destino, wait_until="domcontentloaded", timeout=60000)
    pronto = pronto or cfg["sistema"].get("pronto_padrao")
    if isinstance(pronto, str):
        pronto = {"texto": pronto}
    if pronto:
        motor.resolver(pronto).wait_for(state="visible", timeout=60000)
    pg.wait_for_timeout(int(1000 * float(cena.get("espera_extra", 2.0))))
    for passo in cena.get("preparo", []):  # passos sem gravar (ex.: abrir aba antes)
        motor.executar(passo)
    pg.mouse.move(*motor.pos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cenas", default="")
    ap.add_argument("--sem-intro", action="store_true")
    a = ap.parse_args()
    banner("gravar")
    cfg = carregar_config()
    roteiro = carregar_roteiro()
    dur = (ler_json("audio/duracoes.json", {}) or {})
    dur = {k: v for k, v in dur.items() if not k.startswith("_")}
    so = filtro_cenas(a.cenas)
    v = cfg["video"]
    lead, tail = float(v["lead"]), float(v["tail"])
    os.makedirs(CLIPS, exist_ok=True)
    xvfb = subir_xvfb(cfg)
    relatorio = {"cenas": {}, "bloqueados": []}

    with sync_playwright() as p:
        b, ctx, bloqueados = montar(p, cfg, headless=False)
        pg = ctx.new_page()
        pg.set_default_timeout(15000)
        pg.goto("about:blank")
        pg.wait_for_timeout(400)
        barra = pg.evaluate("outerHeight - innerHeight")
        gravador = Gravador(cfg, int(math.ceil(barra * v["escala"])) + 1)
        motor = Motor(pg, cfg)

        # intro
        intro = v["intro"]
        if intro.get("ativa") and not a.sem_intro and (not so or "intro" in so):
            pasta = os.path.join(PROJ, "_intro")
            os.makedirs(pasta, exist_ok=True)
            shutil.copy(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "intro.html"),
                        os.path.join(pasta, "intro.html"))
            logo = intro.get("logo") or ""
            if logo and os.path.exists(os.path.join(PROJ, logo)):
                shutil.copy(os.path.join(PROJ, logo), os.path.join(pasta, os.path.basename(logo)))
            q = urllib.parse.urlencode({"titulo": intro.get("titulo") or roteiro.get("titulo", ""),
                                        "subtitulo": intro.get("subtitulo") or roteiro.get("subtitulo", ""),
                                        "logo": os.path.basename(logo), "cor": intro.get("cor", v["cor_destaque"])})
            arq = os.path.join(CLIPS, "intro.mkv")
            t0, ini = gravador.iniciar(arq, float(intro["duracao"]) + 1.2)
            pg.goto("file://%s/intro.html?%s" % (pasta, q))
            while time.time() < t0 + float(intro["duracao"]) + 1.4:
                pg.wait_for_timeout(100)
            gravador.esperar()
            open(os.path.join(CLIPS, "intro.start"), "w").write("%.3f" % ini)
            print("gravado intro", flush=True)

        for cena in roteiro["cenas"]:
            cid = cena["id"]
            if so and cid not in so:
                continue
            if cena.get("fala") and cid not in dur:
                print("  ! %s sem áudio (rode a etapa narrar)" % cid, flush=True)
                continue
            d = dur.get(cid, float(cena.get("duracao", 5)))
            erros = []
            try:
                preparar_tela(motor, cfg, cena, roteiro)
            except Exception as e:
                erros.append("preparo: %s" % str(e).splitlines()[0][:200])
            total = lead + d + tail
            arq = os.path.join(CLIPS, "%s.mkv" % cid)
            t0, ini = gravador.iniciar(arq, total)
            passos = sorted(cena.get("passos", []), key=lambda s: ancora(cena, s.get("quando", 0), d, lead))
            for passo in passos:
                alvo_t = t0 + ancora(cena, passo.get("quando", 0), d, lead) - 0.15
                falta = alvo_t - time.time()
                if falta > 0:
                    pg.wait_for_timeout(int(falta * 1000))
                try:
                    motor.executar(passo)
                except PassoProibido as e:
                    erros.append("PROIBIDO %s" % e)
                except Exception as e:
                    erros.append("%s @ %r: %s" % (passo.get("fazer"), passo.get("quando"), str(e).splitlines()[0][:200]))
            falta = t0 + total + 0.3 - time.time()
            if falta > 0:
                pg.wait_for_timeout(int(falta * 1000))
            gravador.esperar()
            open(os.path.join(CLIPS, "%s.start" % cid), "w").write("%.3f" % ini)
            relatorio["cenas"][cid] = {"duracao": round(total, 2), "erros": erros}
            print("gravado %s %.1fs%s" % (cid, total, "".join("\n  ! " + x for x in erros)), flush=True)

        relatorio["bloqueados"] = list(bloqueados)
        hosts = sorted({x.split("/")[2] for x in bloqueados if "//" in x})
        print("escritas bloqueadas: %d (%s)" % (len(bloqueados), ", ".join(hosts) or "nenhuma"), flush=True)
        b.close()
    anterior = ler_json("clips/relatorio.json", {}) or {}
    anterior.setdefault("cenas", {}).update(relatorio["cenas"])
    anterior["bloqueados"] = relatorio["bloqueados"]
    gravar_json("clips/relatorio.json", {k: v for k, v in anterior.items() if not k.startswith("_")})
    if xvfb:
        xvfb.terminate()


if __name__ == "__main__":
    main()
