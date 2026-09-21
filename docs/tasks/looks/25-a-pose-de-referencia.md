---
id: LOOKS-TASK-25
title: "A pose de referência — as matrizes de cada peça num quadro contado, e a hierarquia"
type: investigação
category: oráculo
phase: 9
depends_on: [LOOKS-TASK-24]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: 2026-09-18
review_commit: null
done_on: 2026-09-18
done_commit: 81c8ca8
---

# LOOKS-TASK-25: A pose de referência

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (k) e §10.4 (2).
- **Esta captura é o gabarito da Fase 9.** O leitor do `ANIME.BIN`
  ([`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md)) se mede contra ela; sem ela, um leitor plausível passa.
- **Quadro contado, nunca "depois de uns segundos".** `load_state`, `pause`, e
  `frame_step` N vezes.
- **Ponto fixo é inteiro.** Gravada como inteiros 4.12, a comparação de depois
  é exata.
- **A hierarquia não se deduz da anatomia.** Se a matriz do antebraço é
  absoluta ou composta com a do braço, mede-se: a translação da filha varia com
  a rotação da mãe, ou não varia.
- **Onde a matriz entra, medido pela [`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md)
  em 2026-09-17** (`oracle.py --pose`), e o que ela deixou para cá:
  - dos **30** `ctc2` da RAM que escrevem o primeiro registrador da matriz,
    **cinco** rodam nesta tela, e dois carregam quase tudo:
    `layout.POSE_MATRIX` (`0x80012168`) e `layout.POSE_MATRIX_SECOND`
    (`0x8001229C`) — 18 e 18 de 40 paradas, contra 2, 1 e 1 dos outros três;
  - **qual carga é de qual peça é desta task**, e é o que falta: a 24 conta
    paradas, não peças. O número de paradas antes de a sequência se repetir
    **varia entre corridas** (207 e 408 medidos), então ele não serve de
    contagem — quem conta quadro é esta, com `pause` + `frame_step`;
  - **um `continue` só nomeia a primeira instrução que dispara, não as que
    disparam.** As mesmas trinta, armadas igual, deram `0x80012168` numa
    corrida e `0x80010E38` na seguinte; o que transforma isso em contagem é
    soltar o emulador dezenas de vezes e ler o `hit_count` de cada uma.

---

## Objetivo

Gravar, para um quadro N contado a partir do `load_state`, a matriz de rotação
e a translação que o jogo usa em **cada peça desenhada** — as onze da figura e a
cabeça —, e dizer qual peça é filha de qual.

---

## Critério de conclusão

- [x] `oracle.py --pose <SLOT> <N>` grava em `work/looks-pose/` um JSON por
      quadro, com matriz e translação **inteiras** de cada peça, a peça nomeada
      pelo `pieces.py` e o N ao lado. `--poses` roda os dois slots e os oito
      quadros de `oracle.POSE_CAPTURE_FRAMES` de uma vez.
- [x] **Repetível:** duas capturas do mesmo N idênticas número a número; e
      dois N diferentes, diferentes — sem isso a captura pode ler uma
      constante. O controle fecha **antes** de qualquer outro número ser lido,
      e a segunda conferência é do próprio comando (`reading a constant`).
- [x] A hierarquia medida, com a evidência. **E o resultado é que ela não é
      rígida:** cinco pares se separam por 4,6x a 14,6x nos dois slots e
      nenhuma linha fora deles passa de 3,3x (3,3x no slot 1, 2,5x no 2 —
      corrigido de 2,3x para 2,5x em 2026-09-18,
      [`CORR-LOOKS-060`](/docs/tasks/looks/CORR-LOOKS-060.md), e de 2,5x para
      3,3x no mesmo dia pela
      [`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md), que trocou o
      nome de cada peça por aquela que a matriz desenha). O leitor não compõe hierarquia — o que
      chega ao GTE por peça já é absoluto.
- [x] A convenção escrita: ordem de aplicação, escala 4.12, e o sinal de `y`
      contra o `UP = -1` do `scene.py`. Medido: `y` cresce para baixo, a
      composição é câmera × volta da peça (`M x Mt = C x Ct`, pior caso
      0,0071 contra 0,99 de uma matriz que não é composta assim), e nenhuma
      matriz tem determinante negativo.
- [x] Os dois slots.
- [x] §10.3 (k) com o veredito e a data.

---

## Log de Execução

**Executado em:** 2026-09-18

**Resumo do que foi aprendido**

A pose por peça **é absoluta**: `layout.POSE_PIECE_MATRIX` entrega, para cada
peça desenhada, a câmera já composta com a volta daquela peça, e um leitor
nosso reproduz doze transformações prontas em vez de compor uma hierarquia.
As duas cargas que a [`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md)
contou como "duas instruções" **não são do mesmo tipo**: a primeira
(`POSE_MATRIX`) repete a mesma rotação em toda parada da passada enquanto a
translação anda pelas peças — é a câmera —, e ler a pose dela daria doze peças
com a mesma orientação. A hierarquia, medida pelo quadro da mãe, separa **cinco
pares** e mais nada: o esqueleto do jogo não é rígido, e isso é resultado, não
lacuna.

**Arquivos criados/modificados**

- `tools/looks/oracle.py` — a captura (`capture_pose`, `_pose_cycle`,
  `_repeating_period`, `_named_pass`, `_camera_matrix`, `_matrix_struct`,
  `piece_names`, `_drawn_section`, `write_pose`), a leitura dos números
  (`matrix_deviation`, `joint_offset`, `hierarchy`, `_multiply`, `_transpose`,
  `_determinant`, `_inverse`), a medição de seção lida (`_sections_read`,
  `_section_addresses`), o comando `check_pose_frames` e os self-checks novos
- `tools/looks/layout.py` — `POSE_PIECE_MATRIX`, `POSE_PIECE_MATRIX_BASE` e
  `POSE_MATRIX_BASE`, e o `POSE_MATRIX` corrigido sobre qual carga é qual
- `tools/looks/controls.py` — três controles plantados novos (78 de 78)
- `docs/PLAN-LOOKS-PY.md` — §10.3 (k) com o veredito e a data
- `docs/tasks/looks/26-o-formato-do-anime-bin.md` e
  `docs/tasks/looks/27-o-boneco-montado.md` — o que esta task lhes deixa
- `docs/prompts/perfil-looks.md` — a linha de gate e as armadilhas 45 a 47
- `docs/tasks/looks/progresso.md` — a linha e o checklist da Fase 9
- `CLAUDE.md` — a seção do ciclo, que envelhece com ele

**Gates, na árvore de `9dfb713`**

```text
$ python tools/looks/selftest.py
  ..... 78 of 78 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 6 of 6 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --poses
  -- slot 1 (goalkeeper) --
    control: frame 0 captured twice, 12 load(s), identical number by number
    12 piece(s) every pass: foot a, forearm a, forearm b, head, root, shin a,
      shin b, thigh a, thigh b, torso, upper arm a, upper arm b
      section 10 (foot b) read 2 time(s)
      section 19 (shin b) read 2 time(s)   <- control, drawn this pass
      section 10 is READ and carries no matrix load of its own [...]
    every matrix is the camera composed with a rotation: worst
      |M x Mt - C x Ct| is 0.0071 of the largest entry (threshold 0.0200)
    0 of 12 carry a mirrored matrix (negative determinant): none
      root          child of head          spread  3.2, next at 46.8 (14.5x)
      shin a        child of thigh a       spread  5.0, next at 52.3 (10.5x)
      shin b        child of thigh b       spread  4.8, next at 47.2  (9.9x)
      upper arm a   child of torso         spread 14.5, next at 76.5  (5.3x)
      upper arm b   child of forearm a     spread 15.5, next at 77.2  (5.0x)
      head          child of root          spread  6.3, next at 20.6  (3.3x)
      (os outros seis: 1,1x a 2,2x -- nao se separam)
    y grows DOWNWARD, as scene.UP = -1 already assumes: the head sits at
      y=-10 and the lowest foot at y=55
  -- slot 2 (outfield player) --
    control: frame 0 captured twice, 12 load(s), identical number by number
    worst |M x Mt - C x Ct| is 0.0015; 0 of 12 mirrored
      root 14.6x, shin b 12.8x, shin a 9.2x, upper arm a 4.9x,
      upper arm b 4.6x; os outros sete abaixo de 2,5x
    y grows DOWNWARD: head y=-8, lowest foot y=60
oracle --pose: 0 problem(s) over 8 frame(s) and 2 slot(s)

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**O vermelho, plantado e rodado** — o registrador base da câmera na carga da
peça (`POSE_PIECE_MATRIX_BASE`, `"v1"` → `"a0"`), numa cópia da árvore por
`git worktree`:

```text
  FAIL  slot 2 frame 0: 11 of the 12 loads carry the same numbers as another
        -- a pass in which the pieces do not differ is not a pose, whatever
        it repeats like
  FAIL  slot 2 frame 20: 11 of the 12 loads carry the same numbers as another
oracle --pose: 2 problem(s) over 2 frame(s) and 1 slot(s)
```

**Problemas encontrados**

1. **A rotação de `POSE_MATRIX` é a mesma para as doze peças, e quase virou "a
   pose".** Só a translação anda. O que separou as duas cargas foi olhar a
   rotação peça a peça em vez de aceitar a primeira que dispara.
2. **O contador de quadros vira no MEIO da passada.** Cortar a passada pelo
   `internal_frame_number` entregou **cinco** peças na primeira captura e doze
   na seguinte, sem erro nenhum. Quem fecha a passada é a sequência se
   repetindo.
3. **Dez quadros seguidos não nomeiam hierarquia nenhuma.** O boneco se mexe
   tão pouco entre quadros vizinhos que toda peça parece grudada em toda peça:
   1,0x a 8,6x. Espalhando os oito quadros por 140, as juntas verdadeiras vão a
   4,6x-14,6x e nenhuma linha fora dos cinco pares passa de 3,3x — o tronco
   no slot 1, e 2,5x no slot 2. Os números desta task saíram com a nomeação
   de antes do atraso de desenho, então cada par estava um elo fora: o que
   aqui se lê "raiz↔cabeça" é cabeça↔tronco, e as duas "canela↔coxa" são
   chuteira↔canela ([`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)).
   As transcrições abaixo ficam como foram lidas.
4. **Distância entre peças pareceu osso elástico, e era a câmera.** A câmera
   escala `y` por 0,61 e `x`/`z` por 0,80, então `|t_filha − t_mãe|` varia 25%
   com a peça girando. A conclusão "nenhum osso é rígido" chegou a ser escrita
   por esse caminho antes de o `M_mãe⁻¹` desfazer a câmera.
5. **Watchpoints de seção armados juntos leram silêncio que não existia.** O
   emulador para no primeiro acerto e fica lá, então a seção desenhada tomou as
   quatro paradas e a seção 10 leu **0** — o que se lê como "a tela nunca toca
   o `foot b`". Uma corrida por seção: **2 e 2**, e a janela mostrava duas
   chuteiras o tempo todo. É a armadilha 42 de novo, de outro lado: lá o erro
   foi amostrar pouco, aqui foi disputar a parada com o controle.
6. **O limiar da composição foi escrito de uma amostra só.** 0,006 saiu do pior
   caso do slot 2 (0,0013) e o slot 1 veio com 0,0071 e reprovou. O limiar
   agora é 0,02, escrito dos dois slots.
7. **O vermelho vivo saiu VERDE na primeira tentativa, e o buraco era do
   gate.** Plantando numa cópia da árvore o registrador base da câmera na
   carga da peça — de modo que as doze peças fossem lidas do mesmo lugar —, a
   corrida imprimiu doze peças idênticas, hierarquia com dispersão **0,0** e
   `infx`, e a cabeça na altura dos pés, e ainda assim disse **0 problemas**:
   o controle de repetição fecha (a captura repete), o de constante compara
   quadros (e a câmera muda de quadro para quadro), e nenhum dos dois olhava
   **dentro** da passada. O comando agora recusa passada em que duas cargas
   tragam os mesmos números — medido em 16 passadas nos dois slots, as doze
   sempre diferem —, e aí o plantio dá **2 problemas**, um por quadro. A regra
   que fica: **o controle plantado se roda de verdade**; um controle que só
   foi imaginado teria deixado esse gate passar para sempre.
8. **A regra 1 acusou os literais 4.12 do self-check.** `4096` é escala, não
   endereço; virou `FIXED_ONE` com a anotação, e as três linhas de matriz de
   teste levam `# not-an-address:` cada uma — a anotação vale para a **linha**,
   e uma acima não conta.
