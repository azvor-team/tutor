# Tutor™ by Azvor · © 2026 Azvor · AZVOR-NR-1.0 — gera capa.png (1280x640) e capa@2x.png a partir de capa.html
import sys
from playwright.sync_api import sync_playwright
pasta = sys.argv[1] if len(sys.argv) > 1 else "."
with sync_playwright() as p:
    b = p.chromium.launch()
    for escala, nome in ((1, "capa.png"), (2, "capa@2x.png")):
        pg = b.new_page(viewport={"width": 1280, "height": 640}, device_scale_factor=escala)
        pg.goto("file://%s/capa.html" % pasta, wait_until="networkidle")
        pg.wait_for_timeout(800)
        pg.locator("#capa").screenshot(path="%s/%s" % (pasta, nome), animations="disabled")
        print("ok", nome)
    b.close()
