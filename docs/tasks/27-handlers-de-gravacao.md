---
id: WTE-TASK-27
title: "Handlers de gravação — escrever na imagem de CD"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-26"]
status: concluído
---

# WTE-TASK-27: Handlers de gravação

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4 e §6.
- **O grupo mais arriscado do projeto.** É onde o app toca 474 MB de imagem
  in-place, e é o único grupo que o golden test mede diretamente e sem
  ambiguidade.

Vêm por último de propósito: dependem de carga e edição estarem certas.

---

## Objetivo

Implementar as quatro gravações que não dependem de fórmula, cada uma com golden
verde antes de passar para a seguinte.

### Alvos

| Handler | Endereço | O que grava |
|---|---|---|
| `boton_nombres2isoClick` | `0x0040d534` | nomes na imagem |
| `boton_barras2isoClick` | `0x0040cab8` | barras/atributos |
| `boton_tex2isoClick` | `0x0040de18` | textura |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` (saída, não a imagem) |

### A quinta gravação não é um botão

*(medido em 2026-08-19)*

| Handler | Endereço | O que grava |
|---|---|---|
| `MainForm.dorsalClick` | `0x00410a74` → `0x00404048` | o número de camisa, escrita **pontual** |

O `dorsalClick` é handler de **edição** — é da tabela da
[WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) —, mas ao fechar o modal
ele escreve o número na imagem. A 26 fechou com ele e mais oito `aberto`, de
dono nomeado aqui, pela **opção A**: implementar a gravação lá misturaria duas
causas possíveis num golden vermelho.

**São nove ao todo, e esta task os promove:** o `dorsalClick` e os oito de
mover jogador, cuja metade de escrita é a `0x00404820`. O primeiro fechou.

### As outras duas gravações não moram aqui, e a razão é o ciclo

*(decisão do usuário, 2026-08-19)*

`boton_mcr2isoClick` (`0x0040c46c`) e `grabar_camisetaClick` (`0x0040ee80`)
também gravam na imagem, e até 2026-08-19 esta task era dona deles. Não é mais:
o primeiro é da [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) e o segundo da
[WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md).

O motivo é que a divisão anterior — gravação aqui, origem dos bytes lá — criava
um **ciclo**: esta task não fechava sem o parser de `.mcr` e o render 2D, e as
duas tasks que os entregam declaravam `depends_on` esta. A regra de seleção põe
fase antes de número, então a 27 pendente seria escolhida para sempre. Cada uma
das duas passou a **carregar** a gravação que ela viabiliza, e as duas subiram
para a fase 4 — a mesma forma como a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez o ciclo do gate e como a
[WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) entregou o critério de byte
para cá.

O que foi junto: as regras da próxima seção, o diff de controle, e a armadilha
da descarga bufferizada. Nenhuma delas é sobre o handler — são sobre gravar
nesta imagem —, e sem repeti-las lá o golden daquelas tasks nasceria com o
defeito que a primeira passagem daqui levou oito dias para achar.

### Regras que não podem ser violadas

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; preservar é o
  comportamento correto.
- **Fronteira de setor.** Os offsets pulam cabeçalho de setor manualmente
  (2352 = 24 + 2048 + 280). Se um round-trip falhar, é a primeira suspeita.
- **Cópia, sempre.** Cada rodada de golden usa duas cópias de ~474 MB.

### O diff de controle vem antes

Como na WTE-TASK-19: gravar **sem editar nada** nos dois lados e registrar o que
muda de graça. O `Save` reconstrói as all-star a partir dos links, e sem esse
controle toda medição vem contaminada.

> A segunda armadilha que esta linha citava — o `Load`+`Save` trocando os dois
> primeiros cobradores de cada clube de ML — é do **`ed.exe`**, e chegou aqui
> junto com a frase da WTE-TASK-19. Medido pela
> [CORR-WTE-109](/docs/tasks/CORR-WTE-109.md) em 2026-08-25: o `wte.exe` não a
> tem em nenhum dos dois caminhos que tocam `OFS_KICKER`.

### Critério

**Byte-idêntico** entre `wte.exe` e o app Lazarus, nas duas ROMs, para cada
operação. Divergência que sobreviver à análise vira **divergência deliberada**
com registro (WTE-TASK-35) — nunca "aceita e esquecida".

### A metade da WTE-TASK-26 que esta task herdou

*(decisão do usuário, 2026-08-12)*

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) edita **em memória** e não
grava; o critério dela dizia "editar pela tela nos dois lados, então gravar nos
dois, e o golden compara". O segundo verbo é desta task — as barras editadas lá
só chegam à imagem pelo `boton_barras2isoClick`, os nomes pelo
`boton_nombres2isoClick` —, e a 27 `depends_on` a 26. Circularidade da mesma
forma que a [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para o gate.

**A 26 passou a fechar por conferência de tela e esta task herdou o byte.** Na
prática: cada uma das quatro gravações roda o golden **duas** vezes —

1. **gravar sem editar** (o diff de controle da seção acima);
2. **editar pela tela, com um handler do grupo da 26, e então gravar.**

A segunda é a que julga a edição e a gravação juntas. Sem ela, a edição fica
verificada só por pixel, e pixel igual dos dois lados não prova que os dois
escreveram o **mesmo byte do modelo** — os dois poderiam desenhar a mesma
largura a partir de campos diferentes. É a lição da terceira ponta da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md).

Par mínimo por gravação, quando existir handler de edição correspondente:

| gravação | edição que a exercita (WTE-TASK-26) |
|---|---|
| `boton_barras2isoClick` | `sel_barraClick` + `track_barraChange` |
| `boton_nombres2isoClick` | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick` |
| `grabar_memoryClick` | os de número (`dorsalClick`, `scroll_dorsalChange`) |

`boton_tex2isoClick` não tem par na 26: a fonte dele é um arquivo externo, não
um campo de tela.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/MainForm.*.md` | criar (12) — as quatro gravações, o `dorsalClick` e os sete de mover |
| `wte/src/impl/ep2002_mainform.*.inc`, `wte/src/we2002_estado.pas`, `wte/src/we2002_ml.pas` | modificar |
| `wte/tests/roteiros/golden-NN-*.txt` + `.port.txt` | criar (21) — o roteiro do gate, em arquivo fixo |
| `wte/tests/roteiros/27-*.txt` | criar (9) — as sondas |

*(2026-08-20)* A tabela era do enunciado de 2026-08-11 e citava
`wte/tools/roteiros/gravacao-*.sh`. **O roteiro virou arquivo declarativo**, não
script de shell: driver que reage à tela muda o estímulo quando um lado diverge,
e aí os dois lados deixam de receber a mesma entrada.

---

## Critério de conclusão

- [x] Diff de controle medido e registrado antes de qualquer edição
      — 2026-08-18, em [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md),
      gerado. Gravar sem editar **muda** 22 bytes: katakana virando ASCII
- [x] As quatro com spec e com golden verde — 2026-08-19
      (`boton_barras2iso`, `boton_nombres2iso`, `boton_tex2iso`,
      `grabar_memory`). **Só na ROM japonesa**, e o limite é medido, não
      omissão: com a europeia o `wte.exe` morre na troca de time e a gravação
      nunca acontece, então não existe oráculo daquele lado
- [x] **Cada gravação que tem par na WTE-TASK-26 rodada também com uma edição
      de tela antes** — herdado da 26 em 2026-08-12. É o único critério do
      projeto que julga edição e gravação juntas, e os três pares fecharam:

      | gravação | edição antes | gate |
      |---|---|---|
      | `boton_barras2iso` | `sel_barraClick` + `track_barraChange` | `golden-04-barras-editada` |
      | `boton_nombres2iso` | os três `edit_nombreNKeyPress` | `golden-05-nomes` |
      | `grabar_memory` + `dorsalClick` | `dorsalClick` + `scroll_dorsalChange` | `golden-08-dorsal-mcr` |

      O terceiro julga **duas** gravações numa corrida: a escrita pontual do
      número na imagem e o `.mcr`, que lê os 23 `dorsalN` da tela. O número é o
      único campo do cartão que não vem do disco nem do molde
- [x] **Os handlers de mover promovidos** — a outra metade da opção A da
      WTE-TASK-26. **Seis dos sete**, e o sétimo não depende desta task. O
      enunciado dizia "oito" e o índice de specs diz **sete**
      (`paderecha`, `paizquierda`, `paderecha2`, `paizquierda2`,
      `paderechaeizquierda`, `parriba`, `pabajo`) — a contagem antiga somava o
      `dorsalClick`, que é o nono da lista da WTE-TASK-26 e fechou na sétima
      passagem.

      A metade de escrita é a `0x00404820`, e ela fechou em três etapas, cada
      uma com controle byte-idêntico antes:

      | ramo | quando | gate |
      |---|---|---|
      | destino de seleção | 2026-08-19 | [`golden-09-mover`](../../wte/tests/roteiros/golden-09-mover.txt) |
      | destino de ML, libera bloco | 2026-08-20 | [`golden-10-mover-ml`](../../wte/tests/roteiros/golden-10-mover-ml.txt) |
      | destino de ML, aloca bloco | 2026-08-20 | [`golden-11-descarte-ml`](../../wte/tests/roteiros/golden-11-descarte-ml.txt) |

      Os três **byte-idênticos, sem faixa declarada** — o que só passou a ser
      possível quando os dois remendos de arranque foram portados.

      **O `parriba` continua `aberto`, e não é desta task:** ele não grava. O
      que falta nele é régua de tela — o `compara_tela.sh --edicao` não alcança
      a lista de descarte —, e já estava assim antes
- [x] EDC/ECC preservados **nas gravações desta task** — 2026-08-20,
      **148 faixas conferidas em 11 sessões**, nenhuma tocando byte de EDC/ECC
      nem de cabeçalho de setor. As três sessões novas são as de Master League
      da oitava passagem, e a conta as absorveu sozinha: ela enumera pelo
      prefixo `27-`, então sonda nova entra sem ninguém somar nada. A conta é do
      [`gravacao_controle.py`](../../wte/tools/gravacao_controle.py), sobre o
      `cmp-medido.tsv` que as corridas já versionaram — não precisou de medição
      nova. A forma forte do critério migrou inteira para a
      [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md), onde a pergunta é real:
      o `boton_mcr2iso` é a única gravação do projeto que escreve setor
      completo, e ali preservar EDC/ECC é decisão, não consequência
- [x] Nenhuma divergência sem veredito escrito — são **três**, todas da mesma
      família e todas na spec do handler que as tem: o port também atualiza
      `Jogo` ao gravar (barras, número), e lê nome e atributos da camada de
      dados em vez de reler a imagem (cartão). O `wte.exe` relê a imagem a cada
      troca de time; o port carrega uma vez, e sem isso a tela dele discordaria
      do próprio arquivo. Mesmo byte, mesma posição, outra fonte — nenhuma
      aparece no gate. Vão para o registro central na
      [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md)
- [x] `roms/` intocada em todas as rodadas — vale por passagem, e a de
      2026-08-18 rodou toda sobre cópia em `work/`
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-20 — **oitava passagem, em duas metades.** A
  segunda começou onde a primeira parou: o bloqueio do gate de alocação era a
  escrita de arranque em `2012984`, sem autor desde a WTE-TASK-25. Ela tem
  autor agora, e o remendo está portado.

### A segunda metade: os dois remendos de arranque

**Estavam escondidos à plena vista.** `0x0040c19e` no `boton_dialogo_weClick` e
`0x00411616` no `FormShow`, com o endereço **imediato** no `.text`
(`push 0x1eb738`, `push 0x1d5346`). Toda busca anterior partia do nome do
offset — e a única referência a `OFS_LINK_ML` em toda a `.text` é o
`push 0x1eb608` da rotina de contagem, que só lê. Procurar por nome nunca
acharia um literal.

Dois detalhes que só o disassembly dá:

- **Ficam fora da guarda da sentinela.** O `je` de `0x0041158e`, que pula a
  injeção de sete setores quando a imagem já foi injetada, salta justamente
  para `0x00411616` — onde os remendos começam. Rodam em toda abertura.
- **Não estão nos mesmos dois lugares.** O `FormShow` faz os dois; o
  `boton_dialogo_weClick` faz só o do vínculo. O port reproduz isso: o do
  vínculo no `AbreImagem`, que os dois caminhos usam; o do byte solto no corpo
  do `FormShow`.

O do vínculo é **conserto de dado**: o par `(102, 23)` do slot 13 do clube de
ML 5 aponta para um bloco do time 102, e o time 102 não tem jogador
*non-contract* nenhum. Mandá-lo para `(0, 27)` o aponta para o bloco 4. O do
byte solto grava zero em `1921862` e **continua sem significado** — portá-lo
assim é legítimo porque a especificação está completa (endereço fixo, sem
condição, valor zero); o que não se pode é inventar-lhe um nome.

**Duas quase-descobertas anteriores.** O `offsets.md` já listava `2012984`
como candidato `imm32` com duas ocorrências — que são exatamente estes dois
`push` —, e o log da WTE-TASK-19 já registrava `1921862` entre os candidatos
extraídos do `.text`. As duas evidências estavam em tabelas geradas há meses;
ninguém as tinha ligado à faixa que o gate declarava.

**Consequência imediata: nenhum roteiro do gate declara faixa `conhecida:`
mais.** As doze declarações saíram, pela própria regra que as sustentava — o
`golden_veredito.py` reprova (código 3) declaração que não aparece. E o
`golden-10-mover-ml` foi refeito nessa condição: **PASSOU: byte-idêntico**,
sem exceção nenhuma.

### O gate de alocação, e as duas ordens de clique que não serviam

Com o remendo portado, os dois lados passaram a ter o **mesmo** conjunto de
blocos livres — que era a condição de o ramo de alocação poder ser medido. O
roteiro, porém, precisou de três tentativas, e as duas primeiras ensinaram
coisas diferentes:

1. **Linha do descarte clicada DEPOIS do `parriba`.** O handler lê o
   `ItemIndex` da lista de descarte para escolher o buffer; com `-1` o original
   carrega o buffer `-1 + 3 = 2` — o do lado direito — e grava a partir de um
   buffer que ninguém preencheu. O port, que tem guarda, não grava nada. Um
   lado gravando lixo e o outro nada não é gate. De quebra, isso **observou em
   execução** a divergência deliberada que a spec do `parriba` declarava desde
   a WTE-TASK-26 e que ninguém tinha visto acontecer.
2. **Só o `lista_equipos_1`, sem o combo principal.** São dois combos e os dois
   importam: o `lista_equipos` do alto é quem **carrega** o time (sem ele o
   painel fica vazio e quase nada é lido do disco), e o `lista_equipos_1` é
   quem o `parriba` **lê**. Com só o de baixo, nenhum dos dois lados grava.

A ordem que serve está no cabeçalho de
[`27-descarte-ml.txt`](../../wte/tests/roteiros/27-descarte-ml.txt), e o
diagnóstico saiu do `port-trace.log`: o `pabajoClick` aparecia lá e a execução
**parava** logo depois — sinal de `ShowModal`, não de `Exit`.

Com a terceira ordem, os dois lados alocam o **bloco 350** — vínculo em
`2012730`, nome em `2010092`, atributos em `2208920`, custo em `3069862` —, e o
`golden-11-descarte-ml` fecha **byte-idêntico**.

### O que esta metade fechou

| gate | resultado |
|---|---|
| `golden-10-mover-ml` (refeito, sem faixa declarada) | **PASSOU: byte-idêntico** |
| `golden-11-descarte-ml` controle | **PASSOU: byte-idêntico** |
| `golden-11-descarte-ml` golden | **PASSOU: byte-idêntico** |
| `golden-09-mover` (refeito, sem faixa declarada) | **PASSOU: byte-idêntico** |

Com o `pabajo` promovido, **seis dos sete** handlers de mover estão
`implementado`. O `parriba` fica, e o motivo não é desta task: ele não grava, e
o que falta nele é o `compara_tela.sh --edicao` alcançar a lista de descarte.

**A lição que vale para a próxima:** a busca por um endereço que o binário usa
tem de cobrir o **literal**, não só o nome. As duas faixas ficaram três tasks
sem autor porque toda tentativa partia de `OFS_LINK_ML`, e o `.text` nunca
menciona `OFS_LINK_ML` ali — menciona `0x1eb738`. As duas evidências que
bastavam já estavam em tabelas geradas (`offsets.md` listava `2012984` como
`imm32` com duas ocorrências; o log da WTE-TASK-19 listava `1921862` entre os
candidatos do `.text`) e ninguém as cruzou com a faixa que o gate declarava.

- **Arquivos da segunda metade:**
  - criados: `wte/tests/roteiros/golden-11-descarte-ml{,.port}.txt`
  - modificados: `wte/src/we2002_estado.pas` (os dois remendos),
    `ep2002_mainform.FormShow.inc`, os **doze** roteiros que declaravam faixa,
    `wte/tests/roteiros/README.md`, `27-descarte-ml.txt`,
    `wte/re/spec/MainForm.{boton_dialogo_weClick,pabajoClick,parribaClick}.md`,
    `wte/re/spec/INDICE.md`, `wte/tools/conta_ml.py` (e as saídas),
    `docs/tasks/25-handlers-de-carga.md`,
    `docs/tasks/33-slots-de-master-league.md`, `docs/PLAN-WTE-LAZARUS.md` §4.4

- **Problemas da segunda metade:**
  - **Três ordens de clique até o roteiro medir a rotina** — ver acima. Vale
    guardar o sintoma: handler que aparece no trace e **nada depois dele** é
    `ShowModal`, não `Exit`; um `Exit` deixa o trace continuar.
  - **Tirar as declarações é obrigatório, não opcional.** O
    `golden_veredito.py` reprova (código 3) faixa declarada que não aparece —
    então portar a escrita e deixar a declaração quebraria os doze roteiros de
    uma vez. A regra estava escrita e serviu exatamente para o que foi feita.

---

- **Executado em (primeira metade):** 2026-08-20 — **oitava passagem.** O ramo de destino de
  Master League da `0x00404820` foi portado e **um** dos seus dois caminhos
  fechou com golden verde. Cinco dos sete handlers de mover foram promovidos; a
  task continua `⬜ Pendente` por dois, e agora cada um tem motivo escrito e
  medido.

- **Resumo do que foi feito:**

  **O destino de Master League grava outra coisa, e é isso que separa as duas
  metades.** No destino de seleção o slot guarda um jogador e a gravação põe 10
  bytes de nome, 12 de atributos e o condicional em cima dele. No destino de ML
  o slot guarda um **par de vínculo de dois bytes** e o que se move é para onde
  ele aponta — daí quatro saídas onde a outra metade tem uma, e daí a
  necessidade do vetor de ocupação vivo, que é o mesmo que a
  [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) enche.

  **As três colunas de offset de um bloco de ML caem em offsets já nomeados.**
  Para o bloco 0 o nome dá 2006288 = `OFS_ML_PLAYER_NAME`, os atributos dão
  2204112 = `OFS_ML_PLAYER_ATTR` e a base do terceiro **é** `OFS_COST_NC`. A
  última reenquadra o campo: para bloco de ML o `+0x28` do buffer não é
  condição nenhuma — é o **custo** do jogador *non-contract*. O `OFS_COST_NC`
  estava `confirmado` no `offsets.tsv` com a evidência
  `0x004046b9|0x00404b66`, que são exatamente as duas instruções envolvidas; o
  que faltava era saber de quem elas eram.

  **A coluna do vínculo se confirma sozinha, sem gravar nada.** A fórmula
  `46*time + 2*slot + 9086 - 1520*(time div 95)`, lógica sobre o setor 850, dá
  2012728 para o time 63 slot 0 (= `OFS_LINK_ML1`) e 2012680 para o time 95
  slot 0 (= `OFS_LINK_ML`). Dois offsets já versionados, dois acertos.

  **O `TrocaEmCurso` ganhou leitor.** O `BYTE[0x00423169]` que o
  `paderechaeizquierdaClick` liga e desliga era, no port, um sinalizador sem
  ninguém que o lesse. Ele existe para calar o aviso modal (`ficha_info4`) que
  o ramo de ML mostra quando o bloco largado ainda tem outros donos — e numa
  troca o aviso subiria duas vezes, uma por gravação.

- **O que fechou, medido:**
  - `golden-10-mover-ml` controle: **PASSOU: byte-idêntico**;
  - `golden-10-mover-ml` golden: **PASSOU**, só as duas faixas declaradas. O
    caminho exercitado é o de `0x00404d73` — o único do programa que **devolve**
    bloco —, e os dois lados escrevem os mesmos 2 bytes em 2012734..2012735;
  - cinco specs promovidas a `implementado`: `paderecha`, `paizquierda`,
    `paderecha2`, `paizquierda2`, `paderechaeizquierda`.

- **O que NÃO fechou, e é achado, não pendência vaga:**

  **O ramo de alocação não pode ser gated hoje, e a causa foi medida.** Ele é o
  único que pede origem do tipo 3, e só buffer de descarte tem isso — ou seja,
  só o `pabajo` chega lá. O alocador pega o **primeiro** bloco livre, e os dois
  lados não têm o mesmo conjunto de livres: a escrita de arranque em `2012984`,
  que esta task já declarava `conhecida:` e cujo autor continua sem nome, troca
  `(102, 23)` por `(0, 27)` e com isso ocupa o bloco 4.

  Medido com a sonda `27-descarte-ml.txt`: o oráculo alocou o bloco **350** —
  vínculo em 2012730, nome em 2010092, atributos em 2208920, custo em 3069862.
  O port, partindo da tabela limpa, escolheria o **4**. Não é divergência da
  rotina: é a mesma rotina sobre estados diferentes.

  Isso promove a pergunta de `2012984` de curiosidade a **bloqueio**. Ela já
  tinha ganhado significado na WTE-TASK-33 (são dois bytes de um par de
  vínculo); agora tem consequência.

  O `parriba` continua `aberto` pelo motivo antigo e alheio a esta task: ele
  não grava, e o que falta nele é o `compara_tela.sh --edicao` alcançar a lista
  de descarte.

- **Arquivos criados/modificados:**
  - criados: `wte/tests/roteiros/27-mover-ml.txt`,
    `wte/tests/roteiros/27-descarte-ml.txt`,
    `wte/tests/roteiros/golden-10-mover-ml{,.port}.txt`
  - modificados: `wte/src/impl/ep2002_mainform.aux.inc` (o
    `GravaJogadorEmMl`, o `GuardaVinculoNoModelo`, as duas famílias de offset e
    as constantes), `ep2002_mainform.uses`, `wte/src/ep2002_mainform.pas`
    (regerado), `wte/src/we2002_ml.pas` (vetor de ocupação vivo,
    `IndiceDoBlocoMl`, `ParDoIndiceLinearMl`, `PrimeiroBlocoLivreMl`), seis
    specs, `wte/re/spec/INDICE.md`, `wte/re/{cmp,io}-medido.tsv`,
    `gravacao-controle.md`, `offsets-novos.md`, `fase-2.md` (todos regerados),
    `docs/PLAN-WTE-LAZARUS.md` §4.4

- **Problemas encontrados:**
  - **A previsão do bloco alocado errou, e o erro foi o achado.** A conta dizia
    bloco 4; o oráculo pegou 350. Refazer a conta *sobre a imagem que o oráculo
    produziu* — e não sobre a ROM limpa — deu 350 na hora. A lição é a mesma da
    WTE-TASK-33: comparar número, não procedência.
  - **O enunciado dizia "oito handlers de mover" e são sete.** A contagem
    antiga somava o `dorsalClick`, que é o nono da lista da WTE-TASK-26 e
    fechou na sétima passagem. Corrigido no critério.
  - O combo de time do lado direito precisa de **64** `Down` para alcançar o
    primeiro clube de ML, e uma rajada sem espera perde evento: cada tecla
    dispara o `lista_equipos_2Change`, que repovoa a lista de jogadores. Os
    roteiros novos os dão em blocos de dez, com espera entre eles.

---


- **Executado em:** 2026-08-18 — **primeira passagem, parcial.** A tarefa
  continua `⬜ Pendente`: nenhuma das seis gravações foi implementada. O que
  fechou foi a primeira linha do critério, o **diff de controle** — e ele
  mudou o desenho de todo roteiro de gravação que vier depois.

- **Resumo do que foi feito:**

  Três coisas, e a segunda vale mais que as outras duas juntas.

  **O diff de controle está medido e registrado.** Carregar um time e mandar
  gravar sem tocar em campo nenhum **não** é neutro nesta imagem: a ROM
  japonesa guarda o nome do time em latino no primeiro bloco e em katakana de
  meia largura nos demais, e o editor lê o campo da tela — que veio do bloco
  latino — e o grava em **todos**. Vinte e dois bytes mudam de graça, em três
  trechos, e são katakana virando ASCII. Reproduzir isso é obrigação: um port
  que "preservasse" o katakana divergiria do oráculo em toda gravação de nomes,
  e o golden acusaria a gravação por um defeito que seria de fidelidade.

  A medição é a sessão `27-gravacao-controle` do `diff_dirigido.sh`, e o
  registro é gerado — [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md),
  do novo [`gravacao_controle.py`](../../wte/tools/gravacao_controle.py), que
  **não mede nada sozinho**: cruza as duas réguas já versionadas. Os offsets
  desta medição são a seção `Bytes tocados` das seis specs que vêm, e
  copiá-los à mão de dois TSV seria a forma conhecida de o número envelhecer
  calado.

  **O clique não grava — quem grava é o `fseek` seguinte.** O `wte.exe` escreve
  pela saída bufferizada do runtime C. A primeira medição desta passagem disse
  que o `boton_barras2iso` **não tocava a imagem**, e o TSV de uma sessão
  anterior (`09-areas-com-time`) dizia o mesmo desde 2026-08-10. Estava errado
  nos dois: ele grava 5 bytes, que ficam no buffer até algo depois procurar
  noutro ponto do mesmo arquivo.

  Medido com um par de sondas de **uma** variável de diferença, agora
  versionadas — [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt)
  e [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt),
  iguais linha a linha, e o `-com` troca de time depois do clique: **zero**
  escrita no `-sem`, os 5 bytes em 2328184 no `-com`. O
  `test_gravacao_controle.py` compara os dois corpos e exige que o resultado
  medido continue oposto, como o `test_analisar_crash.py` faz com o par 07/08.

  Duas consequências, e as duas são armadilha de gate:

  1. **roteiro que termina numa gravação mede um oráculo truncado** — o harness
     encerra com `wineserver -k` e o buffer se perde. Se o port gravar direto,
     o golden acusaria o *port* por bytes que o oráculo nunca escreveu;
  2. **marca de corte antes da descarga credita a faixa à ação seguinte.** Na
     primeira corrida os 5 bytes das barras apareceram como se fossem dos
     nomes — atribuição errada, em silêncio, num TSV que parecia medido.

  Por isso cada bloco do `golden-02-gravacao.txt` termina com uma troca de time
  e só então a marca. Refeita a corrida, a atribuição fecha: barras 5 bytes,
  nomes 8 faixas.

  **A primeira régua não tinha porta automática, e ninguém tinha notado.** A
  [CORR-WTE-047](/docs/tasks/CORR-WTE-047.md) deu ao `cmp` um `--fundir-cmp`
  porque o `cmp.tsv` morria em `/tmp`; o **trace** tinha a mesma doença e
  chegava ao `io-medido.tsv` a mão, o que é indistinguível de não chegar quando
  alguém esquece. As 75 faixas desta sessão não entrariam sozinhas. Entrou
  `--fundir-io`, simétrico, chamado pelo `diff_dirigido.sh`.

- **O que a passagem NÃO fez, e é o resto da task:**
  - as seis gravações continuam sem spec e sem Pascal. O
    `boton_nombres2isoClick` foi lido até o ponto de se saber que ele valida os
    três campos de nome antes de gravar (vazio em 1 e 2, menos de 3 letras em
    3) e que endereça oito faixas; isso ainda **não** é spec;
  - o par edição+gravação (o critério herdado da WTE-TASK-26) não rodou: sem
    gravação implementada não há o que comparar;
  - EDC/ECC preservados continua **presumido**, não provado.

- **A ROM europeia não hospeda este grupo, e agora está medido aqui.** O mesmo
  roteiro sobre `roms/golden-european-deluxe.bin` morre na troca de time —
  49.749 violações de acesso, o número que a
  [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) já tinha medido — e a caixa de
  confirmação da gravação nunca aparece. O critério "nas duas ROMs" da task
  herda esse limite; ele não é omissão desta passagem.

- **Arquivos criados/modificados:**
  - `wte/tests/roteiros/golden-02-gravacao.txt` — o roteiro do controle
  - `wte/tests/roteiros/27-descarga-{sem,com}.txt` — o par de sondas
  - `wte/tools/gravacao_controle.py`, `wte/tools/test_gravacao_controle.py`
  - `wte/re/gravacao-controle.md` — gerado
  - `wte/tools/analisar_io.py` (`--fundir-io`), `wte/tools/test_analisar_io.py`
  - `wte/tools/diff_dirigido.sh` — funde as duas réguas
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv`, `wte/re/offsets-novos.md`
  - `wte/tools/README.md`, `wte/tests/roteiros/README.md`
  - `docs/tasks/progresso.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` **PASSOU: byte-idêntico**
  e `--modo positivo` **detectou** o byte plantado em 405228, os dois sobre o
  roteiro final; `make -C wte check` rc 0, com **590 testes** OK; `lazbuild`
  rc 0. As duas réguas do `diff_dirigido.sh` fecham nas três sessões novas
  (12/12, 9/9, 9/9). `roms/` intocada — todas as corridas sobre cópia em
  `work/`.

- **Problemas encontrados:** o descrito acima — a leitura de que o
  `boton_barras2iso` "não grava" era artefato de buffer, e sobreviveu por oito
  dias num TSV versionado porque nada exercia a descarga. Foi preciso desmontar
  a atribuição do próprio instrumento antes de confiar em qualquer número desta
  task.

---

- **Executado em:** 2026-08-18 — **segunda passagem, ainda parcial.** A
  primeira das seis gravações fechou: `boton_barras2isoClick`, com spec, Pascal
  e golden verde. Cinco continuam abertas.

- **Resumo do que foi feito:**

  **`boton_barras2isoClick` está `implementado`.** É o menor do grupo — 272
  bytes, do `0x0040cab8` ao `0x0040cbc7` — e coube inteiro numa leitura. Ele
  grava cinco bytes do **buffer de edição** (`0x00434592`), não do modelo, o
  que é exatamente a distinção que a WTE-TASK-26 mediu e guardou como
  `BarrasEmEdicao`; sem ela a gravação levaria o valor velho e o gate acusaria
  a gravação por um defeito da edição.

  **O endereço não sai de um `OFS_*` mais um passo — sai da aritmética do
  original, e as duas fontes foram confrontadas.** O Obocaman calcula
  `0x45FF0 + 5·idx` como índice de byte no fluxo de dados a partir do setor
  850 e converte para offset absoluto na hora. O `we2002_core` chega aos
  mesmos endereços por outro caminho: lê em sequência e **salta** na fronteira
  de setor, com `OFS_TEAM_BARS_A` para o time 3. As duas concordam onde
  poderiam divergir — 2328199 para `idx = 3`, 2328508 para `idx = 4`. É a
  conferência que a §4.2 do plano manda fazer antes de acreditar em fórmula.

  **O gate agora julga edição e gravação juntas, e precisou de DOIS roteiros
  para isso.** O `golden-03-barras` grava sem editar e passa — mas passaria
  igual com um port que não gravasse nada, porque sem edição os dois lados
  escrevem os bytes que já estavam lá. O `golden-04-barras-editada` edita
  `bar_defence` do time 2 pela tela antes de mandar gravar: medido no lado
  oráculo, `0x04` vira `0x06` em 2328195, e o port produziu o mesmo arquivo. É
  o critério que a WTE-TASK-26 passou para cá em 2026-08-12, e é a primeira vez
  que ele roda.

  O estímulo do `golden-04` não é novo: as três coordenadas (3 `Down`,
  `sel_barra1` em (30,112), trilha em (190,200)) são as que o
  `compara_tela.sh` mediu nos dois lados em 2026-08-12, inclusive o passo de
  `+2` por clique na trilha, que é código diferente nos dois widgetsets.

  **EDC/ECC preservados deixou de ser presumido, para esta gravação.** O
  `cmp` da corrida editada muda **um** byte, em 2328195; os 280 bytes de
  EDC/ECC do setor 989 (2328200..2328479) saem idênticos. Medido, não
  presumido — mas vale para a gravação medida, não para o grupo, então o
  critério continua aberto.

- **A assimetria de coordenada entre os lados tem causa medida.** O `Ok` do
  `ficha_info3` fica em (142,80) no oráculo e em (140,56) no port: sob Wine sem
  gerenciador de janela a moldura é desenhada **dentro** da janela X (3 px de
  borda, 29 de título), e a janela mede 282×113; sob gtk2 a janela **é** o
  cliente, e mede os 276×81 do DFM. Por isso cada `golden-0*` tem `.port.txt`
  próprio.

- **Uma divergência de arquitetura, e ela não aparece no gate.** O port também
  atualiza `Jogo.teams[].bar_*` ao gravar. O `wte.exe` relê a imagem a cada
  troca de time, então o disco é a fonte dele; o port carrega uma vez e desenha
  a partir de `Jogo`. Gravar só no disco faria a tela do próprio port discordar
  do próprio arquivo na volta ao time. Mesmo byte, mesmo offset — está escrito
  na spec.

- **Um número do plano mudou, e o `check_fase2.py` não deixou passar.** Escrever
  Pascal à mão move a fração de código gerado: 74,0% → **73,6%** (9.323 geradas
  contra 3.345 à mão). A §4.4 do `PLAN-WTE-LAZARUS.md` afirma esse número
  literalmente e o `--check` reprovou até ela ser corrigida. Isso vai se repetir
  a cada handler desta fase.

- **O que esta passagem NÃO fez:**
  - `boton_nombres2iso`, `boton_tex2iso`, `boton_mcr2iso`, `grabar_camiseta` e
    `grabar_memory` continuam sem spec e sem Pascal;
  - EDC/ECC preservados continua critério aberto — provado para uma gravação,
    não para as seis;
  - os nove handlers que a WTE-TASK-26 deixou em `aberto` pela opção A
    continuam lá: só o par das barras (`sel_barraClick` + `track_barraChange`)
    ganhou julgamento por byte nesta passagem.

- **Arquivos criados/modificados:**
  - `wte/re/spec/MainForm.boton_barras2isoClick.md` — veredito `implementado`
  - `wte/src/impl/ep2002_mainform.boton_barras2isoClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — a aritmética de endereço e o
    `GuardaBarrasNoModelo`
  - `wte/src/we2002_estado.pas` — `EnderecoDeDados` e `GravaNaImagem`, a porta
    de escrita do port
  - `wte/tests/roteiros/golden-03-barras{,.port}.txt`,
    `golden-04-barras-editada{,.port}.txt`
  - `wte/re/spec/INDICE.md`, `wte/re/fase-2.md`, `wte/re/offsets-novos.md`,
    `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv` — gerados/evidência
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — a fração remedida
  - `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `golden_check.sh` sobre `golden-03-barras` **PASSOU** e
  sobre `golden-04-barras-editada` **PASSOU** (nos dois, só as duas faixas
  declaradas do arranque divergem); `make -C wte check` rc 0 com **590 testes**
  OK; `lazbuild` rc 0; `spec_index.py` 19 `implementado`. `roms/` intocada.

- **Problemas encontrados:** nenhum que tenha sobrado. Um `pkill -f 'build/wte'`
  numa medição exploratória casou com a própria linha de comando do shell e o
  matou junto — sem consequência para o repositório, e a lição é a de sempre
  neste projeto: filtro por nome alcança quem está segurando o nome.

---

- **Executado em:** 2026-08-19 — **terceira passagem, ainda parcial.** Abertura
  do `boton_nombres2isoClick`: a spec está escrita e o mapa de bytes medido, e
  o Pascal **não**. O veredito ficou `aberto` de propósito.

- **Resumo do que foi feito:**

  **A estrutura do maior handler do grupo está recuperada.** 2.268 bytes, e ele
  não grava sozinho: apoia-se em duas tabelas e três rotinas internas.

  | endereço | papel |
  |---|---|
  | `0x004231a0` | 3 linhas × 6 `DWORD` — quais blocos cada campo tem; zero quer dizer "não tem" |
  | `0x00433a0c` | 3 × 6 registros de 52 B, preenchidos por time: `{offset, comprimento, modo, buffer 40 B}` |
  | `0x00403a68` | codifica o texto da tela no buffer, em **duas** codificações |
  | `0x00403dcc` | resolve o registro `(campo, bloco)` |
  | `0x00403400` | `fseek` + `fputc` byte a byte — não conhece nome nenhum |

  O `+4` da tabela de registros é o `0x00433a10` que a
  [CORR-WTE-061](/docs/tasks/CORR-WTE-061.md) já tinha medido como largura por
  time; agora ele tem vizinhos com nome.

  **O trace não separa bloco de bloco, e isso obrigou uma régua nova.** As oito
  faixas que o `27-gravacao-controle` registrou são fronteiras de **descarga**
  do buffer do runtime C, não gravações lógicas: duas gravações vizinhas caem
  na mesma faixa. A sonda
  [`27-nomes-editados.txt`](../../wte/tests/roteiros/27-nomes-editados.txt)
  digita texto distinto nos três campos antes de gravar, e aí o `cmp` atribui
  cada bloco ao seu campo. Resultado: **dez** blocos, com offset, tamanho e
  conteúdo — 2 de `edit_nombre1`, 5 de `edit_nombre2` e 3 de `edit_nombre3`.

  O estímulo não é novo: texto `A B-C.DEFG` e time 2, os mesmos do
  `compara_tela.sh --nomes`, já medidos nos dois lados em 2026-08-12.

  **Duas codificações, e o campo `modo` do registro escolhe.** Modo 1 é dois
  bytes por caractere (`0x00403448` devolve o par em `0x00432eb4`/`0x00432eb8`;
  caractere não reconhecido vira um espaço simples) — é o
  `OFS_TEAM_NAME_KANJI_A`, onde `A BC.` ocupa 10 bytes. Modo 2 é um byte por
  caractere. Nos dois o resto do comprimento vai a `0x00`, e o laço para no
  comprimento do **registro**, nunca no fim do texto.

  **Três exclusões dentro do laço, e nenhuma é validação de entrada.** Bloco
  ausente na tabela; `edit_nombre1` começando com `?` pula **todos** os blocos
  daquele campo (o `?` é o que a carga mostra quando não soube decodificar, e
  regravá-lo destruiria o nome); e `edit_nombre2` bloco 3 com `ItemIndex >= 63`,
  que é clube de Master League. É por isso que a tabela promete onze blocos e
  a medição vê dez.

  **Ele também mexe na tela, e não só na imagem:** remonta o rótulo do combo
  (`IntToStr(idx)` alinhado à direita em três colunas, mais o texto de
  `edit_nombre1`) e o escreve em `Items[idx]` de `lista_equipos_1` e
  `lista_equipos_2`, guardando e repondo o `ItemIndex` — porque atribuir a
  `Items[]` zera a seleção.

- **O que esta passagem NÃO fez, e por quê:** o Pascal. A spec responde *o que*
  e *onde* para o time medido; falta a regra geral que a carga usa para
  preencher os 18 registros — offset e comprimento **por time** —, e o port
  precisa reproduzi-la ou derivá-la do `we2002_core`. Isso está escrito na
  própria spec, na seção "O que falta para escrever o Pascal": pelo gabarito,
  spec que não basta para escrever o código está incompleta, e dizer isso é a
  informação que ela existe para dar.

- **Arquivos criados/modificados:**
  - `wte/re/spec/MainForm.boton_nombres2isoClick.md` — veredito `aberto`
  - `wte/tests/roteiros/27-nomes-editados.txt` — a sonda de atribuição
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv` — a evidência da sessão
  - `wte/re/offsets-novos.md`, `wte/re/spec/INDICE.md` — gerados
  - `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `spec_index.py` 58 com spec, 19 `implementado`. Nenhuma corrida de golden
  nesta passagem — não há Pascal novo para julgar, e rodar o gate sobre código
  inalterado mediria a passagem anterior. `roms/` intocada.

- **Problemas encontrados:** nenhum.

---

- **Executado em:** 2026-08-19 — **quarta passagem.** `boton_nombres2isoClick`
  está `implementado`, com golden verde e controle fechando antes. **Duas das
  seis** gravações prontas; a task continua `⬜ Pendente`.

- **Resumo do que foi feito:**

  **A peça que faltava era `0x00403c0c`, e ela não é tabela — é varredura.** A
  terceira passagem parou dizendo que faltava "a regra geral que enche os 18
  registros, offset e comprimento por time". A regra é: partir do offset do
  bloco, andar `94 − índice` registros terminados em NUL (com o enchimento que
  vier depois) e medir o slot que sobrou. Sem tabela de offset por time e sem
  tabela de comprimento.

  Duas coisas caem de graça daí, e nenhuma tabela as diria: **os blocos guardam
  os times em ordem inversa** — o offset da tabela é o slot do time 94, e o
  `we2002_core` conhece a mesma inversão pelo outro lado (`ml_teams[31-i]` no
  `Save`) — e **o comprimento é a largura do slot medida na imagem**, não uma
  constante, que é por que o mesmo campo grava 7 bytes num bloco e 3 noutro.

  **O salto de setor é do fluxo, não do endereço.** `0x00403388` testa
  `posição mod 2352 = 2072` depois de **cada** byte e pula 304. É o que torna o
  MODE2/2352 invisível para o resto do código do original — e é obrigatório no
  port: sem ele, nome que atravessa fronteira de setor escreveria por cima do
  EDC/ECC. Entrou como `SaltaFronteiraDeSetor` / `LeDoFluxo` / `GravaNoFluxo`
  no `we2002_estado`.

  **O espaço é codificado diferente do `ed.exe`, e isso mudou uma decisão de
  reuso.** No modo de dois bytes o `wte.exe` escreve **um** `0x20` para o
  espaço; o `AsciiToKanji` do `we2002_core` escreve o par `0x82 0x80`. Medido
  no byte gravado: `A BC.` sai com nove bytes, não dez. Como o alvo deste
  projeto é o editor do Obocaman, o port **não** reusa o codec do core aqui —
  reusar teria dado um golden vermelho com cara de bug de offset.

  **Um erro da passagem anterior foi corrigido pela medição.** A spec dizia que
  o bloco 3 do campo 2 é pulado para `ItemIndex >= 63`; é o contrário —
  `cmp eax,0x3f` / `jl` pula quando o índice é **menor** que 63, porque o bloco
  é `OFS_ML_TEAM_NAME_7` e só clube de Master League o tem. A tabela promete
  onze blocos e o `cmp` viu dez com o time 2, que é o que denunciou.

- **A passagem do golden não é vazia, e isso foi medido separado.** Verde entre
  dois lados poderia significar "nenhum dos dois gravou". Rodado o lado port
  sozinho contra a ROM limpa, ele grava **os dez blocos**, nos mesmos offsets e
  tamanhos que a sonda `27-nomes-editados` mediu no oráculo.

- **O `:99` caiu no meio da passagem, e o sintoma é o da memória do projeto:
  saída vazia e código 1, sem uma linha de erro.** O `roteiro_display` resolve
  o `XAUTHORITY` do `ps` e, com o servidor morto, o `set -e` derruba o script
  antes de qualquer mensagem. Foi religado com a geometria documentada no
  `CLAUDE.md` (`Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp`) — não houve
  queda para o `:1`.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.boton_nombres2isoClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — a tabela `NOME_BLOCOS`, a
    varredura `LocalizaBlocoDeNome` e o codificador `CodificaNomeDoBloco`
  - `wte/src/we2002_estado.pas` — o fluxo com salto de setor
  - `wte/tests/roteiros/golden-05-nomes{,.port}.txt`
  - `wte/re/spec/MainForm.boton_nombres2isoClick.md` — veredito `implementado`,
    mais a regra recuperada e a correção do sentido da exclusão
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/re/fase-2.md`, `wte/re/spec/INDICE.md`
  - `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` sobre `golden-05-nomes`
  **PASSOU: byte-idêntico** — e num roteiro que digita isso não é formalidade,
  é a única régua onde o não-determinismo do teclado apareceria; o `golden`
  contra o port **PASSOU**, só as duas faixas do arranque. `make -C wte check`
  rc 0; `lazbuild` rc 0; `spec_index.py` **20 `implementado`**. A fração de
  código gerado caiu de 73,6% para **72,0%** e o `check_fase2.py` reprovou até
  a §4.4 do plano ser corrigida — de novo. `roms/` intocada.

- **Problemas encontrados:** o `:99` morto, acima. Nada mais.

---

- **Executado em:** 2026-08-19 — **quinta passagem.** `boton_tex2isoClick`
  está `implementado`, com controle e golden verdes. **Três das seis**
  gravações prontas; a task continua `⬜ Pendente`.

- **Resumo do que foi feito:**

  **A textura é aritmética pura — nem varredura, nem tabela.**

  ```
  offset = 19756824 + 47040 * (indice + 9 * (indice div 95))
  ```

  `19756824` = `8400 * 2352 + 24` e `47040` = `20 * 2352`: **vinte setores por
  time**, contíguos. Medido com o time 2 e uma fonte de 5000 bytes — setores
  8440..8459, a partir de 19850904, que é exatamente `19756824 + 47040 * 2`.

  **São sempre os vinte, e é aí que um port erraria.** O original copia
  enquanto a fonte durar; quando ela acaba no meio de um bloco ele enche o resto
  com zero, e um **segundo** laço escreve de zero os blocos que sobraram. Uma
  textura menor que a anterior não deixa rabo. Um port que gravasse só o que
  leu passaria com uma fonte de 40960 bytes e falharia com qualquer outra — por
  isso a sonda usa 5000, que não é múltiplo de 2048.

  **O botão não estava habilitado, e achar quem o habilita foi metade da
  passagem.** O primeiro golden falhou com o port sem mostrar o modal, e o
  trace não tinha o handler: `boton_tex2iso` nasce `Enabled = False` no DFM.
  Quem o liga no original é o `boton_dialogo_texClick`, em `0x0040e17d` —
  `SetEnabled(True)` pela VMT[0x64] sobre o campo `0x0474`, que o
  `wte/re/campos.tsv` resolve nesse botão. Faz sentido: sem fonte escolhida não
  há o que gravar.

  **A textura entra no port por `WTE_TEXTURA`, e isso é afordância de harness.**
  O lado port do gate não consegue escolher arquivo — o `TOpenDialog` do gtk2
  não se dirige por coordenada fixa sem gerenciador de janela. A variável semeia
  `TexturaEscolhida` no `FormShow` e liga o botão, exatamente como o argumento
  posicional semeia a imagem desde a WTE-TASK-25. Não muda byte nenhum: muda por
  onde o caminho entra, e os dois lados terminam com o mesmo arquivo.

- **O `boton_dialogo_texClick` continua `aberto`, de propósito.** Portá-lo pela
  metade — só o `Execute` e o caminho — daria um veredito que afirma mais do que
  se fez, e o formato `.tex` é da
  [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md). Na janela do port o
  botão de diálogo segue inerte, e está escrito na spec dele e na do
  `boton_tex2iso`.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.boton_tex2isoClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — as três constantes da região
  - `wte/src/impl/ep2002_mainform.FormShow.inc` — a semeadura e o `Enabled`
  - `wte/src/we2002_estado.pas` — `TexturaEscolhida`, `TexturaTamanho`,
    `TamanhoDoArquivo`
  - `wte/tools/golden_run_laz.sh` — repassa `WTE_TEXTURA`
  - `wte/tests/roteiros/27-textura.txt` — a sonda
  - `wte/tests/roteiros/golden-06-textura{,.port}.txt` — o gate
  - `wte/re/spec/MainForm.boton_tex2isoClick.md` — veredito `implementado`
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv`, `wte/re/offsets-novos.md`,
    `wte/re/spec/INDICE.md`, `wte/re/fase-2.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/tests/roteiros/README.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` **PASSOU: byte-idêntico**
  e o `golden` contra o port **PASSOU**, só as duas faixas do arranque.
  Verificado à parte que a passagem não é vazia: o port sozinho contra a ROM
  limpa grava os **vinte** setores, a partir do mesmo 19850904. `make -C wte
  check` rc 0; `lazbuild` rc 0; `spec_index.py` **21 `implementado`**. A fração
  de código gerado caiu para **71,4%** e a §4.4 do plano foi corrigida de novo.
  `roms/` intocada.

- **Problemas encontrados:** o botão desabilitado, acima — e o sintoma dele é
  instrutivo: o gate falhou dizendo "a janela `W11 TE PT` não apareceu", que
  parece problema de roteiro. O que respondeu foi o `port-trace.log`, onde o
  handler simplesmente não constava.

---

- **Executado em:** 2026-08-19 — **sexta passagem.** `grabar_memoryClick` está
  `implementado`, com controle e golden verdes — e o gate precisou de uma régua
  que não existia. **Quatro das seis** gravações prontas; a task continua
  `⬜ Pendente`.

- **Resumo do que foi feito:**

  **Este handler não grava na imagem, e é a primeira vez que isso importa.** Ele
  emite um `.mcr` de 128 KiB — um memory card PSX com o time dentro. A ROM sai
  intacta, e está medido: as seis faixas de `GRAVA_MCR` no trace são todas de
  **leitura**, e o `cmp` da sonda acusa só os sete setores do arranque.

  Isso quebra o gate como ele estava. `golden_check.sh` compara duas imagens;
  aqui as duas sairiam iguais mesmo com um port que não fizesse absolutamente
  nada. Entrou `--artefato <nome>`: o script apaga `work/<nome>` antes de cada
  lado, guarda o que aquele lado produziu, compara os dois — e **continua**
  comparando as imagens, que passou a ser como se prova que a gravação não
  vazou para dentro da ROM. Não-vacuidade sai de graça no desenho: o arquivo é
  criado pelo handler, então port inerte não produz nada e o script para antes
  de comparar.

  **O molde vem do `dat.bin`, e a segunda metade dele já era conhecida.** A
  primeira metade (`0x20000`, o tamanho exato de um memory card) é um cartão
  formatado com o slot do WE2002 pronto; o handler a copia inteira e só então
  escreve o time por cima. A `wte/re/assets.md` já tinha dado esse veredito na
  WTE-TASK-08 — o que faltava era o consumidor.

  **Três regiões de origem, e a do meio não tem nome no `we2002_core`.**

  | lógico | passo | time 0 | `we2002_core` |
  |---|---|---|---|
  | `0x40C2C` | 30 | 2303700 | `OFS_FORMATIONS` |
  | `0x408A8` | 5 | 2302800 | **sem nome** |
  | `0x46228` | 6 | 2329056 | `OFS_KICKER` |

  A do meio é a **tática**, e quem a nomeia é o próprio `wte.exe`: o mesmo
  `0x408A8` aparece em `mostrar_estrategiaClick`, em `estrategia.BitBtn3Click` e
  em `boton_mcr2isoClick`, e nos três enche o mesmo rascunho de 4 bytes em
  `0x00432eaf`. O `ed.exe` não lê essa região, e é por isso que ela não tem
  `OFS_*`.

  O `+2` quando `índice div 95` é 1 não é enfeite: é o mesmo par de bytes que o
  `Load` do `we2002_core` pula entre os 32 clubes de ML e o time-modelo.

  **Os números de camisa vêm da TELA, e esse é o ponto do handler.** Ele monta
  `'dorsal' + IntToStr(j+1)`, chama `FindComponent`, lê o `Caption`, tira 1 e
  limita a 31 — e só então empacota 5 bits por jogador, 6 por `DWORD`, 16 bytes.
  É o único campo que não sai da imagem nem do molde, e é assim que um número
  editado pela WTE-TASK-26 chega ao cartão.

  **O botão nasce desabilitado, e desta vez a busca foi barata.** Igual ao
  `boton_tex2iso` — mas aqui quem liga é o `lista_equiposChange`, em
  `0x0040d31a`, com o `grabar_camiseta` na linha seguinte. Escolher time já
  habilita os dois. O port não fazia isso; passou a fazer.

- **Uma medição que expôs a cegueira da própria régua.** O `.mcr` produzido
  difere do molde em **489 bytes, 51 faixas** — e a tabela do handler promete
  52. A que falta é `0x6479`, o nibble alto do byte 1 da tática: para o time 2
  ele vale zero, que é o que o molde já tinha. Gravação de valor igual nenhum
  `cmp` enxerga, que é a mesma distinção que o
  [`gravacao_controle.py`](../../wte/tools/gravacao_controle.py) faz entre
  `escreveu` e `mudou`. A conferência que fecha isso não é o `cmp`: é ler os
  quatro bytes de tática da imagem e comparar com os seis destinos.

- **Divergência deliberada, a mesma do `boton_barras2isoClick`.** O original
  relê nome e atributos **da imagem** para o buffer 23; o port chama a
  `CarregaJogador`, que lê a camada de dados. Mesmo byte, mesma posição, outra
  fonte. O buffer continua sendo o 23 — que cai **dentro** da lista de descarte
  (`BUF_DESCARTE_BASE + 20`), então emitir um cartão embaralha a linha 20 do
  descarte no original e aqui.

- **O que esta passagem NÃO fez:**
  - o critério herdado da WTE-TASK-26 **não fechou para este handler**. Ele tem
    par (`dorsalClick`, `scroll_dorsalChange`) e o `27-mcr` grava sem editar
    número nenhum. Falta o que o `golden-04` teve antes de existir: uma medição
    do `compara_tela.sh` do **passo do `scroll_dorsal` nos dois widgetsets**. A
    barra é `Min=1 Max=99` e o passo por clique é código diferente no Wine e no
    gtk2 — foi exatamente a armadilha que a trilha do `track_barra` teve, e lá
    o `+2` só foi confiável depois de medido nos dois lados;
  - `boton_mcr2iso` e `grabar_camiseta` continuam sem spec e sem Pascal, e as
    duas dependem de outra task (31 e 32);
  - EDC/ECC preservados continua critério aberto. Esta gravação não o toca de
    forma nenhuma — não escreve na imagem —, então ela nem soma evidência.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.grabar_memoryClick.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — as constantes do cartão, o
    `GravaCartaoDeMemoria`, o `TextoDoDorsal` e o `SETOR_BASE_DADOS` (o `850`
    deixou de ser "das barras" e virou o que sempre foi)
  - `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — os dois `Enabled`
  - `wte/src/impl/ep2002_mainform.FormShow.inc`, `wte/src/we2002_estado.pas` —
    `CartaoDestino` e o `LeDoFluxoEm`, o simétrico do `GravaNoFluxo`
  - `wte/tools/golden_check.sh` — `--artefato`; `wte/tools/golden_run_laz.sh` —
    repassa `WTE_MCR`
  - `wte/tests/roteiros/27-mcr.txt` — a sonda
  - `wte/tests/roteiros/golden-07-mcr{,.port}.txt` — o gate
  - `wte/re/spec/MainForm.grabar_memoryClick.md` — veredito `implementado`
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv`, `wte/re/offsets-novos.md`,
    `wte/re/spec/INDICE.md`, `wte/re/fase-2.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, os dois `README.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle --artefato saida.mcr`
  **PASSOU: byte-idêntico** nas duas réguas — o `.mcr` é determinístico e a
  imagem sai igual; o `golden` contra o port **PASSOU**, `saida.mcr`
  byte-idêntico nos dois lados e só as duas faixas do arranque na imagem. As
  duas réguas do `diff_dirigido.sh` fecham na sessão nova (9/9). `make -C wte
  check` rc 0; `lazbuild` rc 0; `spec_index.py` **22 `implementado`**. A fração
  de código gerado caiu de 71,4% para **69,9%** e o `check_fase2.py` reprovou
  até a §4.4 do plano ser corrigida — pela quarta vez seguida. `roms/`
  intocada.

- **Problemas encontrados:** um, e de método: a primeira corrida do
  `diff_dirigido.sh` foi com `--saida /tmp/dd/mcr`, e o nome da sessão sai do
  **basename da saída** — as faixas entraram nos TSV versionados como `mcr` em
  vez de `27-mcr`, fora da convenção das outras quatro. Desfeito com `git
  checkout` dos dois TSV e refeito sem a opção, que é o que usa o nome do
  roteiro.

---

- **Executado em:** 2026-08-19 — **sétima passagem.** Fecharam **três** dos
  critérios abertos: o par edição+gravação, o EDC/ECC e o registro de
  divergências. A task continua `⬜ Pendente` por **um** item, e ele é grande:
  os oito handlers de mover ainda esperam a metade de escrita.

- **Resumo do que foi feito:**

  **Havia uma quinta gravação, e ela não é um botão.** O `dorsalClick` é
  handler de *edição* — está na tabela da WTE-TASK-26 —, mas ao fechar o modal
  ele escreve o número na imagem, pela `0x00404048`. A 26 fechou com ele e mais
  oito `aberto` de dono nomeado aqui, pela **opção A**; esta passagem promoveu
  o primeiro dos nove. O comentário do próprio `.inc` do port já dizia isso
  desde a WTE-TASK-25 — a tabela de alvos desta task é que nunca o listou.

  **Três ramos, e os dois que têm nome batem com o `we2002_core`.**

  | ramo | condição | endereço |
  |---|---|---|
  | all-star | `índice = 48` | setor 850, lógico `$299AF + 12·slot`, 5 bits no bit 2 |
  | Master League | `índice > 62` | **absoluto** `$1EB797 + 23·i − 760·(i div 95) + slot`, 1 B cru |
  | seleção | `índice ≤ 62` | setor 24, lógico `$4A094 + 16·índice`, 16 B com 5 bits por slot |

  `EnderecoDeDados(24, $4A094)` dá **404716** = `OFS_SQUAD_NUMBERS_NATIONAL`, e
  a fórmula de ML no time 95 dá **2014504** = `OFS_SQUAD_NUMBERS_ML`. O `+1`
  entre o time-modelo e o primeiro clube também bate: o `Load` do core lê 23
  bytes, **pula um**, e só então os 32 clubes — e a fórmula põe o time 63 em
  2014528, que é `2014504 + 23 + 1`. É a conferência que a §4.2 do plano manda
  fazer antes de acreditar em fórmula, e as duas fontes concordam nos três
  pontos onde poderiam divergir.

  **O ramo de ML é o único que não passa pelo fluxo** — `fseek`/`fputc` crus,
  sem o salto de fronteira de setor que os outros dois fazem. É um byte só, e o
  original não pula.

  **O passo da barra foi medido nos dois widgetsets antes de o roteiro
  existir**, como a trilha do `track_barra` exigiu na WTE-TASK-26: clique no
  meio da trilha pagina por `LargeChange = 4`, os dois andam igual, e o time 2
  vai de `dorsal1 = 1` para 5 — **um** byte, em 404748. Sem medir isso primeiro,
  um passo de 4 de um lado e 1 do outro daria divergência de tela que não é do
  handler.

  **O gate novo julga duas gravações numa corrida.** O
  [`golden-08-dorsal-mcr`](../../wte/tests/roteiros/golden-08-dorsal-mcr.txt)
  edita o número, grava na imagem pelo `dorsalClick` e emite o `.mcr` pelo
  `grabar_memory`. Os dois juntos porque o número é o **único** campo do cartão
  que não vem do disco nem do molde: gravar o cartão sem editar número nenhum
  verifica os 16 bytes de `0x5404` contra um valor que ninguém tocou.

  **EDC/ECC deixou de ser presumido, e não precisou de corrida nova.** A conta
  entrou no `gravacao_controle.py`: **114 faixas em 8 sessões**, nenhuma tocando
  byte de EDC/ECC nem de cabeçalho — cada extremo cai entre 24 e 2071 do próprio
  setor. As sessões saem do TSV pelo prefixo `27-` em vez de lista à mão, então
  sonda nova entra sozinha. Quatro testes cobrem a conta, inclusive um que
  planta uma faixa no EDC para provar que ela **detecta**.

- **Um defeito do próprio driver apareceu, e ele era invisível até agora.** O
  `>~` (busca de janela por tamanho) enumerava com
  `xdotool search --name '.'` — "qualquer janela com nome". Só que o `xdotool`
  casa a regex contra o nome **já decodificado**, e janela cujo `WM_NAME` é
  Shift-JIS cru simplesmente não entra na lista. Sob Wine o `ficha_dorsal`
  aparecia; sob gtk2, não. E os três formulários que precisam de busca por
  tamanho são exatamente os que trocam o `Caption` por nome de jogador ou de
  time — ou seja, o `>~` falhava justamente no caso para o qual foi criado. O
  `janela_geo` passou a enumerar por `--pid` quando há filtro de processo.

  O conserto trouxe um segundo erro, de mão: `local ... lista` sob `set -u` fica
  **não atribuída**, e o golden passou (lá o filtro de PID existe) enquanto o
  `diff_dirigido.sh` quebrou (lá não existe). Duas rotas pelo mesmo código, e só
  uma exercitada.

- **O que esta passagem NÃO fez:**
  - os **oito** handlers de mover continuam `aberto`. A metade de escrita deles
    é a `0x00404820`, 1.459 bytes, e é o que falta para a opção A fechar por
    inteiro. Virou critério explícito desta task, que antes só o tinha implícito
    no log da 26;
  - `boton_mcr2iso` e `grabar_camiseta` seguem nas tasks 28 e 29, por desenho.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.aux.inc` — `GravaNumeroDaCamisa`,
    `GuardaNumeroNoModelo` e as constantes dos três ramos
  - `wte/src/impl/ep2002_mainform.dorsalClick.inc` — a chamada e o cabeçalho
  - `wte/tools/roteiro.sh` — o `janela_geo` por `--pid`
  - `wte/tools/gravacao_controle.py` + `test_gravacao_controle.py` — a conta de
    EDC/ECC e os quatro testes dela
  - `wte/tests/roteiros/27-dorsal-editado.txt`,
    `golden-08-dorsal-mcr{,.port}.txt`, `README.md`
  - `wte/re/spec/MainForm.dorsalClick.md` — veredito `implementado`
  - `wte/re/gravacao-controle.md`, `wte/re/offsets-novos.md`,
    `wte/re/cmp-medido.tsv`, `wte/re/io-medido.tsv`, `wte/re/spec/INDICE.md`,
    `wte/re/fase-2.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, `docs/tasks/progresso.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle --artefato saida.mcr`
  sobre `golden-08-dorsal-mcr` **PASSOU: byte-idêntico** nas duas réguas; o
  `golden` contra o port **PASSOU**, `saida.mcr` byte-idêntico e só as duas
  faixas do arranque na imagem. As duas réguas do `diff_dirigido.sh` fecham na
  sessão nova (10/10). `make -C wte check` rc 0; `lazbuild` rc 0;
  `spec_index.py` **23 `implementado`**. A fração de código gerado caiu para
  **69,2%**. `roms/` intocada.

- **Problemas encontrados:** os dois do driver, acima. Mais um de higiene: uma
  sonda manual deixou o port aberto no `:99` e a guarda 2 do `golden_check.sh`
  recusou começar — que é exatamente para isso que ela existe.

---

- **Executado em:** 2026-08-19 — **oitava passagem.** A metade de escrita dos
  oito handlers de mover fechou **para destino de seleção**, com golden verde. A
  task continua `⬜ Pendente` por um ramo: destino de Master League.

- **Resumo do que foi feito:**

  **A `0x00404820` tem três destinos, e só um deles cabia nesta passagem.** O
  ramo de seleção está portado e medido; o de Master League aloca bloco livre,
  mexe na tabela de vínculos e decrementa o contador `0x004335c0` — que é a
  WTE-TASK-33 quem calcula. Gravar meio bloco seria pior do que não gravar,
  então a rotina **sai sem tocar em byte nenhum** quando o destino não é
  seleção. Lacuna declarada, com dono, e não silêncio.

  **As três colunas de offset do registro de buffer voltaram do exílio.** A
  WTE-TASK-25 as deixou de fora de propósito — naquele momento só a leitura
  importava, e leitura vem da camada de dados. A gravação precisa delas, e elas
  não são deriváveis do `Jogo`:

  | coluna | fórmula | tipo |
  |---|---|---|
  | nome | `EnderecoDeDados(24, $467F8 + 230·time + 10·slot)` | lógico |
  | atributos | `EnderecoDeDados(850, $265EC + 276·time + 12·slot)` | lógico |
  | condicional | `3067404 + 23·time + 2·(time div 56) + slot` | **absoluto** |

  As duas primeiras dão `OFS_PLAYER_NAME` e `OFS_PLAYER_ATTR` no time 0 slot 0.
  A terceira se confere de outro jeito, e é a conferência mais bonita desta
  passagem: para o time 2 slot 0 ela dá **3067450**, que é exatamente a sexta
  leitura que o `0x0040f150` faz ao montar o cartão — medida três passagens
  atrás sem se saber de quem era.

  **Duas particularidades que só aparecem lendo o disassembly, e as duas são
  correção e não estilo:**

  1. **O time 48 lê o número de camisa ANTES e o regrava DEPOIS.** Ele guarda o
     número dentro do registro de atributos, e a gravação dos 12 bytes passaria
     por cima. A ordem do original existe por isso.
  2. **Os times 54 e 55 não têm campo condicional**, e no lugar dele o original
     grava outras duas coisas: o nome de novo, numa segunda região (390432), e
     o par de identidade `(time, slot)` em 2326480 — este por `fseek`/`fputc`
     crus, sem fluxo, como o ramo de ML do número de camisa.

  **O gate precisou de quatro combos preenchidos.** O `paderecha` não faz nada
  sem time e jogador dos **dois** lados, e a guarda lê o `ItemIndex` do jogador
  de destino antes de qualquer outra coisa — por isso o roteiro escolhe a
  direita primeiro. Medido: o destino da sequência é o **time 1, slot 1**, e o
  oráculo grava 10 bytes de nome em 388336 e 12 de atributos em 2179780, onde as
  duas fórmulas prevêem. O `cmp` vê menos — 4 e 10 —, porque o resto já era
  igual; a mesma cegueira que o `gravacao_controle.py` descreve.

  Os quatro botões de mover um jogador só compartilham corpo (`MoveUmJogador`) e
  rotina de gravação. Exercitar um exercita a rotina; o que muda entre eles é
  qual lado é a origem.

  **A conta de EDC/ECC absorveu a sonda nova sozinha**, que era o ponto de
  enumerar as sessões pelo prefixo `27-` em vez de listá-las: passou de 114
  faixas em 8 sessões para **125 em 9**, sem tocar no gerador.

- **O que esta passagem NÃO fez:**
  - o ramo de destino de Master League da `0x00404820`. É o último item aberto
    desta task, e o único que depende de outra (a 33, pelo contador);
  - os oito continuam `aberto`. O corpo deles está completo e gated para destino
    de seleção; promover com um ramo faltando seria afirmar mais do que se fez.
    A spec do `paderechaClick` traz o veredito estreitado; as outras sete
    continuam apontando para cá, o que segue verdadeiro.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.aux.inc` — `OffsetsDoJogador`,
    `GuardaJogadorNoModelo`, o corpo de gravação do `GravaJogador` e as seis
    constantes das três colunas
  - `wte/tests/roteiros/27-mover.txt`, `golden-09-mover{,.port}.txt`
  - `wte/re/spec/MainForm.paderechaClick.md` — veredito estreitado
  - `wte/re/gravacao-controle.md`, `wte/re/offsets-novos.md`,
    `wte/re/cmp-medido.tsv`, `wte/re/io-medido.tsv`, `wte/re/fase-2.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` sobre `golden-09-mover`
  **PASSOU: byte-idêntico**; o `golden` contra o port **PASSOU**, só as duas
  faixas do arranque. Conferido à parte que a passagem não é vazia: o port
  sozinho contra a ROM limpa grava as **mesmas duas faixas** que o oráculo,
  388336..388339 e 2179782..2179791, e os bytes batem um a um. As duas réguas do
  `diff_dirigido.sh` fecham na sessão nova (11/11). `make -C wte check` rc 0;
  `lazbuild` rc 0. A fração de código gerado caiu para **68,6%**. `roms/`
  intocada.

- **Problemas encontrados:** um, de linguagem: `GravaNumeroDaCamisa` mora depois
  do `GravaJogador` no mesmo `.inc`, e o Pascal exige `forward` para a chamada
  para frente. O compilador disse exatamente isso, e o conserto é uma linha.
