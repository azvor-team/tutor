# 01 · Briefing

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

O briefing evita o erro mais caro: gravar o vídeo certo do jeito errado, ou gravar algo que
não devia acontecer em produção. Faça as perguntas numa mensagem só, com sugestões padrão,
para o usuário responder rápido.

## Perguntas

| # | Pergunta | Padrão sugerido |
|---|---|---|
| 1 | Qual módulo ou fluxo ensinar? Do quê até o quê? | Do painel/lista principal até o ponto de "salvar/enviar" |
| 2 | Para quem é o vídeo (cliente, equipe interna, franqueado, suporte)? | Usuário final do módulo |
| 3 | Onde o vídeo vai ser usado (apresentação, onboarding, central de ajuda)? | Onboarding |
| 4 | O que **não pode** acontecer? Ex.: "vai até o disparo mas não dispara" | Nada é enviado, salvo ou apagado |
| 5 | URL do sistema e se é produção, homologação ou local | — |
| 6 | O sistema exige login? Existe usuário de demonstração? | Token temporário de um usuário neutro (ver 09) |
| 7 | Servidor para rodar (host SSH com Docker) | — |
| 8 | Onde está a chave da ElevenLabs? | Arquivo .env/config do usuário |
| 9 | Logos: intro (marca de quem recebe) e assinatura no canto (opcional, white label) | Logo do cliente na intro, assinatura vazia |
| 10 | Cor de destaque | Cor primária da marca |
| 11 | Duração desejada | 4 a 7 minutos |
| 12 | Voz (masculina/feminina, tom) | Profissional pt-BR, tom conversado |
| 13 | Legendas? | Arquivo .srt ao lado do vídeo |

## Como achar a chave sem expor

Liste só **nomes de arquivos** e mostre o valor mascarado:

```bash
grep -rIl --exclude-dir=node_modules --exclude-dir=.git -i "elevenlabs" <pasta> | head
grep -n "ELEVENLABS" <arquivo> | sed -E 's/(sk_[A-Za-z0-9]{4})[A-Za-z0-9]+/\1…/g'
```

Depois envie com `scripts/local/enviar_segredo.sh`, que faz pipe direto para a VPS e nunca
imprime o valor.

## Portão A

Resuma em 5 linhas o escopo, o ponto final, as restrições, onde roda e as marcas. Só siga
com o "ok" do usuário.
