# Plano — port em Python do editor de `.mcr` do WE2002, com UI Qt

> **Estado:** nenhuma fase executada. Este arquivo é a **fonte de verdade** do
> ciclo `port-mcr`; o andamento fica em
> [/docs/tasks/port-mcr/progresso.md](/docs/tasks/port-mcr/progresso.md).

---

## 0. Escopo

### Objetivo

Um editor do **memory card do Winning Eleven 2002 (PSX)** escrito em Python:
núcleo puro que lê e grava o save dentro de um `.mcr` de 128 KiB, e uma UI Qt
por cima dele. O ponto de partida é o
[`zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1`](https://github.com/zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1)
(VB.NET/WinForms), **portado literalmente** onde ele acrescenta conhecimento, e
medido contra o que este repositório já sabe.

O que o editor edita, na v1:

- os **23 jogadores** do slot de Edit Mode — 12 bytes de atributo empacotado
  (posição, aparência, físico e os 16 atributos de 3 bits) e 10 bytes de nome;
- os **números de camisa**, de 5 bits, na tabela de 16 B;
- a **formação**: X e Y dos 10 jogadores de linha, o papel posicional de cada
  um, os cobradores de bola parada e o capitão.

### Não-objetivos

- **Não** mexer na imagem de CD. A ponte cartão↔ISO é do editor do Obocaman e
  do `newWe2002`; aqui é cartão, só.
- **Não** portar o que o upstream tem de próprio dele: o navegador embutido, o
  banco Access `BD.accdb`, o raspador de Sofifa/Transfermarkt/PESMaster, as
  faces `.bmp` e o campo de URL em `130880`. Nada disso é dado do save.
- **Não** editar tática na v1 — ver §5.6.
- **Não** estender o `we2002_core`. Vale aqui a mesma proibição da §6.9 do
  [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md): o que for compartilhado é
  copiado com atribuição no comentário.

### Definição de pronto

1. `mcr roundtrip` byte-idêntico nas **duas** formas (§5.1);
2. controle negativo **5/5 vermelhos** (§5.2);
3. `layout.py --check` **17/17** contra [`wte/re/mcr.md`](../wte/re/mcr.md);
4. codec de atributos com **0 divergências** contra `Player::Decode/Encode`
   (§5.4);
5. a UI abre no `:98`, lê um cartão, edita ficha e formação, grava, e o
   arquivo gravado passa no round-trip;
6. `ctest -R mcr` numa máquina sem venv e sem fixture: **1 passed, 2 skipped**.

---

## 1. Diagnóstico — o que já está medido

Tudo desta seção sai de `work/entrada.mcr` (131.072 B, cartão japonês válido,
`BISLPM-86600WEW-OPT`, **fora do git**) e do código já no repositório. Medido em
2026-09-07.

### 1.1 O contêiner PSX, e o molde que já temos

`wte/tools/dump_mcr.py` conhece o contêiner pela spec pública do nocash:
`CARTAO_BYTES = 0x20000`, `BLOCO_BYTES = 8192`, `QUADRO_BYTES = 128`,
`QUADROS_DE_DIRETORIO = 15`, e o dicionário completo de estados — `0x51/0x52/0x53`
(primeiro/meio/último da cadeia), `0xA0/0xA1/0xA2/0xA3` (livre, e as três formas
de "era"), `0xFF`.

Na fixture: `d[0:2] = 4d 43` (`MC`), e a entrada 1 do diretório é
`51 00 00 00 | 00 40 00 00 | 01 00` — estado, tamanho 16.384 e link.

`we-team-editor/data/dat.bin` (145.408 B) começa com `MC`: a primeira metade é
um **cartão-molde de 131.072 B**, e é dele que sai o cartão virgem do editor do
Obocaman.

### 1.2 Os 17 destinos, e os 14 num bloco que o diretório diz livre

[`wte/re/mcr.md`](../wte/re/mcr.md) traz a tabela medida do
`we-team-editor.exe`: 17 destinos `(endereço, campo, bytes, quem escreve, quem
lê)`. Dois fatos dela decidem o desenho:

- **14 dos 17 caem no bloco 3**, que o diretório declara **livre** (`0xA0`);
- o escritor original **nunca toca o diretório** — o menor endereço que ele
  grava é `0x5404` — e **não recalcula o checksum XOR** de quadro.

O port reproduz os dois, e §5.6 diz por quê.

### 1.3 O registro de 32 bytes: 12 + 10 + 10 intocados

Base `0x5904` (=22788), passo 32, **23 entradas** — e o zetaprog chega
independentemente aos mesmos números (`ListBoxMcrOffset`, de 22788 a 23492).

| faixa | conteúdo |
|---|---|
| `+0..+11` | atributos empacotados |
| `+12..+21` | nome, 10 bytes |
| `+22..+31` | **não tocado por nenhum dos dois editores** |

Na fixture o slot 0 tem `00 00 00 e1 00 85 e0 00 1b 0c` nos dez finais: não é
preenchimento, é dado que ninguém decodifica ainda. **Passa intacto.**

### 1.4 O codec de atributos **já tem oráculo neste repositório**

O mapa de bits do zetaprog — `skin(2) body(3) age(5) response(3) gap(1)
bodybalance(3) stamina(3) dribble(3) speed(3) acceleration(3) offense(3)
defense(3) shotpower(3) shotacc(3) pass(3) technique(3) head(3) jump(3)
curve(3) aggression(3) boots(3) feet(2)` — é o mesmo codec de
[`src/core/Player.cpp`](../src/core/Player.cpp), campo por campo:

| zetaprog | `Player::Decode()` |
|---|---|
| `skin = raw[4] & 0x03` | `skin_colour = raw_attributes[4]&0x03` |
| `bodybalance` | `strength = 12 + ((raw[5]>>6)&0x03) + ((raw[6]<<2)&0x04)` |
| `feet` | `foot = (raw[11]>>6)&0x03` |
| `feetoutside` (nibble alto de `+3`) | `out_of_position = (raw[3]>>7)&0x01` |

E o `Player::Decode()` decodifica **um campo que o zetaprog trata como tabela
separada**: `number = 1 + ((raw_attributes[3]>>2)&0x1f)`.

**Consequência de projeto:** a parte mais cara do port não é engenharia
reversa — são duas implementações independentes que **têm de concordar**, e a
discordância é medível sem emulador, sem Wine e sem imagem.

### 1.5 Os dorsais estão gravados duas vezes, e é a melhor tripwire do plano

A tabela de 16 B em `0x5404` (=21508) guarda 24 valores de 5 bits — 4 grupos de
4 bytes, 6 valores por grupo, deslocamentos `(5·(j mod 6)) mod 8 = [0,5,2,7,4,1]`,
a mesma forma do `SquadNumbers` do `we2002_core`. O cartão guarda **o número
menos um**.

Medido na fixture: os 23 slots do bit-field do registro e os 23 da tabela
**concordam 23 de 23** —

```
tabela:     1  5  4  3  2  7  6 11 10  9  8 16 17 13 19 22 12 18 20 14 15 21 23
no registro:1  5  4  3  2  7  6 11 10  9  8 16 17 13 19 22 12 18 20 14 15 21 23
```

O slot 24 da tabela, não usado, guarda 0 (que lido dá 1).

Qualquer erro de `±1` ou de bit-packing na gravação **rompe o par no primeiro
save**, e o teste custa uma subtração. É por isso que ele é critério de
conclusão da MCR-TASK-07 e não uma curiosidade.

O zetaprog descreve essa leitura como "inverter os bytes e ler da direita para
a esquerda". É a mesma conta escrita de outro jeito; o port usa
`int.from_bytes(..., "little")` e os deslocamentos acima.

### 1.6 O nome de 10 bytes **não é ASCII** — é cp932

Medido:

| slot | bytes | cp932 | como ASCII |
|---|---|---|---|
| 0 | `50 a5 83 57 ae b0 d9 83 59 00` | `P･ジｮｰﾙズ` | `P??W????Y` |
| 20 | `83 4b d8 bd a5 db 83 6f b0 bd` | `ガﾘｽ･ﾛバｰｽ` | ilegível |

É mistura de ASCII, katakana **meia-largura de 1 byte** e Shift-JIS de 2 bytes.
Duas consequências, as duas caras se descobertas tarde:

- **O `TextCodec` do `we2002_core` não serve para este campo.** O
  `KanjiToAscii` só translitera pares que começam em `0x82` e manda todo o resto
  para espaço de largura dupla — o slot 0 sai como cinco espaços. Usá-lo aqui
  **apaga nome japonês em silêncio**. O `TextCodec` continua certo para o que
  ele foi escrito: o nome de time da imagem de CD.
- **O zetaprog assume ASCII** e tem o mesmo defeito, agravado por um
  `Regex.Replace(texto, "[^a-zA-Z.]", "")` antes de gravar.

E o campo **não é cadeia terminada em NUL**: o slot 20 usa os 10 bytes. O
readme do Obocaman registra isso como correção da v0.98 ("the spaces in the
players names").

### 1.7 A formação: X[10], Y[10] e papéis[10] dentro dos 30 bytes

Nossa RE tinha `MCR_FORMACAO_2 = $62A8` (20 B) e `MCR_FORMACAO_1 = $63D5` (10 B)
como faixas opacas. **É aqui que o zetaprog acrescenta de fato**: são
X, Y e papel posicional.

Medido na fixture:

```
X      @0x62A8  0b 0b 0b 0f 0f 14 1f 1f 2c 29
Y      @0x62B2  20 34 48 11 57 32 1e 3e 2a 3e
papéis @0x63D5  02 03 06 07 08 0a 0e 10 11 13   -> índices 0,1,4,5,6,8,12,14,15,17
```

Os fatores `X*7` e `Y*2` do upstream são **de tela**, não de formato. O papel é
gravado como **índice + 2**, sobre uma lista de 20 rótulos (`CB-L`, `CB-R`,
`SW`, `LIB`, `CB-C`, `LB`, `RB`, `DH-L`, `DH-C`, `DH-R`, `LH`, `RH`, `OH-L`,
`OH-C`, `OH-R`, `CF-L`, `CF-C`, `CF-R`, `LW`, `RW`).

Os cobradores ficam numa **tabela não-crescente** — `0x614F, 0x6140, 0x6122,
0x6113, 0x6131` —, o que é razão suficiente para tabela em vez de aritmética.
Na fixture eles valem `[7, 7, 8, 7, 7]`.

### 1.8 A discordância do `0x6500`

`0x6500` (=25856) vale `8` na fixture. Nossa RE do `.exe` o chama de
**capitão**; o zetaprog o chama de **sexto cobrador** ("C"). Os dois papéis
guardam índice de slot, então **o valor sozinho não discrimina** — só um
experimento no oráculo do Obocaman resolve, e é a MCR-TASK-13.

Enquanto não houver veredito, o port **passa o byte intacto** e não o expõe na
UI.

### 1.9 A tática vai e não volta

O escritor original grava seis destinos de tática — `0x64E2` e `0x6102` (o
mesmo byte, e o mesmo mais 50), e os nibbles em `0x6479`/`0x6488` e
`0x6497`/`0x64A6` — e **o leitor dele nunca lê nenhum**: quem lê tática de um
`.mcr` é o `boton_mcr2iso`, direto para a imagem.

Na fixture: `0x64E2 = 1`, `0x6102 = 51`, nibbles `0/14` e `4/9`.

**Decisão: na v1 a tática é somente leitura**, e os seis bytes atravessam
intactos. Editar tática sem oráculo trocaria um desconhecido por outro.

### 1.10 O que o zetaprog **não** entende do formato

Ele trata o cartão como um binário plano de 131.072 B com endereços absolutos.
Não há no fonte dele nenhuma menção a diretório, quadro, bloco de 8192,
estado, checksum XOR, nem aos formatos `.gme`/`.vgs`/`.mcd`. Três efeitos:

1. só funciona com dump raw de 128 KiB;
2. **quebra se o save não estiver no bloco esperado** — o offset inteiro se
   desloca em múltiplos de 8192;
3. ele grava IDs de um banco privado nos bytes **0..137**, que são — medido — o
   quadro de cabeçalho `MC` inteiro **mais** `state`+`size`+`link` da entrada 1
   do diretório. Não é sujeira em campo livre: é um cartão que nenhum console
   lê. O próprio autor detecta `0x434D` (`MC`) para saber se aquele slot de ID
   ainda não foi sobrescrito.

O port **recusa qualquer escrita abaixo de `0x800`**, e isso é caso de controle
negativo.

---

## 2. Ressalva legal e linhagem

O upstream **não tem licença** — sem `LICENSE`, sem cabeçalho, `"license": null`
na API do GitHub, e um `<Copyright>Copyright © 2023</Copyright>` no `.vbproj`.
Todos os direitos reservados por padrão. O usuário foi avisado e **decidiu
portar literalmente**, em 2026-09-07.

A posição do repositório não muda por isso, e é a mesma de sempre:

- **não há `LICENSE`** e não vai haver — o código herdado de Moriero (2002) e
  thyddralisk (2015) já é todos-os-direitos-reservados. Ver
  [NOTICE.md](../NOTICE.md).
- **o fonte VB do upstream não entra no git.** Ele é clonado para
  `work/easy-mcr/` (gitignored, como `we-team-editor/`), com o SHA
  `30af1fe59cf96beee3b066f6cdfcb1b6f3df37cc` fixado e o inventário de arquivos
  registrado na MCR-TASK-02. O que entra é o port.
- **a diferença de método para o ciclo `wte/` fica escrita.** Lá o editor do
  Obocaman foi tratado como binário a medir, nunca a transcrever; aqui há fonte
  e o dono decidiu transcrever. Um leitor futuro precisa das duas razões lado a
  lado para não concluir que a regra mudou sozinha.

O que fica **legível como limite**, e é a razão de cada módulo declarar
proveniência (§3.3):

| natureza | onde |
|---|---|
| medição nossa | `card.py`, `layout.py`, os cross-checks |
| transcrição do upstream | `attributes.py`, `formation.py`, `domains.py` |
| dado de terceiro que **não entra** | `BD.accdb`, as faces `.bmp`, os presets de foto |

---

## 3. Arquitetura

### 3.1 Onde mora

`tools/mcr/`, ao lado de `tools/pes2/` — mesmo precedente: projeto separado,
Python 3 puro, sem compartilhar build, com gates próprios no `ctest`.

`src/` é território do CMake e do C++/Qt6 do `newWe2002`; `wte/` é a árvore
Lazarus. Se um dia isto for empacotado sozinho, vira `mcr/` na raiz com
`pyproject.toml`, e os nomes de módulo não mudam — a mudança custa um commit.
Não antecipar.

### 3.2 Os módulos

```
tools/mcr/
  card.py         conteiner PSX: diretorio, blocos, quadros, estados, checksum
  layout.py       os 17 enderecos -- FONTE UNICA, conferida contra wte/re/mcr.md
  attributes.py   o codec de 12 bytes
  numbers.py      os 23 dorsais de 5 bits (0x5404)
  text.py         o nome de 10 bytes <-> str, em cp932
  formation.py    X[10], Y[10], papeis[10], cobradores, capitao, os presets
  tactics.py      os 6 campos de tatica -- somente leitura na v1
  domains.py      cabelos, posicoes, barbas, cores, alturas, idades, corpos, chuteiras, pe
  model.py        Card / Player / Formation -- dataclasses, sem Qt, sem endereco
  io.py           ler, gravar, validar, recusar
  glossary.py     es -> en, e a recusa de espanhol remanescente
  cli.py          argparse: info dump get set roundtrip negative check
  selftest.py     o agregador, com o controle negativo
  ui/             app.py, main_window.py, squad_view.py, player_form.py, formation_view.py
```

### 3.3 As três regras de desenho

**Regra 1 — só `layout.py` tem endereço.** Nenhum outro módulo escreve
constante de endereço, e `layout.py --check` se mede contra a tabela de
[`wte/re/mcr.md`](../wte/re/mcr.md): 17/17, nos dois sentidos. Precedente
exato: o `dump_mcr.py` já confere o `we2002_mcr.pas` contra o `.exe` a cada
`make -C wte check`.

**Regra 2 — os bytes crus são normativos.** `model.Card` guarda os 131.072
bytes e edita por read-modify-write **no campo**; nada mais é tocado. É o que
torna o round-trip byte-idêntico alcançável — os 10 bytes finais de cada
registro, a folga do bloco, o diretório e os seis campos de tática atravessam
porque ninguém os reescreve. O contraexemplo é o upstream, que remonta o
arquivo, e por isso consegue escrever no cabeçalho.

**Regra 3 — a UI não conhece endereço, e o núcleo não conhece Qt.** Duas
guardas mecânicas no `selftest.py`: `tools/mcr/ui/*.py` não importa `layout`,
`card` nem `io`; e depois de importar o núcleo inteiro,
`assert "PySide6" not in sys.modules`. Sem a segunda, o gate obrigatório passa
a exigir Qt.

### 3.4 Proveniência — quem sabe o quê

Cada módulo abre com três linhas dizendo qual célula desta tabela ele é.

| módulo | contêiner | endereço | semântica | codec |
|---|---|---|---|---|
| `card.py` | spec nocash + `dump_mcr.py` | — | — | — |
| `layout.py` | — | **`wte/re/mcr.md`** | — | — |
| `attributes.py` | — | — | upstream (nomes, domínios) | **`src/core/Player.cpp`** |
| `numbers.py` | — | `wte/re/mcr.md` | upstream | próprio (§1.5) |
| `text.py` | — | — | medido (§1.6) | próprio — **`TextCodec` não serve** |
| `formation.py` | — | `wte/re/mcr.md` | **upstream** (§1.7) | próprio |
| `tactics.py` | — | `wte/re/mcr.md` | aberta — sem oráculo | — |
| `domains.py` | — | — | upstream inteiro | — |

### 3.5 Nomenclatura

Identificadores em **inglês**; docstrings em **português**. O fonte de origem é
espanhol, então `glossary.py` carrega o mapa (`jugador→player`, `cancha→pitch`,
`formacion→formation`, `grabar→write`, `bufersizenum→group_size`) e o
`selftest` recusa espanhol remanescente. Mesma mecânica de
[tools/glossary.py](../tools/glossary.py) com o italiano do `legacy/mfc/`.

---

## 4. Ambiente

### 4.1 O Python é duplo nesta máquina, e é a armadilha número um

`python3` do `PATH` é o **mise 3.13.13**
(`~/.local/share/mise/installs/python/3.13/`); `/usr/bin/python3` é **3.12.3**;
e o `build/CMakeCache.txt` fixou o mise. Portanto:

> **`apt install python3-pyqt6` instala para o 3.12 e fica invisível.** O apt
> termina em verde e o `import` continua falhando.

### 4.2 A decisão: PySide6 em venv

```sh
python3 -m venv work/venv-mcr
work/venv-mcr/bin/pip install 'PySide6>=6.8'
```

Quatro razões: o Python duplo acima; **licença** (PySide6 é LGPL, PyQt6 é
GPL-ou-comercial, e este repositório não pode ser licenciado); **sem colisão de
ABI** com o Qt6 do sistema que serve ao `newWe2002` em C++; e `work/` é
gitignored e o `make fresh` não o apaga (ele remove quatro caminhos nomeados).

A MCR-TASK-03 registra no Log a versão resolvida, o `python -VV` do venv e o
`pip freeze` — "instalei PySide6" não é medição.

### 4.3 A UI roda no `:98`

Vale a regra do repositório sem exceção: `make mcr-98` para o Xvfb, e `:1`
só a pedido explícito do usuário.

### 4.4 Os três alvos de `ctest`

| alvo | precisa | skip |
|---|---|---|
| `mcr_selftest` | nada — cartão sintético em memória | **nunca**; é o obrigatório |
| `mcr_card` | `WE2002_MCR_CARD` apontando um `.mcr` | `SKIP_RETURN_CODE 77` |
| `mcr_ui` | venv com PySide6 + `:98` | `SKIP_RETURN_CODE 77` |

Critério: máquina limpa, sem venv e sem variável → `ctest -R mcr` dá
**1 passed, 2 skipped** — nunca `0 tests`, nunca erro.

---

## 5. Estratégia de verificação

Seis níveis. Os cinco primeiros têm oráculo; o sexto diz o que não tem.

### 5.1 Round-trip byte-idêntico

Duas formas, e a segunda é a que vale:

1. ler → gravar. Prova o I/O.
2. ler → **decodificar os 23 jogadores para o modelo** → re-codificar todos →
   gravar. Prova o encoder.

`cmp` = **0 bytes** nas duas. Precedente: `golden-13-roundtrip` do ciclo `wte/`
e o `iso.py roundtrip` dos 244 arquivos.

### 5.2 Controle negativo

"Um guard que nunca ficou vermelho é decoração" — a lição das
`CORR-PES2-009` e `CORR-PES2-020`. Cinco injeções, cada uma com o guard que ela
tem de acender:

| injeção | guard |
|---|---|
| trocar `speed` e `dribble` no encoder (o bug da v4.2) | round-trip com edição |
| tirar o `−1` da gravação do dorsal | o cross-check dos dois codificadores |
| escrever 138 bytes em `0x0000` | a recusa de escrita abaixo de `0x800` |
| trocar o estado do quadro 1 de `0x51` para `0xA0` | a validação de diretório |
| truncar o arquivo em 1 byte | a validação de tamanho |

**5/5 vermelhos.** Um caso verde é bug do guard, não do teste.

### 5.3 Cross-check dos endereços

`layout.py --check` contra os 17 destinos de [`wte/re/mcr.md`](../wte/re/mcr.md),
conjunto idêntico nos dois sentidos, mais duas asserções que a `mcr.md` já
cobra e que não custam nada: a tabela de cobradores **não é crescente**, e os
deslocamentos de bit do dorsal são `[0,5,2,7,4,1]`.

### 5.4 Cross-check do codec de atributos — o oráculo mais forte e mais barato

Duas implementações independentes: a nossa (transcrita de `Player.cpp`) e a do
upstream (o bitstream com carry da árvore `lite/`). Três medições:

1. os **23 registros da fixture**, campo a campo — 0 divergências;
2. **100.000 blobs de 12 bytes** com semente fixa — 0 divergências;
3. `encode(decode(b)) == b` nos dois, nos mesmos 100.000 — 0 divergências.

Mais a tripwire da §1.5: `1 + ((raw[3]>>2)&0x1f) == numbers[j]` para os 23
slots. **23/23 na fixture.**

Nível acima, se a transcrição de `Player.cpp` ficar em dúvida: `tests/golden_tool.cpp`
já linka o `we2002_core`, e um subcomando que imprime os 30 campos de um blob
dá o diff C++ × Python sem transcrição no meio.

### 5.5 O oráculo do Obocaman

`make wte` (Wine, prefix `win32`, `:98`) responde três perguntas, e só elas:

- **o `0x6500`**: pôr o capitão num slot conhecido e os cinco cobradores em
  slots distintos, salvar, ler os seis bytes. Discrimina o que o valor sozinho
  não discrimina (§1.8).
- **o nome que enche os 10 bytes**: escrever nome de 10 caracteres com espaço
  no fim e ler de volta.
- um **cartão salvo pelo próprio jogo**, se der para produzir um pelo
  DuckStation, é o único jeito de validar os 17 presets de formação e os
  rótulos de domínio.

### 5.6 O que **não** tem oráculo — dito antes de começar

1. **A tática.** O escritor grava seis destinos e o leitor original não lê
   nenhum (§1.9). v1: somente leitura, bytes intactos.
2. **Se o cartão emitido é válido para o console.** 14 dos 17 destinos caem no
   bloco 3, que o diretório declara livre, e ninguém recalcula checksum.
   Ninguém botou um PSX com um cartão assim. A MCR-TASK-13 agenda o
   experimento; **a definição de pronto da v1 não depende dele** — ela se mede
   contra o original, não contra o console.
3. **Os 17 presets de formação.** São a tabela do autor do upstream.
4. **Os rótulos das tabelas de domínio** — 32 cabelos, 7 barbas, 8 cores. Os
   *índices* são conferíveis por faixa; os *nomes* são opinião de terceiro, e
   `domains.py` os marca como tal.

---

## 6. Os bugs do original — reproduzir ou divergir

Reproduz-se o que é formato; diverge-se do que é defeito, e cada divergência
fica registrada com a medição que a justifica. O precedente escrito está no
`wte/src/we2002_mcr.pas` ("Divergencia deliberada, WTE-TASK-35").

| item | v1 | por quê | o que prova |
|---|---|---|---|
| Speed/Dribble trocados na gravação (v4.2, `Frmmcr.vb:2796-2797`) | **divergir** | é defeito de gravação: a leitura da mesma versão é direta. `Player::Encode` é normativo | §5.1 (2ª forma) + §5.4 |
| leitura do dorsal soma `+1`, gravação não | **divergir** | rompe a invariante medida em §1.5, e o sintoma é "o número mudou sozinho" | §5.4 + o negativo do `−1` |
| IDs de banco nos bytes `0..137` | **divergir, e recusar ativamente** | são o quadro `MC` e o cabeçalho da entrada 1 (§1.10) | o negativo da escrita em `0x0000` |
| off-by-one do campo de URL em `130880` | **não portar** | não é campo do save, é anotação privada da ferramenta | — |
| `bufersizenum = 5` com passo de 4 | **divergir** | erro aritmético: lê 1 byte além do grupo | §5.3 |
| nome tratado como ASCII | **divergir** (cp932) | §1.6 | `text.py --check`: os 23 re-codificam nos mesmos bytes |
| o carimbo `+0x16 := 0xff` (o goleiro da Eire) | **reproduzir** | não é bug, é a correção da v0.98 do Obocaman | `golden-13-roundtrip` já depende dele |
| tabela de cobradores não-crescente | **reproduzir** | é o formato | §5.3 |
| não tocar o diretório nem recalcular checksum | **reproduzir, por ora** | é o comportamento medido que produz round-trip de zero divergência; divergir sem oráculo troca um desconhecido por outro | §5.1; reavaliar na MCR-TASK-13 |
| o `+50` duplicado da tática em `0x6102` | **reproduzir** (passar intacto) | o cartão guarda o byte duas vezes e ninguém lê a segunda de volta | §5.1 |

---

## 7. Fases e tasks

| Fase | O que fecha |
|---|---|
| 0 | o ciclo em subpasta, a base legal, a fixture e o ambiente Qt |
| 1 | o núcleo: contêiner, endereços, os quatro codecs, modelo e round-trip |
| 2 | o gate — `selftest`, CLI e os três alvos de `ctest` |
| 3 | a UI Qt (leitura e gravação) e o oráculo do Obocaman |
| 4 | a verificação final contra a definição de pronto |

O quadro com as 14 tasks, dependências e datas está em
[/docs/tasks/port-mcr/progresso.md](/docs/tasks/port-mcr/progresso.md).

**Ordem, e o que não pode ser pulado:**

- **05 antes de 06/07/08** — decodificador escrito contra endereço não
  conferido produz campo plausível e errado, e o sintoma só aparece no jogo.
- **09 antes de 11** — UI sobre modelo que ainda não fecha round-trip
  transforma bug de codec em bug de widget.
- **10 antes de 12** — gravação pela UI sem gate é o que perde cartão do
  usuário.
- **13 antes de 12 fechar** — se o `0x6500` for capitão, a tela tem um campo
  "capitão"; se for o sexto cobrador, tem seis cobradores.

---

## 8. Armadilhas conhecidas

1. **O Python duplo** (§4.1) — o apt "instala" Qt e o import falha, em verde.
2. **O `mcr_selftest` passar a exigir Qt** por um import indevido em `ui/`. As
   duas guardas da Regra 3 existem para isso.
3. **O nome cp932 virar mojibake** sem ninguém olhar (§1.6). `text.py --check`
   re-codifica os 23 e exige bytes idênticos.
4. **Herdar o Speed/Dribble trocado** por transcrever a v4.2 sem conferir.
5. **Escrever no cabeçalho do cartão** por transcrever o `GrabarData` do
   upstream. A recusa abaixo de `0x800` é caso de teste, não comentário.
6. **Casar tabela por índice** — a lição da §6.1 do
   [/docs/PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) vale aqui: os 20 rótulos de
   papel, os 32 cabelos e os 17 presets são listas de comprimentos diferentes.
7. **`Frmmcr.vb` tem 326 KB na árvore `lite/`**, e quase tudo é WinForms. Só
   `attributes`, `numbers`, `formation` e `domains` saem de lá; o resto não se
   porta.
8. **Cópia, sempre.** O cartão do usuário é estado dele. A fixture é
   `work/entrada.mcr`; gravação vai para cópia em `work/` ou no scratchpad.

---

## 9. Entregáveis

- `tools/mcr/` — o núcleo (12 módulos), o CLI e o `selftest`;
- `tools/mcr/ui/` — a UI PySide6;
- três alvos em `tests/CMakeLists.txt` e dois no `Makefile` (`mcr`, `mcr-98`);
- este plano atualizado com o que a execução medir, e
  [/docs/prompts/perfil-mcr.md](/docs/prompts/perfil-mcr.md) com o que for do
  ciclo;
- `NOTICE.md` com a linhagem do upstream e a diferença de método para o `wte/`.
