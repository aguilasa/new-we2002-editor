---
id: WTE-TASK-26
title: "Handlers de edição — nomes, números, atributos, mover jogador"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25"]
status: concluído
---

# WTE-TASK-26: Handlers de edição

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- Editam o estado **em memória**. A gravação é a WTE-TASK-27. A separação é de
  propósito: assim o golden test da 27 mede gravação, não edição, e uma
  divergência aponta para um lado só.

---

## Objetivo

Implementar o grupo de edição, com spec por handler.

### Alvos

| Grupo | Handlers | Endereços |
|---|---|---|
| nomes | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick`, `casilla_nombreKeyPress` | `0x0040d36c`, `0x0040d3c4`, `0x0040d41c`, `0x0040d43c`, `0x00408af8` |
| números | `dorsalClick`, `dorsalMouseDown`, `scroll_dorsalChange`, `casilla_dorsalKeyPress` | `0x00410a74`, `0x00410ddc`, `0x00402b58`, `0x00408b50` |
| atributos | `barrhabScroll`, `barrhab_bisScroll` | `0x00407a88`, `0x00407bb4` |
| barras | `sel_barraClick`, `track_barraChange` | `0x0040c9d0`, `0x0040ca10` |
| mover jogador | `paderechaClick`, `paizquierdaClick`, `parribaClick`, `pabajoClick`, `paderecha2Click`, `paizquierda2Click`, `paderechaeizquierdaClick`, `flechasapaClick` | `0x0040e5e8` … `0x00408088` |
| tática | `bolaMouseDown`, `bolaMouseMove`, `bolaEndDrag`, `campoMouseMove`, `rectanguloDragOver`, `rectanguloDragDrop`, `relojTimer` | `0x00408f00` … `0x00409ba4` |

`paderechaeizquierdaClick` é a novidade da v0.98 — "mover todos os jogadores de
cada time com um clique". ~~`ficha_movertodos` é a tela dela.~~ **Errado, e
medido em 2026-08-12 (nona passagem):** o `ficha_movertodos` é a confirmação dos
botões `paderecha2Click`/`paizquierda2Click`, os que copiam um elenco inteiro de
um lado para o outro. O `paderechaeizquierdaClick` (`0x0040e304`) não toca o
global `0x00432e48` (`_ficha_movertodos`, exportado pelo próprio `.exe`).

**São 28 handlers, e a tabela acima está completa** — conferido em 2026-08-12
contra a coluna `grupo` do
[`published_methods.tsv`](../../wte/re/published_methods.tsv). O grupo `edicao`
tem 44 linhas lá; as 16 de diferença carregam na coluna `nota` o dono fora
desta task: **11 do `ficha_color`** mais `colorearClick` e os dois
`mallaNMouseDown` são da
[WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md), e
`casilla_precioKeyPress` com `etiqprecioClick` são da
[WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md). Os 28 restantes são
exatamente os seis grupos acima (5 + 4 + 2 + 2 + 8 + 7).

### O que a spec tem de capturar aqui, e que a de carga não tinha

**Validação.** Estes handlers recusam entrada, e a regra da recusa é o que
importa. A WTE-TASK-05 já mapeou as mensagens de erro para os handlers que as
referenciam — a mensagem é o atalho para a regra. Exemplo já visto:

```
Numero do uniforme invalido ([33 ... 99] somente na Mastere
```

**Truncamento.** Todo campo de texto tem tamanho máximo no formato. O original
é C++Builder com buffer fixo; o comportamento de estouro (trunca? recusa?
corrompe o vizinho?) entra na spec, porque o Pascal não vai reproduzi-lo por
acidente. Isto alimenta a WTE-TASK-36.

**Ordem de evento.** `OnKeyPress` filtra caractere; a gravação no modelo
acontece onde? A WTE-TASK-13 mediu a ordem — usar a medição, não supor.

### Verificação

Estes não gravam. A verificação é: editar pela tela nos dois lados, **então**
gravar nos dois, e o golden test da WTE-TASK-22 compara. Uma edição por rodada,
para que a divergência tenha uma causa só.

**E o segundo verbo não tinha dono nesta task** *(medido em 2026-08-12)*. Quem
grava é o grupo da [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), que
`depends_on` esta — as barras editadas aqui só chegam à imagem pelo
`boton_barras2isoClick` (`0x0040cab8`), os nomes pelo `boton_nombres2isoClick`,
e assim por diante. É a mesma forma de circularidade que a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) e que a decisão de 2026-08-11
desfez para o critério de tela da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md). Como as outras duas, **não
se desfaz por mais uma passagem** — se desfez por decisão.

### Decisão do usuário, 2026-08-12: esta task fecha por pixel; o byte é da 27

Cada handler de edição tem duas metades de verificação, e elas medem coisas
diferentes:

| régua | o que julga | quem executa |
|---|---|---|
| **pixel** — `compara_tela.sh` | o efeito na tela: largura de barra, número de camisa, texto do campo | **esta task** |
| **byte** — `golden_check.sh` | que a edição chega ao byte certo da imagem | **[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md)** |

**Nenhuma das duas substitui a outra**, e é por isso que a segunda tem de ter
dono escrito em vez de sumir: pixel igual dos dois lados não prova que os dois
estão editando o **mesmo byte do modelo** — os dois poderiam desenhar a mesma
largura a partir de campos diferentes. É a lição da terceira ponta da
WTE-TASK-25, onde comparar port com oráculo teria passado igual se **ambos**
estivessem lendo o time errado.

A metade excluída virou linha de critério de conclusão da WTE-TASK-27, na forma
"cada gravação com uma edição de tela do grupo da 26 antes". Exclusão sem dono
nomeado é buraco, e este projeto já pagou por isso na 25.

**Alternativas descartadas:** implementar o par de gravação junto com cada
edição fura o escopo da 27 e devolveria duas causas possíveis a cada golden
vermelho; fundir 26 e 27 numa task só perderia a separação que faz uma
divergência apontar para um lado só, que é a razão de as duas existirem
separadas (primeiro parágrafo do Contexto).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/edicao-*.sh` | criar |

---

## Critério de conclusão

- [x] Todo handler do grupo com spec, incluindo regra de validação — **28 de
      28** (2026-08-13): barras 2, número 4, nomes 5, mover 8, atributos 2,
      tática 7. Nove fecham `aberto` com dono nomeado, como a opção A previu
- [x] Comportamento de truncamento documentado por campo — [`wte/re/truncamento.md`](../../wte/re/truncamento.md) (2026-08-13), gerado pelo [`dump_truncamento.py`](../../wte/tools/dump_truncamento.py)
- [x] ~~Golden verde para cada edição, uma por rodada~~ ~~conferência de tela
      verde para cada edição, uma por rodada~~ **Reescrito duas vezes, ambas por
      decisão do usuário** (2026-08-12 e 2026-08-18 — ver "As duas reescritas do
      critério de tela" abaixo): **conferência verde para cada grupo de edição,
      uma por rodada — de tela onde o alvo é mensurável em pixel, estática onde
      já se mediu que não é.** Mecanizado pelo
      [`check_edicao.py`](../../wte/tools/check_edicao.py) →
      [`wte/re/edicao-cobertura.md`](../../wte/re/edicao-cobertura.md): os 28
      handlers com instrumento nomeado, os estáticos rodando `--check`, e os de
      tela conferidos contra a **evidência de trace da própria corrida**. O
      golden por byte da mesma edição é critério da
      [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), porque só ela tem
      como levar a edição ao disco
- [x] Limpeza de campo usando `End`/`shift+Home`/`BackSpace`, nunca `ctrl+a` —
      o `edita_nomes` do `compara_tela.sh --nomes` (2026-08-18) limpa os três
      campos assim, nos dois lados, e é o primeiro roteiro deste projeto a
      digitar texto
- [x] Nenhuma medição sobre `roms/` diretamente — todas as passagens usaram cópia em `work/` ou no scratchpad
- [x] Commit no formato conventional, em inglês — as 22 passagens

### As duas reescritas do critério de tela

Ambas do usuário, e as duas pela mesma razão: **o critério pedia um instrumento
que não existe para parte do alvo**, e critério assim não fica mais rigoroso —
fica só impossível de fechar honestamente.

**2026-08-12 — de golden para tela.** O golden por byte exige levar a edição ao
disco, e gravar é da [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md). O
critério passou a pedir conferência de **tela**.

**2026-08-18 — de "cada edição" para "cada grupo, no instrumento que alcança".**
Três medições, todas já no log desta task, mostram que a régua de pixel não
alcança tudo:

- **a ficha do jogador não é mensurável em pixel** (décima quinta passagem): o
  `TScrollBar` do gtk2 desenha mais alto que os 12 px declarados e cobre a faixa
  das linhas 2 a 16 — de 16 `imghab`, só o primeiro dá medida. Isso atinge os
  grupos **atributos** e metade do de **números**;
- o substituto **já existe e já foi aceito**: o
  [`check_bitfields.py`](../../wte/tools/check_bitfields.py) confere a ordem de
  preenchimento da ficha contra os descritores de bit em `.data`. Ele mede
  **identidade de campo**, que é mais forte do que largura de pixel, e roda sem
  `:99` e sem Wine;
- o mesmo vale para o campinho da **tática**: a passagem 18 conferiu o arrasto
  na tela por inspeção dirigida, e o que sustenta a geometria é o
  [`dump_zonas.py`](../../wte/tools/dump_zonas.py), que confere cada retângulo
  contra o tamanho do `campo` no `.lfm`.

**O que a reescrita não afrouxa.** A régua de **byte** desses handlers continua
sendo da WTE-TASK-27, intocada. E "conferência estática" aqui não quer dizer
"nenhuma medição": quer dizer medição que não passa por pixel, com ferramenta
versionada e `--check`, como as duas acima.

**Alternativa descartada:** construir a régua de pixel da ficha pela assinatura
de cor dos 16 `valorhab` — o caminho que a décima quinta passagem identificou
como o único viável. É projeto de ferramenta por si, para cobrir o que duas
conferências estáticas já cobrem por outro caminho.

## Plano de fechamento

*(escrito em 2026-08-12, com 11 de 28 feitos. Os custos são medidos —
`dump_auxiliares.py` e o tamanho de corpo do `published_methods.tsv` —, não
estimados.)*

### A decisão que o plano precisou primeiro: **opção A**, do usuário, 2026-08-12

`0x00404820` **grava** (oitava passagem). Logo, os 8 handlers de mover são como
o [`dorsalClick`](../../wte/re/spec/MainForm.dorsalClick.md): editam e escrevem
no fim, e pela decisão (b) a metade de escrita é da
[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md).

**Consequência: 9 dos 28 handlers — o `dorsalClick` e os 8 de mover — não
chegam a `implementado` antes da 27.** Um terço da task.

| opção | efeito | |
|---|---|---|
| **A** | manter a decisão (b): a 26 fecha com **9 `aberto` de dono nomeado**, e a 27 os promove | **escolhida** |
| B | inverter 26 ↔ 27 e fechar tudo `implementado` aqui | descartada: refaz o grafo de dependências por causa de um lote |
| C | abrir exceção e escrever a chamada de gravação só para esses 9 | descartada: reintroduz duas causas possíveis por golden vermelho, que é o que a (b) existe para evitar |

**O critério "todo handler do grupo com spec" continua valendo integralmente**
— o que a opção A admite é que 9 deles fechem esta task com veredito `aberto`,
e não que fiquem sem spec.

### As seis passagens

| # | o que fecha | custo por ler | destrava |
|---|---|---|---|
| ~~9~~ | ~~mover, a família de 4~~ — **feita em 2026-08-12** | 881 B (a `0x00404374`, que o plano dava por medida e não estava) | `casilla_dorsalKeyPress` |
| ~~10~~ | ~~mover, os outros 4~~ — **feita em 2026-08-12**, menos o `flechasapaClick`, que não é do `MainForm` e está bloqueado com os lotes de atributo e tática | 181 B (a `0x0040b934`); as outras quatro da lista abaixo **não são chamadas** por estes handlers | — |
| 11 | preencher a ficha do jogador (`0x0040756c`) | 1.275 B | `iguala_nombresClick`, e o `50` da WTE-TASK-32 |
| ~~12~~ | ~~atributos (`barrhabScroll`, `barrhab_bisScroll`)~~ — **feita em 2026-08-12**, e o `flechasapaClick` **feito em 2026-08-13** | 0 B nos dois de `barrhab`; 1.124 B no `flechasapaClick`, mais o inicializador das legendas (`0x00401da8`, 2.998 B, lido por ferramenta e não à mão) | as legendas enumeradas da ficha, que estavam abertas desde a passagem 12 |
| ~~13~~ | ~~tática (`0x0040a0b4` + os 7)~~ — **feita em 2026-08-13**, em duas passagens | **o `0x0040a0b4` não é deste lote** — quem o chama é o `MainForm.mostrar_estrategiaClick`, do grupo de carga. Medido: os 7 somam 2.088 B e **não chamam auxiliar interna nenhuma**; os seis de arrastar são 1.152 B | as zonas do campinho, que o `estrategia.FormCreate` monta e ninguém tinha lido |
| 14 | os três critérios que sobram | — | fecha a task |

**Passagem 9 — mover, a família de 4.** 312 a 314 bytes cada, e **não depende
de mais nenhuma leitura**: as duas rotinas centrais foram medidas na sétima e
na oitava passagens. O que ela precisa escrever no port:

- `BufferJogador`, o registro de 44 bytes em três cópias (0 = destino, 1 e 2 =
  os dois lados), com o layout que as duas leituras independentes confirmaram;
- `CarregaJogador` — a `0x004046e8`;
- a comparação de identidade (`+0x16`, `+0x17`) e o `MostraCodigo` da
  `0x00403e20`, com as duas mensagens medidas.

Fecha de tabela o [`casilla_dorsalKeyPress`](../../wte/re/spec/jugador.casilla_dorsalKeyPress.md):
o buffer é exatamente o que faltava para ele avaliar a condição do `SetFocus`.

**Passagem 10.** `parriba` 807 B, `flechasapa` 981 B, `paderechaeizquierda`
425 B, `pabajo` 447 B. ~~Por ler: `0x00407338` (561 B), `0x00407110` (552 B),
`0x00406fe0` (301 B), `0x0040b934` (181 B), `0x00408460` (143 B).~~ **A lista
estava errada, e medido em 2026-08-12:** dos três handlers do `MainForm`
(`parriba`, `pabajo`, `paderechaeizquierda`) a única auxiliar nova é a
`0x0040b934`. As outras quatro são do `flechasapaClick`, que **não é do
`MainForm`** — é do formulário `jugador`, com doze botões ligados ao mesmo
corpo, e portanto está bloqueado no mesmo preenchimento de ficha que os lotes de
atributo e de tática.

**Ressalva acrescentada na décima primeira passagem:** dizer "são do
`flechasapaClick`" sugeria exclusividade, e três delas não são exclusivas —
`0x00406fe0`, `0x00407110` e `0x00407338` são chamadas **também** pelo
`0x0040756c`, o preenchimento da ficha. Só a `0x00408460` (143 B) é só dele. Lê-las
serve aos dois, e por isso elas entram na passagem 11 e não custam duas vezes.

**Passagem 11.** `0x0040756c` não é handler — é pré-requisito: sem a ficha
preenchida os dois handlers de atributo não são exercitáveis. Sai dela o valor
de `DWORD[0x00433b48]`, que fecha o `iguala_nombresClick`, e o `50` do campo
condicional, que é da [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md).

**Custo real, medido em 2026-08-12: 3.003 B, não 1.275.** O corpo chama cinco
rotinas internas — `0x00403278` (270), `0x00406fb4` (44), `0x00406fe0` (301),
`0x00407110` (552) e `0x00407338` (561) —, e o número do plano contava só o
corpo. Mesma forma do erro da passagem 9. **Mas a leitura mudou de tamanho para
melhor**: ver o Log da décima primeira passagem — o mapeamento de bit é tabela
de dados, não código, e ele já bate com o port.

**Passagem 12.** Mesma forma que as barras de força: devem escrever nos 12 bytes
de atributo do buffer. Gate por `compara_tela.sh --edicao` sobre a ficha.

**Passagem 13.** O risco real do plano — ver abaixo.

**Passagem 14.** Truncamento por campo (já com uma divergência achada: o port
não põe `MaxLength` em `edit_nombre1/2`); consolidação das sequências de clique
do `--edicao`; e o `iguala_nombres`.

### Riscos, e o que cada um custa se acontecer

1. **Drag-and-drop LCL × VCL** (passagem 13). `OnDragOver`/`OnDragDrop` não têm
   a mesma ordem de evento nos dois frameworks, e é o único ponto do plano onde
   a régua de pixel pode não valer. **A WTE-TASK-13 mediu ordem de evento —
   usar aquela medição, não supor.** Se divergir, o lote de tática vira
   divergência deliberada registrada em vez de paridade.
2. **`iguala_nombres` pode não fechar.** Três hipóteses já caíram. A próxima
   linha é comparar o que a LCL desenha para `TSpeedButton` desabilitado **com
   e sem** `ParentFont = False` — a única diferença que sobrou entre ele e o
   vizinho que acinzenta certo. Se não fechar, vira entrada da
   [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), com dono escrito.
3. **Cada lote novo custa uma varredura de coordenada** para o `--edicao`. A
   das barras precisou varrer `y` para achar a trilha, porque a janela do port
   deriva ~6 px descendo (o `calibra()` já media isso). Não é acidente: é o
   preço fixo de estender a régua a um grupo novo.

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-12 — **primeira passagem, parcial.** A tarefa
  continua `⬜ Pendente`: 2 dos 28 handlers têm spec e Pascal.

- **Resumo do que foi feito:**

  Duas coisas, e a segunda vale mais que a primeira.

  **O grupo das barras — `sel_barraClick` e `track_barraChange`.** São os dois
  menores do grupo (61 e 166 bytes), foram lidos inteiros, e o que eles
  revelaram organiza a fase 4: **existe um buffer de edição, e ele não é
  cache**. Os cinco bytes das barras não vão da imagem para a tela; vão para
  `0x00434592`, e é dali que sai a largura. Três handlers o tocam — a carga
  enche (`0x0040cf79`), o `track_barraChange` grava (`0x0040caa1`), e o
  `boton_barras2isoClick` **lê para gravar na imagem** (`0x0040cb3d`).

  Sem esse buffer no port, editar mudaria o pixel e a gravação escreveria o
  valor velho — e o golden acusaria a **gravação** por um defeito que é da
  edição. Entrou como `BarrasEmEdicao` no `.aux.inc`, separado de
  `Jogo.teams[].bar_*`. A coincidência dos quatro endereçamentos virou guarda
  no [`check_barras.py`](../../wte/tools/check_barras.py), junto com a
  conferência de que `11*v + 9` é **a mesma sequência de bytes** na carga e na
  edição — se divergirem, uma barra carregada e uma editada com o mesmo valor
  deixam de ter a mesma largura, e a comparação de tela passa a medir a coisa
  errada sem avisar.

  **A dívida sem dono da WTE-TASK-25 fechou: `TControl::SetEnabled` é
  virtual.** A 25 encerrou registrando que o símbolo tem **zero** `call rel32`
  na `.text` e que não há escrita direta em `FEnabled` — e por isso a seção
  Saída da spec do `lista_equiposChange` desceu de `disassembly lido` para
  `nao medido`, e depois só até `observacao de tela`. A resposta estava nos
  bytes do próprio handler: o original carrega o VMT em `[obj]` e chama
  `call DWORD PTR [reg+0x64]` — três vezes só ali (`0x0040ce9b`, `0x0040cee9`,
  `0x0040d05c`). Chamada virtual não deixa `call rel32`; **a busca procurava a
  forma errada.**

  O slot é medido, não afirmado: o valor exportado de
  `@Controls@TControl@SetEnabled$qqro` aparece a `0x64` bytes do início do VMT
  em **108 classes** do `vcl60.bpl`, com o nome de cada uma lido de
  `[vmt - 0x2c]` — entre elas `TRadioButton`, `TComboBox`, `TStaticText` e
  `TImage`, que são as que o `MainForm` instancia. Virou conferência de build
  no `sonda_dorsal.py --check`, que já era o tool que fala `.bpl`. A seção
  Saída voltou a `disassembly lido`.

- **O achado que desbloqueia o resto da task: o teclado chega ao port.**

  O `golden_run_laz.sh` **reprovava com código 5** qualquer roteiro com
  `! tecla` ou `! texto`, apoiado na medição da
  [WTE-TASK-13](/docs/tasks/13-trace-de-eventos.md) de que o GTK2 sem
  gerenciador de janela nunca se considera ativo. Metade desta task — os cinco
  `KeyPress` de nome, os de número, e o critério "limpar campo com `End` /
  `shift+Home` / `BackSpace`" — só existe por tecla. Com aquela recusa de pé,
  ela **não tinha gate nenhum**.

  A medição de 2026-08-09 da WTE-TASK-13 vale para o que ela testou (`xdotool
  key` sem foco, e `key --window`, que usa `XSendEvent` e o GTK2 descarta) e
  não para o caso que faltava: `xdotool windowfocus` é `XSetInputFocus` e não
  precisa de gerenciador. Foi assim que o `compara_tela.sh` da WTE-TASK-25
  passou a trocar de time com `Down` — a evidência já estava na árvore,
  contradizendo a recusa, e ninguém tinha cruzado as duas.

  Remedido por este caminho, pelo próprio harness: com `ROTEIRO_FOCO=1`,
  **3 `! tecla Down` produzem 3 disparos de `lista_equiposChange`** no
  `port-trace.log`. O driver ganhou o foco atrás de variável, ligada **só** no
  lado port — mexer no lado oráculo invalidaria o controle sem ganho, porque o
  Wine implementa o próprio foco. A recusa saiu, e no lugar dela ficou o
  registro do porquê: ela era a resposta certa para o que se sabia, e o que
  mudou não foi o port, foi a pergunta ter sido refeita.

- **Escopo conferido, e ele bate:** os 28 handlers desta task são as 44 linhas
  `grupo = edicao` do `published_methods.tsv` menos as 16 que já trazem dono na
  coluna `nota` (14 da WTE-TASK-29, 2 da WTE-TASK-32). A tabela de alvos do
  enunciado não divergia — só não dizia isso.

- **Arquivos criados/modificados:**
  - `wte/re/spec/MainForm.sel_barraClick.md`, `MainForm.track_barraChange.md`
    — as duas specs, `disassembly lido` nas seis seções
  - `wte/src/impl/ep2002_mainform.sel_barraClick.inc`, `.track_barraChange.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — `BarrasEmEdicao`
  - `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — a carga passa pelo
    buffer
  - `wte/tools/check_barras.py` — o buffer nos quatro handlers, o `11*v + 9`
    idêntico nos dois lados, a âncora do `sel_barraClick` contra o `campos.tsv`
  - `wte/tools/sonda_dorsal.py` — `TControl.SetEnabled = VMT[0x64]`
  - `wte/tools/roteiro.sh` — `ROTEIRO_FOCO`, e a lápide de `roteiro_usa_teclado`
  - `wte/tools/golden_run_laz.sh` — a recusa fora, o foco ligado
  - `wte/tests/roteiros/golden-01-arranque.port.txt` — as duas justificativas
    que caducaram
  - `wte/re/spec/MainForm.lista_equiposChange.md` — a Saída de volta a
    `disassembly lido`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 88,5% → **87,8%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos nesta passagem:**
  - `make -C wte check` — **rc 0**
  - `lazbuild wte/wte.lpi` — compila
  - `golden_check.sh --modo controle` — **PASSOU: byte-idêntico**
  - `golden_check.sh --modo positivo` — **detectou** o byte plantado em 405228,
    com o offset (`OFS_SQUAD_NUMBERS_NATIONAL+512`)
  - `golden_check.sh --modo golden` — **PASSOU**, só as duas faixas declaradas
    (`1921862`, `2012984..2012985`). Repetido depois de mexer no `roteiro.sh`

- **Problemas encontrados:**
  1. **O `Xvfb` do `:99` morreu no meio da passagem outra vez**, e outra vez o
     `golden_check.sh` falhou com **saída vazia e código 1** — o `set -e` o
     derruba no primeiro `xdotool`, antes de qualquer mensagem. É a mesma
     ocorrência da nona passagem da WTE-TASK-25, e continua sem causa. O
     achado de ferramenta continua de pé e continua não executado: **um script
     que depende do `:99` devia dizer "não há `:99`" antes de tentar dirigir
     janela.** Restaurado como estava (`Xvfb :99 -screen 0 1280x1024x24
     -nolisten tcp`, sem `-auth`).
  2. O padrão `mov eax,[ebx+imm32]` casava **duas** vezes no
     `sel_barraClick` — a âncora e a `track_barra` logo abaixo. A guarda exige
     casamento único, então reprovou em vez de ler o campo errado; o padrão
     passou a incluir o `sub esi,eax` que só a âncora tem. Mesma forma do
     problema 1 da terceira passagem da WTE-TASK-25.
  3. A guarda do slot de VMT foi testada contra o erro plantado antes de
     entrar: com `SLOT_SETENABLED = 0x60` ela devolve 2 e diz que **0 classes**
     casaram. Sem isso ela seria "guarda testada contra o erro errado", que a
     WTE-TASK-25 já pagou.

- **O que falta para esta task fechar:**
  - **26 dos 28 handlers**, sem spec: os 5 de nome, os 3 de número que sobram
    (`dorsalClick`, `dorsalMouseDown`, `scroll_dorsalChange`,
    `casilla_dorsalKeyPress`), os 2 de atributo, os 8 de mover jogador e os 7
    de tática;
  - **a régua de byte**, que depende da
    [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) — ver a seção
    "Verificação" acima. É decisão, não passagem;
  - **a régua de pixel para edição**: o `compara_tela.sh` leva os dois lados ao
    mesmo time e mede as cinco larguras, mas não edita nada. Estender é o que
    fecha `track_barraChange`, e é o próximo passo barato;
  - o comportamento de truncamento por campo, que alimenta a
    [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md);
  - **como a `TTrackBar` responde ao clique na trilha nos dois widgetsets.** O
    `PageSize` do comctl32 sob Wine e o do GTK2 podem não ser o mesmo, e a
    faixa é curta (`Max = 9`): um clique que ande 2 de um lado e 1 do outro
    produziria divergência de tela que não é do handler. Medir antes de
    escrever roteiro de edição de barra.

---

- **Executado em:** 2026-08-12 — **segunda passagem, ainda parcial.**

- **Resumo do que foi feito:**

  A decisão do usuário sobre a régua, executada — e com ela o primeiro par de
  handlers de edição **conferido contra o original**.

  **A régua de pixel para edição existe:** `compara_tela.sh --edicao`. Ela leva
  os dois lados ao time 2, marca `sel_barra1` ("Defesa") e clica na trilha da
  `track_barra`. Medido, ROM japonesa:

  | | oráculo | port |
  |---|---|---|
  | as cinco larguras, em px | `64, 75, 75, 75, 75` | `64, 75, 75, 75, 75` |
  | `defesa`, valor do jogo | 4 → **6** | 4 → **6** |
  | as outras quatro contra o `we2002_core` | 4 de 4 exatas | 4 de 4 exatas |

  **As duas metades importam, e por razões diferentes.** As quatro não editadas
  continuarem ancoradas no dump mostra que a edição não respingou; a editada
  ter mudado mostra que houve edição — sem isso, "os dois lados concordam"
  passaria com a tela intacta, que é o par que a
  [WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) ensinou a exigir. Do
  lado do port o script ainda exige do trace 1 `sel_barraClick` e o número
  previsto de `track_barraChange`.

  **O número que precisava ser medido antes de o roteiro existir era o passo do
  clique**, e ele fecha: clique na trilha não arrasta o cursor, **pagina**, e o
  `PageSize` do comctl32 sob Wine e o do `TTrackBar` da LCL sobre gtk2 são
  código diferente numa faixa curta (`Max = 9`). **Os dois andam +2 por
  clique** — 4 → 6 → 8, larguras 53, 75, 97. Se tivessem divergido, o roteiro
  de edição mediria divergência que não é do handler.

  E o valor esperado **não é literal no script**: sai do dump da camada de
  dados mais o passo. O único número escrito à mão é o passo, que é o que foi
  medido.

- **Duas coisas que a medição mostrou de graça:**

  1. **`Position :=` dispara `OnChange` na LCL.** A carga de time faz
     `track_barra.Position := ...`, e isso reentra no `track_barraChange` — que
     regrava o mesmo valor e redesenha a mesma largura, então é inofensivo,
     mas está na conta que o script confere. É a pergunta que o
     [`check_lcl_combo.py`](../../wte/tools/check_lcl_combo.py) respondeu para
     `TComboBox` (**não** dispara), com resposta oposta para `TTrackBar`.
  2. **As coordenadas de clique não são as mesmas nos dois lados abaixo de
     certa altura.** A `track_barra` do oráculo aceita clique em y 190..200 e a
     do port em y 199..207: o gtk2 desenha uma borda de 6 px que o Wine não
     desenha — o mesmo `(6, 6)` que o `calibra()` do `compara_tela.py` já
     media —, e a diferença cresce descendo a janela. `y = 200` é a
     intersecção, verificada nos dois. Vale para todo roteiro de edição desta
     task: **controle no rodapé do formulário pode não ter coordenada comum**,
     e nesse dia a saída é o `calibra()`, não o chute.

- **A decisão (b) alcançou o vocabulário de veredito, e tinha de alcançar.**
  `implementado` dizia "spec, Pascal, **golden** verde". Com a régua de byte
  morando na 27, nenhum handler de edição poderia ser `implementado` — nem os
  conferidos —, e o veredito passaria a medir a ordem das tasks em vez do
  estado do handler. Passou a dizer "a régua da task do handler verde", com uma
  tabela nomeando qual é qual por grupo, no
  [`GABARITO.md`](../../wte/re/spec/GABARITO.md). A metade por byte não sumiu:
  virou linha de critério de conclusão da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), com o par
  gravação × edição escrito.

  Os dois handlers foram de `aberto` para `implementado`. O índice vai a
  **3 `implementado`** de 96.

- **Arquivos criados/modificados:**
  - `wte/tools/compara_tela.sh` — o modo `--edicao`, o `edita_barra` comum aos
    dois lados, as duas exigências de trace, o valor esperado vindo do dump
  - `wte/tools/compara_tela.py` — `--editada N=V`, `confere_editada`, a barra
    editada fora da conferência contra o dump
  - `wte/re/spec/GABARITO.md` — a régua por grupo
  - `wte/re/spec/MainForm.sel_barraClick.md`, `MainForm.track_barraChange.md` —
    `implementado`, com a medição
  - `docs/tasks/26-handlers-de-edicao.md`, `docs/tasks/27-handlers-de-gravacao.md`
    — a decisão, nos dois lados
  - `wte/re/spec/INDICE.md` — regerado

- **Gates medidos:** `make -C wte check` rc 0; `compara_tela.sh --edicao` rc 0.

- **Problemas encontrados:**
  1. **`pkill -f "wte/build/wte"` mata o próprio shell** que roda o comando —
     o padrão casa a linha de comando do `zsh` que o executa. O sintoma foi
     uma série de comandos terminando em código 1 sem saída nenhuma, que
     parecia o `:99` caindo de novo. Os scripts do repositório não sofrem
     disso (o `limpa()` do `compara_tela.sh` roda dentro do próprio script,
     que morre junto e por último), mas medição de apoio à mão sofre. Prefira
     `pgrep -x wte` / `kill <pid>`.
  2. Primeira estimativa da coordenada da trilha (`y = 196`) veio de olhar uma
     captura ampliada e **errou por 11 px** no lado port: o clique caía acima
     do controle e nada acontecia, sem erro. Trocado por varredura — clicar em
     vários `y` e ver qual dispara o handler no trace.
  3. `sel_barra0` nasce `Checked = True` no `.dfm`, então clicar nele **não**
     dispara `OnClick`. A primeira tentativa de exercitar o `sel_barraClick`
     mediu zero disparo e parecia defeito do port. O rádio de prova passou a
     ser o `sel_barra1`.

- **O que falta para esta task fechar** *(revisado)***:**
  - **26 dos 28 handlers**, sem spec;
  - o comportamento de truncamento por campo (WTE-TASK-36);
  - estender o `--edicao` aos grupos que vierem — cada um precisa da sua
    sequência de cliques medida, como esta precisou.

---

- **Executado em:** 2026-08-12 — **terceira passagem, ainda parcial.** Abertura
  do lote de **número**, pelo defeito que já estava medido e sem dono.

- **Resumo do que foi feito:**

  **O off-by-one dos 23 `dorsalN` acabou.** A
  [CORR-WTE-057](/docs/tasks/CORR-WTE-057.md) tinha medido, na tela, que o port
  mostra o byte cru onde o original mostra byte + 1, e deixou o conserto sem
  dono — "é defeito de comportamento, pede correção própria". O dono é este
  lote, e a regra foi conferida nos **dois oráculos** antes de uma linha ser
  escrita:

  - **`wte.exe`:** a rotina do número (`0x00403f00`) termina em `inc eax` nos
    **três** ramos — `0x00403f65` (o time 48, que tem caminho próprio),
    `0x00403fae` (clube de ML), `0x0040403f` (seleção). Não é efeito de um ramo
    só, que é o que uma leitura apressada concluiria olhando um deles;
  - **`newWe2002`**, byte-idêntico ao `ed.exe`: `+ 1` ao exibir
    (`src/app/TeamView.cpp:195`), `- 1` ao gravar (`:468`), nas três famílias.

  E a correção foi verificada **sem abrir janela**: os `raw_numbers` do
  `ml_teams[0]` que o `dump_estado.pas` carrega da ROM japonesa, mais 1, dão
  exatamente os 23 números que a CORR-WTE-057 tinha lido da tela do oráculo.
  Terceira ponta outra vez — dado, tela do original, Pascal.

  **A consequência vale para o resto do lote e está anotada no código:** a
  imagem guarda base zero, a tela mostra base um, então quem **gravar** número
  desfaz a soma.

- **O modelo do lote, medido (specs ainda por escrever):**

  - **`dorsalClick`** (`0x00410a74`) não edita nada: sai se
    `lista_equipos.ItemIndex < 0`; extrai o índice do **nome** do componente
    (`Copy(Name, 7, 2)` sobre `'dorsalNN'`, não do `Tag` nem do ponteiro);
    seleciona o jogador em `lista_jugadores_1`; chama a rotina de realce
    (`0x0040b188`, o `MarcaCamisa` que já está em Pascal); posiciona o
    `ficha_dorsal` ao lado do rótulo clicado; e copia o número atual para lá.
  - **A regra de validação que o enunciado desta task pedia é imposta pelo
    widget, não por `if`:** `dorsalClick` chama
    `TScrollBar::SetMax` no `scroll_dorsal` com **99** quando o índice do time é
    > 62 (clube de ML) e com **32** caso contrário. Casa com a mensagem de erro
    que a WTE-TASK-05 mapeou (`[33 ... 99] somente na Master`) e com o clamp em
    32 do `newWe2002`.
  - **`scroll_dorsalChange`** (`0x00402b58`) é uma linha:
    `etiq_dorsal.Caption := scroll_dorsal.Position - Min + 1`. Os
    deslocamentos saíram do `vcl60.bpl` pelo método do `sonda_dorsal.py` —
    `TScrollBar.FMin = 0x20c`, `FMax = 0x210`, `FPosition = 0x214`, deduzidos de
    quais campos `SetMin`, `SetMax` e `SetPosition` tocam. Com `Min = 1` a conta
    é a identidade; o autor escreveu a forma geral.
  - **E a gravação do número não é desta task:** quem leva o valor de volta é o
    `BitBtn1Click` do `ficha_dorsal` (`0x00402b40`), que o
    `published_methods.tsv` põe no grupo `auxiliar` — a
    [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md). Mais um par que
    atravessa task, como o das barras com a 27.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.aux.inc` — o `+ 1` em `NumeroDaCamisa`, com
    a evidência dos dois oráculos e o aviso para quem for gravar
  - `wte/re/spec/MainForm.lista_equiposChange.md` — o defeito fechado, com a
    conferência

- **Gates medidos:** `lazbuild` compila; os 23 números do port batem com a
  linha `oráculo` da CORR-WTE-057, conferidos contra o `dump_estado.pas`.

- **O que falta neste lote:** specs e Pascal de `dorsalClick`,
  `dorsalMouseDown`, `scroll_dorsalChange` e `casilla_dorsalKeyPress`; o buffer
  de edição do número em `.data`, se houver (as barras têm um, e a simetria
  sugere que sim); e estender o `--edicao` para medir os 23 rótulos — hoje eles
  só saem na montagem, para olho humano.

---

- **Executado em:** 2026-08-12 — **quarta passagem, ainda parcial.** O lote de
  número, mais um handler do lote de nome que veio de graça.

- **Resumo do que foi feito:**

  Cinco handlers com spec e Pascal: `dorsalClick`, `dorsalMouseDown`,
  `scroll_dorsalChange`, `casilla_dorsalKeyPress` e — porque estava no mesmo
  bloco de disassembly — `casilla_nombreKeyPress`. O grupo vai de **2 para 7 de
  28**; o índice de specs vai a **6 `implementado`** de 96.

  **A resposta à pergunta "onde está o buffer de edição do número" é: não há
  um.** As barras têm `0x00434592` porque a gravação delas é um botão separado.
  O número não: o `dorsalClick` **grava na hora**, quando o modal fecha.

  **E essa é a descoberta que muda a classificação do handler.** `0x00404048` é
  a irmã escritora da rotina de leitura `0x00403f00` — mesmos três ramos, mesma
  aritmética de endereço —, recebe número, time, slot e o arquivo aberto, faz
  `add al,0xff` (o `- 1` da base zero, confirmando de novo a regra da terceira
  passagem) e escreve **aquele trecho**, sem nada parecido com um `Save` do
  banco inteiro.

  É o primeiro handler que o `published_methods.tsv` classifica como `edicao` e
  que grava na imagem. A classificação não está errada — o que ele faz é
  edição, e a gravação é uma chamada no fim —, mas **o par atravessa task**,
  como o das barras. O Pascal escrito faz tudo menos a gravação, e a metade que
  falta está no critério de conclusão da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md). Escrevê-la aqui
  também exigiria a primeira escrita **pontual** do port: o
  `we2002_database.pas` gerado sabe `Save` do banco inteiro, não "escreve estes
  dois bytes aqui".

  **A regra de validação que o enunciado desta task pedia não é um `if`.** É o
  `Max` da barra de rolagem da janelinha: 99 para clube de Master League
  (índice > 62), 32 para seleção. O usuário não digita número inválido porque
  **não há onde digitar** — a escolha é uma barra com faixa fixada na abertura.
  Casa com a mensagem que a WTE-TASK-05 mapeou e com o teto de 32 do
  `newWe2002`.

- **O erro que cometi e que só a semântica cruzada desmentiu:**

  Os deslocamentos de campo do `TScrollBar` saíram errados na primeira leitura.
  Varri os prólogos de `SetMin`/`SetMax`/`SetPosition` atrás de
  `mov reg,[this+disp]` e concluí `FMin = 0x20c`, `FMax = 0x210`,
  `FPosition = 0x214` pela interseção de quais campos cada uma toca. **Com
  esses valores a conta do `scroll_dorsalChange` vira `Position - Min + 1`,
  que com `Min = 1` é a identidade — plausível, e a spec teria fechado assim.**

  O que desmentiu foi o handler vizinho: o `dorsalClick` faz
  `Position := [0x214] - numero + 1`, e só sob `[0x214] = FMax` as duas contas
  se cancelam e o rótulo mostra o número escolhido. Refeita a leitura pelo
  caminho certo — as três não escrevem campo nenhum, são invocações finas do
  mesmo `SetParams(Position, Min, Max)`, e a ordem dos argumentos identifica os
  três: **`FPosition = 0x20c`, `FMin = 0x210`, `FMax = 0x214`**.

  É a armadilha 1 do projeto por outra porta. Interseção de campos tocados é
  heurística, e heurística que "fecha" num caso particular (`Min = 1`) é a que
  passa. Quem decide é a semântica cruzada de dois handlers, não a leitura
  isolada de um.

- **Outros três números que a leitura apressada erraria:**
  1. O índice da camisa sai do **nome** do componente (`Copy(Name, 7, 2)` sobre
     `'dorsalNN'`), não do `Tag` nem do ponteiro.
  2. `dorsalMouseDown` só reage a `mbRight`, e chama o `mostrar_jugadorClick`
     passando **`mostrar_jugador_1`** como `Sender` — é a cadeia do nome que faz
     aquele handler escolher o lado titular, então passar outro botão abriria a
     ficha do time errado.
  3. O título da janelinha é `' ' + nome`: a cadeia em `0x00425077` tem **um**
     caractere. O `Caption = 'Number'` do DFM é de projeto e some no primeiro
     clique.

- **Arquivos criados/modificados:**
  - `wte/re/spec/` — 5 specs novas (`MainForm.dorsalClick`,
    `MainForm.dorsalMouseDown`, `ficha_dorsal.scroll_dorsalChange`,
    `jugador.casilla_dorsalKeyPress`, `jugador.casilla_nombreKeyPress`)
  - `wte/src/impl/` — os 5 `.inc`, mais `ep2002_mainform.uses` e
    `ep2002_dorsal.uses`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 87,6% → **86,0%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` compila.

- **O que fica aberto neste lote, com a razão:**
  - `dorsalClick` — `aberto`: falta a gravação, que é da 27;
  - `casilla_dorsalKeyPress` — `aberto`: o `SetFocus` dele é condicionado a
    `DWORD[0x00433614 + 44*global] <> 0`, e o que essa tabela guarda não foi
    medido. O port foca **sempre**, o que é divergência declarada. Medir sai
    barato quando a ficha do jogador estiver sendo preenchida;
  - os dois `KeyPress` da ficha ainda **não são exercitáveis de verdade**: a
    ficha abre, mas vazia — preenchê-la (`0x00404820`, `0x0040756c`) é o
    obstáculo que os lotes de atributo e de tática também têm pela frente.

---

- **Executado em:** 2026-08-12 — **quinta passagem, ainda parcial.** O lote de
  **nome**: os três `edit_nombreNKeyPress` e o `iguala_nombresClick`. O grupo
  vai de **7 para 11 de 28**; o índice a **9 `implementado`** de 96.

- **Resumo do que foi feito:**

  **Os três campos de nome não são três cópias do mesmo handler**, e a
  diferença estava no tamanho: 88, 88 e **32** bytes. O terceiro é outro
  bicho —

  | | `nombre1` | `nombre2` | `nombre3` |
  |---|---|---|---|
  | aceita | letra, dígito, `.`, espaço | idem | **só alfanumérico** |
  | `Return` | foca `nombre2` | foca `nombre3` | **não faz nada** |
  | teste | faixa a faixa, à mão | idem | `isalnum` da RTL |

  As duas diferenças fazem sentido no dado, e é uma **confirmação
  independente** de um achado da WTE-TASK-25: o terceiro campo é a
  **abreviatura** (`abbreviations[0]`, `MaxLength = 3` no DFM), não `names[2]`.
  A 25 descobriu isso comparando telas de um clube de ML; aqui o mesmo fato
  vem do código, por outro caminho.

  **`iguala_nombresClick`** copia `Nome1` nos outros dois, truncando cada um ao
  que cabe: `Copy(..., 1, global - 1)` no segundo e `Copy(..., 1, 3)` no
  terceiro.

- **Dois achados que valem mais que os handlers:**

  1. **O port não põe `MaxLength` em `edit_nombre1` nem em `edit_nombre2`.** O
     original põe, ao carregar a imagem: `edit_nombre1.MaxLength :=
     DWORD[0x00433a10] div 2` e `edit_nombre2.MaxLength := DWORD[0x00433b48] -
     1` (`0x0040cc38` e `0x0040cc48`). No port os dois aceitam texto de
     qualquer tamanho. **Nenhum teste atual pega isso** — é comportamento, não
     pixel —, e o `edit_nombre3` escapa por acaso, porque o `MaxLength = 3`
     dele está no DFM e o `.lfm` herda. É divergência aberta e entrada da
     [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md).
  2. **A global `0x00433b48` não é escrita por `mov` nenhum.** Varri o `.text`
     inteiro atrás de `mov ds:0x433b48,reg` e de `mov DWORD PTR
     ds:0x433b48,imm`: **zero**. Ela é preenchida por outro caminho — ponteiro,
     ou estrutura carregada em bloco. O valor em execução continua por medir, e
     o port usa **19**, tirado do tamanho do campo na camada de dados (`names`
     é `array[0..19] of AnsiChar`). É o método da §4.2 outra vez, mas **sem
     confirmação cruzada** desta vez, e está dito assim na spec.

- **O `iguala_nombres` continua com o defeito da CORR-WTE-057, e agora com mais
  uma hipótese derrubada.** O port não o desabilita no time-modelo (518 px de
  mudança no oráculo, **0** no port). Comparei o `.lfm` dele com o do vizinho
  `boton_nombres2iso`, que acinzenta certo: mesmo `TSpeedButton`, mesmo
  `Flat = True`, mesmo `Enabled = False` de nascença, os dois com `Glyph`. A
  **única** diferença é `ParentFont = False` mais as propriedades de fonte, o
  que não explica glifo que não acinzenta. Continua sem causa medida, e está
  registrado na spec do `iguala_nombresClick`.

- **Arquivos criados/modificados:**
  - `wte/re/spec/` — 4 specs novas (`edit_nombre1/2/3KeyPress`,
    `iguala_nombresClick`)
  - `wte/src/impl/` — os 4 `.inc`; `TAMANHO_DO_NOME` no `.aux.inc`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 86,0% → **85,2%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` compila.

- **Aberto neste lote:** `iguala_nombresClick`, pelo limite não medido e pelo
  defeito de habilitação. Os três `KeyPress` fecham `implementado` — são
  filtros puros, sem estado e sem gravação.

---

- **Executado em:** 2026-08-12 — **sexta passagem: medição do lote de mover, e
  parada consciente.** Nada implementado nesta; o produto é o tamanho do
  problema, medido.

- **Por que parar aqui em vez de emendar o lote:**

  Os 8 handlers de mover jogador parecem pequenos — 312 a 981 bytes — e não
  são. Medido pelo [`dump_auxiliares.py`](../../wte/tools/dump_auxiliares.py),
  eles alcançam **24 rotinas internas**, e **8 delas somam 3.585 bytes sem
  papel lido**:

  | rotina | bytes | chamadores no lote |
  |---|---|---|
  | `0x00404820` | 1.459 | 6 |
  | `0x00407338` | 561 | 1 |
  | `0x00407110` | 552 | 1 |
  | `0x00406fe0` | 301 | 1 |
  | `0x00403e20` | 224 | 4 |
  | `0x0040b934` | 181 | 1 |
  | `0x004046e8` | 164 | 6 |
  | `0x00408460` | 143 | 1 |

  Escrever os 8 corpos sem ler essas oito seria inventar. É a lição da quarta
  passagem da WTE-TASK-25 — *lista de auxiliar escrita à mão erra da forma que
  não aparece* — aplicada antes de errar, e não depois.

- **O que já foi lido do lote, e vale para quem continuar:**

  `paderechaClick` (`0x0040e5e8`, 312 B) é o representante da família. A forma:

  ```text
  guarda := lista_jugadores_2.ItemIndex
  0x004046e8(time1, slot1, modo := 1, arquivo)
  esi := 0x00404820(1, time2, slot2, arquivo)
  se esi >= 0:
      0x0040b2d8(lista_equipos_2, lista_jugadores_2)   ' repovoa a lista destino
      lista_jugadores_2.<vmt+0x88>()
      lista_jugadores_2.ItemIndex := guarda            ' restaura a selecao
      0x004046e8(time2, slot2, modo := 2, arquivo)
  contador_ml.Text := IntToStr(WORD[0x004335c0])
  0x00403e20(esi)
  ```

  Três coisas que já dá para afirmar:

  1. ~~**`0x004046e8` tem um argumento de MODO** (`1` na leitura, `2` na
     escrita), e é o par ler/gravar de um jogador inteiro.~~ **Errado, e a
     sétima passagem corrigiu:** o `1`/`2` é **índice de buffer**, não modo, e
     as duas chamadas são **leituras**. Ver abaixo. Os 164 bytes dela continuam
     sendo o alvo mais barato do lote, e foram lidos.
  2. **`0x00404820` devolve valor e o valor governa o fluxo** (`< 0` pula o
     bloco). A [spec do `mostrar_jugadorClick`](../../wte/re/spec/MainForm.mostrar_jugadorClick.md)
     a descrevia como "enche a ficha", herdado da WTE-TASK-25; ela faz mais que
     isso, e chama a escritora de número de camisa `0x00404048` que a quarta
     passagem mediu. **A descrição herdada está incompleta**, e isso está
     anotado aqui em vez de corrigido na spec — corrigir exige ler os 1.459
     bytes.
  3. **O contador de slots livres de ML é atualizado aqui**, de
     `WORD[0x004335c0]` — a mesma global que o `sonda_dorsal.py` já conhecia. É
     a [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) aparecendo por
     dentro do lote de mover.

- **E os dois lotes que faltam depois deste têm o mesmo obstáculo, maior:** os
  2 de atributo (no `jugador`) e os 7 de tática (no `estrategia`) só são
  exercitáveis com o formulário **preenchido**, e preencher é `0x00404820`
  (1.459 B), `0x0040756c` (1.275 B) e `0x0040a0b4` — que a WTE-TASK-25 já tinha
  nomeado como dívida desta task.

- **Balanço honesto do estado da WTE-TASK-26:**

  | lote | handlers | estado |
  |---|---|---|
  | barras | 2 | **fechado**, conferido por pixel |
  | número | 4 | spec e Pascal; 2 `aberto` com dono nomeado |
  | nomes | 5 | spec e Pascal; 1 `aberto` |
  | mover | 8 | **medido, não implementado** — 3.585 B por ler |
  | atributos | 2 | bloqueado no preenchimento da ficha |
  | tática | 7 | bloqueado no preenchimento do `estrategia` |

  **11 de 28 com spec e Pascal.** O que falta não é mais do mesmo: são ~6,3 KB
  de disassembly de rotina interna, que é trabalho de outra ordem que os
  filtros de tecla desta passagem.

- **Arquivos criados/modificados:** só documentação — este arquivo.

---

- **Executado em:** 2026-08-12 — **sétima passagem.** A rotina mais barata do
  lote de mover, lida — e ela fechou uma pergunta de outro lote e derrubou uma
  afirmação minha da passagem anterior.

- **`0x004046e8`, 164 bytes: carrega um jogador para um buffer de 44 bytes.**

  ```text
  0x00404374(indice, arquivo)                 ' calcula os offsets deste slot
  le 10 B de DWORD[0x00433608 + 44*i] para 0x004335ec + 44*i   ' nome
  le 12 B de DWORD[0x0043360c + 44*i] para 0x004335f6 + 44*i   ' atributos
  se DWORD[0x00433614 + 44*i] <> 0:
      le  1 B daquele offset      para 0x00433604 + 44*i
  senao:
      BYTE[0x00433604 + 44*i] := 50
  ```

- **A afirmação da sexta passagem estava errada, e o erro é instrutivo.** Eu
  tinha lido o `1` e o `2` das duas chamadas do `paderechaClick` como **modo**
  — ler e gravar —, porque a sequência "chama com 1, faz alguma coisa, chama
  com 2" tem exatamente essa cara. Não é: `1` e `2` indexam um vetor de passo
  44, e **as duas chamadas são leituras** — a de origem e a de destino, cada
  uma para o seu buffer. Quem grava é a `0x00404820`, e é ela que sobrou por
  ler.

  O que desmentiu foi a aritmética, não a leitura de mais código: `lea` +
  `lea` + `shl 2` dá `44*ebx`, e passo 44 sobre um argumento que vale 1 ou 2 é
  índice, não modo. **Argumento pequeno com dois valores distintos parece
  enumeração de modo, e essa é a leitura barata que erra.**

- **E o passo 44 fechou a pergunta em aberto do `casilla_dorsalKeyPress`.** A
  quarta passagem tinha deixado `DWORD[0x00433614 + 44*global] <> 0` como
  tabela não identificada. É a **terceira coluna de offsets deste mesmo
  buffer**: se o offset for zero, o campo **não existe na imagem** para aquele
  jogador — a `0x004046e8` escreve `50` no lugar de ler, e o handler não move o
  foco para o `casilla_precio`. Ou seja, o `Return` só avança para o preço
  quando o jogador **tem** o byte; para os demais o valor é sintético e o
  original não deixa o cursor chegar lá.

  Sai daqui um número para a [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md):
  **50 é o preço que a ficha mostra quando o jogador não tem o campo.**

  E sai a identidade da global `0x004335c4`: é **qual buffer de jogador está em
  edição**, com `1` e `2` sendo os dois lados que os handlers de mover usam.

- **Uma descrição herdada que ficou sob suspeita:** a
  [spec do `mostrar_jugadorClick`](../../wte/re/spec/MainForm.mostrar_jugadorClick.md)
  descreve `0x00404820` como "enche a ficha", herdado da WTE-TASK-25. Ela
  devolve valor que governa fluxo, chama a escritora de número de camisa
  (`0x00404048`) e a escritora de bytes (`0x00403400`) — comportamento de quem
  **grava** um jogador, não de quem preenche tela. **Não corrigi a spec**:
  corrigir exige ler os 1.459 bytes, e afirmar o contrário sem ler seria trocar
  um palpite por outro. Fica anotado como suspeita, com a evidência.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_auxiliares.py` — `PAPEIS` ganhou 5 rotinas medidas nesta
    sessão (`0x00403400`, `0x00403f00`, `0x00404048`, `0x004046e8`,
    e o papel corrigido das vizinhas); `auxiliares.md`/`.tsv` regerados
  - `wte/re/spec/jugador.casilla_dorsalKeyPress.md` — a condição identificada
  - este arquivo — a correção da sexta passagem

- **Gates medidos:** `make -C wte check` rc 0.

- **`casilla_dorsalKeyPress` continua `aberto`**, por motivo menor e nomeado: o
  port não tem o buffer de 44 bytes, então move o foco sempre. O buffer entra
  com o lote de mover, e a spec fecha junto.

---

- **Executado em:** 2026-08-12 — **oitava passagem.** `0x00404820`, o nó de
  1.459 bytes, lido o bastante para responder o que travava dois lotes.

- **Ela GRAVA um jogador, e a suspeita da passagem anterior estava certa.**

  ```text
  0x00404820(eax = buffer de origem, edx = time destino, ecx = slot destino, arquivo)

    0x00404374(time, slot, buffer 0)          ' offsets do DESTINO, no buffer 0
    se buffer[origem].identidade = buffer[0].identidade
       e BYTE[0x00423168] = 0:  devolve -2
    ...
    grava 10 B de nome        em DWORD[buffer0 + 0x1c]
    grava 12 B de atributos   em DWORD[buffer0 + 0x20]
    se DWORD[buffer0 + 0x28] <> 0:
        grava 1 B do campo condicional
  ```

  **O layout de 44 bytes fecha com o que a sétima passagem derivou pelo outro
  lado**, e isso é a conferência que dá confiança nos dois:

  | campo | do lado da leitura (`0x004046e8`) | do lado da escrita (`0x00404820`) |
  |---|---|---|
  | nome, 10 B | `0x004335ec + 44*i` | `+0x00` |
  | atributos, 12 B | `0x004335f6 + 44*i` | `+0x0a` |
  | identidade | — | `+0x16`, `+0x17` |
  | condicional, 1 B | `0x00433604 + 44*i` | `+0x18` |
  | tipo | — | `+0x19` |
  | offset do nome | `0x00433608 + 44*i` | `+0x1c` |
  | offset dos atributos | `0x0043360c + 44*i` | `+0x20` |
  | offset do condicional | `0x00433614 + 44*i` | `+0x28` |

  As duas leituras foram feitas separadas, uma de cada rotina, e **os oito
  deslocamentos batem**.

- **E a regra de validação do lote de mover apareceu inteira, com as mensagens
  do usuário.** `0x00403e20` recebe o código de retorno, soma 2 e indexa uma
  tabela de salto de cinco entradas:

  | código | mensagem |
  |---|---|
  | `-2` | **"It's the same player in both teams..."** |
  | `-1` | **"You need at least 1 memory block free to do that"** |
  | `0`, `1`, `2` | nada |

  O `-2` é a comparação de identidade acima — mover um jogador para um time que
  já o tem é recusado, **a não ser que `BYTE[0x00423168]` seja diferente de
  zero**, uma chave que desliga a checagem. O `-1` é o contador de blocos
  livres de Master League, que é a
  [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) aparecendo aqui pela
  segunda vez.

  É o que o enunciado desta task pede na seção "Validação": *a mensagem é o
  atalho para a regra*. Aqui as duas mensagens **e** a regra estão medidas.

- **Duas linhas de spec corrigidas.** A
  [spec do `mostrar_jugadorClick`](../../wte/re/spec/MainForm.mostrar_jugadorClick.md)
  dizia `0x004046e8` "não lida" e `0x00404820` "enche a ficha" — escritas na
  décima passagem da WTE-TASK-25 a partir do que o handler *parecia* precisar.
  As duas estão trocadas pelo que foi medido. **O que aquele handler faz com
  uma rotina de gravação continua sem resposta** e está escrito como pergunta,
  não como descrição plausível: responder exige seguir o fluxo, não só saber o
  que a rotina faz.

- **A guarda do `dump_auxiliares.py` recusou um papel meu, e estava certa.**
  Tentei registrar `0x00403e20` no `PAPEIS`; ela reprovou com *"PAPEIS descreve
  rotina que o grupo de carga nao chama"*. É verdade — aquela rotina é do lote
  de mover, e o gerador cobre o grupo de carga. O papel ficou em comentário, no
  lugar certo, e a medição está aqui.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_auxiliares.py` — `0x00404820` no `PAPEIS`, e o porquê de
    `0x00403e20` ficar de fora; `auxiliares.md`/`.tsv` regerados
  - `wte/re/spec/MainForm.mostrar_jugadorClick.md` — as duas linhas corrigidas
  - este arquivo

- **Gates medidos:** `make -C wte check` rc 0.

- **O que isso destrava:** os 8 handlers de mover deixam de depender de leitura
  para depender de **escrita de código** — as duas rotinas centrais têm papel,
  layout e regra de erro medidos. Sobram delas `0x00407338` (561 B),
  `0x00407110` (552 B) e `0x00406fe0` (301 B), que são do `flechasapaClick` e
  do `parribaClick`, não da família de quatro botões.

---

- **Executado em:** 2026-08-12 — **nona passagem, ainda parcial.** A família de
  quatro botões de mover jogador, com spec e Pascal. O grupo vai de **11 para
  15 de 28**.

- **Resumo do que foi feito:**

  Os quatro — `paderechaClick`, `paizquierdaClick`, `paderecha2Click`,
  `paizquierda2Click` — mais o buffer de 44 bytes, a `CarregaJogador`
  (`0x004046e8`), a `PreparaBuffer` (`0x00404374`) e a `MostraCodigo`
  (`0x00403e20`) com as duas mensagens.

  **E a passagem começou custando 881 bytes que o plano dizia custar zero.** O
  quadro das seis passagens afirmava "**0 B**, e não depende de mais nenhuma
  leitura: as duas rotinas centrais foram medidas na sétima e na oitava
  passagens". Não foi o que aconteceu: a sétima mediu a `0x004046e8` e a oitava
  a `0x00404820`, mas as duas **chamam** a `0x00404374`, que nenhuma das duas
  leu — ela é quem calcula a identidade, o tipo e as três colunas de offset.
  Sem ela, "a comparação de identidade (`+0x16`, `+0x17`)" que o plano mandava
  escrever seria comparar dois campos sem saber o que os enche.

  É o mesmo erro de forma da sexta passagem, uma camada acima: **rotina que já
  apareceu na lista de auxiliares não é rotina já lida**, e um plano escrito a
  partir de "as centrais estão medidas" não olha a lista de chamadas delas.

- **A identidade é um par de bytes, e o que ele significa muda com o time.**
  Lido da `0x00404374`:

  - seleção (índice `< 63`): identidade é literalmente `(time, slot)`;
  - clube de ML: identidade é o **par de vínculo** que a imagem guarda para
    aquele slot, lido do arquivo byte a byte — o mesmo par que o
    `ResolveMlLink` do `we2002_core` consome, com o mesmo `>= 23` separando
    vínculo de bloco próprio.

  Daí sai a regra do `-2` inteira: dois clubes de ML que apontem para o mesmo
  jogador de seleção têm a mesma identidade, e mover um para o outro é
  recusado. Comparar índice resolvido daria o mesmo resultado hoje; o original
  compara o par, e é o par que está reproduzido.

- **O achado que vale para outra task: os dois oráculos concordam na REGRA do
  campo condicional e discordam do ENDEREÇO.**

  A `0x00404374` zera a coluna `+0x28` — "este jogador não tem o campo na
  imagem", e aí a `0x004046e8` escreve o literal `50` — quando o índice do time
  cai entre `0x35` e `0x38` exclusive, isto é, **54 ou 55**. O
  `we2002_database.pas` gerado pula, ao carregar `cost`, exatamente os
  jogadores **1704..1749** — que é `462 + 54*23` até `462 + 56*23 - 1`, os
  mesmos dois times. Duas leituras independentes, mesma resposta sobre *quem*
  não tem o campo.

  Sobre *onde* ele está, elas divergem. O `wte.exe` calcula
  `0x2ece0c + 23*time + slot + 2*(time div 56)`; o `we2002_core` lê a partir de
  `OFS_COST_NATIONAL = 3067404 = 0x2ecc0c`, e põe o furo depois do time 53, não
  depois do 55. Medido sobre a cópia em `work/` da ROM europeia, os 64 bytes em
  cada um dos dois endereços são **diferentes**. Um dos dois está errado sobre
  o formato, e o `we2002_core` é o que já é byte-idêntico ao `ed.exe`.

  Encaminhado para a [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md), escrito
  como pergunta na spec do `paderechaClick`. Nesta task nada lê o valor.

- **Uma correção ao enunciado desta task, medida:** o `ficha_movertodos` **não
  é a tela do `paderechaeizquierdaClick`**. Ele é a confirmação dos dois botões
  de lote (`paderecha2Click`, `paizquierda2Click`) — o global `0x00432e48` que
  os dois carregam é o `_ficha_movertodos` exportado pelo próprio `.exe`, e o
  `paderechaeizquierdaClick` (`0x0040e304`) não toca nesse endereço. O
  enunciado foi corrigido no lugar, com a medição.

- **Os dois botões de lote não são o de um só num laço**, e as três diferenças
  são medidas: eles perguntam antes (`ShowModal` = `6` = `mrYes`, o mesmo `6`
  que o `.dfm` põe no `BitBtn1`), **descartam os 23 códigos de retorno** — mover
  um elenco para um time que já tenha um daqueles jogadores não produz mensagem
  nenhuma — e repovoam a lista de destino **incondicionalmente**.

- **Três slots de VMT, medidos e não inferidos.** O corpo chama
  `[vmt+0xc8]`, `[vmt+0xcc]` e `[vmt+0x88]` sobre os combos. Resolvidos no
  `vcl60.bpl` pelo método que o `sonda_dorsal.py` já usava para o
  `SetEnabled` — achar o VMT da classe e ler o slot: `TComboBox +0xc8` é
  `TCustomCombo::GetItemIndex`, `+0xcc` é `SetItemIndex`, `+0x88` é
  `TWinControl::Update`. E `TForm +0xe8` é `TCustomForm::ShowModal`, que
  confirma de outro lado o `+0xe8` que o `dorsalClick` já usava.

- **O que ficou de fora, com dono escrito:** a metade de gravação da
  `0x00404820` — os 10 B de nome, os 12 de atributos, o byte condicional, o
  número de camisa do slot 48, e a alocação de bloco de ML de onde sai o `-1`.
  É a opção A da decisão de 2026-08-12: os quatro fecham esta passagem com
  veredito `aberto` e a [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md)
  os promove. Sem a gravação, a lista de destino não muda, e por isso o
  `compara_tela.sh --edicao` não foi estendido a este lote — não haveria o que
  medir.

- **Uma lacuna declarada, e ela aparece na tela:** o `casilla_xmlibres` mostra
  zero, porque o contador de blocos livres de ML é da
  [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md). A linha do handler
  que o exibe está escrita, com a variável existindo e o dono nomeado — omitir
  a linha esconderia que o handler atualiza o rótulo.

- **Arquivos criados/modificados:**
  - `wte/re/spec/` — 4 specs novas (`MainForm.paderechaClick`,
    `paizquierdaClick`, `paderecha2Click`, `paizquierda2Click`)
  - `wte/re/spec/MainForm.mostrar_jugadorClick.md` — a única escrita do `.text`
    em `BYTE[0x00423168]` está dentro daquele corpo (`0x0040fd7a`), junto com o
    `+0x19 := 3` de `0x0040fd72`; registrado como medição, não como intenção
  - `wte/src/impl/ep2002_mainform.aux.inc` — `TBufferJogador`, `PreparaBuffer`,
    `CarregaJogador`, `MostraCodigo`, `GravaJogador` (metade de validação),
    `MoveUmJogador`, `MoveTodosOsJogadores`
  - `wte/src/impl/` — os 4 `.inc`, mais `ep2002_mainform.uses`
  - `wte/tools/dump_auxiliares.py` — papel da `0x00404374`; `auxiliares.md` e
    `.tsv` regerados
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 85,2% → **82,1%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild wte/wte.lpi` rc 0;
  `python3 -m unittest test_dump_auxiliares` 19 testes OK.

- **Problemas encontrados:**
  1. O custo de leitura anunciado pelo plano (**0 B**) estava errado por 881
     bytes — ver o resumo. O quadro das seis passagens foi corrigido no lugar.
  2. A primeira leitura do `paderechaClick` (sexta passagem) tratava o `1`/`2`
     como modo; a sétima já corrigira para índice de buffer. Esta passagem
     acrescenta o que faltava: o índice acompanha o **lado da tela**, não o
     papel na operação — `paderecha` carrega o buffer 1 e recarrega o 2,
     `paizquierda` faz o inverso. Ler como "origem/destino" fecharia igual nos
     dois handlers e quebraria no `paderecha2`.

- **O que falta para esta task fechar** *(revisado)***:**
  - **13 dos 28 handlers**, sem spec: os 4 de mover que sobram (`parriba`,
    `pabajo`, `paderechaeizquierda`, `flechasapa`), os 2 de atributo e os 7 de
    tática — passagens 10 a 13 do plano de fechamento;
  - o comportamento de truncamento por campo (WTE-TASK-36);
  - estender o `--edicao` aos grupos que puderem ser medidos por tela.

---

- **Executado em:** 2026-08-12 — **décima passagem, ainda parcial.** Três dos
  quatro handlers de mover que faltavam. O grupo vai de **15 para 18 de 28**.

- **Resumo do que foi feito:**

  `paderechaeizquierdaClick` (a troca), `parribaClick` e `pabajoClick` (a lista
  de descarte), com spec e Pascal. Mais a `RepovoaAsDuasListas` (`0x0040b934`),
  os 23 buffers de descarte, e as duas chaves de `.data` que o lote usa.

- **O quarto handler não é do `MainForm`, e por isso não entrou.** O
  `flechasapaClick` (`0x00408088`) é do formulário `jugador`, com **doze**
  botões `flechasapa1..12` ligados ao mesmo corpo. O plano o agrupava com os
  outros três por serem todos "mover", e as quatro rotinas que ele listava como
  custo de leitura desta passagem — `0x00407338`, `0x00407110`, `0x00406fe0`,
  `0x00408460` — são **dele**, não dos três do `MainForm`. Ele está bloqueado no
  mesmo preenchimento de ficha que os lotes de atributo e de tática, e foi para
  lá. Custo real desta passagem: 181 bytes, a `0x0040b934`.

- **O achado que quase virou um preço: `* 10000` é a escala do `Currency`.**

  O `parribaClick` multiplica `linha + 1` por 10.000 e converte o resultado. Lido
  como aritmética inteira, isso é um número de cinco dígitos, e num editor que
  tem preço de jogador como funcionalidade
  ([WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md)) a leitura "é o preço da
  transferência" teria passado.

  Não é. As duas rotinas foram identificadas: `0x0041978c` é o `__llmul` da RTL
  (o miolo são quatro `mul` de 32 bits — multiplicação, não divisão) e
  `0x00422402` é o thunk de `SysUtils::CurrToStr`, lido pelo nome importado.
  **10.000 é exatamente a escala do tipo `Currency` da Borland**, então a conta
  produz `'1'`, não `10000`.

  Quem confirma por fora é o próprio `.dfm`: `lista_descarte` nasce com as 23
  linhas `'  1 ...'` a `'23 ...'`, que é o que as duas larguras de legenda do
  corpo produzem. Terceira ponta — código, tipo da RTL, formulário.

- **A lista de descarte tem 23 buffers, e isso fecha o ramo `> 2` da
  `0x00404374`.** O `parribaClick` carrega para `lista_descarte.ItemIndex + 3` e
  o `pabajoClick` grava a partir do mesmo. A oitava passagem tinha visto aquele
  ramo — `+0x16 := 0xff`, `+0x19 := 3`, aplicados **depois** de tudo — sem saber
  de quem era. `0xff` não é índice de time válido, então jogador vindo do
  descarte **nunca** bate identidade com o destino: a recusa `-2` não alcança
  esse caminho, e isso é projeto, não acaso.

- **Duas chaves vizinhas em `.data`, e elas não são a mesma:**

  | endereço | quem escreve | quem lê |
  |---|---|---|
  | `0x00423168` | `0x0040fd7a`, dentro do `mostrar_jugadorClick` | `0x00404871` — desliga a recusa `-2` |
  | `0x00423169` | o `paderechaeizquierdaClick`, `1` antes e `0` depois das duas gravações | `0x00404bc4`, uma vez |

  Confundir as duas seria trocar "não recuse jogador repetido" por "estou no
  meio de uma troca". O que a segunda faz é da metade de gravação, e portanto da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md); aqui ela só é ligada e
  desligada na hora certa.

- **Três detalhes do original que pareceriam descuido e estão reproduzidos:**
  1. no caminho de erro da troca, o corpo **força `-2`** em vez de repassar o
     código — uma recusa por falta de bloco na primeira metade é anunciada como
     "It's the same player in both teams...";
  2. o `pabajoClick` repovoa o lado **esquerdo** também, mas só quando os dois
     combos mostram o mesmo time — sem isso a lista da esquerda continuaria com
     o nome antigo;
  3. o `pabajoClick` não limpa a linha da lista de descarte nem recarrega
     buffer: dar a seta para baixo duas vezes copia o mesmo jogador duas vezes.

- **E dois formulários de erro, não um.** O `pabajoClick` usa o `ficha_error2`
  (`0x00432e54`) para "Selecione um jogador para mover!!!", enquanto a
  `MostraCodigo` usa o `ficha_error` (`0x00432dd8` → `_ficha_error`). Usar um
  pelo outro mudaria a janela que o usuário vê.

- **Mais um slot de VMT medido:** `+0x50` é `TControl::GetEnabled`, resolvido no
  `vcl60.bpl` pelo mesmo caminho do `SetEnabled` em `+0x64`. É o teste que faz a
  `0x0040b934` repovoar o lado direito só quando ele está habilitado.

- **Arquivos criados/modificados:**
  - `wte/re/spec/` — 3 specs novas (`MainForm.paderechaeizquierdaClick`,
    `parribaClick`, `pabajoClick`)
  - `wte/src/impl/ep2002_mainform.aux.inc` — os 23 buffers de descarte, o ramo
    `> 2` da `PreparaBuffer`, `DescarteOcupado`, `TrocaEmCurso`,
    `RepovoaAsDuasListas`, `NomeDoItemSelecionado`, `LegendaDoDescarte`
  - `wte/src/impl/` — os 3 `.inc`, mais `ep2002_mainform.uses`
  - `wte/tools/dump_auxiliares.py` — por que `0x0040b934`, `0x0041978c` e
    `0x00422402` ficam fora do `PAPEIS`, com o que foi medido de cada uma
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 82,1% → **80,2%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild wte/wte.lpi` rc 0.

- **Problemas encontrados:**
  1. O quadro das seis passagens agrupava o `flechasapaClick` com os três do
     `MainForm` e somava o custo de leitura dos quatro. Ele é de outro
     formulário e de outro bloqueio — corrigido no lugar. **Agrupar handler por
     nome de gesto ("mover") em vez de por formulário e por dependência foi o
     que produziu tanto esse erro quanto a atribuição errada do
     `ficha_movertodos` na nona passagem.**
  2. O `parribaClick` foi marcado `implementado` na primeira escrita da spec e
     rebaixado antes do commit: ele é o único do lote que **não grava**, então
     nada dele depende da WTE-TASK-27 — mas o `compara_tela.sh --edicao` não foi
     estendido à lista de descarte, e `implementado` diz "a régua da task
     verde". Sem a régua o veredito passaria a medir quanta leitura foi feita.

- **O que falta para esta task fechar** *(revisado)***:**
  - **10 dos 28 handlers**, sem spec: o `flechasapaClick`, os 2 de atributo e os
    7 de tática — todos bloqueados no preenchimento da ficha (`0x00404820`,
    `0x0040756c`) e do `estrategia` (`0x0040a0b4`), que são as passagens 11 a 13;
  - o comportamento de truncamento por campo (WTE-TASK-36);
  - estender o `--edicao` à lista de descarte, que é o único gate de tela que o
    lote de mover pode ter antes da 27 — o `parribaClick` é o único handler dele
    que não grava.

---

- **Executado em:** 2026-08-12 — **décima primeira passagem: abertura do
  preenchimento da ficha.** Nenhum handler novo; o produto é uma conferência
  que apaga a maior parte do trabalho previsto para as passagens 11 e 12.

- **O custo era 1.275 B e é 3.003 B — e não importa, porque a leitura mudou de
  natureza.**

  O plano cobrava o corpo do `0x0040756c`. Ele chama cinco rotinas internas, e
  desta vez a lista saiu de ferramenta antes de qualquer leitura, como
  combinado depois da nona passagem:

  | rotina | bytes | o que é |
  |---|---|---|
  | `0x00403278` | 270 | extrai `n` bits a partir do bit `w` do par de bytes `(b1, b2)` |
  | `0x00406fb4` | 44 | cor da fonte de um rótulo: amarelo se o valor ≥ 5, branco se não |
  | `0x00406fe0` | 301 | carrega um `.bmp` de `<cwd>\image` |
  | `0x00407110` | 552 | idem, de `<cwd>\image\pelo` |
  | `0x00407338` | 561 | idem, de `<cwd>\image\barba` |

- **O achado: o mapeamento de bit não está no código, está em duas tabelas.**

  O `0x0040756c` não traz deslocamento de bit nenhum. Ele percorre dois vetores
  de registros de 12 bytes em `.data` — `{byte, bit inicial, largura}` — e passa
  cada registro ao extrator:

  | tabela | endereço | registros | o que descreve |
  |---|---|---|---|
  | habilidades | `0x00423648` | 16 | os atributos de 3 bits |
  | aparência | `0x00423708` | 12 | posição, cabelo, barba, altura, idade, pé… |

  Ler uma tabela é um `struct.unpack_from` num laço. Era isso, e não 1.275 bytes
  de disassembly, o que estava atrás da passagem 11.

- **E os 28 registros batem com o `TPlayer.Decode` do port, um a um.**

  As duas descrições do formato são **independentes**: uma é tabela de dados do
  `wte.exe` do Obocaman, a outra são expressões `shr`/`and` herdadas do `ed.exe`
  pelo `we2002_core`. Elas concordam nos 28 — inclusive nos sete campos que
  atravessam fronteira de byte, onde a máscara se parte em duas.

  **Consequência prática: o port não precisa de lógica de bit nova para a
  ficha.** A camada de dados já a tem, e agora isso é medido em vez de suposto —
  que é a diferença entre "provavelmente dá para reusar" e um gate de build.

  Virou o [`check_bitfields.py`](../../wte/tools/check_bitfields.py), que lê as
  duas tabelas do `.exe`, gera a expressão canônica de cada registro e exige que
  ela esteja no `we2002_player.pas`. `make -C wte check` o roda. Testado contra
  três erros plantados antes de entrar: endereço de tabela deslocado em 4 bytes
  (recusa por largura impossível), deslocado em 8 (idem), e máscara errada na
  fórmula (recusa por divergência, nomeando os campos).

  O único campo do `TPlayer` sem registro é o `number` — o número de camisa tem
  tela própria (`ficha_dorsal`) e a ficha do jogador não o mostra.

- **Um buraco de escopo, sem dono:** as três rotinas de bitmap carregam
  `image\pelo` e `image\barba` para a ficha do jogador. A
  [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) cobre `uniformes2d` e
  `banderas` — cabelo e barba não estão no escopo dela, nem no de nenhuma outra
  task. **Não inventei um dono**: fica registrado aqui como achado, e a decisão
  de onde pôr é do usuário. O preenchimento da ficha funciona sem eles (são dois
  `TImage`), então isto não bloqueia a passagem 12.

- **Uma correção à décima passagem:** dizer que `0x00406fe0`, `0x00407110` e
  `0x00407338` "são do `flechasapaClick`" sugeria exclusividade. Elas são
  chamadas **também** pelo `0x0040756c`; só a `0x00408460` (143 B) é exclusiva
  daquele handler. Corrigido no quadro.

- **O que ficou sem medir, e está dito assim:** o terceiro endereço que o corpo
  carrega, `0x00423798`, lido com o mesmo layout de 12 bytes sai **todo zero** —
  o layout não vale ali. Não virou uma terceira tabela inventada; virou uma
  linha no `bitfields.md` dizendo que continua por medir.

- **Arquivos criados/modificados:**
  - `wte/tools/check_bitfields.py` — novo, com `--check`
  - `wte/re/bitfields.md`, `wte/re/bitfields.tsv` — gerados
  - `docs/tasks/26-handlers-de-edicao.md` — o custo real da passagem 11, a
    ressalva da 10, este log

- **Gates medidos:** `make -C wte check` rc 0 (o alvo já pega o gerador novo
  pelo wildcard); `python3 -m unittest` em `tools/`: 478 testes, OK.

- **O que a passagem 12 herda:** o que falta do `0x0040756c` é **casar cada
  registro com o controle da tela que o recebe** — a ordem dos registros é a
  ordem de consumo, e os controles saem das chamadas de `SetText`/`SetItemIndex`
  do corpo. Isso é leitura de código, mas de um corpo cuja aritmética já está
  resolvida. Junto vem o bloco final, que já está lido: quando
  `DWORD[0x00433614 + 4*global]` é zero, o campo condicional recebe um literal e
  o controle é **desabilitado** (`call [ecx+0x64]`, o `SetEnabled` virtual) — é a
  mesma condição do `casilla_dorsalKeyPress` e o `50` da
  [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md).

---

- **Executado em:** 2026-08-12 — **décima segunda passagem: a ficha do jogador
  deixou de abrir vazia.** O `0x0040756c` portado, e uma divergência de três
  passagens fechada.

- **Resumo do que foi feito:**

  `PreencheFicha` — os dois laços do `0x0040756c` —, o bloco final do campo
  condicional, e o `casilla_dorsalKeyPress` deixando de mover o foco sempre.

- **Os controles saem por NOME, e a ordem das tabelas é a ordem da tela.** Cada
  volta do laço monta `'<prefixo>' + IntToStr(n)` e chama `FindComponent`. Os
  cinco prefixos e o que recebem:

  | controle | classe | o que recebe |
  |---|---|---|
  | `barrhab1..16` | `TScrollBar` | `Position := valor cru` |
  | `valorhab1..16` | `TLabel` | `Caption := cru + 12`; fonte **amarela** se cru ≥ 5 |
  | `imghab1..16` | `TImage` | `Width := 7*cru + 8` |
  | `flechasapa1..12` | `TUpDown` | `Position := valor cru` |
  | `valorapa1..12` | `TLabel` | legenda |

  As classes não são chute: saem dos símbolos importados que o corpo chama —
  `TScrollBar::SetPosition`, `TCustomUpDown::SetPosition`, `TControl::SetWidth`,
  `TFont::SetColor` —, e batem com o `.lfm`, que tem exatamente 16 `TScrollBar`,
  16 `TImage`, 12 `TUpDown` e os `TLabel`.

  O `7*cru + 8` é largura de barrinha, da mesma família do `11*v + 9` das barras
  de força do time.

- **Nenhuma aritmética de bit foi escrita**, e é o que a passagem 11 pagou para
  saber: os 28 valores vêm da camada de dados já desempacotados, na ordem das
  tabelas, com o `check_bitfields.py` provando a cada build que as duas
  descrições do formato concordam.

- **A divergência do `casilla_dorsalKeyPress` fechou, e não pelo caminho
  previsto.** A quarta passagem deixou o port movendo o foco **sempre**, porque
  a condição dependia do buffer de 44 bytes. A spec previa que ela fechasse
  junto com o lote de mover.

  Fechou por outro lado: a pergunta é sobre o **dado**, não sobre o buffer — o
  campo condicional só falta nos times 54 e 55 —, e virou
  `JogadorTemCampoCondicional` no `we2002_estado`. Mesmo resultado, e sem
  obrigar a ficha a conhecer o buffer de um handler de outro formulário.

- **E isso foi obrigatório, não preferência: o `uses` gerado sai na
  INTERFACE.** `ep2002_mainform` já usa `ep2002_jugador`, então
  `ep2002_jugador` não pode usar `ep2002_mainform` — referência circular, e o
  compilador recusa. Duas consequências:

  1. `TimeEmEdicao` e `JogadorEmEdicao` mudaram do `.aux.inc` do `MainForm`
     para o `we2002_estado`, que é onde o cabeçalho daquela unidade já dizia
     que mora estado compartilhado por mais de um formulário;
  2. o `PreencheFicha` ficou no `.aux.inc` do `MainForm` e **não** num do
     `jugador` — o que, medido, é como o original faz: o `0x0040756c` não é
     método do formulário da ficha, é rotina solta que alcança os controles
     pelo ponteiro global `0x00433e38` (`_jugador`), a mesma forma da
     `MarcaCamisa` com o `0x00434360`.

  A primeira tentativa foi escrever um `ep2002_jugador.aux.inc`; ela não
  compila, e o erro (`Identifier not found "PreencheFicha"`) diz o porquê a
  três frames de distância do motivo real.

- **O que ficou de fora, medido e nomeado:** as legendas dos campos
  **enumerados** do segundo laço — posição, cabelo, barba, porte, chuteira, pé,
  fora de posição. O original as tira de `0x00423798`, que agora se sabe o que
  é: um vetor de `AnsiString` de passo `0x20`, com o finalizador da RTL
  (`0x004029b5`) recebendo contagem `0x60` = 96 = **12 × 8** — doze campos, até
  oito opções cada. Ele **nasce zerado no arquivo** e é preenchido em tempo de
  execução (`0x00401db6`), e esse preenchimento não foi lido.

  Os rótulos ficam vazios em vez de receberem cadeia inventada. Os dois campos
  **numéricos** — altura e idade, os únicos que o original monta com `IntToStr`
  — estão preenchidos.

- **Arquivos criados/modificados:**
  - `wte/src/we2002_estado.pas` — `TimeEmEdicao`, `JogadorEmEdicao`,
    `TIMES_SEM_CONDICIONAL`, `JogadorTemCampoCondicional`
  - `wte/src/impl/ep2002_mainform.aux.inc` — `PreencheFicha`; o bloco movido
  - `wte/src/impl/ep2002_mainform.mostrar_jugadorClick.inc` — a chamada
  - `wte/src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc` — a condição real
  - `wte/src/impl/*.uses` — as duas listas
  - `wte/tools/check_bitfields.py` — o que `0x00423798` é
  - `wte/re/spec/MainForm.mostrar_jugadorClick.md`,
    `jugador.casilla_dorsalKeyPress.md` — as linhas que caducaram
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 80,2% → **79,2%**
  - regerados: `bitfields.md`, os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild wte/wte.lpi` rc 0.

- **Problemas encontrados:**
  1. A referência circular acima. Custou duas recompilações e a lição está
     escrita no `.aux.inc`: **rotina que precisa dos dois formulários só cabe
     no do `MainForm`**, e isso coincide com a estrutura do original.
  2. `CONDICIONAL_AUSENTE` ficou declarado duas vezes ao mover o bloco. O
     compilador pegou; vale registrar que mover código entre `.inc` do mesmo
     `{$I}` não é livre — eles compartilham um escopo só.
  3. Um `{` dentro de comentário Pascal (`{byte, bit inicial, largura}`) abre
     comentário aninhado e o FPC avisa. Trocado por parênteses.

- **O que falta para esta task fechar** *(revisado)***:**
  - **10 dos 28 handlers**, sem spec. Os 2 de atributo e o `flechasapaClick`
    **deixaram de estar bloqueados** — a ficha enche —, e são a próxima
    passagem; os 7 de tática continuam atrás do `0x0040a0b4` (1.443 B);
  - as legendas dos campos enumerados da ficha (`0x00401db6`);
  - o comportamento de truncamento por campo (WTE-TASK-36);
  - a régua de tela: o `--edicao` não alcança nem a lista de descarte nem a
    ficha.

---

- **Executado em:** 2026-08-12 — **décima terceira passagem: a régua de tela
  para a ficha, e por que ela não pode ser escrita como as outras.** Nenhum
  handler novo; o produto é uma medição que corrige uma explicação errada já
  no código.

- **A tentativa:** estender o `compara_tela.sh --edicao` à ficha do jogador. O
  motivo era o saldo — o `PreencheFicha` da passagem anterior enche 44
  controles a partir de duas tabelas lidas do disassembly, e **nada tinha
  medido isso**. Índice trocado ali dá número plausível no rótulo errado, que é
  o defeito sem sintoma.

- **A sondagem falhou, e o modo como ela falhou é o achado.** Cliquei em 21
  posições em volta de onde o `.lfm` põe o `mostrar_jugador_1` — `GroupBox1`
  em `(8, 320)` mais `(8, 72)`, ou seja `(16, 392)` no cliente. Nenhuma
  disparou o handler; a última abriu o **`estrategia`**, que é o
  `mostrar_estrategia_1`, o botão 32 px ACIMA. O alvo estava sistematicamente
  mais abaixo do que a conta dizia.

- **A causa: `Application.Scaled := True`, no `wte.lpr`.**

  A janela do port sai **1,0421 vez** a do projeto. Medido no `:99`: **544×495**
  contra os **522×475** que o `.lfm` declara — e os dois quocientes batem na
  quarta casa decimal. Não é borda, não é decoração (não há gerenciador de
  janela no `:99`): é a LCL reescalando o formulário inteiro.

- **E isso desmente uma explicação que já estava escrita no código.** O
  `calibra()` do [`compara_tela.py`](../../wte/tools/compara_tela.py) dizia,
  desde a segunda passagem: *"o oráculo dá (0, 0) e o port dá (6, 6): o gtk2
  desenha uma borda que o Wine não desenha"*. A borda não existe.

  O que a torna insustentável é uma medição que a **própria segunda passagem
  registrou** e não cruzou: *"a diferença cresce descendo a janela"*, e ela
  escolheu `y = 200` como interseção para clicar na `track_barra`. O controle
  está em `y = 192` no projeto, e `192 × 0,0421 = 8,1` — exatamente a deriva
  observada. **Borda é constante; escala não.** A evidência estava na árvore há
  duas passagens, do mesmo jeito que a recusa de teclado da primeira passagem
  estava.

- **Por que isso bloqueia a régua da ficha e não bloqueou a das barras.**
  Enquanto o alvo é um controle só, perto do topo, um deslocamento constante
  serve de aproximação e o clique cai dentro. A ficha é outra coisa: o que se
  mede lá é **largura** — as 16 barrinhas `imghab`, cada uma com
  `Width := 7*v + 8` —, e largura entra multiplicada por 1,0421 no port. A
  comparação acusaria divergência onde há só escala, e pior: acusaria de forma
  *plausível*, porque 1,0421 sobre uma largura de 8 a 57 px dá diferença de 0 a
  2 px, do tamanho de um erro de arredondamento.

- **Não escolhi a saída**, e é decisão do usuário porque as três custam coisas
  diferentes:

  | saída | o que custa |
  |---|---|
  | desligar `Application.Scaled` | muda a janela do port para todo mundo, inclusive para o `golden_gui`; é a única que faz as coordenadas voltarem a ser as do `.lfm` |
  | dividir por 1,0421 no comparador | mantém a janela e põe um número medido no `compara_tela.py`; arredondamento vira ruído de 1 px |
  | medir em unidades de projeto | o mais correto e o mais caro: o comparador passaria a converter cada retângulo |

- **O que fica registrado como medido:** a escala (1,0421 = 544/522 = 495/475),
  a causa (`Application.Scaled := True` no `wte.lpr`), e a correção da
  explicação antiga no `calibra()`. O `--ficha` não foi escrito.

- **Arquivos criados/modificados:**
  - `wte/tools/compara_tela.py` — o `calibra()` deixou de afirmar que existe
    uma borda de 6 px e passou a dizer o que foi medido
  - `docs/tasks/26-handlers-de-edicao.md` — este log

- **Gates medidos:** `make -C wte check` rc 0; `python3 -m unittest` em
  `tools/`: 478 testes, OK.

- **Problemas encontrados:**
  1. A sondagem abriu um modal (`estrategia`) no meio da varredura, e a partir
     dali todo clique foi para ele — o trace mostra **um** disparo e as 20
     tentativas seguintes desaparecem sem erro. Varredura de coordenada em
     formulário que tem botão de modal precisa parar no primeiro disparo de
     **qualquer** handler, não só do procurado.
  2. `roms/` continuou intocada: a sondagem rodou sobre cópia em `work/`,
     apagada ao final.

---

- **Executado em:** 2026-08-12 — **décima quarta passagem: a escala saiu, e a
  ficha abriu na primeira tentativa.**

- **`Application.Scaled := True` foi removido do `wte.lpr`, e a hipótese
  fechou.** Medida a janela no `:99` depois: **522×475**, que é exatamente o
  que o `.lfm` declara. Antes eram 544×495. Não sobrou deriva para explicar.

- **A decisão custou menos do que a passagem anterior escreveu, e isso é uma
  correção minha.** O log da décima terceira dizia que desligar a escala
  "muda a janela do port para todo mundo, inclusive para o `golden_gui`".
  **Errado, e conferido antes de mexer:** o `golden_gui.sh` mora em
  [`tools/`](../../tools/golden_gui.sh), na raiz do repositório, e é do
  `newWe2002` — o port Qt. O harness de tela deste projeto é o
  `wte/tools/compara_tela.sh` e o `golden_run_laz.sh`. O alcance da mudança é o
  `wte` e só.

  E a linha **nunca tinha sido argumentada**: aparecia uma vez no `wte.lpr`, sem
  task, doc ou comentário que a defendesse. Era gabarito de projeto do Lazarus.
  Saiu com um comentário no lugar dizendo por que não deve voltar — a razão de
  fundo é fidelidade: o alvo é um Win32 de 2002 sem escala, e com ela ligada o
  tamanho da janela do port dependia do DPI de fonte da máquina, o que tornava
  qualquer régua de pixel dependente de onde rodou.

- **O gate exigido antes de qualquer coisa nova: `compara_tela.sh --edicao`,
  verde**, e com os mesmos números da segunda passagem — barras
  `64, 75, 75, 75, 75` nos dois lados, `defesa` de 4 para 6, 4 de 4 ancoradas no
  dump. A régua que já existia não se mexeu.

- **E aí a sondagem que tinha falhado 21 vezes acertou na primeira.** Clique em
  `(20, 402)` — que é `GroupBox1(8, 320)` mais `(8, 72)` do `.lfm`, sem
  correção nenhuma — e o `mostrar_jugadorClick` disparou. A janela
  `Player characteristics` abriu em 707×273, também o tamanho de projeto.

- **Primeira conferência visual do `PreencheFicha`, e ela passa nos dois pontos
  que dava para julgar a olho:**

  - os 16 valores de habilidade aparecem (12, 16, 17, 13, 15, 15, 13, 15, 13,
    13, 17, 13, 13, 12, 14, 18);
  - **a regra do amarelo está certa**: os três `17, 17, 18` saem amarelos e o
    `16` sai branco. `17` é cru 5 e `16` é cru 4, que é exatamente o `>= 5` do
    `0x00406fb4`. Um erro de fronteira ali (`> 5` em vez de `>= 5`) teria
    passado despercebido em qualquer teste que não olhasse a cor.
  - Altura `183` e Ano `32`, os dois campos numéricos.

- **Um achado que a captura entregou de graça, e que muda o que "deixei vazio"
  significa.** Os rótulos dos campos enumerados **não aparecem em branco**:
  mostram `Gl`, `A`, `A1`, `Dire.`, `NO`. São as legendas de projeto do `.lfm`,
  que continuam lá porque o `PreencheFicha` não toca nesses controles.

  Ou seja, a decisão da passagem 12 — "não inventar cadeia" — produz na tela
  algo **pior** do que branco: um texto plausível e estático, igual para todo
  jogador. Um leitor da tela não tem como saber que aquilo não é o dado. Isso
  precisa virar decisão explícita quando as legendas forem medidas
  (`0x00401db6`); enquanto isso, está registrado aqui e na spec.

- **Arquivos criados/modificados:**
  - `wte/wte.lpr` — a linha fora, e o comentário que diz por que
  - `docs/tasks/26-handlers-de-edicao.md` — este log e a correção da passagem 13

- **Gates medidos:** `lazbuild wte/wte.lpi` rc 0; `make -C wte check` rc 0;
  `compara_tela.sh --edicao` **PASSOU**, mesmos números da segunda passagem;
  janela do port 522×475 = `.lfm`.

- **O que a próxima passagem herda, agora sem obstáculo de coordenada:** o
  `--ficha` propriamente dito — abrir a ficha nos dois lados e medir as 16
  larguras de `imghab` (`7*v + 8`) contra o dump, do mesmo jeito que o modo das
  barras mede as cinco. As coordenadas do `.lfm` valem direto nos dois lados,
  que era o que faltava.

---

- **Executado em:** 2026-08-12 — **décima quinta passagem: a régua de tela da
  ficha não existe, e o que existe no lugar é melhor.**

- **O `--ficha` por pixel morreu na medição, e o motivo é do widgetset.** O
  plano era medir as 16 larguras de `imghab` (`7*v + 8`) como o modo das barras
  mede as cinco. Medido no `:99`, varrendo a coluna pixel a pixel: **só a
  primeira das dezesseis é visível.**

  O `imghab<n>` fica em `Top = 8 + 16n` com 8 px de altura e o `barrhab<n>` em
  `Top = 12 + 16n` com 12 — de projeto, sobra uma faixa de 4 px do `imghab`
  acima do scrollbar. O `TScrollBar` do gtk2 desenha **mais alto** que os 12 px
  declarados e come essa faixa. A primeira linha escapa porque não há nada
  acima dela.

  E ela mede certo: **8 px**, para um `attack` de 12, que é cru 0, que é
  `7*0 + 8`. Uma linha confirma a fórmula e não julga uma ordem.

- **O risco que sobrava era exatamente o que a tela não pega**: campo trocado de
  lugar entre os 28: número plausível no rótulo errado. Ele fecha **sem tela**,
  e é a segunda conferência do
  [`check_bitfields.py`](../../wte/tools/check_bitfields.py):

  1. para cada descritor, gera a expressão canônica e acha a linha do
     `TPlayer.Decode` que a contém — **casamento único exigido**, porque dois
     descritores com a mesma expressão tornariam a atribuição ambígua, e
     ambiguidade aqui é troca silenciosa;
  2. dali sai o membro do `TPlayer` que aquele descritor descreve;
  3. exige que a chamada `n` do `PreencheFicha` use esse membro.

  Testada contra erro plantado antes de entrar: trocando `p.jump` e
  `p.heading` entre as posições 10 e 11, ela nomeia as duas e diz qual era
  esperado em cada.

- **Por que isto vale mais que a régua de pixel que substitui**, e não é
  conformismo: a régua de tela mediria a largura de uma barrinha, que é função
  do valor; esta mede a **identidade do campo**, que é o que a ordem das
  tabelas afirma. Duas habilidades no mesmo balde de largura passariam pela
  primeira e não passam por esta. E ela roda no `make check`, sem `:99`, sem
  Wine e sem coordenada.

- **Arquivos criados/modificados:**
  - `wte/tools/check_bitfields.py` — `campo_por_descritor` e `conferir_ficha`
  - `docs/tasks/26-handlers-de-edicao.md` — este log

- **Gates medidos:** `make -C wte check` rc 0; `python3 -m unittest` em
  `tools/`: 478 testes, OK; guarda nova reprovando o erro plantado.

- **O que fica dito e não resolvido:** a ficha continua **sem régua de tela**.
  O que existe é a conferência estática acima mais a inspeção visual da
  passagem 14 (os 16 valores aparecem, e o amarelo do `>= 5` está certo). Se
  alguém quiser gate de pixel ali, o caminho medido é a **assinatura de cor**
  dos 16 `valorhab` — quais saem amarelos —, que é robusta a fonte e a
  widgetset; a largura de `imghab` não é caminho.

---

- **Executado em:** 2026-08-12 — **décima sexta passagem: os dois handlers de
  atributo, e eles são os primeiros do lote que fecham `implementado`.** O
  grupo vai de **18 para 20 de 28**; o índice a **11 `implementado`** de 96.

- **As duas conferências prometidas vieram antes do Pascal, e as duas
  mudaram o que seria escrito.**

  **1. Eles não gravam.** O inventário de chamadas dos 300 bytes de cada um
  alcança `FindComponent`, `IntToStr`, `Copy`, `TControl::SetText`,
  `TControl::SetWidth` e a rotina de cor `0x00406fb4` — e **nenhuma** escritora
  de imagem. É o único lote desta task que fecha sem depender da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), e por isso os dois
  saem `implementado` em vez de `aberto` como todos os anteriores.

  **2. `TScrollBar.Position :=` DISPARA `OnChange` na LCL.** Medido, não
  suposto, estendendo o `check_lcl_combo.py` de cinco casos para oito: o
  `TScrollBar` dispara (e só quando o valor muda de verdade) e o `TUpDown`
  **não** dispara o `OnClick`. É a resposta oposta à do `TComboBox` e a mesma
  do `TTrackBar` da segunda passagem.

  Consequência escrita no código: o `PreencheFicha` **reentra** nos dezesseis
  `barrhabScroll` ao encher a ficha, cada reentrada reescrevendo rótulo,
  largura e cor com o mesmo valor. A tela não muda; a contagem de disparos no
  trace muda, e é isso que um gate de trace sobre a ficha teria de esperar. As
  duas escritas continuam necessárias — quando o valor já é o que estava lá, o
  `OnChange` não dispara e só a do preenchimento acontece.

- **O achado do lote: `barrhab_bisScroll` não é outra família de controles.**

  Os dois corpos têm 300 bytes e o **mesmo** conjunto de chamadas, símbolo por
  símbolo. A única diferença é o comprimento do `Copy` sobre o nome do
  componente: `Copy(Sender.Name, 8, 1)` no primeiro e `Copy(..., 8, 2)` no
  segundo. `barrhab` tem sete caracteres, então a posição 8 é o primeiro
  dígito — um serve `barrhab1..9` e o outro `barrhab10..16`.

  **É a largura do número.** O `.lfm` tem exatamente 16 `barrhab`, de 1 a 16, e
  nenhum `barrhab_bis`. Ler o par como "as barras normais e as outras" mandaria
  procurar um segundo grupo de controles que não existe — e o nome do handler é
  o único lugar onde essa leitura errada é convidada.

- **Arquivos criados/modificados:**
  - `wte/re/spec/jugador.barrhabScroll.md`, `jugador.barrhab_bisScroll.md`
  - `wte/src/impl/ep2002_jugador.aux.inc` — `AtualizaHabilidade`, o corpo comum
  - `wte/src/impl/ep2002_jugador.barrhabScroll.inc`, `.barrhab_bisScroll.inc`
  - `wte/src/impl/ep2002_jugador.uses`
  - `wte/tests/test_lcl_combo.pas` — os três casos novos
  - `wte/tools/check_lcl_combo.py` — os vereditos medidos, e a mensagem de
    sucesso deixou de dizer "nenhum dispara", que passou a ser falso
  - `wte/src/impl/ep2002_mainform.aux.inc` — a reentrância anotada no
    `PreencheFicha`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 79,1% → **78,5%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: 478 testes, OK; `check_lcl_combo` com oito
  casos verdes.

- **Problemas encontrados:** a mensagem de sucesso do `check_lcl_combo.py`
  afirmava "nenhum dispara `OnChange` por atribuição". Com o `TScrollBar` medido
  ela virou mentira **enquanto os vereditos passavam** — guarda verde dizendo o
  contrário do que mediu. Trocada.

- **O que falta para esta task fechar** *(revisado)***:**
  - **8 dos 28 handlers**: o `flechasapaClick` (981 B mais a `0x00408460`, 143 B
    — as outras três auxiliares dele já foram lidas na passagem 11) e os 7 de
    tática, atrás do `0x0040a0b4` (1.443 B);
  - as legendas dos campos enumerados da ficha (`0x00401db6`), que hoje mostram
    o texto de projeto do `.lfm`;
  - o truncamento por campo (WTE-TASK-36);
  - a régua de tela da ficha, se alguém a quiser: pela assinatura de cor dos 16
    `valorhab`, não pela largura de `imghab`.

---

- **Executado em:** 2026-08-13 — **décima sétima passagem: o `flechasapaClick`,
  e as legendas da ficha deixaram de ser as do `.lfm`.** O grupo vai de **20
  para 21 de 28**. Fecha o lote de atributo inteiro e paga uma dívida que estava
  aberta desde a passagem 12.

- **A conferência prometida veio antes do Pascal, e mudou o que seria escrito.**
  O inventário de chamadas dos 1.124 bytes (`0x00408088` mais a `0x00408460`)
  **não alcança nenhuma das duas escritoras de imagem** — nem a `0x00403400`
  nem a `0x00404048`. Como os dois de `barrhab`, este handler não depende da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md).

  **Mas ele escreve em disco assim mesmo**, e é a diferença que o inventário
  sozinho esconderia: as três carregadoras de bitmap abrem o `.bmp` em `"r+b"`
  e **regravam a paleta dentro do arquivo de asset**. Mexer numa seta de cabelo
  altera o arquivo que todos os jogadores compartilham. Já estava medido na §6
  da [`assets.md`](../../wte/re/assets.md); aparece aqui porque é este handler
  que fecha o ciclo, e porque "não grava" dito sem essa ressalva seria falso.

- **São dois despachantes em fila, e a leitura apressada veria um.** O primeiro
  escreve o rótulo, o segundo redesenha os bitmaps, e **todo caminho do
  primeiro cai no segundo**. Os dois comparam o mesmo sufixo contra literais
  diferentes, e ler os `'3'` das duas listas como um só faria o segundo parecer
  código morto.

  Um só corte de nome serve os doze — `Copy(Sender.Name, 11, 2)` —, ao
  contrário dos `barrhab*Scroll`, que precisaram de dois corpos. O que muda é
  que aqui o despacho compara **cadeia** e lá comparava número.

- **A dívida das legendas foi paga, e por ferramenta.** Nove dos doze controles
  não mostram número: mostram palavra, buscada num `AnsiString[12][8]` em
  `0x00423798` — **zero no disco**, montado em tempo de execução. É o que a
  passagem 12 registrou como "não inventar cadeia" e o que a 14 viu na tela: as
  legendas de projeto do `.lfm` (`Gl`, `A`, `A1`, `Dire.`, `NO`) iguais para
  todo jogador, que é pior do que branco porque parece dado.

  O novo [`dump_legendas.py`](../../wte/tools/dump_legendas.py) percorre o
  inicializador (`0x00401da8`..`0x0040295e`, 150 chamadas ao construtor de
  `AnsiString`) e emite o par (slot, cadeia) que **o binário monta**. As
  cadeias sairiam num `strings`; o que só está na ordem das chamadas é **qual
  vai em qual slot** — transcrever à mão acertaria o conteúdo e erraria a
  posição sem nada reclamar.

- **A conferência que sustenta a atribuição, e por que ela precisava existir.**
  Nada no binário diz que a linha `n` é o `flechasapa n+1`: isso sai da ordem
  de construção. A segunda medida vem de outra fonte — o `Max` de cada seta no
  `.dfm` — e as doze casam: cada linha tem exatamente `Max + 1` células com
  texto, e as **três** linhas vazias são exatamente os três controles de faixa
  maior que as 8 colunas (`flechasapa3` cabelo, `7` altura, `9` idade). O
  gerador **aborta** se isso deixar de valer, e um teste prova que ele aborta.

  A tabela do cabelo, contígua em `0x00423918`, tem 32 nomes — os mesmos 32 de
  `image/pelo/pelo_<n>.bmp` contados na §5 da `assets.md`, por um caminho
  independente.

- **Visto na tela, não só no gerador.** Com a ficha aberta no `:99`, cinco dos
  dez rótulos enumerados deixaram de mostrar o texto de projeto: `Cab.` foi de
  `A1` para `I1`, `Peso` de `A` para `E`, `Chut.` de `A` para `B`,
  `3D(Trivela)` de `NO` para `YES`. E o handler responde: três cliques na seta
  de `Posicao` levam de `Gl` a `Vl`, que é `LEGENDAS[0][3]`, com três disparos
  no `trace.log`.

- **Veredito `aberto`, e não pela régua de bytes.** É a **metade dos bitmaps**:
  o segundo despachante está portado como estrutura, mas as três carregadoras
  (`0x00406fe0`, `0x00407110`, `0x00407338`, 1.414 B somados) **não têm dono** —
  a [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) cobre uniforme e
  bandeira do `MainForm`, não cara/cabelo/barba da ficha. Até alguém adotá-las,
  a seta muda o rótulo e não muda o desenho.

- **Uma armadilha de Pascal que custou um build:** o parâmetro `legenda` do
  `Aparencia` **escondia** a função `Legenda` da tabela — Pascal não distingue
  caixa. O erro sai como `Syntax error, ";" expected but "(" found`, que não
  menciona sombra nenhuma. Renomeado para `pronta`, com o motivo escrito ao
  lado.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_legendas.py` — o gerador, com as cinco conferências que
    abortam
  - `wte/tools/test_dump_legendas.py` — 13 testes, 10 sobre PE sintético e 3
    contra o `.exe` sob `skipUnless`
  - `wte/re/legendas.md`, `wte/re/legendas.tsv`, `wte/src/wte_legendas.pas` —
    gerados
  - `wte/re/spec/jugador.flechasapaClick.md`
  - `wte/src/impl/ep2002_jugador.flechasapaClick.inc`, `.uses`
  - `wte/src/impl/ep2002_mainform.aux.inc` — o `Aparencia` do `PreencheFicha`
    passou a buscar as legendas medidas; `ep2002_mainform.uses`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 78,5% → **78,1%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: 491 testes, OK; `check_lcl_combo` com oito
  casos verdes no `:99`; `compara_tela.sh --edicao` **PASSOU**, mesmos números
  das passagens 2 e 14 — barras `[64, 75, 75, 75, 75]` nos dois lados, 4 de 4
  contra o `we2002_core`.

- **Problemas encontrados:** o Xvfb `:99` não estava no ar nesta sessão. Subido
  em 1280x1024 sem `-auth`, que é a forma que esta máquina usa; **não** houve
  queda para o `:1`.

- **O que falta para esta task fechar** *(revisado)***:**
  - **7 dos 28 handlers**, todos de tática, atrás do `0x0040a0b4` (1.443 B); as
    auxiliares `0x004097d4` e `0x004099bc` estão inventariadas e a `0x00403278`
    já foi lida;
  - as três carregadoras de bitmap da ficha (`0x00406fe0`, `0x00407110`,
    `0x00407338`) **continuam sem dono** — decisão de escopo, não trabalho
    pendente desta task;
  - o truncamento por campo (WTE-TASK-36);
  - a régua de tela da ficha, se alguém a quiser: pela assinatura de cor dos 16
    `valorhab`, não pela largura de `imghab`.

---

- **Executado em:** 2026-08-18 — **décima oitava passagem: os seis handlers de
  arrastar bola no campinho.** O grupo vai de **21 para 27 de 28**; falta um
  handler para esta task fechar.

- **O custo do lote estava errado por três vezes, e nas três na mesma direção.**
  O plano dizia "os 7 de tática, atrás do `0x0040a0b4` (1.443 B)". Medido antes
  de ler, como manda a disciplina das últimas passagens:

  1. **`0x0040a0b4` não é deste lote.** Quem o chama é o
     `MainForm.mostrar_estrategiaClick`, do grupo de carga — está na coluna de
     chamadores da [`auxiliares.tsv`](../../wte/re/auxiliares.tsv) desde a
     WTE-TASK-25. Os 7 handlers **não chamam auxiliar interna nenhuma**: todas
     as chamadas dos 2.088 bytes vão para a VCL.
  2. **`campoMouseMove` tem 52 bytes, não 1.404.** A conta de 1.404 é a
     distância até o próximo handler *publicado*, e entre um e outro mora o
     `estrategia.FormCreate` (1.352 B). Medir corpo por subtração de vizinhos
     **superestima em silêncio** sempre que houver rotina não listada no meio.
  3. **`relojTimer` tem 936 B, não 348** — aqui para menos, pelo motivo
     inverso: o corte que eu tinha usado era arbitrário.

  O erro (1) e o (2) juntos faziam o lote parecer caro demais para uma passagem.
  Erro de custo não é ruído: é o que decide o recorte, e recorte errado deixa
  trabalho barato parado.

- **O achado que o lote entregou: as zonas do campinho.** Arrastar um jogador
  **não é livre**. O `bolaMouseDown` desenha o `rectangulo` em volta da área
  permitida daquela bola, e o `rectanguloDragOver` prende o movimento a uma
  grade dentro dela. A geometria sai de uma tabela em `0x00433e5c` — 11
  registros de 16 bytes, `(x1, y1, x2, y2)`.

  **Essa tabela não existe no arquivo**, como as legendas da passagem anterior:
  é `.bss`, montada em tempo de execução. Quem a monta é o
  `estrategia.FormCreate`, escrevendo 44 imediatos um a um, em ordem
  embaralhada — o compilador intercala `lea` de ponteiro com `mov` de
  deslocamento, e o primeiro campo de cada registro sai por um registrador
  diferente dos outros três. Transcrever a olho trocaria um `x2` por um `y1` e
  produziria um retângulo plausível.

  O novo [`dump_zonas.py`](../../wte/tools/dump_zonas.py) decodifica e confere
  contra o `.lfm`, que é outra fonte: **nenhum retângulo pode sair do `campo`**
  (395×246) e a contagem tem de bater com os `bolaN` do formulário.

- **E a spec do `estrategia.FormCreate` não dizia nada disso.** Escrita na
  WTE-TASK-25, ela descreve as cores da zebra e chama os blocos de `0x00409168`
  em diante de "quatro laços curtos de 11 iterações". O **produto principal** da
  rotina é a tabela de zonas. Corrigida nesta passagem, com a lição escrita
  dentro: spec de `FormCreate` escrita a partir da pergunta *"o que ele pinta?"*
  responde só isso, e a ausência não se anuncia.

- **Três detalhes que a leitura apressada erraria, e os três estão no Pascal:**

  **A grade do eixo X tem fase.** Não é "múltiplo de 8": é múltiplo de 8 **mais
  5** — os pontos válidos são 5, 13, 21… Arredondar para o múltiplo de 8 mais
  próximo daria posições três pixels fora em todo o campo, e nenhum teste de "a
  bola se move" pegaria. O eixo Y é grade de 5 sem fase.

  **`X`/`Y` do `rectanguloDragOver` são relativos ao `rectangulo`, não ao
  `campo`.** O alvo do arrasto é o retângulo. Tratá-los como se já fossem do
  campo desloca a bola pela posição da zona — erro que cresce com a zona e
  **desaparece na zona 0**, que é justamente onde um teste apressado olharia.

  **Um global, dois papéis.** `0x00434340` é "bola destacada" no
  `bolaMouseMove` e "bola sendo arrastada" no `bolaMouseDown`; não há um segundo
  ponteiro. O original pode reusá-lo porque para apertar o botão sobre a bola o
  ponteiro necessariamente passou por ela.

- **Um teste meu reprovou, e a tabela estava certa.** Escrevi que os `x1`
  distintos seriam três — defesa, meio e ataque. São **quatro**: além de 10, 122
  e 274 há uma coluna em 170, um meio-campo adiantado mais estreito. Corrigido
  para o valor medido, com o motivo dentro do teste. Palpite bonito escrito como
  asserção é asserção errada.

- **Visto na tela, no `:99`, e não só no gerador.** Com a `estrategia` aberta:
  passar o mouse acende a bola de verde vivo e o rótulo de branco enquanto apaga
  a anterior; apertar o botão faz aparecer o retângulo preto de borda vinho na
  zona 0, com os 120×120 que a tabela prevê, e some o rótulo da bola arrastada;
  arrastar move bola e rótulo juntos; soltar recoloca tudo. O `trace.log` mostra
  a ordem completa — `bolaMouseDown` → `rectanguloDragOver` (várias) →
  `rectanguloDragDrop` → `bolaEndDrag`.

- **Um aviso de compilação ficou de propósito.** `Variable "ZonaDaBola" read but
  nowhere assigned` — o vetor bola→zona é preenchido pelo
  `estrategia.lista_formacionesClick`, que não é desta passagem. Enquanto ele
  não existir, toda bola cai na zona 0. Calar o aviso esconderia exatamente a
  lacuna que ele anuncia; é o que mantém o `bolaMouseDown` em `aberto` enquanto
  os outros cinco fecham `implementado`.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_zonas.py`, `wte/tools/test_dump_zonas.py` (10 testes)
  - `wte/re/zonas.md`, `wte/re/zonas.tsv`, `wte/src/wte_zonas.pas` — gerados
  - `wte/re/spec/estrategia.bolaMouseMove.md`, `.bolaMouseDown.md`,
    `.campoMouseMove.md`, `.rectanguloDragOver.md`, `.rectanguloDragDrop.md`,
    `.bolaEndDrag.md`
  - `wte/re/spec/estrategia.FormCreate.md` — a correção
  - `wte/src/impl/ep2002_estrategia.aux.inc`, `.uses` e os seis `.inc`
  - `wte/tools/README.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 78,1% → **76,4%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: 501 testes, OK;
  `compara_tela.sh --edicao` **PASSOU**, barras `[64, 75, 75, 75, 75]` nos dois
  lados, 4 de 4 contra o `we2002_core`.

- **Problemas encontrados:** o Xvfb `:99` caiu no meio da sessão e foi subido de
  novo em 1280x1024; **não** houve queda para o `:1`.

- **O que falta para esta task fechar** *(revisado)***:**
  - **1 dos 28 handlers**: o `estrategia.relojTimer` (`0x00409ba4`, 936 B) — uma
    máquina de estados sobre `0x0043428c` que move as 11 bolas por tabelas de
    coordenadas diferentes a cada fase. É ele que semeia os dois globais que os
    handlers de arrastar leem, e por isso o port precisa hoje de uma guarda de
    `nil` que o original não tem;
  - o vetor bola→zona (`estrategia.lista_formacionesClick`), que promove o
    `bolaMouseDown` de `aberto` a `implementado`;
  - as três carregadoras de bitmap da ficha — **decisão de escopo, sem dono**;
  - o truncamento por campo (WTE-TASK-36);
  - a régua de tela da ficha, se alguém a quiser.

---

- **Executado em:** 2026-08-18 — **décima nona passagem: o `relojTimer`, e com
  ele os 28 handlers têm spec.** Fica **um** critério aberto: o truncamento por
  campo.

- **O achado: trocar de formação não teleporta os jogadores, desliza.** O
  `reloj` tem `Interval = 1` e `Enabled = False` no `.lfm`; o
  `lista_formacionesClick` calcula um delta por bola e o liga, e este handler
  desenha **quatro quadros**.

  **São dois ramos, e o teste está na primeira instrução.** Se o contador chegou
  a 4, este disparo é o do **encaixe final** — escreve a coordenada inteira que
  a formação pediu, zera o contador e desliga o timer. Senão, soma o delta e
  desenha o truncado.

  O ramo do encaixe não é enfeite: depois de quatro somas em ponto flutuante a
  posição acumulada não é o destino, e sem ele a formação ficaria um pixel fora
  **sempre no mesmo sentido**. Ler só o segundo ramo daria uma animação que
  nunca para e nunca chega ao inteiro.

- **A contiguidade das seis tabelas é o que confirma o tamanho delas.** Elas são
  `.bss` — `0x00434238`, `0x00434264`, `0x00434294`, `0x004342c0`, `0x004342ec`,
  `0x00434318` — com `0x2c` (11 entradas) entre bases sucessivas, e logo depois
  da última vem o `0x00434340`, a bola em foco que os handlers de arrastar usam.
  O laço percorre 1..10: a entrada extra é da `bola0`, o goleiro, que não anda.
  São `Single`, não `Double` — o original lê com `fld DWORD PTR`.

- **Dois detalhes que a leitura apressada funde:**

  **`Trunc`, não `Round`.** O original chama o auxiliar da RTL que põe a FPU em
  arredondar-para-zero (`fstcw` / `or 0xc01`). Meio pixel por quadro, sempre
  para o mesmo lado.

  **Dois ponteiros de rótulo, não um.** `0x00434348` é o `etiqjug` que a
  animação move; `0x00434344` é o que o mouse destaca. Os dois andam ao mesmo
  tempo, e fundi-los faria o destaque saltar para a última bola animada.

- **`CurrToStr` de novo.** O nome da bola sai de `CurrToStr(n * 10000)`:
  `Currency` na Borland é inteiro de 64 bits escalado por 10.000, então o
  produto desfaz a escala e o texto sai `'1'`. Mesmo idioma do
  `iguala_nombresClick`. O port usa `IntToStr`.

- **Veredito `aberto`, e não pela régua de bytes.** Quem enche as seis tabelas é
  o `estrategia.lista_formacionesClick`, que não foi portado: enquanto ele não
  existir o `reloj` nunca é habilitado e este corpo nunca roda. Está escrito e
  correto, e **não há como exercitá-lo na tela** — dizer o contrário seria
  chamar de verificado o que só foi compilado.

- **Arquivos criados/modificados:**
  - `wte/re/spec/estrategia.relojTimer.md`
  - `wte/src/impl/ep2002_estrategia.relojTimer.inc`
  - `wte/src/impl/ep2002_estrategia.aux.inc` — o estado da animação e as duas
    buscas por nome
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 76,4% → **75,5%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: 501 testes, OK.

- **Problemas encontrados:** Nenhum novo.

- **O que falta para esta task fechar** *(revisado)***:**
  - **o truncamento por campo** — é o último critério, e é desta task, não da
    36. O que já está medido: quatro `MaxLength` nos DFM (`casilla_dorsal` 3,
    `casilla_nombre` 10, mais dois) e **três atribuições em tempo de execução**
    em `0x0040cc43`…`0x0040cc71`, que dão a `edit_nombre1` metade de
    `[0x00433a10]`, a `edit_nombre2` o `[0x00433b48] − 1` e a `edit_nombre3` o
    literal 3. Falta a ferramenta que cruze isso com a largura do campo de
    destino na camada de dados;
  - o vetor bola→zona e as tabelas da animação (`lista_formacionesClick`), que
    promovem `bolaMouseDown` e `relojTimer` de `aberto` a `implementado`;
  - as três carregadoras de bitmap da ficha — **decisão de escopo, sem dono**.

---

- **Executado em:** 2026-08-18 — **vigésima passagem: o truncamento por campo,
  medido.** Sobra **um** critério, e ele é grande: estender o `--edicao` aos
  outros grupos.

- **O limite de um campo não está num lugar só, e essa é a razão de existir a
  ferramenta.** São seis campos com limite: três o trazem do `.dfm` e três o
  recebem em tempo de execução, por `TCustomEdit::SetMaxLength`. Ler só o
  `.dfm` acha três e **não anuncia** que há outros três; ler só o código acha
  três e perde os outros.

  E dos que vêm do código, **nenhum é literal puro**: dois são expressão sobre a
  largura do campo de destino.

- **O achado é o `div 2`.** O `edit_nombre1` recebe `[0x00433a10] div 2`. Sem
  olhar o destino isso é um número mágico; olhando, fecha: o campo é
  `raw_kanji_name`, **40 bytes, dois por caractere** — 20 caracteres. Os outros
  dois cortam um byte antes do destino, que é o do terminador:
  `mixed_case_name` 20 → 19, `abbreviations[0]` 4 → 3.

  **Essa é a conferência que o gerador roda**, e ela vale porque as duas medidas
  vêm de fontes que não se falam: a expressão sai do `.text` do `.exe`, a
  largura sai da camada de dados (o `we2002_core`, byte-idêntico ao `ed.exe`).
  O gerador aborta se discordarem.

- **Um `MaxLength` verdadeiro e irrelevante.** `jugador.casilla_dorsal` declara
  10 e recebe **número de camisa**, que tem no máximo três dígitos. O limite
  útil vem do `casilla_dorsalKeyPress`, que recusa tecla. Quem portasse "o campo
  corta em 10" teria copiado uma medição correta para o lugar errado — está
  registrado como tal.

- **O que derrubou a primeira versão do decodificador:** o terceiro sítio
  carrega o ponteiro do formulário em `edx` (`mov edx,ds:_MainForm`), indexa o
  controle e só então põe o literal em `edx`. Tratar a primeira carga como
  comprimento daria `MaxLength := endereço do formulário` — um número enorme, e
  nenhum erro. Há teste para isso.

  E `abbreviations` é `array[0..2] of array[0..3]`: a largura é a dimensão
  **interna**, 4. Pegar a externa daria 3, que **por acaso é o `MaxLength`
  certo** — a conferência passaria pelo motivo errado, para sempre. Também tem
  teste.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_truncamento.py`, `wte/tools/test_dump_truncamento.py`
    (15 testes)
  - `wte/re/truncamento.md`, `wte/re/truncamento.tsv` — gerados
  - `wte/tools/README.md`
  - `docs/tasks/26-handlers-de-edicao.md` — três critérios marcados

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: 516 testes, OK.

- **Problemas encontrados:** Nenhum além dos dois modos de erro acima, que
  viraram teste.

- **O que falta para esta task fechar** *(revisado)***:**
  - **um critério, e é o caro:** *conferência de tela verde para cada edição,
    uma por rodada*. O `compara_tela.sh --edicao` hoje exercita **um** par —
    `sel_barraClick` e `track_barraChange` —, e cada grupo restante precisa da
    sua sequência de cliques medida nos dois lados, como aquele precisou. É o
    que a nona passagem já anotava como "estender o `--edicao` aos grupos que
    vierem";
  - com ele vem a limpeza de campo por `End`/`shift+Home`/`BackSpace`, que
    nenhum roteiro exercita ainda porque nenhum digita texto;
  - o vetor bola→zona e as tabelas da animação (`lista_formacionesClick`);
  - as três carregadoras de bitmap da ficha — **decisão de escopo, sem dono**.

---

- **Executado em:** 2026-08-18 — **vigésima primeira passagem: o critério de
  tela estreitado por decisão do usuário, e os dois `MaxLength` que o port não
  punha.**

- **A decisão, e ela é a segunda sobre o mesmo critério.** Registrada em "As
  duas reescritas do critério de tela", acima. Em resumo: conferência verde para
  cada **grupo** de edição — de tela onde o alvo é mensurável em pixel,
  **estática** onde já se mediu que não é. O que a sustenta são três medições
  que já estavam neste log: a ficha não é mensurável em pixel (passagem 15), o
  substituto estático já existe e foi aceito (`check_bitfields.py`), e a
  geometria da tática é sustentada pelo `dump_zonas.py`. A régua de **byte**
  continua com a WTE-TASK-27, intocada.

- **O port não punha `MaxLength` em `edit_nombre1` nem em `edit_nombre2`, e a
  divergência era muda.** Os dois campos aceitavam texto de qualquer tamanho; só
  o truncamento na gravação apararia, tarde. Corrigido no `MainForm.FormShow`, e
  **por `SizeOf` do campo de destino, não por literal** — as expressões do
  original são a largura do campo, e escrever 20 e 19 à mão romperia o vínculo
  no dia em que o campo mudasse.

  Conferido na tela, no `:99`: 30 caracteres digitados em `Nome1` param no **T**
  (20º) e em `Nome2` param no **S** (19º). A limpeza foi por
  `End`/`shift+Home`/`BackSpace`, que é o que o critério manda — e foi a
  primeira vez que este projeto digitou texto no port sob o harness.

- **Um erro meu, e ele é do tipo que a spec existe para impedir.** Eu havia
  anunciado o `iguala_nombresClick` como promovível. **Não é.** A spec dele traz
  **dois** motivos para `aberto` e eu só tinha lido o primeiro:

  1. o valor de `[0x00433b48]` não medido — **este fechou**, e por confirmação
     cruzada: o `dump_truncamento.py` cruza a expressão do `.exe` com a largura
     do campo na camada de dados e aborta se discordarem;
  2. **o botão não acinzenta no port** — a CORR-WTE-057 mediu 518 px de mudança
     no oráculo e **0** no port, com o Pascal pondo `Enabled := nacional` na
     linha 49 e o vizinho `boton_nombres2iso` acinzentando certo na linha 55.
     **Sem causa medida.**

  Levantei duas hipóteses — a cor transparente do glifo e o `ParentFont = False`
  — e **não testei nenhuma**, então nenhuma entrou na spec. A CORR-WTE-057 já
  escreveu que este defeito pede correção própria; ela **ainda não foi aberta**.

- **O log desta task estava corrompido, por minha causa.** As passagens 18 e 19
  apareciam **duas vezes** e fora de ordem: uma `str.replace` sem `count=1`
  casou um âncora que existia em dois lugares. Ordem refeita (17 → 20), nada
  perdido — só linhas em branco a mais —, e as datas das passagens 18, 19 e 20
  corrigidas de 2026-08-13 para **2026-08-18**, que é a dos commits. A guarda
  que faltava (`assert` de ocorrência única antes de substituir) foi usada nesta
  passagem e **reprovou de novo**, no mesmo âncora — o texto foi anexado no fim
  do arquivo em vez de por marca.

- **Arquivos criados/modificados:**
  - `docs/tasks/26-handlers-de-edicao.md` — o critério reescrito, a seção da
    decisão, a ordem do log e as datas
  - `wte/src/impl/ep2002_mainform.FormShow.inc` — os dois `MaxLength`
  - `wte/re/spec/MainForm.iguala_nombresClick.md` — um motivo fechado, o outro
    nomeado
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 75,5% → **75,4%**
  - regerados: `fase-2.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: 516 testes, OK. Mais a conferência de tela
  dos dois `MaxLength`, acima.

- **O que falta para esta task fechar** *(revisado)***:**
  - **duas sequências de tela**, pelo critério novo: **nomes** e **mover** — os
    dois no `MainForm`, sem sub-diálogo, alvo mensurável em pixel. Com elas vem
    a limpeza de campo em roteiro;
  - **números**: a metade do `MainForm` (`dorsalClick`, `dorsalMouseDown`) entra
    na sequência de mover; a metade do `ficha_dorsal` fecha por conferência
    estática;
  - **atributos** e **tática** fecham por conferência estática — o
    `check_bitfields.py` e o `dump_zonas.py` já são ela; falta escrever o
    veredito;
  - o `iguala_nombres` que não acinzenta — **precisa de CORR própria**;
  - o vetor bola→zona e as tabelas da animação (`lista_formacionesClick`);
  - as três carregadoras de bitmap da ficha — **decisão de escopo, sem dono**.

---

- **Executado em:** 2026-08-18 — **vigésima segunda passagem: a régua de tela do
  grupo de nomes, e ela achou uma divergência na primeira corrida.**

- **`compara_tela.sh --nomes`.** Digita o MESMO texto nos dois lados —
  `AB-C.D E` — nos três campos de nome, encadeando pelo `Return`, e compara.

  **O texto não é qualquer um.** Os três filtros não são iguais: `nombre1` e
  `nombre2` aceitam espaço e ponto, `nombre3` só alfanumérico. Um texto só de
  letras passaria idêntico pelos três e a régua mediria digitação, não filtro.
  O `-` é recusado pelos três; o `.` e o espaço separam o terceiro dos outros.

  **O `Return` faz parte do teste**: os dois primeiros handlers movem o foco
  para o campo seguinte, o terceiro não. A sequência digita nos três **sem
  clicar entre eles** — se o encadeamento falhar, os campos 2 e 3 ficam vazios.

- **A régua não compara pixel com pixel, e não é desleixo.** gtk2 e Win32 não
  desenham a mesma fonte, e o `MS Sans Serif` do original nem está instalado: um
  diff estrito acusaria divergência em qualquer campo com letra dentro. O que
  sobrevive à troca de widgetset é a **propriedade que o filtro impõe** —
  quantos caracteres passaram —, e a largura da tinta é o proxy dela.

  A tolerância é **meio glifo (4 px)**, e não folga escolhida por conveniência:
  um caractere vale 7 a 8 px nesta fonte. Medido: com os dois lados de acordo a
  diferença foi de 0 a 1 px; com um caractere de diferença, 10 px.

- **Na primeira corrida ela ficou verde medindo a MOLDURA.** Os três campos
  deram largura de tinta igual à largura deles — 112, 112, 33 — e a
  coincidência passou por "os dois lados concordam". Duas causas somadas: a
  medição não descontava a borda do `TEdit`, e eu havia **digitado** os
  retângulos à mão com 113 px nos três, quando o `edit_nombre3` tem 33.

  Os dois consertos são do mesmo tipo — parar de digitar o que dá para ler: os
  retângulos saem agora do `.lfm` somando a cadeia de pais, e a medição desconta
  3 px de borda. Mais a guarda que faltava: **tinta ocupando a largura útil
  inteira reprova**, porque não distingue "texto transbordou" de "a moldura
  entrou na conta".

- **E aí ela achou o que existe para achar.** Oráculo `edit_nombre1` mostra
  `ABC.D` — **cinco** caracteres. O port mostrava `ABC.D E` — sete.

  A divergência era **minha, da passagem anterior**. Eu havia posto
  `edit_nombre1.MaxLength := SizeOf(raw_kanji_name) div 2` = 20, e a conferência
  do `dump_truncamento.py` aprovou. **Ela aprovou pelo motivo errado:** aquela
  conferência confere a *aritmética* contra o destino que a tabela `DESTINOS`
  declara — e a tabela é escrita à mão. `40 div 2` fecha em 20; a tela diz 5;
  logo `[0x00433a10]` vale **10** e o destino não é o `raw_kanji_name`.

  Corrigido nos três lugares: o port usa 5 com a medição citada, o gerador
  aceita `None` em `DESTINOS` e emite **`não medido`** para o destino, e o
  markdown perdeu a história do kanji, que era invenção plausível.

  **Qual é o campo de 10 bytes continua sem medir**, e escolher outro que
  também feche a conta seria repetir o erro.

- **Uma regra minha estava errada e reprovava o oráculo por ele ser como é.**
  A primeira versão do veredito exigia `nombre1 == nombre2` "porque têm o mesmo
  filtro". Têm — e `MaxLength` **diferentes**, 5 e 19. Regra estrutural
  inventada sobre o app reprova o app. Ficou a comparação entre os lados, campo
  a campo, que não inventa nada.

- **Uma fragilidade real virou guarda.** A cor de fundo do campo sai da cor mais
  frequente da região. Se a tinta for maioria, a medida **se inverte em
  silêncio** e passa a medir o buraco entre os glifos. Num `TEdit` de 11 px isso
  não acontece — mas o teste sintético o produziu, e a lição é que o modo de
  falha existe. O `tinta()` agora recusa região cuja cor mais frequente não seja
  maioria.

- **Arquivos criados/modificados:**
  - `wte/tools/compara_tela.sh` — o modo `--nomes` e o `edita_nomes`
  - `wte/tools/compara_tela.py` — `retangulos_do_lfm`, `tinta`, `compara_nomes`,
    `relata_nomes`, `main_nomes`
  - `wte/tools/test_compara_tela.py` — 7 testes do modo novo
  - `wte/tools/dump_truncamento.py` + `test_dump_truncamento.py` — o `None` em
    `DESTINOS`, o `MEDIDO_NA_TELA`, e o teste que afirmava a história errada
  - `wte/re/truncamento.md`, `.tsv` — regerados
  - `wte/src/impl/ep2002_mainform.FormShow.inc` — `MaxLength` de 20 para **5**
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 75,4% (9.187 contra 3.003)

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` rc 0;
  `python3 -m unittest` em `tools/`: **523 testes**, OK; `compara_tela.sh
  --nomes` **PASSOU** — tinta 31/41/22 no oráculo contra 32/41/22 no port.

  **O controle negativo é a própria corrida anterior**, e está acima: com o port
  em 20 a régua reprovou com 31 contra 41 px. Ela morde.

- **O que falta para esta task fechar** *(revisado)***:**
  - **uma sequência de tela**: **mover** + `dorsalClick`/`dorsalMouseDown` — só
    cliques, MainForm, sem sub-diálogo;
  - escrever o veredito de **atributos**, **tática** e da metade `ficha_dorsal`
    dos números como conferência **estática** — o `check_bitfields.py` e o
    `dump_zonas.py` já são ela;
  - o destino de `[0x00433a10]` — **não medido**, e agora nomeado como tal;
  - o `iguala_nombres` que não acinzenta — **precisa de CORR própria**;
  - o vetor bola→zona e as tabelas da animação (`lista_formacionesClick`);
  - as três carregadoras de bitmap da ficha — **decisão de escopo, sem dono**.

---

- **Executado em:** 2026-08-18 — **vigésima terceira passagem: a task fecha.**
  Os seis critérios marcados.

- **O último critério era prosa, e prosa não reprova.** O log dizia qual régua
  cobria o quê; handler novo entraria sem instrumento, script mudaria de nome,
  conferência passaria a ser pulada — e o texto continuaria afirmando cobertura.

  O novo [`check_edicao.py`](../../wte/tools/check_edicao.py) mecaniza a frase.
  Ele **não mede tela nem byte**: confere que cada um dos 28 handlers tem
  instrumento nomeado, que o instrumento existe, que o estático passa no próprio
  `--check`, e — a parte que faltava — que o de tela **aparece na evidência de
  trace da corrida que diz cobri-lo**. Produto:
  [`wte/re/edicao-cobertura.md`](../../wte/re/edicao-cobertura.md).

- **O grupo `mover` não pode ter régua de tela, e isso foi MEDIDO.** Antes de
  escrever uma, li o Pascal: o `GravaJogador` do port devolve o código do
  caminho feliz e **não escreve byte nenhum** — a gravação é da WTE-TASK-27.
  Logo o `PreencheJogadores` seguinte repovoa com dado igual e **a tela do port
  não muda**. Régua ali seria teste que tem de falhar até a 27 existir. É a
  opção A vista do outro lado, e agora está escrita como classe `outra_task`,
  não como omissão.

- **A tabela tinha uma mentira, e a primeira versão da ferramenta não pegava.**
  Eu havia atribuído o `dorsalMouseDown` ao `compara_tela.sh --edicao` — que não
  clica camisa nenhuma. O script conferia que o *modo* existe, não que o modo
  *exercita* o handler, e a atribuição atravessou a escrita inteira.

  O conserto é a evidência de trace: o `compara_tela.sh` passou a gravar, por
  modo, quais handlers dispararam de fato
  ([`wte/re/edicao-tela.tsv`](../../wte/re/edicao-tela.tsv), versionada), e o
  `check_edicao.py` exige que todo handler de classe `tela` esteja lá. Rodado, o
  `dorsalMouseDown` reprovou na hora. Ele é `estatico`: dispara com o botão
  **direito** e termina abrindo a ficha do jogador, sub-diálogo que nenhuma
  régua de tela alcança.

  **Dizer que um modo cobre um handler não faz o handler disparar** — e essa
  frase agora tem um teste.

- **Arquivos criados/modificados:**
  - `wte/tools/check_edicao.py`, `wte/tools/test_check_edicao.py` (10 testes)
  - `wte/re/edicao-cobertura.md` — gerado
  - `wte/re/edicao-tela.tsv` + os parciais por modo — a evidência de trace
  - `wte/tools/compara_tela.sh` — grava a evidência
  - `wte/tools/README.md`
  - `docs/tasks/progresso.md`, e o frontmatter desta task

- **Gates medidos:** `make -C wte check` rc 0 (com o `check_edicao.py --check`
  dentro); `lazbuild` rc 0; `python3 -m unittest` em `tools/`: **533 testes**,
  OK; `compara_tela.sh --edicao` e `--nomes` rodados nesta passagem, os dois
  **PASSOU**, e é a evidência deles que o `check_edicao.py` lê.

- **O que esta task NÃO fechou, e tem dono escrito:**
  - **nove handlers em `aberto` pela opção A** — os 7 de mover, o `dorsalClick`
    e o `paderechaeizquierdaClick`: a metade de gravação é da
    [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md). Era o previsto desde
    2026-08-12;
  - ~~o `iguala_nombres` que **não acinzenta** no port — defeito medido pela
    CORR-WTE-057, sem causa, e **precisa de CORR própria**~~ — **fechado em
    2026-08-18** pela [CORR-WTE-060](/docs/tasks/CORR-WTE-060.md): não era
    defeito. O glifo é invariante sob o `gdeDisabled` da LCL, que é grayscale;
    virou divergência deliberada da
    [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md);
  - ~~o destino de `[0x00433a10]` — **não medido**, e nomeado como tal no
    `truncamento.md`~~ — **medido em 2026-08-18** pela
    [CORR-WTE-061](/docs/tasks/CORR-WTE-061.md): é a largura, por time, do
    registro no lote `OFS_TEAM_NAME_KANJI` (`0x004231a0`[0][0]). A mesma
    leitura achou que o vizinho `[0x00433b48]` **não** era `mixed_case_name` —
    é `OFS_TEAM_NAME_3`, e o limite do `edit_nombre2` é 7 no time 2, não 19.
    Sobrou uma discordância de exatamente 1 entre a conta e a tela no primeiro
    campo, que a [CORR-WTE-064](/docs/tasks/CORR-WTE-064.md) fechou no mesmo
    dia: era um `dec` que o original aplica **só** ao lote kanji, e o limite é
    `TEAM_NAME_KANJI_LEN − 1`;
  - ~~o vetor bola→zona e as tabelas da animação, que o
    `estrategia.lista_formacionesClick` preenche~~ — **portado em 2026-08-18**
    pela [CORR-WTE-062](/docs/tasks/CORR-WTE-062.md), com as duas auxiliares.
    O `0x00434230` era **ponteiro**, não vetor: aponta para a tabela de 18 × 44
    de `0x00433f0c`, extraída pelo `dump_formacoes.py`. Sobra outra coisa, com
    dono nomeado — quem aponta os quatro ponteiros **ao abrir** o formulário é
    `0x0040a0b4`, do grupo de carga, e ela não está portada;
  - ~~as três carregadoras de bitmap da ficha (`0x00406fe0`, `0x00407110`,
    `0x00407338`) — **decisão de escopo, sem dono**: a WTE-TASK-29 cobre
    uniforme e bandeira do `MainForm`, não cara/cabelo/barba~~ — **decidido em
    2026-08-18** pela [CORR-WTE-063](/docs/tasks/CORR-WTE-063.md): não serão
    portadas. As três regravam a paleta dentro do `.bmp` compartilhado, na
    pasta de dados do usuário; viraram exclusão deliberada da
    [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md). A saturação em
    `7` do `beard_style` **não** vai junto: ela é do `TUpDown` e chega ao disco
    pela gravação, logo é da
    [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md).
