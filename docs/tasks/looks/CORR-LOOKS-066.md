---
id: CORR-LOOKS-066
title: "Correção: a divisão da LOOKS-TASK-31 não chegou a cinco textos — a §10.3 (o) segue \"PARCIAL\", e o close-up e o cenário ainda apontam para a 31"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-066: a 31 fechou dividida, e cinco textos ainda a leem aberta

## Problema identificado

A [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md) fechou em
2026-09-21 dividida, a pedido do usuário. O que faltava virou as
[`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) a
[`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md). O commit do
fechamento (`4772b67`) tocou a task, o plano, o `progresso.md` e as tasks
novas. Cinco textos ficaram como estavam antes da divisão:

1. **O cabeçalho da §10.3 (o) do plano diz `PARCIAL em 2026-09-20`.** O
   veredito no fim da mesma seção diz que a task fecha em 2026-09-21, e as
   vizinhas (m), (s) e (n) dizem `FECHADA em <data>`. O critério 4 da task —
   *"§10.3 (o) com o veredito e a data"* — está marcado, e a data escrita no
   cabeçalho é a da primeira passada.
2. **O `CLAUDE.md` põe na 31 o que foi para a 36–40:**
   - *"faltam o painel e o cenário (task 31) e a caminhada (fase 11)"*: a 31
     está fechada, e o que falta da tela são as 36 a 40;
   - *"o close-up por linha é da task 31"*: foi para a
     [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md), e a
     [`LOOKS-TASK-33`](/docs/tasks/looks/33-a-janela-animada.md) já depende dela;
   - *"as fases 8 a 11 (tasks 21 a 35)"*: agora são 21 a 40.
3. **O cabeçalho do `progresso.md` diz** *"As tasks 21 a 35 são as Fases 8 a
   11"*, na mesma página que lista as 36 a 40 na fase 10.
4. **A docstring de `tools/looks/ui/looks_set.py` diz o contrário do que a
   janela faz:** *"NOT measured, and therefore not claimed: the colours, the
   gradient of the panel, the borders and the typeface. Whether the scenery is
   an image off the disc or polygons of the GPU is LOOKS-TASK-31, and until it
   is measured this draws a plain arrangement"*. Cores, degradês e borda estão
   medidos, e a janela pinta os 43 pacotes (`scene.furniture_picture`). Só a
   fonte continua sendo a do Qt, e isso é da
   [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md).
5. **"17 ladrilhos do painel cada"** (task, segunda passada, e §10.3 (o)) vale
   para o slot 2 só. O slot 1 imprime **12** e **18**, e nos dois slots a
   ferramenta diz *"over help, panel"* — a ajuda entra junto com o painel.

## Evidência

Na árvore de `4772b67`:

```text
$ grep -n "task 31\|21 a 35" CLAUDE.md docs/tasks/looks/progresso.md
CLAUDE.md:818:**aberto**, com as fases 8 a 11 (tasks 21 a 35). O alvo da v2 é a própria tela
CLAUDE.md:822:uniforme do time (task 30); faltam o painel e o cenário (task 31) e a
CLAUDE.md:917:  por linha é da task 31.
docs/tasks/looks/progresso.md:37:mostra. As tasks 21 a 35 são as Fases 8 a 11, e a fonte de verdade delas é a

$ grep -n "^\*\*(o)" docs/PLAN-LOOKS-PY.md
2955:**(o) O painel e o cenário — PARCIAL em 2026-09-20.** Se o degradê, a borda, a

$ python tools/looks/oracle.py --pages
  -- slot 2 (outfield player) --
    page (512,256): 17 tile(s) of the screen change, over help, panel
    page (576,256): 17 tile(s) of the screen change, over help, panel
  -- slot 1 (goalkeeper) --
    page (512,256): 12 tile(s) of the screen change, over help, panel
    page (576,256): 18 tile(s) of the screen change, over help, panel
oracle --pages: 0 problem(s) over 2 slot(s)
```

O resto do que a task afirma reproduz: `--scenery` com **43 pacotes** (13 + 1
\+ 5 + 24) e **142 sprites** nas duas leituras e nos dois slots, a fonte em 1.068
de 1.068 texels do `EDT_2D.BIN`, o controle deslocado divergindo em 1.502 de
2.128; `--outside` com barra 3, fundo 3 e 3, painel 4, ajuda 4, faixas 6;
`looks_ui` com 12 de 12 controles e 33 pacotes amostrados.

## Causa raiz

O fechamento dividido reescreveu a task, o plano e o progresso a partir do
veredito, e não varreu os lugares que citavam a 31 como a dona do close-up e do
cenário.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md`

O cabeçalho da §10.3 (o) passa a `FECHADA em 2026-09-21`, no formato das
vizinhas, dizendo que a fecha a medição e a mobília e que o resto é das 36 a 40.
E o "17 ladrilhos do painel cada" diz os dois slots e as duas regiões, como a
ferramenta imprime.

### Arquivo: `CLAUDE.md`

- "tasks 21 a 35" vira "tasks 21 a 40";
- "faltam o painel e o cenário (task 31)" diz o que falta: os sprites, o
  texto, o alinhamento, a ajuda e o close-up (36 a 40);
- "o close-up por linha é da task 31" vira task 40.

### Arquivo: `docs/tasks/looks/progresso.md`

"As tasks 21 a 35 são as Fases 8 a 11" vira "21 a 40".

### Arquivo: `tools/looks/ui/looks_set.py`

A docstring diz o que está medido e pintado (a mobília, pela lista do GPU) e
o que ainda não está: a fonte do jogo, da LOOKS-TASK-37.

### Arquivo: `docs/tasks/looks/31-o-painel-e-o-cenario.md`

O "17 ladrilhos do painel cada" da segunda passada ganha a nota com o slot 1,
sem reescrever o que foi escrito naquela passada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `CLAUDE.md` | modificar |
| `docs/tasks/looks/progresso.md` | modificar |
| `tools/looks/ui/looks_set.py` | modificar (só docstring) |
| `docs/tasks/looks/31-o-painel-e-o-cenario.md` | modificar |

## Verificação

- [ ] `grep -n "task 31\|21 a 35" CLAUDE.md docs/tasks/looks/progresso.md` não
      alcança mais o close-up nem o cenário como pendentes
- [ ] o cabeçalho da §10.3 (o) diz `FECHADA em 2026-09-21`
- [ ] os ladrilhos do `--pages` citados com os dois slots, iguais ao que a
      ferramenta imprime
- [ ] `python tools/looks/selftest.py --quiet` verde (a regra 1 varre a
      docstring)
- [ ] `python tools/check_tasks.py` ok
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
