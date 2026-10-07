# Ajustes da aba 3D do `kits`

O ciclo `kits` está arquivado em
[docs/tasks/concluidos/kits/](/docs/tasks/concluidos/kits/progresso.md). No teste manual da aba
3D, o usuário achou cinco lacunas, que estão listadas aqui (2026-10-07). Este documento é a entrada
do ciclo seguinte. Não é plano: diz o que se pede, como a aba está hoje e o que ainda precisa ser
decidido ou medido.

Os caminhos são relativos a `tools/kits/`, e as linhas são as da HEAD em que este arquivo entrou. As
fontes de verdade do ciclo anterior são as seções do
[PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md):

- [§0](/docs/PLAN-KITS-PY.md#0), com os Não-objetivos;
- [§3.4](/docs/PLAN-KITS-PY.md#3.4), a interface;
- [§4.3](/docs/PLAN-KITS-PY.md#4.3), manga longa e braçadeira;
- [§4.7](/docs/PLAN-KITS-PY.md#4.7), as costas e o número.

## G1 — "Set" vira "Kit": Home/Away, Uniforme: Casa/Visitante

**Pedido.** O campo "Set" passa a se chamar **Kit**, com as opções **Home** e **Away**. Em pt-BR, o
campo é **Uniforme**, com **Casa** e **Visitante**. Quando o idioma troca, os tamanhos se ajustam
(ver G2).

**Hoje:**

- `set_box` em `ui/app.py:390-392`, com os dados 1 e 2.
- Os rótulos saem de `ui/i18n.py`:

  | Chave | en-US | pt-BR |
  |---|---|---|
  | `kit_set` | "Set" (`:72`) | "Conjunto" (`:132`) |
  | `set_first` | "first" (`:73`) | "titular" (`:133`) |
  | `set_second` | "second" (`:74`) | "suplente" (`:134`) |

- `retranslate` aplica os rótulos (`ui/app.py:490-491`).

**Decidido (usuário, 2026-10-07).** Não há o que medir. No futebol, o primeiro uniforme é o de casa
(mandante) e o segundo, o de visitante, e uma coisa não exclui a outra. O conjunto 1 é Home/Casa e
o 2 é Away/Visitante. Isto é convenção do domínio, não medição, e o texto deve dizer assim.

**Em aberto.** O CLI usa `--set 1|2` (`cli.py:1256`), e os documentos falam em "primeiro e segundo
conjunto". Falta decidir se a troca vale só para a interface ou também para o vocabulário de CLI e
docs.

## G2 — Combos do tamanho da opção mais longa

**Pedido.** Todo combo mostra inteira a opção de texto mais longo do idioma em uso, e volta a se
ajustar quando o idioma muda.

**Hoje:**

- `set_box`, `figure_box`, `language_box`, `palette_box` e `zoom_box` ficam na política padrão do
  Qt, que mede o combo uma vez só, quando ele aparece pela primeira vez.
- O `retranslate` (`ui/app.py:468`, chamado pelo `language_changed` em `:504`) só faz
  `setItemText`. Nada é medido de novo.
- O único combo com `AdjustToContents` é o `image_box` (`ui/app.py:325-331`). O comentário em
  `:326-327` já descreve exatamente esse defeito, que só foi corrigido ali.
- O `tag_box` usa `setMinimumContentsLength(18)`.

**A verificação deve prever:**

- uma captura nas duas línguas, com o rótulo mais longo de cada combo sem corte;
- uma planta que tira o ajuste e deixa o caso vermelho.

## G3 — Sem "match player": só "player" e "goalkeeper"

**Pedido.** O seletor de figura passa a ter só **player** e **goalkeeper**. A figura de partida
sai da interface. Do trabalho de "match player", só o **conhecimento medido** pode ser usado.

**Hoje:**

- O `figure_box` tem três itens (`ui/app.py:393-398`), e o terceiro é `MATCH_FIGURE = 2` (`:68`).
- Jogador e goleiro vêm do `EDT_MOD.BIN`, montados por `scene_of` (`core/figure.py:84-104`).
- A figura de partida é o `MODEL.BIN` inteiro, na pose `core/match_pose.json`, montado por
  `match_scene` (`core/figure.py:250-333`).
- Marcar Captain armband ou Long sleeves no jogador **troca** o desenho para a figura de partida
  (`match_drawn`, `ui/app.py:576-581`).

**Medido no ciclo anterior, e que pode ser aproveitado** (§4.3; KITS-TASK-43 a 47):

- seção 93: a braçadeira de manga longa, no lugar da 97;
- seção 90: a braçadeira de manga curta, no lugar da 4;
- seções 95-98: braços de manga longa do jogador de linha;
- seções 3, 5, 4 e 6: braços de manga curta do jogador de linha (`LONG_TO_SHORT`,
  `core/figure.py:188`);
- seções 99-102 e 57-60: braços do goleiro, longos e curtos (`SLEEVE_LENGTHS`,
  `core/figure.py:177-182`);
- a matriz de GTE de cada peça e a pose medida.

**Em aberto: é a decisão central do ciclo.** Como vestir a figura do `EDT_MOD.BIN` com geometria
medida do `MODEL.BIN` sem remapear UV à mão, o que o §0 proíbe. Há duas saídas:

- transplantar as seções do `MODEL.BIN` para a figura, com matriz medida;
- medir se o `EDT_MOD.BIN` tem peça equivalente.

As duas pedem medição antes de código.

## G4 — Number, Captain armband e Long sleeves em qualquer combinação, nas duas figuras

**Pedido.** As três caixas valem para **player** e **goalkeeper** e combinam livremente: nenhuma,
uma, duas ou as três ao mesmo tempo.

**Hoje** (`dressings()`, `ui/app.py:583-601`):

| Caixa | Jogador | Goleiro |
|---|---|---|
| Number | recusado quando a figura de partida é desenhada (`number_off`, `ui/i18n.py:84`): o painel do torso de partida não foi medido (§4.7) | funciona |
| Captain armband | funciona, trocando para a figura de partida | desligado, com `armband_off` (`ui/i18n.py:86`) |
| Long sleeves | funciona, trocando para a figura de partida | escondido (`ui/app.py:589`) |

Hoje só a braçadeira e a manga longa combinam entre si.

**Em aberto:**

- A braçadeira do goleiro não foi medida. `SLEEVE_LENGTHS` lista os braços do goleiro (99-102 e
  57-60), mas nenhuma braçadeira para ele.
- O pedido **reabre uma decisão** da KITS-TASK-40, a de esconder a manga longa no goleiro. A mudança
  precisa ser registrada como decisão nova, com data.
- O Number junto com a braçadeira ou a manga longa depende de G3: em qual torso o painel é
  montado.

**A verificação deve prever** as oito combinações nas duas figuras. Cada caixa tem de mudar a
captura, e cada uma precisa de uma planta que a ignore e fique vermelha.

## G5 — Figura inteira em qualquer giro

**Pedido.** Em qualquer posição de giro, o jogador aparece completo. Hoje as costas e outras partes
não aparecem.

**Hoje.** O que se sabe de por que falta pedaço:

- **Lacuna do torso.** O torso amostra (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro
  (`core/zones.py:194-196`). Essa área é transparente no TEX.
- **A cópia das costas é medida, mas condicional.** O jogo copia a "shirt back" para essa lacuna:
  (44,6) no jogador e (108,6) no goleiro (`BACK_COPY`, `core/figure.py:351`; medido na §4.7). Aqui
  a cópia só acontece **com Number marcado** (`api.numbered`, `ui/app.py:619-625`). Na figura de
  partida ela nunca acontece.
- **Texel transparente deixa ver o fundo.** As superfícies são desenhadas em RGBA
  (`ui/figure_view.py:64-65`), então o que é transparente mostra o que está atrás.
- **Ordem de desenho.** O `figure_view` não descarta faces. Ele ordena os triângulos pela
  profundidade média de cada um (`ui/figure_view.py:97-100`), o que pode inverter peças que se
  cruzam.
- **Triângulos perdidos.** Um triângulo com transformação degenerada é pulado sem aviso
  (`ui/figure_view.py:119-121`).
- **A dica da aba explica o vazado** (`ui/i18n.py:79-82`). Ela foi escrita sob a decisão de
  2026-10-05 (KITS-TASK-37) de desenhar fiel aos dados.

**Em aberto.** Aplicar sempre a cópia das costas é regra medida do jogo, não invenção. O resto
precisa de uma ferramenta que, por ângulo, conte o que falta na figura: texel transparente, ordem de
profundidade e triângulo pulado. Só depois disso se escolhe o conserto.

## Para o ciclo

**Ordem sugerida:**

1. G1 e G2: texto e layout, baratos e independentes.
2. G5: a cópia das costas passa a ser sempre aplicada, e o resto se mede por ângulo.
3. G3 e G4: dependem da decisão de geometria da G3.

**Decisões do ciclo anterior que este pedido reabre.** Cada uma precisa entrar no plano novo como
decisão nova, datada:

- a figura "match player" no seletor (KITS-TASK-47);
- a manga longa escondida no goleiro e a braçadeira desligada nele (KITS-TASK-40);
- as costas vazadas por fidelidade aos dados (usuário, 2026-10-05; KITS-TASK-37).

**O que não muda:**

- o §0: nada de geometria inventada nem de UV remapeado à mão;
- o desenho por `QPainter` em software;
- o catálogo i18n como fonte única de texto da interface.
