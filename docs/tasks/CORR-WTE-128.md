---
id: CORR-WTE-128
title: "Correção: o item 1 da §8.4 não tem roteiro, e a seção afirma que os cinco têm"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-128: o clamp de habilidade é o único dos cinco sem estímulo versionado

## Problema identificado

A §8.4 do [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) abre assim:

> **Os cinco conferidos** pela [PAR-TASK-04](/docs/tasks/PAR-TASK-04.md) — o
> primeiro em 2026-08-28, os outros quatro em 2026-08-29. **Roteiros em
> `tools/par/8.4-*.sh`**, todos sobre o `8.4-prelude.sh`, que abre o
> `PlayerSkillsDialog`.

São quatro roteiros para cinco itens. **O item 1 — o clamp de habilidade em
`12..19`, o único medido em 2026-08-28 — não tem nenhum:**

| item da §8.4 | roteiro |
|---|---|
| 1 — clampar habilidade abaixo de 12 e acima de 19 | **nenhum** |
| 2 — altura, idade e número nos dois extremos | `8.4-limites-fisicos.sh` |
| 3 — custo com mais de 2 dígitos | `8.4-custo.sh` |
| 4 — os 10 combos, mouse e teclado | `8.4-combos.sh` |
| 5 — nome de jogador | `8.4-nome-jogador.sh` |

A data explica e não desculpa: o item 1 foi medido no mesmo dia em que a
[CORR-WTE-123](/docs/tasks/CORR-WTE-123.md) criou o `tools/par/`, e os outros
quatro no dia seguinte, já com a convenção em pé. O que sobra é uma seção que
**afirma** cobertura que não tem — a frase "Roteiros em `tools/par/8.4-*.sh`"
vem logo abaixo de "Os cinco conferidos", e quem ler vai procurar cinco.

É a mesma família da [CORR-WTE-126](/docs/tasks/CORR-WTE-126.md), aberta na
§8.2 pelo mesmo motivo, e a §8.4 é agora a **segunda** seção incompleta:

```text
$ for s in 8.1 8.2 8.3 8.4; do
    printf "%s: %s roteiro(s) para %s itens\n" "$s" \
      "$(ls tools/par/$s-*.sh | wc -l)" "$(...)"; done
8.1: 6 roteiro(s) para 5 itens
8.2: 1 roteiro(s) para 3 itens     <- CORR-WTE-126
8.3: 3 roteiro(s) para 3 itens
8.4: 5 roteiro(s) para 5 itens     <- mas um deles é o prelúdio, que não roda
                                      sozinho: são 4 itens cobertos de 5
```

O `8.4-prelude.sh` é o que faz a conta enganar: ele **não é roteiro de item**,
é o prelúdio concatenado antes dos outros, e o próprio cabeçalho dele diz
"não roda sozinho".

## Evidência

```text
$ ls tools/par/8.4-*
tools/par/8.4-combos.sh
tools/par/8.4-custo.sh
tools/par/8.4-limites-fisicos.sh
tools/par/8.4-nome-jogador.sh
tools/par/8.4-prelude.sh

$ head -1 tools/par/8.4-combos.sh
# PARIDADE-FUNCIONAL §8.4, item 4 -- os 10 combos, com mouse E com teclado.
$ head -1 tools/par/8.4-custo.sh
# PARIDADE-FUNCIONAL §8.4, item 3 -- custo com mais de 2 dígitos.
$ head -1 tools/par/8.4-limites-fisicos.sh
# PARIDADE-FUNCIONAL §8.4, item 2 -- altura, idade e número nos dois extremos.
$ head -1 tools/par/8.4-nome-jogador.sh
# PARIDADE-FUNCIONAL §8.4, item 5 -- editar nome de jogador.
```

Os cabeçalhos nomeiam os itens 2, 3, 4 e 5. **O 1 não aparece.**

**Os outros quatro estão certos** — esta revisão rodou os quatro com o golden e
o controle positivo, na `ptbr-remaster.bin`, e todos saíram
`OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`:

| roteiro | o que o controle mostra em `players[462]` |
|---|---|
| `8.4-limites-fisicos.sh` | `height 187→155`, `age 26→15`, `number 1` (piso) |
| idem, com `PAR_H/A/N=999/99/99` | `height 210`, `age 46`, `number 32` |
| `8.4-custo.sh` | `cost 25→12` |
| `8.4-combos.sh` | nove combos +1, `out_of_position` parado em 1 |
| `8.4-nome-jogador.sh` | `name = 4a4f4741444f5278797a` = `JOGADORxyz`, 10 bytes |

E o clamp do item 1 **existe e está certo no código dos dois lados** —
`ClampBox(box, 12, 19)` em `src/app/PlayerSkillsDialog.cpp:154` contra
`if(i<12)` / `if(i>19)` em `legacy/mfc/carattDlg.cpp:409,414`. O que falta é a
corrida que o demonstra pela tela, gravada em arquivo.

## Causa raiz

O item 1 foi medido antes de a convenção do `tools/par/` existir, e o
fechamento do dia seguinte versionou só os quatro itens novos, sem voltar para
ele nem ajustar a frase da §8.4.

## Correção

### Arquivo: `tools/par/8.4-habilidade.sh` (novo)

O estímulo que o Log descreve — **os dois extremos numa corrida só**: `25` em
`TXT_ATTACK` e `3` em `TXT_DEFENCE`, sobre o `8.4-prelude.sh`, com o `par_type`
que já existe. O cabeçalho no molde dos outros quatro: seção, item, time,
jogador e os controles em DLU.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md` §8.4

O nome do roteiro ao lado da faixa no item 1, como os outros quatro já fazem, e
a frase de abertura dizendo que o `8.4-prelude.sh` é prelúdio, não item — senão
a contagem de arquivos continua parecendo cobrir a seção.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.4-habilidade.sh` | criar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar |
| `docs/tasks/PAR-TASK-04.md` | modificar |

## Verificação

- [ ] `ls tools/par/8.4-*` devolve seis arquivos: o prelúdio e um por item
- [ ] O golden com o roteiro novo sai `OK`:
      `WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$(cat prelude; cat roteiro)"
      GOLDEN_GUI_EDIT="$GOLDEN_EDIT" bash tools/golden_check.sh
      roms/ptbr-remaster.bin`
- [ ] O controle positivo mostra `players[462].attack = 19` e
      `players[462].defence = 12` — **remedido**, não copiado do Log
- [ ] A §8.4 nomeia roteiro nos cinco itens
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
