---
id: CORR-KITS-062
---

# CORR-KITS-062 — Conferir ou reescrever o item 5 da DoD: a CLI faz tudo o que a janela faz

Origin: [KITS-TASK-34](/docs/tasks/kits/34-definicao-de-pronto.md)

## Problem

O item 5 da Definição de pronto da §0 diz "A CLI faz tudo o que a janela faz sem importar nada além da fachada". A KITS-TASK-34 o reduziu a "CLI importa só a fachada" e conferiu só a regra de import. A janela desenha a figura 3D por `api.figure` (`tools/kits/ui/app.py:551`), e nenhum subcomando da CLI a chama. A §3.1 do plano também lista um subcomando `check` que não existe. Ainda assim, o `PLAN-KITS-PY.md` agora diz que os cinco itens valem, e a mensagem do commit diz "All five items of PLAN-KITS-PY.md section 0 now hold at HEAD".

## Evidência

```text
$ grep -c 'api.figure' tools/kits/cli.py
0
$ grep -n 'api.figure' tools/kits/ui/app.py
551:            scene = api.figure(self.kit, self.set_box.currentData(), self.figure_box.currentData(),
$ python3 tools/kits/cli.py check --help
cli.py: error: argument command: invalid choice: 'check' (choose from survey, rects, prims, uv, open, tex, teams, info, export, flat, zones)
$ sed -n 293p docs/PLAN-KITS-PY.md
A **CLI** (`tools/kits/cli.py`: `info`, `teams`, `export`, `check`) é o segundo
$ sed -n 47,48p docs/PLAN-KITS-PY.md
5. A CLI faz tudo o que a janela faz sem importar nada além da fachada do
   núcleo, e a janela sai com a mesma paleta e o mesmo painel Fusion no
$ grep -n 'Item 5' docs/tasks/kits/34-definicao-de-pronto.md
21:- [x] Item 5: CLI importa só a fachada; captura igual no Windows e no Linux
```

## Root cause

Hipótese: o critério 5 da task foi escrito como resumo do item da DoD e perdeu a metade "faz tudo"; a regra de import do selftest pareceu cobrir o item inteiro.

## Fix

Uma de duas — **decisão do dono do repositório**:

- (a) Acrescentar à CLI um subcomando que desenhe a figura 3D por `api.figure` (a única capacidade da janela que falta à CLI) e acertar a lista de subcomandos da §3.1 com a real (`check` está listado e não existe).
- (b) Se o 3D é deliberadamente só da janela, reescrever o item 5 da DoD e a §3.1 em `docs/PLAN-KITS-PY.md`, dizê-lo na frase do item 5 do parágrafo de Conferência, e registrar a decisão.

## Arquivos a criar ou modificar

- `tools/kits/cli.py` (opção a)
- `docs/PLAN-KITS-PY.md`
- `docs/tasks/kits/34-definicao-de-pronto.md`

## Verificação

- (a) `grep -c 'api.figure' tools/kits/cli.py` dá 0 hoje e ≥1 depois.
- (b) `sed -n 47,48p docs/PLAN-KITS-PY.md` deixa de afirmar que a CLI faz tudo o que a janela faz.
- Nos dois casos, todo subcomando que a §3.1 lista é aceito por `python3 tools/kits/cli.py <cmd> --help`; hoje o `check` falha.

## Log de Execução
