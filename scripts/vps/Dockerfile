# Tutor™ by Azvor · © 2026 Azvor (azvor.com.br) · Licença AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41
# Imagem de produção do Tutor: Chromium (Playwright) + Xvfb + ffmpeg + fontes + imagemagick.
# A versão do pacote playwright precisa ser a MESMA da imagem base (a imagem não traz o pacote pip).
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy
LABEL org.opencontainers.image.title="Tutor by Azvor" \
      org.opencontainers.image.vendor="Azvor" \
      org.opencontainers.image.url="https://azvor.com.br" \
      org.opencontainers.image.licenses="LicenseRef-AZVOR-NR-1.0" \
      br.com.azvor.produto="AZVT-TUTOR-9C41"
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ffmpeg xvfb fonts-inter fonts-noto-color-emoji fonts-dejavu-core imagemagick \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir playwright==1.49.0 requests==2.32.3 pyyaml==6.0.2 pillow==11.0.0
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
