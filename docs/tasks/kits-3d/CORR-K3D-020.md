---
id: CORR-K3D-020
---

# CORR-K3D-020 — edit_number_judge não afirma cabeça, número e giro medidos no G7

Origin: [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md)

## Problem

Numa corrida real, o juiz da [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md) não pede nenhum dos valores que o G7 afirma. A cabeça
esperada sai da própria captura — `head = report["figures"][0]["head"]`
(`tools/kits/oracle.py:2806`) —, então "o goleiro abre na seção 34" é impresso, não
afirmado: uma captura em que o goleiro abre na 24 passa com "ok". Também não se compara o
número do painel das costas (1 para o Marcos, 5 para o Edmilson) com a linha do elenco,
nem os 30 quadros, o passo de cerca de 5,6 graus, a câmera parada ou a família por linha;
o `panels_judge` só confere que os dígitos seguem a regra. A planta só fica vermelha
porque injeta ela mesma a cabeça 103. A conferência de família ("figure %d is of no
family") nunca foi vista vermelha, embora o critério de pronto peça "FAIL no juiz da
família". É a armadilha "juiz que imprime em vez de afirmar".

## Evidência

```text
$ grep -n 'head = report\["figures"\]\[0\]\["head"\]' tools/kits/oracle.py
2806:            head = report["figures"][0]["head"]
$ python3 - <<'PY'
import json
k=json.load(open("work/kits-oracle/edit-8-0.json"))
for ph in ("front","turn"):
    for s in k[ph]:
        for nm in s["named"]:
            if nm[0].endswith("MODEL.BIN") and nm[1]==34: nm[1]=24
json.dump(k,open("head24.json","w"))
PY
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edit-number 8 --frame-json head24.json | tail -1
  ok    the goalkeeper opens at section 24, Circle turned it -166 degrees in 30 frame(s), and its back panel holds number 1
```

## Root cause

Hipótese sobre a intenção: o juiz foi escrito para conferir consistência interna, com a
cabeça tirada do que a captura abriu. Os valores do G7 nunca viraram constantes esperadas
por (slot, linha). O vazio do juiz em si está provado acima.

## Fix

Pôr as expectativas medidas em `tools/kits/oracle.py` — por exemplo uma tabela por
(slot, linha): cabeça 34 ou 24, família goleiro ou jogador, número 1 ou 5, 30 quadros de
giro — e fazer o `edit_number_judge` afirmá-las, junto com o "mesma página antes e depois
do giro". Acrescentar casos ao selftest e um controle ao catálogo de
`tools/kits/controls.py`, inclusive um que deixe vermelha a conferência de família.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- tools/kits/selftest.py
- tools/kits/controls.py

## Verificação

Rodar o heredoc acima e depois
`python3 tools/kits/oracle.py --edit-number 8 --frame-json head24.json; echo $?`: tem de
imprimir um FAIL sobre a cabeça e sair 1. Hoje imprime ok e sai 0.

## Log de Execução

- 2026-10-09 — triagem: **REPRODUCED**, à mão (o heredoc da Evidência grava `head24.json` no
  diretório corrente; refeito com saída no scratchpad). Com a cabeça 34 trocada por 24 na captura,
  `--edit-number 8 --frame-json head24.json` imprimia `ok    the goalkeeper opens at section 24, …`
  e saía 0.
- `oracle.py`: `EDIT_EXPECT` por (slot, linha) — cabeça, família, número, quadros do giro e kit,
  lidos de `edit-8-0.json` e `edit-8-1.json` —, e o `edit_number_judge` os afirma (o quadro com folga
  `EDIT_FRAMES_SLACK = 2`). A cabeça esperada vem da tabela, não da captura; (slot, linha) sem
  entrada é impressa como não julgada.
- `selftest.py`: casos de família nenhuma, família trocada, outro número, outro tamanho de giro e
  outro kit. `controls.py`: `oracle-edit-number-family-blind` e `oracle-edit-number-number-unasked`.
- Verificação:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edit-number 8 --frame-json <scratch>/head24.json; echo $?
  FAIL  no figure opened at section 34
1
$ … --edit-number 8 --frame-json work/kits-oracle/edit-8-0.json
  ok    the goalkeeper opens at section 34, Circle turned it -166 degrees in 30 frame(s), and its back panel holds number 1
$ … --edit-number 8 --player 1 --frame-json work/kits-oracle/edit-8-1.json
  ok    the player opens at section 24, Circle turned it -168 degrees in 30 frame(s), and its back panel holds number 5
$ python3 tools/kits/controls.py --only oracle-edit-number-family-blind | tail -1
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only oracle-edit-number-number-unasked | tail -1
controls: 1 of 1 red
```

  `selftest.py`: `kits_selftest: 0 failure(s)`.
- **Closed** — commit `fe188ba` (2026-10-09): fix(kits): assert G7's measured head, family, number, turn and kit in --edit-number
  - Files (`git show --name-status fe188ba`):
    - `M docs/tasks/kits-3d/CORR-K3D-020.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/controls.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
