---
id: LOOKS-TASK-11
title: "A contradição 8 × 3.568 — qual imagem do `DAT2D.BIN` é o cabelo"
type: engenharia-reversa
category: textura
phase: 3
depends_on: ["LOOKS-TASK-10"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.8"
status: pendente
---

# LOOKS-TASK-11: Qual imagem é o cabelo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.8 e
  §1.7.
- **Dois documentos da cena se contradizem.** A tabela do CARP rotula o offset
  **8** como *"Pelos Cuerpos y botines"* e o **3.568** como *"Caras"*; o
  tutorial do `zeta` manda abrir o **3.568** para achar os cabelos.
- Os dois não podem estar certos, e **o disco decide**. É barato: exportar as
  duas imagens e olhar.
- Enquanto não estiver decidido, **nenhum código pode cravar nenhum dos dois**.

---

- **A primitiva diz qual página ela amostra, e isso entra na contradição.**
  Desde 2026-09-14 (§1.6, medida pela
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md)) sabe-se que
  os bytes 6..7 de cada primitiva são uma **página de textura**, e que nos dois
  arquivos ela vale `0x18`, `0x1A` ou `0x99` — VRAM (512, 256), (640, 256) e
  (576, 256). **A primeira é o gráfico do offset 8**, o que o CARP chama de
  *"Pelos"*; o do offset 3.568 cai em (544, 256), que **nenhuma primitiva
  nomeia**. Isso é evidência a favor do CARP e contra o tutorial do `zeta`,
  **e não fecha a questão**: 3.568 pode ser amostrado por uma primitiva cujo
  `u` passe dos 256 da página, que é como o hardware alcança o vizinho. Medir
  isso é desta task — o veredito continua sendo dela, agora com um lado da
  balança pesado.
- **E `HAIR` anda `v` de `0x20` em `0x20`**, nas quatro quinas das primitivas 1
  e 14 da `MODEL.BIN` seção 24. Se o cabelo é uma faixa de 32 pixels de altura
  num atlas, é nessa página que a faixa tem de aparecer.

---

- **As paletas do `DAT2D.BIN` já estão achadas e lidas** — 267, por
  `python tools/looks/texture.py --report`, medido em 2026-09-15 pela
  [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md). O que esta
  task ganha com isso é poder **exportar a imagem candidata já colorida**, em
  vez de olhar índices: o cabelo mora em `MODEL.BIN` seção 24, cujas primitivas
  amostram (16, 480) e (144, 480) — dentro da paleta larga da pele corrente.
- **E quatro dos nove CLUT ids da geometria não estão neste arquivo:** os três
  de 8 bits em (0, 485), (0, 486) e (0, 488) — que são os uniformes, jogador de
  linha e goleiro — e um estreito em (336, 510). Junto com as duas páginas de
  textura que a §1.7 já registrava como ausentes, é a mesma pergunta: **de qual
  contêiner vem o resto**. Achar isso é desta task, e o `texture.py` lê qualquer
  `BIN/*.BIN` do disco, não só o `DAT2D.BIN`.
- **Seis seções do `MODEL.BIN` compartilham a paleta da chuteira**, e são
  candidatas nomeáveis pelo mesmo método que nomeou as onze peças. Medido em
  2026-09-15 ([`CORR-LOOKS-023`](/docs/tasks/looks/CORR-LOOKS-023.md)): as
  seções **11, 12, 22, 23, 63 e 64**, cinco primitivas cada, amostram
  (0, 484) — a paleta que no `EDT_MOD.BIN` é só do pé. A cabeça **não** está
  entre elas: a seção 24 amostra (16, 480) e (144, 480) e nunca (0, 484), o que
  reforça que a geometria da cabeça é outra coisa. Luva, meião ou o que for, o
  gesto que nomeia é o da LOOKS-TASK-09 — trocar a opção no jogo e ver o que
  muda.
- **A tabela do CARP acertou os dois rótulos de paleta** (as quatro "Pieles" e
  "Botines"), o que diz que ela foi feita olhando o arquivo — e **não** diz nada
  sobre os rótulos de imagem, que são justamente o que contradiz o tutorial do
  `zeta`. §1.8 do plano.

---

## Objetivo

Resolver a contradição por exportação, e deixar o rótulo de cada uma das 23
imagens conferido ou marcado como não conferido.

---

## Critério de conclusão

- [ ] As imagens de offset 8 e 3.568 exportadas para PNG e **olhadas**.
- [ ] O veredito registrado com a evidência, e o documento da cena que errou
      fica nomeado — não para culpar, para que ninguém volte a ele.
- [ ] Cross-check barato disponível: o Superpack traz
      `Caras - zeta\cabellowe2002.bmp` (8,1 KB, folha de cabelo 4 bpp) e dois
      `.tim` do mesmo conteúdo; comparar contra a nossa exportação decide sem
      depender de julgamento visual.
- [ ] Os 23 rótulos ficam numa tabela, cada um marcado **conferido** ou
      **opinião de terceiro**.

---

## Log de Execução

*(preencher ao executar)*
