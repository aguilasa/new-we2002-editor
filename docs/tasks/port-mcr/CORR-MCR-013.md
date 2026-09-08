---
id: CORR-MCR-013
title: "Correção: a §3.2 do plano ainda põe `Card` como dataclass do `model.py`, e a task cita a §5.1 no lugar dela"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-013: o inventário de módulos do plano não acompanhou o que a MCR-TASK-09 entregou

## Problema identificado

A linha 295 do plano — dentro da árvore de módulos da **§3.2** — continua
dizendo:

```text
  model.py        Card / Player / Formation -- dataclasses, sem Qt, sem endereco
```

O que a MCR-TASK-09 entregou é outra coisa, e **de propósito**:

| o que a §3.2 diz | o que existe |
|---|---|
| `Card` é dataclass do `model.py` | `Card` é **classe comum** e mora em `card.py` desde a MCR-TASK-04 |
| `Player` é dataclass do `model.py` | confere |
| `Formation` é dataclass do `model.py` | é dataclass, mas mora em `formation.py` (MCR-TASK-08); o `model.py` a reexporta |
| — | **`Save`**, a dataclass central do modelo, não é mencionada em lugar nenhum do plano |

O critério de conclusão da task registra a divergência e a justifica ("o
contêiner `card.Card` continua classe comum — ele guarda um `bytearray` mutável
e valida no construtor, e `@dataclass` ali não acrescentaria nada"), o que está
certo. O que não aconteceu foi levar a decisão ao plano — que é a **fonte de
verdade**, e cujo perfil manda "onde este perfil e o plano divergirem, o plano
ganha".

O commit `16a0ae0` editou a linha **imediatamente abaixo** dessa
(`io.py` → `mcrio.py`, com o parágrafo do motivo), então a linha errada estava
sob os olhos.

**E a referência de seção está trocada.** O critério atribui a frase à §5.1:

> A §5.1 escrevia "`Card`, `Player` e `Formation`"

A §5.1 (linha 429) é "Round-trip byte-idêntico" e não nomeia classe nenhuma.
Quem escreve isso é a §3.2 (linha 283, a linha 295).

## Evidência

```
$ grep -n "model.py" docs/PLAN-MCR-PY.md
295:  model.py        Card / Player / Formation -- dataclasses, sem Qt, sem endereco

$ grep -n '\bSave\b' docs/PLAN-MCR-PY.md
(vazio)

$ grep -n "^### 5.1\|^### 3.2" docs/PLAN-MCR-PY.md
283:### 3.2 Os módulos
429:### 5.1 Round-trip byte-idêntico
```

E a árvore:

```
$ grep -n '^class Card\|^class Formation\|^@dataclasses.dataclass' \
      tools/mcr/card.py tools/mcr/model.py tools/mcr/formation.py
tools/mcr/model.py:58:@dataclasses.dataclass      <- Player
tools/mcr/model.py:77:@dataclasses.dataclass      <- Save
tools/mcr/formation.py:60:@dataclasses.dataclass
tools/mcr/formation.py:61:class Formation:
tools/mcr/card.py:100:@dataclasses.dataclass      <- a entrada de diretorio
tools/mcr/card.py:141:class Card:                 <- sem decorador
```

`Card` sai de `card.py` **sem decorador**; `Player` e `Save` saem de
`model.py`, decorados; `Formation` sai de `formation.py`.

## Causa raiz

A task documentou a divergência no próprio critério em vez de corrigir o
inventário de módulos do plano, e apontou a seção errada ao fazê-lo.

## Correção

### Arquivo: `docs/PLAN-MCR-PY.md`

Trocar a linha 295 pelo que existe, e nomear o `Save`:

```text
  model.py        Player / Save -- dataclasses sobre os bytes crus, sem Qt,
                  sem endereco (o contêiner `Card` mora em card.py e é classe
                  comum; `Formation` mora em formation.py)
```

Não é caso de renomear nada no código: a distribuição atual é a que a Regra 2
pede — o contêiner guarda o `bytearray`, o modelo é uma **vista** sobre ele.

### Arquivo: `docs/tasks/port-mcr/09-modelo-e-round-trip.md`

Corrigir a referência de seção no primeiro item do critério de conclusão: é a
**§3.2**, não a §5.1.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-MCR-PY.md` | modificar |
| `docs/tasks/port-mcr/09-modelo-e-round-trip.md` | modificar |

## Verificação

- [x] `grep -n "model.py" docs/PLAN-MCR-PY.md` nomeia `Player` e `Save`, e não
      atribui `Card` ao `model.py`
- [x] `grep -n '\bSave\b' docs/PLAN-MCR-PY.md` deixa de sair vazio
- [x] a citação de seção do critério da MCR-TASK-09 diz §3.2
- [x] conferência de forma e de existência de link de `.claude/rules/links.md`
      vazias
- [x] `python3 tools/check_tasks.py` e `ctest -R tasks` verdes

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

Os três `grep` da Evidência reproduziram exatos: a linha 295 dizia
`Card / Player / Formation`, `grep -n '\bSave\b' docs/PLAN-MCR-PY.md` saía
**vazio**, e as seções são 283 (§3.2) e 429 (§5.1). A árvore confirma a
distribuição: `card.py:141` tem `class Card` **sem decorador**, `model.py:58` e
`model.py:77` são `Player` e `Save` decorados, `formation.py:60` é
`Formation`.

O inventário de módulos do plano passou a nomear `Player` e `Save`, e a dizer
onde `Card` e `Formation` moram — inclusive que o `model.py` reexporta a
`Formation`, que é o que faz a leitura antiga parecer certa. Nada mudou no
código: a distribuição atual é a que a Regra 2 pede, com o contêiner guardando
o `bytearray` e o modelo sendo vista sobre ele.

A citação de seção do critério da MCR-TASK-09 passou de §5.1 para **§3.2**. As
outras quatro menções à §5.1 na mesma task ficaram: o `fonte_de_verdade`
(§5.1 é o round-trip, que é o que esta task mede), a referência do Contexto, e
as duas sobre a companheira da forma 2 — nenhuma delas fala de classe.

**Problemas encontrados:**

**A varredura puxou a MCR-TASK-14, que a lista da CORR não previa.** O quadro
de recontagem dela tem um item sobre a §3.2, e ele só cobria o primeiro erro
daquela linha (`io.py` → `mcrio.py`, corrigido na MCR-TASK-09). A **mesma
linha** errava uma segunda vez, que é esta correção — e sem dizê-lo, a
verificação final reconferiria só metade do que a linha afirma. O item ganhou a
cláusula, com o comando que confronta o plano contra o disco.

**Medições:**

| gate | número |
|---|---|
| `grep -n "model.py" docs/PLAN-MCR-PY.md` | nomeia `Player / Save`, e não atribui `Card` ao `model.py` |
| `grep -c '\bSave\b' docs/PLAN-MCR-PY.md` | **1** (era 0) |
| a citação do critério da MCR-TASK-09 | **§3.2** |
| conferência de forma de link | só alvo fora de `docs/` (`../NOTICE.md`, `../CLAUDE.md`, `../wte/re/mcr.md`) |
| conferência de existência de link | **vazia** |
| `tools/check_tasks.py` | **100 task(s), ok** |
| `ctest -R tasks` | **1/1 Passed** |

**Arquivos criados/modificados:**

- `docs/PLAN-MCR-PY.md` — a linha 295 da §3.2
- `docs/tasks/port-mcr/09-modelo-e-round-trip.md` — a citação de seção
- `docs/tasks/port-mcr/14-verificacao-final.md` — a cláusula do quadro de
  recontagem (varredura de discrepância)
