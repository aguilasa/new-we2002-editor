---
id: WTE-TASK-32
title: "Preço derivado dos atributos — jogador e time inteiro"
type: implementação
category: features
phase: 5
depends_on: ["WTE-TASK-24", "WTE-TASK-25"]
status: concluído
---

# WTE-TASK-32: Preço do jogador

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.1.
- Primeira das quatro features que motivaram o projeto: **o `ed.exe` não
  *oferece* preço** — o editor do Obocaman oferece. Novidade da v0.98 para o
  jogador e da v0.99 para o time inteiro ("calculate credits for a whole team
  with just one click").

> **A frase acima dizia "o `ed.exe` não calcula preço", e isso era falso**
> ([CORR-WTE-094](/docs/tasks/CORR-WTE-094.md), 2026-08-24). Ele calcula: a
> fórmula está em `legacy/mfc/edDlg.cpp:7703` (`CalcolaCostoGiocatore`), o laço
> do time inteiro em `:7948`, e o handler no message map em `:1286`. O que não
> existe é o **controle** — `CMD_CALCCOSTI` (1244) está no `resource.h` e não
> no `ed.rc`, o mesmo caso do `MainForm.Button2Click` no binário do Obocaman.
>
> **Isso dá a esta task um oráculo B que ela não sabia ter**, e já em Pascal:
> `ComputePlayerCost` em `wte/src/we2002_database.pas:1776`, transpilado de
> `src/core/Database.cpp:1465`.
>
> **Sem presumir fórmula igual.** A do `ed.exe` é `double`, parte de `k = 16`,
> ramifica por posição e fecha em `if (k<1) k = 1; return (int)ceil(k);`; a do
> Obocaman é inteira, sobre uma soma, com `0x2DC6C0`, `0x9C40`, `0x2BC`, `7`,
> um `+5` e a variante `× 5 div 3`. O valor dele é **desenhar a amostragem**:
> os três riscos da seção "onde a tabela pode enganar" estão todos
> exemplificados lá — saturação no `if (k<1)`, arredondamento no `ceil`, e
> termo cruzado nos bônus `== 19` e no `if(foot == 2)`.

**Vem primeiro entre as quatro, e fora de ordem no plano geral** (§10, passo 5):
entrega valor antes de a Fase 4 fechar, é isolada e valida o ferramental de
decompilação num alvo pequeno e conferível.

> **"Não depende de gravação" era metade verdade, e a
> [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) mediu a outra metade em
> 2026-08-21.** Vale para o `etiqprecioClick`, que só mostra o número na tela.
> **Não vale** para o preço do time inteiro: o `base_teamClick` percorre os 23
> slots e **grava um byte em cada**, no offset da terceira coluna da tabela de
> offsets — a mesma coluna condicional que a `0x004046E8` usa. A régua desta
> task é **dupla**: tela para a fórmula, byte para o time inteiro.

---

## Objetivo

Recuperar a fórmula e implementá-la, com prova numérica.

### Alvos

| Handler | Formulário | Endereço | O que falta |
|---|---|---|---|
| `etiqprecioClick` | `jugador` | `0x00408bb8` | a fórmula, e o número na tela |
| `casilla_precioKeyPress` | `jugador` | `0x00408b9c` | o filtro de tecla do campo |
| `base_teamClick` | `MainForm` | `0x00410ff4` | **o laço dos 23 e a gravação** |

O `base_teamClick` chegou nesta lista pela WTE-TASK-30, que implementou a
**moldura** dele — posicionar o `ficha_creditos_equipo`, mostrá-lo e desistir
em `mrCancel` — e deixou o miolo aqui, com o veredito `aberto` e o dono
nomeado. A spec medida está em
[`wte/re/spec/MainForm.base_teamClick.md`](../../wte/re/spec/MainForm.base_teamClick.md)
e já traz a faixa de endereços da fórmula (`0x004110E7`..`0x0041112A`), as
constantes que aparecem nela (`0x2DC6C0`, `0x9C40`, `0x2BC`, `7`, `+5`) e a
variante `× 5 div 3` de `0x00411142`.

**Quem separa titular de reserva ali é o ponteiro do `Sender`**, comparado com
o campo `base_team`, e não o nome — o `LadoTitular` do `.aux.inc` não serve.

### O método que **não** precisa de decompilador

A fórmula é aritmética pura sobre atributos já decodificados. Então dá para
recuperá-la por **tabela de verdade**:

1. Abrir o original no Wine com um jogador conhecido.
2. Variar **um** atributo por vez, ler o preço na tela, tabelar.
3. Repetir para cada atributo.
4. Ajustar a fórmula contra a tabela.

Isso é observação, não engenharia reversa de código — e produz evidência mais
forte que ler assembly, porque mede o comportamento em vez de interpretá-lo.

**Use o decompilador para conferir a fórmula recuperada, não para descobri-la.**
As duas fontes concordando é a melhor evidência que este projeto pode ter.

### Onde a tabela pode enganar

- **Saturação.** Se o preço satura num teto, variar atributo alto não move nada
  e a tabela sugere coeficiente zero.
- **Arredondamento.** Divisão inteira vs. real muda o resultado em ±1 e some no
  olho. Amostrar valores que caiam perto de meio.
- **Termo cruzado.** Se a fórmula tiver produto de dois atributos, variar um por
  vez não revela. Testar pelo menos um par variando junto.

### O time inteiro

O botão de time é presumivelmente a soma dos jogadores — **presumivelmente**.
Conferir: pode haver desconto, teto, ou tratamento diferente do goleiro.

### Critério

Acerto em **100%** de uma amostra grande, não numa amostra escolhida. Gerar a
amostra a partir dos jogadores reais das duas ROMs e comparar app contra
original, jogador a jogador.

**Não precisa de golden test de imagem** — o preço não é gravado, é exibido.

> **Esta linha do enunciado está errada, e a execução mediu por quê.** Ela vale
> para o `jugador.etiqprecioClick`, que mostra o número na tela; a outra metade
> da feature, o `MainForm.base_teamClick`, **grava** um byte por jogador. A
> régua desta task é dupla — tela para a fórmula, byte para o time inteiro —, e
> o golden de byte é o
> [`golden-22-precos`](../../wte/tests/roteiros/golden-22-precos.txt). O
> enunciado fica como foi escrito; a §5.1 do plano, que dizia o mesmo, foi
> corrigida pela [CORR-WTE-098](/docs/tasks/CORR-WTE-098.md).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/jugador.etiqprecioClick.md` | criar |
| `wte/re/spec/jugador.casilla_precioKeyPress.md` | criar |
| `wte/re/preco.md` | criar — a fórmula, a tabela de verdade, as duas fontes |
| `wte/re/preco.tsv` | criar — a amostra medida |
| `wte/src/we2002_preco.pas` | criar |
| `wte/tests/test_preco.pas` | criar |
| `wte/tests/dump_preco.pas` | criar |
| `wte/tools/check_preco.py`, `test_check_preco.py` | criar |
| `wte/tests/roteiros/golden-22-precos{,.port}.txt` | criar |

*Adaptado na execução:* a task listava `wte/re/spec/etiqprecioClick.md` sem o
prefixo de formulário, e o `spec_index.py` exige `<formulario>.<handler>.md`.
E faltava a segunda spec — o `casilla_precioKeyPress` também não tinha
arquivo.

---

## Critério de conclusão

- [x] Fórmula recuperada por tabela de verdade — **132 jogadores, 6 times**,
      em [`wte/re/preco.tsv`](../../wte/re/preco.tsv)
- [x] Fórmula conferida contra o disassembly, e as duas fontes concordando —
      e são **três**: os dois handlers foram lidos instrução a instrução e são
      a mesma fórmula compilada duas vezes (`0x004110e7`..`0x0041112a` e
      `0x00408c3b`..`0x00408c83`)
- [x] Saturação, arredondamento e termo cruzado testados explicitamente —
      [`test_preco.pas`](../../wte/tests/test_preco.pas), 12 conferências. A
      saturação é **transbordo de 32 bits**, e o ponto de virada foi medido:
      soma **216**
- [x] Cálculo do time inteiro conferido, não presumido soma — não é soma: é a
      mesma fórmula por jogador, e o achado foi outro (o slot 22)
- [x] `base_teamClick` com golden verde — **byte, não tela** —, com o controle
      fechando antes, e o veredito trocado no `re/spec/INDICE.md`
- [x] 100% de acerto sobre amostra grande — **das duas ROMs não**, e a razão é
      medida: a ROM europeia **não hospeda este oráculo**. A corrida sobre ela
      gravou zero bytes; o `wte.exe` morre na troca de time com aquela imagem
      ([CORR-WTE-044](/docs/tasks/CORR-WTE-044.md)). É a mesma adaptação que a
      WTE-TASK-31 fez no critério 4, e as linhas europeias estão no TSV **sem**
      `medido`, com o coletor dizendo isso em voz alta
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo do que foi feito:**

  A fórmula é `s⁴ div 3000000 + s³ div 40000 + s² div 700 + s div 7 + 5`, com
  `× 5 div 3` para goleiro, sobre a soma das dezesseis barras de habilidade. Ela
  está inteira em [`wte/re/preco.md`](../../wte/re/preco.md). **Com ela, a fase
  4 fechou: 96 de 96 vereditos.**

  **O método rendeu mais que o previsto, e por uma troca.** A task manda montar
  a tabela de verdade lendo o preço de **um** jogador na tela. Ler a tela custa
  OCR; mas o `base_teamClick` do oráculo **grava** o preço de 22 jogadores na
  imagem, e byte se lê com `cmp`. Cada corrida do oráculo passou a valer 22
  amostras em vez de uma, e a amostra final tem **132 jogadores em 6 times**,
  com 100% de acerto. A régua ficou mais forte *e* mais barata.

  **As duas metades da feature são a mesma fórmula compilada duas vezes**, e
  isso não era garantido — o enunciado alertava que o preço do time podia ter
  desconto ou teto. Lidas instrução a instrução, `0x004110e7`..`0x0041112a` e
  `0x00408c3b`..`0x00408c83` são idênticas. O que muda é de onde vem a soma: o
  `etiqprecioClick` soma o que está **na tela** (as dezesseis
  `barrhab<N>.Position`), e o `base_teamClick` soma da **memória**, porque não
  tem tela por jogador.

- **O que se aprendeu, e vale para as próximas:**

  **1. A saturação que a task previu existe, e não é teto — é transbordo.** O
  original faz `imul` de 32×32 e logo em seguida um `cdq`, que joga fora a
  metade alta antes da divisão. Em Pascal isso é `LongInt` **deliberado**: com
  `Int64` o preço divergiria de toda soma ≥ **216** (medido, não estimado — é
  onde 215⁴ deixa de caber em 31 bits), e a partir dali o preço do original
  **cai** enquanto o de 64 bits sobe. Jogador real não chega lá; nada no formato
  impede.

  **2. O original preça 22 slots, não 23** — achado que ninguém procurava. O
  laço vai de 0 a 22 e grava 22 bytes. Medido em seis times; no time 9 os slots
  21 e 22 têm a **mesma** soma e a **mesma** posição, e só o 21 é gravado, o que
  descarta explicação pelo conteúdo.

  Esta linha explicou o salto pelo `je` da terceira coluna — *"a terceira coluna
  do slot 22 sai zero e ele é pulado"* — e a
  [CORR-WTE-095](/docs/tasks/CORR-WTE-095.md) **refutou isso em 2026-08-24**,
  sob `strace`: o oráculo **lê** o byte condicional do slot 22 em 3067472, com o
  mesmo número de seeks dos outros 22, e a `0x004046e8` só faz essa leitura
  quando a coluna **não** é zero. O byte se perde na **escrita**, dentro da
  `0x00403400`, e o mecanismo continua aberto. Três coisas ficaram fechadas: o
  salto é real (`0xFF` plantado em 3067472 sobrevive à corrida), a conta de
  offset do port não está errada (a `0x00404374` decide por time, nunca por
  slot), e o slot 22 é endereçável — o `io-medido.tsv`, sessão `27-mcr2iso`,
  mostra o import de `.mcr` gravando os **23** bytes condicionais do time 3.

  **3. Duas janelas do mesmo tamanho podem exigir coordenadas diferentes.** O
  `ficha_creditos_equipo` mede 285×124 nos **dois** lados, e o clique no botão
  de confirmação precisa de `(183,89)` no oráculo e `(180,60)` no port: sob Wine
  a moldura é desenhada **dentro** da janela X, sob gtk2 sem gerenciador não há
  moldura. Buscar por tamanho não distingue os dois casos. Com a coordenada
  errada o diálogo sai por `mrCancel`, o port não grava nada, e o diff parece
  erro de fórmula.

- **Arquivos criados/modificados:**

  - criados: `wte/src/we2002_preco.pas`, `wte/tests/test_preco.pas`,
    `wte/tests/dump_preco.pas`, `wte/tools/check_preco.py`,
    `wte/tools/test_check_preco.py`, `wte/re/preco.md`, `wte/re/preco.tsv`,
    `wte/re/spec/jugador.etiqprecioClick.md`,
    `wte/re/spec/jugador.casilla_precioKeyPress.md`,
    `wte/src/impl/ep2002_jugador.etiqprecioClick.inc`,
    `wte/src/impl/ep2002_jugador.casilla_precioKeyPress.inc`,
    `wte/tests/roteiros/golden-22-precos{,.port}.txt`,
    `docs/tasks/CORR-WTE-095.md`
  - modificados: `wte/src/impl/ep2002_mainform.base_teamClick.inc` (o miolo),
    os dois `.uses`, `wte/tools/check_fase4.py`, `wte/re/fase-4-golden.tsv`,
    `wte/re/spec/MainForm.base_teamClick.md`, `docs/PLAN-WTE-LAZARUS.md` §4.4,
    `docs/tasks/progresso.md`, `docs/tasks/correcoes-progresso.md`,
    `.gitignore` — as dez regras dos binários compilados de `wte/tests/`
    (`dump_preco`, `test_preco` e os oito irmãos), que são gerados pelo
    `check_preco.py`, pelo `compara_tela.sh` e pelos testes de ferramenta.
    É a única alteração da task que não é sobre preço, e a que alguém
    procuraria depois — *"quando foi que passamos a ignorar os binários de
    teste?"*
  - regerados: `wte/re/fase-4.md`, `wte/re/fase-2.md`,
    `wte/re/fase-3-fechamento.md`, `wte/re/spec/INDICE.md`, os `ep2002_*.pas`

- **Problemas encontrados:**

  **A guarda que escrevi pegou a mim mesmo, e estava certa.** O cabeçalho do
  `check_preco.py` avisa que *"o byte de preço de uma imagem virgem não é
  resposta de ninguém"*. A primeira versão do coletor ignorou o próprio aviso:
  incluiu a amostra da ROM europeia — onde o oráculo gravou **zero** bytes — e
  acusou 21 divergências contra os preços de fábrica. Hoje o coletor **exige
  prova** de que o oráculo escreveu, comparando a faixa do time contra a ROM
  virgem antes de marcar qualquer linha como medida.

  **E o `golden-22-precos` reprovou na primeira corrida por coordenada, não por
  fórmula** — ver a lição 3 acima. O diff era exatamente a faixa de preço, o que
  faz o erro parecer de cálculo.
