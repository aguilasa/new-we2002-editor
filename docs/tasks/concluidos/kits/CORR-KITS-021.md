---
id: CORR-KITS-021
---

# CORR-KITS-021 — Add a versioned control that plants a palette defect in confront 1

Origin: [KITS-TASK-09](/docs/tasks/concluidos/kits/09-cli-e-confronto-1.md)

## Problem

O confronto 1 afirma comparar paleta por paleta (§5.1 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md), e `PLTE`/`tRNS` nas decisões da KITS-TASK-09). O único controle versionado dele (`--negative`, o mesmo que o `_confront_checks` roda no `kits_image`) muda o índice de um pixel só. O ramo `pa != pb` do `confront()` nunca fica vermelho numa corrida versionada; o revisor só o viu vermelho numa cópia remendada à mão. Pela regra "verificador sem vermelho visto não é gate", a metade de paleta do gate não tem vermelho visível.

## Evidência

```text
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin | grep -c "palettes differ"
0
$ grep -n "CONTROL_PIXEL" tools/kits/cli.py | head -3
609:CONTROL_PIXEL = (0, 4096)
636:                           CONTROL_PIXEL if name == plant_tag else None)
676:              % (plant_tag, CONTROL_PIXEL[1], "red, held" if held else "FAILED"))
```

Sonda do revisor, sem versão (cópia `git archive` da HEAD com uma cor da paleta 0 trocada em `XOR 1` dentro da conversão RGB555 do `cli.py`):

```text
$ python tools/kits/cli.py export --confront --tag 00 --tag A4 <repo>/roms/japanese-shift-jis.bin
  DIFFER TEX_00_00.png palette 0: palettes differ
  ...
confront 1: 0 of 2 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
(exit 1)
```

## Root cause

Hipótese: o controle foi desenhado em torno da descompressão ("o que se confronta de independente é a descompressão"), e a comparação de paleta ficou sem defeito plantado próprio.

## Fix

Em `tools/kits/cli.py`, estender o `confront` com um controle de paleta: o `--negative` também troca uma cor de uma paleta de um segundo tag, ou um `--negative-palette` separado faz isso. O `_confront_checks` de `tools/kits/selftest.py` passa a exigir que exatamente esse tag difira com "palettes differ". Colar o vermelho no Log da task.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/selftest.py`

## Verificação

```text
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin | grep -c "palettes differ"
```

Hoje imprime 0; depois, pelo menos 1, com a linha do controle continuando "red, held".

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `d722ca1a`)

```text
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin | grep -c "palettes differ"
0
```

REPRODUCED. Causa raiz confirmada: o único plantio (`CONTROL_PIXEL`) muda índice, e o ramo `pa != pb` do `confront()` só é alcançado quando os índices batem.

### O que foi feito

- `tools/kits/cli.py`: `export_kit(..., colour_plant=)` troca o bit baixo do vermelho de uma cor depois da conversão BGR555; `CONTROL_COLOUR = (0, 1)` (paleta 0, cor 1). O `--negative` do confronto planta o pixel no 1º kit, como antes, e a cor no 2º; o controle só fica "red, held" se os dois diferirem, nada mais, e o 2º apenas por "palette 0: palettes differ".
- `tools/kits/selftest.py`, `_confront_checks`: exige `n_kits - 2` de `n_kits` iguais, "red, held" e "palettes differ".
- KITS-TASK-09: o vermelho novo colado no Log.

### Verificação

```text
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin | grep -c "palettes differ"; echo "exit ${PIPESTATUS[0]}"
6
exit 0
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin | tail -2
confront 1: 103 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
control: TEX_00 image 0 pixel 4096 +1, and TEX_01 palette 0 colour 1 red ^1, on our side -- red, held
$ python tools/kits/cli.py export --confront roms/japanese-shift-jis.bin | tail -1
confront 1: 105 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python tools/kits/selftest.py --image | grep -E "confront|kits_image"
  ok    confront 1: every kit equal to bin_archive.py export
  ..... confront 1: 105 of 105 tags equal
  ok    confront 1 control: one pixel and one palette colour changed on our side make two tags differ, the second by its palette
kits_image: 0 failure(s)
```

O controle visto falhando — com um kit só não há onde plantar a cor:

```text
$ python tools/kits/cli.py export --confront --negative --tag 00 roms/japanese-shift-jis.bin | tail -1; echo "exit ${PIPESTATUS[0]}"
control: TEX_00 image 0 pixel 4096 +1, and None palette 0 colour 1 red ^1, on our side -- FAILED
exit 1
```
- **Closed** — commit `a735d97f` (2026-10-01): fix(kits): give confront 1's control a palette half
  - Files (`git show --name-status a735d97f`):
    - `M docs/tasks/kits/09-cli-e-confronto-1.md`
    - `M docs/tasks/kits/CORR-KITS-021.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/selftest.py`
