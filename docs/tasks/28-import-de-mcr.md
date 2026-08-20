---
id: WTE-TASK-28
title: "Import e export de .mcr — memory card do PSX"
type: implementação
category: features
phase: 4
depends_on: ["WTE-TASK-08", "WTE-TASK-24", "WTE-TASK-27"]
status: pendente
---

# WTE-TASK-28: Import de `.mcr`

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.2.
- Segunda das quatro features. Permite trazer jogador de memory card para a
  imagem de CD — o `ed.exe` não faz.
- **Fase 4, não 5**, e a task carrega a gravação `boton_mcr2isoClick` — ver
  "A gravação mora aqui" abaixo.

| Handler | Endereço | Papel |
|---|---|---|
| `boton_mcrClick` | `0x0040c2c8` | abre o `.mcr` |
| `boton_mcr2isoClick` | `0x0040c46c` | **grava o jogador na imagem** — desta task desde 2026-08-19 |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` — **já implementado** na [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), e o layout de saída dele é insumo daqui |

### A gravação mora aqui, e o que veio com ela

*(decisão do usuário, 2026-08-19)*

Até 2026-08-19 o `boton_mcr2isoClick` era da
[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) — a gravação lá, a origem
dos bytes aqui. A divisão criava **ciclo**: a 27 não fechava sem esta task, e
esta declarava `depends_on` a 27. Agora a task que produz os bytes é a mesma que
os grava, e as duas features que estavam nessa situação subiram para a fase 4.

Com a gravação vieram as regras, e nenhuma delas é sobre o handler — são sobre
gravar **nesta imagem**:

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; preservar é o
  comportamento correto.
- **Fronteira de setor.** `2352 = 24 + 2048 + 280`, e os offsets pulam cabeçalho
  de setor à mão. Round-trip que falha: é a primeira suspeita.
- **Cópia, sempre.** Cada rodada de golden usa duas cópias de ~474 MB, e `roms/`
  nunca é alvo.
- **O diff de controle já está medido** e vale aqui igual:
  [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md). Gravar sem
  editar nada **muda** 22 bytes nesta ROM — katakana virando ASCII. Sem esse
  desconto, toda medição vem contaminada.
- **O clique não grava; quem grava é o `fseek` seguinte.** O `wte.exe` escreve
  pela saída bufferizada do runtime C, e um roteiro que **termina** numa
  gravação mede um oráculo truncado: o harness encerra com `wineserver -k` e o
  buffer se perde. Todo roteiro de gravação tem de terminar com uma troca de
  time — a descarga — e só então a marca de corte. Medido com o par
  [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt) /
  [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt); sem
  repetir isso aqui, o golden desta task nasceria com o defeito que a primeira
  passagem da 27 levou oito dias para achar.

O readme do original registra que a v0.98 corrigiu "the problem with the captain
and kickers when loading from .mcr files" e "the problem with the Eire's
goalkeeper" — sinal de que o mapeamento `.mcr` → imagem tem casos especiais.

---

## Objetivo

Ler, escrever e converter, com fixture reproduzível.

### O risco declarado, e a mitigação

**Pode faltar `.mcr` de teste variado.** Mitigação prevista no plano: o
`grabar_memoryClick` do próprio original **escreve** `.mcr`. Então dá para gerar
fixture — editar um jogador conhecido no original, exportar, e usar o arquivo
como entrada do teste de import.

`data/dat.bin` começa com `MC` e tem 145.408 bytes contra os 131.072 de um
memory card padrão. A WTE-TASK-08 já deve ter classificado o arquivo e explicado
os 14.336 de diferença; se não explicou, explicar aqui antes de usá-lo como
fixture.

### O formato

Memory card do PSX é parcialmente documentado publicamente — cabeçalho, tabela
de blocos, diretório. Usar a documentação pública para o **contêiner**, e
engenharia reversa só para o **conteúdo** do bloco do WE2002, que é específico
do jogo.

Essa divisão poupa a maior parte do trabalho.

### Os casos especiais

O readme aponta três, e cada um vira teste:

1. **Capitão e cobradores** ao carregar de `.mcr`
2. **Goleiro da Eire** — provável caso de índice fora do padrão
3. **Espaços no nome do jogador**

Um bug corrigido pelo autor é um caso que o formato tem; reproduzir a *correção*,
não o bug.

### Round-trip

Exportar do app e importar de volta tem de dar o mesmo estado. E exportar do app
vs. exportar do original, a partir do mesmo jogador, tem de dar o **mesmo
arquivo** — é o golden test desta feature.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/MainForm.boton_mcrClick.md` | preencher — feito |
| `wte/re/spec/MainForm.boton_mcr2isoClick.md` | criar — feito |
| `wte/re/mcr.md`, `wte/re/mcr.tsv` | criar — **gerados**, feito |
| `wte/re/mcr-medido.tsv` | criar — medição da fixture, feito |
| `wte/tools/dump_mcr.py`, `wte/tools/test_dump_mcr.py` | criar — feito |
| `wte/src/we2002_mcr.pas` | criar — feito (o leitor e o layout) |
| `wte/tests/test_mcr.pas` | criar — feito |
| `wte/tests/roteiros/golden-12-mcr2iso{,.port}.txt` | criar — **falta** |

*(2026-08-20)* A fixture **não é versionada**, e a decisão está escrita no
[`mcr.md`](../../wte/re/mcr.md): 128 KiB de nomes e atributos tirados da ROM são
dado do jogo, e este repositório não versiona dado do jogo — nem `roms/`, nem
`we-team-editor/`. O que entra no git é a **medição**; quem quiser refazer gera
o cartão com o próprio original, pelo roteiro
[`27-mcr.txt`](../../wte/tests/roteiros/27-mcr.txt). É o mesmo arranjo do
`work/ml-jp.bin` da [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md).

---

## Critério de conclusão

- [x] **Contêiner lido conforme documentação pública, com a fonte citada** —
      16 blocos de 8192, bloco 0 = cabeçalho `MC` mais 15 quadros de 128 B, e os
      códigos de estado do quadro (`0x51`/`0x52`/`0x53`/`0xA0`) pela *nocash PSX
      spec*, seção "Memory Card Data Format". O `dump_mcr.py` **lê** o diretório
      do molde em vez de supô-lo: o save se chama `BISLPM-86600WEW-OPT`
      (`SLPM-86600` é a japonesa do gate) e declara 16.384 bytes nos blocos 1 e 2
- [x] **Conteúdo do bloco do WE2002 mapeado** — 16 destinos, os dois lados
      (`0x0040f150` escreve, `0x0040b9ec` lê), em
      [`wte/re/mcr.md`](../../wte/re/mcr.md). Duas tabelas do `.exe` entram como
      guard: a de cobradores (`0x00423F84`) e a de deslocamentos de bit
      (`0x0042360C`), e o gerador recusa se qualquer uma deixar de bater
- [x] **Fixtures geradas pelo original, não à mão** — pelo roteiro `27-mcr.txt`,
      com a medição versionada em `wte/re/mcr-medido.tsv`: **489 bytes em 51
      faixas**, os mesmos números que a spec do `grabar_memoryClick` mediu, mais
      duas colunas novas — o diretório sai **intacto** e a escrita se reparte
      448 bytes no bloco 2 e 41 no bloco 3
- [ ] Os três casos especiais do readme cobertos por teste
- [ ] Round-trip export/import estável
- [ ] Export do app byte-idêntico ao export do original
- [ ] `boton_mcr2isoClick` com spec em
      `wte/re/spec/MainForm.boton_mcr2isoClick.md` e golden verde na ROM
      japonesa — gravação e origem dos bytes fecham na mesma task.
      **A spec está feita** (2026-08-20), com a recusa e os três caminhos de
      escrita mapeados; falta o Pascal e o golden
- [ ] **EDC/ECC preservados na escrita de setor inteiro — provado, não
      presumido.** É a única gravação do projeto que escreve setor completo, e a
      única em que preservar EDC/ECC é decisão e não consequência: as quatro da
      WTE-TASK-27 escrevem dentro do payload de 2048 B e não alcançam os 280
      bytes de correção
- [ ] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-20 — **primeira passagem, parcial.** Fecharam os
  **três primeiros** critérios: contêiner, conteúdo e fixture. A task continua
  `⬜ Pendente`; o que falta é Pascal e gate, não mapa.

- **Resumo do que foi feito:**

  **A divisão que o enunciado mandava fazer é real e poupou a maior parte do
  trabalho.** O contêiner saiu da documentação pública do memory card do PSX —
  16 blocos de 8192, bloco 0 com o cabeçalho `MC` e 15 quadros de diretório de
  128 B, códigos de estado `0x51`/`0x52`/`0x53`/`0xA0` — e o
  [`dump_mcr.py`](../../wte/tools/dump_mcr.py) **lê** o diretório do molde em
  vez de supô-lo. O save se chama `BISLPM-86600WEW-OPT`, e `SLPM-86600` é
  exatamente a ROM japonesa que o gate usa.

  **A pergunta do `dat.bin` fechou.** 145.408 bytes contra 131.072: a primeira
  metade é o cartão-molde, e os 14.336 restantes são os sete setores que a
  abertura injeta na imagem, já descritos na seção 8 do `assets.md`. O
  enunciado mandava responder isso antes de usar o arquivo como fixture.

  **O achado: 14 dos 16 destinos caem num bloco que o diretório declara
  LIVRE.** O save diz ocupar os blocos 1 e 2; jogadores e números de camisa vão
  para o 2, mas formação, tática e cobradores vão para o **3**, que o molde
  entrega zerado e marcado `0xA0`. E o escritor nunca toca o diretório — medido
  na fixture: sai intacto. O readme do original diz que a v0.98 consertou *"the
  problem with the captain and kickers when loading from .mcr files"*, e capitão
  e cobradores são exatamente campos do bloco 3. A coincidência está medida e
  escrita; o **veredito** — se o cartão emitido é válido para o console ou só
  serve de transporte entre cópias do editor — continua aberto.

  **A tática vai e não volta.** O escritor grava seis campos de tática; o leitor
  `0x0040b9ec` não lê nenhum deles. Quem lê tática de um `.mcr` é o
  `boton_mcr2isoClick`, direto do arquivo. Assimetria do original, não do port.

  **O `boton_mcr2isoClick` reusa, não reimplementa.** A spec ficou pronta: ele é
  um laço em volta da `0x00404820` e da `0x00404048`, as duas portadas e com
  golden verde desde a WTE-TASK-27. O único endereço novo é a formação. E a
  recusa dele é aritmética **antes** de gravar: conta quantos blocos de ML os 23
  slots precisariam e recusa os 23 de uma vez, em vez de gravar meio time e
  parar no meio.

- **Arquivos criados/modificados:**
  - criados: `wte/tools/dump_mcr.py`, `wte/tools/test_dump_mcr.py`,
    `wte/re/mcr.md` (gerado), `wte/re/mcr.tsv` (gerado),
    `wte/re/mcr-medido.tsv` (medido),
    `wte/re/spec/MainForm.boton_mcr2isoClick.md`,
    `wte/src/we2002_mcr.pas`, `wte/tests/test_mcr.pas`
  - modificados: `wte/re/spec/MainForm.boton_mcrClick.md` (o mapa do leitor),
    `wte/re/spec/INDICE.md`, `wte/tools/README.md`, `wte/tests/README.md`,
    `wte/src/impl/ep2002_mainform.aux.inc` (as constantes do cartão saíram),
    `ep2002_mainform.uses`, `wte/src/ep2002_mainform.pas` (regerado)

### A segunda metade da passagem: o Pascal do formato

- **`wte/src/we2002_mcr.pas`**, com o layout e o **leitor** — a `0x0040b9ec`.
  As constantes do cartão **mudaram de casa**: estavam no `.aux.inc` do
  `MainForm`, escritas pela WTE-TASK-27 para o escritor, e agora moram na
  unidade do formato. Leitor e escritor precisam dos mesmos endereços, e ter
  duas cópias seria ter duas verdades.
- **O `dump_mcr.py` passou a conferir o Pascal.** Ele não gera o
  `we2002_mcr.pas` — a prosa dele veio da leitura do disassembly e gerador
  nenhum a produziria —, mas lê as constantes do fonte e as compara com o
  layout, do jeito que o `check_lcl_props.py` confere o que não gera. A recusa
  foi **vista**: com `MCR_CAPITAO` plantado em `$6501` o guard reprova, e o
  teste planta.
- **`wte/tests/test_mcr.pas`**, e a terceira ponta. Além dos invariantes sem
  cartão (contêiner, aritmética de 5 bits, índice fora da faixa), ele lê um
  cartão de verdade e confronta com o que o Python leu do **mesmo** arquivo:
  formação, cobradores e os 23 dorsais. E há um caso que não é do Pascal — a
  fixture reproduz os números que a spec do `grabar_memoryClick` mediu quando
  aquele handler foi portado, uma task atrás. Layout errado não os
  reproduziria.

**O que a aritmética de 5 bits precisava provar, e prova:** o sexto jogador de
cada grupo começa no bit 1 do quarto byte e **não vaza** para o grupo seguinte
— são os 2 bits perdidos por grupo que garantem isso, e é o tipo de erro que
passa despercebido porque só o 6º, 12º, 18º de cada grupo sairiam errados.

- **O que ficou pendente, e é o grosso:**
  - o Pascal do `boton_mcrClick` e do `boton_mcr2isoClick` — a unidade que os
    alimenta já existe;
  - o golden do `boton_mcr2iso` e a prova de EDC/ECC na escrita de setor
    inteiro;
  - os três casos especiais do readme e o round-trip.

- **Problemas encontrados:**
  - **A fixture não pode ser versionada, e isso precisou de decisão.** São
    128 KiB de nomes e atributos tirados da ROM — dado do jogo, e este
    repositório não versiona dado do jogo. Ficou em `work/`, com a **medição**
    versionada em `mcr-medido.tsv`; é o mesmo arranjo do `work/ml-jp.bin` da
    [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md).
  - O markdown gerado saía com título e tabela colados no parágrafo anterior. O
    corpo é escrito em blocos curtos, um `w()` por parágrafo, e lembrar de um
    `\n` solto em cada um dos quarenta seria a forma conhecida de esquecer um:
    o gerador passa a saída por uma função que põe a linha em branco onde o
    markdown precisa dela.
