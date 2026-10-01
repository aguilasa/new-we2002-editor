---
id: CORR-KITS-021
---

# CORR-KITS-021 — Add a versioned control that plants a palette defect in confront 1

Origin: [KITS-TASK-09](/docs/tasks/kits/09-cli-e-confronto-1.md)

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
