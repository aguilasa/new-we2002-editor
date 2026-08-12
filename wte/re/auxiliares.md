# `re/auxiliares.md` — as rotinas internas que o grupo de carga chama

Produto da [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md). Gerado
por [`../tools/dump_auxiliares.py`](../tools/dump_auxiliares.py) a partir
de `we-team-editor/we-team-editor.exe` e de
[`published_methods.tsv`](published_methods.tsv). **Não editar à mão:**

```sh
python3 wte/tools/dump_auxiliares.py
python3 wte/tools/dump_auxiliares.py --check   # o que `make -C wte check` roda
```

A tabela está em [`auxiliares.tsv`](auxiliares.tsv); este arquivo é a
leitura dela. **Todo número daqui saiu do script.**

## O problema que a medição resolve

Três specs do grupo de carga pararam em `aberto` pela mesma razão: o
handler chama rotinas que não são handler publicado, e sem saber o que
elas fazem não dá para escrever o corpo. A tabela de auxiliares da
[`spec/MainForm.lista_equiposChange.md`](spec/MainForm.lista_equiposChange.md)
foi escrita à mão e listava **cinco** endereços.

Medido, esse handler chama **13** rotinas internas —
9 delas já com papel lido, 4 ainda
sem:

- `0x004050d0` — carrega os campos de nome do time selecionado para as globais
- `0x00405270` — desenha a bandeira 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md)
- `0x004056c8` — desenha o uniforme 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md)
- `0x0040b0b4` — preenche as 23 legendas `dorsalN` com os numeros de camisa
- `0x0040b188` — marca a camisa N: apaga a marcada, acha a nova por `FindComponent`, destaca
- `0x0040b2d8` — preenche `lista_jugadores_1` com os 23 nomes, filtrados
- `0x0040cbc8` — percorre a tabela de offsets em `.data`, seis colunas por linha
- `0x00415718` — *sem papel lido*
- `0x00417810` — `fseek` da RTL
- `0x00418f70` — `fgetc` da RTL
- `0x00421370` — *sem papel lido*
- `0x004213b4` — *sem papel lido*
- `0x00421870` — *sem papel lido*

A comparação não é 5 contra 13 de igual para igual: parte das que
faltavam é rotina de biblioteca que a tabela à mão descartaria de
propósito. Mas **duas das que faltavam carregam dado do jogo** —
`0x004050d0` e `0x0040cbc8` —, e essas não estavam sendo descartadas: não
estavam sendo vistas. Tabela de auxiliar escrita à mão erra da forma que
não aparece: o que falta na lista simplesmente não é procurado, e a spec
fica parecendo completa.

## O que entrou na conta

Os 28 handlers do grupo `carga` chamam **47** rotinas
internas diretamente. O script desce **um** nível a partir delas — o
objetivo é nomear a rotina que a spec cita, não fechar o grafo de
chamada do binário —, e com isso a tabela tem 91 linhas.

Nem todo `call` do corpo entra: importada sai pelo `jmp DWORD PTR
ds:<IAT>`, handler publicado sai pelo
[`published_methods.tsv`](published_methods.tsv). Sobra a rotina interna,
que é o que interessa.

**11 entram com tamanho `?`.** O fim de uma rotina
sai do decodificador x86, não de subtração de endereços; quando ele
não consegue determinar onde o corpo acaba, a linha diz isso em vez
de sumir da tabela. Nenhuma delas tem papel lido.

## As rotinas

| Endereço | Nível | Bytes | Chamada por | Papel |
|---|---:|---:|---|---|
| `0x00403278` | 2 | 270 | `0x00403f00`, `0x0040756c`, `0x0040a0b4` | — |
| `0x00403388` | 2 | 50 | `0x004033bc`, `0x004042d4`, `0x0040b2d8` | pula a fronteira de setor: se `ftell % 2352 == 2072`, avanca 304 |
| `0x004033bc` | 1 | 67 | `MainForm.mostrar_estrategiaClick`, `0x00403f00`, `0x004046e8`, `0x004050d0`, `0x00405468` | le `ecx` bytes da imagem a partir do offset em `edx` para o destino empilhado |
| `0x00403400` | 2 | 72 | `0x00404820` | grava `ecx` bytes na imagem a partir do offset em `edx` — a irma escritora da `0x004033bc` |
| `0x00403598` | 2 | 1201 | `0x0040bb84`, `0x0040cbc8` | — |
| `0x00403c0c` | 2 | 447 | `0x0040bb84`, `0x0040cbc8` | — |
| `0x00403f00` | 1 | 328 | `MainForm.mostrar_jugadorClick`, `0x00404820`, `0x0040b0b4` | le o numero de camisa e devolve **base um** (`inc eax` nos tres ramos: time 48, clube de ML, selecao) |
| `0x00404048` | 2 | 365 | `0x00404820` | grava o numero de camisa, desfazendo a base um (`add al,0xff`) |
| `0x0040423c` | 2 | 64 | `0x004042d4`, `0x00404820` | — |
| `0x0040427c` | 2 | 87 | `0x00404820` | — |
| `0x004042d4` | 1 | 159 | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow` | — |
| `0x00404374` | 2 | 881 | `0x004046e8`, `0x00404820`, `0x0040b2d8` | prepara um buffer de jogador: identidade (`+0x16`, `+0x17`), tipo (`+0x19`) e as tres colunas de offset na imagem. A identidade e `(time, slot)` para selecao e o PAR DE VINCULO lido do arquivo para clube de ML; a coluna `+0x28` sai ZERO para os times 54 e 55, que e o mesmo furo que o `we2002_database.pas` pula ao carregar `cost` (jogadores 1704..1749) |
| `0x004046e8` | 1 | 164 | `MainForm.mostrar_jugadorClick` | carrega um jogador para o buffer de 44 bytes em `0x004335ec` — 10 B de nome, 12 B de atributos, e 1 B que so existe se a terceira coluna da tabela de offsets nao for zero (senao vai 50) |
| `0x00404820` | 1 | 1459 | `MainForm.mostrar_jugadorClick` | **grava** um jogador do buffer no destino — 10 B de nome, 12 B de atributos, e o byte condicional; recusa com `-2` se a identidade (`+0x16`, `+0x17`) do buffer bater com a do destino |
| `0x00404dd4` | 2 | 154 | `0x00405270`, `0x00405468`, `0x004056c8` | — |
| `0x00404e70` | 2 | 285 | `0x004050d0` | — |
| `0x00404f90` | 2 | 318 | `0x004050d0` | — |
| `0x004050d0` | 1 | 209 | `MainForm.lista_equiposChange` | carrega os campos de nome do time selecionado para as globais |
| `0x00405270` | 1 | 502 | `MainForm.lista_equiposChange` | desenha a bandeira 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md) |
| `0x00405468` | 1 | 606 | `MainForm.lista_equipos_2Change` | — |
| `0x004056c8` | 1 | 1034 | `MainForm.lista_equiposChange` | desenha o uniforme 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md) |
| `0x00406fb4` | 2 | 44 | `0x0040756c` | — |
| `0x00406fe0` | 2 | 301 | `0x0040756c` | — |
| `0x00407110` | 2 | 552 | `0x0040756c` | — |
| `0x00407338` | 2 | 561 | `0x0040756c` | — |
| `0x0040756c` | 1 | 1275 | `MainForm.mostrar_jugadorClick` | — |
| `0x004097d4` | 1 | 474 | `estrategia.lista_formacionesClick`, `0x0040a0b4` | — |
| `0x004099bc` | 1 | 227 | `estrategia.lista_formacionesClick`, `0x0040a0b4` | — |
| `0x0040a0b4` | 1 | 1443 | `MainForm.mostrar_estrategiaClick` | — |
| `0x0040b0b4` | 1 | 210 | `MainForm.lista_equiposChange` | preenche as 23 legendas `dorsalN` com os numeros de camisa |
| `0x0040b188` | 1 | 335 | `MainForm.lista_equiposChange`, `MainForm.lista_jugadores_1Change` | marca a camisa N: apaga a marcada, acha a nova por `FindComponent`, destaca |
| `0x0040b2d8` | 1 | 1548 | `MainForm.lista_equiposChange`, `MainForm.lista_equipos_2Change`, `MainForm.mostrar_jugadorClick` | preenche `lista_jugadores_1` com os 23 nomes, filtrados |
| `0x0040b9ec` | 1 | 407 | `MainForm.boton_mcrClick` | — |
| `0x0040bb84` | 1 | 475 | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow` | — |
| `0x0040cbc8` | 1 | 419 | `MainForm.lista_equiposChange` | percorre a tabela de offsets em `.data`, seis colunas por linha |
| `0x00414570` | 2 | 15 | `0x004213b4` | — |
| `0x0041482c` | 1 | 36 | `estrategia.ComboBoxDrawItem`, `0x0040b2d8` | — |
| `0x00414850` | 2 | 315 | `0x0041482c` | — |
| `0x0041498c` | 2 | 443 | `0x0040b2d8` | — |
| `0x00414d98` | 2 | 16 | `0x00417170` | — |
| `0x004153c4` | 2 | 138 | `0x004042d4` | — |
| `0x00415718` | 1 | ? | `jugador.FormCreate`, `estrategia.FormCreate`, `estrategia.ComboBoxDrawItem`, `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.lista_equiposChange`, `MainForm.boton_dialogo_texClick`, `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick`, `MainForm.FormCreate`, `MainForm.FormShow`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x0040756c`, `0x004097d4`, `0x004099bc`, `0x0040a0b4`, `0x0040b0b4`, `0x0040b188`, `0x0040b2d8`, `0x0040bb84`, `0x0040cbc8` | — |
| `0x00416660` | 2 | 117 | `0x00417170` | — |
| `0x004167b8` | 2 | 132 | `0x00417810` | — |
| `0x00416fc8` | 2 | 29 | `0x00404820` | — |
| `0x00417170` | 1 | 159 | `MainForm.boton_dialogo_texClick`, `0x00405270`, `0x00405468`, `0x004056c8` | — |
| `0x00417210` | 1 | 5 | `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.FormShow` | — |
| `0x00417218` | 2 | 143 | `0x00417170`, `0x00417810` | — |
| `0x004172a8` | 1 | 73 | `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.FormShow` | — |
| `0x00417458` | 2 | 169 | `0x00417530` | — |
| `0x00417504` | 2 | 42 | `0x00417530` | — |
| `0x00417530` | 1 | 51 | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow`, `0x00405270`, `0x00405468`, `0x004056c8` | — |
| `0x00417564` | 2 | 217 | `0x00417910` | — |
| `0x00417640` | 2 | 303 | `0x00417770` | — |
| `0x00417770` | 1 | 67 | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow` | — |
| `0x004177b4` | 2 | 90 | `0x00417810` | — |
| `0x00417810` | 1 | 115 | `MainForm.boton_dialogo_weClick`, `MainForm.lista_equiposChange`, `MainForm.FormShow`, `0x004033bc`, `0x00403f00`, `0x004042d4`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x0040b2d8`, `0x0040b9ec` | `fseek` da RTL |
| `0x00417910` | 1 | 69 | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow` | — |
| `0x0041799c` | 2 | 148 | `0x004172a8` | — |
| `0x00417a30` | 2 | 69 | `0x004172a8` | — |
| `0x00417d50` | 2 | 76 | `0x004172a8` | — |
| `0x00417dbc` | 2 | 18 | `0x004172a8` | — |
| `0x00417e88` | 2 | 230 | `0x00418f70` | — |
| `0x00417f70` | 2 | 272 | `0x00418f98` | — |
| `0x00418080` | 2 | 88 | `0x00417170` | — |
| `0x0041811c` | 1 | 5 | `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.FormShow` | — |
| `0x004183c0` | 2 | 13 | `0x00417530` | — |
| `0x004183d0` | 2 | 13 | `0x00417530` | — |
| `0x004183e0` | 2 | 164 | `0x00417170`, `0x00417770`, `0x00417810`, `0x00417910`, `0x00418f70`, `0x00418f98` | — |
| `0x004184a8` | 2 | 84 | `0x00417170`, `0x00417770`, `0x00417810`, `0x00417910`, `0x00418f70`, `0x00418f98` | — |
| `0x004184fc` | 2 | 26 | `0x00417170` | — |
| `0x00418f70` | 1 | 37 | `MainForm.boton_dialogo_weClick`, `MainForm.lista_equiposChange`, `MainForm.FormShow`, `0x004033bc`, `0x00403f00`, `0x004042d4`, `0x0040b2d8`, `0x0040b9ec` | `fgetc` da RTL |
| `0x00418f98` | 1 | 43 | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow`, `0x00405270`, `0x00405468`, `0x004056c8` | — |
| `0x0041978c` | 1 | 35 | `MainForm.mostrar_jugadorClick`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x004097d4`, `0x0040b2d8`, `0x0040bb84` | — |
| `0x0041be40` | 2 | 106 | `0x0041beac` | — |
| `0x0041beac` | 1 | 21 | `MainForm.boton_dialogo_weClick` | — |
| `0x0042120c` | 1 | ? | `estrategia.ComboBoxDrawItem`, `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick`, `MainForm.FormCreate`, `MainForm.FormShow`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x0040756c`, `0x0040b2d8`, `0x0040bb84` | — |
| `0x004212dc` | 2 | ? | `0x0040b2d8` | — |
| `0x00421328` | 1 | ? | `MainForm.boton_dialogo_weClick`, `MainForm.mostrar_jugadorClick`, `MainForm.FormShow` | — |
| `0x00421370` | 1 | ? | `jugador.FormCreate`, `estrategia.FormCreate`, `MainForm.lista_equiposChange`, `0x0040756c`, `0x004099bc`, `0x0040a0b4`, `0x0040b0b4`, `0x0040b188`, `0x0040b2d8` | — |
| `0x004213b4` | 1 | 47 | `jugador.FormCreate`, `estrategia.FormCreate`, `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.lista_equiposChange`, `MainForm.boton_dialogo_texClick`, `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick`, `MainForm.FormCreate`, `MainForm.FormShow`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x0040756c`, `0x004097d4`, `0x004099bc`, `0x0040a0b4`, `0x0040b0b4`, `0x0040b188`, `0x0040b2d8`, `0x0040bb84`, `0x0040cbc8` | — |
| `0x004213e4` | 1 | 20 | `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick`, `MainForm.FormCreate`, `MainForm.FormShow`, `0x004056c8`, `0x0040b2d8`, `0x0040bb84` | — |
| `0x004213f8` | 1 | ? | `MainForm.boton_dialogo_weClick`, `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick`, `MainForm.FormCreate`, `MainForm.FormShow`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x0040b2d8`, `0x0040bb84` | — |
| `0x00421484` | 1 | 22 | `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick` | — |
| `0x00421580` | 1 | 40 | `MainForm.mostrar_jugadorClick`, `0x0040b2d8`, `0x0040bb84` | — |
| `0x004215a8` | 1 | 38 | `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.FormShow` | — |
| `0x004215f0` | 1 | ? | `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick` | — |
| `0x00421678` | 1 | ? | `MainForm.boton_dialogo_weClick`, `MainForm.mostrar_jugadorClick`, `MainForm.mostrar_estrategiaClick`, `MainForm.FormShow`, `0x0040a0b4` | — |
| `0x004217ac` | 1 | ? | `MainForm.boton_dialogo_weClick`, `MainForm.boton_mcrClick`, `MainForm.boton_dialogo_texClick`, `MainForm.FormShow` | — |
| `0x00421820` | 1 | ? | `MainForm.boton_dialogo_weClick`, `MainForm.FormShow` | — |
| `0x00421870` | 1 | ? | `jugador.FormCreate`, `estrategia.FormCreate`, `MainForm.lista_equiposChange`, `MainForm.mostrar_jugadorClick`, `0x00404820`, `0x0040756c`, `0x004097d4`, `0x004099bc`, `0x0040a0b4`, `0x0040b0b4`, `0x0040b188` | — |

## A fronteira de setor, e por que ela fecha um círculo

`0x00403388` não recebe offset nenhum. Ela pergunta ao `ftell`
em que ponto do setor o arquivo está e, se está no fim dos dados, avança:

```text
se ftell(imagem) mod 2352 = 2072:
    avanca 304 bytes e devolve verdadeiro
senao: devolve falso
```

2352 é o setor MODE2/2352 inteiro; 2072 é
24 de cabeçalho mais 2048 de dados; 304 é os 280 de EDC/ECC
mais os 24 do cabeçalho do setor seguinte. É a **mesma geometria** que o
`we2002_core` deste repositório assa nas constantes `OFS_*` — a diferença
é que o original a calcula em tempo de execução e nós a temos pré-somada.

As três constantes saem decodificadas do corpo da própria rotina, e o
script aborta se deixarem de bater — inclusive na identidade
`2072 + 304 = 2352 + 24`.

## A tabela de offsets, vista do outro lado

`0x0040cbc8` carrega `0x004231a0` e percorre a tabela
em linhas de 0x18 bytes, 6 colunas de quatro —
pulando a coluna que estiver zerada.

Esse endereço é o mesmo que a
[WTE-TASK-06](../../docs/tasks/06-mapa-de-offsets.md) registrou como
primeiro slot em [`offsets.tsv`](offsets.tsv), medido por outro caminho:
lá pela varredura de constantes que batem com os nossos `OFS_*`, aqui
pelo código que as consome. O script lê a base do corpo da rotina e
**aborta se as duas medições discordarem** — a tabela deixaria de ter um
dono só.

## O filtro de nome não traduz — ele filtra

`0x0040b2d8` lê o nome byte a byte e indexa duas tabelas em
`.data` pelo próprio byte. A leitura barata seria "são tabelas de
tradução, como o `KanjiToAscii` do `we2002_core`". Medido, as duas são
**identidade**:

| Tabela | Base | Faixa | Conteúdo |
|---|---|---|---|
| maiusculas | `0x00423129` | `0x41`…`0x5a` | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| minusculas | `0x00423124` | `0x61`…`0x7a` | `abcdefghijklmnopqrstuvwxyz` |

Ou seja, a rotina copia letra, dígito, `.` e espaço como estão, troca
**qualquer byte acima de `z` por `?`** e descarta o resto. Isso é uma
divergência de comportamento contra o `we2002_core`, que para byte
desconhecido devolve espaço; ela vale para o que aparece na tela e não
para o que se grava. A conferência aborta se as tabelas deixarem de ser
identidade, porque nesse dia a palavra "filtro" fica errada.

## As lidas, uma a uma

O inventário é piso, não teto: literais são as cadeias ASCII de três
caracteres ou mais apontadas por operando imediato, e globais são os
endereços da `.data` alcançados por `mov eax,moffs32` ou
`mov <reg>,[disp32]`.

### `0x00403388` — 50 bytes

- **Papel:** pula a fronteira de setor: se `ftell % 2352 == 2072`, avanca 304
- **Chamada por:** `0x004033bc`, `0x004042d4`, `0x0040b2d8`
- **Chama internas:** nenhuma
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x004033bc` — 67 bytes

- **Papel:** le `ecx` bytes da imagem a partir do offset em `edx` para o destino empilhado
- **Chamada por:** `MainForm.mostrar_estrategiaClick`, `0x00403f00`, `0x004046e8`, `0x004050d0`, `0x00405468`
- **Chama internas:** `0x00417810`, `0x00418f70`, `0x00403388`
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x00403400` — 72 bytes

- **Papel:** grava `ecx` bytes na imagem a partir do offset em `edx` — a irma escritora da `0x004033bc`
- **Chamada por:** `0x00404820`
- **Chama internas:** nenhuma
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x00403f00` — 328 bytes

- **Papel:** le o numero de camisa e devolve **base um** (`inc eax` nos tres ramos: time 48, clube de ML, selecao)
- **Chamada por:** `MainForm.mostrar_jugadorClick`, `0x00404820`, `0x0040b0b4`
- **Chama internas:** `0x004033bc`, `0x00403278`, `0x00417810`, `0x00418f70`
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x00404048` — 365 bytes

- **Papel:** grava o numero de camisa, desfazendo a base um (`add al,0xff`)
- **Chamada por:** `0x00404820`
- **Chama internas:** nenhuma
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x00404374` — 881 bytes

- **Papel:** prepara um buffer de jogador: identidade (`+0x16`, `+0x17`), tipo (`+0x19`) e as tres colunas de offset na imagem. A identidade e `(time, slot)` para selecao e o PAR DE VINCULO lido do arquivo para clube de ML; a coluna `+0x28` sai ZERO para os times 54 e 55, que e o mesmo furo que o `we2002_database.pas` pula ao carregar `cost` (jogadores 1704..1749)
- **Chamada por:** `0x004046e8`, `0x00404820`, `0x0040b2d8`
- **Chama internas:** nenhuma
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x004046e8` — 164 bytes

- **Papel:** carrega um jogador para o buffer de 44 bytes em `0x004335ec` — 10 B de nome, 12 B de atributos, e 1 B que so existe se a terceira coluna da tabela de offsets nao for zero (senao vai 50)
- **Chamada por:** `MainForm.mostrar_jugadorClick`
- **Chama internas:** `0x00404374`, `0x004033bc`
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x00404820` — 1459 bytes

- **Papel:** **grava** um jogador do buffer no destino — 10 B de nome, 12 B de atributos, e o byte condicional; recusa com `-2` se a identidade (`+0x16`, `+0x17`) do buffer bater com a do destino
- **Chamada por:** `MainForm.mostrar_jugadorClick`
- **Chama internas:** `0x00415718`, `0x00404374`, `0x0040423c`, `0x00403f00`, `0x00403400`, `0x00417810`, `0x00416fc8`, `0x00404048`, `0x0040427c`, `0x0041978c`, `0x00421870`, `0x0042120c`, `0x004213f8`, `0x004213b4`
- **Importados:** `@Sysutils@CurrToStr$qqr15System@Currency`, `@Controls@TControl@SetText$qqrx17System@AnsiString`
- **Literais:** `in another `, ` different place(s) in the game`
- **Globais da `.data`:** `0x00432e58`, `0x00433db8` (`_ficha_info4`)

### `0x004050d0` — 209 bytes

- **Papel:** carrega os campos de nome do time selecionado para as globais
- **Chamada por:** `MainForm.lista_equiposChange`
- **Chama internas:** `0x00404e70`, `0x004033bc`, `0x00404f90`
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** `0x004331dc`, `0x004331e8`, `0x004331f4`, `0x004331f8`, `0x0043321c`, `0x00433220`

### `0x00405270` — 502 bytes

- **Papel:** desenha a bandeira 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md)
- **Chamada por:** `MainForm.lista_equiposChange`
- **Chama internas:** `0x00415718`, `0x0041978c`, `0x0042120c`, `0x004213f8`, `0x004213b4`, `0x00417530`, `0x00417810`, `0x00404dd4`, `0x00418f98`, `0x00417170`
- **Importados:** `@Sysutils@CurrToStr$qqr15System@Currency`, `@Graphics@TPicture@LoadFromFile$qqrx17System@AnsiString`
- **Literais:** `\bandera`, `.bmp`
- **Globais da `.data`:** `0x00432ebc`, `0x00432ec8`

### `0x004056c8` — 1034 bytes

- **Papel:** desenha o uniforme 2D — [WTE-TASK-32](../../docs/tasks/32-camisa-e-bandeira-2d.md)
- **Chamada por:** `MainForm.lista_equiposChange`
- **Chama internas:** `0x00415718`, `0x0041978c`, `0x0042120c`, `0x004213f8`, `0x004213e4`, `0x004213b4`, `0x00417530`, `0x00417810`, `0x00404dd4`, `0x00418f98`, `0x00417170`
- **Importados:** `@Sysutils@CurrToStr$qqr15System@Currency`, `@Graphics@TPicture@LoadFromFile$qqrx17System@AnsiString`
- **Literais:** `\camiseta`, `.bmp`, `\pantalon`
- **Globais da `.data`:** `0x00432ec0`, `0x00432ec4`

### `0x0040b0b4` — 210 bytes

- **Papel:** preenche as 23 legendas `dorsalN` com os numeros de camisa
- **Chamada por:** `MainForm.lista_equiposChange`
- **Chama internas:** `0x00415718`, `0x00421370`, `0x00421870`, `0x00403f00`, `0x004213b4`
- **Importados:** `@Classes@TComponent@FindComponent$qqrx17System@AnsiString`, `@Controls@TControl@SetText$qqrx17System@AnsiString`
- **Literais:** `dorsal`
- **Globais da `.data`:** `0x00432e58`, `0x00434360` (`_MainForm`)

### `0x0040b188` — 335 bytes

- **Papel:** marca a camisa N: apaga a marcada, acha a nova por `FindComponent`, destaca
- **Chamada por:** `MainForm.lista_equiposChange`, `MainForm.lista_jugadores_1Change`
- **Chama internas:** `0x00415718`, `0x00421370`, `0x00421870`, `0x004213b4`
- **Importados:** `@Graphics@TFont@SetSize$qqri`, `@Controls@TControl@SetLeft$qqri`, `@Controls@TControl@SetWidth$qqri`, `@Controls@TControl@SetTop$qqri`, `@Controls@TControl@SetHeight$qqri`, `@Controls@TControl@SetColor$qqr15Graphics@TColor`, `@Graphics@TFont@SetColor$qqr15Graphics@TColor`, `@Controls@TControl@SendToBack$qqrv`, `@Classes@TComponent@FindComponent$qqrx17System@AnsiString`, `@Controls@TControl@BringToFront$qqrv`
- **Literais:** `dorsal`
- **Globais da `.data`:** `0x00434360` (`_MainForm`)

### `0x0040b2d8` — 1548 bytes

- **Papel:** preenche `lista_jugadores_1` com os 23 nomes, filtrados
- **Chamada por:** `MainForm.lista_equiposChange`, `MainForm.lista_equipos_2Change`, `MainForm.mostrar_jugadorClick`
- **Chama internas:** `0x00415718`, `0x0041498c`, `0x00404374`, `0x00417810`, `0x0042120c`, `0x004213e4`, `0x004213b4`, `0x00403388`, `0x00418f70`, `0x004213f8`, `0x00421370`, `0x004212dc`, `0x0041978c`, `0x00421580`, `0x0041482c`
- **Importados:** `@Sysutils@CurrToStr$qqr15System@Currency`
- **Literais:** ` (L)`
- **Globais da `.data`:** `0x00432e58`, `0x00433608`

### `0x0040cbc8` — 419 bytes

- **Papel:** percorre a tabela de offsets em `.data`, seis colunas por linha
- **Chamada por:** `MainForm.lista_equiposChange`
- **Chama internas:** `0x00415718`, `0x00403c0c`, `0x00403598`, `0x004213b4`
- **Importados:** `@Stdctrls@TCustomEdit@SetMaxLength$qqri`, `@Controls@TControl@SetText$qqrx17System@AnsiString`
- **Literais:** nenhum
- **Globais da `.data`:** `0x00432e58`, `0x00433a10`, `0x00433b48`, `0x00433c80`, `0x00434360` (`_MainForm`)

### `0x00417810` — 115 bytes

- **Papel:** `fseek` da RTL
- **Chamada por:** `MainForm.boton_dialogo_weClick`, `MainForm.lista_equiposChange`, `MainForm.FormShow`, `0x004033bc`, `0x00403f00`, `0x004042d4`, `0x00404820`, `0x00405270`, `0x00405468`, `0x004056c8`, `0x0040b2d8`, `0x0040b9ec`
- **Chama internas:** `0x00417218`, `0x004183e0`, `0x004177b4`, `0x004167b8`, `0x004184a8`
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma

### `0x00418f70` — 37 bytes

- **Papel:** `fgetc` da RTL
- **Chamada por:** `MainForm.boton_dialogo_weClick`, `MainForm.lista_equiposChange`, `MainForm.FormShow`, `0x004033bc`, `0x00403f00`, `0x004042d4`, `0x0040b2d8`, `0x0040b9ec`
- **Chama internas:** `0x004183e0`, `0x00417e88`, `0x004184a8`
- **Importados:** nenhum
- **Literais:** nenhum
- **Globais da `.data`:** nenhuma
