---
id: CORR-KITS-079
---

# CORR-KITS-079 — Rodar o --attach no slot de manga curta e sustentar a frase da imagem de uniforme

Origin: [KITS-TASK-46](/docs/tasks/kits/46-manga-curta-partida.md)

## Problem

O Escopo da KITS-TASK-46 diz que o `--attach` roda no slot novo, de manga curta. Ele só rodou sobre o save antigo do slot 6, de manga longa, antes de o usuário regravá-lo: o `work/kits-oracle/attach-6.json` que o `--frame-json` leu era esse quadro velho, que mostra `93 95 96 98` e passa. O julgamento do `--attach` só conhece a seção 93, então uma corrida ao vivo sobre o estado de manga curta de verdade sai 1. E a §4.3 afirma "Os braços curtos amostram a imagem de uniforme", mas nada que a task rodou atribui primitivas das páginas de kit às seções de braço curto. Medido: só as seções 3 e 4 (e as 57 e 59 do goleiro) aparecem nas páginas de kit; as 5 e 6 não aparecem.

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 tools/kits/oracle.py --attach 6
  player  0 ( 34 prims, CLUT (0,487)): 2 3 7 8 9 10
  player  2 ( 31 prims, CLUT (0,486)): 2 3 4 7 8 9 10
  player  5 ( 23 prims, CLUT (0,486)): 56 57 59 61 62 63 64
  4 primitive(s) whose texels sections 3 57 all hold: left out
  3 primitive(s) whose texels sections 4 90 all hold: left out
  FAIL  no player draws section 93
(exit 1)
$ grep -n 'Os braços curtos amostram' docs/PLAN-KITS-PY.md
690:...
```

## Root cause

Provavelmente, depois de desbloqueada a task, só `--attach-matrix` e `--sleeves` foram refeitos; o julgamento do `--attach` (`attach_judge`, com `ARMBAND_SECTION`/`REPLACED_SECTION`) não recebeu a tabela `SLEEVE_LENGTHS`.

## Fix

Em `tools/kits/oracle.py`, dar `--sleeve-length` ao `--attach` e fazer o `attach_judge` usar `SLEEVE_LENGTHS[length]` (braçadeira 90 no lugar da 4); refazer no slot 6. Na §4.3 de `docs/PLAN-KITS-PY.md`, trocar a frase pelo que foi medido: que seções de braço curto amostram a imagem de uniforme (3 e 4 vistas; 5 e 6 não vistas nas páginas de kit).

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Verificação

`python3 tools/kits/oracle.py --attach 6 --sleeve-length short` (com o ambiente acima) sai 0. Hoje a opção não existe, e `--attach 6` sai 1.

## Log de Execução
