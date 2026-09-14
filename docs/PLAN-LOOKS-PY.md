# Plano — visualizador 3D da aparência do jogador, em Python + Qt

> **Estado: plano escrito em 2026-09-14, nenhuma fase executada.**
>
> Este arquivo é a **fonte de verdade** do projeto `looks`, o sexto deste
> repositório, ao lado do `newWe2002`, do `wte/`, do PES2 e do port do `.mcr`.
> Ele não compartilha build nem código com nenhum deles; o que empresta é
> ferramenta de leitura de disco e conhecimento de formato.
>
> Tudo que a §1 afirma foi **medido nesta máquina em 2026-09-13 e 2026-09-14**,
> e cada linha traz o comando que a reproduz. Onde há opinião de terceiro ainda
> não conferida, está dito na própria linha.
>
> Ciclo de tasks: **aberto em 2026-09-14**, em
> [`/docs/tasks/looks/progresso.md`](/docs/tasks/looks/progresso.md) — 20 tasks,
> prefixo `LOOKS-TASK-`, pool `CORR-LOOKS-`, perfil
> [`/docs/prompts/perfil-looks.md`](/docs/prompts/perfil-looks.md). Roda por
> `/executar looks`. A §7 ganhou uma **Fase 0** que a primeira versão não tinha:
> linhagem e ambiente precisam existir antes do primeiro módulo.

---

## 0. Escopo

### Objetivo

Renderizar, num aplicativo Python + Qt, o **modelo 3D do jogador** que o WE2002
desenha na tela `LOOKS SET` — lendo a geometria, as texturas e as paletas
**direto dos arquivos do disco**, sem recorte de imagem e sem captura de tela.

A tela alvo fica em `EDIT` → `NEW PLAYER` / `EDIT PLAYER` → `LOOKS SET`, e tem
doze campos: `DEFAULT`, `NAT`, `SKIN`, `HAIR`, `H.COL`, `FACE`, `H.F.COL.`,
`HEIG`, `BODY`, `AGE`, `BOOTS`, `FOOT`. O jogo redesenha o boneco a cada
mudança; é esse comportamento que se reproduz.

### Não-objetivos

- **Não grava nada.** Nem na imagem de CD, nem no cartão. v1 é visualizador, e
  a decisão é do dono do repositório (2026-09-13).
- **Não anima.** Pose parada. Animação mora no `ANIME.BIN` e é outro projeto.
- **Não toca `roms/`.** Mesma regra de todos os projetos daqui.
- **Não estende o `we2002_core`.** Nada em `src/` aprende o que é modelo 3D.
- **Não reconstrói ISO.** O jogo acha arquivo por LBA fixo (§8, item 8); mesmo
  que a v2 grave, será fit-or-fail.

### Definição de pronto

1. `python tools/looks/cli.py sections roms/japanese-shift-jis.bin` lista as
   **20 seções** do `EDT_MOD.BIN` — duas listas de onze, com duas em comum
   (§1.5) — e as **106** do `MODEL.BIN`, e as duas varreduras terminam
   **exatamente no EOF**.
2. Cada uma das 11 peças de **cada lista** do `EDT_MOD.BIN` tem nome medido —
   cabeça, tronco, braço, coxa, pé —, decidido pelo emulador e não por palpite.
3. `python tools/looks/ui/app.py --screenshot out.png --looks A-I3-A-F-A`
   produz um boneco reconhecível, com a pele e o cabelo daquela tupla.
4. `ctest -R looks` numa máquina limpa: **1 passed, 2 skipped**.
5. O confronto da §5.3 roda: nosso quadro contra o quadro do emulador na mesma
   tupla, com a diferença medida e registrada — não necessariamente zero, mas
   **medida e explicada**.

---

## 1. Diagnóstico — o que já está medido

A imagem de trabalho é **`roms/japanese-shift-jis.bin`** (307.187.664 B, dump
de arquivo único, SLPM-87056), escolhida pelo dono do repositório em
2026-09-13. As medições de RAM foram feitas no DuckStation rodando
`C:\games\ps1\work\we2002-english.cue`, que é um patch de tradução de terceiro
da mesma release — e a §1.3 mostra **o que o patch encosta e o que não**, que é
o que autoriza dirigir o emulador num disco e ler os bytes no outro.

### 1.1 Os dois arquivos de modelo, e o que eles não são

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/iso.py ls roms/japanese-shift-jis.bin
```

| arquivo | LBA | bytes | forma | comprimido? |
|---|---:|---:|---|---|
| `/BIN/EDT_MOD.BIN` | 5000 | 36.072 | form1 | **não** |
| `/BIN/MODEL.BIN` | 8100 | 64.800 | form1 | **não** |

Os dois são **form1 nesta imagem**, o que importa: na
`golden-european-deluxe.bin` 18 dos 105 `TEX_*.BIN` são **form 2** e o
`iso.py` se recusa a lê-los (§1.14 do [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md)).
Essa armadilha não alcança estes dois arquivos, mas alcança as texturas de
uniforme se o projeto crescer para elas.

E nenhum dos dois é LZSS, ao contrário do `DAT2D.BIN` e dos `TEX_*`:

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/lzss.py roms/japanese-shift-jis.bin \
  --file /BIN/EDT_MOD.BIN -v
#  /BIN/EDT_MOD.BIN   36072 B  header 2 w -> stream at 8  none  0 block(s)
#  whole 0   partial 0   not LZSS 1   (of 1)
```

O `MODEL.BIN` responde igual, com cabeçalho de 18 palavras. **São dados crus,
prontos para uso** — é o que se espera de arquivo que a Konami carrega direto
para a RAM sem passar por descompressor.

### 1.2 Onde cada um carrega, medido e não deduzido

O cabeçalho dos dois começa com **ponteiros KSEG0 absolutos**, e é isso que dá
o endereço de carga sem tentativa e erro:

```sh
python -c "
import sys,struct; sys.path.insert(0,'tools/pes2'); import iso
with iso.Image('roms/japanese-shift-jis.bin') as im:
    for p in ('/BIN/EDT_MOD.BIN','/BIN/MODEL.BIN'):
        d=im.read_file(p); print(p, ' '.join('%08x'%x for x in struct.unpack_from('<8I',d,0)))"
```

```
/BIN/EDT_MOD.BIN  8011c070 8011c008 00000003 00000000 00000002 80120bf0 ...
/BIN/MODEL.BIN    8016e848 8016e858 8016e968 8016e968 8016ea38 8016eaa0 ...
```

O segundo ponteiro do `EDT_MOD.BIN` é `0x8011C008`, e o alvo dele é o offset 8
do próprio arquivo — logo **`BASE = 0x8011C000`**. Para o `MODEL.BIN` o mesmo
raciocínio dá **`BASE = 0x8016E800`**, que é exatamente o valor que o `we3d`
deduziu sem emulador e que a §2.2 do
[ANALISE-REPOS-WE3D-DBMANAGER.md](/docs/ANALISE-REPOS-WE3D-DBMANAGER.md) já
tinha conferido no disco.

**E quem redeixa isso é um comando, não esta seção.** O
`layout.derive_base()` implementa a regra acima — `base = min(ponteiros do
cabeçalho) - 4 × (número de palavras do cabeçalho)` — e o
`iso_source.py --check-discs` a **roda sobre os dois arquivos reais, nos dois
discos**, a cada corrida. Sem isso as duas constantes ficariam cravadas na
prática: o `derive_base()` só era exercitado sobre vetores sintéticos
construídos para casar com o algoritmo, e uma regressão nele deixaria o
`--check` verde até a Fase 2 ([`CORR-LOOKS-008`](/docs/tasks/looks/CORR-LOOKS-008.md)).

```text
  base     /BIN/EDT_MOD.BIN      2 words -> 0x8011c000 (constant 0x8011c000) ok
           642 word(s) with the top bit set, 24 of them inside the file under that base
  base     /BIN/MODEL.BIN       18 words -> 0x8016e800 (constant 0x8016e800) ok
           1703 word(s) with the top bit set, 240 of them inside the file under that base
```

A segunda linha de cada par é a **advertência medida**, e não enfeite: é por
isso que a derivação **não** varre o arquivo inteiro. São 642 e 1.703 palavras
com o bit alto ligado — dado de vértice e de cor —, das quais só algumas
dezenas apontam para dentro do arquivo. Ler tudo aquilo como tabela de
endereço dá alvo na casa dos bilhões e uma base que não significa nada. O
número é impresso pela ferramenta justamente para não envelhecer na prosa.

Como a geometria é byte a byte idêntica nos dois discos, a base derivada do
lado inglês tem de ser **a mesma** — asserção de graça sobre bytes que o
comando já leu, e a razão de dirigir o disco inglês ser permitido.

### 1.3 A prova pelo emulador, e a divisão de trabalho entre dois discos

Com o jogo parado na tela `LOOKS SET`, lendo a RAM pelo servidor MCP do
DuckStation:

| endereço | RAM | arquivo no disco |
|---|---|---|
| `0x0011C000` | `70c0118008c0118003000000...` | `EDT_MOD.BIN[0:64]` **idêntico** |
| `0x0016E800` | `48e8168058e8168068e91680...` | `MODEL.BIN[0:48]` **idêntico** |

Os dois carregam crus, no endereço previsto, sem transformação nenhuma.

E a RAM veio de um disco **com patch de tradução para inglês**, enquanto o
arquivo veio do **japonês original**. Isso pedia conferência de verdade, e ela
foi feita em 2026-09-14 comparando os arquivos inteiros, não os primeiros bytes:

| arquivo | LBA/tamanho nos dois | japonês × inglês |
|---|---|---|
| `/BIN/EDT_MOD.BIN` | 5000 / 36.072 | **idêntico** (`6ff56894e7ce`) |
| `/BIN/MODEL.BIN` | 8100 / 64.800 | **idêntico** (`0b3814bb0d3b`) |
| `/BIN/DAT2D.BIN` | 5300 / 81.124 | **difere** |
| `/SELECT.BIN` | 850 / 300.648 | **difere** |
| `/SLPM_870.56` | 24 / 337.920 | **difere** |

**Esta é a linha mais operacional do plano**, e decide como se trabalha:

- **A geometria é a mesma nos dois discos.** Os dois arquivos de modelo são
  byte a byte iguais, no mesmo LBA e com o mesmo tamanho. Logo a Fase 2 pode
  dirigir o emulador no disco **inglês**, com os menus legíveis, sem risco
  nenhum para o que ela mede.
- **A textura não é a mesma.** O `DAT2D.BIN` **difere**, e é justamente o
  arquivo que guarda cabelos, rostos, corpos, chuteiras e as paletas de pele
  (§1.7). O patch mexeu ali — provavelmente na fonte dos menus, que mora no
  mesmo contêiner. Portanto **toda medição de textura e de paleta sai do
  japonês**, e ler offset de paleta no disco inglês é erro silencioso: o número
  existe, o gráfico aparece, e é outro.

A divisão, então: **o japonês é a fonte de verdade dos bytes; o inglês é o
disco de dirigir.** As duas imagens japonesas desta máquina são o **mesmo
dump** — `roms/japanese-shift-jis.bin` e
`C:\games\ps1\roms\we2002\we-2002-original-japao.bin` têm o mesmo
`sha256 e853eb14f5bddd50…`, 307.187.664 bytes, **reconferido em 2026-09-14**
pela [`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md):

```sh
python tools/looks/iso_source.py --check-discs <japonês.bin> <inglês.bin>
```

O `--check-discs` confere os quatro arquivos **por dentro do disco**, que é o
que decide, e não a imagem inteira. **Ele mora no `iso_source.py` desde a
[`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md)**
(2026-09-14), e não mais no `layout.py`: ler disco é trabalho da fachada, e o
`layout.py` não faz I/O. Para a imagem inteira, que só responde "é
este dump mesmo?":

```powershell
python -c "import hashlib,sys; h=hashlib.sha256(); f=open(sys.argv[1],'rb'); [h.update(b) for b in iter(lambda: f.read(1<<22), b'')]; print(h.hexdigest())" roms/japanese-shift-jis.bin
```

Os digests de dentro do disco, todos os quatro, estão na §4.5 — e o
`layout.py` os carrega como constante, para que ler textura do disco errado
**pare** em vez de entregar outro gráfico.

A imagem inglesa tem 306.834.864 bytes — **352.800 a menos**, 150 setores —,
mas todos os LBAs conferidos batem, então o encolhimento está na cauda e não
desloca nada que este plano leia.

### 1.4 O formato de seção, e a correção que ele exigiu

A §2.2 do [ANALISE-REPOS-WE3D-DBMANAGER.md](/docs/ANALISE-REPOS-WE3D-DBMANAGER.md)
descreve o `MODEL.BIN` como seções contíguas:

```
seção:      uint32 numVertex | uint32 numPrimitive
            primitiva[numPrimitive]   (24 bytes cada)
            vértice[numVertex]        (8 bytes cada)
```

Isso está certo, **e incompleto** em dois pontos. A varredura ingênua morre na
seção 55, e foi o que aconteceu aqui na primeira tentativa; o que falta é o
separador. A primeira redação desta seção dizia:

```
depois da última seção de um grupo vêm 8 bytes de zero
```

**e o "8" estava errado** — corrigido em 2026-09-14 pela
[`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md), que implementou a
regra e a mediu nos dois arquivos:

```
depois da última seção de um grupo vem uma CORRIDA de palavras zero
```

No `MODEL.BIN` a corrida tem sempre 8 bytes, então a regra fixa funciona lá por
coincidência. No `EDT_MOD.BIN` as duas primeiras folgas têm **12 bytes** e as
oito seguintes têm 8 — medido `[12, 12, 8, 8, 8, 8, 8, 8, 8, 8]`, mais 8 de
cauda. Um varredor que consuma sempre 8 cai 4 bytes dentro do próximo cabeçalho
e lê `nVert = 65.563` e `nPrim` na casa dos bilhões. **É o mesmo sintoma da
seção 55**: parece formato errado, e é a regra do intervalo.

Com a regra da corrida, a varredura fecha:

| arquivo | a partir de | seções | vértices | primitivas | termina em |
|---|---:|---:|---:|---:|---|
| `MODEL.BIN` | 1816 | **106** | 2.461 | 1.767 | **64.800 = EOF exato** |
| `EDT_MOD.BIN` | **216** | **20** | 1.218 | 1.074 | 36.064 + 8 = **36.072 = EOF exato** |
| `EDT_MOD.BIN` | 15.704 | 11 | 690 | 611 | 36.064 + 8 = 36.072 = EOF exato |

As 106 do `MODEL.BIN` confirmam a contagem que o repositório já tinha. O que é
**novo** é que elas se dividem em **6 grupos**, de tamanhos
`[55, 1, 34, 7, 5, 4]` — a fronteira de grupo é justamente a corrida de zeros.
O `EDT_MOD.BIN` dá `[1] × 20`: cada peça é seu próprio grupo.

**A segunda linha da tabela está ali de propósito.** Começar em 15.704 também
fecha no EOF exato, e por isso passou por leitura completa do arquivo até a
[`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md): **terminar no fim não
diz nada sobre o começo**. É a razão de a coluna "a partir de" existir nesta
tabela, e de nenhuma contagem de seção ser escrita sem ela.

**O `+ 8` da linha do `EDT_MOD.BIN` é cauda, e não detalhe de escrita.** A
última seção dele acaba em 36.064 e o arquivo tem 36.072: há uma corrida de
zeros **depois** da última seção. Quem afirmar "termina no EOF" comparando o
fim da última seção erra por 8 bytes num arquivo que leu perfeitamente, e vai
procurar uma seção que não falta. Por isso o `section.scan()` devolve **onde a
passagem parou**, cauda consumida, e não o fim da última seção — no `MODEL.BIN`
os dois coincidem, que é justamente por que medir só ele não mostraria a
diferença.

E duas correções ao formato da primitiva, medidas na mesma corrida:

- **O quarto byte de cada cor não é `pad`.** Na cor 0 ele **nunca** é zero —
  120, 121, 122 ou 127 nas 1.767 primitivas do `MODEL.BIN`, e 120, 121 ou 122
  nas 611 do `EDT_MOD.BIN` — e nas cores 1, 2 e 3 é **sempre** zero. É um byte
  de **modo por primitiva**, guardado na primeira cor. O `we3d` o chama de pad,
  e descartá-lo obrigaria a reescrever o parser na Fase 3, que é onde a
  incógnita (d) depende dele.
- **O `pad` do vértice, esse é pad mesmo**: zero em 2.461 de 2.461 no
  `MODEL.BIN`. É o que o distingue de uma quarta coordenada, e o
  `section.py` o preserva porque a regra 2 do plano diz que byte cru é
  normativo.

### 1.5 O `EDT_MOD.BIN` tem 20 seções e **duas** listas de onze

> **Corrigido em 2026-09-14** pela
> [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md). Esta seção dizia
> *"é um jogador só, de onze peças"*, que *"há dados não-geometria entre as
> seções"*, e que a região entre 216 e 15.704 era *"material de textura"* com
> *"um cabeçalho TIM em 3.228"*. As três coisas estavam erradas, e pela mesma
> causa: a varredura que as mediu **começou no offset 15.704**, a 43% do
> arquivo, e fechou no EOF exato — o que parece leitura completa e não é.

O `MODEL.BIN` é contíguo; o `EDT_MOD.BIN` **também é**, do offset 216 ao EOF:
seção, corrida de zeros, seção. O que não é geometria são os **216 bytes
iniciais**, que são o cabeçalho e as duas listas. Varrendo dali:

```
scan(edt, 15704) ->  11 sec   690 vert   611 prim  end=36072   (a leitura parcial)
scan(edt,   216) ->  20 sec  1218 vert  1074 prim  end=36072
```

Os dois fecham no EOF, e **é por isso que o primeiro engana**: começar perto do
fim e terminar no fim não diz nada sobre o começo. Daí a regra que a
[`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md) passou a exigir:
**toda contagem de seção vem acompanhada do offset de onde a varredura
começou.**

O início não é constante — é **derivado**, pelo `layout.geometry_start()`, como
o `BASE` da §1.2: o menor alvo de qualquer lista do cabeçalho. Para este arquivo
dá 216.

#### As duas listas

O cabeçalho tem **duas palavras**, e cada uma aponta para uma lista de onze
registros `(contagem, ponteiro)` terminada por `0x000000FF`:

```
[ 0] 8011c070 -> 112   (lista A)
[ 1] 8011c008 ->   8   (lista B)
```

```
lista A (em 112): 216 2608 4272 3440 6800 9328 13352 15704 11340 14528 17572
lista B (em   8): 19440 21832 24136 22984 26920 29704 33720 15704 31712 34896 17572
```

**A união das duas é exatamente as 20 seções**, e elas compartilham duas:
15.704 e 17.572, nas **mesmas posições** (7 e 10) das duas listas.

| pos | lista A | | lista B | |
|---:|---:|---|---:|---|
| 0 | 216 | 84/71 | 19.440 | 84/71 |
| 1 | 2.608 | 30/24 | 21.832 | 40/34 |
| 2 | 4.272 | 80/78 | 24.136 | 88/86 |
| 3 | 3.440 | 30/24 | 22.984 | 40/34 |
| 4 | 6.800 | 80/78 | 26.920 | 88/86 |
| 5 | 9.328 | 72/59 | 29.704 | 72/59 |
| 6 | 13.352 | 40/35 | 33.720 | 40/35 |
| 7 | **15.704** | 63/56 | **15.704** | 63/56 |
| 8 | 11.340 | 72/59 | 31.712 | 72/59 |
| 9 | 14.528 | 40/35 | 34.896 | 40/35 |
| 10 | **17.572** | 63/56 | **17.572** | 63/56 |

Quatro leituras, todas de peso:

- **As duas listas têm a mesma forma.** Cada uma é uma peça sozinha (`84/71`,
  na posição 0) mais **cinco pares de contagem idêntica**. Isso é um corpo:
  membros espelhados mais um tronco ou cabeça. O que muda entre elas são as
  contagens de três dos cinco pares — `30/24` e `80/78` na A contra `40/34` e
  `88/86` na B —, e duas peças são **literalmente a mesma seção**.
- **São dois modelos, não um.** O `we3d` levantou, só do `MODEL.BIN` e sem
  conferir, que os 106 blocos de lá se combinam em **14 jogadores de 11
  peças**. O `EDT_MOD.BIN` traz dois desses conjuntos de onze, montados sobre o
  mesmo esqueleto.
- **A pergunta que isso abre**, e que **não** se responde aqui: dois bonecos
  (jogador de linha e goleiro?), duas qualidades do mesmo boneco, ou um modelo
  mais um conjunto de variações? Quem decide é a
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md), pelo
  emulador — e o estímulo já existe: os **dois save states** do usuário são
  exatamente goleiro e jogador de linha. A incógnita (a) da §6 passou a ter
  **três** respostas possíveis, não duas.
- **A ordem da lista não é a ordem do arquivo**, nas duas. Na A, o 216 — a
  primeira seção do arquivo — é o primeiro registro, mas o 4.272 vem antes do
  3.440; na B, o 15.704 é o **oitavo**. A lista é ordem de montagem ou de
  desenho, não de armazenamento, e é ela que vale. Assumir ordem de arquivo
  embaralha as peças sem sintoma óbvio — o mesmo erro que a §3.3 do
  [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) registra para elenco. **E é esta a
  razão de precisar da lista**, não a de a varredura não alcançar as seções: a
  varredura as alcança todas, do 216 ao EOF; o que ela não dá é a ordem, nem
  qual peça pertence a qual modelo.

#### O "cabeçalho TIM" de 3.228 era falso positivo

```
e[3228:3244] = 1000000007002700110000000300e6ff
palavra em 3228 == 0x10        : True
seção que contém 3228          : 2608 .. 3432  (30 vert / 24 prim)
palavras == 0x00000010 no arquivo: 3
```

`0x10` é a magia de um TIM e é também um inteiro qualquer. Este cai **dentro do
corpo** de uma seção que varre limpa. Não há textura no `EDT_MOD.BIN`; onde ela
mora é no `DAT2D.BIN` (§1.7).

#### O cabeçalho do `MODEL.BIN`: 18 listas, o slot vazio, e uma terceira forma

Medido em 2026-09-14 pela
[`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md), ao fechar a
pergunta que a §1.2 tinha deixado aberta — por que o início do `MODEL.BIN` é
constante enquanto o do `EDT_MOD.BIN` é derivado.

**Um par `(0, 0)` é slot vazio, não fim de lista.** O `read_pointer_list()`
recusava seis das dezoito listas dizendo que a de 672 *"fecha com `0x00000000`
em 736 e não com o terminador"*. Não fecha: 736 é a **entrada 8 de um par cujo
tag também é zero**, e a lista segue até o `0x000000FF` de 768, como todas.
Pulando o par vazio, as dezoito leem:

```
tamanhos: [1, 1, 12, 12, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 12]
```

Um ponteiro zero é **pulado e não guardado**: guardá-lo poria o offset 0 — o
próprio cabeçalho — numa lista de inícios de seção, e uma varredura que
recebesse isso entraria na tabela de ponteiros.

**E o início continua constante, por um motivo que agora é medido e não
procedimental.** Dezesseis das dezoito listas abrem com uma entrada de tag
`0x80` mirando o offset **104**, e 104 **não é seção**:

```
secao em 104?  nao -> claims 2148999984 vertices and 2149000600 primitives
words em 104:  80172330 80172598 80172800 80172b30 80172e60 ...
               -> 15152  15768  16384  17200  18016 ...
```

É uma **corrida de ponteiros KSEG0 crus** — sem tag, sem terminador —, uma
**terceira forma** de tabela neste arquivo, mirando dentro da região de
geometria. Logo `min(alvos)` responderia 104, e o `geometry_start()` entregaria
a uma varredura um início dentro da tabela de ponteiros: exatamente a falha que
derivar o início existe para impedir. Por isso o `layout.is_derivable()` recusa
este arquivo, e o `MODEL_GEOMETRY_START` guarda o **1816**, que é fato medido e
não algo que as listas declarem.

**O que fica aberto, e quem responde.** Ninguém mediu o que essa corrida
agrupa. Se a incógnita (a) concluir que o boneco vem do `MODEL.BIN`, é ela que
diz **qual** dos modelos de lá — e é onde a hipótese do `we3d`, de 14 jogadores
de 11 peças, se confere. A linha está escrita na
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md).

### 1.6 A tela desenha com textura, e o formato de seção não tem textura

Aqui está a contradição que a Fase 3 tem de resolver, e vale ter na mesa desde
já. Com o jogo na tela `LOOKS SET`:

- `get_gpu_state --aspect draw` responde **`texture_color_mode: "4-bit CLUT"`**,
  texpage em VRAM (704, 0), `texture_disable: false`;
- há **quatro TMDs Sony de verdade** vivos na RAM — `id=0x41`, `flags=1`, ou
  seja já *fixados* pelo `OpenTMD` —, em `0x0016821C`, `0x00168C0C`,
  `0x0016A2C4` e `0x0016A650`, com 92, 261, 30 e 18 vértices, e primitivas de
  modo **`0x2d`** e **`0x3d`** — quad texturizado, flat e gouraud;
- mas a primitiva de 24 bytes das seções de `EDT_MOD.BIN`/`MODEL.BIN` é
  *"gradation, no-texture"*: quatro cores RGB e quatro índices, **sem UV**.

E os quatro TMDs texturizados ficam **fora** do span dos dois arquivos:
`EDT_MOD.BIN` ocupa `0x8011C000..0x80124CE8`, `MODEL.BIN` ocupa
`0x8016E800..0x8017E520`, e `0x00168xxx` não está em nenhum dos dois. Eles são
outra coisa, ainda não identificada. É a incógnita de maior risco do plano.

### 1.7 As texturas de aparência moram no `DAT2D.BIN`, e falta a lista de paletas

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/bin_archive.py ls \
  roms/japanese-shift-jis.bin --file /BIN/DAT2D.BIN
#  /BIN/DAT2D.BIN   81124 B   23 image(s), 0 clut(s)
```

As 23 imagens saem inteiras — 128×128 a 4 bpp cada, com as coordenadas de VRAM
que o modelo vai precisar. As três primeiras são as que interessam, segundo a
tabela do CARP (`Offsets\Offsets WE2002 - CARP\Dat\DAT2D.BIN.txt`):

| offset | VRAM | rótulo do CARP |
|---:|---|---|
| 8 | (512, 256) | *"Pelos Cuerpos y botines"* — cabelos, corpos e chuteiras |
| 3.568 | (544, 256) | *"Caras"* — rostos |
| 7.456 | (512, 384) | *"Cuerpo"* |

**Mas `0 clut(s)`**, e isso é uma lacuna real: o `entries()` do `bin_archive.py`
acha a lista de imagens e **não** acha a lista de paletas deste arquivo. Que ela
existe, a tabela do CARP diz — as paletas começam em **65.892**, logo depois do
fim da lista de imagens (65.508 + 23×16 = 65.876). Fazer esse varredor achar as
duas listas é trabalho da Fase 3, e é a única mudança prevista em código de
outro projeto.

### 1.8 Uma contradição entre dois documentos da cena

O tutorial de cabelo do `zeta`
(`MCR\Apariencia fisica jugadores\Tutorial para pintar el cabello a jugadores WE2002 - zeta.pdf`)
manda abrir o gráfico no **offset 3.568** para achar os cabelos. A tabela do
CARP rotula o 3.568 como *"Caras"* e o **8** como *"Pelos"*. Os dois não podem
estar certos. **O disco decide**, e decidir isso é barato: exportar as duas
imagens por `bin_archive.py export` e olhar.

Enquanto não estiver decidido, nenhum código pode cravar nenhum dos dois.

### 1.9 O lado dos bits já está resolvido, e com três testemunhas

O campo de aparência do jogador não precisa de engenharia reversa nenhuma —
`src/core/Player.cpp` já decodifica os 12 bytes. O que esta sessão acrescentou
foi uma **terceira testemunha independente**: o fonte C++/MFC de
`MCR\We2002 edit - Haplo y polipoli\...\Codigo fuente\en_we2000edit\`, cujo
`PlayerEditDlg.cpp` faz o mesmo unpack, bit a bit, com os mesmos
deslocamentos e máscaras.

As tabelas de rótulo de lá são o vocabulário exato da tela:

| campo | valores |
|---|---|
| `skincolor` | `A B C D` (4) |
| `hairstyle` | `A1 A2 A3 B1 B2 B3 B4 B5 B6 C1 C2 D1 D2 E1 E2 F1 F2 F3 G1 H1 I1 I2 I3 J1 K1 L1 L2 L3 M1 N1 O1 P1` (**32**) |
| `haircolor` | `A`…`H` (8) |
| `facialhair` / `facialhaircolor` | `A`…`G` (7) |
| `build` | `A`…`H` (8) |
| `spike` (chuteira) | `A`…`H` (8) |
| `foot` | direito, esquerdo, ambos |

Batem com o `kHair[32]`, `kSkin[4]` e `kLetters[8]` que o
`src/app/Commands.cpp` já usa para o `defaultlook.txt`, e com o
`tools/mcr/domains.py`. **São quatro implementações concordando**; o assunto
está encerrado e não é fase deste plano.

No disco, os registros ficam em `/SELECT.BIN`, offset **157.164**, **1.242
jogadores × 12 bytes = 14.904 B** (fonte: `Offsets We2002.txt` do mesmo editor —
opinião de terceiro, a conferir na Fase 4).

### 1.10 A tabela de texto do editor

A interface da tela está em **Shift-JIS full-width**, não em ASCII, e a tabela
vive por volta de `0x000FCF50` na RAM: `"Skin Colour"`, `"Kind of Hair"`,
`"Nation"`, o símbolo `□` do `□ Turn`, e logo depois os códigos de posição
(`GK`, `CB`, `SB`, `DH`, `SH`, `OH`, `WG`, `CF`). Procurar `"Skin"` como ASCII
não acha nada; como `82 72 82 8B 82 89 82 8E`, acha em um lugar só.

É o mesmo codec que o `KanjiToAscii` do `we2002_core` trata, e a mesma
armadilha que o port do `.mcr` registra para o nome de 10 bytes.

### 1.11 Como voltar a essa tela — porque o emulador não fica de pé

As medições de RAM da §1.3 e da §1.6 foram tiradas com o jogo parado na tela
`LOOKS SET`. **O emulador foi encerrado em 2026-09-14**, e nada do que está
escrito acima depende dele para continuar valendo — mas reconferir depende, e
por isso a receita fica registrada aqui.

**Subir o emulador.** É o fork com servidor MCP, o mesmo do projeto de PES2;
nenhum dos dois DuckStation está no `PATH`:

```sh
python tools/pes2/fork.py status          # diz se já há um de pé
python tools/pes2/fork.py recipe          # como obter o binário, se faltar
```

**Qual disco — e são dois, de propósito.** As cópias de trabalho ficam em
`C:\games\ps1\work\`, cada uma com um `.src` ao lado dizendo de onde veio:

| cópia | origem | papel |
|---|---|---|
| `we2002-english.cue` | `…\roms\we2002\we2002-english\we2002-english.bin` | **dirigir o emulador** |
| `we2002-japao.cue` | `…\roms\we2002\we-2002-original-japao.bin` | conferência, quando a tela não importa |

**Bote o inglês.** As duas imagens japonesas têm os menus em japonês, e a tela
`LOOKS SET` inteira — os doze rótulos, o rodapé que nomeia o campo sob o cursor
— fica ilegível para quem dirige. O patch resolve isso, e pela §1.3 ele é
**byte a byte idêntico** nos dois arquivos de geometria, que é tudo que a Fase
2 mede na tela.

**Mas nunca leia textura dele.** O `DAT2D.BIN` difere entre os dois discos
(§1.3). Offset de paleta medido no inglês é número que existe e está errado.

O boot, no Windows, é pelo `make.ps1` — ele já tem a inglesa como default e
confere o carimbo `.src` da cópia:

```powershell
.\make.ps1 we2002-play          # sobre o option file que houver
.\make.ps1 we2002-play-fresh    # com o option file zerado
```

O `tools/pes2/fork.py launch <cue>` continua valendo, e é o caminho no Linux.

**A tela.** `EDIT` → `NEW PLAYER` → `LOOKS SET`. A tela de edição de jogador
tem o título japonês `選手エディット` e sete itens à esquerda; `LOOKS SET` é o
quarto, com o rodapé `Visual`.

**Duas coisas medidas sobre o controle**, e as duas custaram tentativa:

- **Círculo confirma** (não Cruz — é jogo japonês). E precisa de duração: com
  `duration_frames: 3` o jogo **não registra**, e a tela fica igual, o que
  parece botão errado. Com **8** entra.
- **Cruz abre `Exit?`** com `CANCEL` já selecionado. Não é destrutivo, mas é um
  desvio: confirmar ali com Círculo volta para onde estava.

**Dois save states resolvem a chegada.** O usuário gravou em 2026-09-14, com o
jogo já na tela de edição do jogador:

| slot | arquivo | mostra |
|---|---|---|
| 1 | `…/duckstation-mcp/savestates/SLPM-87056_1.sav` | **goleiro** |
| 2 | `…/duckstation-mcp/savestates/SLPM-87056_2.sav` | **jogador de linha** |

Os dois apontam para `C:\games\ps1\work\we2002-english.cue` — conferido no
campo `media` de dentro do arquivo, e não pelo nome, que **não diz de que disco
o state veio**: ele usa o serial japonês `SLPM-87056` mesmo no disco inglês.

**O ganho maior não é pular a navegação, é o baseline.** `load_state` devolve um
estado byte a byte idêntico antes de cada medição, e é isso que faz o diff da
Fase 2 medir só o campo que se trocou, em vez de medir também tudo que o jogo
mexeu no caminho. Os dois slots ainda dão um controle de graça: o que diferir
entre goleiro e jogador de linha é **uniforme ou posição**, não LOOKS.

**A RAM, porém, não sai do arquivo de state.** Medido em 2026-09-14: o
`tools/pes2/savestate.py` lê o cabeçalho e para — ele chama o CLI `zstd`, que
não está no `PATH` desta máquina, e o módulo `zstandard` também não está
instalado. Ele imprime o cabeçalho e **depois** estoura com
`FileNotFoundError [WinError 2]`, mensagem que não menciona `zstd` em lugar
nenhum. Portanto a memória se lê **por MCP vivo** — `read_memory`,
`search_memory`, `snapshot_memory` + `diff_memory` —, e o state é o ponto de
partida, não a fonte.

**O que continua não registrado:** a sequência de botões da tela de título até o
menu `EDIT`. Enquanto os states existirem ela não faz falta; se o disco ou o
build do emulador mudarem e os states pararem de carregar, ela volta a ser
necessária, e escrevê-la é trabalho da Fase 2 no `oracle.py`, no molde das rotas
nomeadas de `tools/pes2/mcp_drive.py`.

---

## 2. Ressalva legal e linhagem

- **O Superpack v6** (`C:\games\we2002\Superpackv6\`) é coletânea de terceiros
  sem licença — binários, fontes e tutoriais da cena de modding
  hispano-luso-italiana. **Nada dele entra no git**, nem arquivo nem
  transcrição extensa. Vale como o `roms/` e o `we-team-editor.exe`: o usuário
  mantém a pasta.

  **Os números, e a subpasta que eles descrevem** — remedidos em 2026-09-14 pela
  [`LOOKS-TASK-01`](/docs/tasks/looks/01-base-legal-e-linhagem.md). Esta seção
  dizia *"4,2 GB, 28.720 arquivos"* da **raiz**, e eles são da subpasta
  `We2002\` — 4.452.185.957 B em 28.720 arquivos. A raiz tem **31.790 arquivos
  e 4.830.420.054 B**, repartidos em treze pastas (`Iss1`, `Iss2`,
  `Iss98`, `Mls`, `Pes1`, `Pes2`, `We2000 1st`, `We2000 2nd`, `We2000 u23`,
  `We2001`, `We2002`, `We3`, `We4`) mais um `.htm` de cronologia. A diferença
  importa por um motivo prático e não de contabilidade: **todo caminho `MCR\u2026`
  citado neste plano é relativo a `Superpackv6\We2002\`**, não à raiz —
  `Superpackv6\MCR` não existe, e procurá-lo ali dá "pasta não encontrada" que
  parece Superpack errado.

  ```sh
  python tools/looks/superpack_count.py "C:/games/we2002/Superpackv6"
  ```
- **`Darkensses/we3d` é MIT** e pode ser reaproveitado **com crédito**. O
  parser dele serve como conferência cruzada de contagem, não como código a
  copiar — o stack é web.
- **O fonte `en_we2000edit`** (Haplo/polipoli) não tem licença, igual ao nosso
  `legacy/`. Serve como **testemunha**, para confirmar o que já sabemos. Não se
  copia código de lá.
- Obrigação **cumprida em 2026-09-14** pela
  [`LOOKS-TASK-01`](/docs/tasks/looks/01-base-legal-e-linhagem.md): o
  [NOTICE.md](../NOTICE.md) tem a seção *"Lineage of the appearance viewer"*,
  com os três materiais em linhas separadas, como o repositório já faz com o
  `WECompressor` e com o `Easy-Mcr`. Duas coisas que a execução acrescentou ao
  que esta seção previa: a seção *"Copyright and license status"* do mesmo
  arquivo afirmava que **todo** material de terceiro daqui é sem licença, o que
  o `we3d` desmente, e passou a nomear a exceção; e o `.gitignore` ganhou
  `/Superpackv6/`, entrada que hoje **não casa com nada** de propósito — a
  coletânea mora fora da árvore, e a linha é a guarda para o dia em que alguém
  a copiar para dentro.

---

## 3. Arquitetura

### 3.1 Onde mora, e o que não pode tocar

```
tools/looks/            núcleo Python puro. ZERO Qt, ZERO endereço fora de layout.py
tools/looks/ui/         a janela PySide6. ZERO endereço, ZERO leitura de disco.
work/venv-looks/        PySide6, fora do git
```

Nada em `src/`, nada em `include/we2002/`, nada no `we2002_core`. O projeto lê
o disco pelas ferramentas de `tools/pes2/` e não duplica nenhuma delas.

### 3.2 Os módulos

```
iso_source.py   fachada fina sobre tools/pes2/iso.py; abre a imagem e entrega
                bytes -- todo arquivo pela guarda do layout.py (ver 4.5)
layout.py       O ÚNICO com endereço: LBA, BASE, offsets de lista, 157164,
                mais a identidade dos dois discos e a guarda que a aplica (§4.5)
section.py      o formato da §1.4: cabeçalho, primitiva de 24 B, vértice de 8 B
modelfile.py    EDT_MOD.BIN e MODEL.BIN: lista de (contagem, ponteiro), grupos
texture.py      DAT2D.BIN por bin_archive.py + a lista de CLUTs que falta
looks.py        os 12 campos, seus domínios e os rótulos (A1..P1, A..D, ...)
assembly.py     campo de LOOKS -> peça + paleta. O coração, e a Fase 4
oracle.py       o emulador por MCP: capturar quadro, ler RAM, comparar
harness.py      Checker: ok/attempt/refuses/skip/report   (molde: tools/mcr)
controls.py     controles negativos por substituição literal no fonte
selftest.py     o agregador -- alvo looks_selftest
check_image.py  o alvo looks_image, que precisa da imagem
cli.py          sections | pieces | texture | looks | check
ui/app.py       --smoke, --screenshot, --looks TUPLA
ui/viewer.py    QOpenGLWidget, câmera orbital
ui_check.py     o alvo looks_ui, julgando a UI de fora
```

### 3.3 As três regras de desenho

Copiadas do `tools/mcr/`, onde já são varridas mecanicamente pelo `selftest.py`:

1. **Só `layout.py` carrega endereço.** Varredura sobre a árvore recusa
   constante hexadecimal ou LBA em qualquer outro módulo.
2. **Bytes crus são normativos.** Nada de estrutura intermediária que perca
   informação; o que se afirma sobre o arquivo se reconfere lendo o arquivo.
3. **A UI não conhece endereço e o núcleo não conhece Qt.** Varredura de linha
   em `ui/` recusa `import layout`; e depois de importar o núcleo inteiro,
   `assert "PySide6" not in sys.modules`.

### 3.4 Proveniência — quem sabe o quê

| módulo | sabe | não sabe |
|---|---|---|
| `layout.py` | todo endereço | formato, Qt |
| `section.py` | o formato de 24/8 bytes | onde as seções estão |
| `assembly.py` | a tabela de montagem | como desenhar |
| `ui/` | como desenhar | onde qualquer coisa mora |

### 3.5 Idioma

Documento em **pt-BR**, código e comentários em **en-US** — a mesma divisão do
resto do repositório.

---

## 4. Ambiente

### 4.1 Python duplo, e o venv

Vale aqui a mesma armadilha do port do `.mcr`: nesta máquina há mais de um
Python, e `apt install python3-pyqt6` instala para o errado e **termina em
verde**. Por isso PySide6 num venv próprio, `work/venv-looks/`, nunca por
gerenciador de pacote do sistema.

No Windows, `python` resolve para 3.13.14; `python3` **não existe** e cai no
atalho da Microsoft Store.

**Criado em 2026-09-14** pela
[`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md), no
Windows desta máquina:

```powershell
python -m venv work/venv-looks
work/venv-looks/Scripts/python.exe -m pip install PySide6
```

O `pip freeze` resultante, que é o que o Log da task registra:

```text
PySide6==6.11.2
PySide6_Addons==6.11.2
PySide6_Essentials==6.11.2
shiboken6==6.11.2
```

`PySide6` é o metapacote; quem traz o `QOpenGLWidget` da §0 é o
`PySide6_Essentials` (`from PySide6.QtOpenGLWidgets import QOpenGLWidget`,
conferido na mesma corrida). São ~246 MB baixados, e por isso o venv mora em
`work/`, que o `.gitignore` já ignora inteiro.

**O interpretador do venv se chama por caminho, não por `activate`.** Uma
receita que dependa de ativação não é reproduzível num agente que não mantém
estado de shell entre comandos; `work/venv-looks/Scripts/python.exe` (ou
`work/venv-looks/bin/python` no Linux) funciona em qualquer invocação.

### 4.2 A armadilha do MSYS

No Git Bash do Windows, um argumento que parece caminho absoluto POSIX é
**convertido** antes de chegar ao programa:

```sh
python tools/pes2/lzss.py roms/japanese-shift-jis.bin --file /BIN/EDT_MOD.BIN
#  C:/Program Files/Git/BIN/EDT_MOD.BIN: not a Form 1 /BIN/*.BIN of ...
```

O erro parece dizer que o arquivo não é form1, e o que houve foi outra coisa.
**`MSYS_NO_PATHCONV=1` é obrigatório** em toda chamada que passe caminho de
dentro do ISO. No PowerShell o problema não existe.

**Reproduzido de novo em 2026-09-14**, palavra por palavra, ao fechar a
[`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md):

```sh
$ python tools/pes2/lzss.py roms/japanese-shift-jis.bin --file /BIN/EDT_MOD.BIN
C:/Program Files/Git/BIN/EDT_MOD.BIN: not a Form 1 /BIN/*.BIN of japanese-shift-jis.bin

$ MSYS_NO_PATHCONV=1 python tools/pes2/lzss.py roms/japanese-shift-jis.bin --file /BIN/EDT_MOD.BIN
japanese-shift-jis.bin   1 container(s) in /BIN/
  /BIN/EDT_MOD.BIN          36072 B  header   2 w -> stream at     8  none  0 block(s), 36072 B outside
```

**E há uma saída melhor do que lembrar da variável: não passar o caminho pela
linha de comando.** Os caminhos de dentro do ISO que este projeto usa são
quatro e são fixos, então eles são **constantes do `layout.py`**
(`layout.EDT_MOD`, `layout.MODEL`, `layout.DAT2D`, `layout.SELECT`) e nunca
atravessam um shell. O `MSYS_NO_PATHCONV=1` fica valendo para as ferramentas de
`tools/pes2/`, que recebem o caminho como argumento — é o caso do `lzss.py`
acima, e é o caso de toda receita que este plano copiar de lá.

### 4.3 Tela

No Linux, `DISPLAY=:98`, pela regra do [CLAUDE.md](../CLAUDE.md). No Windows,
janela lançada e **movida para fora da tela** (`SetWindowPos` em −32000), pela
mesma razão: a máquina é do usuário enquanto o trabalho corre.

### 4.4 Os três alvos de `ctest`

Mesma divisão por custo que o repositório já usa:

| alvo | precisa | pula? |
|---|---|---|
| `looks_selftest` | nada | nunca |
| `looks_image` | `WE2002_LOOKS_IMAGE` | 77 |
| `looks_ui` | venv + display | 77 |

Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped**.

### 4.5 As duas variáveis, e a guarda que faz a regra valer

A §1.3 mede que os dois discos servem para coisas diferentes. Esta seção diz
como isso vira ferramenta. **São duas variáveis porque são dois arquivos**, e o
segundo é um `.cue` e não um `.bin`:

| variável | aponta para | serve a |
| --- | --- | --- |
| `WE2002_LOOKS_IMAGE` | `roms/japanese-shift-jis.bin` — a **trilha de dados** japonesa | tudo que **lê byte**: geometria, textura, paleta, registros |
| `WE2002_LOOKS_DRIVE_IMAGE` | o **`.cue` inglês** (nesta máquina `C:\games\ps1\work\we2002-english.cue`) | dirigir o emulador, pelos menus legíveis |

São duas famílias pela mesma razão que o PES2 tem `WE2002_PES2_*` e `PES2_*`:
lá a receita passou um tempo só com a primeira, e nesse tempo o único gate que
punha o jogo na tela se reportava *skipped* em 0,01 s enquanto a corrida
imprimia `100% tests passed` (§6.11 do
[`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md)). Uma variável para dois
papéis economiza uma linha e compra esse silêncio.

**A regra não mora na prosa: mora no `tools/looks/layout.py`**, que guarda o
sha256 de cada um dos quatro arquivos como lido de dentro do disco japonês, e
**recusa** conteúdo que não bata. Medido em 2026-09-14:

| arquivo no disco | sha256 (japonês) | inglês |
| --- | --- | --- |
| `/BIN/EDT_MOD.BIN` | `6ff56894e7ce94aa…` | **idêntico** |
| `/BIN/MODEL.BIN` | `0b3814bb0d3b47f4…` | **idêntico** |
| `/BIN/DAT2D.BIN` | `0e914e584c889635…` | `4a4d6a4fe301b116…` |
| `/SELECT.BIN` | `86d14a66a3cd72b9…` | `c9e1eaf89151b0c0…` |

```sh
python tools/looks/layout.py --check
python tools/looks/layout.py --sweep
python tools/looks/iso_source.py --check
python tools/looks/iso_source.py --check-discs <japonês.bin> <inglês.bin>
```

O primeiro é o gate: roda sem imagem, sem venv e sem display, e tem **oito
casos vermelhos** — conteúdo estranho no `DAT2D.BIN`, caminho que ninguém
mediu, geometria que não bate, a **varredura do `DIGEST` inteiro** exigindo
dica não vazia para todo caminho medido, base que joga um ponteiro do próprio
cabeçalho para fora do arquivo, arquivo que não começa por ponteiro, base
derivada que não bate com a constante, e a **árvore plantada** que a varredura
da regra 1 tem de achar.

Dois deles são varredura e não caso de propriedade, e pelo mesmo motivo: a
falha que fecham é por **omissão**. O `/SELECT.BIN` não pertencia a família
nenhuma e recusava com o "digest mismatch" pelado que o próprio módulo chama de
erro ([`CORR-LOOKS-006`](/docs/tasks/looks/CORR-LOOKS-006.md)); e o
`sweep_addresses()` só era rodado contra a árvore real, que está limpa, então
só era observado **verde**
([`CORR-LOOKS-009`](/docs/tasks/looks/CORR-LOOKS-009.md)).

O **`--sweep`** é a regra 1 conferida em vez de prometida: ele varre
`tools/looks/` por literal hexadecimal e por decimal de quatro dígitos ou mais
fora do `layout.py`. É tripwire, não parser, então tem escape — uma linha com
`# not-an-address: <razão>` sai da conta. **O marcador se chama pelo que ele
afirma**: a primeira grafia era `# address:`, que se lê como o contrário do que
o anotador quer dizer, e escape que se lê ao contrário é escape usado errado.

**E ele diz quanto varreu**, porque "varri tudo e está limpo" e "não abri
arquivo nenhum" imprimiam a mesma frase e saíam 0 — e essa frase é a que se lê
como prova de que a regra 1 está sendo cumprida:

```text
layout --sweep: no address outside layout.py (2 file(s), 500 line(s) swept)
```

A isenção do dono é por **caminho**, não por nome: o `os.walk` desce, então um
`ui/layout.py` sairia de graça se a comparação fosse pelo nome do arquivo — uma
pasta inteira fora da regra, que é exatamente como o ciclo do `.mcr` perdeu a
dele. O caso vermelho 8 planta as duas coisas e exige o resultado certo em
cada uma.

O **`iso_source.py --check`** exercita a fachada sobre um leitor de mentira, sem
disco: a leitura conferida recusa, a `read_unchecked()` devolve, e é o par que
importa — se as duas recusassem, o caso vermelho da primeira deixaria de estar
medindo a guarda.

O **`--check-discs`** é a demonstração viva contra os dois discos reais, e é o
que mostra a guarda ficando vermelha onde deve:

```text
English disc -- geometry accepted, the Japanese-only files refused
  refused  /BIN/DAT2D.BIN       (wanted refused) ok
  accepted /BIN/EDT_MOD.BIN     (wanted accepted) ok
  accepted /BIN/MODEL.BIN       (wanted accepted) ok
  refused  /SELECT.BIN          (wanted refused) ok
```

E a cada linha dessas o `--check-discs` ainda chama a `read_unchecked()` no
mesmo arquivo e exige bytes de volta — os 81.124 do `DAT2D.BIN`, no caso. É o
que faz a recusa acima ser uma **decisão** e não uma falha de leitura
disfarçada de guarda.

**A mensagem de recusa nomeia o problema real**, e isso é tão importante quanto
a recusa: o erro que ela pega é "você abriu o disco inglês", e uma exceção que
só diga "digest mismatch" manda o leitor olhar o parser.

```text
/BIN/DAT2D.BIN: read 4a4d6a4f… from we2002-english.bin, expected 0e914e58….
  /BIN/DAT2D.BIN differs between the Japanese original and the English
  translation patch, and textures and palettes may only be read from the
  Japanese one.  Point WE2002_LOOKS_IMAGE at it; WE2002_LOOKS_DRIVE_IMAGE is
  the disc you drive, not the disc you read.
```

**A chave é o digest do arquivo, não o da imagem**, de propósito: dois dumps da
mesma release podem divergir na cauda e trazer os mesmos assets, e um patch de
tradução pode manter o tamanho do disco e trocar exatamente este arquivo — que
é o que acontece aqui.

**E a guarda só vale porque não há outro caminho de leitura.** Função que recusa
não impede nada se o chamador puder não chamá-la. O `iso_source.py` (§3.2,
[`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md)) é a
**única** porta de leitura de disco do projeto, e passa **todo** arquivo pelo
`require()` antes de devolver bytes — não por disciplina de quem escreve o
chamador. Quem precisar dos bytes sem conferência (comparar dois discos é o caso
legítimo, e é o que o `--check-discs` faz) usa função separada e nomeada —
`Disc.read_unchecked()` —, para o desvio aparecer no `grep`. Sem essa metade esta seção descreve uma função; com
ela, descreve uma garantia.

---

## 5. Estratégia de verificação

Este projeto é privilegiado: ao contrário do de PES2, que abriu sem oráculo
nenhum, aqui **o jogo roda instrumentado**. São quatro níveis, e o quinto diz o
que não tem como ser conferido.

### 5.1 A contagem fecha

O `MODEL.BIN` percorrido tem de dar **106 seções terminando em 64.800**, e o
`EDT_MOD.BIN` **11 terminando em 36.072**. É a asserção mais barata do plano e
pega qualquer erro de tamanho de primitiva ou de vértice: errar 24 por 20
desalinha na primeira seção e o fim não bate.

### 5.2 A RAM bate com o disco

`EDT_MOD.BIN` em `0x8011C000` e `MODEL.BIN` em `0x8016E800`, byte a byte. É
reconferível a qualquer momento por MCP, e é o que amarra "o que eu li do
arquivo" a "o que o jogo está desenhando".

### 5.3 O emulador é o gabarito vivo

O ciclo: escolher uma tupla de LOOKS na tela do jogo por `press_button`,
capturar o quadro por `take_screenshot`, renderizar a mesma tupla no nosso
visualizador, e comparar. A diferença **não precisa ser zero** — resolução,
filtro e câmera diferem —, mas precisa ser **medida, registrada e explicada**.
Um número que ninguém olhou não é verificação.

### 5.4 Os 50 renders do Superpack

`We2002\MCR\We DB - polipoli\Faces\` tem **50 JPGs**, dos quais **49 nomeados
pela tupla exata**: `A-I3-A-F-A` é pele A, cabelo I3, cor A, barba F, cor de
barba A. O quinquagésimo se chama `0.jpg` e não tem tupla no nome — conferido
em 2026-09-14, e a decisão sobre ele é da
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md), que
ganhou a linha. **O caminho é relativo a `Superpackv6\We2002\`** e não à raiz
da coletânea, como toda citação `MCR\…` deste plano (§2). É
corpus independente, produzido por outra pessoa, com rótulo. Serve para pegar
erro sistemático que o confronto com o emulador não pegaria por estar usando o
mesmo caminho de código dos dois lados.

### 5.5 Controle negativo

Pelo molde do `tools/mcr/controls.py`: cada guarda ganha uma injeção que a faz
ficar **vermelha**, plantada por substituição literal numa cópia da árvore.
*Guarda que nunca ficou vermelha é decoração.* Os primeiros três, óbvios:
trocar 24 por 20 no tamanho de primitiva; inverter a ordem da lista de
montagem; trocar uma paleta por outra.

### 5.6 O que não tem oráculo — dito antes de começar

1. **A pose.** O boneco da tela está numa pose de animação, e a animação está no
   `ANIME.BIN`, fora de escopo. Nosso render será em pose neutra, e por isso a
   comparação da §5.3 nunca vai bater pixel a pixel.
2. **A câmera.** O jogo escolhe enquadramento por campo — fecha no rosto em
   `SKIN` e `HAIR`, abre o corpo em `BODY`. Reproduzir isso é adivinhação até
   alguém achar a tabela; a v1 usa câmera orbital livre.
3. **`NAT` e `AGE`.** Provavelmente não afetam a geometria. "Provavelmente" é a
   palavra certa até a Fase 2 medir — e medir é barato.

---

## 6. As incógnitas, em ordem de risco

**(a) O que são os quatro TMDs texturizados de `0x00168xxx`.** São TMD Sony de
verdade, fixados, texturizados, e não pertencem a nenhum dos dois arquivos de
modelo. Ou o boneco da tela é montado a partir deles — e aí o `EDT_MOD.BIN` é
outra coisa —, ou eles são o cenário/UI e o boneco vem mesmo do `EDT_MOD.BIN`.
**Nada de geometria deve ser escrito antes de responder isto**, e a resposta é
uma corrida de `diff_memory` trocando `HAIR` na tela.

**(b) Qual peça é qual.** Onze seções, cinco pares e uma sozinha. Nomeá-las
pelo tamanho é palpite; nomeá-las trocando a opção no jogo e vendo qual muda é
medição.

**(c) A tabela de montagem.** O que liga `HAIR = B3` à peça e à paleta certas.
É o coração do projeto e a fase mais cara.

**(d) Pele: paleta ou cor de vértice?** A GPU diz 4-bit CLUT; o formato de seção
diz cor por vértice, sem UV. Os dois não podem estar certos para a mesma
geometria. Decidir isto decide metade da Fase 3.

---

## 7. Fases

| Fase | O que fecha |
|---|---|
| 0 | Abertura: linhagem no `NOTICE.md`, `work/venv-looks/`, e a guarda que recusa ler textura do disco errado |
| 1 | Leitor e formato: `iso_source`, `section`, `modelfile`; as duas varreduras terminando no EOF, com controle negativo |
| 2 | **A incógnita (a) e a (b)**: o que o jogo desenha, e qual peça é qual — por `diff_memory` e troca de opção na tela |
| 3 | Texturas: a lista de CLUTs que falta no `DAT2D.BIN`, a contradição 8 × 3.568 resolvida, e a incógnita (d) |
| 4 | A tabela de montagem: campo de LOOKS → peça + paleta, os 32 cabelos e as 4 peles |
| 5 | Render: `QOpenGLWidget`, câmera orbital, uma tupla na tela |
| 6 | Confronto: nosso quadro × emulador × os 50 JPGs, com a diferença medida |
| 7 | Gates no `ctest`, `perfil-looks.md`, `NOTICE.md` |

### O que não pode ser pulado

- **Fase 2 antes da 4.** Tabela de índice escrita contra peça não identificada
  produz mapeamento plausível e errado — é exatamente a armadilha das oito
  listas de nome de time do PES2 (§6.1 do
  [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md)), onde casar por índice gravava no
  time errado e a tela parecia certa.
- **Fase 1 antes de tudo.** Sem a varredura fechando no EOF, qualquer peça lida
  pode estar deslocada e ainda assim renderizar algo que parece um corpo.
- **A incógnita (a) antes da Fase 3.** Não adianta caçar paleta para uma
  geometria que talvez não seja a que está na tela.
- **A Fase 0 antes de qualquer leitura de textura.** É ela que planta a guarda
  contra ler paleta do disco inglês, e esse erro não tem sintoma (§1.3).

---

## 8. Armadilhas conhecidas

1. **A varredura ingênua morre na seção 55 do `MODEL.BIN`** e parece formato
   errado. É o par de zeros entre grupos (§1.4).
2. **O `EDT_MOD.BIN` é contíguo do 216 ao EOF**, e são **20** seções em duas
   listas de onze (§1.5). Esta armadilha dizia o contrário até 2026-09-14
   ([`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md)). O que quebra é
   começar em 0 ou em 8 — cabeçalho e listas —, e o que engana é começar em
   15.704: também fecha no EOF exato, lendo metade do arquivo.
3. **A ordem da lista não é a ordem do arquivo** (§1.5). Assumir a do arquivo
   embaralha peça sem sintoma.
4. **`MSYS_NO_PATHCONV=1`** ou o caminho de dentro do ISO vira caminho Windows,
   com mensagem de erro que culpa a coisa errada (§4.2).
5. **18 dos 105 `TEX_*.BIN` são form 2** na `golden-european-deluxe.bin`, e o
   `iso.py` os recusa. Não alcança os dois arquivos de modelo, alcança uniforme.
6. **`bin_archive.py` não acha a lista de CLUTs do `DAT2D.BIN`** e responde
   `0 clut(s)` sem reclamar (§1.7). Ler isso como "não tem paleta" é erro.
7. **A tabela de texto é Shift-JIS full-width**, não ASCII (§1.10).
8. **O jogo acha arquivo por LBA fixo, não por nome.** Não há `CdSearchFile`, e
   por isso crescer arquivo é impossível e rebuild de ISO é errado — não só
   caro (§2 do [PLAN-FEATURES.md](/docs/PLAN-FEATURES.md)).
9. **`roms/` são os originais.** Cópia sempre, mesmo em leitura.
10. **Dois discos, e cada um serve para uma coisa** (§1.3). O inglês tem os
    menus legíveis e geometria idêntica, então é o de dirigir; o `DAT2D.BIN`
    dele **difere**, então textura e paleta só se leem no japonês. O erro aqui
    é silencioso: o offset existe nos dois e entrega gráfico diferente.
11. **As duas imagens japonesas são o mesmo dump** —
    `roms/japanese-shift-jis.bin` e `we-2002-original-japao.bin`, mesmo
    `sha256 e853eb14…`. Nomes diferentes não significam imagens diferentes, e
    conferir custou um `sha256sum`.
12. **`numpy` não está instalado** nesta máquina, e a decisão de instalar é do
    dono. Por isso o render vai para a GPU via `QOpenGLWidget`, e nenhum
    rasterizador em Python puro é previsto.
13. **Uma tecla de cada vez no emulador.** `Return`/`Circle` em laço fecha a
    caixa seguinte junto; a regra está no [CLAUDE.md](../CLAUDE.md) e custou uma
    corrida inteira no ciclo `wte/`.

---

## 9. Entregáveis

- Os módulos da §3.2, em `tools/looks/` e `tools/looks/ui/`.
- **Três alvos** em `tests/CMakeLists.txt`, na convenção de brackets já usada:
  um que não precisa de nada, um com `SKIP_RETURN_CODE 77` e variável de
  ambiente, e um de UI sob `if(UNIX AND Python3_FOUND)`.
- Os controles negativos, contados pela ferramenta e nunca escritos em prosa.
- [NOTICE.md](../NOTICE.md) com a linhagem do `we3d` (MIT, com crédito) e a
  ressalva do Superpack.
- O ciclo `docs/tasks/looks/` com `progresso.md` e
  `/docs/prompts/perfil-looks.md`.
- Este plano, mantido: **o que a execução mudar, muda aqui, na seção que
  mudou.**
