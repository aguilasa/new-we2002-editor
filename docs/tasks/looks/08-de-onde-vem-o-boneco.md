---
id: LOOKS-TASK-08
title: "Incógnita (a) — de onde vem o boneco: `EDT_MOD.BIN` ou os TMDs de `0x00168xxx`"
type: engenharia-reversa
category: formato
phase: 2
depends_on: ["LOOKS-TASK-07"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: concluído
---

# LOOKS-TASK-08: De onde vem o boneco da tela

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (a), e §1.6.
- **São três candidatos, não dois.** O `EDT_MOD.BIN` traz **dois** modelos de
  onze peças — duas listas de ponteiros, compartilhando duas peças, sobre o
  mesmo esqueleto (§1.5, medido pela
  [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md) em 2026-09-14).
  A pergunta "de onde vem o boneco" tem de escolher entre **lista A, lista
  B e os TMDs de `0x00168xxx`**, e os dois save states — goleiro e jogador
  de linha — são o estímulo óbvio para decidir se as duas listas são esses
  dois bonecos.
- **É a incógnita de maior risco do plano.** Quatro TMDs Sony de verdade —
  `id=0x41`, `flags=1`, texturizados, modos `0x2d` e `0x3d`, com 92, 261, 30 e
  18 vértices — vivem em `0x0016821C`, `0x00168C0C`, `0x0016A2C4` e
  `0x0016A650`, e **não pertencem a nenhum dos dois arquivos de modelo**.
- A GPU desenha em **4-bit CLUT** com textura ligada; a primitiva de 24 bytes
  das seções **não tem UV**. Os dois não podem estar certos para a mesma
  geometria.
- **Nada de geometria deve ser escrito antes de responder isto** — é a ordem
  obrigatória da §7 do plano.
- **Comece por `load_state`.** Os dois states de 2026-09-14 põem o jogo na tela
  de edição: **slot 1 goleiro, slot 2 jogador de linha**, os dois no disco
  inglês. Recarregar entre medições dá baseline byte a byte idêntico, e é o que
  faz o diff medir só o que você mudou.
- **A RAM se lê por MCP vivo.** O `savestate.py` não alcança a RAM nesta
  máquina: sem CLI `zstd` e sem o módulo `zstandard`, ele lê cabeçalho e para.
- **Os dois states são um controle de graça.** Goleiro e jogador de linha usam
  uniformes diferentes e, possivelmente, peças diferentes. O que diferir entre
  os dois é **posição ou uniforme**, não LOOKS — e isso separa dois eixos sem
  custo nenhum.

- **O `MODEL.BIN` guarda uma terceira forma de ponteiro, ainda não lida, e são
  DUAS corridas dela** — candidatas junto com as outras. Medido em 2026-09-14
  pela [`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md) e
  remedido pela
  [`CORR-LOOKS-013`](/docs/tasks/looks/CORR-LOOKS-013.md), que achou esta
  linha falando de uma só: 16 das 18 listas do cabeçalho abrem com tag `0x80`,
  e **12** miram o offset **104** enquanto **4** miram o **232**. Nenhum dos
  dois é seção — são corridas de ponteiros KSEG0 crus, sem tag e sem
  terminador, de **64** e de **32** ponteiros, apontando para dentro da região
  de geometria (104: 15.152, 15.768, 16.384, 17.200, …; 232: 49.856, 49.856,
  50.240, 50.240, … — e os pares repetidos ali são achado por si só). O
  `read_pointer_list()` não as lê, e ninguém mediu o que agrupam nem por que
  são duas. Se a resposta da incógnita (a) for "o boneco vem do `MODEL.BIN`",
  **são essas corridas que dizem qual dos modelos dele**, e a hipótese do
  `we3d` — 14 jogadores de 11 peças — se confere ali. **Procure duas tabelas,
  não uma**, e a segunda pode ser justamente o que distingue os agrupamentos.
- **E as duas listas de uma entrada do `MODEL.BIN` nomeiam seção**: tag `0x02`,
  mirando 1816 e 4792, que são as duas primeiras seções do arquivo.
- **O jogo REESCREVE a geometria carregada, e o diff com o disco já aponta
  onde.** Medido em 2026-09-14 pela
  [`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md), com o
  jogo parado na tela, por `python tools/looks/oracle.py --check-live`:

  ```text
  /BIN/EDT_MOD.BIN at 0x8011c000: 203 of 36072 byte(s) differ (99.44% equal), in section(s) 0, 3, 4, 5, 6, 7, 8, 9, 10
      every one of them at byte [2] of a 24-byte primitive
  /BIN/MODEL.BIN at 0x8016e800: 20 of 64800 byte(s) differ (99.97% equal), in section(s) 24, 32
      every one of them at byte [1, 2, 5, 9] of a 24-byte primitive
  ```

  Quatro coisas para começar por aqui, em vez de por uma varredura de RAM:

  1. **Cabeçalho e listas de ponteiro estão intactos nos dois arquivos** — só
     corpo de seção muda, e em posição de primitiva.
  2. **No `EDT_MOD.BIN` é sempre o byte 2 da primitiva de 24**, e em nove das
     vinte seções. Uma primitiva só, nas seções 1 e 2, não é tocada.
  3. **O `EDT_MOD.BIN` difere entre os dois states e o `MODEL.BIN` não**: 162
     corridas de diferença entre goleiro e jogador de linha no primeiro,
     **zero** no segundo. Isso é evidência direta sobre a incógnita (a) — mas é
     evidência de *quem é reescrito*, não ainda de *quem é desenhado*, e a
     distinção é a pergunta obrigatória desta fase.
  4. **`oracle.verify_load()` já devolve isso pronto** — offsets, seção de cada
     um e posição dentro da primitiva —, então o diff de `HAIR` do critério
     abaixo se compara contra uma linha de base que já existe.

---

## Objetivo

Decidir, por medição, qual dado o jogo está desenhando na tela `LOOKS SET`.

---

## Critério de conclusão

- [x] Carregar o state, tirar `snapshot_memory`, trocar `HAIR`, e rodar
      `diff_memory`: as regiões que mudam ficam listadas, com endereço e
      tamanho.
- [x] A medição é **repetida a partir do state recarregado**, e dá o mesmo
      resultado. Diff que não reproduz depois de `load_state` é ruído, não
      achado.
- [x] O mesmo diff é feito no **slot 1 e no slot 2**, e a comparação entre os
      dois diz o que é do boneco e o que é do uniforme.
- [x] Fica decidido, com a evidência ao lado, se o boneco vem do
      `EDT_MOD.BIN`, dos quatro TMDs, ou de uma combinação — e o que os quatro
      TMDs são, se não forem o boneco.
- [x] Se forem os TMDs: de onde eles vêm (qual arquivo, qual carga) fica
      medido, e o plano ganha a seção nova.
- [x] Se for o `EDT_MOD.BIN`: fica explicado **como a textura entra** numa
      geometria cuja primitiva não tem UV.
- [x] O resultado é escrito no plano **na seção que muda**, não num apêndice.

---

## Log de Execução

**Executado em:** 2026-09-14

### O veredito

**O boneco vem dos dois arquivos de modelo — `EDT_MOD.BIN` e `MODEL.BIN`,
cada um com uma parte — e de TMD nenhum.**

Trocar um campo na tela reescreve bytes **dentro** dos dois arquivos, nos
endereços de carga, de forma reprodutível; e **zero** bytes em qualquer TMD. A
medição é o comando novo `python tools/looks/oracle.py --fields`:

| campo | onde escreve | o que escreve |
| --- | --- | --- |
| `SKIN` | `EDT_MOD.BIN`, 5 a 7 seções, **mais** `MODEL.BIN` seção 24 | byte 2 — byte baixo do CLUT, `+0x40` por passo |
| `HAIR` | **só** `MODEL.BIN` seção 24, primitivas 1 e 14 | bytes 1, 5, 9, 13 — o `v` das quatro quinas, `+0x20` |
| `FACE` | **só** `MODEL.BIN` seção 24 | os mesmos bytes de `v` |
| `BODY` | **nenhum dos dois** | buffers de trabalho, não a geometria carregada |

E a pergunta que o critério exige que se responda de verdade — **"o veredito
distingue *medi e é isto* de *não achei o contrário*?"** — tem resposta pelos
dois lados. Não é só que nada apareceu nos TMDs: é que **apareceu**, com
endereço, nos dois arquivos de modelo, em campos que o hardware sabe nomear, e
com o passo aritmético certo para o que a tela mostra.

### Os quatro TMDs da §1.6 não existem nos dois states

`python tools/looks/oracle.py --tmds`:

```text
  slot 1 (goalkeeper):
      0x8016821c  000000000000000000000000   ALL ZERO
      0x80168c0c  000000000000000000000000   ALL ZERO
      0x8016a2c4  000000000000000000000000   ALL ZERO
      0x8016a650  000000000000000000000000   ALL ZERO
      TMDs actually in RAM: 29
          from 0x800c1678 to 0x800c4948, 4..54 vertices
```

Idêntico no slot 2. Os quatro endereços que o plano registrava estão **zerados**
nos dois; os TMDs que de fato vivem nessa tela são **29** pequenos, de 4 a 54
vértices, e **nenhum campo de LOOKS toca um deles**. Os de 92/261/30/18 vértices
foram medidos numa sessão que não se reproduz a partir dos states — registrados
agora no `layout.TMD_CLAIMED` **com essa ressalva ao lado**, que é o único lugar
onde um endereço deste ciclo pode morar.

> **"Nenhum campo toca um deles" era, nesta corrida, leitura de dois relatórios
> que não se cruzavam** — o `--tmds` acima e o `--fields`, que contava o resíduo
> como *"in no model file"*, coisa diferente de *"fora dos TMDs"*. A
> [`CORR-LOOKS-019`](/docs/tasks/looks/CORR-LOOKS-019.md) fez do cruzamento um
> comando em 2026-09-15: cada TMD percorrido até o fim (96..896 B cada, 13.104
> B ao todo) e o resíduo atribuído contra esse mapa — **0 bytes em TMD** para
> `HAIR` no slot 1 e `SKIN` no slot 2. A conclusão desta corrida não muda; o
> que passou a existir é a medição que a sustenta.

### A contradição da §1.6 era de leitura, e a primitiva **tem** UV

Este é o achado que vale mais que o veredito, e ele caiu do veredito.

Se `HAIR` muda o boneco inteiro mexendo em **8 bytes**, não é malha — é
**textura**. E de fato: lidos como quatro grupos de quatro bytes, os dezesseis
primeiros bytes da primitiva são a metade de textura de um `POLY_FT4`:

```text
step 0:  bc0f0178 bc011800 c70f0000 c7010000   indices 5 6 4 7
step 1:  bc2f0178 bc211800 c72f0000 c7210000   indices 5 6 4 7
```

- bytes 0, 1 = `u, v`; bytes 2, 3 = **CLUT id**; bytes 6, 7 = **página de
  textura**; os grupos 2 e 3 levam `u, v` e **dois zeros**.
- `HAIR` anda o **`v`** das quatro quinas: `0f/01` → `2f/21`, `+0x20`.
- `SKIN` anda o **byte baixo do CLUT**: `00` → `40` → `80` → `c0`, quatro
  valores — as quatro peles.

Três medições independentes, e nenhuma sozinha bastaria:

1. **Nos 2.841 primitivas dos dois arquivos**, os bytes 10, 11, 14 e 15 são zero
   **todas as vezes** — a forma do pacote, não o que quatro cores fariam.
2. O **"byte de modo"** que a `section.py` guardava desde a
   [`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md) — 120, 121, 122
   ou 127 na cor 0, zero nas outras — é `0x78..0x7F`, o byte **alto do CLUT
   id**. A estatística estava certa; a conclusão, não.
3. A palavra em 6..7 vale `0x18`, `0x1A` ou `0x99` — páginas em VRAM
   (512, 256), (640, 256) e (576, 256). **A primeira é o gráfico do `DAT2D.BIN`
   no offset 8.**

**Por que a leitura errada resistiu:** vinha do `we3d`, batia com uma estatística
real, e **nada no parser dependia de estar certa** — `section.py` lia 24 bytes e
fechava no EOF exato com a leitura errada. Só o jogo, reescrevendo esses bytes ao
vivo, desempatou. É o argumento do plano para a §5.3 inteira, e esta é a primeira
vez que ele paga.

Consequência em código: `Primitive` passou a ter `texcoords`, `clut` e `tpage` no
lugar de `colours` e `mode`, com `clut_vram` e `tpage_vram` derivando a posição
pela codificação do hardware. E ganhou controle negativo próprio,
`section-primitive-is-colours`, que repõe a leitura velha e exige vermelho.

### As duas listas do `EDT_MOD.BIN` são os dois bonecos

Os dois save states responderam de graça a pergunta que a task guardava:

```text
  SKIN, slot 1 (goalkeeper):  /BIN/EDT_MOD.BIN: list 1 owns section(s) [11, 16, 17, 18, 19]
  SKIN, slot 2 (outfield player):  /BIN/EDT_MOD.BIN: list 0 owns section(s) [0, 3, 4, 5, 6, 7, 8]
```

Interseção **vazia**. **Lista 0 é o jogador de linha, lista 1 é o goleiro**, e a
atribuição sai de `modelfile.read_models()`, não do olho: "seções 11 e 16 a 19" e
"a segunda lista" só são a mesma afirmação se alguma coisa conferir.

### Como o ruído foi separado do sinal — três filtros, e os dois primeiros não bastam

O `diff_memory` cru sobre a RAM inteira devolve **20.150 bytes** para um passo de
`HAIR`. Quase tudo é o jogo estar vivo.

1. **Subtrair um controle sem tecla** deixou 570 bytes em 102 regiões — melhor, e
   ainda display list.
2. **A/B/A** — `Right` e depois `Left`, guardando o que voltou ao valor antigo —
   deixou **4.248**. Pior do que parece: o boneco é **animado**, e byte periódico
   volta sozinho. A/B/A sozinho teria "achado" quatro mil bytes e qualquer
   narrativa caberia neles.
3. **Os dois juntos**, com o conjunto de ruído tirado em **três** passagens
   ociosas (uma passagem amostra uma fase da animação), deixam **132**.

Os três estão no `field_diff()`, com a razão de cada um escrita ao lado — porque
a tentação de ficar no primeiro é exatamente o que produziria um mapa plausível.

### Duas calibrações que quase mediram nada

- **A tecla `Down` não se confere pelo quadro inteiro.** Andar uma linha move a
  imagem toda em 0,0068 a 0,0215 — que se confunde com o que a animação do
  boneco faz nos mesmos 28 frames. Quem separa é o **rodapé**, que soletra o
  campo selecionado: as mesmas dez teclas movem 0,0086 a 0,0548 ali, e um par
  ocioso move 0,000000.
- **A célula de valor pisca.** `A1TYPE` → `A2TYPE` move a célula em 0,016759 —
  uma letra —, e a caixa amarela do cursor, com as setas nas pontas, movia
  0,005682 **sem tecla nenhuma**. Duas coisas resolveram: a caixa foi estreitada
  para os glifos do valor, e o `field_diff()` passou a **medir** a deriva ociosa
  antes de confiar no limiar, recusando em vez de medir se a região se mexer
  sozinha demais. Limiar entre dois números medidos é limiar; escolhido por
  parecer seguro é chute.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 8 file(s), 3651 line(s)
  controls: 0 failure(s)      ..... 11 of 11 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/modelfile.py --check-image   ->  ok
python tools/looks/oracle.py --check            ->  oracle.py: 0 failure(s)
python tools/looks/oracle.py --check-live       ->  oracle --check-live: 0 failure(s)
python tools/looks/oracle.py --fields HAIR SKIN FACE BODY  ->  exit 0
python tools/looks/oracle.py --tmds             ->  exit 0
python tools/check_tasks.py                     ->  123 task(s), ok
```

O décimo primeiro controle é novo e é deste achado: `section-primitive-is-colours` repõe
a leitura de "byte de modo" e o `section.py` tem de ficar vermelho.

`roms/` só foi lida. O disco inglês é o que o emulador boota, e dele não se leu
textura nenhuma — as seções vêm da japonesa, por `WE2002_LOOKS_IMAGE`.

### Arquivos criados/modificados

- `tools/looks/section.py` — a primitiva relida: `texcoords`, `clut`, `tpage`,
  `clut_vram`, `tpage_vram`; `build_section()` monta o pacote com a forma real;
  o `self_check()` afirma os zeros dos grupos 2 e 3
- `tools/looks/oracle.py` — `ROWS`, `select_row()`, `churn()`, `field_diff()`,
  `spans()`, `attribute()`, `lists_touched()`, `report_field()`, `check_tmds()`
  e os comandos `--fields` e `--tmds`; mais `FOOTER`/`ROW_MOVED` e a célula de
  valor por linha, com a deriva ociosa medida
- `tools/looks/layout.py` — `TMD_CLAIMED` e `TMD_MAGIC`, com a ressalva medida
- `tools/looks/controls.py` — o controle `section-primitive-is-colours`
- `docs/PLAN-LOOKS-PY.md` — §1.4 (a primitiva), §1.6 reescrita, §6 (a) e (d)
- `docs/tasks/looks/04-formato-de-secao.md` — a ressalva sobre a leitura que ela
  registrou
- `docs/tasks/looks/09-nomear-as-onze-pecas.md` — as duas listas com dono, a
  cabeça, e as duas faixas de buffer por nomear
- `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md` — a página de textura que as
  primitivas nomeiam
- `docs/tasks/looks/12-pele-paleta-ou-vertice.md` — o veredito de (d)
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 2
- `docs/tasks/looks/08-de-onde-vem-o-boneco.md` — este arquivo

### Problemas encontrados

- **`BODY` não escreve em nenhum dos dois arquivos** — 304 e 237 bytes, todos
  fora. É resultado legítimo e não buraco: altura e porte são transformação, não
  geometria guardada. Quem nomeia as duas faixas de buffer é a
  [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md), e a linha
  está escrita lá.
- **A §1.6 era a incógnita de maior risco do plano e caiu numa tarde**, mas pelo
  motivo errado de comemorar: ela nunca foi uma contradição nos dados, só na
  leitura deles. O que isso ensina para as fases seguintes é que **uma afirmação
  de terceiro que nenhum teste exercita não é conhecimento** — a leitura do
  `we3d` atravessou quatro tasks porque o parser fechava no EOF com ela.
- E o de sempre: `ctest -R looks` neste worktree responde `No tests were found!!!`
  e sai 0 ([`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md)); os gates
  acima saíram dos comandos da coluna do meio do
  [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
