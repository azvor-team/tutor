# 08 · Revisão (QA) e entrega

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

## Revisão das cenas (sempre por imagem)

`pipeline.sh <proj> folhas` gera mosaicos com 3 quadros por cena (15%, 50%, 85% da fala).
Traga e olhe **todos**. Para cada cena:

| Verificar | Defeito típico | Correção |
|---|---|---|
| Destaque no elemento que a fala cita | Destacou o card vizinho | Alvo mais específico; `card:true` só quando o alvo está dentro do card certo |
| Tela carregada | Skeleton ao trocar de aba | Rota em `privacidade.cache_rotas`; `espera_extra` maior |
| Busca com resultado | "Nenhum resultado" | Outro termo; garantir a aba "Todas" antes |
| Dados | Coluna/tela vazia | Gancho de demo (`demo/*.js`) com ids próprios e datas recentes |
| Privacidade | Nome real aparecendo | Incluir a chave em `chaves_nome` e a rota em `privacidade.rotas` |
| Cursor | Parado ou fora do assunto | Passo `apontar` na âncora certa |
| Log | `!` em algum passo | Ver `references/99-troubleshooting.md` |
| Escritas bloqueadas | Host da própria API com POST inesperado | Algum clique dispararia algo: revise o passo |

Corrija e regrave **só** as cenas com defeito. Repita até o log não ter `!` e as folhas
estarem limpas.

## QA final

`pipeline.sh <proj> qa` grava `qa/final.json` e `qa/final.png`. Aceite quando:
- 1920×1080, h264 + aac, duração dentro de ±2 s da soma prevista;
- loudness integrado entre −17,5 e −14,5 LUFS;
- intro, meio e cartela corretos no mosaico, assinatura legível e fora de informação
  essencial;
- confira a fala contra a tela em pelo menos 3 pontos do vídeo.

## Entrega

1. `scripts/local/trazer.sh <host> <proj> <pasta>` traz MP4, SRT e QA.
2. `pipeline.sh <proj> limpar` apaga a sessão (`shred`) e os temporários. Áudio, clipes e
   vídeo ficam para regravações.
3. Guarde `tutor.config.yaml`, `roteiro.json` e `demo/` no repositório do projeto.
   Nunca guarde `sessao.json` nem chaves.
4. Mensagem ao usuário:
   - onde está o vídeo, a duração e o tamanho;
   - **quais telas usaram dado ilustrativo** (obrigatório);
   - divergências entre fala e tela, botões desabilitados, pronúncias ajustadas;
   - como regravar uma cena;
   - lembrar de revogar tokens/chaves que tenham passado pela conversa.

## Checklist

- [ ] Portões A, B, C e D aprovados
- [ ] `validar` sem erros
- [ ] `conferir` ≥ 90% em todas as cenas (ou diferenças explicadas)
- [ ] Log de gravação sem `!`; escritas bloqueadas só de analytics/telemetria
- [ ] Folhas revisadas
- [ ] `qa` aprovado
- [ ] Sessão apagada
- [ ] Avisos de dados ilustrativos feitos
