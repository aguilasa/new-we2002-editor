---
id: KITS-TASK-02
title: "Medir o que são os retângulos (608,256) e (704,256)"
type: "investigação"
phase: 0
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#4.4"
files: ["tools/kits/cli.py", "tools/kits/core/survey.py", "docs/PLAN-KITS-PY.md", "docs/PLAN-LOOKS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
done_on: 2026-09-30
done_commit: 18e7ec61
reviewed_on: 2026-09-30
review_commit: b529ac6b
---

# KITS-TASK-02 — Medir o que são os retângulos (608,256) e (704,256)

## Goal

A §4.4 fechada: qual arquivo do disco declara registro em (608,256) e em (704,256), lido por comando versionado, e a linha do PLAN-LOOKS §1.7 corrigida se estiver velha.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/core/survey.py`
- `docs/PLAN-KITS-PY.md`
- `docs/PLAN-LOOKS-PY.md`

## Done criteria

- [x] Um subcomando da CLI lista, para os dois retângulos, todo arquivo do disco japonês que declara registro ali; a saída está colada no Log
- [x] A §4.4 do plano tem veredito e o comando que o sustenta
- [x] Se o PLAN-LOOKS §1.7 estava errado, a linha foi corrigida no mesmo commit; se estava certo, o Log diz por quê

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.4).

## Log de Execução

### O que foi feito

- `core/survey.py`: `owners_of({path: bytes}, points)` (pura), `read_all_files`, `covers`, `parse_point`; `cli.py rects <imagem> X,Y ...` imprime quem cobre cada ponto e quem começa nele, agrupado por formato de registro.
- §4.4 do plano fechada com o veredito; PLAN-LOOKS §1.7 ganhou nota de rodapé na linha do (608, 256) em vez de reescrita, porque a tabela é transcrição do `atlas.py --elsewhere`.

### Evidência

```
$ python tools/kits/cli.py rects roms/japanese-shift-jis.bin 608,256 704,256 576,256 576,384
  236 files read, 131 hold records; 9 skipped        (1 Form 2, 8 fora da trilha)
(608,256): 211 record(s) in 106 file(s) cover it, 0 start there
  image origin ( 576, 256)  64x128 hw  covers only  105 file(s): /BIN/TEX_00.BIN, ...
  image origin ( 592, 256)  32x128 hw  covers only    1 file(s): /SELECT2.BIN
(704,256): 116 record(s) in 116 file(s) cover it, 116 start there
  image origin ( 704, 256)  64x 64 hw  STARTS here  105 file(s): /BIN/TEX_00.BIN, ...
  image origin ( 704, 256)  32x128 hw  STARTS here   11 file(s): /BIN/DATSEL3.BIN, /BIN/EDT_2D.BIN, /BIN/LC_AF.BIN ...
(576,256): 211 record(s) in 106 file(s) cover it, 211 start there
(576,384): 210 record(s) in 105 file(s) cover it, 210 start there

$ python tools/looks/atlas.py --elsewhere roms/japanese-shift-jis.bin
      ( 576, 256)   1520 corner(s)  in 107 container(s): DATSEL2.BIN, SELECT2.BIN, TEX_00.BIN ...
      ( 608, 256)   1984 corner(s)  in 107 container(s): DATSEL2.BIN, SELECT2.BIN, TEX_00.BIN ...

$ grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py
(sem saída, exit 1)
```

As onze de 32×128 em (704, 256): `DATSEL3`, `EDT_2D`, `LC_AF`, `LC_AM`, `LC_AS`, `LC_EU`, `LC_IC`, `LC_KO`, `LC_LG`, `LC_MS`, `LC_OL`.

Controle negativo (em memória): as duas origens de uniforme do `TEX_A4` deslocadas de 576 para 640 → donos de (608,256) de 106 para 105, registros de 211 para 209, `TEX_A4` fora da lista.

O `survey` segue com as mesmas 12 linhas da KITS-TASK-01.

### Problemas encontrados

- **Os dois leitores de contêiner discordam num arquivo.** O `atlas.py --elsewhere` (leitor `texture.tables` do `looks`) põe `DATSEL2.BIN` como dono de (576,256)/(608,256); o `rects` (leitor `bin_archive.entries`) não acha registro dele cobrindo nenhum dos quatro pontos. Nota deixada na KITS-TASK-09, que confronta decodificadores.
- **Closed** — commit `18e7ec61` (2026-09-30): feat(kits): add cli.py rects and close §4.4 — (608,256) is a bucket, not a record
  - Files (`git show --name-status 18e7ec61`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/tasks/kits/02-retangulos-608-e-704.md`
    - `M docs/tasks/kits/09-cli-e-confronto-1.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/survey.py`
- **Reviewed** (2026-09-30) at `b529ac6b`: CORR-KITS-003, CORR-KITS-004
