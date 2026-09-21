---
id: LOOKS-TASK-31
title: "Incógnita (o) — o painel e o cenário da tela: do disco ou da GPU"
type: implementação
category: render
phase: 10
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-28"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (o)"
status: pendente
---

# LOOKS-TASK-31: O painel e o cenário

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1 e §10.3 (o).
- **A [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) desenha a tela com o arranjo medido, e o cenário por aproximação.**
  O degradê do painel, a borda, a barra de título, as faixas das linhas e a
  fonte podem ser imagem do `DAT2D.BIN` ou do `EDT_2D.BIN`, ou polígonos da
  GPU — e isso decide se a janela lê ou desenha.
- **A display list já é legível** (`oracle.walk_packets`, §6 (a)).
- **O que a [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) deixou
  para cá, olhando a dupla de capturas que ela pôs no Log** — a janela ao lado
  do quadro do emulador, com os mesmos doze textos:
  - **as duas setas `◀ ▶` ao lado do valor da linha selecionada.** O jogo as
    desenha coladas na caixa do cursor e elas **somem na ponta do alcance** —
    é o que a armadilha 28 do perfil já media pelo outro lado, contando valor
    pela célula. A janela não as desenha, porque o `screen.json` guarda a
    caixa do cursor e não elas. Medir de onde saem (objeto de texto, glifo ou
    polígono) responde de quebra se a seta que some é a testemunha barata de
    "esta ponta travou";
  - **o valor é alinhado à DIREITA dentro da caixa do cursor** no jogo, e a
    janela o escreve a partir da esquerda dela. A caixa está medida; a posição
    do texto dentro dela, não;
  - **a placa (`GK`/`CB`) e o nome da camisa têm caixa própria**, com uma
    barra vazia ao lado da camisa e um ícone à esquerda dela;
  - as cores, o degradê e a fonte, que é o objeto desta task.

- **O painel aproxima a câmera na CABEÇA quando a linha sob o cursor é de
  cabeça** — medido pela [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md)
  em 2026-09-18: com o cursor em `HAIR` a foto é um close-up, com `Kind of Hair`
  na caixa de ajuda e o dobro da tinta da figura inteira. A janela não faz isso:
  ela desenha sempre a câmera de corpo inteiro que o `oracle.py --camera` mediu
  com o cursor em `NAT`. Medir a câmera do close-up e trocá-la por linha é
  desta task, junto com o resto do painel.

---

## Objetivo

Dizer de onde vem cada elemento do cenário da tela `LOOKS SET` e reproduzi-lo
na janela, lido do disco quando for do disco.

---

## Critério de conclusão

- [ ] A fonte de cada elemento — painel, borda, barra de título, faixas,
      caixa de ajuda, fonte dos textos — medida pela display list: pacote e
      cores, ou registro de imagem e página.
- [ ] A janela os desenha; o que é imagem sai do disco japonês pela guarda.
- [ ] Com a câmera da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), o nosso quadro e o do emulador comparados **fora
      da silhueta**, com o controle do emulador contra ele mesmo.
- [ ] §10.3 (o) com o veredito e a data.

---

## Log de Execução

**PARCIAL — a task continua `⬜ Pendente`.** Três dos elementos estão medidos e
desenhados; o título, a placa, a camisa, as setas e os textos não, e o motivo
é um achado, não falta de tentativa.

- **Executado em:** 2026-09-20
- **Resumo do que foi feito:** a mobília da tela se lê na **display list**, e o
  que separa a lista viva das sobras é o quadro: as bandas guardam também a
  lista da tela anterior (as faixas dela ficam a 9 pixels, as desta a 12), e
  geometria plausível não prova que o pacote foi desenhado. O `oracle.py
  --scenery` fica só com os pacotes cuja cor é a que o console mostrou dentro
  do retângulo deles — sobram **28**, iguais nas duas leituras: o painel do
  boneco e a caixa de ajuda são **quads gouraud** (degradês medidos), e as
  doze faixas das linhas são **26 quads chatos** em duas cores alternadas, com
  a primeira linha em preto. **Nenhum é imagem.** Os texturizados que a
  varredura acha são o boneco, e confirmam a LOOKS-TASK-30 de graça: cabeça da
  página (512,256) do `DAT2D.BIN`, corpo da (576,256), que é do kit.
- **Arquivos criados/modificados:** `tools/looks/oracle.py` (`--scenery` e
  `--repaint`, com os decodificadores de pacote, sprite e página);
  `tools/looks/layout.py` (`SCENERY_SWEEP`); `tools/looks/scene.py`
  (`load_scenery`, `NoScenery`); `tools/looks/ui/looks_set.py` (pinta a
  mobília medida, e o painel manda a cor no viewer);
  `tools/looks/ui/viewer.py` (`clear_colour`); `docs/PLAN-LOOKS-PY.md`
  (§10.3 (o) com o veredito parcial e a data);
  `docs/prompts/perfil-looks.md` (armadilhas 80 a 82 e duas linhas de gate);
  `CLAUDE.md` (as duas linhas de comando).
- **Problemas encontrados:**
  1. **Seguir a cadeia de nós na RAM dá a tela errada.** Uma cadeia de 74
     pacotes bem formados é de outra tela, ainda na banda. Quem desempata é o
     quadro (armadilha 80).
  2. **O texto não está em lista nenhuma.** Varri a RAM inteira com quads,
     triângulos e sprites: nada cai fora do painel. E não é que seja pintado
     uma vez — o `--repaint` sobrescreve os dois buffers e **a tela inteira
     volta**, então o caminho de impressão (`layout.SCREEN_PRINT`) manda os
     comandos sem deixar nó em memória (armadilha 81).
  3. **O `gpu_dump` do fork sai em `.zst`**, e esta máquina não tem
     descompressor de zstd — nem módulo nem CLI (armadilha 82). Era a fonte
     exata dos comandos do quadro, e está fechada aqui.
  4. **A regra 1 pegou os opcodes e a faixa de varredura.** Os códigos de
     comando viraram tabela de strings, como o `_PACKETS` já fazia, e o
     endereço foi para o `layout.py`.

### Segunda passada, 2026-09-21

- **A fonte dos textos está medida, e é imagem do disco.** Parando na passada
  que DESENHA do `layout.SCREEN_GLYPH` e lendo o estado do próprio GPU, a
  página em vigor é **VRAM (704, 0), 4 bits com CLUT**, e o `DAT2D.BIN` tem um
  registro nela. Quando a lista não traz o desenho, quem responde é o hardware.
- **Nada da tela é cópia de VRAM.** O mapa de procedência do `--scenery`
  procura cada ladrilho no resto da VRAM e não acha nenhum — nem o texto, que
  é desenhado por CLUT e por isso não casaria de qualquer forma; uma cópia
  casaria.
- **O `--pages` (novo) atribui a tela às páginas, estragando uma por vez:** as
  do boneco (512,256) e do kit (576,256) derrubam 17 ladrilhos do painel cada,
  três páginas vizinhas não derrubam nada — o controle que a lista carrega — e
  a da fonte derruba **um** ladrilho só, o que diz que ela é reenviada a cada
  quadro.
- **Arquivos desta passada:** `tools/looks/oracle.py` (`--pages`, a página da
  fonte lida no `SCREEN_GLYPH`, o mapa de procedência);
  `docs/PLAN-LOOKS-PY.md`, `docs/prompts/perfil-looks.md` (armadilhas 83 e 84)
  e `CLAUDE.md` (a linha do `--pages`).
- **Problema encontrado:** a primeira versão do `--pages` comparava o quadro
  antes e depois do dano e acusava **48 ladrilhos para toda página**, inclusive
  as que nada amostra: o boneco anda entre as duas capturas. O controle certo
  são duas corridas do mesmo comprimento a partir do state (armadilha 83).

### Terceira passada, 2026-09-21

- **A comparação fora da silhueta existe, e passa** (`confront.py --outside`,
  novo): o chão de cada região no quadro do jogo e na janela em escala nativa,
  com o jogo fotografado duas vezes de controle. **Painel a 4, ajuda a 3,
  faixas a 11**, nos dois slots. É o critério 3, para as regiões medidas.
- **Duas coisas a métrica ensinou.** "A cor mais comum" de um degradê é
  decidida por empate e pelo pontilhado do console — a ajuda saiu (8,64,96) no
  jogo e (0,40,64) aqui, com os dois degradês iguais —, e a mediana de cada
  canal resolve (armadilha 85). E o painel ficava **24** longe porque o viewer
  OpenGL limpava com uma cor só: agora ele pinta o degradê medido por
  `QPainter` por trás do boneco.
- **O `looks_ui` julga a mobília** contra a tabela medida, sem emulador: os 28
  pacotes amostrados dentro do canto, todos a menos de 16, e o controle
  plantado (a janela que não pinta o medido) fica vermelho.
- **O alinhamento está medido, e não aplicado.** O objeto de texto dos valores
  que o `SCREEN_PRINT` recebe é uma caixa de largura 296 a partir de x 176 —
  borda direita em **472** —, e os valores desenhados pelo `SCREEN_GLYPH`
  terminam contra ela (`23` começa em 448, `TYPE` em 425, `Unknown` em 392).
  Levar isso à janela pede o `screen.json` com as caixas dos objetos, que é
  mudar o gerador e rodar o `--screen --write` e o `--screen` de novo.
- **Problema encontrado:** o degradê do painel quebrou o juiz de estatura do
  `looks_ui`. O `panel_ink` tomava uma cor só como fundo do painel inteiro, e
  num degradê isso faz de toda linha "tinta" — as quatro razões deram 1,000.
  O fundo passou a ser tomado **por linha**, e os números voltaram aos de
  antes (100×187, 88×165, 122×222, 123×188).
- **Arquivos desta passada:** `tools/looks/confront.py` (`--outside`,
  `ground_colour`); `tools/looks/ui/looks_set.py` (degradê pelo canto de cima
  de fato, e o painel manda o degradê ao viewer); `tools/looks/ui/viewer.py`
  (`clear_gradient`, pintado por `QPainter` com o boneco por cima);
  `tools/looks/ui_check.py` (`measure_scenery`, `plant_scenery`,
  `SCENERY_BREAKS`, e o `panel_ink` com fundo por linha); `docs/PLAN-LOOKS-PY.md`,
  `docs/prompts/perfil-looks.md` (armadilha 85, duas linhas de gate e a do
  `looks_ui`) e `CLAUDE.md`.

### O que falta para fechar esta task

- **A barra de título, a borda, a placa (`GK`/`CB`), a caixa da camisa e as
  setas `◀ ▶`.** Não são pacote na RAM, não são cópia de VRAM e não somem
  quando as páginas conhecidas são estragadas. O que resta é ler o que o
  caminho de impressão manda ao GPU comando a comando — parar em
  `layout.SCREEN_PRINT` e seguir o que ele escreve.
- **A fonte desenhada do disco.** Ela está medida (página (704,0) do
  `DAT2D.BIN`), mas a janela ainda escreve com uma fonte do Qt; o critério 2
  pede o que é imagem lido do disco pela guarda.
- **O alinhamento à direita**, medido acima e não aplicado.
- **A câmera do close-up por linha**, que o contexto desta task traz da
  LOOKS-TASK-22: a janela desenha sempre a câmera de corpo inteiro.

**Gates, na árvore commitada:** `selftest` 0 falhas, 90 de 90 controles
vermelhos; `cli check` 10 de 10; `oracle.py --scenery` 0 problemas (28
pacotes, iguais nas duas leituras); `oracle.py --repaint` 0 problemas;
`oracle.py --pages` 0 problemas, com as duas corridas sem dano idênticas;
`confront.py --outside` 0 problemas nos dois slots; `looks_ui` 11 de 11
controles vermelhos;
`check_tasks` 138 ok.
