# 06 · Narração (ElevenLabs)

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

## Escolher a voz

```bash
ssh <host> "bash <raiz>/skill/scripts/vps/pipeline.sh <proj> narrar --vozes"
```

Lista `voice_id · nome · categoria · idioma · sotaque · gênero` e o consumo do plano.
Prefira vozes `pt` + `brazilian` da categoria *professional*, ou uma que o usuário já use.
Grave o `voice_id` em `narracao.voz`.

## Parâmetros que funcionaram

| Campo | Valor | Por quê |
|---|---|---|
| `modelo` | `eleven_v4` | Melhor naturalidade em pt-BR; aceita `previous_text`/`next_text` |
| `formato` | `mp3_44100_128` | O plano Starter recusa 192 (erro 403 `output_format_not_allowed`) |
| `estabilidade` | 0.5 | Natural sem variar demais entre cenas |
| `similaridade` | 0.8 | Fiel ao timbre |
| `estilo` | 0.15 | Leve expressividade, sem teatralidade |
| `velocidade` | 1.0 | ~150 palavras/min medidas |

`previous_text`/`next_text` recebem as falas vizinhas: a entonação flui como se fosse uma
gravação só, mesmo gerando por cena.

## Gerar e conferir

```bash
pipeline.sh <proj> narrar                 # pula cenas já geradas
pipeline.sh <proj> narrar --cenas c04 --forcar
pipeline.sh <proj> conferir               # transcreve (scribe_v1) e compara com a fala
```

`conferir` mostra a similaridade por cena e as diferenças (`esperado → ouvido`). Procure:
- **marca pronunciada errado** (ex.: "Zenvix" ouvido como "Zenviques"): ajuste
  `grafia_fonetica: {"Zenvix": "Zénvics"}` e regenere só a cena;
- palavra engolida ou trocada;
- números: o STT escreve "10", "48". Isso é normal se a fala estiver correta.

A transcrição com tempo de cada palavra fica em `audio/<id>.stt.json` e alimenta as
legendas no render.

## Consumo de referência

16 cenas, ~6 min de vídeo ≈ 5,3 mil caracteres (Starter: ~60 mil/mês). A transcrição de
conferência também consome cota de STT. Regenere só o que mudou.
