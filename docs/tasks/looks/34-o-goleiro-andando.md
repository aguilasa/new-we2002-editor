---
id: LOOKS-TASK-34
title: "O goleiro — figura 1 montada e andando na tela, conferida no slot 1"
type: verificação
category: oráculo
phase: 11
depends_on: [LOOKS-TASK-33]
status: in-progress
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.4"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
---

# LOOKS-TASK-34: O goleiro

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.4, e §6 (b).
- **O goleiro é o mesmo esqueleto com duas peças remodeladas** (§1.5), na
  lista 1 do `EDT_MOD.BIN`. Se a animação é a mesma, a pose se aplica às seções
  da lista 1; se não for, é outra entrada.
- **As tasks anteriores medem os dois slots**, mas o que implementam pode ter
  sido exercitado só na figura 0. Resultado negativo é resultado.

---

- **Da [`LOOKS-TASK-33`](/docs/tasks/looks/33-a-janela-animada.md):** o
  `confront.py --silhouette 1` já julga **oito passadas** do ciclo no slot 1,
  as duas metades incluídas, sem `N` na linha de comando — medido em
  2026-09-25, a melhor passada a 13–15% da tinta do jogo e a 1–3 passadas da
  nomeada. E o `oracle.py --rhythm` mostrou o goleiro lendo os pares da
  **mesma entrada 5** que o jogador de linha em todas as linhas menos `FOOT`,
  onde o jogo toca a entrada 147 nos dois slots. O que sobra para esta task é
  olhar a janela, e o que for só da figura 1.

---

## Objetivo

Conferir que o slot 1 sai com a placa `GK`, a figura 1 montada, vestida e
andando igual ao jogo, e corrigir o que só funcionava na figura 0.

---

## Critério de conclusão

- [x] `.\make.ps1 looks -State 1` olhado, com captura no Log.
- [x] Qual animação a figura 1 usa, medido.
- [x] `confront.py --silhouette 1 <N>` em pelo menos oito N, dentro do limiar.
- [x] O que diferia entre as figuras corrigido, ou aberto como CORR com a
      tupla nomeada.

---

## Log de Execução

### 2026-09-26 — executada

**Resultado: nada que só funcionasse na figura 0.** O slot 1 sai com a placa
`GK`, a figura 1 montada, vestida e andando, e cada medição da figura 1 bate
com a da figura 0 no mesmo instrumento. Nenhuma CORR aberta, e o critério 4
fecha pelo negativo — medido abaixo, não presumido.

**Critério 1 — a janela olhada.** O `.\make.ps1 looks -State 1` chama o mesmo
`ui/app.py --state 1` com `--visible`; olhar à vista não é o que esta máquina
admite sem o usuário pedir (`CLAUDE.md`, "fora da tela"), então a captura saiu
do mesmo app estacionado em -32000:

```
work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --state 1 --frame 0 --screenshot <png>
  A-A1-A-A-A, figure 1: 629 primitive(s), 629 textured, 6 surface(s), 1258 triangle(s)
  plate GK, shirt 'SHIRT N', title 'S SET'
  sprites ... plate clut 192,499 ...
work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --state 2 --smoke
  A-A1-A-A-A, figure 0: 593 primitive(s), 593 textured, ...
  plate CB, ... plate clut 208,499 ...
work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --state 1 --animate-for 1.287 --smoke
  walk: pass 34 (0 of the cycle's 34), ... 33 pass change(s) drawn; ran 77.005 frame(s) in 1.287339 s
```

Capturas em `work/looks-shots/task34/` (fora do git): `gk-frame0.png` e
`gk-frame17.png` (as duas metades do ciclo), `s1-f24.png` e `s2-f24.png`.
Olhadas lado a lado com `work/looks-shots/walk-silhouette-1-60.png`, a foto do
jogo: placa `GK` na CLUT própria, uniforme lilás com luvas brancas, calção e
meião do goleiro, chuteira preta — o mesmo que o jogo mostra. A caixa de ajuda
segue na fonte de apoio, que é a da LOOKS-TASK-39 e não da figura.

**Critério 2 — a animação da figura 1.** `python tools/looks/oracle.py --pose 1`
e, de controle, `--pose 2`, os dois a partir de `load_state`:

```
  -- slot 1 (goalkeeper) --
  /BIN/ANIME.BIN at 0x8017ee00: 396804 of 396804 byte(s) equal
    header entry 5 (0x8017EE14) read 3 time(s), by 0x800270B8
    the state at 0x80076040 plays list 0x801947F4, frame 0x80194194
oracle --pose: 0 problem(s)
  -- slot 2 (outfield player) --
    header entry 5 (0x8017EE14) read 3 time(s), by 0x800270B8
    the state at 0x80076040 plays list 0x801947F4, frame 0x80194194
```

**A mesma entrada 5, a mesma lista e o mesmo quadro nos dois slots**: a
animação é uma só, e a pose se aplica às seções da lista 1. É o que o
`--rhythm` da LOOKS-TASK-33 já tinha visto pelos pares, agora pelo cabeçalho.
E o ciclo que a janela anda no slot 1 é o que o jogo carregou, sem emulador:

```
python tools/looks/anime.py --against-walk 1
  slot 1 (goalkeeper): 34 pass(es) of the cycle, 408 matrix(es), 17 frame(s) in the file, 77 counted frame(s) a cycle
  408 of 408 exact, integer for integer (worst 0)
  control: one visit along, 34 of 408 exact
```

**Critério 3 — a silhueta em oito passadas.** `python tools/looks/confront.py
--silhouette 1`, 50 s:

```
    control: frame 60 captured twice, 2458 pixel(s) of ink, identical, pass 26 both times
    control: frame(s) [70, 79, 89, 99, 108, 118, 128] differ from frame 60 by [488, 694, 1029, 1440, 1472, 1367, 913] pixel(s)
    the eight frames name passes [26, 31, 1, 5, 9, 13, 18, 22] of 34
    slot 1 frame 60   names pass 26; best at pass 24, 2 behind, 333 of 2458 (14%)
    ...
    slot 1 frame 128  names pass 22; best at pass 20, 2 behind, 366 of 2635 (14%)
  the picture trails the named pass by [1, 2, 3] pass(es) over 8 comparison(s), and the bound is 3
confront --silhouette: 0 problem(s) over 1 slot(s)
```

Oito passadas espalhadas pelas duas metades (1 a 31), a melhor a 13–15% da
tinta do jogo e a 1–3 passadas da nomeada, dentro do limiar de `WALK_LAG`.

**Critério 4 — o que diferia, e o que não é da figura.** Nada diferiu entre as
figuras. O que as fotos mostram diferente do jogo é **onde a figura senta no
painel**, e isso não é da figura 1: a caixa da tinta normalizada pelo painel,
medida nas capturas acima com um script de rascunho (bbox da tinta contra o
fundo por linha),

```
                        esquerda  topo   direita  base
jogo slot 1, quadro 60   0.384   0.214   0.690   0.974
janela slot 1, passada 24 0.215  0.118   0.545   0.908
jogo slot 2, quadro 60   0.376   0.214   0.690   0.983
janela slot 2, passada 24 0.253  0.113   0.562   0.908
```

sai à esquerda e acima **nos dois slots**, do mesmo tanto, com o tamanho
batendo (altura 0,76 contra 0,79). É o `scene.ROOT_AT`, que o próprio código
declara escolha de enquadramento — o *draw offset* do GPU não foi medido no
ciclo —, e o `--silhouette` é livre de translação de propósito
(`confront.fit_centre`). Não é defeito da figura 1 e não entra aqui: fica
anotado na LOOKS-TASK-35, que é quem fecha a v2.

