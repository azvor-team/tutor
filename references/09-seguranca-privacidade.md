# 09 · Segurança, privacidade e sessão

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

Tutoriais costumam ser gravados no sistema real. Estas camadas existem para que nada
saia do lugar enquanto o vídeo é feito.

## 1. Bloqueio de escrita (rede)

`seguranca.bloquear_escrita: true` (padrão) faz o navegador abortar todo
POST/PUT/PATCH/DELETE, de qualquer domínio, exceto os padrões em `seguranca.permitir`
(ex.: `/auth/refresh` para a sessão não expirar). Mesmo que um clique errado aconteça,
nada chega ao servidor. O relatório lista tudo que foi bloqueado: espere ver só analytics
e telemetria.

## 2. Botões de disparo (roteiro)

`seguranca.botoes_proibidos` lista palavras de ação perigosa. O validador recusa
`clicar` nesses botões e o motor recusa de novo na hora da gravação. Para mostrar o fim de
um fluxo, use `ate_o_disparo`. Só use `"permitido": true` (com `nota` explicando) quando o
clique for inofensivo, por exemplo "Salvar filtro" local, e o bloqueio de rede continua ativo.

## 3. Privacidade

O `anonimizador.js` intercepta as respostas `fetch` das rotas em `privacidade.rotas`:
- troca os valores das chaves em `chaves_nome` por nomes fictícios **coerentes** (o mesmo
  cliente vira sempre o mesmo nome fictício, inclusive o primeiro nome dentro de mensagens);
- mascara telefones (`•••••1234`);
- respostas acima de 150 KB são percorridas campo a campo (substituição global travaria a
  página);
- não inclua chaves genéricas como `nome` se elas também nomeiam unidades, produtos etc.

Os prints que você traz para a conversa já vêm anonimizados. Se algum dado pessoal escapar,
corrija a config **antes** de gravar o resto.

## 4. Dados ilustrativos

Telas vazias ou com conteúdo inadequado recebem dados de demonstração **só no navegador**,
via ganchos em `<projeto>/demo/*.js` (modelo em `assets/adaptadores/demo_exemplo.js`).
- Derive de dados reais anonimizados sempre que possível: fica verossímil.
- Dê **ids próprios** aos itens: muitos fronts recolocam o objeto original pelo id.
- Use datas recentes para caber nos filtros de período.
- Limite o gancho à tela certa (`location.pathname`).
- **Sempre avise o usuário** na entrega quais telas foram ilustrativas.

## 5. Sessão (login)

Nunca digite senha real. Opções, em ordem de preferência:

| Tipo | Quando | Como |
|---|---|---|
| `nenhum` | Página pública | Nada a fazer |
| `storage` + token do backend | Sistema com JWT/localStorage | Com **OK explícito do usuário** (portão C), gere um token temporário de um usuário neutro dentro do container da API (modelo em `assets/adaptadores/sessao_jwt_backend.exemplo.py`) e grave `<raiz>/segredos/sessao.json` (chmod 600) |
| `storage` + cookie de sessão de teste | Ambiente local/homologação com conta de teste | O usuário fornece; nunca de produção |

Formato de `sessao.json`:

```json
{"localStorage": {"app_access_token": "…", "app_refresh_token": "…"},
 "cookies": [{"name": "sid", "value": "…", "domain": "app.exemplo.com", "path": "/"}]}
```

Escolha um usuário com nome neutro ("Admin Demo"): ele aparece no canto da tela. Ao fim:
`pipeline.sh <proj> limpar` (apaga com `shred`).

## 6. Segredos

- Chave da ElevenLabs: só por `scripts/local/enviar_segredo.sh` (pipe, chmod 600, nunca
  impressa). Dentro do container entra como volume somente leitura.
- Nada de chave, token ou `sessao.json` em git, logs, prints ou mensagens.
- Se uma chave apareceu em arquivo de exemplo do usuário, recomende trocá-la.
