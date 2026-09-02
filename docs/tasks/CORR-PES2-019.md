---
id: CORR-PES2-019
title: "Correção: o import não valida profundidade nem paleta, e grava um PNG de 4 bpp num slot de 8 bpp em silêncio"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-PES2-019: `asset_write.py import` aceita a profundidade errada

## Problema identificado

O método da PES2-TASK-29 diz, no passo 1: *"Importar PNG indexado, validando
dimensão, **profundidade e paleta** contra a entrada de destino. Divergência é
recusa, **não conversão silenciosa**."*

O `cmd_import` valida **só a dimensão**, mais dois testes que não alcançam o
caso: `if bpp == 4 and any(i > 15 …)` e `len(palette) > (1 << bpp)`. Nenhum dos
três recusa o caminho inverso — um PNG de **16 cores** entrando num slot de
**8 bpp** —, porque:

- as dimensões batem: um bloco de 32×128 unidades de VRAM tem `32*4 = 128` px
  de largura a 4 bpp e `64*2 = 128` px a 8 bpp, e os dois casos existem no
  disco lado a lado;
- a contagem de bytes bate: `largura × altura × 2` é a mesma nos dois, que é
  exatamente o que a §1.14(f) já avisava — *"a contagem de bytes é a mesma, só
  a leitura de um byte muda"*;
- `any(i > 15)` só dispara no sentido 8→4, nunca 4→8;
- `len(palette) > 1 << bpp` é 16 > 256, falso.

Resultado: a gravação passa, o `check` de descompressão passa, e o slot fica
com uma figura cujos índices apontam para a paleta errada. **É a conversão
silenciosa que o critério proíbe.**

## Evidência

Exportando a entrada 2 do `LOGO.BIN` — 4 bpp — e importando no `TITLE.BIN`
entrada 2 — 8 bpp — sobre uma cópia de trabalho:

```
$ python3 tools/pes2/asset_write.py export <copia> --file /BIN/LOGO.BIN  --entry 2 --png l2.png
/BIN/LOGO.BIN entry 2: 128x128 px 4 bpp -> l2.png

$ python3 tools/pes2/asset_write.py import <copia> --file /BIN/TITLE.BIN --entry 2 --png l2.png
/BIN/TITLE.BIN entry 2: 128x128 8 bpp, 1246 B of 3312 B
written, and verified before it went
  exit=0
```

Aceito e gravado. As outras recusas do mesmo comando funcionam, o que mostra
que o buraco é este e não a validação em geral:

```
$ … import … --entry 99 …   → refused: this container has 9 image record(s)
$ … import … --png lixo.png → refused: … is not a PNG
```

## Causa raiz

A validação compara **dimensão em pixels**, que é ambígua entre 4 e 8 bpp para
o mesmo retângulo de VRAM, e nunca compara a profundidade da origem com a do
destino nem a paleta do PNG com o CLUT do slot.

## Correção

### Arquivo: `tools/pes2/asset_write.py`

1. **Carimbar a profundidade na exportação.** O `cmd_export` já sabe o `bpp`;
   gravar `len(palette)` coerente com ele — 16 entradas para 4 bpp, 256 para
   8 bpp — de modo que o PNG carregue a informação em vez de deixá-la implícita.
2. **Recusar quando a profundidade da origem não é a do destino.** Derivar a
   profundidade do PNG do tamanho da `PLTE` (≤16 ⇒ 4 bpp, senão 8) e comparar
   com `depth_for(...)`; divergência é `Refused`, com os dois valores no texto.
3. **Comparar a paleta com o CLUT do destino** quando o contêiner tiver um, e
   recusar — ou exigir um `--repaint` explícito — se as cores não forem as
   mesmas. O critério pede a paleta validada, não só a contagem.
4. Manter as recusas atuais; elas cobrem o sentido 8→4 e o PNG malformado.

### Arquivo: `tools/pes2/asset_write.py`, função `cmd_check`

Acrescentar o caso ao `check`, para a guarda ficar exercitada em vermelho: um
export de 4 bpp importado num slot de 8 bpp tem de ser recusado. Sem isso o
verde do gate não diz nada sobre esta validação — é a mesma lição da
CORR-PES2-009.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/asset_write.py` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar (a linha da §1.14(g) que descreve o import) |

## Verificação

- [ ] importar um PNG de 4 bpp num slot de 8 bpp é **recusado**, dizendo as duas profundidades
- [ ] importar o PNG exportado do mesmo slot continua aceito
- [ ] o `check` exercita a recusa nova e falha se ela for removida
- [ ] `ctest --test-dir build -R pes2` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
