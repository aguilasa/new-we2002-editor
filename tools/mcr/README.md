# `tools/mcr/` — o editor de memory card do WE2002

Lê e grava o save do **Winning Eleven 2002 (PSX)** dentro de um cartão de
128 KiB: os 23 jogadores (atributos, nome, dorsal), a formação, os cobradores e
o capitão. Núcleo Python puro aqui; UI **PySide6** em [`ui/`](ui/).

**Três embalagens, um cartão.** `.mcr` e `.mcd` (o do emulador) são o mesmo
dump cru de 131.072 bytes; `.gme` é o do DexDrive, com 3.904 bytes de cabeçalho
na frente. Qualquer uma abre e qualquer uma grava, e `cli.py convert` vai de uma
à outra. **Quem decide o que um arquivo é são os bytes dele, nunca o nome** — um
`.gme` chamado `.mcr` abre igual. Quem decide o que se **escreve** é a extensão
do destino. Detalhe e medição em [`gme.py`](gme.py).

**O caminho curto é o [`Makefile`](Makefile) deste diretório** — `make -C
tools/mcr` lista tudo. As seções abaixo mostram o alvo e, ao lado, o comando
cru que ele roda: o alvo é o que se usa no dia a dia, e o comando cru é o que
se usa quando algo dá errado e se quer ver a ferramenta sozinha.

- **O plano** — [`docs/PLAN-MCR-PY.md`](../../docs/PLAN-MCR-PY.md), fonte de
  verdade do que este projeto é e do que ele decidiu não ser.
- **O ciclo de tasks** —
  [`docs/tasks/port-mcr/`](../../docs/tasks/port-mcr/progresso.md).
- **A linhagem** — [`NOTICE.md`](../../NOTICE.md): o ponto de partida é o
  [`zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1`](https://github.com/zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1),
  que **não tem licença**, e portar assim mesmo foi decisão do dono do
  repositório.

> **Este arquivo é português, e o código ao lado dele é inglês.** Não é
> descuido: a §3.5 do plano põe todo `tools/mcr/**.py` em en-US — identificador,
> docstring, comentário, mensagem de recusa e rótulo de tela — e deixa a
> documentação em português, como os demais `README.md` do repositório
> (`wte/tools/`, `wte/tests/roteiros/`). A varredura de idioma
> (`glossary.py`) cobre os `.py` e não alcança este arquivo, então a fronteira
> aqui é convenção e não guarda — foi exatamente assim que a
> [CORR-MCR-019](../../docs/tasks/port-mcr/CORR-MCR-019.md) aconteceu, num
> arquivo vizinho.

---

## A regra que mais custa: **cópia, sempre**

O editor grava **in-place**, como os de imagem de CD. Um `.mcr` é o save de
alguém, não um artefato reproduzível — não há de onde regerá-lo.

```sh
cp work/entrada.mcr work/minha-copia.mcr     # e edite a cópia
```

Três recusas defendem isso, e elas moram no `mcrio.py`:

| destino | o que acontece |
|---|---|
| qualquer coisa sob `roms/` | recusado, e **`--force` não levanta** |
| o cartão nomeado por `WE2002_MCR_CARD` | recusado; `--force` levanta, dizendo o que significa |
| escrita abaixo de `0x800` | recusada sempre — ali moram o quadro `MC` e a entrada 1 do diretório, e é o que o upstream sobrescreve |

> **A segunda só está armada se a variável estiver exportada.** Sem
> `WE2002_MCR_CARD` no ambiente, `cli.py set work/entrada.mcr …` **grava na
> fixture** — medido em 2026-09-08, escrevendo 1 byte em `0x0590b` por
> acidente. O digest é a régua para saber se isso aconteceu:
>
> ```sh
> sha256sum work/entrada.mcr
> # e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546
> ```
>
> Exporte a variável antes de qualquer coisa que grave, e edite cópias:
>
> ```sh
> export WE2002_MCR_CARD="$PWD/work/entrada.mcr"
> ```

---

## Ambiente

O núcleo é **Python 3 da biblioteca padrão** — não precisa instalar nada. Só a
UI precisa de PySide6, e ele vai num venv:

```sh
make mcr-venv          # cria work/venv-mcr/ e instala PySide6
```

> **O Python desta máquina é duplo.** `python3` do `PATH` é o mise 3.13.13 e
> `/usr/bin/python3` é 3.12.3. `apt install python3-pyqt6` instala para o 3.12 e
> **fica invisível** — o apt termina em verde e o `import` continua falhando.
> Por isso venv, nunca apt.
>
> E **não use `chmod -x` no python do venv** para simular "máquina sem venv":
> `work/venv-mcr/bin/python` é um symlink que termina no binário do mise, o
> `chmod` segue o link, e o interpretador da máquina inteira para de executar.
> Para simular, mova o diretório.

---

## O `Makefile` deste diretório

```sh
make -C tools/mcr              # a lista de alvos, com o cartão e a cópia em uso
cd tools/mcr && make check     # ou de dentro
```

Ele **não duplica o `Makefile` da raiz**: `ui`, `ui-98` e `venv` são
**delegados** aos alvos `mcr`, `mcr-98` e `mcr-venv` de lá, que já resolvem a
cópia do cartão e o `XAUTHORITY`. O que é próprio daqui são os alvos que a raiz
não tem.

**Leitura lê `$(CARD)`; escrita mexe em `$(COPY)`.** Os alvos que não gravam
apontam para o cartão direto; os que gravam trabalham sobre uma cópia que o
próprio `make` faz. Não há alvo que escreva no cartão que você apontou.

| alvo | o que faz | o comando cru |
|---|---|---|
| `check` | **o gate obrigatório** | `python3 selftest.py` |
| `controls` | planta cada controle e exige o vermelho | `python3 controls.py` |
| `sweeps` | idioma, endereço fora do `layout.py`, os 17 destinos e a medição da câmera | `glossary.py` · `layout.py --rule1` · `layout.py --check` · `options.py --check` |
| `card` | o gate da fixture; 77 sem cartão | `cli.py check` |
| `gate` | `ctest -R mcr` com a variável apontada | `ctest --test-dir build -R mcr -V` |
| `gates` | os cinco acima, nessa ordem | — |
| `info` | contêiner, cadeia, checksums | `cli.py info <cartão>` |
| `dump` | os 23 jogadores | `cli.py dump <cartão>` |
| `get` | um jogador ou um campo | `cli.py get <cartão> $(SLOT) $(FIELD)` |
| `formation` | X, Y, papéis, cobradores, capitão | `formation.py <cartão>` |
| `numbers` | os 23 dorsais de 5 bits | `numbers.py <cartão>` |
| `names` | os nomes byte a byte, em cp932 | `text.py <cartão>` |
| `camera` | a câmera do option file, e os dois registros | `options.py <cartão>` |
| `cameras` | o gate da medição; pula sem `$(CAMERAS)` | `options.py --check` |
| `roundtrip` | as duas formas | `cli.py roundtrip <cartão>` |
| `copy` | a cópia de trabalho | `cp --reflink=auto` |
| `set` | grava um campo **na cópia** | `cli.py set <cópia> $(SLOT) $(FIELD) $(VALUE)` |
| `probe` | muda um campo e diz que bytes se moveram | `mcrio.py <cópia> --edit-probe …` |
| `camera-set` | grava a câmera **na cópia** — dois bytes | `options.py <cópia> --set $(CAMERA)` |
| `negative` | as cinco injeções da §5.2 | `cli.py negative` |
| `venv` | cria o venv com PySide6 | `make -C ../.. mcr-venv` |
| `ui` / `ui-98` | abre a janela sobre uma cópia | `make -C ../.. mcr` / `mcr-98` |
| `ui-vazia` | abre a janela **sem cartão** — quem escolhe o arquivo é o usuário | `make -C ../.. mcr WE2002_MCR_CARD=` |
| `shot` | captura a janela em `$(OUT)` | `ui/app.py --screenshot` |
| `oracle-controle` · `oracle-capitao` · `oracle-nome` | os três roteiros do editor do Obocaman | `wte/tools/golden_run_wte.sh …` |
| `limpa` | apaga só o que estes alvos criam | — |

As variáveis: `CARD` (default `$WE2002_MCR_CARD`, e ele default
`work/entrada.mcr`), `SLOT`, `FIELD`, `VALUE`, `OUT`, `TAB`, `XVFB`, `PY`,
`CAMERA` e `CAMERAS` (default `$WE2002_MCR_CAMERA_CARDS`).

```sh
make get SLOT=3 FIELD=speed          # 15
make get SLOT=3 FIELD=               # a ficha inteira do slot 3
make set SLOT=0 FIELD=speed VALUE=17 # na cópia, e diz o byte que moveu
make camera                          # camera: 1 (normal-mid)
make camera-set CAMERA=ov-far        # na cópia, e diz os dois bytes
make shot TAB=1 OUT=/tmp/campo.png
make info CARD=/caminho/outro.mcr
```

Cartão que não existe dá a mensagem que nomeia a variável, e não um
`No such file`:

```console
$ make info CARD=/tmp/nao-existe.mcr
ERRO: cartao nao encontrado ou vazio: /tmp/nao-existe.mcr
      aponte WE2002_MCR_CARD (ou CARD=) para um .mcr de 128 KiB;
      cartao de jogo nao e versionado, como roms/.
```

---

## Linha de comando

Um comando cobre o núcleo inteiro:

```sh
python3 tools/mcr/cli.py {info,dump,get,set,roundtrip,negative,check}
```

### `info` — o contêiner, e onde o save mora

```console
$ python3 tools/mcr/cli.py info work/minha-copia.mcr
file            work/minha-copia.mcr
size            131072 bytes, magic MC
save            BISLPM-86600WEW-OPT
blocks          [1, 2]
declared size   16384 bytes
bad checksums   none
outside chain   block 3, state 0xa0, 41 non-zero bytes
```

O `outside chain` não é defeito: 14 dos 17 destinos caem no bloco 3, que o
diretório declara **livre**. É assim que o editor original faz, e o port
preserva.

### `dump` — o elenco inteiro

```console
$ python3 tools/mcr/cli.py dump work/minha-copia.mcr
slot  no  name        pos  hgt  age  spd  tec  sta  str
   0   1  P･ジｮｰﾙズ      gk  191   35   15   13   13   18
   1   5  ｺｰﾗﾝ         cb  183   31   15   14   15   16
   ...
```

O nome é **cp932** (Shift-JIS mais katakana meia-largura), não ASCII.

### `get` — um jogador, ou um campo

```console
$ python3 tools/mcr/cli.py get work/minha-copia.mcr 0        # a ficha inteira
$ python3 tools/mcr/cli.py get work/minha-copia.mcr 0 speed
15
```

### `set` — grava um campo, **na cópia**

```console
$ python3 tools/mcr/cli.py set work/minha-copia.mcr 0 speed 17
speed=17 on slot 0: 1 byte(s) moved
  0x0590b
```

Ele **grava no arquivo que você passou**, e relata exatamente que bytes se
moveram — um atributo move 1 byte, um dorsal move 2, porque o cartão guarda o
dorsal duas vezes. `field` é `name`, `number` ou qualquer um dos 29 atributos — e quem os nomeia
todos é o `get` de um slot, que imprime cada campo com o valor.

Apontar para a fixture com a variável exportada dá a recusa, não a gravação:

```console
$ python3 tools/mcr/cli.py set work/entrada.mcr 0 speed 17
error: …/work/entrada.mcr is the card named by WE2002_MCR_CARD. It is the
fixture every measurement in this cycle is anchored to, by digest, and the
wte/ cycle uses the same file. Write a copy, or pass --force if overwriting
it is really what you mean.
```

### `roundtrip` — as duas formas, que têm de dar zero

```console
$ python3 tools/mcr/cli.py roundtrip work/minha-copia.mcr
form 1: 0 byte(s) differ
form 2: 0 byte(s) differ
```

A forma 1 lê e grava — prova o I/O. A **forma 2** decodifica os 23 jogadores
para o modelo, re-codifica todos e grava — é ela que põe o encoder sob teste.

### `negative` — as injeções, e os controles plantados

```console
$ python3 tools/mcr/cli.py negative
  RED   swap speed and dribbling in the encoder  ->  form 2 of the round-trip
  ...
negative control: 5 of 5 guards fired
```

`--plant` acrescenta os controles de substituição literal do `controls.py`.

### `check` — o gate da fixture

```console
$ python3 tools/mcr/cli.py check                  # sem cartão
skipped: no memory card. Point WE2002_MCR_CARD at a .mcr, or pass one as an argument.
$ echo $?
77
```

É o alvo `mcr_card` do `ctest`, e o `77` é a convenção de *skip*.

### `convert` — entre `.gme`, `.mcr` e `.mcd`

```console
$ python3 tools/mcr/cli.py convert mcr/pro-evolution-soccer-2.29939.gme work/c.mcr
mcr/pro-evolution-soccer-2.29939.gme -> work/c.mcr (raw, 131072 bytes)
$ python3 tools/mcr/cli.py convert work/c.mcr work/c.gme
work/c.mcr -> work/c.gme (gme, 134976 bytes)
note: the card had no wrapper, so the header was synthesized. ...
```

**Os dois sentidos não são simétricos, e a nota diz por quê.** Ir de `.gme` a
cartão é um corte, e é sem perda. Voltar só devolve o **mesmo arquivo** se o
cabeçalho original vier junto — e ele viaja com o *cartão em memória*, não com o
`.mcr` no disco, que não tem onde guardá-lo. Medido sobre os oito `.gme` de
[`mcr/`](../../mcr/README.md): **8 de 8** idênticos quando o cabeçalho viaja,
**2 de 8** quando ele é sintetizado — os dois cujos bytes depois do espelho do
diretório calham de ser todos `0xFF`. Os outros três de cabeçalho zerado nunca
saem de uma síntese, que assina o que faz.

O `convert` **não** exige que o cartão tenha um save do WE2002: **cinco** dos
oito `.gme` versionados são de PES2 e um não tem option file, então o `info`
recusa **seis** e aceita dois. Contêiner não é save, e quem responde a segunda
pergunta é o `info`. Quem é de qual jogo está na tabela de
[`mcr/README.md`](../../mcr/README.md), que é a fonte desta conta.

## A câmera — `options.py`

**Outro save, no mesmo cartão.** O `BISLPM-*WEW-OPT` guarda dois registros, e o
editor de time só conhece o segundo. O primeiro tem 134 bytes e começa com a
**câmera**: o byte que escolhe uma das nove vistas do jogo.

```console
$ python3 tools/mcr/options.py work/limpo.mcr
camera: 1 (normal-mid)
  at 0x02104, save data at 0x02100
  record 0:    134 bytes at 0x02103, checksum 0xd9 ok
  record 1:  12420 bytes at 0x02203, checksum 0x8b ok

$ python3 tools/mcr/options.py work/limpo.mcr --set ov-far
camera 1 (normal-mid) -> 8 (ov-far)
  0x02104
  0x02102
written: work/limpo-edited.mcr
```

Os nove nomes são `normal-near`, `normal-mid`, `normal-far`, `wide`, `tv`,
`zoom`, `ov-near`, `ov-mid`, `ov-far` — índices 0 a 8, e `--set` aceita nome ou
número.

**São sempre dois bytes, e o segundo é o que se esquece.** Cada registro carrega
o próprio checksum na frente: a soma do payload, mod 256. Gravar só a câmera
deixa um cartão que o console **carrega** e o jogo **descarta** — na tela isso
parece "a edição não pegou", e é na verdade um save que o jogo jogou fora. O
módulo refaz o checksum, e **recusa** gravar sobre um registro que já chegou com
o checksum errado, em vez de corrigi-lo e esconder o que o estragou.

**Nenhum endereço aqui é absoluto**, e essa é a diferença para os 17 destinos do
editor de time. O bloco vem do diretório, o tamanho do quadro do contêiner e o
número de quadros de ícone do cabeçalho do próprio save — só então se chega ao
primeiro byte de dados. Escrito como constante, `0x02104` estaria certo nos
cartões desta máquina e errado em qualquer um cujo save more noutro bloco, que é
a armadilha 6 do perfil. Os offsets ficam no [`layout.py`](layout.py), na seção
dos registros de opção, e são **relativos ao save**.

### De onde vem a medição, e como ela se repete

Quatro option files salvos numa sessão do jogo, sem mexer em nada além da
câmera. **O jogo escreveu, nós lemos.** Só duas coisas se moveram — o valor e o
checksum:

| câmera | byte `0x2104` | checksum `0x2102` |
|---|---|---|
| `normal-near` | `00` | `d8` |
| `normal-mid` (o limpo) | `01` | `d9` |
| `normal-far` | `02` | `da` |
| `ov-far` | `08` | `e0` |

Gravar esses dois bytes no cartão limpo reproduz cada um dos outros três **byte
a byte**. O `--check` é essa medição, rodada de novo:

```console
$ WE2002_MCR_CAMERA_CARDS=~/cards python3 tools/mcr/options.py --check
  ok    camera-normal-near: two bytes reproduce the card the game saved (12 in the title padding)
  ok    camera-normal-far: two bytes reproduce the card the game saved (11 in the title padding)
  ok    camera-ov-far: two bytes reproduce the card the game saved (12 in the title padding)
options.py --check: 4 cards
```

**O "title padding" não é dado.** São os bytes depois do fim do título, dentro
do cabeçalho do save PSX, onde o jogo deixa o que estava na memória — eles
diferem entre dois saves da mesma sessão. O `--check` **conta** e os nomeia em
vez de os varrer para debaixo do tapete: diferença que passe dessa faixa é
diferença de verdade, e vira falha.

**Cartão de jogo não se versiona**, mesma regra de `roms/`, então sem
`WE2002_MCR_CAMERA_CARDS` o `--check` **pula e diz que pulou**. Os quatro nomes
de arquivo que ele procura estão no `CAMERA_FIXTURES` do módulo.

### O outro sentido, que é o que importa

As quatro linhas acima são **o jogo escrevendo e nós lendo**. Elas provam o
decodificador e não provam a gravação: cartão que o jogo salvou é cartão que o
jogo **já aceitou**, então relê-lo não diz nada sobre o checksum que **nós**
calculamos ser o mesmo que ele valida.

Em 2026-09-11 o sentido inverso foi fechado: este módulo gravou a câmera **5**
por cima do cartão do DuckStation — dois bytes, saindo de `ov-far` — e o jogo
subiu com **Zoom** selecionado na tela de opções. É a única evidência que diz que
a gravação funciona, e ela não vinha dos quatro cartões.

Ela também **fixa a ordem por dentro**: as duas pontas já estavam presas, e o `5`
cair exatamente no quinto nome não deixa espaço para a lista estar deslocada.
Sobram quatro sem confirmação direta — 3, 4, 6 e 7 —, e elas estão cercadas dos
dois lados.

### Os módulos, um a um

Cada módulo do núcleo roda sozinho sobre um cartão, e é onde está o detalhe que
o `cli.py` resume:

```sh
python3 tools/mcr/card.py      <cartão> --blocks     # ou --json
python3 tools/mcr/gme.py       <arquivo>            # que embalagem é esta
python3 tools/mcr/gme.py       --check              # os oito de mcr/, round-trip
python3 tools/mcr/numbers.py   <cartão>              # os 23 dorsais de 5 bits
python3 tools/mcr/text.py      <cartão>              # os nomes, byte a byte
python3 tools/mcr/formation.py <cartão>              # X, Y, papéis, cobradores, capitão
python3 tools/mcr/model.py     <cartão>              # a visão decodificada
python3 tools/mcr/layout.py    --check               # os 17 destinos, nos dois sentidos
python3 tools/mcr/options.py   <cartão>              # a câmera, e os dois registros
python3 tools/mcr/mcrio.py     <cópia> --edit-probe 0 number 30
```

O `--edit-probe` é a medida ponta a ponta: muda um campo e diz que bytes se
moveram.

```console
$ python3 tools/mcr/mcrio.py work/minha-copia.mcr --edit-probe 0 number 30
number=30 on slot 0: 2 byte(s) moved
  0x05404
  0x05907
```

---

## A interface

**Toda execução com GUI acontece no `DISPLAY=:98`** — o `:1` é a sessão real do
usuário. O servidor sobe sem `-auth`, então `XAUTHORITY` vazio é o certo:

```sh
Xvfb :98 -screen 0 1280x1024x24 -nolisten tcp &
```

O jeito curto, que cuida da cópia e do display sozinho — daqui ou da raiz, dá
no mesmo, porque um delega ao outro:

```sh
make -C tools/mcr ui        # ou, na raiz:  make mcr
make -C tools/mcr ui-98     # ou, na raiz:  make mcr-98
make -C tools/mcr shot TAB=1 OUT=/tmp/campo.png
```

À mão, com o python do venv:

```sh
export DISPLAY=:98
work/venv-mcr/bin/python tools/mcr/ui/app.py work/minha-copia.mcr
work/venv-mcr/bin/python tools/mcr/ui/app.py            # sem argumento: janela vazia
```

### Escolher o cartão pela janela

**A janela sobe com ou sem cartão**, e escolher um é ação dela: o botão
`Open card...` do estado vazio e o item `File > Open card...` (`Ctrl+O`), que é
o mesmo caminho — o botão dispara a ação do menu, não uma segunda cópia da
lógica. Com um cartão aberto, o mesmo item troca de cartão; se houver edição que
não está em arquivo nenhum, ele pergunta **antes** de abrir o diálogo.

```sh
make -C tools/mcr ui-vazia    # a janela sem cartao; ou, na raiz: make mcr WE2002_MCR_CARD=
```

Sem `WE2002_MCR_CARD` — ou com a variável apontando para arquivo que não existe
— o `make mcr` **não aborta mais**: ele sobe a janela vazia e diz que é o editor
quem abre o cartão. Até a MCR-TASK-15 ele parava com `ERRO: cartao nao
encontrado`, o que tirava do usuário justamente a tela que sabe pedir um
arquivo; e o `app.py` sem argumento abria o diálogo **antes** da janela, um
modal sobre nada que, cancelado, não deixava nada visível.

### O que a janela faz

Duas abas. **Players** traz os 23 slots à esquerda (`[POS] Nome`) e a ficha à
direita: nome, dorsal — mostrado **duas vezes**, porque o cartão o guarda duas
vezes, e as duas discordarem é a melhor evidência de encoder errado —,
aparência, físico e os 16 atributos. Todo editor tem o alcance do **campo**, então
valor fora de faixa é inalcançável, não recusado adiante.

**Formation** desenha o campo com os dez jogadores de linha. **Arraste um
marcador** para movê-lo: os fatores `×7` e `×2` são de tela e só existem em
[`ui/formation_view.py`](ui/formation_view.py), que divide de volta antes de
qualquer coisa chegar ao modelo. Abaixo, os dez papéis, os cinco cobradores
(`SF LF RC LC PK`) e o **capitão** (`CP`) — todos como posição no **onze
inicial**, `0..10`.

### Gravar

| ação | o que faz |
|---|---|
| **Save a copy** (`Ctrl+S`) | grava em `<nome>-edited.mcr`, ao lado — nunca no cartão aberto |
| **Save as…** | escolhe o destino |
| **Overwrite the original…** | pede confirmação, com **No** como padrão, e **não** passa `--force`: a recusa que protege a fixture continua valendo |

Fechar com edições não gravadas pergunta antes. Nada chega ao arquivo até um
desses três — editar mexe no modelo, e só.

### As bandeiras de automação

```sh
app.py --smoke                       # abre, pinta um quadro, sai 0. É o contrato do gate
app.py <cartão> --screenshot out.png --tab 1
app.py <cópia> --write-probe DIR --drag-to 14,43
app.py <cartão> --report-formation
app.py --open-probe --open-with <cópia>   # a janela vazia e as duas portas de abrir
```

---

## Os gates

| comando | o que julga |
|---|---|
| `python3 tools/mcr/selftest.py` | **o obrigatório.** Os `self_check()` de 14 módulos, as três regras de desenho, a varredura de idioma e os controles negativos plantados. Não precisa de cartão, de venv, de Qt nem de display |
| `python3 tools/mcr/controls.py` | planta cada controle numa cópia da árvore e **exige o vermelho**; a última linha diz quantos são e de que tipo |
| `python3 tools/mcr/ui_check.py` | a janela sobe no `:98`; com cartão, dirige os widgets, grava dois cartões, confere o round-trip deles e planta os próprios controles |
| `python3 tools/mcr/gme.py --check` | os oito `.gme` de `mcr/`: cada um desmontado e remontado tem de dar o **mesmo arquivo**. Não precisa de fixture — é o único gate deste ciclo que roda em qualquer clone |
| `python3 tools/mcr/glossary.py` | espanhol e português remanescentes em `tools/mcr/**.py` |
| `python3 tools/mcr/layout.py --rule1` | endereço de save fora do `layout.py` |
| `python3 tools/mcr/options.py --check` | a medição da câmera, contra os quatro cartões; pula sem `WE2002_MCR_CAMERA_CARDS` |

14 dos 17 módulos respondem a `--self-check` sozinhos; os três que não são o
`cli.py`, o `harness.py` (que o agregador roda) e o `ui_check.py`.

No `ctest`, quatro alvos:

```sh
WE2002_MCR_CARD="$PWD/work/entrada.mcr" ctest --test-dir build -R mcr
```

- **`mcr_selftest`** — não precisa de nada, e nunca pula;
- **`mcr_card`** — precisa de `WE2002_MCR_CARD`, senão pula com 77;
- **`mcr_container`** — precisa só de `mcr/*.gme`, que está versionado;
- **`mcr_ui`** — precisa do venv e do `:98`, senão pula com 77.

Numa máquina sem venv e sem fixture: **2 passed, 2 skipped** — o
`mcr_container` passa junto com o `mcr_selftest`, porque a entrada dele veio no
clone.

> **O `mcr_ui` só mede gravação com `WE2002_MCR_CARD` apontado.** Sem a
> variável ele passa com a janela sozinha e imprime `note: no WE2002_MCR_CARD,
> so the write probe did not run`. **Leia a linha, não o `Passed`.**

---

## O oráculo

[`oracle/`](oracle/) tem três roteiros que dirigem o **editor do Obocaman**
(`we-team-editor.exe`, sob Wine, no `:98`) — foi assim que o `0x6500` deixou de
ser opinião:

```sh
make -C tools/mcr oracle-controle     # o par obrigatório: sem editar nada
make -C tools/mcr oracle-capitao      # as seis colunas em seis linhas
make -C tools/mcr oracle-nome         # o nome que enche os dez bytes
```

Cada alvo refaz a imagem de trabalho, roda o roteiro e já imprime o resultado.
Cru, é isto:

```sh
cp --reflink=auto roms/japanese-shift-jis.bin work/wte-japanese-shift-jis.bin
rm -f work/oraculo-13-seis.mcr
bash wte/tools/golden_run_wte.sh tools/mcr/oracle/13-seis-linhas.txt \
     work/wte-japanese-shift-jis.bin /tmp/oraculo-13
python3 tools/mcr/formation.py work/oraculo-13-seis.mcr
```

> **A primeira linha não é zelo, é a diferença entre ter e não ter controle.**
> O ` Accept` da tela de tática do oráculo **grava na imagem de CD**, então uma
> corrida deixa a seguinte com os valores da anterior. Medido em 2026-09-08:
> rodado sobre a imagem que a MCR-TASK-13 tinha deixado, o `oracle-controle`
> devolveu `[0, 1, 2, 3, 4]` e capitão `5` — os valores do **experimento**, com
> cara de controle. Sobre a imagem refeita ele devolve `[7, 7, 8, 7, 7]` e `8`,
> que é o que o jogo gravou. O alvo do `make` refaz sozinho; à mão, não esqueça.

- `13-controle.txt` — o **controle**: exporta sem tocar em nada;
- `13-seis-linhas.txt` — põe as seis colunas em seis linhas distintas, o que
  mostrou que `0x6500` é o **capitão**;
- `13-nome-de-dez.txt` — o nome que enche os dez bytes.

A imagem tem de ser a **japonesa**: com a europeia o `wte.exe` morre ao trocar
de time.

---

## As três regras de desenho

1. **Só o `layout.py` tem endereço.** Todo o resto pede a ele, e uma varredura
   tokenizada recusa o contrário.
2. **Os bytes crus são normativos.** O modelo é uma *vista* sobre o cartão, e
   escrever é read-modify-write **no campo** — é isso que faz o round-trip
   fechar em zero e que carrega intactos os 10 bytes finais de cada registro, a
   folga do bloco, o diretório e os seis campos de tática.
3. **A UI não conhece endereço, e o núcleo não conhece Qt.** A tela entra por
   `model.load()` e sai por `model.store()`, e nada mais; as duas metades são
   varridas a cada corrida do `selftest`.
