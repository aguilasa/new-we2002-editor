# Plano — a animação da linha `FOOT` na tela `LOOKS SET`

Proposta de 2026-09-30, para virar ciclo por `/rite:plan-to-tasks`. **Nenhuma
fase foi executada**; o que está marcado como medido foi medido antes deste
plano, com o comando ao lado.

É continuação do visualizador de aparência (`tools/looks/`), cuja v2 fechou
com esta animação **aberta**: ver a §10.3 (p) do
[PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md). Tudo que aquele plano decidiu vale
aqui sem ser repetido — só lê, disco japonês para os bytes, `.cue` inglês para
dirigir o emulador, `load_state` como ponto de partida de toda medição, render
por `QOpenGLWidget`, nada em `src/`.

## 0. Escopo

### Objetivo

Com o cursor na linha `FOOT`, o painel da janela faz o que o jogo faz: sai da
caminhada, toca a **entrada 147** do `ANIME.BIN` no ritmo e na forma que o jogo
a toca, e volta para a caminhada ao sair da linha, do jeito que o jogo volta.
Hoje a janela continua andando ali e o relatório diz que não modela a outra
animação (`layout.WALK_OTHER_ANIMATION`).

### Não-objetivos

- **Não grava.** Nem imagem, nem cartão — a mesma decisão da v1 e da v2.
- **Não modela outras animações do `ANIME.BIN`.** São 197 blocos; este plano é
  sobre a que a tela `LOOKS SET` toca em `FOOT`, e só. Se a medição mostrar que
  outra linha ou outro valor toca uma terceira entrada, isso é incógnita nova
  (§2), não escopo implícito.
- **Não generaliza por generalizar.** O código da caminhada está amarrado à
  entrada 5 (§1.4); ele passa a receber a entrada como parâmetro na medida em
  que a 147 precisa, sem virar um tocador de animação genérico.
- **Não usa a gravação de tela do usuário** para ritmo ou pose — a mesma regra
  da Fase 11 da v2: quem mede é `frame_step`.

### Definição de pronto

1. A 147 medida no jogo nos dois slots: quantas passadas, se repete ou para, o
   que cada valor de `FOOT` (`RIGHT`, `LEFT`, `BOTH`) faz com ela, e o que
   acontece ao entrar e ao sair da linha — cada um com o comando que o mede e
   um controle que fecha antes.
2. Um reprodutor que acerta **entrada por entrada** o que o jogo carrega nas
   passadas da 147, sem emulador, como o `anime.py --against-walk` acerta
   408 de 408 na caminhada; com o controle deslocado de uma visita caindo.
3. A janela troca de animação ao entrar em `FOOT` e volta ao sair, no ritmo
   medido; o `looks_ui` julga isso com controles plantados, e a silhueta do
   jogo nessa linha fica dentro do limiar da caminhada.
4. `layout.WALK_OTHER_ANIMATION` deixa de ser nota: ou a janela modela o que
   ele nomeia, ou o que sobrou está escrito com razão e destravamento.
5. Plano de origem (§10.3 (p) do PLAN-LOOKS-PY), perfil e `CLAUDE.md`
   reconciliados.

## 1. O que já se sabe

### 1.1 A linha

`FOOT` é a última das doze. Guarda dois bits no byte 11 do registro do jogador
(`looks.py`, campo `foot`, `Piece(11, 6, 0x03)`), e a tela escreve **três**
valores — `RIGHT`, `LEFT`, `BOTH` —, travando nas duas pontas
(`tools/looks/screen.json`, linha `FOOT`, `"left": "locks"`, `"right":
"locks"`). O valor **não** entra na tupla de montagem (`A-A1-A-A-A` são pele,
cabelo, cor do cabelo, barba e cor da barba), então nada da geometria muda com
ele — o que muda, se mudar, é a animação.

A câmera da linha é a de **corpo inteiro**, idêntica número a número à da
linha de carga ([`LOOKS-TASK-40`](/docs/tasks/concluidos/looks/40-a-camera-do-close-up.md),
`oracle.py --closeups`). Isso tira a câmera do risco deste plano.

### 1.2 O que o jogo faz ali, medido

A [`LOOKS-TASK-33`](/docs/tasks/concluidos/looks/33-a-janela-animada.md) classificou cada
linha pela origem dos pares que a montagem de pose lê (`oracle.row_walk`,
`oracle.pair_owner`, `oracle.classify_walk`), dentro do `oracle.py --rhythm`:

```text
    row NAT       (0 Down) the figure walks
    row SKIN      (1 Down) the figure is HELD on frame 12 of the walk
    ...
    row FOOT      (2 Up) the figure plays animation (147,) instead of the walk
```

Nos dois slots. E a leitura passa do **quadro 43** da 147, onde a caminhada tem
17 (docstring de `layout.WALK_OTHER_ANIMATION`). `FOOT` é alcançada com dois
`Up` a partir da linha de carga, e não descendo, porque descer atravessa todas
as outras (`oracle.RHYTHM_UP_ROWS`).

### 1.3 A entrada 147 no disco

Medido em 2026-09-30, com o leitor do ciclo (`anime.header`, `anime.block`) —
ainda sem comando versionado que o imprima, o que a Fase 1 corrige:

| entrada | quadros | bytes no arquivo | compartilhada |
|---|---|---|---|
| 5 (a caminhada) | 17 | 86932..88636 | — |
| **147** | **47** | **64796..69308** | com nenhuma outra |

47 × 96 = 4.512 bytes, o tamanho de quadro de sempre (`anime.FRAME_BYTES`). É a
maior das vizinhas — 140 a 151 têm de 11 a 29 quadros —, e o nome da linha
sugere um chute com o pé preferido. **Isso é palpite pelo nome**, e o plano o
trata como tal.

### 1.4 Onde a caminhada está amarrada à entrada 5

`layout.ANIME_SCREEN_ENTRY = 5` é lido direto em `anime.py` (o `pose` e o
`--against-walk`), `oracle.py` (o `--walk`, o `--rhythm`, a montagem das
passadas), `scene.py` (o relógio e o lugar da peça de referência) e
`confront.py` (as três silhuetas). E há o que foi **medido para a 5** e pode
não valer para a 147:

- `anime.WALK_SWAP` e `anime.WALK_RULES` — o espelho do segundo lado, lido das
  dez variantes de desempacotamento do dispatch `0x80011DA0`;
- `anime.WALK_FIRST_SLOT` e a média `(a + b) >> 1` na visita que abre cada
  lado (`layout.ANIME_BLEND_MODE`);
- `layout.WALK_HELD_ROWS` / `WALK_HELD_FRAME` — o que o cursor faz com o
  relógio;
- o ciclo de **34 passadas em 77 quadros** (`oracle.py --walk`), com a passada
  a cada dois ou três quadros, e a taxa de 59,817 quadros por segundo
  (`layout.FRAME_TICKS`, que é do console e continua valendo).

### 1.5 O precedente mais próximo

O giro do close-up, que a v2 também deixou aberto, fechou em 2026-09-29 pela
[`CORR-LOOKS-107`](/docs/tasks/concluidos/looks/CORR-LOOKS-107.md): o ângulo lido do
próprio jogo (`layout.TURN_ANGLE`, `oracle.py --turn`) contra um modelo puro
(`scene.turn_after`) — repouso, passo por passada, pontas e o sentido guardado
na reentrada. É a forma que este plano copia: medir o estado do jogo por
passada, escrever um modelo sem Qt, e só então ligar a janela.

## 2. As incógnitas, em ordem de risco

**(a) Como a 147 é desempacotada — o maior risco.** A caminhada tem regras de
espelho e uma média que saíram do código do jogo para **aquele** dispatch. Se a
147 passar pelo mesmo caminho, o reprodutor é o mesmo com outra entrada; se
não, é leitura nova de código MIPS. *Mede:* os watches da montagem
(`layout.ANIME_BUILD`, `ANIME_UNPACK`) com o cursor em `FOOT`, e quais das
variantes do dispatch rodam.

**(b) Laço ou tiro único.** 47 quadros podem ser um ciclo, ou uma animação que
toca uma vez e para no último quadro, ou que toca e devolve para a caminhada
sozinha. *Mede:* o dono de cada par (`pair_owner`) por várias centenas de
quadros contados a partir da entrada na linha.

**(c) O que o valor faz.** `RIGHT`, `LEFT` e `BOTH` podem tocar a mesma 147,
a 147 espelhada, ou entradas diferentes — e o estado dos dois slots pode
carregar valores diferentes. *Mede:* a mesma corrida de (b) com o valor
trocado antes de contar, e a leitura do valor carregado em cada state.

**(d) O ritmo.** Se a 147 avança uma passada por desenho como a caminhada, e
se a passada continua sendo a cada dois ou três quadros. *Mede:* o
`--rhythm` com o cursor em `FOOT`.

**(e) Entrar e sair.** Em que quadro a 147 começa ao entrar (do zero, ou de
onde a caminhada estava), e onde a caminhada retoma ao sair — a tela das
linhas de cabeça retoma do quadro seguinte ao que segurou, e aqui pode ser
outra regra. E o que acontece ao trocar o valor **dentro** da linha, no meio
da animação. *Mede:* entrar e sair em quadros diferentes da caminhada, com a
corrida sem tecla de controle.

**(f) O lugar da figura.** A janela assenta a figura pela peça de referência
na âncora da caminhada (`scene.walk_anchor`). Um chute pode mover a raiz;
se mover, a âncora da 147 é outra, e o `--placement` tem de medir o painel
nessa linha também.

## 3. Onde o código muda

Nenhum módulo novo é pressuposto; se um nascer, é porque a Fase 2 mostrou que
a 147 não cabe nas funções da caminhada.

- **`layout.py`** — a entrada e o que se medir dela, cada constante com o
  comando que a mede no docstring, como as da caminhada. `WALK_OTHER_ANIMATION`
  passa a ser consumido, não só anotado.
- **`oracle.py`** — o `--walk` e o `--rhythm` recebem a linha em que o cursor
  fica antes de contar; um comando que diga o que (b) a (e) respondem, com
  controle.
- **`anime.py`** — o `walk_pose` e o `--against-walk` recebem a entrada; o
  relatório passa a imprimir a contagem de quadros de uma entrada pedida, que
  hoje só sai de um trecho de Python solto (§1.3).
- **`scene.py`** — o relógio (`WalkClock`) troca de animação por linha, do
  mesmo jeito que já segura o quadro 12 nas linhas de cabeça; o lugar da peça
  de referência por animação, se (f) pedir.
- **`ui/`** — só o que o relógio decidir chega aqui: a janela continua sem
  decidir nada sobre a tela.
- **`confront.py`** — a silhueta e o lugar com o cursor em `FOOT`.
- **`controls.py`** — um controle plantado por regra nova (a troca de
  animação que não acontece, a volta que não acontece, o espelho de `LEFT`
  trocado).

## 4. Como se verifica

A mesma régua da §10.4 do plano de origem, sem desconto:

1. **Passada contra passada, sem emulador.** O que o reprodutor diz para cada
   peça em cada passada da 147 contra o que o jogo carregou, **exato** — ponto
   fixo é inteiro. Controle: uma visita de deslocamento tem de cair, como caiu
   de 408 para 34 na caminhada.
2. **Silhueta contra silhueta.** A máscara do painel com o cursor em `FOOT`
   em várias passadas da 147, nos dois slots, dentro do limiar de
   `confront.py --silhouette`; o mesmo quadro duas vezes e quadros diferentes
   de controle. **Várias passadas**, porque um quadro certo é pose.
3. **O lugar.** `confront.py --placement` na linha `FOOT`, dentro de
   `PLACEMENT_SLACK`, se (f) mostrar que a raiz se move.
4. **A janela.** O `looks_ui` entra em `FOOT`, anda passadas, troca o valor e
   sai, e exige a animação e o quadro que o modelo diz — com os controles
   plantados de §3. Nenhuma janela à vista: só o `.\make.ps1 looks` / `make
   looks` abre visível.

## 5. Riscos de projeto

- **O dispatch pode ser outro** (§2 (a)). É o que transforma uma
  parametrização em leitura de MIPS; a Fase 1 existe para saber isso antes de
  qualquer código.
- **`LEFT` pode ser espelho, e espelho engana.** A caminhada mostrou que um
  espelho mal aplicado deixa toda peça individualmente plausível e o boneco
  errado — a armadilha do atraso de ponteiro e a das 111 unidades de `x`
  negado (perfil do `looks`). Espelho só entra comparado entrada por entrada.
- **Quarenta e sete quadros não são um ciclo por decreto.** Se a animação
  toca uma vez, o relógio da janela ganha um estado que a caminhada não tem
  ("acabou"), e a volta para a caminhada vira regra medida, não suposta.
- **O ciclo `looks` está arquivado.** As armadilhas dele moram em
  `docs/prompts/perfil-looks.md` e `perfil-looks.armadilhas.md`; o ciclo novo
  precisa de perfil próprio que as cite, e não de cópia delas.

### 5.1 O que o ciclo `looks` ensinou

Da [retro do `looks`](/docs/tasks/concluidos/looks/retro.md), para o perfil
do ciclo novo — cada uma com as correções de lá que a provam:

- **K1 — Uma medição de uma entrada, um valor e um slot não é a regra.** Antes
  de escrever "a 147 faz X", ela foi andada nos dois slots e nos três valores
  de `FOOT`? Foi o grupo maior de engenharia do `looks`, 22 correções
  (CORR-LOOKS-010, 043, 044, 047, 048, 104, 105, 108, 109 entre elas).
- **K2 — O verificador nasce com o controle vermelho visto.** Toda asserção
  nova tem um defeito plantado em `controls.py` na mesma entrega, e o Log
  mostra o vermelho (CORR-LOOKS-009, 040, 046, 063, 068, 095).
- **K3 — Número em Log ou documento sai de comando versionado.** A contagem de
  quadros da 147 na §1.3 é o primeiro caso deste plano: sai de um trecho de
  Python solto, e a Fase 1 a põe numa ferramenta (CORR-LOOKS-022, 027, 092,
  097).
- **K4 — O Log cola a saída da HEAD entregue.** Os gates rodam depois da
  última edição, e a transcrição é colada daí, sem resumo dentro da cerca
  (CORR-LOOKS-032, 036, 041, 091, 093).
- **K5 — Fechar um veredito é varrer quem dizia o anterior.** Os termos do
  `rite sweep` incluem o número velho e o nome da incógnita, e a varredura olha
  docstrings e cabeçalhos de seção (CORR-LOOKS-024, 033, 057, 058, 085, 094,
  098).

## 6. Fases

| Fase | O que entrega | Depende de |
|---|---|---|
| 1 — medir | (a) a (f) respondidas nos dois slots, cada uma com comando versionado e controle; a contagem de quadros da 147 impressa por ferramenta; o veredito sobre o dispatch | — |
| 2 — reproduzir | o reprodutor da 147 exato passada a passada contra o que a Fase 1 gravou, sem emulador, com o controle deslocado caindo | 1 |
| 3 — a janela | o relógio trocando de animação em `FOOT` e voltando, no ritmo medido; `looks_ui` com controles plantados; silhueta e lugar na linha | 2 |
| 4 — fechamento | a §10.3 (p) do plano de origem com o veredito, perfil e `CLAUDE.md` reconciliados, `ctest -R looks` com os alvos listados pelo nome | 3 |

**O que não pode ser pulado:** a Fase 1 antes de qualquer código — um
reprodutor escrito para a regra da caminhada lê a 147 perfeitamente e desenha
outra coisa, que foi a lição da Fase 9 da v2. E a Fase 2 antes da 3: animar
num ritmo ou numa regra não medidos produz um chute bonito e errado.
