---
id: LOOKS-TASK-28
title: "A câmera do jogo — projeção medida, e a silhueta como testemunha de forma"
type: implementação
category: oráculo
phase: 9
depends_on: ["LOOKS-TASK-27"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (m)"
status: pendente
---

# LOOKS-TASK-28: A câmera do jogo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (m), §10.4 (3) e §6 (h).
- **Sem a câmera do jogo, comparar desenho mede a câmera.**
- **Esta task fecha a §6 (h).** Figura montada na pose do jogo e mesma
  projeção: a silhueta passa a ser comparável, e forma ganha testemunha.
- **A [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) deixou uma
  armadilha que alcança toda leitura de registrador numa parada:** o ponteiro
  de modelo que o jogo carrega quando a matriz é carregada nomeia a peça que
  ele **acabou de desenhar**, uma parada atrás (`oracle.DRAW_LAG`). Quem
  acrescentar uma captura por breakpoint confere o atraso com
  `oracle.py --pose-lag` em vez de supor que o registrador fala da peça da vez.
- **O controle já existe:** a captura do emulador se repete em zero pixel a
  partir do `load_state` (§5.3). O limiar sai do controle, escrito depois de
  medido e dito que foi.

---

## Objetivo

Medir a projeção e a câmera da tela `LOOKS SET`, aplicá-las no painel, e
comparar a silhueta do nosso quadro com a do emulador no mesmo quadro N.

---

## Critério de conclusão

- [x] `H`, o deslocamento de tela e a matriz de câmera lidos do GTE por
      breakpoint, com o comando que os lê — `oracle.py --camera`. **E o
      deslocamento de tela do GTE é ZERO**, que é achado: quem põe o boneco
      dentro do painel é o deslocamento de desenho da GPU.
- [ ] O painel desenha com eles, no tamanho do painel do jogo. **NÃO FEITO** —
      a silhueta se calcula no núcleo (`scene.silhouette`), no tamanho do
      painel, e a **janela** ainda desenha com a câmera orbital da v1.
- [x] `confront.py --silhouette [SLOT]`: máscara nos dois quadros e a
      diferença impressa.
- [x] **Controles antes do teste:** o mesmo quadro contado duas vezes dá **0**
      pixel de diferença, e quadros diferentes dão 603 a 1.680. Os limiares
      saem daí e estão escritos como medidos.
- [x] Um estilo trocado de propósito **discorda**: `A-I3` pontua 696 a 834
      onde o estilo que o state veste pontua 179 a 426 — 1,8x a 3,9x pior, nos
      dois slots. *(Os **três** estilos andados no próprio jogo ficam de fora:
      o controle troca o nosso lado, não o do emulador.)*
- [x] §6 (h) e §10.3 (m) com o veredito e a data — a (h) **fecha**: a forma tem
      testemunha. A (m) fica **parcial**, pela janela.

---

## Log de Execução

**Executado em:** 2026-09-18 — **PARCIAL**

**O que ficou medido**

**A câmera da tela, do GTE, com três controles.** `oracle.py --camera` para na
carga da matriz por peça — dentro do desenho da própria figura, e não em
qualquer ponto do quadro — e lê os registradores de controle do GTE:

- **`H` = 1376 px**, a distância focal com que o `RTPS` projeta;
- **`OFX` = `OFY` = 0,00**, e isso é o achado do dia: o ponto principal do GTE
  é a origem, então **o painel não é posicionado pelo GTE**. Quem o posiciona é
  o deslocamento de desenho da GPU, e o critério que dizia "o deslocamento de
  tela lido do GTE" recebe, medido, a resposta *é zero*;
- a matriz da câmera `[3195, 0, 635, -27, 2488, 133, -635, -268, 3195]` com
  translação `[-480, 192, 4125]` — **a mesma nos dois slots**.

Os três controles, nesta ordem: o mesmo quadro capturado **duas vezes** dá
números idênticos; as **doze** cargas de uma passada carregam a mesma projeção,
que é o que autoriza falar de "a" projeção do painel; e o quadro contado 140
projeta com os mesmos três, o que diz que a projeção é montagem de tela e não
animação.

**E a projeção está certa na largura.** Projetada com esses números, a nossa
figura mede **50,5 px** de largura contra **50** da figura do jogo no painel —
1% de diferença, sobre uma medida que nenhuma constante nossa escolheu.

**A silhueta, com os dois controles verdes.** `confront.py --silhouette` tira a
máscara do painel do **quadro nativo** (512x240, do `dump_vram`), pelo fundo de
cada **linha** — o painel é um degradê de 339 cores, e um fundo único para a
caixa inteira não separa nada. Os controles fecham antes de qualquer
comparação: o mesmo quadro contado duas vezes dá **0** pixel de diferença sobre
2.532 de tinta, e o quadro contado 80 difere do 20 em **1.300**.

**O que NÃO fecha, e é o bloqueio**

**A ponte entre o quadro contado do emulador e o quadro do `ANIME.BIN` que a
foto mostra.** O `anime.frame_of_pair` já diz qual quadro do arquivo o par que
o jogo estava lendo pertence, e a captura da foto e a captura do par são
corridas separadas — a foto custa alguns `frame_step` a mais, e a animação anda
no meio. Varrendo o **ciclo inteiro** (17 quadros, com a volta):

```text
frame 20: o par nomeia o quadro 13; melhor casamento no 7, 1.156 px de 2.532
frame 80: o par nomeia o quadro  6; melhor casamento no 5,   411 px de 2.454
```

O mínimo do quadro 80 é nítido e cai **um quadro antes** do que o par nomeia —
o que uma tela que mostra o buffer anterior explicaria. O do quadro 20 é raso
(1.156 contra 1.173 do vizinho) e cai seis quadros fora. Dois deslocamentos
diferentes não são uma ponte, e o comando **reprova** em vez de escolher o que
convém. Enquanto isso não fechar, comparar silhueta em três estilos mediria a
diferença de pose, não a de malha — que é justamente a §6 (h).

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/oracle.py` — `gte_projection()`, `capture_camera()`,
  `write_camera()`, `check_camera()` e a rota `--camera`
- `tools/looks/scene.py` — `load_camera()`, `to_camera()`, `project()`,
  `silhouette()`, `projected_box()`, `mask_box()`, `masks_differ()`
- `tools/looks/anime.py` — `frame_of_pair()`, a ponte entre o par lido e o
  quadro do arquivo
- `tools/looks/confront.py` — `panel_mask()`, `playing_frame()`,
  `game_silhouette()`, `our_silhouette()`, `fit_centre()`,
  `check_silhouette()` e a rota `--silhouette`
- `docs/tasks/looks/27-o-boneco-montado.md` — a contagem de controles
  corrigida de 86 para 87 (ver os problemas)
- `docs/prompts/perfil-looks.md`, `docs/PLAN-LOOKS-PY.md`,
  `docs/tasks/looks/28-a-camera-do-jogo.md`

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 87 of 87 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --camera
    H 1376 px, principal point (0.00, 0.00), the same at all 12 load(s)
oracle --camera: 0 problem(s) over 2 slot(s)

$ python tools/looks/oracle.py --pose-lag
oracle --pose-lag: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette 2
    control: frame 20 captured twice, 2532 pixel(s) of ink, identical
    control: frame(s) [80] differ from it by [1300] pixel(s)
confront --silhouette: 1 problem(s) over 1 slot(s)   <- o bloqueio acima

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**Problemas encontrados**

1. **A ponte de quadro não fecha** — o bloqueio, descrito acima e escrito no
   critério.
2. **Número de gate transcrito de uma corrida anterior à última edição.** O Log
   da [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) dizia
   `86 of 86` controles; rodando a ferramenta **sobre o commit** dá **87**. A
   corrida de onde o número saiu foi feita antes de o último controle entrar.
   Corrigido lá, e é armadilha de perfil agora.
3. **Janela de varredura que o resultado encosta não é janela.** A primeira
   corrida procurou o casamento a dois quadros de distância e achou o melhor
   **na borda**, nas duas comparações e em direções opostas — o que não diz
   onde está o mínimo. Alargada para o ciclo inteiro, com a volta, os mínimos
   ficam no interior e a resposta passa a ser legível.
4. **Máscara por cor única não separa figura de painel.** O fundo do painel é
   um degradê; o fundo tomado por **linha** entrega a silhueta limpa, e a borda
   do painel precisa de três pixels de recuo ou a caixa da figura vira o painel
   inteiro.

---

### Segunda sessão — a silhueta fecha

**A ponte de quadro era um bug de recorte, não um mistério.** O segundo buffer
de quadro desta tela começa na linha **240** da VRAM, não na 256; lido com 256,
o conteúdo chega **dezesseis linhas deslocado** e a caixa de ajuda entra no
retângulo do painel — a máscara então conta o branco de `Visual` como figura,
2.618 pixels de tinta contra 2.376, e nenhum quadro da caminhada casa. Duas das
seis comparações estavam assim, e a assinatura é sempre a mesma: **tinta acima
do normal e varredura chata**.

**E a comparação tinha de ser livre de translação.** A primeira versão media
uma translação única e a mantinha fixa — o que soa mais rigoroso e é pior:
ajustada numa pose e aplicada à foto de outra, ela desloca a figura inteira e
**todo** candidato pontua mal (medido: o melhor casamento foi de 13% da tinta
para 72%). Alinhada por comparação, a medida passa a julgar **forma e
tamanho**, que é o que a §6 (h) pede; onde a figura cai dentro do painel é o
deslocamento de desenho da GPU, e isto não o mede.

**O resultado, nos dois slots e em três quadros contados cada:**

```text
slot 2   quadro 60  -> caminhada 0,  0 atrás, 399 de 2383 (17%)
         quadro 80  -> caminhada 6,  2 atrás, 300 de 2454 (12%)
         quadro 100 -> caminhada 14, 1 atrás, 198 de 2532 ( 8%)
slot 1   quadro 60  -> caminhada 0,  0 atrás, 426 de 2376 (18%)
         quadro 80  -> caminhada 7,  2 atrás, 331 de 2460 (13%)
         quadro 100 -> caminhada 16, 2 atrás, 179 de 2426 ( 7%)
```

Cada varredura tem **mínimo interior e nítido**, e o quadro que o par do
próprio jogo nomeia está sempre **0 a 2 quadros à frente** do que a foto
mostra — que é o buffer anterior, com um quadro da caminhada durando ~3,5
quadros do emulador. O atraso é um **limite**, não uma constante, e exigir uma
constante foi o que fez a primeira leitura parecer ausência de ponte.

**A §6 (h) fecha: a forma tem testemunha.** O controle é um estilo de cabelo
que o state não veste — `A-I3` pontua **696 a 834** onde o certo pontua 179 a
426. E o que dá direito de chamar isso de testemunha de **forma** é o par que
não mexe: trocar a **cor de pele** (`B-A1` contra `A-A1`) muda **0** pixel da
silhueta, porque pele é paleta e não geometria.

**Por que a tomada começa no quadro 60:** antes disso a tela ainda assenta. No
quadro contado 20 o painel traz 2.726 pixels de tinta contra os 2.376 a 2.532
de todos os outros, e **nenhum** quadro da caminhada casa melhor que 3.570 —
pior que a própria tinta.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/confront.py` — `BUFFERS`, `still_frame()`, `game_at()`,
  `swapped_style()`, os limiares medidos (`WALK_LAG`, `MATCH_SHARE`,
  `MATCH_MARGIN`, `STYLE_MARGIN`) e as asserções do `check_silhouette`
- `docs/PLAN-LOOKS-PY.md` — o veredito da §10.3 (m) e o fechamento da §6 (h)
- `docs/prompts/perfil-looks.md` — as armadilhas novas
- `docs/tasks/looks/28-a-camera-do-jogo.md` — este Log

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 87 of 87 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/confront.py --silhouette
    control: frame 60 captured twice, 2383 pixel(s) of ink, identical
    control: frame(s) [80, 100] differ from it by [603, 1483] pixel(s)
    (slot 1) control: frame(s) [80, 100] differ from it by [670, 1452]
  the picture trails the draw by [0, 1, 2] frame(s) of the walk over 6
  comparison(s), and the bound is 2
confront --silhouette: 0 problem(s) over 2 slot(s)

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**O que continua aberto**

1. **A janela não desenha com a câmera do jogo.** A silhueta vive no núcleo; o
   painel da tela ainda usa a órbita da v1. É o critério 2, e é o que falta
   para a task fechar.
2. **Os três estilos não foram andados no jogo.** O controle troca o **nosso**
   lado sobre a mesma foto, que é o que prova que a silhueta vê a malha; andar
   o `HAIR` no emulador e refotografar é o resto.

**Problemas encontrados**

1. **Buffer de quadro lido na linha errada desloca a foto sem parecer erro.**
   240 e não 256 — e o sintoma é uma máscara com tinta demais que não casa com
   nada, não uma imagem visivelmente torta.
2. **Translação única mantida fixa é pior que alinhamento por comparação.**
   Ela parece mais rigorosa e mede outra coisa: 13% viraram 72%.
3. **Limite não é constante.** Exigir um deslocamento único entre o quadro que
   o par nomeia e o que a foto mostra produziu quatro respostas diferentes e a
   leitura "não há ponte"; o que há é um atraso com teto, e o teto se mede.
4. **Janela de varredura que o resultado encosta não é janela** — a de dois
   quadros devolveu o melhor na borda nas duas direções.
