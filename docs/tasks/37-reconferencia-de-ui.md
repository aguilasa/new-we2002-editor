---
id: WTE-TASK-37
title: "Reconferência dos 18 formulários, com a lógica ligada"
type: verificação
category: ui
phase: 6
depends_on: ["WTE-TASK-34"]
status: pendente
---

# WTE-TASK-37: Reconferência de UI

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 4.
- A WTE-TASK-12 conferiu os formulários **vazios**. Este confere com dado
  carregado e com a lógica ligada — que é quando os problemas de verdade
  aparecem.

Diferenças que só existem agora: rótulo que cabia vazio e não cabe com o nome de
um time real; combo populado com 63 entradas em vez de nenhuma; imagem de camisa
desenhada por cima do que era espaço reservado; controle habilitado ou
desabilitado por estado.

---

## Objetivo

Passar pelos 18 de novo, com imagem carregada, e comparar com o original no
mesmo estado.

### Método

Mesmo da WTE-TASK-12 — captura dos dois lados no `:99`, inspeção humana, sem
tolerância de pixel — com uma diferença: **mesmo estado dos dois lados**. Abrir
a mesma ROM, selecionar o mesmo time, o mesmo jogador.

### O que procurar agora

| Achado | Onde volta |
|---|---|
| rótulo cortado por dado real | decisão: aceitar ou alargar |
| controle habilitado/desabilitado errado | spec do handler (Fase 4) |
| ordem de itens em combo | carga (WTE-TASK-25) |
| imagem não desenhada ou desenhada errada | render (WTE-TASK-29) |
| foco inicial e ordem de tabulação | DFM (`TabOrder`) — o gerador preservou? |

### `TabOrder` e o botão default

O `newWe2002` levou uma mordida aqui: `PUSHBUTTON` do `.rc` precisou sair com
`autoDefault=false`, senão `Return` clicaria um botão arbitrário — e um dos
candidatos aplicava formação predefinida sobre o time selecionado.

O risco equivalente existe: `lista_formacionesClick` é destrutivo. Conferir o
que `Return` faz em cada formulário, nos dois lados.

### As 37 `TStaticText`

Reconferir a decisão da WTE-TASK-12 com fundo real desenhado atrás.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual.md` | modificar — segunda passada |
| `wte/re/visual/carregado/*.png` | criar |

---

## Critério de conclusão

- [ ] Os 18 reconferidos com a mesma ROM e o mesmo estado dos dois lados
- [ ] `TabOrder` e comportamento de `Return` conferidos por formulário
- [ ] Nenhuma ação destrutiva alcançável por `Return`
- [ ] Decisão das `TStaticText` reconferida com fundo real
- [ ] Achado que volta para outra fase registrado com a task de destino
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
