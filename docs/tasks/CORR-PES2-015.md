---
id: CORR-PES2-015
title: "Correção: um dos quatro offsets de bandeira citados é de forma, e mora noutro arquivo; o quarto de cor é 75776"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-PES2-015: 72400 não é cor de bandeira nem está em `DAT2D.BIN`

## Problema identificado

A §1.14(f) do plano e o repasse escrito na
[PES2-TASK-14](/docs/tasks/14-bandeiras.md) dizem:

> Os quatro `OFS_FLAG_*` da §1.4 caem em `/BIN/DAT2D.BIN` nos offsets
> relativos **69798, 72400, 73254 e 73728** …

Medido com `tools/pes2/ofs_map.py`, os quatro `OFS_FLAG_COLOURS*` de
`/BIN/DAT2D.BIN` são **69798, 73254, 73728 e 75776**. O **72400** não é nenhum
deles: é `OFS_FLAG_SHAPE_COPY_4`, que é **forma** de bandeira, não cor, e mora
em **`/SELFORM.BIN`** — outro arquivo. O quarto offset de cor,
`OFS_FLAG_COLOURS_B`, **não aparece na lista** e está em 75776.

Não é detalhe de redação: a lista foi entregue à PES2-TASK-14 como o mapa de
entrada dela, e um dos quatro endereços aponta para outro arquivo e outro tipo
de dado. Quem for atrás vai ler geometria achando que lê paleta.

## Evidência

```
$ python3 tools/pes2/ofs_map.py roms/golden-european-deluxe.bin
OFS_FLAG_SHAPE_COPY_1          1929004 -> ('/OPENNING.BIN', 20820)
OFS_FLAG_SHAPE_COPY_2          2005412 -> ('/SELECT.BIN',    5580)
OFS_FLAG_SHAPE_COPY_3          2328060 -> ('/SELECT.BIN',  286580)
OFS_FLAG_SHAPE_COPY_4          4904664 -> ('/SELFORM.BIN',  72400)   ← o citado
OFS_FLAG_SHAPE_COPY_5          5711640 -> ('/REPLAYS.BIN',  58304)
OFS_FLAG_COLOURS              12549518 -> ('/BIN/DAT2D.BIN', 73254)
OFS_FLAG_COLOURS_A            12550296 -> ('/BIN/DAT2D.BIN', 73728)
OFS_FLAG_COLOURS_B            12552648 -> ('/BIN/DAT2D.BIN', 75776)  ← o que falta
OFS_FLAG_COLOURS_SENEGAL      12545758 -> ('/BIN/DAT2D.BIN', 69798)
```

O conteúdo confirma. Na imagem japonesa, nos quatro offsets de cor:

```
@69798: 0x8dc3 0x8982 0x97bd 0x837b     ← o literal que o doc cita
@73254: 0x8dc3 0x8982 0xf7bd 0xe318
@73728: 0x9096 0xc639 0x0000 0x9096
@75776: 0xdad6 0xf7bd 0x0000 0xf7bd
```

Enquanto em `DAT2D.BIN` **+72400** — que não é offset de coisa nenhuma, só o
número trazido do outro arquivo — se lê `0x0d4d 0x118f 0x11d2 0x1613`, com o
bit alto **apagado** em todas, ao contrário do que a frase descreve.

*(Nota, e é resultado legítimo: o literal `0x8dc3 0x8982 0x97bd` citado no doc
reproduz na imagem **japonesa** e não na European Deluxe, que é a hackeada. O
doc não diz em qual das duas mediu; vale acrescentar.)*

## Causa raiz

A lista foi montada juntando `OFS_FLAG_*` por prefixo de nome, e
`OFS_FLAG_SHAPE_COPY_4` entrou junto com as cores; o `OFS_FLAG_COLOURS_B`
ficou de fora porque o `ofs_map.py` imprime no máximo **três** offsets por
arquivo no resumo (`sorted(...)[:3]`), e o quarto de `DAT2D.BIN` — que o
cabeçalho da seção conta como `4` — não aparece na tela.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`, §1.14(f)

A lista passa a ser **69798, 73254, 73728 e 75776**, dita como os quatro
`OFS_FLAG_COLOURS*`; e uma linha diz que os cinco `OFS_FLAG_SHAPE_COPY_*` são
outra coisa e moram noutros arquivos (`/OPENNING.BIN`, `/SELECT.BIN` ×2,
`/SELFORM.BIN`, `/REPLAYS.BIN`), com o comando que os localiza. Acrescentar em
qual das duas imagens de WE2002 o literal foi lido.

### Arquivo: `docs/tasks/14-bandeiras.md`

O repasse leva a mesma correção — é ele que a task vai usar.

### Arquivo: `tools/pes2/ofs_map.py`, opcional mas é a causa

O corte em três por arquivo no resumo é o que escondeu o quarto. Ou o resumo
imprime todos quando o arquivo tem poucos, ou a linha diz "… e mais N", para
que a contagem do cabeçalho e a lista não se contradigam na mesma tela.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/tasks/14-bandeiras.md` | modificar |
| `tools/pes2/ofs_map.py` | modificar (opcional) |

## Verificação

- [ ] os quatro offsets do doc batem com o `ofs_map.py`, arquivo e valor
- [ ] `grep -rn "72400" docs/` não devolve mais a afirmação de que é cor em
      `DAT2D.BIN`
- [ ] se o `ofs_map.py` mudar, o resumo dele não contradiz mais o próprio
      contador por arquivo
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
