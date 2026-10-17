---
id: CORR-KRP-027
---

# CORR-KRP-027 — §3.2 ainda diz que a pele do corpo não muda, e o Feito da §3.3 não credita a KRP-TASK-24

Origin: [KRP-TASK-24](/docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md)

## Problem

A §3.3 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#3.3) revoga, para a figura da aba, o
"inclusive a pele do corpo" da §3.2. Mas a §3.2 continua dizendo, sem ressalva, que a pele do corpo
não muda, e não remete à revogação.

A linha de fechamento da §3.3 também continua dizendo que a seção inteira foi feita pelas KRP-TASK-22
e 23 "como escrito acima e sem diferença do texto". O parágrafo da pele, logo acima dessa linha, foi
escrito depois das duas e é entregue pela KRP-TASK-24.

A task declara o `docs/PLAN-KITS-REPLAY.md` no "In", mas o commit de entrega a0bec3f8 não o toca; só
o commit de decisão 34763c76 toca. Isso fere a regra do `CLAUDE.md` "Fechar um veredito é varrer quem
dizia o anterior".

## Evidência

```text
$ sed -n 261,263p docs/PLAN-KITS-REPLAY.md
ela deixa parte das primitivas da 46 na coluna do disco, e o jogo pinta todas. **O resto da figura
não muda**, inclusive a pele do corpo, que nenhum replay mediu. No `match_scene`, a seção da cabeça
$ sed -n 326,328p docs/PLAN-KITS-REPLAY.md
**Feito na fase 3a** ([KRP-TASK-22](...22-painel-de-controles-da-cabeca-na-aba-3d.md)
e [23](...23-fechamento-da-fase-3a.md)), como escrito acima e sem diferença
$ git show --stat a0bec3f8 | grep PLAN
(sem saída)
$ sed -n 255,330p docs/PLAN-KITS-REPLAY.md | grep -c "KRP-TASK-24\|24-pele-do-corpo"
0
```

## Root cause

(Hipótese.) A decisão foi escrita na §3.3 antes da implementação (34763c76), e o commit da
implementação não voltou nem à frase mais antiga da §3.2 nem à linha "Feito", que é anterior ao
parágrafo novo.

## Fix

No `docs/PLAN-KITS-REPLAY.md`:

- na linha 262 da §3.2, remeter à §3.3 para a pele do corpo da figura da aba, mantendo a parte do
  `match_scene`;
- trocar a linha "Feito" da §3.3 para creditar à KRP-TASK-24 o parágrafo da pele.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-REPLAY.md`

## Verificação

```sh
sed -n 255,330p docs/PLAN-KITS-REPLAY.md | grep -c "KRP-TASK-24\|24-pele-do-corpo"
```

Hoje imprime 0. Depois do conserto tem de imprimir pelo menos 1, e a frase "inclusive a pele do
corpo" tem de estar ao lado de uma referência à §3.3.

## Log de Execução
