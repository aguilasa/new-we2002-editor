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

Reproduzido em 2026-10-05 sobre `5299494`: `grep -c 'api.figure' tools/kits/cli.py` dá `0`, e
`cli.py check --help` sai com `invalid choice: 'check'`.

Decisão do dono do repositório, nesta sessão: **opção (a)**, a CLI ganha a figura 3D.

Conserto:

- `tools/kits/cli.py figure <origem> [--tag T] [--set 1|2] [--figure 0|1] [--geometry BIN]`
  chama `api.figure` como a janela (`frame=api.FIGURE_POSE`, geometria lida uma vez). Imprime
  uma linha por conjunto e figura (peças, peças texturizadas, superfícies, limites, sha256 da
  cena) e, com os dois conjuntos, se eles diferem.
- O `--negative` desenha o conjunto 2 como o 1 e só passa se o veredito virar.
- `selftest.py --image` (alvo `kits_image`) ganhou `_figure_cli_checks`, com três afirmações:
  - o digest do `cli.py figure` para `TEX_00`, conjunto 1, figura 0, é o da chamada da janela;
  - os conjuntos diferem nas duas figuras;
  - o `--negative` sai 0.
- `docs/PLAN-KITS-PY.md`:
  - §3.1: lista `info`, `teams`, `export`, `figure` e diz que o `check` nunca existiu;
  - Conferência do §0: registra a metade do item 5 que faltava.
- `docs/tasks/kits/34-definicao-de-pronto.md`: o critério do item 5 remete a esta CORR.

```text
$ python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 00 | cut -c1-90
set 1 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)
set 1 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)
set 2 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)
set 2 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)
figure 0: set 1 and set 2 differ
figure 1: set 1 and set 2 differ
$ python3 tools/kits/cli.py figure --negative roms/japanese-shift-jis.bin --tag 00 | tail -1
negative: 2 of 2 figure(s) whose sets differ come out the same with the set ignored -- ok
```

`TEX_A4`, cujo suplente é igual ao titular, dá `0 of 0 ... -- FAIL` no `--negative`, com saída
1: o controle não passa onde não há o que virar.

Vermelho visto: numa cópia da árvore no scratchpad, a chamada do `cmd_figure` foi trocada para
`api.figure(kit, 1, figure, …)`, isto é, o conjunto ignorado.

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $S/tools/kits/selftest.py --image | grep -E "cli.py figure|failure"
  FAIL  cli.py figure tells set 1 from set 2 on TEX_00, for both figures    ab81491bd0f654d0…
  FAIL  cli.py figure --negative: the set ignored is seen red  negative: 0 of 0 figure(s) whose sets differ come out the same with the set ignored -- FAIL
figure: 2 failure(s)
```

Na árvore real, o mesmo comando dá:

```text
  ok    cli.py figure draws the window's scene: TEX_00 set 1 figure 0 digest ab81491bd0f654d0
  ok    cli.py figure tells set 1 from set 2 on TEX_00, for both figures
  ok    cli.py figure --negative: the set ignored is seen red
figure: 0 failure(s)
```

Verificação: `grep -c 'api.figure' tools/kits/cli.py` dá `2`, e `info`, `teams`, `export` e
`figure` saem 0 com `--help`. `ctest --test-dir build -R kits` dá `100% tests passed, 0 tests
failed out of 4`, e `python3 tools/kits/controls.py` dá `controls: 24 of 24 red`.
- **Closed** — commit `f363279` (2026-10-05): feat(kits): cli.py figure draws the window's 3D scene
  - Files (`git show --name-status f363279`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/34-definicao-de-pronto.md`
    - `M docs/tasks/kits/CORR-KITS-062.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/selftest.py`
