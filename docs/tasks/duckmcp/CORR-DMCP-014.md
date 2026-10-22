---
id: CORR-DMCP-014
---

# CORR-DMCP-014 — Pôr o filtro 0 no vetor fixo de PNG ou parar de dizer cinco filtros

Origin: [DMCP-TASK-13](/docs/tasks/duckmcp/13-hardware-e-pixels.md)

## Problem

O check "a fixed vector of all five filters decodes as Pillow did" e o comentário dele existem para que
um defeito comum a `_filter` e `_unfilter` não passe como ida-e-volta. Mas o `VECTOR_STREAM` usa os
filtros [1, 2, 3, 4, 4], sem o 0. Um defeito comum no filtro 0 (decodificador soma 1, codificador
subtrai 1) passa o selftest inteiro verde.

## Evidência

```text
$ python3 -c "import sys; sys.path.insert(0,'tools'); from duckmcp import png; s=bytes.fromhex(png.VECTOR_STREAM); print([s[r*10] for r in range(5)])"
[1, 2, 3, 4, 4]
```

Planta (numa cópia `git archive HEAD tools`; a indentação dos trechos tem de bater com o `png.py`:
8 espaços antes de `elif`, 12 antes de `raise`/`line[i]`):

```text
$ D=$(mktemp -d); git archive HEAD tools | tar -x -C "$D"; cd "$D" && python3 - <<'PY'
p="tools/duckmcp/png.py"; s=open(p).read()
old="""        elif kind:
            raise PngError"""
new="""        elif kind == 0:
            line[i] = (line[i] + 1) & 255
        elif kind:
            raise PngError"""
assert old in s; s=s.replace(old,new,1)
old2="        guess = (0, left,"; assert old2 in s; s=s.replace(old2,"        guess = (1, left,",1)
open(p,"w").write(s)
PY
$ python3 tools/duckmcp/selftest.py | grep -E 'FAIL|check\(s\)'
duckmcp_selftest: 339 check(s) ran, 0 failure(s)        (em 87987d9d; 361 na HEAD)
```

## Root cause

Hipótese: a quinta linha recebeu Paeth duas vezes em vez de None.

## Fix

No `tools/duckmcp/png.py`, regenerar `VECTOR_STREAM`/`VECTOR_PIXELS` com uma linha por filtro 0-4
(decodificada pelo Pillow) e manter `kinds == [0, 1, 2, 3, 4]` no check. Senão, renomear check e
docstring para "four filters".

## Arquivos a criar ou modificar

- `tools/duckmcp/png.py`

## Verificação

O comando de lista dos filtros imprime `[0, 1, 2, 3, 4]` (ou o check deixa de dizer cinco), e a planta
acima dá ao menos 1 falha no `selftest.py`. Na árvore real o selftest sai 0.

## Log de Execução
