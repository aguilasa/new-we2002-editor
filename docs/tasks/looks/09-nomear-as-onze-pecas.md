---
id: LOOKS-TASK-09
title: "Incógnita (b) — nomear as onze peças pelo emulador, não pelo tamanho"
type: engenharia-reversa
category: formato
phase: 2
depends_on: [LOOKS-TASK-08]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#6"
reviewed_on: 2026-09-15
review_commit: null
done_on: 2026-09-15
done_commit: bb34937
---

# LOOKS-TASK-09: Qual peça é qual

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (b), e §1.5.
- Onze peças: cinco duplas de contagem idêntica mais uma sozinha. **Nomeá-las
  pelo tamanho é palpite.**
- A tela ajuda de graça: ela **fecha a câmera no rosto** em `SKIN` e `HAIR`, e
  **abre o corpo** em `BODY`. Isso já separa cabeça de tronco sem medir nada.
- **Comece por `load_state`.** Os dois states de 2026-09-14 põem o jogo na tela
  de edição: **slot 1 goleiro, slot 2 jogador de linha**, os dois no disco
  inglês. Recarregar entre medições dá baseline byte a byte idêntico, e é o que
  faz o diff medir só o que você mudou.
- **A RAM se lê por MCP vivo.** O `savestate.py` não alcança a RAM nesta
  máquina: sem CLI `zstd` e sem o módulo `zstandard`, ele lê cabeçalho e para.
- **O slot 1 é goleiro e o slot 2 é jogador de linha.** Goleiro tem luva e
  manga comprida; a diferença entre os dois já aponta quais peças são de
  uniforme.

---

- **As duas listas do `EDT_MOD.BIN` já têm dono, e isso poda metade do
  trabalho.** Medido em 2026-09-14 pela
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) com
  `python tools/looks/oracle.py --fields SKIN`: trocar `SKIN` no **slot 1
  (goleiro)** reescreve as seções 11, 16, 17, 18 e 19, que são as da **lista
  1**; no **slot 2 (jogador de linha)**, as seções 0, 3, 4, 5, 6, 7 e 8, que
  são as da **lista 0**. Interseção vazia. **Lista 0 é o jogador de linha,
  lista 1 é o goleiro** — e as peças que cada uma nomeia já estão separadas por
  boneco antes de esta task começar.
- **A `MODEL.BIN` seção 24 é a cabeça, e é compartilhada.** `HAIR`, `FACE` e
  `SKIN` escrevem os três nela, e só nela dentro do `MODEL.BIN`. É a primeira
  peça que esta task pode nomear sem trocar nada.
- **Sobram duas faixas de buffer por nomear.** Cada campo move de 130 a 320
  bytes que caem **fora** dos dois arquivos de modelo, e eles se concentram em
  `0x80153000+` e `0x80162000+` — a `0xF000` uma da outra, e **não** cópias uma
  da outra (15,3% de bytes iguais). Nomeá-las é o que separa "a geometria
  carregada" de "a geometria que a GPU desenhou", e é trabalho desta task.

---

## Objetivo

Cada uma das onze peças com nome medido, e o critério que sustentou o nome.

---

## Critério de conclusão

- [x] Cada peça tem nome — cabeça, cabelo, tronco, braço, antebraço, coxa,
      perna, pé, ou o que a medição mostrar —, e ao lado **como se soube**.
- [x] Cada medição parte de `load_state`, e **é repetida** a partir dele: o
      mesmo gesto duas vezes tem de dar o mesmo diff.
- [x] As onze peças são levantadas nos **dois slots**, e a diferença entre
      goleiro e jogador de linha fica registrada — é o que separa peça de
      uniforme de peça de corpo.
- [x] O método é trocar a opção no jogo e ver o que muda, não deduzir do
      número de vértices.
- [x] Fica medido se **`HAIR` troca a peça** (malha nova) ou só a paleta. A
      tela sugere malha — `A1` → `B3` mudou o cabelo de curto para comprido —,
      mas sugestão não é medição.
- [x] Fica medido o que `NAT` e `AGE` fazem, se é que fazem alguma coisa
      (§5.6, item 3).
- [x] Fica medido o que `HEIG` e `BODY` fazem: escala, peça diferente, ou as
      duas coisas.
- [x] A dupla de contagem idêntica é confirmada como **espelho esquerda/direita**,
      ou desmentida.

---

## Log de Execução

**Executado em:** 2026-09-15

### As doze peças, e por que cada nome

`python tools/looks/pieces.py --check-image`:

| posição na lista | seções (lista 0 / lista 1) | peça |
|---|---|---|
| 0 | 0 / 11 | **tronco** |
| 1 e 3 | 1, 2 / 12, 13 | **braço** (parte alta) |
| 2 e 4 | 3, 4 / 14, 15 | **antebraço** |
| 5 e 8 | 5, 6 / 16, 17 | **coxa** |
| 6 e 9 | 7, 8 / 18, 19 | **perna** |
| 7 e 10 | 9, 10 — **compartilhadas** | **pé** |
| — | `MODEL.BIN` seção 24 | **cabeça** |

**Cinco argumentos, e nenhum é o número de vértices.** O módulo implementa os
três primeiros e **confere** os dois últimos, que vêm do emulador:

1. **Os pares são espelhos exatos em `z`.** Conjunto de vértices igual, vértice
   a vértice, com `z` negado — nove pares em nove. O eixo é **procurado**, não
   suposto, e isso não é zelo: `x` é o palpite óbvio e `x` não é. Comparar
   *conjuntos* e não caixas envolventes também é de propósito: duas peças podem
   dividir uma caixa e ser malhas diferentes. **A dupla de contagem idêntica do
   critério está confirmada**, e não por semelhança: por igualdade.
2. **A lista do cabeçalho é uma cadeia.** `0 | 1 3 | 2 4 | 5 7 9 | 6 8 10`:
   tronco, um membro, o espelho dele, e dentro do membro de dentro para fora. O
   corte sai de onde o **lado** troca, o que não exige saber o que é um membro.
3. **O que as duas listas compartilham são a 9 e a 10**, byte a byte iguais —
   e membro que termina em seção compartilhada é perna. Daí a cadeia de três ser
   coxa, perna, pé, e a de dois ser braço, antebraço.
4. **O jogo concorda, e é ele quem separa braço de antebraço.** `SKIN` reescreve
   o CLUT exatamente das peças de pele nua:

   ```text
   SKIN on slot 1 rewrote: shin a, shin b, thigh a, thigh b, torso
   SKIN on slot 2 rewrote: forearm a, forearm b, shin a, shin b, thigh a, thigh b, torso
   ```

   No jogador de linha o antebraço **e não** o braço — manga curta. No goleiro
   **nenhum dos dois** — manga comprida. As pernas nos dois; o pé em nenhum, por
   causa da chuteira. E o tronco leva 4 bytes só, que é o pescoço.
5. **E `BOOTS` concorda sem ter sido perguntado.** As únicas seções que ele toca
   são a 9 e a 10, nos dois slots — exatamente as que a regra 3 achou pelo outro
   lado, sem que nenhuma das duas tenha sido ajustada à outra.

### O que cada campo faz, medido nos dois slots

`python tools/looks/oracle.py --fields`, cada um a partir de `load_state`:

| campo | peça que toca | o que muda | fora dos arquivos |
|---|---|---|---|
| `SKIN` | tronco, antebraço, coxa, perna + cabeça | **CLUT**, `+0x40` | 145 / 202 B |
| `HAIR` | **só** a cabeça | **`v`**, `+0x20` | 124 / 122 B |
| `H.COL` | **só** a cabeça | **CLUT** | 74 / 96 B |
| `BOOTS` | **só** os pés | **CLUT** | 128 / 135 B |
| `FACE` | **só** a cabeça | **`v`** | 35 / 35 B |
| `HEIG` | **nenhuma** | — | 106 / 270 B |
| `BODY` | **nenhuma** | — | 304 / 237 B |
| `NAT` | **nenhuma** | — | 70 / 138 B |
| `AGE` | **nenhuma** | — | 4 / 4 B |

Quatro respostas do critério caem daí:

- **`HAIR` é textura, não malha.** Ele move `v` e mais nada — nenhum vértice,
  nenhuma contagem, nenhuma peça a mais. O par `HAIR` + `H.COL` fecha o
  argumento: um anda a faixa do atlas, o outro anda a paleta, e os dois na mesma
  seção. A tela sugeria malha nova, e a sugestão estava errada.
- **`NAT` e `AGE` não fazem nada de geometria**, e o `AGE` move **quatro bytes**
  em toda a RAM. A §5.6 do plano dizia "provavelmente"; agora diz o número.
- **`HEIG` e `BODY` são escala na hora de desenhar.** Nenhum byte na geometria
  carregada, e os dois escrevem na lista de display.
- **Goleiro contra jogador de linha:** o segundo boneco é **o mesmo esqueleto
  com duas peças remodeladas**, e não um remapeamento de textura do primeiro.
  Medido posição a posição pelo `pieces.py --check-image`, que desde
  2026-09-15 imprime a comparação
  ([`CORR-LOOKS-021`](/docs/tasks/looks/CORR-LOOKS-021.md)):

  | posição | seções | o que difere |
  |---|---|---|
  | tronco | 0 × 11 | **mesmo tamanho** — 505 de 2.384 B, **2** deles de vértice |
  | braço | 1 × 12, 2 × 13 | **malha diferente** — 30/24 contra 40/34 |
  | antebraço | 3 × 14, 4 × 15 | **malha diferente** — 80/78 contra 88/86 |
  | coxa | 5 × 16, 6 × 17 | mesmo tamanho, 250 de 2.000 B, **22** de vértice |
  | perna | 7 × 18, 8 × 19 | mesmo tamanho, 240 de 1.168 B, **zero** de vértice |
  | pé | 9, 10 | a **mesma seção**, compartilhada pelas duas listas |

  **Esta linha dizia outra coisa até 2026-09-15**, e as três estavam erradas:
  punha o tronco entre as de tamanho diferente (ele tem o mesmo tamanho, e a
  tabela da §1.5 já dizia), dava os dois bytes de vértice do tronco como se
  descrevessem as três, e concluía *"mesma malha, uniforme diferente"* para as
  onze. Vale só da perna e do pé. Quem ler a frase velha e escrever montagem
  carrega **uma** malha e troca paleta — e desenha o goleiro com o braço do
  jogador de linha.

### As duas faixas de residuo: são a lista de display, dobrada

Era a pendência que a LOOKS-TASK-08 encaminhou para cá.
`python tools/looks/oracle.py --buffers`:

```text
  0x80153000  14394 of 20480 byte(s) non-zero; 365 display-list node(s)
      textured quad                301
      gouraud quad                  35
      flat quad                     24
      draw mode                      5
  0x80162000  15901 of 20480 byte(s) non-zero; 440 display-list node(s)
      textured quad                298
      flat quad                     67
      gouraud quad                  59
      draw mode                     16
  the two bands are 0xf000 apart and 3130 of 20480 byte(s) equal (15.3%)
```

Cada nó é `[link][pacote]`: uma palavra cujos 24 bits baixos apontam o nó
seguinte e cujo **byte alto é o comprimento** do pacote que vem a seguir. O que
faz disso prova é a **concordância dos dois números** — o comprimento declarado
tem de ser o comprimento que o hardware dá àquele comando. Um código de comando
sozinho é coincidência de um byte; trezentas concordâncias não são.

**E a primeira versão do walk respondeu zero.** Ela exigia que o link apontasse
para **dentro** da própria faixa, e ele não aponta: o primeiro nó da faixa mira
`0x0006B53C`, longe dali. Perguntar se a região é fechada em si é outra pergunta,
e a resposta dela estava sendo lida como resposta desta. O conserto está no
docstring, e o controle `oracle-list-walk-lax` guarda a metade que importa.

O primeiro pacote da faixa B, desmontado, fecha o círculo com a §1.6:

```text
0906b53c 7f7f7f2c 5bffe9ff bc0f0178 5bffe3ff bc011800 ...
   link     0x2C      tela   u=bc v=0f  clut=7801   tpage=0018
```

`u`, `v`, CLUT e página **iguais aos da primitiva do disco** — é a mesma
primitiva, já transformada para a tela.

### Duas calibrações, e a segunda recusou medir

- **A tecla de valor não tem um limiar só.** `A1TYPE` → `A2TYPE` move a célula
  0,016759; `175 cm` → `174 cm` move **0,009463**, uma casa decimal. O piso de
  0,010, calibrado numa letra, **rejeitou o dígito** como "a tecla não
  registrou".
- **E baixá-lo para 0,002 fez a guarda morder**: a célula do `AGE` deriva
  **0,002033 sozinha** — a caixa amarela do cursor pisca, e quanto menos texto a
  célula tem, mais a piscada pesa. A ferramenta **recusou em vez de medir**, que
  é o que se pede dela. O conserto não foi outro número fixo: o piso passou a ser
  **três vezes a deriva ociosa da própria linha**, medida na hora, com 0,004 de
  mínimo. `NAT` roda com piso 0,004000 e `AGE` com 0,006098.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 9 file(s), 4565 line(s)
  controls: 0 failure(s)      ..... 15 of 15 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/pieces.py --check         ->  pieces.py: 0 failure(s)
python tools/looks/pieces.py --check-image   ->  pieces --check-image: ok
python tools/looks/oracle.py --check         ->  oracle.py: 0 failure(s)
python tools/looks/oracle.py --check-live    ->  oracle --check-live: 0 failure(s)
python tools/looks/oracle.py --fields ...    ->  exit 0
python tools/looks/oracle.py --buffers       ->  exit 0
python tools/looks/modelfile.py --check-image ->  ok
python tools/check_tasks.py                  ->  123 task(s), ok
```

Três controles novos, e os três guardam o que esta task afirma:
`pieces-mirror-x-only` procura o espelho só em `x` — o eixo do palpite — e não
acha par nenhum; `pieces-witness-blind` cega o emulador, e aí uma nomeação com
braço e antebraço **trocados** passa; `oracle-list-walk-lax` tira a
concordância de comprimento do walk, e a lista de display vira histograma.

`roms/` só foi lida; a geometria vem da japonesa por `WE2002_LOOKS_IMAGE`, e do
disco inglês, que o emulador boota, não se leu textura nenhuma.

### Arquivos criados/modificados

- `tools/looks/pieces.py` — **novo**. `mirror_axis()`, `mirrors()`, `limbs()`,
  `name_pieces()`, `bare_skin()`, `agrees_with_the_game()`, `bounds()`,
  `report()`, as constantes `SKIN_SECTIONS` e `BOOTS_SECTIONS` com a
  proveniência, e `self_check()` com os casos vermelhos
- `tools/looks/oracle.py` — `--buffers`, `walk_packets()`, a tabela
  `GPU_COMMANDS` escrita como **códigos** e não como literais hexadecimais, as
  faixas em `BUFFER_BANDS`, e o piso da célula de valor recalibrado para a
  deriva da própria linha
- `tools/looks/controls.py` — os três controles novos
- `tools/looks/selftest.py` — `pieces` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §6 (b) respondida, a tabela da §1.5 com os nomes, e
  a §5.6 item 3 com o número no lugar de "provavelmente"
- `docs/tasks/looks/13-campos-e-dominios-de-looks.md` — os campos sem efeito
  visual, e os rótulos de linha
- `docs/tasks/looks/14-tabela-de-montagem.md` — as quatro linhas já medidas, e o
  padrão de que a peça nunca é trocada
- `docs/tasks/looks/15-visualizador-opengl.md` — o gabarito da geometria
  desenhada, e onde ele está
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 2
- `docs/tasks/looks/09-nomear-as-onze-pecas.md` — este arquivo

### Problemas encontrados

- **A hipótese de que as faixas eram lista de display quase foi descartada por
  um walk errado.** Ele respondeu `0 OT link(s)` e a leitura confortável seria
  "não são". O que salvou foi olhar os bytes: o segundo `0x2C` e o `bc0f0178`
  do primeiro pacote são reconhecíveis a olho depois da §1.6. **Ferramenta que
  responde zero merece a mesma desconfiança que uma que responde verde** — é a
  armadilha 12 do perfil noutra roupa.
- **A cabeça não está no `EDT_MOD.BIN`**, e por isso não é uma das onze: são
  onze peças de corpo por boneco mais a cabeça, que mora na `MODEL.BIN` seção
  24. O `pieces.py` guarda isso numa constante em vez de deixar a conta "onze"
  sugerir que a cabeça é uma delas.
- **E a cabeça entrou aqui como uma peça só, o que ela não é.** Das suas
  **dezoito** primitivas, os três campos de cor movem **nove** —
  `{0, 1, 4, 8, 9, 13, 14, 16, 17}`; as outras nove ficam na mesma janela de
  paleta **inclusive depois de trocar a pele**, medido nos dois slots
  ([`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md)). Parte da cabeça
  não é pele — olho, boca, sobrancelha, o que for. **Nomeá-las é a pergunta
  seguinte, e o método é o desta task:** trocar a opção na tela e ver o que
  muda. Fica aberta aqui em vez de virar nome inventado.
- E o de sempre: `ctest -R looks` neste worktree responde `No tests were
  found!!!` e sai 0 ([`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md));
  os gates acima saíram dos comandos da coluna do meio do
  [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
