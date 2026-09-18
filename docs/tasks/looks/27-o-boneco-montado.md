---
id: LOOKS-TASK-27
title: "As peças no lugar — `scene.py` aplica a pose, e o painel da tela mostra o boneco montado"
type: implementação
category: render
phase: 9
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-26"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.4"
status: pendente
---

# LOOKS-TASK-27: O boneco montado

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1, §10.4 e §6 (e).
- **É o primeiro pedido do usuário:** o jogador **montado**, no painel da tela
  `LOOKS SET` da [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md), não em prateleira.
- **A regra 3 continua:** a pose sai do núcleo (`anime.py` → `scene.py`); a
  `ui/` só desenha.
- **A prateleira não some.** É o jeito de olhar uma peça isolada, e o `S` a
  alterna; o que muda é o default.
- **O que a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md)
  mediu em 2026-09-18 e esta task tem de honrar:**
  - **a transformação por peça é absoluta** — a câmera composta com a volta da
    peça —, então montar não é compor hierarquia: é aplicar doze
    transformações prontas. O esqueleto do jogo **não é rígido** (cinco juntas
    se separam, o resto não), e supor uma cadeia anatômica é inventar;
  - **a tela desenha DUAS chuteiras e só UMA carrega matriz.** As seções 9 e 10
    são lidas as duas (watchpoint de leitura, uma corrida por seção, 2 e 2, com
    seção desenhada de controle), e a passada tem uma carga só para a 9. A
    segunda chuteira é desenhada **reaproveitando a rotação que já está no
    GTE**. Uma montagem que espere uma matriz por peça desenhada deixa um pé
    para trás ou o põe no lugar errado — **medir onde a segunda chuteira cai é
    desta task**, e a captura da 25 não a nomeia;
  - **`y` cresce para baixo** (cabeça em `y = −8`, pé mais baixo em `y = 60`),
    de acordo com o `UP = -1` que o `scene.py` já usa, e **nenhuma matriz tem
    determinante negativo** — o espelho das peças `b` está na geometria.

---

## Objetivo

O `scene.py` monta a figura aplicando a pose do quadro pedido a cada peça, e o
painel da tela `LOOKS SET` abre com o boneco montado.

---

## Critério de conclusão

- [x] `scene.from_image(..., frame=N)` devolve os pontos transformados pela
      pose do quadro N; `scene.shelf` continua disponível.
- [x] `ui/app.py --frame N`; sem ele, a prateleira de sempre.
- [ ] **Conferido contra o jogo, peça a peça:** a ordem relativa dos centros
      como asserção do `scene.py --check-image`. **NÃO FEITO, e a razão é um
      achado:** com as posições que o arquivo guarda, a figura **não fica em
      pé** — e isso não é erro de leitura (ver o Log).
- [ ] Captura olhada no Log, nos dois slots.
- [ ] `ui_check.py` julga a figura montada.
- [ ] Controle negativo: a hierarquia invertida fica vermelha.

---

## Log de Execução

**Executado em:** 2026-09-18 — **PARCIAL**

**Resumo do que foi aprendido**

**O `ANIME.BIN` guarda a pose inteira: ângulo E lugar.** A segunda palavra de
cada par, que a [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md)
tinha deixado sem leitura, é a **posição** da peça: `x` nos bits 10:0 com
sinal, `z` nos 31:21 com sinal, e `y` em dez bits que o jogo remonta
**trocados** — os bits 11..15 viram os cinco altos e os 16..20 os cinco baixos
—, com o sinal nos dois bits de cima da **primeira** palavra. É o código em
`0x80011F0C..0x80011F50` lido de volta, e a conferência é contra as translações
que o próprio jogo entregou ao GTE: com o lugar da raiz subtraído e a câmera
aplicada, **96 peças batem com erro máximo de 4 unidades** (79 delas com 1).

**E com esses lugares a figura não fica em pé.** Montada, a chuteira cai na
altura da coxa. Isso **não é erro de decodificação**, e é o que esta task deixa
medido: nas translações que o jogo carregou — não nas nossas —, a origem da
chuteira está a **192** unidades da raiz e a da canela a **394**. O jogo põe a
origem da chuteira acima da canela, e as duas seções de chuteira medem
`y −18..15` em torno da própria origem, então não é geometria pendurada. Falta
uma peça do quadro: o que reposiciona a chuteira não está no par dela.

**O que fica pronto** é a máquina inteira: `anime.position()`, `scene.pose()`,
`scene.from_image(..., frame=N)` aplicando matriz e lugar no núcleo (a `ui/`
não importa `anime`), `ui/app.py --frame N`, e a captura fora da tela.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/anime.py` — `position()`, o lugar em cada peça de `frame_angles`,
  e os self-checks do campo
- `tools/looks/scene.py` — `pose()`, `piece_names()`, `mirror_of()`,
  `place_points()`, `_posed()`, e o `frame` em `build`/`from_image`/`Builder`
- `tools/looks/ui/app.py` — `--frame N`, e a prateleira desligada quando há pose
- `tools/looks/ui_check.py` — a linha plantada seguiu a linha que mudou de forma
- `docs/tasks/looks/27-o-boneco-montado.md` — este Log

**Problemas encontrados**

1. **A figura montada com o que o arquivo diz não fica em pé**, e a medição do
   jogo concorda com o arquivo — então o que falta é outra coisa, não a
   leitura. É o bloqueio da task, e está escrito no critério.
2. **A prateleira e a pose se somam se as duas ficarem ligadas.** O
   `ui/app.py` desliga a prateleira quando há `--frame`; sem isso cada peça é
   movida duas vezes e o resultado parece pose errada.
3. **Controle plantado do `ui_check` casava com uma linha que mudou de forma.**
   Quebrar a chamada do `from_image` em duas linhas para caber o `frame` fez o
   literal parar de casar: `matched 0 time(s)`, nem verde nem vermelho. É a
   mesma armadilha 53, noutro arquivo.
