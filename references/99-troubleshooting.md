# 99 · Problemas conhecidos e soluções

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

Registro de problemas reais encontrados em produção. Consulte antes de improvisar.

## Ambiente

| Sintoma | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: playwright` | A imagem Playwright traz navegadores, não o pacote pip | `pip install playwright==<mesma versão da imagem>` (já no Dockerfile) |
| Chromium trava ao abrir | Container sem init/shm | `docker run --init --ipc=host` (o `pipeline.sh` já usa) |
| `scp: dest open … No such file` | Pasta remota não existe | `mkdir -p` antes (o `enviar.sh` já faz) |
| `parse error near '<'` no shell local | Heredoc com aspas simples dentro de `ssh '…'` | Escreva o arquivo local e envie com `scp`/`rsync` |
| `% format: not enough arguments` | `%` de JavaScript dentro de string Python formatada com `%` | Escape como `%%` ou leia o JS de arquivo (padrão do motor) |

## Narração

| Sintoma | Causa | Solução |
|---|---|---|
| 403 `output_format_not_allowed` | Formato acima do plano | `mp3_44100_128` |
| Marca pronunciada errado | Grafia ambígua | `narracao.grafia_fonetica` + `narrar --cenas cX --forcar` |
| Entonação "recomeça" a cada cena | Cenas geradas isoladas | O `narrar.py` já envia `previous_text`/`next_text` |

## Navegador e dados

| Sintoma | Causa | Solução |
|---|---|---|
| Página trava ao carregar | Interceptar respostas grandes pelo Playwright (`route.fetch`) | O motor anonimiza dentro da página (wrapper de `fetch`) |
| Print/ação em timeout com lista grande | Substituição global por nome em JSON de MB | Caminho rápido > 150 KB (já implementado) |
| Unidade/produto virou nome de pessoa | Chave genérica (`nome`) em `chaves_nome` | Use só chaves de cliente |
| `networkidle` nunca chega | App com polling | `domcontentloaded` + `pronto_quando` |
| Skeleton ao trocar de aba | Cache do front expirou e refez a requisição pesada | `privacidade.cache_rotas` |
| Itens ilustrativos somem | Front recoloca o objeto original pelo id | Ids próprios (`demo-1`…) e datas recentes |
| Lista ilustrativa filtrada | Datas fora do período padrão da tela | Datas dentro do período |

## Gravação

| Sintoma | Causa | Solução |
|---|---|---|
| Barra do navegador no vídeo | `--kiosk`/`--start-fullscreen` ignorados no Chromium do Playwright | O motor mede a barra e recorta (automático) |
| Janela gigante / layout errado | `--window-size` em CSS px com escala | Já calculado em `navegador.py` |
| Ações atrasadas segundos | Esperar o arquivo de vídeo crescer (buffer do contêiner) | O motor lê `start:` do stderr do ffmpeg |
| MKV corrompido | `-copyts` com timestamps de relógio | Não usar `-copyts` (o motor não usa) |
| `elemento sem caixa visível` / timeout | Texto casou com `<option>`, item responsivo oculto ou tela sem o elemento | O motor já filtra visíveis; refine o alvo (`papel`, `contexto`, `exato`) |
| Clicou no lugar errado | Primeiro texto igual era um banner/link | Alvo com texto único do card, `contexto` ou `indice` |
| Destaque no card vizinho | Subida até o card pegou o contêiner errado | Destaque um elemento mais específico ou sem `card:true` |
| Cena regravada sozinha falha | Dependia da tela da anterior | Dê `tela` à cena ou use `preparo`; o motor já herda a tela anterior |
| Busca sem resultado | Aba com filtro ativo ou termo raro | `trocar_aba` para "Todas" antes; termo frequente |
| Uma ação lenta atrasa o resto | Alvo inexistente espera até 6 s | Corrija o alvo; veja `!` no log |
| Classificador/assistente bloqueia gerar token | Ação sensível sem consentimento | Peça o OK explícito (portão C) e diga qual usuário aparecerá |
