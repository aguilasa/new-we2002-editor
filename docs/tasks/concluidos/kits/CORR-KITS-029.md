---
id: CORR-KITS-029
---

# CORR-KITS-029 — Reconcile the 4.6 unsampled-zone rule with the verdict

Origin: [KITS-TASK-16](/docs/tasks/concluidos/kits/16-zonas.md)

## Problem

A regra no topo do §4.6 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) continua dizendo que zona que nenhuma primitiva amostra "ou é da manga longa, da braçadeira e dos figurantes com bandeira — ou está errada". O veredito novo, na mesma seção, aceita a zona "os números" (64,68) 60×12 por outro motivo ("quem desenha o número de camisa não está nesta tela"), e aceita os dois cotovelos e a manga curta do capitão goleiro sob "imagem de mangas". A regra não foi atualizada: por ela a zona dos números está "errada", mas a ferramenta a deixa passar. Isso contraria a regra do repositório "fechar um veredito é varrer quem dizia o anterior".

## Evidência

```text
$ sed -n 468,476p docs/PLAN-KITS-PY.md | grep -c "números"
0
$ sed -n 470,472p docs/PLAN-KITS-PY.md
é mecânica: toda primitiva do boneco com UV no TEX cai numa zona do mapa, e zona
que nenhuma primitiva amostra ou é da manga longa, da braçadeira e dos figurantes
com bandeira — ou está errada.
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | grep -A1 "1 zone(s)"
1 zone(s): no primitive of the LOOKS SET samples the shirt numbers; who draws them is not on this screen
    shared    (64,68) 60x12  numbers 0-9
```

## Root cause

O veredito ampliou os motivos aceitos, e a frase que enuncia o critério ficou como estava.

## Fix

Reescrever a regra de abertura do §4.6: zona não amostrada precisa trazer motivo declarado, e os motivos aceitos são a imagem de mangas não desenhada nesta tela e os números desenhados por algo fora dela. Ou registrar a zona dos números como exceção à regra original, com a decisão.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Verificação

```text
$ sed -n 468,476p docs/PLAN-KITS-PY.md | grep -c "números"
```

Hoje dá 0; depois, pelo menos 1.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `eaeb6838`)

```text
$ sed -n 468,476p docs/PLAN-KITS-PY.md | grep -c "números"
0
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | grep -A1 "1 zone(s)"
  1 zone(s): no primitive of the LOOKS SET samples the shirt numbers; who draws them is not on this screen
    shared    (64,68) 60x12  numbers 0-9
```

REPRODUCED.

### O que foi feito

Regra de abertura do §4.6 reescrita: zona que nenhuma primitiva amostra traz o motivo declarado, e os aceitos são os dois que o `cli.py zones` imprime — a imagem de mangas, não amostrada nesta tela (15 zonas: manga longa, braçadeira, cotovelos e a manga curta de capitão das duas figuras), e os números (1 zona). A frase velha fica citada, com o motivo da troca.

```text
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | sed -n '/15 zone(s)/,/^[a-z]/p' | grep -c "^    "
15
```

### Verificação

```text
$ sed -n 468,476p docs/PLAN-KITS-PY.md | grep -c "números"
1
```
- **Closed** — commit `9638e231` (2026-10-02): docs(kits): state plan 4.6's rule as the two reasons the zone check accepts
  - Files (`git show --name-status 9638e231`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-029.md`
