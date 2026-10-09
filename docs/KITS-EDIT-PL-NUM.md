# Tela EDIT PL. NUM — o que ela mostra sobre o boneco 3D

Relatório da investigação [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md),
fechada em 2026-10-09 (commits `6409a49` e `241b77a`) e revisada no mesmo dia, com três correções
([CORR-K3D-020](/docs/tasks/kits-3d/CORR-K3D-020.md),
[CORR-K3D-021](/docs/tasks/kits-3d/CORR-K3D-021.md),
[CORR-K3D-022](/docs/tasks/kits-3d/CORR-K3D-022.md)). A saída completa das ferramentas, colada da
HEAD, está em [G7 do KITS-AJUSTES-3D](/docs/KITS-AJUSTES-3D.md#g7--tela-edit-pl-num-o-jogo-desenhando-o-número-e-o-giro).
Este documento resume o que foi medido e responde a uma pergunta: **a tela traz algo que a aba 3D
possa usar?**

## A tela

EDIT MODE → EDIT PL. NUM → um time. O jogo abre "背番号エディット": a lista dos 23 jogadores à
esquerda, um boneco 3D no painel central e a grade de números à direita. O boneco abre de frente.
Quando um jogador é confirmado, o boneco gira até ficar de costas e mostra o número.

O state usado é o **slot 8** do DuckStation: Brasil, com o Marcos (goleiro, nº 1) selecionado e de
frente. A cópia mestra é `work/kits-states/SLPM-87056_8.sav`, com sha256
`ee349d74e26eef2cdb9f459ff2360dd15c4e0bdcf36677a9df242bf5b601a184`. A captura do usuário está em
`/home/ingmar/Pictures/2026-10-09_14-34.png`.

## Como foi medido

Todo número abaixo sai de `tools/kits/oracle.py`. A opção `--edit-number` foi criada na task:

```sh
export WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin
export WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue
export DISPLAY=:98 XAUTHORITY=

python3 tools/kits/oracle.py --edit-number 8                 # Marcos, GK 1 (linha 0)
python3 tools/kits/oracle.py --edit-number 8 --player 1      # Edmilson, CB 5 (linha 1)
python3 tools/kits/oracle.py --edit-number 8 --button Cross  # só o Cross
```

A captura fica em `work/kits-oracle/edit-8-<linha>.json`. Com `--frame-json <arquivo>` a mesma
leitura se refaz sem emulador.

O que o juiz afirma está em `EDIT_EXPECT` (`oracle.py`), por slot e linha: a cabeça, a família, o
número, os quadros do giro (com folga de 2) e o kit. Quatro controles do catálogo derrubam esse juiz:

- `oracle-edit-number-head-unasked`;
- `oracle-edit-number-family-blind`;
- `oracle-edit-number-number-unasked`;
- `--plant-edit-number`, que sai 1 com três `FAIL`.

As duas corridas de verdade saem 0. As linhas decisivas são estas:

```text
ok    the goalkeeper opens at section 34, Circle turned it -166 degrees in 30 frame(s), and its back panel holds number 1
ok    the player opens at section 24, Circle turned it -168 degrees in 30 frame(s), and its back panel holds number 5
```

## O que foi encontrado

### 1. O modelo é o da `LOOKS SET`, não o de partida

As duas figuras vêm do `EDT_MOD.BIN`, o mesmo arquivo que a `LOOKS SET` e a aba 3D usam:

- **goleiro:** lista 1, seções 11 a 19, mais a chuteira 9 compartilhada. A outra chuteira, a 10,
  aparece como `?` porque nenhuma parada a nomeia;
- **jogador de linha:** lista 0, seções 0 a 9.

Ordem de desenho, cabeça primeiro, nos 14 quadros de frente e nos 99 do giro:

```text
goleiro: MODEL.BIN:34 EDT_MOD.BIN:11 12 14 13 15 16 18 9 17 19 ?
jogador: MODEL.BIN:24 EDT_MOD.BIN:0 1 3 2 4 5 7 9 6 8 ?
```

Nenhuma seção de braço, manga ou braçadeira do `MODEL.BIN` entra. **Negativa:** a braçadeira 91 ou
94, que o G4 dá como "não vista", também não aparece aqui.

### 2. A cabeça muda: 34 no goleiro, 24 no jogador

A única seção do `MODEL.BIN` que a tela desenha é a cabeça:

- a do jogador de linha é a **24**, a mesma que a `LOOKS SET` desenha (`pieces.HEAD_SECTION`);
- a do goleiro é a **34**.

A aba desenha a 24 nas duas figuras. A hipótese plausível é que a cabeça seja do *jogador*, não da
figura: o `MODEL.BIN` tem várias cabeças, e a `LOOKS SET` troca o cabelo. **Isso não foi medido.**
Só há um goleiro e um jogador de linha medidos, e não dá para dizer se a 34 vem do Marcos ou de
qualquer goleiro.

### 3. O uniforme é o mesmo da partida

A tela veste o `TEX_41` (Brasil), conjunto 1, nas páginas da partida:

- **uniforme** em (576,256);
- **mangas** em (576,384);
- **paletas** nas linhas 486 (jogador) e 488 (goleiro).

As mangas são as peças de braço de cada lista do `EDT_MOD.BIN`: longas no goleiro e curtas no
jogador, como na `LOOKS SET`.

### 4. Não há pose parada, e a câmera não foi derivada (negativa)

O boneco **caminha** também nesta tela. De frente, a guinada do torso oscila entre −9,9° e −11,4°
no goleiro e entre −10,0° e −12,7° no jogador. Ela muda a cada quadro, e a perna aparece levantada
na captura. Os arquivos `work/kits-pose/slot8-row<linha>-{front,back}.json` guardam um quadro dessa
caminhada, não uma pose parada.

A câmera não foi derivada, porque a leitura não captura o par do `ANIME.BIN` que o
`camera_from_pieces` exige. O que se sabe é a posição do torso: (3, −54, 3778) no goleiro e
(−1, −44, 3778) no jogador. **Ela não muda com o giro.**

### 5. O giro: Circle, 30 quadros a cerca de −5,6° por quadro

Quem confirma o jogador é o **Circle**. O torso gira de −12° até ±180° em **30 quadros**. Quase
todo passo é de −5,6° a −5,7°, com algumas exceções (−4,2, −4,3 e −7,0). A translação não se mexe,
então a câmera é a mesma de frente e de costas. Depois do giro o boneco continua caminhando de
costas, com um balanço de ±2° por quadro.

O **Cross não confirma**. Ele volta para a seleção de time, e a carga de matriz por peça para de
disparar ([CORR-K3D-022](/docs/tasks/kits-3d/CORR-K3D-022.md)):

```text
Cross pressed: did not turn the figure; the per-piece matrix load gave 313 of 1200 stop(s) (12 whole figure(s)), then stopped firing for 20 s
```

### 6. O número nas costas segue a regra da partida e é escrito ao selecionar

Na página de uniforme, só diferem do disco os dois painéis do torso: (0,80) e (100,104), com 480 px
cada. O painel da figura mostrada tem o número pela regra do §4.7: um dígito em (7,7), sobre as
costas da camisa, sem nenhum pixel que a regra não explique. Medido assim:

- Marcos: o 1 no painel do goleiro (100,104);
- Edmilson: o 5 no painel do jogador (0,80).

A página é **a mesma antes e depois do giro**. O jogo escreve o painel quando a linha é selecionada,
e não quando o boneco vira.

## Diagnóstico: a tela traz algo que a aba possa usar?

**Para o desenho do boneco, quase nada de novo.** A tela é a figura da `LOOKS SET` vestida com o
uniforme da partida. É a mesma combinação que a aba 3D já monta: mesma geometria (`EDT_MOD.BIN`,
listas 0 e 1), mesmas mangas, mesmas páginas e paletas do `TEX_*`, mesmo painel de número. A tela
**não** dá o que se esperava dela:

- pose parada: não tem;
- câmera própria: não foi derivada;
- seções de partida (91, 94): não aparecem.

O que ela dá, item por item:

| Achado | Valor para a aba | Uso |
|---|---|---|
| Geometria `EDT_MOD.BIN` nas duas figuras | **Confirmação.** Uma segunda tela do jogo desenha o boneco do mesmo jeito que a aba | nenhuma mudança |
| Número nas costas pela regra do §4.7, fora de partida e nas duas figuras | **Confirmação.** Antes a regra vinha só do slot 5, uma partida; agora vale também aqui, com o painel do goleiro medido | nenhuma mudança; o Number da aba já faz isso |
| Cabeça 34 no goleiro | **Novo, e o único achado que pode mudar o desenho.** A aba põe a 24 nas duas figuras | se a cabeça for por jogador, a aba precisa saber qual cabeça cada jogador usa |
| Giro de 30 quadros a cerca de 5,6° por quadro, com a câmera parada | **Novo, mas cosmético.** É a regra de um "virar de costas" animado | só se a aba ganhar esse botão; hoje ela gira pelo mouse |
| Kit `TEX_41` nas páginas de partida | confirmação do que o `oracle.py --kit` já media | nenhuma mudança |
| Pose, câmera, 91/94 | **Negativas.** | nenhum |

**Recomendação.** Se for abrir uma task a partir disto, que seja a da **cabeça**. É o único achado
que diz que a aba pode estar desenhando algo diferente do jogo, e medir sai barato: o mesmo slot 8 e
o mesmo `--edit-number`, descendo a lista até os outros goleiros do Brasil e alguns jogadores de
linha (`--player N`). Assim se vê se a seção da cabeça acompanha o jogador ou a figura.

O giro animado pode esperar até a aba ter motivo para mostrar as costas sozinha. A regra já está
medida e não se perde: está em G7 e em `EDIT_EXPECT`.
