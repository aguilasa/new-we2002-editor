---
id: CORR-LOOKS-085
title: "O docstring do HELP_ICON_CODES contradiz a medição"
origin: LOOKS-TASK-39
severity: medium
files: [tools/looks/layout.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-085 — O docstring do HELP_ICON_CODES contradiz a medição

Origin: [LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)

## Problema identificado

O `tools/looks/layout.py` diz, da tabela de 22 meias-palavras em
`HELP_ICON_CODES = 0x800BCA58`, que "a code in it comes out on
`HELP_ICON_CLUT`, which is how `■` is the one sprite of the box on another
CLUT", e que "which file the table is loaded from was not measured". As duas
metades estão erradas, e o **mesmo commit** traz a evidência:

- o `■` é `0x81A1`, que **não está** nessa tabela — é um dos quatro códigos do
  `HELP_SPECIAL_SPAN`, cujo docstring, 25 linhas acima, dá a razão de verdade;
- a tabela **está no disco**: `/SELECT.BIN`, offset 253.728, como os
  "Problemas encontrados" da própria task e a §10.3 (o) afirmam.

O arquivo oferece duas explicações mutuamente exclusivas para o `■` cair na
CLUT (32,498), e a que perde é a constante que um leitor seguinte usaria.

## Evidência

```text
$ python - <<'EOF'   # a tabela lida do jogo vivo e do disco
# (Oracle no slot 2, read_ram(0x800BCA58, 44), contra /SELECT.BIN[253728:253772])
RAM 0x800BCA58 : ['0x9b89', '0x9bbd', ..., '0xfab1', '0x9b9a', '0xe085', '0xe54d', '0xe7e9']
SELECT 253728  : ['0x9b89', '0x9bbd', ..., '0xfab1', '0x9b9a', '0xe085', '0xe54d', '0xe7e9']
same: True
RAM blob found in SELECT at: 253728
EOF

$ python -c "...codes at /SELECT.BIN+253728...; print([hex(c) for c in (0x819a,0x819c,0x81a1,0x81a3) if c in codes])"
[]          # nenhum dos quatro códigos do despacho, o ■ inclusive, está nos 22
```

## Causa raiz

(hipótese) O docstring foi escrito enquanto a tabela de 22 códigos ainda era a
explicação candidata para a segunda CLUT, e não foi reconciliado quando o
`help_special_codes` mediu a de verdade nem quando a tabela foi localizada por
conteúdo no `/SELECT.BIN`.

## Correção

Reescrever o docstring de `HELP_ICON_CODES` em `tools/looks/layout.py` (perto
da linha 1845): tirar a afirmação sobre o `■`/CLUT (apontar o
`HELP_SPECIAL_SPAN`, que a mediu), e trocar "which file the table is loaded
from was not measured" pela procedência medida — `/SELECT.BIN` + 253.728, 22
meias-palavras, os bitmaps de 32 bytes em 253.772 —, mantendo a ressalva de
"registrado, não lido" para os bitmaps, que de fato não foram lidos.

## Arquivos

- tools/looks/layout.py

## Verificação

`grep -A6 "^HELP_ICON_CODES" tools/looks/layout.py | grep -c "which is how"`
tem de imprimir `0` (imprime `1` hoje), e o docstring passa a nomear
`/SELECT.BIN` e o offset 253.728.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-23, HEAD `dca4a96e`: **reproduzida** pelo lado do disco (o lado vivo não rodou — o emulador estava com outro agente).

```text
# /SELECT.BIN + 253728, 22 meias-palavras:
['0x9b89','0x9bbd','0x9bc1','0x9bd4','0x9bdf','0x9c41','0x9e8a','0x9f86','0x9fba','0xe056',
 '0xe05f','0xe1b8','0xe1c1','0xe555','0xe7b2','0xe7b3','0xe863','0xfab1','0x9b9a','0xe085',
 '0xe54d','0xe7e9']
special present: []      # nenhum de 0x819a/0x819c/0x81a1/0x81a3 -- o ■ inclusive
$ grep -A6 "^HELP_ICON_CODES" tools/looks/layout.py | grep -c "which is how"
1
```

**Um terceiro ponto, fora do vão que a Correção nomeia:** o `HELP_ICON_CLUT`
(layout.py:1810) repete a mesma atribuição errada — "the game's own exception
list (22 codes, at `HELP_ICON_CODES`) is what puts a code on the other
palette". Mesmo arquivo, mesmo defeito.
