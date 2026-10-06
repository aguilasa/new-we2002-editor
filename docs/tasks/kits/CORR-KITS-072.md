---
id: CORR-KITS-072
---

# CORR-KITS-072 — Acertar os números do ajuste conjunto na §4.3 com o que o --attach imprime

Origin: [KITS-TASK-43](/docs/tasks/kits/43-medir-encaixe-mangas.md)

## Problem

A §4.3 diz que um ajuste sozinho erra "cerca de 1 px" e um ajuste de duas seções "de 2 a 7 px, sem um par que caia no erro de uma seção". A ferramenta imprime ajustes sozinhos de 0,56–2,18 px mais 16,69 px na seção 99 do goleiro, e ajustes conjuntos de 1,28–9,00 px. O par 95+2 do jogador 1 dá 1,28 px contra 1,09 px sozinho, dentro da faixa individual. O próprio Log da task cita a faixa certa (1,28 a 9,00) e a exceção de 16,69, então o plano contradiz o Log.

## Evidência

```text
$ grep -n "2 a 7\|cerca de 1 px" docs/PLAN-KITS-PY.md
633:projetiva geral ajustada a cada seção sozinha erra cerca de 1 px. Ajustada a
634:duas seções juntas, erra de 2 a 7 px, sem um par que caia no erro de uma seção
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach 5 --frame-json work/kits-oracle/attach-5.json | grep -E "section +(95|98|99), "
  player  1 ( 44 prims) section  95,  9 point(s): alone 1.09 px; one camera with section 2 1.28 px, ...
  player  3 ( 44 prims) section  98,  9 point(s): alone 1.90 px; one camera with section 95 6.38 px, 8 7.06 px, 96 9.00 px
  player  5 ( 28 prims) section  99,  8 point(s): alone 16.69 px; ...
```

## Root cause

Hipótese: o parágrafo da §4.3 foi escrito de memória ou de uma corrida anterior, em vez de colado da ferramenta na HEAD.

## Fix

No parágrafo "Negativa medida" da §4.3 de `docs/PLAN-KITS-PY.md`: citar 0,56–2,18 px sozinho (16,69 px na seção 99), 1,28–9,00 px conjunto, e tirar "sem um par que caia no erro de uma seção".

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Verificação

`grep -n "2 a 7 px" docs/PLAN-KITS-PY.md` casa a linha 634 hoje; vazio depois do conserto.

## Log de Execução
