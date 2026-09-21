---
id: LOOKS-TASK-36
title: "Os sprites estáticos da tela — placa, caixas, ícone, barra, título e setas, lidos do disco"
type: implementação
category: render
phase: 10
depends_on: [LOOKS-TASK-31]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: 2026-09-21
review_commit: 3fba5391
done_on: 2026-09-21
done_commit: 2b698730
---

# LOOKS-TASK-36: Os sprites estáticos da tela

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o), a tabela dos sprites da quinta passada.
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário. A 31
  mediu de onde vem cada sprite da tela; esta os desenha.
- **O que já está medido:** o `oracle.py --scenery` anda a lista do quadro,
  parte cada nó em comandos e deixa os sprites em `work/looks-scenery/slotN.json`
  (ponto, tamanho, `uv`, CLUT, página, cor, blend). Os texels de cada grupo
  saem do `EDT_2D.BIN` ou do `DAT2D.BIN` e batem com a VRAM; as oito CLUTs
  saem do `DAT2D.BIN`.
- **Os estáticos:** o título `S SET`, o ícone à esquerda da camisa, as caixas
  verdes da camisa, a barra vazia ao lado da placa e a placa `CB`/`GK` — cuja
  **CLUT muda com a posição** ((208,499) no jogador de linha, (192,499) no
  goleiro), o que diz que a janela precisa saber a posição do jogador, não só
  copiar o quadro de um slot.
- **As setas `◀ ▶` não são estáticas:** seguem o cursor e somem na ponta do
  alcance (armadilha 28 do perfil). A `▶` está medida (página (704,0), CLUT
  (80,497), `DAT2D.BIN`); a `◀` não apareceu no quadro medido, com o cursor
  em `NAT`. Medir quando cada uma aparece é desta task.
- **O texto não é desta task** — é a [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md). A ajuda também
  não — é a [`LOOKS-TASK-39`](/docs/tasks/looks/39-o-texto-da-ajuda.md).

---

## Objetivo

A janela desenha os sprites estáticos da tela e as setas com texels e paletas
lidos do disco japonês pela guarda, no lugar e na ordem em que o jogo os
desenha.

---

## Critério de conclusão

- [x] Um núcleo que monta a imagem de um sprite a partir do disco (texels
      LZSS, página, CLUT, cor e blend), com self-check e controle plantado —
      o texel 0 transparente e a modulação pela cor do sprite inclusos.
- [x] A janela desenha título, ícone, caixas, barra e placa; a CLUT da placa
      vem da posição do jogador, conferida nos dois slots.
- [x] As setas: quando cada uma aparece medido no jogo, e a janela as
      desenha igual ao longo de `oracle.py --keys`, com o controle fechando
      antes.
- [x] O `looks_ui` amostra os sprites contra a tabela medida, com um controle
      plantado vermelho.
- [x] `confront.py --outside` ganha as regiões desses sprites, com o jogo
      fotografado duas vezes de controle.

---

## Log de Execução

**Executado em:** 2026-09-21

### O que foi feito

- **`tools/looks/sprites.py` (novo):** a VRAM do `EDT_2D.BIN` e do `DAT2D.BIN`
  montada do disco pela guarda, a CLUT pelo `texture.window_for`, e o sprite
  cortado como o GPU corta: quatro texels por halfword; a entrada `0x0000`
  transparente (quem decide é a entrada, não o índice 0); a cor do sprite
  modulando cada canal, com 128 valendo um e saturação em 255; e `raw` sem
  modulação. Sprite semitransparente é recusado. `static()` escolhe os cinco
  grupos de `layout.SCREEN_SPRITES` e troca a CLUT da placa pela da
  **posição** (`layout.PLATE_CLUT`), recusando posição sem medida.
  Self-check com casos verdes e vermelhos; três controles plantados em
  `controls.py`.
- **`layout.py`:** `SCREEN_SPRITES`, `PLATE_CLUT`, `ARROW_PAGE`.
- **Janela:** os estáticos são pintados sobre a imagem da mobília, que é a
  ordem da lista (medida abaixo). O título do Qt some quando existe o título
  sprite, as setas são desenhadas do disco onde o `State` diz, e o relatório
  imprime `sprites` e `arrows`. `--no-stand-in-text` omite o texto provisório
  da placa e da camisa (armadilha 93).
- **`oracle.py`:**
  - `frame_commands`/`frame_arrows` leem os sprites do quadro pela lista
    (0,34 s para a RAM inteira);
  - o walk do `--screen` grava as setas de cada linha (na chegada, nas
    pontas e entre elas) e recusa se as de entre variarem;
  - o `--scenery --write` grava amostras de pixel de cada estático, tiradas
    do frame buffer do jogo;
  - o `--keys` compara as setas nas três frentes.
- **`screen.py`:** `State.arrows()`, validação das setas, casos no toy.
- **`ui_check.py`:** `measure_sprites` nos dois slots, com dois defeitos
  plantados.
- **`confront.py`:** regiões `title`, `icon`, `shirt boxes` e `plate`, com as
  caixas tiradas da tabela medida (`sprite_regions`).

### Evidência

A ordem de desenho, lida com `oracle.commands_of` sobre a lista do slot 2:
a barra de título aditiva é o comando 301, a placa é o 307 e o título é o 384.
Toda mobília que fica sob os estáticos vem antes deles.

A barra é transparente (`sprites.Art.image` do sprite 16 da tabela):
`16 bar [96, 12] opaque 0 of 1152 {(0, 0, 0, 0)}`.

```text
$ python tools/looks/sprites.py --check-image
  title        page (768, 256) clut (128, 498): 16 entries, 16384 halfword(s) of the page held
  icon         page (768, 256) clut (80, 499): 16 entries, 16384 halfword(s) of the page held
  shirt boxes  page (576, 0) clut (176, 496): 16 entries, 16384 halfword(s) of the page held
  bar          page (960, 256) clut (0, 497): 16 entries, 16384 halfword(s) of the page held
  plate        page (576, 0) clut (192, 499): 16 entries, 16384 halfword(s) of the page held
  plate        page (576, 0) clut (208, 499): 16 entries, 16384 halfword(s) of the page held
  arrow left  uv (128, 240): 22 of 64 texels opaque
  arrow right uv (128, 248): 22 of 64 texels opaque
  the left arrow is the right one mirrored
sprites --check-image: 0 problem(s)

$ python tools/looks/controls.py --only <cada um dos três>
  RED    sprites-transparent-drawn  sprites.py :: paint
  RED    sprites-colour-ignored     sprites.py :: image
  RED    sprites-plate-from-the-state sprites.py :: static

$ python tools/looks/oracle.py --scenery --write
    control: the screen loaded twice draws the same 43 packet(s) and the same 142 sprite(s)
    the static sprites sampled: 359 pixel(s) of 14 sprite(s), each the colour the game's frame shows there
oracle --scenery: 0 problem(s) over 2 slot(s)

$ python tools/looks/oracle.py --screen --write        # 14 min 22 s
            arrows: on arrival <(384,43), at the left end >(276,43), between -, at the right end <(384,43)
  DEFAUL      1 value(s), Left locks, Right locks; ...
            arrows: on arrival >(480,55), at the left end >(480,55), between <(302,55) >(480,55), at the right end <(302,55)
  NAT        80 value(s), ...
            arrows: on arrival <(424,151) >(480,151), at the left end >(480,151), between <(424,151) >(480,151), at the right end <(424,151)
  AGE        32 value(s), ...
            arrows: on arrival >(480,175), at the left end >(480,175), between <(416,175) >(480,175), at the right end <(416,175)
  FOOT        3 value(s), ...
oracle --screen --write: wrote tools/looks/screen.json
```

Nas outras oito linhas (SKIN, HAIR, H.COL, FACE, H.F.COL., HEIG, BODY e BOOTS)
o ◀ fica em x 384. O HEIG chega no meio da faixa,
com `<(384,127) >(480,127)`. O `screen.json` regravado só **acrescenta**
(`git diff --stat`: 539 inserções, 0 remoções); nada do que já estava medido
mudou.

```text
$ python tools/looks/oracle.py --keys "<a sequência padrão, 19 teclas>" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help and the same arrows
    arrows    <(384,127) >(480,127)
oracle --keys: 0 difference(s) after 19 press(es), across the game, screen.json and our window
  (slot 1: o mesmo, 0 difference(s))

$ python tools/looks/oracle.py --keys "Down,Right,Right,Right,Right" 2      # a ponta direita
    arrows    <(384,67)
oracle --keys: 0 difference(s) after 5 press(es), across the game, screen.json and our window

$ python tools/looks/oracle.py --keys "Up,Left" 2                             # vermelho: CORR-LOOKS-067
  FAIL  the arrows: the game draws >(276,43) and screen.json says <(384,43)
  FAIL  the arrows: the game draws >(276,43) and our window draws <(384,43)
oracle --keys: 4 difference(s) after 2 press(es), across the game, screen.json and our window

$ python tools/looks/ui_check.py                                               # 3 min 17 s
  the static sprites the window paints are the game's: 718 pixel(s) sampled over slots 2, 1, every one within 8
negative: breaking the static sprites reaching the window reddens the sprites -- slot 2: 359 of 359 sprite pixel(s) are not the game's; ...
negative: breaking the plate's CLUT read from the position reddens the sprites -- slot 1: 91 of 359 sprite pixel(s) are not the game's; the first at (40,52) is (115, 132, 41) in the game and (82, 115, 115) in the window, 74 apart
looks_ui: 14 of 14 negative control(s) red, ...

$ python tools/looks/confront.py --outside
  -- slot 2 --
    control: the game photographed twice, the same ground in all 11 region(s)
    icon         game (90, 82, 165)   ours (90, 82, 165)     0 apart
    plate        game (49, 82, 90)    ours (49, 82, 90)      0 apart
    shirt boxes  game (33, 66, 57)    ours (33, 74, 57)      8 apart
    title        game (8, 99, 90)     ours (8, 98, 91)       1 apart
  -- slot 1 --
    control: the game photographed twice, the same ground in all 11 region(s)
    icon         game (90, 82, 165)   ours (90, 82, 165)     0 apart
    plate        game (90, 90, 33)    ours (90, 90, 33)      0 apart
    shirt boxes  game (33, 74, 49)    ours (33, 74, 49)      0 apart
    title        game (8, 99, 90)     ours (8, 98, 91)       1 apart
confront --outside: 0 problem(s) over 2 slot(s)
```

### Problemas encontrados

- **A primeira corrida do `looks_ui` ficou vermelha, e a causa não era dos
  sprites.** 16 e 18 das 359 amostras erravam só onde a fonte do Qt ("CB",
  "SHIRT N") cai sobre texels que o jogo deixa à mostra; nesses mesmos pixels
  o decode batia com o jogo ((82,115,115) nos dois em (16,57)). O julgamento
  passou a fotografar a janela com `--no-stand-in-text` (armadilha 93), e a
  nota foi para a
  [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md).
- **O `DEFAUL` tem uma segunda posição**, que o `screen.json` registra como
  trava. Abri a [`CORR-LOOKS-067`](/docs/tasks/looks/CORR-LOOKS-067.md).
  Enquanto ela estiver aberta, as setas do `DEFAUL` na janela ficam certas até
  o `Left` e erradas depois dele.
- **O pulso das setas não é reproduzido:** a janela as desenha a 128. O ritmo é
  da fase 11.
- **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado**
  (seriam mais 14 min). O gerador fechou com 0 problema no `screen.validate`,
  e o `--keys` nos dois slots e nas pontas confere o arquivo contra o jogo.

### Gates

```text
# na arvore de 2b698730
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 26 file(s), 27982 line(s)
  ..... 97 of 97 controls red
looks_selftest: 0 failure(s)
$ python tools/looks/cli.py check
cli check: 11 module(s), 11 ok, 0 skipped, 0 failed -- ok
$ python tools/check_tasks.py
check: 0 error(s), 11 warning(s) in 4 cycle(s)
```

Os outros três alvos do ciclo — `looks_ui` (14 de 14 controles vermelhos),
`looks_live` (`oracle --check-live: 0 failure(s)`) e `--keys`/`--outside` —
rodaram sobre o código do commit, antes das últimas edições de texto dele
(prosa do perfil, do `CLAUDE.md` e uma string do `controls.py`). Estão
transcritos acima.
- **Closed** — commit `2b698730` (2026-09-21): feat(looks): draw the static sprites and the arrows off the disc
  - Files (`git show --name-status 2b698730`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `A docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/36-os-sprites-estaticos.md`
    - `M docs/tasks/looks/37-a-tabela-de-glifos.md`
    - `M docs/tasks/looks/38-o-alinhamento-dos-valores.md`
    - `M tools/looks/cli.py`
    - `M tools/looks/confront.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/layout.py`
    - `M tools/looks/oracle.py`
    - `M tools/looks/scene.py`
    - `M tools/looks/screen.json`
    - `M tools/looks/screen.py`
    - `M tools/looks/selftest.py`
    - `A tools/looks/sprites.py`
    - `M tools/looks/ui/app.py`
    - `M tools/looks/ui/looks_set.py`
    - `M tools/looks/ui_check.py`
- **Reviewed** (2026-09-21) at `3fba5391`: CORR-LOOKS-068, CORR-LOOKS-069
