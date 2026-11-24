# 02 · Descoberta: entender o módulo

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

O objetivo é saber, para cada tela: o que existe, como se chama na interface, o que é
perigoso clicar e quais dados podem expor clientes. Há duas fontes: o **crawler** (sempre)
e o **código-fonte** (quando houver). As duas juntas dão um mapa confiável.

## 1. Crawler (sempre)

```bash
ssh <host> "bash <raiz>/skill/scripts/vps/pipeline.sh <proj> descobrir"
# ou rotas avulsas: ... descobrir --rotas /clientes,/clientes/novo --espera 8
```

Gera em `descoberta/`:
- `<rota>.png` (tela visível) e `<rota>_inteira.png` (página inteira);
- `mapa.json` com, por tela, os elementos visíveis (`papel`, `texto`, `rotulo`, `placeholder`,
  posição), as tabelas (colunas e número de linhas), os contêineres roláveis e a lista
  `risco` (botões que batem com `botoes_proibidos`).

Traga os prints para a conversa (`scripts/local/trazer.sh` ou `scp`) e **olhe todos**.
Procure:
- telas vazias ou com dados ruins para demonstrar (vão precisar de dado ilustrativo);
- conteúdo constrangedor (mensagens internas, testes, palavrões);
- nomes e telefones reais (confirme que a privacidade da config cobre essas rotas);
- menu cortado (vai precisar rolar a navegação);
- skeletons demorados (rotas pesadas vão para `privacidade.cache_rotas`).

`networkidle` nunca é usado: apps com polling nunca ficam "ociosos". O crawler espera
`domcontentloaded` + alguns segundos.

## 2. Código-fonte (quando houver)

Leia, sem rodar nada localmente:

| O que | Onde costuma estar | Para quê |
|---|---|---|
| Rotas do módulo | `App.tsx`, `router.*`, `routes/` | `sistema.rotas` e `tela` das cenas |
| Itens de menu | `nav.ts`, `sidebar.*` | Cena de menu (`navegar_menu`) |
| Rótulos visíveis | `grep -oE 'title="[^"]+"\|label="[^"]+"\|placeholder="[^"]+"'` | Âncoras e alvos exatos |
| Estados e enums | tipos TS, models | Abas, colunas de kanban, filtros |
| Formato das respostas da API | client/api, serializers | `privacidade.chaves_nome`, ganchos de demo |
| Como a sessão é guardada | `localStorage.setItem`, cookies | `sessao.json` |
| Botões que disparam algo | `onClick` → `POST/PUT/DELETE` | Lista de "nunca clicar" |
| O que fica desabilitado e por quê | `disabled={…}` | A fala não promete o que a tela não mostra |

## 3. Mapa de riscos

Antes do roteiro, escreva (na conversa) uma tabela curta:
- botões de disparo da tela e o que fazem;
- campos com dados pessoais;
- telas que precisam de dado ilustrativo e de onde ele vem (de preferência derivado de
  dado real anonimizado, para parecer verdadeiro).

## 4. Prova no modo real

O crawler roda sem janela. Para interações (abrir gaveta, modal, editor), confirme os
alvos já na prévia (fase 7), que roda no mesmo modo da gravação final.
