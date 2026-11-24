# 04 · Biblioteca de padrões de interação

<!-- Tutor™ by Azvor · AZVOR-NR-1.0 · ID AZVT-TUTOR-9C41 -->

Cada passo do roteiro tem `fazer` (o padrão) e `quando` (trecho da fala ou segundos desde o
início da fala). A implementação está em `scripts/motor/padroes.py`. Se precisar de um
padrão novo, acrescente um método `@padrao` lá e registre os parâmetros obrigatórios em
`scripts/roteiro/validar_roteiro.py`. Não escreva coreografia em Python solto no projeto.

## Alvos

Um alvo descreve o elemento pelo que ele **é**, nunca por coordenada:

| Campo | Exemplo | Resolve com |
|---|---|---|
| `texto` | `"Detratores"` | texto visível (filtra elementos ocultos) |
| `papel` + `texto` | `{"papel": "button", "texto": "Filtros"}` | papel de acessibilidade + nome |
| `rotulo` | `{"rotulo": "Celular (com DDD)"}` | campo pelo `<label>` |
| `placeholder` | `{"placeholder": "Buscar cliente"}` | campo pelo placeholder |
| `contexto` | `{"texto": "Salvar", "contexto": "Enviar teste"}` | procura dentro do card/seção que contém o texto do contexto |
| `seletor` | `{"seletor": "tbody tr", "indice": 2}` | CSS/XPath (último recurso) |
| `indice` | `1` | qual ocorrência (começa em 0) |
| `exato` | `true` | texto idêntico (evita "Pesquisas" casar com "Pesquisas enviadas") |

Uma string simples vale como `{"texto": ...}`. Papéis úteis: `button`, `link`, `tab`,
`tablist`, `heading`, `textbox`, `combobox`, `checkbox`, `row`, `dialog`, `navigation`.

## Padrões

| `fazer` | Parâmetros | O que acontece | Use quando |
|---|---|---|---|
| `apontar` | `alvo`, `segundos=0.7`, `dx`, `dy`, `rolar=true` | Cursor vai até o elemento (rola antes se estiver fora da tela) | A fala cita algo |
| `destacar` | `alvo`, `segundos=2.5`, `margem=6`, `card=false`, `apontar=false` | Anel na cor de destaque + véu leve no resto | Dar ênfase. `card:true` sobe até o card que contém o alvo |
| `clicar` | `alvo`, `segundos`, `permitido=false` | Move, pausa, clica com a animação de clique | Navegar, abrir, alternar. **Recusa botões de disparo** |
| `rolar_ate` | `alvo` ou `y`, `deslocamento=90`, `segundos=1.2`, `conteiner` | Rolagem suave até o alvo ficar a N px do topo | Próximo assunto fora da tela |
| `trocar_aba` | `aba` | Procura tab → botão → texto, clica, espera o conteúdo | Abas e segmentos |
| `pesquisar` | `campo`, `termo`, `atraso=95` | Clica no campo, limpa e digita com ritmo humano | Busca. Escolha termo que retorna resultado |
| `filtrar` | `filtro`, `opcao` | Abre o filtro e escolhe a opção | Dropdowns de filtro, popovers |
| `selecionar` | `campo`, `opcao` | `<select>` nativo (sem abrir lista) ou dropdown customizado | Campos de seleção |
| `abrir_detalhe` | `linha` (índice ou texto), `tabela="tbody tr"` | Clica na linha e espera gaveta/modal | Ficha, detalhe, histórico |
| `fechar_detalhe` | — | Esc | Voltar para a lista |
| `preencher_formulario` | `campos{rotulo: valor}`, `contexto` | Campo a campo: rótulo → placeholder → texto ao lado | Cadastro, envio de teste. **Use dados claramente fictícios** |
| `ate_o_disparo` | `botao`, `segundos=3.5` | Leva o cursor ao botão final e destaca. **Nunca clica** | Fim de todo fluxo que envia/salva |
| `percorrer` | `itens[]`, `segundos`, `pausa`, `destacar`, `card` | Passa por uma sequência de alvos | KPIs, colunas de kanban, blocos de fluxo |
| `navegar_menu` | `item`, `clicar=true`, `conteiner="nav"` | Rola a navegação até o item e clica (ou só destaca) | Apresentar o menu, trocar de tela "como usuário" |
| `paginar` | `direcao=proxima` | Clica em Próxima/Anterior | Listas paginadas |
| `digitar` / `tecla` | `texto` / `tecla` | Teclado | Atalhos, ajustes finos |
| `esperar` | `segundos` | Pausa | Respiro antes de um destaque importante |
| `mover_para` | `x`, `y`, `segundos` | Cursor para uma posição livre | Tirar o cursor da frente no fim |
| `navegar` | `url` | Abre a rota sem animação | Raro; prefira `tela` da cena ou `navegar_menu` |

## Receitas por tipo de tela

| Tela | Receita |
|---|---|
| Dashboard | `apontar` no número principal → `destacar card:true` em cada card na frase que o cita → `percorrer` filtros do topo |
| Gráficos | `rolar_ate` o título (deslocamento 70–90) → `destacar card:true` → `apontar` em pontos da série |
| Lista + busca + filtros | `apontar` linha → `trocar_aba` por aba citada → `filtrar` → `pesquisar` |
| Detalhe | `abrir_detalhe` → `apontar` seções → `trocar_aba` interna → `apontar` botões de ação (sem clicar) → `fechar_detalhe` |
| Kanban | `percorrer` colunas com `destacar card:true` no ritmo "nova, em andamento, concluída" |
| Editor/fluxo | `apontar` blocos de cima para baixo com `rolar_ate` do canvas |
| Simulador | `preencher_formulario`/`selecionar` → `destacar` o resultado |
| Configuração | `destacar card:true` por seção → `rolar_ate` a próxima |
| Envio/cadastro | `preencher_formulario` com dados fictícios → `ate_o_disparo` |

## Campos extras da cena

- `tela`: rota (ou URL). Sem `tela`, a cena continua de onde a anterior parou. Se ela for
  regravada sozinha, o motor usa a tela da última cena anterior que tem `tela`.
- `pronto_quando`: alvo que indica "carregou" (espera até 60 s).
- `espera_extra`: segundos depois de pronto (padrão 2).
- `preparo`: passos executados **antes** de gravar (ex.: já deixar a aba Detratores aberta).
- `duracao`: só para cenas sem fala.
