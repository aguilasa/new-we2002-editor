---
id: CORR-LOOKS-006
title: "Correção: a recusa do `/SELECT.BIN` sai como `digest mismatch` pelado"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-LOOKS-006: a recusa do `/SELECT.BIN` sai como `digest mismatch` pelado

## Problema identificado

O `require()` do `tools/looks/layout.py` monta a dica pela **família** do
arquivo:

```python
    if disc_path in TEXTURE_FILES:      # {DAT2D}
        hint = ...  "you opened the English disc"
    elif disc_path in GEOMETRY_FILES:   # {EDT_MOD, MODEL}
        hint = ...  "a third disc"
```

`/SELECT.BIN` **não está em nenhuma das duas**, então cai no `hint = ""` e a
exceção sai como a mensagem que o docstring do próprio módulo diz ser a errada:
*"an exception that only says 'digest mismatch' sends the reader looking at the
parser instead."*

E é o pior arquivo para isso acontecer. `/SELECT.BIN` é um dos **dois** que
diferem entre os discos — o outro é o `DAT2D.BIN` —, guarda os registros de
jogador (`+157.164`, 1.242 × 12 B) e, pela tabela de fontes de verdade do
perfil, é **japonês**. A causa esmagadoramente provável de uma recusa dele em
produção é exatamente a mesma do `DAT2D.BIN`: alguém abriu o disco inglês. É o
único dos quatro cuja mensagem não diz isso.

O Log da task afirma que *"a mensagem recebeu tanto cuidado quanto a recusa"*.
Recebeu em três dos quatro arquivos.

## Evidência

```
$ python -c "import sys; sys.path.insert(0,'tools/looks'); import layout; \
layout.require(layout.SELECT, b'english select', 'we2002-english.bin')"
...
layout.WrongDisc: /SELECT.BIN: read 508d82ec… from we2002-english.bin,
expected 86d14a66a3cd72b9363832260d4f3842e15d530c2f76eb0d6a3f6823cd603ce1.
```

Nenhuma dica. Contra o `DAT2D.BIN`, mesmo estímulo:

```
/BIN/DAT2D.BIN: read 14744027… from we2002-english.bin, expected 0e914e58….
  /BIN/DAT2D.BIN differs between the Japanese original and the English
  translation patch, and textures and palettes may only be read from the
  Japanese one.  Point WE2002_LOOKS_IMAGE at it; WE2002_LOOKS_DRIVE_IMAGE is
  the disc you drive, not the disc you read.
```

E que o `/SELECT.BIN` de fato difere entre os discos, remedido nesta revisão:

```
jap /SELECT.BIN 300648 86d14a66a3cd72b9363832260d4f3842e15d530c2f76eb0d6a3f6823cd603ce1
eng /SELECT.BIN 300648 c9e1eaf89151b0c026dda80e490276ec510409423e774423ce7ac145071461b3
```

O `self_check()` não pega isso: os três casos vermelhos dele são `DAT2D`,
caminho não medido e `MODEL`. Nenhum é o `SELECT`.

## Causa raiz

`TEXTURE_FILES` e `GEOMETRY_FILES` cobrem três dos quatro caminhos, e o quarto
cai no ramo sem dica por omissão, não por decisão.

## Correção

### Arquivo: `tools/looks/layout.py`

O conserto **não** é enfiar o `SELECT` em `TEXTURE_FILES` — ele não é textura, e
a dica falaria de paleta onde a coisa é registro de jogador. Duas partes:

1. Um terceiro conjunto — `JAPANESE_ONLY_FILES = frozenset({DAT2D, SELECT})`,
   ou uma tabela `caminho → texto` — com dica própria para o `/SELECT.BIN`:
   ele difere entre os discos, os registros de jogador se leem do japonês, e a
   variável a apontar é `WE2002_LOOKS_IMAGE`.
2. Um `assert` no `self_check()` de que **todo caminho de `DIGEST` produz dica
   não vazia**. É o que impede o próximo arquivo acrescentado ao mapa de
   herdar o mesmo silêncio — a falha aqui foi por omissão, e só um caso
   vermelho que varra o mapa inteiro fecha essa porta.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |

## Verificação

- [ ] `python tools/looks/layout.py --check` verde, com o caso novo que exige
      dica para todo caminho de `DIGEST`
- [ ] a recusa do `/SELECT.BIN` nomeia o disco japonês e a variável
- [ ] `python tools/looks/layout.py --check-discs <japonês> <inglês>` continua
      dando `ok` nas oito linhas
- [ ] nada em português no módulo, e nenhum endereço fora dele (§3.3 e §3.5)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
