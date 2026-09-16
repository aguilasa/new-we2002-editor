---
id: LOOKS-TASK-17
title: "Confronto — nosso quadro contra o quadro do emulador, na mesma tupla"
type: verificação
category: oráculo
phase: 6
depends_on: ["LOOKS-TASK-16"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §5.3"
status: pendente
---

# LOOKS-TASK-17: O confronto com o gabarito vivo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.3 e
  §5.6.
- **A diferença não precisa ser zero, e não vai ser.** A §5.6 já diz por quê: a
  pose vem do `ANIME.BIN`, que está fora de escopo, e a câmera do jogo muda por
  campo. Nosso render é pose neutra e câmera livre.
- *Um número que ninguém olhou não é verificação.* A diferença tem de ser
  **medida, registrada e explicada**.
- **`load_state` é o que torna o confronto repetível.** Sem baseline fixo, o
  quadro capturado depende de quanto tempo a animação correu, e o número muda
  entre corridas sem que nada tenha mudado. Slot 1 é goleiro, slot 2 é jogador
  de linha.

---

- **Três resíduos da tabela de montagem chegam aqui, e o confronto é o que os
  fecha.** Medidos em 2026-09-16 pela
  [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md):
  **(1)** os estilos de cabelo `H1`, `M1` e `N1` não foram alcançados pelo mapa
  e o `assembly.head_of` os recusa — as seções pares 38, 40 e 42 nunca foram
  nomeadas, e casar três com três por contagem é o mapeamento plausível que
  este ciclo não escreve; **(2)** a faixa da folha de cabelo só é aplicada em
  **quatro** das treze cabeças (`layout.HAIR_QUADS`), porque o breakpoint da
  instrução que escreve o quad só parou nessas quatro; **(3)** o mapa inteiro é
  do **jogador de linha**, e o bloco de cabeças do goleiro não foi andado.
  Confrontar as tuplas nos **dois slots** é o que mede as três coisas de uma
  vez — e uma tupla com `H1` tem de aparecer no confronto como recusa, não
  como diferença de pixel.
- **O corpus já foi confrontado uma vez, e no nível de textura.** O
  `assembly.py --corpus` compara onde os renders de terceiro mudam com a altura
  que a malha dá às primitivas de cada campo, e fecha em `rho = 0,80`. O que
  ele **não** faz é comparar o desenho: isso é daqui.

---

- **A POSE NÃO ESTÁ EM ARQUIVO NENHUM QUE ESTE CICLO LÊ, e isso chega aqui.**
  Medido em 2026-09-16 pela
  [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md): cada seção é
  modelada em torno da **própria origem** — a cabeça vai de y -15 a 48 e a
  chuteira de -15 a 18 —, então nem "pose neutra" o disco dá. O visualizador
  desenha uma **prateleira** (`scene.shelf`), peças em fila. Quem posiciona é o
  jogo, na display list da §6(a) do plano, que é justamente o que se lê com o
  emulador de pé — então **medir o deslocamento de cada peça é trabalho desta
  task**, e sem ele o confronto compara uma fila com um jogador e a métrica não
  quer dizer nada.
- **Qual das duas diagonais um quad é continua sem veredito.** O
  `scene.TRIANGLES` usa a ordem **como o arquivo guarda** — (0, 1, 2) e
  (1, 2, 3) — e o `section.Primitive.corners` oferece a leitura do `we3d`, que
  escolhe a outra. As duas desenham; só o confronto contra o quadro do jogo
  diz qual. Escolher aqui em silêncio é o que esta linha existe para impedir.
- **O uniforme não é desenhado, e não é bug:** 237 das 593 primitivas da figura
  amostram páginas que o `DAT2D.BIN` não tem — elas vivem nos 105
  `TEX_*.BIN`, um por time, cada um com cinco paletas de 256 entradas
  ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)). Saem em cinza de
  espaço reservado. Qual contêiner e qual das cinco paletas o jogo usa é
  pergunta que só o emulador responde, e o `layout.DIGEST` ainda não tem esses
  arquivos.
- **A tela da barba pode alcançar mais do que a varredura mediu.** O
  `assembly` mede `FACE` chegando a **cinco** valores (A..E) e **recusa** `F` e
  `G`; o corpus de terceiro traz dezesseis renders com eles
  (`scene.py --corpus`: 31 dos 50 desenhados, 16 recusados por isso). É a
  armadilha 19 outra vez, do outro lado: andar o campo até a ponta nos **dois**
  slots é o que separa "a tela trava em E" de "a varredura parou em E".

---

## Objetivo

Fechar o laço: mesma tupla dos dois lados, e um número que se possa acompanhar
ao longo do projeto.

---

## Critério de conclusão

- [ ] O ciclo roda: `load_state`, escolher a tupla na tela por `press_button`,
      capturar por `take_screenshot`, renderizar a mesma tupla, comparar.
- [ ] A captura é feita **no mesmo quadro** de cada corrida — `pause` mais
      `frame_step` contado a partir do state, nunca "depois de uns segundos".
- [ ] O confronto cobre os **dois slots**, e não só um: goleiro e jogador de
      linha exercitam conjuntos de peças diferentes.
- [ ] Ao menos **três tuplas** confrontadas, e não uma — uma só não distingue
      acerto de coincidência.
- [ ] A métrica é nomeada e justificada, e o número registrado por tupla.
- [ ] Cada fonte de diferença é **atribuída**: pose, câmera, resolução, filtro.
      O que sobrar sem explicação é achado, e vira CORR ou task.
- [ ] O confronto é **repetível**: a tupla, a rota e o comando ficam
      versionados, como os roteiros de `tools/par/` fazem para o golden.

---

## Log de Execução

*(preencher ao executar)*
