---
id: LOOKS-TASK-31
title: "Incógnita (o) — o painel e o cenário da tela: do disco ou da GPU"
type: implementação
category: render
phase: 10
depends_on: [LOOKS-TASK-22, LOOKS-TASK-28]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: 2026-09-21
review_commit: null
done_on: 2026-09-21
done_commit: "8164261"
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

- [x] A fonte de cada elemento — painel, borda, barra de título, faixas,
      caixa de ajuda, fonte dos textos — medida pela display list: pacote e
      cores, ou registro de imagem e página.
- [x] A janela desenha a **mobília** — degradês, blend, faixas e borda — como
      o GPU desenha. *Reescrito em 2026-09-21, a pedido do usuário:* o que
      é imagem — sprites, texto, alinhamento, ajuda — e a câmera do close-up
      saíram para as [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) a [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md).
      Dizia: "A janela os desenha; o que é imagem sai do disco japonês pela
      guarda."
- [x] Com a câmera da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), o nosso quadro e o do emulador comparados **fora
      da silhueta**, com o controle do emulador contra ele mesmo.
- [x] §10.3 (o) com o veredito e a data.

---

## Log de Execução

**Fechada em 2026-09-21, dividida.** A pedido do usuário, a task fecha com a
medição de cada elemento e a mobília desenhada, e o que faltava virou as
[`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) a [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md) — ver "Fechamento", no fim deste Log. As
passadas abaixo ficam como foram escritas; a primeira linha dizia "PARCIAL — a
task continua `⬜ Pendente`".

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
  *Nota da [`CORR-LOOKS-066`](/docs/tasks/looks/CORR-LOOKS-066.md): os 17 e 17
  são do slot 2; o slot 1 imprime **12** e **18**, e nos dois a ferramenta diz
  "over help, panel" — a ajuda entra junto com o painel.*
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

### Quarta passada, 2026-09-21

- **A lista que o quadro entrega ao GPU.** Um watchpoint de escrita no
  endereço do DMA do GPU para só em `sw a0, 0x0(v0)` — virou
  `layout.GPU_LIST_SUBMIT` —, e o `a0` é a cabeça: três por quadro. O
  `--scenery` agora anda essa lista em vez de varrer a RAM com filtro de cor:
  **43 pacotes**, os mesmos nas duas leituras e nos dois slots, em ordem de
  desenho, com o blend de cada semitransparente lido do comando de modo (ou
  da página de um texturizado) que vem antes dele.
- **A barra de título e a borda estavam na lista.** A barra são três degradês
  **aditivos** (blend 1) através da tela, e o filtro de cor os descartava
  porque o quadro mostra a mistura (armadilha 86). A borda são quatro
  polilinhas cinza, duas por lado. O fundo são oito degradês, e duas das 26
  faixas da primeira passada eram sobra: são 24.
- **A janela desenha como o GPU.** `scene.furniture_picture` (núcleo) põe cada
  quad em dois triângulos 0,1,2 e 1,2,3, sombreia entre os cantos e mistura
  pelo blend, uma vez; a janela pinta a imagem e o viewer recebe o recorte do
  painel, borda inclusive. Degradê por retângulo de cima para baixo não
  alcançava a barra, que corre da esquerda para a direita (armadilha 88).
  Quatro self-checks novos e dois controles plantados (a diagonal somada duas
  vezes, o quad partido errado).
- **`confront.py --outside` ganhou três regiões** que o `screen.json` não
  nomeia: **barra de título a 3, fundo a 3 e 3**; painel a 4, ajuda a 4 e
  faixas a **6** (eram 11), nos dois slots.
- **O `looks_ui` aprendeu a borda.** O juiz de estatura media a tinta do
  painel e passou a achar a borda em toda linha (razões 1,000): ele agora mede
  por dentro dela (`PANEL_BORDER`). O juiz da mobília pula pacote
  semitransparente, linha e pacote coberto por outro depois, e tem um controle
  novo — o viewer que não pinta o recorte fica vermelho.
- **A página da fonte não está resolvida.** A mesma pergunta ao GPU, em três
  corridas, deu (704,256) e (832,256) no slot 2 e ainda (704,0) no slot 1; o
  "(704,0)" da primeira passada foi uma corrida só (armadilha 87).
- **Arquivos desta passada:** `tools/looks/layout.py`
  (`GPU_LIST_SUBMIT`, `GPU_LIST_HEAD`); `tools/looks/oracle.py`
  (`gpu_list_heads`, `walk_gpu_list`, `furniture_of`, o `_scenery_of` novo, e
  saem `scenery_nodes`, `_corner_pixels`, `_colour_gap`); `tools/looks/scene.py`
  (`furniture_picture`, `BLENDS`); `tools/looks/controls.py`;
  `tools/looks/ui/looks_set.py`, `tools/looks/ui/viewer.py` (`clear_image`);
  `tools/looks/ui_check.py`; `tools/looks/confront.py`
  (`FURNITURE_REGIONS`); `docs/PLAN-LOOKS-PY.md`,
  `docs/prompts/perfil-looks.md` (armadilhas 86 a 88) e `CLAUDE.md`.

### Quinta passada, 2026-09-21

- **O texto, a placa, o título e as setas estavam na lista, como sprites.**
  A quarta passada escreveu que eles "saem por escrita direta no GPU", e as
  duas medidas desta desmentem: um watchpoint de escrita na porta de comando
  do GPU não dispara nenhuma vez com a tela de pé, e o código da rotina de
  glifo (`layout.SCREEN_GLYPH`) só preenche um `GsSPRITE` no scratchpad, que o
  chamador ordena no `GsOT` do quadro — o mesmo cuja cabeça vai ao DMA. O
  defeito era do leitor: a libgs põe o E1 da página e o sprite **no mesmo
  nó**, e o `--scenery` classificava o nó pela primeira palavra (armadilha
  89). Partido em comandos (`oracle.commands_of`), o quadro traz **142
  sprites**, iguais nas duas leituras e nos dois slots.
- **De onde vem cada um, medido do disco contra a VRAM.** O `--scenery`
  decodifica, pela guarda, os texels que cada grupo amostra e os compara com a
  VRAM da tela de pé; o controle, a mesma VRAM três linhas abaixo, diverge em
  1.502 de 2.128. A **fonte** (121 sprites, página (704,256)), o título, o
  ícone e a barra vazia saem do **`EDT_2D.BIN`**, todos os texels iguais; as
  caixas verdes, a placa e a seta, do `DAT2D.BIN`; as oito CLUTs, do
  `DAT2D.BIN`, 16 de 16. A placa troca de CLUT com a posição — (208,499) no
  jogador de linha, (192,499) no goleiro.
- **A ajuda não está no disco como imagem.** O `Visual` da caixa de baixo são
  seis ladrilhos 16×16 da página (832,256), e nenhuma imagem os cobre: o jogo
  os escreve na VRAM em tempo de execução (armadilha 90).
- **A página da fonte se resolve** (armadilha 87): os três valores que o
  estado do GPU deu eram três sprites diferentes — a fonte, a ajuda e a seta.
  A leitura por estado do GPU (`check_glyph_page`) saiu, substituída pela
  lista.
- **`EDT_2D.BIN` entrou na guarda**, com digest, LBA e tamanho: idêntico nos
  dois discos, família própria (`layout.SCREEN_ART_FILES`), e o
  `iso_source.py --check-discs` o aceita nos dois.
- **Arquivos desta passada:** `tools/looks/oracle.py` (`command_words`,
  `commands_of`, `sprites_of`, `sprite_texels`, `_say_sprites` e a
  comparação com o disco; o `furniture_of` anda comandos; saem
  `check_glyph_page`, `_say_glyph_page`, `_draw_page` e uma cópia morta das
  constantes de procedência; sete self-checks novos); `tools/looks/layout.py`
  (`EDT_2D`, `SCREEN_ART_FILES`, e o que o `SCREEN_GLYPH` faz de fato);
  `tools/looks/iso_source.py` (o `EDT_2D` entre os aceitos no disco inglês);
  `tools/looks/controls.py` (o nó lido como um comando só, o sprite que
  esquece a página); `docs/PLAN-LOOKS-PY.md` (a tabela dos sprites),
  `docs/prompts/perfil-looks.md` (armadilhas 89 e 90, a 87 fechada, a fonte
  binária nova e a linha do `--scenery`) e `CLAUDE.md`.
- **Problemas encontrados:** a barra vazia é chapada, e o controle deslocado
  lê nela o mesmo que o disco; o controle passou a valer sobre todos os
  grupos, e o grupo chapado diz na própria linha que ali ele não distingue.
  E as escritas por script deixavam `CRLF` na cópia de trabalho; o
  `.gitattributes` normaliza, mas um `replace` de texto com `\n` não casa —
  os patches passaram a normalizar antes.

### O que faltava, e para onde foi

- **Os sprites estáticos e as setas** — placa, caixas, ícone, barra, título:
  [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md).
- **A tabela de glifos e o texto com a fonte do `EDT_2D.BIN`**:
  [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md).
- **O alinhamento à direita**, medido na terceira passada e não aplicado:
  [`LOOKS-TASK-38`](/docs/tasks/looks/38-o-alinhamento-dos-valores.md).
- **A ajuda**, escrita na VRAM em tempo de execução:
  [`LOOKS-TASK-39`](/docs/tasks/looks/39-o-texto-da-ajuda.md).
- **A câmera do close-up por linha**:
  [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md), antes da
  [`LOOKS-TASK-33`](/docs/tasks/looks/33-a-janela-animada.md).

Cada uma tem o que já está medido escrito no próprio contexto.

**Gates, na árvore commitada:** `selftest` 0 falhas, 94 de 94 controles
vermelhos; `cli check` 10 de 10; `iso_source.py --check-discs` ok, com o
`EDT_2D` aceito nos dois discos; `oracle.py --scenery` 0 problemas (43
pacotes e 142 sprites, iguais nas duas leituras, nos dois slots; texels e
CLUTs de todos os grupos com imagem no disco iguais à VRAM, e o controle
divergindo em 1.502 de 2.128); `oracle.py --repaint` e `--pages` sem mudança
desde a segunda passada; `confront.py --outside` sem mudança desde a quarta
(a janela não mudou nesta passada); `looks_ui` 12 de 12 controles vermelhos,
33 pacotes amostrados; `check_tasks` 138 ok.

### Fechamento, 2026-09-21

- **Resumo:** a pedido do usuário, a task fecha dividida. O que ela entrega é a
  resposta da incógnita (o) — de onde vem cada elemento da tela, lido da lista
  que o quadro entrega ao GPU e, para o que é imagem, do disco contra a VRAM —
  e a mobília desenhada como o GPU desenha, com a comparação fora da
  silhueta. O que faltava virou cinco tasks da fase 10, com IDs novos e as
  linhas logo depois desta no `progresso.md`, porque renumerar arrastaria as
  32 a 35.
- **Arquivos:** as tasks novas `36-os-sprites-estaticos.md`,
  `37-a-tabela-de-glifos.md`, `38-o-alinhamento-dos-valores.md`,
  `39-o-texto-da-ajuda.md` e `40-a-camera-do-close-up.md`; o `progresso.md`
  (tabela, fases, ordem, grafo, sequência e checklist); a
  `33-a-janela-animada.md` e a `35-fechamento-da-v2.md` (dependências); o
  `docs/PLAN-LOOKS-PY.md` (o veredito da §10.3 (o)).
- **Problemas encontrados:** nenhum.
