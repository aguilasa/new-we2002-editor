---
id: CORR-KITS-067
---

# CORR-KITS-067 — Versionar como controle o vermelho do pixel_index

Origin: [KITS-TASK-38](/docs/tasks/kits/38-medir-costas-numero.md)

## Problem

O vermelho do Log da KITS-TASK-38 para a parte pura (ordem de byte do `pixel_index` trocada, três verificações falham) foi uma edição à mão depois revertida. Nenhum controle versionado o refaz a partir da HEAD: o `tools/kits/controls.py` não tem planta de `--back` nem de `pixel_index`. As seis verificações de `--back` do selftest afirmam a lógica do juiz sobre uma página sintética, mas nada no `controls.py` reprova que elas fiquem vermelhas se o decodificador regredir.

## Evidência

```text
$ grep -n -i "back\|pixel_index" tools/kits/controls.py
(sem saída)
$ S=$(mktemp -d); git archive 71cd597 tools docs src data CMakeLists.txt | tar -x -C $S; cd $S
$ python3 - <<'PY'
p='tools/kits/oracle.py'; s=open(p).read()
old='return word & 0xFF if x % 2 == 0 else word >> 8'
assert old in s; s=s.replace(old,'return word >> 8 if x % 2 == 0 else word & 0xFF'); open(p,'w').write(s)
PY
$ python3 tools/kits/selftest.py | grep -E "FAIL  oracle --back|oracle:"
  FAIL  oracle --back: the copy is found at (44,6), inside the shirt back  [] None
  FAIL  oracle --back: --expect-back written holds
  FAIL  oracle --back: a disc page that differs outside the gaps fails
oracle: 3 failure(s)
```

## Root cause

Hipótese: o vermelho foi visto uma vez à mão e nunca virou planta na lista de controles.

## Fix

Em `tools/kits/controls.py`, um controle que troca a paridade em `oracle.pixel_index` e exige que o `kits_selftest` fique vermelho.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`

## Verificação

`python3 tools/kits/controls.py | tail -1` reporta um controle a mais que "24 of 24 controls red", e esse controle vermelho.

## Log de Execução

Reproduzido em 2026-10-05 sobre `2f1a3ec`: `grep -n -i "back\|pixel_index" tools/kits/controls.py`
não dá saída. Nenhum controle refaz o vermelho do `pixel_index`.

Conserto: controle `oracle-back-byte-order` em `tools/kits/controls.py`. Ele troca as duas metades
do halfword em `oracle.pixel_index` (o par passa a ler o byte alto) e exige
`FAIL  oracle --back: the copy is found at (44,6), inside the shirt back` no `kits_selftest` da
cópia.

```text
$ python3 tools/kits/controls.py --only oracle-back-byte-order
  base   unplanted sandbox            selftest exit 0
  RED    oracle-back-byte-order       kits/oracle.py :: pixel_index
controls: 1 of 1 red
$ python3 tools/kits/controls.py | tail -1
controls: 25 of 25 red
```

Nenhum documento repete o total de controles (`grep -rn "24 of 24"` no plano, no perfil e em
`tools/kits/` dá vazio). Quem o imprime é o próprio `controls.py`.
