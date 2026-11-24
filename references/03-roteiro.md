# 03 · Roteiro: estrutura do vídeo e escrita da fala

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

## Anatomia de um tutorial

| Bloco | Duração | Função |
|---|---|---|
| Intro | 5 s | Logo + título do módulo (automático, sem fala) |
| Abertura | 20–30 s | O que é, para que serve, o que a pessoa vai aprender |
| Menu | 10–20 s | Onde fica cada tela do módulo |
| Tela principal / indicadores | 30–60 s | O que cada número ou card significa e como é calculado |
| Telas operacionais | 20–40 s cada | Lista, busca, filtros, abas, detalhe, ações |
| Configuração | 20–40 s | Regras, preferências, integrações |
| Até o disparo | 15–25 s | Preenche e para antes de enviar ("um passo antes") |
| Recapitulação | 15–20 s | O ciclo inteiro em 3 frases + despedida |
| Cartela | 3 s | Logo (automático) |

Uma cena por assunto. Cenas de 10 a 40 s de fala: curtas o bastante para regravar rápido,
longas o bastante para o cursor respirar.

## Como escrever a fala

- **Segunda pessoa e verbo de ação:** "Clique", "Você escolhe", "Aqui você vê".
- **Rótulos exatamente como aparecem na tela.** Eles viram âncoras e o espectador
  reconhece o que ouve.
- **Frases curtas.** Uma ideia por frase. Ritmo medido: ~150 palavras por minuto.
  800 palavras ≈ 6 minutos.
- **Números por extenso** quando houver dúvida: "de zero a seis", "quarenta e oito horas".
- **Explique o porquê**, não só o onde: "unidades com menos de dez respostas ficam no fim,
  para não distorcer a comparação".
- **Nunca prometa** o que a tela não mostra (botão desabilitado, dado vazio). Diga a
  condição: "o botão libera quando o template for aprovado".
- **Marcas e siglas:** se a voz pronunciar errado, corrija em `narracao.grafia_fonetica`
  (a tela continua com a grafia original).
- **Até o disparo:** "Ao clicar em Enviar, a mensagem sai para o cliente. Aqui no vídeo,
  a gente para um passo antes."

## Do roteiro aos passos

Cada passo acontece **quando** um trecho literal da fala é dito. O motor calcula o instante
pela posição do trecho na fala e pela duração real do áudio. Regras de coreografia:
- o cursor sempre mostra aquilo de que a voz está falando;
- mova antes de destacar; destaque de 1,5 a 6 s;
- no máximo uma ação a cada 0,4 s;
- a primeira ação acontece logo no início (`"quando": 0.2`), para a cena não começar parada;
- rolagem só quando o próximo assunto está fora da tela.

## Exemplo comentado

```json
{
  "id": "c07_pesquisas",
  "tela": "/pesquisas",
  "pronto_quando": {"texto": "Detratores"},
  "fala": "Na tela de Pesquisas está cada envio. As abas separam por situação: aguardando, respondidas e detratores. E dá para buscar pelo nome do cliente.",
  "passos": [
    {"quando": 0.2, "fazer": "apontar", "alvo": {"seletor": "tbody tr", "indice": 1}},
    {"quando": "As abas separam", "fazer": "destacar", "alvo": {"papel": "tablist"}},
    {"quando": "aguardando", "fazer": "trocar_aba", "aba": "Aguardando"},
    {"quando": "respondidas", "fazer": "trocar_aba", "aba": "Respondidas"},
    {"quando": "detratores", "fazer": "trocar_aba", "aba": "Detratores"},
    {"quando": "E dá para buscar", "fazer": "pesquisar", "campo": {"placeholder": "Buscar"}, "termo": "atendimento"}
  ]
}
```

Repare: a busca usa um termo que **retorna resultados** e acontece numa aba que tem dados.

## Portão B

Valide (`pipeline.sh <proj> validar`) e mostre ao usuário uma tabela: #, tela, o que
aparece, fala, segundos estimados. Só gere a narração depois do "ok": cada regeneração
consome créditos.
