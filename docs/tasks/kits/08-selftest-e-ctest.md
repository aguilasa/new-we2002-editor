---
id: KITS-TASK-08
---

# KITS-TASK-08 — Criar selftest, controles negativos e os alvos `kits_selftest` e `kits_image`

## Goal

O gate do ciclo existe: `kits_selftest` roda sem nada e nunca pula; `kits_image` precisa de uma ROM e sai 77 sem ela; os controles negativos são plantados por comando e cada um tem o vermelho visto.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`
- `tests/CMakeLists.txt`

## Done criteria

- [x] `ctest -R kits` lista `kits_selftest` e `kits_image` pelo nome (saída colada — `No tests were found` não conta)
- [x] `kits_selftest` roda os self-checks do `looks` que o `kits` importa (§6, Acoplamento)
- [x] `python tools/kits/controls.py` planta cada controle numa cópia e exige o vermelho; a última linha diz quantos são
- [x] Sem `WE2002_LOOKS_IMAGE`, `kits_image` sai *skipped* (77); com ela, passa

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.5).

O que cada parte faz, e as decisões que não estão no plano:

- **A lista dos módulos do `looks` sai dos imports**, não de uma tabela: `selftest.looks_modules_imported()` varre `tools/kits/**/*.py` e fica com os `tools/looks/<nome>.py` que têm `self_check`. Import novo entra sem ninguém lembrar. Desde a [CORR-KITS-017](/docs/tasks/kits/CORR-KITS-017.md) a varredura segue os imports pelos `tools/looks/*.py` até fechar (8 módulos passaram a 21), porque uma quebra a dois imports de distância deixava o gate verde; as transcrições abaixo são da corrida desta task.
- **O contêiner do `kits_selftest` é montado em memória** (`selftest.build_container`), com os retângulos escritos de novo em vez de lidos do `tex.EXPECTED_SHAPE` — fixture tirada da tabela sob teste concorda com ela qualquer que seja a tabela. As regras de disco do `source.read_disc_file` (cauda Form 2, tamanho ISO, arquivo seguinte) rodam num `iso.Image` sobre setores montados ali, sem imagem.
- **Cada controle exige o vermelho na linha certa**: saída diferente de zero **e** a linha `FAIL` que ele mira. Antes de plantar, uma cópia sem plantio tem de sair 0 — a primeira versão da cópia não tinha `src/core` nem `data/`, e o `looks.self_check()` ficava vermelho por isso, em todo controle.
- **Dois vermelhos errados vistos e consertados:** trocar `KIND_IMAGE` do `texture.py` não derruba self-check nenhum do `looks` (o controle de acoplamento passou a ser o `layout-empty-slot` do próprio catálogo do `looks`); e `import controls` dentro do `selftest.py` achava o `controls.py` do `looks`, que o `tex` põe antes no `sys.path` — a primeira corrida imprimiu `109 of 109 controls red`. Importado pelo caminho.
- **`kits_image` usa o disco japonês** (`WE2002_LOOKS_IMAGE`): os 105 passam pela guarda, o controle 4 do §5 vale num TEX real, as fixtures de reconhecimento do `open --negative` dão o que têm de dar. Os `disc_controls` da CORR-KITS-014 precisam da European Deluxe e ficam fora — o japonês não tem TEX a que as duas regras se apliquem.

## Log de Execução

### 2026-10-01

Build fora da árvore (`cmake -S . -B %TEMP%/build-kits08 -G Ninja -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake`):

```
$ ctest -N -R kits
  Test #14: kits_selftest
  Test #15: kits_image
Total Tests: 2

$ env -u WE2002_LOOKS_IMAGE ctest -R kits
1/2 Test #14: kits_selftest ....................   Passed   11.23 sec
2/2 Test #15: kits_image .......................***Skipped   0.14 sec
100% tests passed out of 2
15: kits_image: skipped -- WE2002_LOOKS_IMAGE is not set (the Japanese data track .bin)

$ WE2002_LOOKS_IMAGE=C:/github/new-we2002-editor/roms/japanese-shift-jis.bin ctest -R kits
1/2 Test #14: kits_selftest ....................   Passed   10.09 sec
2/2 Test #15: kits_image .......................   Passed    1.08 sec
15:   ..... 105 of 105 kits pass the guard
```

O `kits_image` visto vermelho, apontado para a European Deluxe (os 8 recusados do §2.1). Retranscrito inteiro pela [CORR-KITS-019](/docs/tasks/kits/CORR-KITS-019.md): o trecho que estava aqui mostrava uma linha FAIL só, e a corrida tinha **três** — as outras duas eram as fixtures de reconhecimento, que liam o `TEX_00` por `iso.Image.read_file` e quebravam com `Form2Sector: sector 8415 is Form 2` nesse disco. Corrigida a leitura (`read_disc_file`, como o resto do `source.py`), a única causa do vermelho é a guarda:

```
$ WE2002_LOOKS_IMAGE=roms/golden-european-deluxe.bin python tools/kits/selftest.py --image      # exit 1
kits_image self-check
  ok    it opens as a disc
  ok    it has kit containers
  FAIL  every kit passes the guard of form  ['/BIN/TEX_03.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_06.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_28.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_48.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_70.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_84.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_92.BIN on roms/golden-european-deluxe.bin', '/BIN/TEX_A2.BIN on roms/golden-european-deluxe.bin']
  ..... 97 of 105 kits pass the guard
  ok    section 5 control 4 on /BIN/TEX_00.BIN on roms/golden-european-deluxe.bin
  ok    every recognition fixture gives what it has to
kits_image: 1 failure(s)
```

Os self-checks do `looks`, dentro do `kits_selftest` (`ctest -R kits_selftest -V`):

```
14:   ..... 8 looks self-check(s): assembly, atlas, harness, iso_source, layout, looks, section, texture
14:   ..... 9 of 9 controls red
14: kits_selftest: 0 failure(s)
```

Os controles:

```
$ python tools/kits/controls.py      # exit 0
  base   unplanted sandbox            selftest exit 0
  RED    tex-shape-referee            kits/core/tex.py :: EXPECTED_SHAPE
  RED    tex-flag-double              kits/core/tex.py :: plain_size
  RED    tex-size-check               kits/core/tex.py :: read_kit
  RED    tex-stream-control-literal   kits/core/tex.py :: module constant
  RED    tex-header-extent            kits/core/tex.py :: declared_extent
  RED    source-form2-tail            kits/core/source.py :: _sector_data
  RED    source-next-file             kits/core/source.py :: _slot_end
  RED    core-prints                  kits/core/errors.py :: KitsError
  RED    looks-layout-empty-slot      looks/layout.py :: the pointer-list walk
controls: 9 of 9 red
```
- **Closed** — commit `e243594d` (2026-10-01): test(kits): add kits_selftest, kits_image and the planted controls
  - Files (`git show --name-status e243594d`):
    - `M docs/tasks/kits/08-selftest-e-ctest.md`
    - `M docs/tasks/kits/progresso.md`
    - `M tests/CMakeLists.txt`
    - `A tools/kits/controls.py`
    - `A tools/kits/selftest.py`
- **Reviewed** (2026-10-01) at `030bd7d9`: CORR-KITS-017, CORR-KITS-018, CORR-KITS-019, CORR-KITS-020
