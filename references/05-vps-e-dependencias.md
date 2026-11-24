# 05 · VPS, dependências e estrutura de pastas

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

## Por que VPS

Gravar tela exige navegador, tela virtual, ffmpeg e fontes iguais em toda execução. Num
container descartável na VPS isso é reproduzível e não toca a máquina do usuário. Do lado do
usuário só saem arquivos de texto/imagem (rsync) e só volta o MP4.

## Requisitos

| Item | Mínimo | Observação |
|---|---|---|
| Linux + Docker | Docker 20+ | Acesso SSH por chave (nunca senha) |
| CPU / RAM / disco | 4 vCPU · 8 GB · 5 GB livres | Render ≈ 1,7× tempo real com 8 vCPU |
| ElevenLabs | Plano Starter ou superior | Starter: `mp3_44100_128` |

## Imagem (`scripts/vps/Dockerfile`)

- Base `mcr.microsoft.com/playwright/python:v1.49.0-jammy` (Chromium e dependências).
- `pip install playwright==1.49.0`: **a mesma versão da imagem**. A imagem traz o navegador,
  mas não o pacote.
- `apt`: ffmpeg, xvfb, fonts-inter, fonts-noto-color-emoji, fonts-dejavu-core, imagemagick.
- `pip`: requests, pyyaml, pillow (versões fixadas).
- Sempre rodar com `--init --ipc=host`: sem isso o Chromium pode travar.

## Estrutura na VPS

```
<raiz>/                     (padrão /root/tutor, chmod 700)
├── skill/                  cópia desta skill (rsync, somente leitura no container)
├── segredos/               chmod 700 · elevenlabs.key, sessao.json (chmod 600)
└── projetos/<projeto>/
    ├── tutor.config.yaml   roteiro.json   marca/   demo/*.js
    ├── descoberta/         mapa.json + prints
    ├── audio/              <id>.mp3, <id>.stt.json, duracoes.json
    ├── clips/              <id>.mkv, <id>.start, relatorio.json
    ├── qa/                 validacao.json, folha_N.png, final.png, final.json
    └── out/                <projeto>.mp4, <projeto>.srt, linha_do_tempo.json
```

## Primeira vez

```bash
# na máquina do usuário (só envia arquivos)
scripts/local/enviar.sh <host> <pasta-do-projeto>            # skill + projeto
scripts/local/enviar_segredo.sh <host> <arquivo-.env-ou-chave>
# na VPS
ssh <host> "bash /root/tutor/skill/scripts/vps/pipeline.sh - setup"
```

`setup` cria as pastas, builda `azvor-tutor:1` e confirma que o Chromium abre (~1,5 min).

## Regras de transporte

- Scripts com aspas simples (JS) **não** vão por heredoc dentro de `ssh '…'`: escreva o
  arquivo localmente e envie com `enviar.sh`/`scp`.
- Crie a pasta remota antes de qualquer `scp` (`enviar.sh` já faz isso).
- Comandos longos (gravar tudo, render) rodam em segundo plano no seu ambiente; espere a
  notificação em vez de consultar repetidamente.
