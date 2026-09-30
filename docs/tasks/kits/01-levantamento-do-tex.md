---
id: KITS-TASK-01
title: "Promover o levantamento do §1.1 a ferramenta versionada"
type: ferramenta
phase: 0
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#1.1"
files: ["tools/kits/core/__init__.py", "tools/kits/core/survey.py", "tools/kits/cli.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-01 — Promover o levantamento do §1.1 a ferramenta versionada

## Goal

O levantamento dos 105 TEX que produziu a tabela do §1.1 passa a ser uma função do núcleo (`core/survey.py`, que devolve dados) e um subcomando `cli.py survey` que os imprime. A tabela do §1.1 deixa de depender de um script descartável.

## Arquivos a criar ou modificar

- `tools/kits/core/__init__.py`
- `tools/kits/core/survey.py`
- `tools/kits/cli.py`

## Done criteria

- [x] `python tools/kits/cli.py survey <trilha japonesa>` imprime, colado no Log: forma única nos 105 (6 imagens + 5 CLUTs), titular = suplente só no `TEX_A4`, 103 com imagens diferentes, 1 só com paletas diferentes, 1 com paleta de jogador = goleiro, árbitro idêntico nos 105, tamanho de 25.948 a 34.200 bytes
- [x] Número do Log que divergir do §1.1 corrige o §1.1 no mesmo commit, com a saída da ferramenta como prova
- [x] `core/survey.py` não tem `print`, `sys.exit` nem import de Qt: `grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py` vazio

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#1.1). O plano diz `tex.py --survey`; o §3.1 proíbe `print` no núcleo. Decisão de 2026-09-30 no `/rite:plan-to-tasks`: a medição fica no núcleo, a impressão na CLI.

## Log de Execução

### O que foi feito

- `tools/kits/core/survey.py`: `survey_files({tag: bytes})` (pura, sem I/O) e `survey_image(path)` (lê pelo `tools/pes2/iso.py`); erros tipados `SurveyError`/`NoKitsFound`. Container malformado não levanta: vira `problem` ou forma fora e sai das contagens seguintes.
- `tools/kits/cli.py survey <imagem>` imprime. Os TEX são listados por `layout.KIT_DIR/KIT_PREFIX/KIT_SUFFIX` do `looks`, não pela tabela de digests (§2.1: o TEX vem de qualquer disco).
- `NOTICE.md` ganhou a seção do `tools/kits/` com a linha do CARP: o núcleo importa `lzss.py`/`bin_archive.py` **nesta** task, e a regra do perfil exige a linha no mesmo commit.
- §1.1 do plano: nenhum número divergiu. Precisei três células com o que a ferramenta passou a nomear (`TEX_98`, `TEX_A4`, e o byte de enchimento da bandeira: `0xFF` em 93, `0x00` em 12) e troquei "script em §7" pelo comando.

### Evidência

```
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin     # exit 0
  TEX_<tag>.BIN containers                       105
  shape 6 images + 5 CLUTs, same rects/order     105 of 105
  distinct shapes                                  1
  first set == second set (images and palettes)    1 of 105  [TEX_A4]
  images differ between the two sets             103 of 105
  only the palettes differ                         1 of 105  [TEX_98]
  player palette == keeper palette (first set)     1 of 105  [TEX_A4]
  flag, decompressed size                        16,384 B (record declares 8,192 B)
  flag, 2nd half is one byte value               105 of 105
  flag, 2nd-half byte value per container        0x00 in 12, 0xff in 93
  referee identical in all                       yes (1 variant(s))
  file size                                      25,948 .. 34,200 bytes

$ grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py tools/kits/core/__init__.py
(sem saída, exit 1)
```

Controles negativos (em memória, sobre os 105 reais):

```
clean   {'shape_ok': 105, 'sets_equal': ('A4',), 'images_differ': 103, 'only_pal': ('98',), 'player_eq_gk': ('A4',), 'referee_variants': 1, ...}
planted {'shape_ok': 104, 'sets_equal': (), 'images_differ': 102, 'only_pal': ('98', 'A4'), 'player_eq_gk': (), 'referee_variants': 1, ...}
```

(bit de cor na CLUT de jogador do 2º conjunto do `TEX_A4`, bit na CLUT de goleiro do 1º, e `x` do árbitro do `TEX_00` 768→769). O árbitro à parte: um bit trocado no fluxo LZSS do árbitro do `TEX_00` (offset +3) leva `referee variants` de 1 a 2.

Erro: `python tools/kits/cli.py survey roms/nope.bin` → `survey: Could not open roms/nope.bin: No such file or directory`, exit 1.

### Problemas encontrados

- Os 11 retângulos (`EXPECTED_SHAPE`) moram em `core/survey.py`; o §3.1 quer endereço no `layout.py` do `looks`, que esta task não podia tocar. Nota deixada na KITS-TASK-07.
