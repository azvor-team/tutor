# 07 · Gravação e render

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

## Como a gravação funciona

```
Xvfb (tela virtual) ──► Chromium com janela, escala 1,25
                          ├─ cursor.js        cursor desenhado no DOM + anel de clique
                          ├─ anonimizador.js  troca nomes/telefones, ganchos de demo, cache
                          └─ bloqueio de rede aborta POST/PUT/PATCH/DELETE
ffmpeg x11grab ─────────► clips/<id>.mkv (30 fps, recorte sem a barra do navegador)
```

- **Escala 1,25:** a interface fica do tamanho de um zoom de 125%, legível em 1080p
  (viewport CSS 1536×864).
- **Janela:** `--window-size` é em pixels CSS quando há escala; o motor calcula
  `1920/1,25 × (1080/1,25 + 92)` e sobe o Xvfb com altura suficiente.
- **Barra do navegador:** o Chromium do Playwright ignora `--kiosk`, então o motor mede
  `outerHeight − innerHeight` e recorta a captura a partir daí.
- **Cursor:** o mouse do Playwright não move o cursor do sistema; por isso o cursor é
  desenhado na página e o ffmpeg grava com `-draw_mouse 0`.
- **Sincronia exata:** o ffmpeg grava com `-use_wallclock_as_timestamps 1` e informa no
  stderr o instante do 1º quadro (`start:`). O motor guarda em `clips/<id>.start` quantos
  segundos depois disso a cena começou de verdade. O render corta exatamente ali.
- **Tempo da cena:** `lead (0,6 s) + duração da fala + tail (0,9 s)`. Cada passo roda em
  `lead + duração × posição_da_âncora / tamanho_da_fala`.
- **Falhas não travam a cena:** cada passo roda isolado. Erros vão para
  `clips/relatorio.json` e aparecem como `!` no log.

## Comandos

```bash
pipeline.sh <proj> gravar                    # intro + todas as cenas
pipeline.sh <proj> gravar --cenas intro,c02,c03   # prévia (portão D)
pipeline.sh <proj> gravar --cenas c07 --sem-intro # regrava uma cena
pipeline.sh <proj> folhas                    # qa/folha_N.png + erros + escritas bloqueadas
```

Gravação completa de ~16 cenas leva ~8 min. Uma cena, 1–2 min.

## Prévia (portão D)

Grave `intro` + 2 cenas representativas, gere as folhas, traga e mostre ao usuário. Confira
enquadramento, tamanho da letra, cursor, destaques e dados anonimizados. Só depois grave
tudo.

## Render

```bash
pipeline.sh <proj> render
pipeline.sh <proj> qa
```

Estrutura montada pelo `render.py`:

```
[Intro 5,2 s] ─fade 0,4 s─ [cena 1] ─fade─ … ─fade─ [última cena] ─fade─ [Cartela 3,4 s → branco]
Assinatura (opcional, white label) sobreposta o vídeo todo no canto configurado
Narração: cada mp3 entra em offset_da_cena + lead · amix · loudnorm −16 LUFS
Legendas: .srt ao lado (ou faixa embutida) a partir dos tempos do STT
```

- O offset de cada cena é a soma das anteriores menos as transições. A fala nunca se
  sobrepõe, porque o tail (0,9 s) é maior que a transição (0,4 s).
- Saída: H.264 high CRF 18 preset slow, AAC 192k, `+faststart`, metadados de título e
  procedência. ~6,5 min ≈ 33 MB; render ≈ 3,5 min com 8 vCPU.
- **Logo do canto:** PNG com transparência. Se vier com fundo branco, remova na VPS:
  `convert in.png -fuzz 10% -transparent white out.png`. Logo com margem sobrando:
  `convert in.png -trim +repage out.png`.

## Regravação rápida

Mudou uma fala? `narrar --cenas cX --forcar` → `gravar --cenas cX --sem-intro` → `render`.
Mudou só a coreografia? `gravar --cenas cX --sem-intro` → `render`.
