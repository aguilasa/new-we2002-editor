---
id: KITS-TASK-01
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

Controles negativos, versionados desde a [CORR-KITS-002](/docs/tasks/concluidos/kits/CORR-KITS-002.md) (`core/survey.py` `NEGATIVE_CONTROLS`; cada defeito plantado sozinho numa cópia dos 105 reais):

```
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin     # exit 0
  A4 player CLUT, second set       TEX_A4   first set == second set: ('A4',) -> ()  red
  A4 goalkeeper CLUT, first set    TEX_A4   player palette == keeper palette: ('A4',) -> ()  red
  00 referee LZSS stream, +3       TEX_00   referee variants / problems: (1, ()) -> (2, ())  red
  00 referee rect x + 1            TEX_00   shape ok: 105 -> 104  red
4 of 4 controls red
```

(Esta seção trazia antes dicionários `clean`/`planted` de uma sonda em memória, com os quatro defeitos plantados juntos; a sonda não foi versionada e foi substituída pelo comando acima.)

Erro: `python tools/kits/cli.py survey roms/nope.bin` → `survey: Could not open roms/nope.bin: No such file or directory`, exit 1.

### Problemas encontrados

- Os 11 retângulos (`EXPECTED_SHAPE`) moram em `core/survey.py`; o §3.1 quer endereço no `layout.py` do `looks`, que esta task não podia tocar. Nota deixada na KITS-TASK-07.
- Exceção temporária ao §3.1 ([CORR-KITS-001](/docs/tasks/concluidos/kits/CORR-KITS-001.md)): `cli.py survey` importa `core.survey` direto e lê `EXPECTED_SHAPE`/`KIND_IMAGE`, porque a fachada `core/api.py` só nasce na KITS-TASK-06. A passagem para trás da fachada fica com a [KITS-TASK-09](/docs/tasks/concluidos/kits/09-cli-e-confronto-1.md), que já exige `cli.py` importando só `core.api`.
- **Closed** — commit `fc5717ae` (2026-09-30): feat(kits): survey the TEX containers in core, print it from cli.py survey
  - Files (`git show --name-status fc5717ae`):
    - `M NOTICE.md`
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/01-levantamento-do-tex.md`
    - `M docs/tasks/kits/06-fachada-e-origem.md`
    - `M docs/tasks/kits/07-tex-e-guarda-de-forma.md`
    - `A tools/kits/cli.py`
    - `A tools/kits/core/__init__.py`
    - `A tools/kits/core/survey.py`
- **Reviewed** (2026-09-30) at `da75b135`: CORR-KITS-001, CORR-KITS-002
