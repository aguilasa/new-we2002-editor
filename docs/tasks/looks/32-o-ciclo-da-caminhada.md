---
id: LOOKS-TASK-32
title: "Incógnita (p) — o ciclo da caminhada: quadros por passada, interpolação e balanço"
type: investigação
category: oráculo
phase: 11
depends_on: [LOOKS-TASK-26]
status: pending
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
---

# LOOKS-TASK-32: O ciclo da caminhada

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (p) e §10.4.
- **Nenhum número da gravação do usuário vale aqui.** Vídeo de tela tem a
  cadência do gravador; quem conta é o `frame_step`.
- **Animar num ritmo inventado produz caminhada bonita e errada.**
- **Duas perguntas que parecem uma:** quantos quadros o jogo leva para repetir
  a pose, e quantos quadros-chave o `ANIME.BIN` guarda. Se forem diferentes, o
  jogo interpola, e a regra se mede.
- **O tronco balança na gravação.** Raiz da animação ou câmera muda onde o
  balanço mora.

- **O jogo MISTURA matrizes, e medir isso é desta task.** Medido em 2026-09-18
  pela [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md), sobre
  96 peças julgadas (de 192 capturadas — oito capturas não param no
  desempacotamento) nos dois slots:
  - **os ângulos vêm sempre do arquivo** — 96 de 96, inteiro por inteiro, no
    par que o jogo está lendo. Uma versão anterior desta linha dizia que
    metade dos quadros era construída, e aquilo era artefato da ponte errada
    (o quadro que o estado nomeia, que erra no goleiro);
  - **mas 6 das 96 matrizes não são a volta de par nenhum do arquivo** —
    varredura de todos os pares, `anime.no_pair_explains()`. O caminho que as
    produz é `0x80011F90`: ele **soma a matriz recém-construída com a que o
    jogo guardou e desloca um bit** (`sra 1`), meia-palavra a meia-palavra, e
    quem escolhe esse caminho é o byte em `0x0(s3)`;
  - as seis eram todas de **um passe só**, e as peças que vieram do quadro
    anterior da animação — o passe atravessou a troca de quadro. **De onde vem
    a segunda matriz da soma é o que falta**, e é o que decide o ritmo.
  - As ferramentas já entregam o que essa medição precisa:
    `oracle.py --pose <SLOT> <N>` grava, por peça, o ângulo e **o par que o
    jogo leu**; `anime.py --against-pose` separa exatas, misturadas e
    inexplicadas a cada corrida.

- **Três medições da [`LOOKS-TASK-29`](/docs/tasks/looks/29-altura-e-corpo.md),
  de 2026-09-19, que são do ritmo e não da estatura.** Ela as achou enquanto
  controlava `HEIG` e `BODY`, recusou-as do controle com razão, e elas se medem
  **aqui** (armadilhas 73 e 74 do perfil). Quem as reproduz é
  `python tools/looks/oracle.py --stature`, em toda corrida:
  - **uma passada de desenho atravessa DOIS quadros do `ANIME.BIN`**, cortados
    numa peça que muda com a fase — `frames [1, 2]` no slot 2 e `[3, 4]` no
    slot 1, remedido em 2026-09-20. Comparar pares peça a peça gastou 80
    passadas procurando um corte que não voltava; o que nomeia a pose é o
    **conjunto** de quadros (`oracle._stature_frames`). Isto é o período visto
    de outro ângulo: se uma passada desenha dois quadros-chave, "quadros por
    passada" e "quadros do `ANIME.BIN`" não são a mesma contagem;
  - **uma passada inteira pode vir interpolada** — 11 pares lidos e **0 de 11**
    matrizes exatas, medido pela 29 —, pela mesma média `(a+b)>>1` de
    `0x80011F90` que explica as 6 misturas de peça avulsa acima. A diferença
    importa para o critério: lá é peça avulsa na troca de quadro, aqui é a
    passada toda;
  - **no goleiro, o quadro 0 é mistura** na estatura do próprio estado: a
    `foot b` sai **até 92 de 4096** fora da matriz do arquivo **com os ângulos
    do scratchpad iguais aos do par** — ângulo certo, matriz outra. O
    `--stature` imprime isso como passada recusada, e a linha é literal na
    corrida de 2026-09-20:

    ```text
    control refuses pass 2, frames [0, 1]: 11 of 12 exact, ['foot b'] off by
    up to 92 of 4096 with the scratchpad angles the file's own
    ```

  É onde o critério "quadros-chave contra quadros desenhados: iguais, ou a
  interpolação medida" encosta: os três casos são a interpolação aparecendo, e
  o goleiro dá o exemplo mais barato de medir, porque acontece no quadro 0.

- **A [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) deixou uma
  armadilha que alcança toda leitura de registrador numa parada:** o ponteiro
  de modelo que o jogo carrega quando a matriz é carregada nomeia a peça que
  ele **acabou de desenhar**, uma parada atrás (`oracle.DRAW_LAG`). Quem
  acrescentar uma captura por breakpoint confere o atraso com
  `oracle.py --pose-lag` em vez de supor que o registrador fala da peça da vez.

---

## Objetivo

Medir o ciclo da caminhada em quadros do jogo, e fazer o `anime.py` devolver a
pose de **qualquer** quadro do ciclo igual à do jogo.

---

## Critério de conclusão

- [ ] O período: a primeira volta de todas as matrizes ao quadro 0, contada
      por `frame_step`, nos dois slots — e o comando que conta.
- [ ] Quadros-chave contra quadros desenhados: iguais, ou a interpolação
      medida, com o arredondamento do ponto fixo.
- [ ] `anime.py --frame N` reproduz o jogo **exatamente** em pelo menos oito N
      espalhados pelo ciclo, fora os quadros-chave.
- [ ] O balanço atribuído: raiz da animação, ou câmera.
- [ ] Controle negativo: interpolar pelo quadro-chave vizinho errado fica
      vermelho.
- [ ] §10.3 (p) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
