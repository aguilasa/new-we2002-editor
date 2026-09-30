---
id: LOOKS-TASK-35
title: "Fechamento da v2 — gates, `make.ps1 looks` e reconciliação do plano"
type: documentação
category: fechamento
phase: 11
depends_on: [LOOKS-TASK-23, LOOKS-TASK-29, LOOKS-TASK-30, LOOKS-TASK-31, LOOKS-TASK-34, LOOKS-TASK-36, LOOKS-TASK-37, LOOKS-TASK-38, LOOKS-TASK-39, LOOKS-TASK-40]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.5"
reviewed_on: 2026-09-26
review_commit: bff49a1c
done_on: 2026-09-26
done_commit: 7e462e60
resources: [emulador, tela]
---

# LOOKS-TASK-35: Fechamento da v2

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10 inteira, e a regra da [`LOOKS-TASK-20`](/docs/tasks/concluidos/looks/20-reconciliacao-e-entregaveis.md): o que a
  execução muda no plano muda na seção que mudou.
- **O `.\make.ps1 looks` existe desde 2026-09-17** e abre a v1. É o alvo que o
  usuário usa, e é aqui que ele passa a abrir o que a gravação e os save
  states mostram.

---

- **Da [`LOOKS-TASK-33`](/docs/tasks/concluidos/looks/33-a-janela-animada.md):** a
  janela anda por default, `Space` pausa e `.` anda uma passada — o `help` do
  `.\make.ps1 looks` ainda não diz isso. Dois comandos novos com emulador,
  sem alvo de `ctest`: `oracle.py --rhythm` (~9 min) e o `confront.py
  --silhouette` refeito sobre oito passadas (~2 min). E ficam **abertos**, com
  veredito a dar na §10.3: o **giro** do modelo nas cinco linhas de cabeça
  (a janela segura o quadro 12 sem girar) e a **animação 147** que o jogo toca
  em `FOOT` (a janela continua andando ali e o relatório diz).

---

- **Da [`LOOKS-TASK-34`](/docs/tasks/concluidos/looks/34-o-goleiro-andando.md):** a
  figura 1 não tem nada próprio a corrigir, mas as fotos mostraram **onde a
  figura senta no painel** longe do jogo, nos dois slots do mesmo tanto: a
  caixa da tinta, em fração do painel, começa em (0,219, 0,117) na janela
  contra (0,377, 0,208) no jogo no slot 1 — e (0,219, 0,125) contra (0,377,
  0,208) no slot 2 —, com o tamanho batendo; quem mede é `python
  tools/looks/confront.py --placement [SLOT]` (CORR-LOOKS-097). É o `scene.ROOT_AT`,
  escolha de enquadramento declarada — o *draw offset* do GPU nunca foi
  medido —, e nenhum gate o julga: o `--silhouette` é livre de translação de
  propósito. Pede veredito na §10.3 — medir o offset, ou registrar a escolha
  como tal.

---

## Objetivo

Fechar a v2: gates novos alcançáveis pelo `ctest`, o alvo do usuário abrindo a
tela `LOOKS SET` com o boneco montado, vestido e andando, e plano, perfil e
`CLAUDE.md` batendo com o disco.

---

## Critério de conclusão

- [x] `.\make.ps1 looks` abre a tela com o boneco montado, vestido e
      andando; o `help` diz os controles.
- [x] Os comandos novos que precisam do emulador dentro de um alvo de `ctest`
      ou decididos como comando de mão, **e isso escrito** — a pergunta que a
      [`LOOKS-TASK-19`](/docs/tasks/concluidos/looks/19-alvos-de-ctest-e-cli.md) respondeu para o `--check-live`.
- [x] `ctest -R looks` com o número copiado de uma corrida que listou os alvos
      pelo nome, numa máquina limpa e com tudo apontado.
- [x] Cada incógnita da §10.3 com veredito: respondida com a medição, ou
      aberta com a razão e o que a destravaria.
- [x] §0, §6 (e), (f) e (h), perfil e `CLAUDE.md` reconciliados.
- [x] `check_tasks.py` verde e a conferência de links sem linha nova.

---

## Log de Execução

### 2026-09-26 — executada

**O que mudou de código, e por quê.** A nota da LOOKS-TASK-34 pedia veredito
sobre **onde a figura senta no painel**, e ele saiu medido em vez de aberto. O
corpo inteiro era posto por uma fração escolhida (`scene.ROOT_AT = (0.5,
0.85)`) sob o argumento de que o *draw offset* do GPU não estava medido — e
estava: `oracle.SCENERY_CENTRE`, o meio do display, que é o `panel_axis` que o
close-up já usava. O `scene.panel_camera` agora enquadra as doze linhas pelo
mesmo eixo, com a câmera de corpo inteiro reassentada na peça de referência
(`rebased`), e recusa sem o lugar dela; o `ROOT_AT` saiu. Com um self-check
novo no `scene.py --check` e um controle plantado
(`scene-full-figure-by-hand`: 109 de 109 controles vermelhos).

```
python tools/looks/confront.py --placement          # antes (ROOT_AT)
    the window's figure sits -0.158 across and -0.083 down of the game's, 0.783 against 0.767 tall
    the window's figure sits -0.158 across and -0.092 down of the game's, 0.792 against 0.767 tall
python tools/looks/confront.py --placement          # eixo medido
    game,   frame  60   0.377 0.208 0.719 0.975
    window, pass 26     0.384 0.217 0.712 0.975
    the window's figure sits +0.007 across and +0.008 down of the game's, 0.758 against 0.767 tall
    game,   frame  60   0.377 0.208 0.705 0.975
    window, pass 24     0.384 0.217 0.705 0.975
    the window's figure sits +0.007 across and +0.008 down of the game's, 0.758 against 0.767 tall
confront --placement: 0 problem(s) over 2 slot(s)
```

E o `--placement` passou a **afirmar** (`confront.PLACEMENT_SLACK = 0.03`, cada
borda da caixa). O vermelho, com o `scene.py` antigo posto de volta numa
corrida:

```
  FAIL  slot 2: the window's figure sits 0.158 of the panel off the game's, over the 0.030 allowed
  FAIL  slot 1: the window's figure sits 0.158 of the panel off the game's, over the 0.030 allowed
confront --placement: 2 problem(s) over 2 slot(s)
```

**Critério 1 — o alvo.** O `help` do `.\make.ps1` ganhou a caminhada:

```
pwsh -NoProfile -File make.ps1
                O boneco ANDA no ritmo medido do jogo (um ciclo
                de 1,287 s): ESPACO pausa e retoma, PONTO anda
                uma passada. Nas cinco linhas de cabeca e em
                BOOTS o painel aproxima, como no jogo
```

O alvo roda `app.py --image <img> --state N --visible`; abrir à vista não é o
que esta máquina admite sem o usuário pedir, então a conferência é o mesmo
comando sem o `--visible`, que estaciona a janela em −32000:

```
work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --image roms/japanese-shift-jis.bin --state 2 --animate-for 0.3 --screenshot t35-0.3.png
  A-A1-A-A-A, figure 0: 593 primitive(s), 593 textured, 6 surface(s), 1186 triangle(s)
  walk: pass 7 (7 of the cycle's 34), ... 7 pass change(s) drawn; ran 17.957 frame(s) in 0.300205 s
... --animate-for 0.6 ...
  walk: pass 15 (15 of the cycle's 34), ... 15 pass change(s) drawn; ran 35.904 frame(s) in 0.600228 s
app.py --compare t35-0.3.png t35-0.6.png
t35-0.3.png vs t35-0.6.png: 9161 of 491520 pixel(s) differ (1.86%)
```

Montado e vestido (593 de 593 texturizadas), andando (duas fotos diferem), e
olhado: a figura agora centrada no painel como na foto do jogo.

**Critério 2 — os comandos de emulador: de mão, por decisão, escrita** na §4.4
do plano — custo de 20 s a 12 min, vários são geradores do gabarito que o
`looks_ui` lê, e o que medem já tem guarda sem emulador. A coluna *sem alvo
ainda* do perfil passa a querer dizer isso; o `--placement` entrou nela.

**Critério 3 — `ctest -R looks`**, build fora da árvore (`cmake -S . -B
$TEMP/build-looks35 -G Ninja -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake`):

```
env -u WE2002_LOOKS_IMAGE -u WE2002_LOOKS_DRIVE_IMAGE ctest --test-dir $B -R looks
3/4 Test #12: looks_ui .........................***Skipped   0.22 sec
4/4 Test #13: looks_live .......................***Skipped   0.15 sec
100% tests passed out of 4
	 11 - looks_image (Skipped)
	 12 - looks_ui (Skipped)
	 13 - looks_live (Skipped)
WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... ctest --test-dir $B -R looks
1/4 Test #10: looks_selftest ...................   Passed   36.05 sec
2/4 Test #11: looks_image ......................   Passed    2.99 sec
3/4 Test #12: looks_ui .........................   Passed  370.70 sec
4/4 Test #13: looks_live .......................   Passed    9.18 sec
100% tests passed out of 4
```

**1 passed, 3 skipped** limpo; **4 passed** apontado — depois da mudança de
enquadramento, então o `looks_ui` julgou a janela nova.

**Critério 4 — §10.3.** Uma tabela de vereditos abre a seção. (q), (r), (j),
(k) respondidas; (m), (s), (n), (o) fechadas; a (l) **fechada** — o ponto que
ela deixava aberto são as seis médias, e `anime.py --against-walk` dá 408 de
408 nos dois slots; a (m) ganhou a medição do lugar acima. A (p) fecha no
ritmo e deixa **dois pontos abertos**, cada um com razão e destravamento: o
**giro** do close-up (falta a curva por passada; o `camera_from_pieces` a cada
passada de uma linha de cabeça a daria) e a **animação 147** de `FOOT` (o
`--walk` com o cursor em `FOOT`, e o `--against-walk` contra ela).

**Critério 5 — reconciliação.** §0 ganhou "A v2, percorrida em 2026-09-26",
item a item com a ferramenta de cada um, e a nota de que a ressalva do item 3
é da v1. §6 (e) **fechada**, com o texto antigo mantido como histórico; (f)
já estava; (h) com as oito passadas e o aviso de que a silhueta não testemunha
o lugar. Perfil: a linha do `--placement` na tabela de gates e a armadilha 104
(o "não medido" que envelhece), com a 97 corrigida. `CLAUDE.md`: a v2
fechada, os dois abertos nomeados, e o `--placement` afirmando.

**Critério 6 — conferência.**

```
python tools/check_tasks.py
check: 0 error(s), 11 warning(s) in 4 cycle(s)
```

Os onze avisos são de prefixo no arquivo `concluidos/` (PAR-TASK), anteriores.
Links: a varredura de destino da `.claude/rules/links.md` dá a **mesma** saída
antes e depois (uma linha, `docs/prompts/02-revisar.md`, que já era quebrada),
e a de forma dá 307 linhas relativas antes e depois, nenhuma nova no diff.
- **Closed** — commit `7e462e60` (2026-09-26): feat(looks): close v2 with the full figure framed on the measured axis
  - Files (`git show --name-status 7e462e60`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/35-fechamento-da-v2.md`
    - `M make.ps1`
    - `M tools/looks/confront.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/scene.py`
- **Reviewed** (2026-09-26) at `bff49a1c`: CORR-LOOKS-098, CORR-LOOKS-099
