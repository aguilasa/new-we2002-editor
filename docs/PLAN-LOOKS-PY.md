# Plano — visualizador 3D da aparência do jogador, em Python + Qt

> **Estado: as oito fases executadas, e o ciclo fechado em 2026-09-17** pela
> [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md). Este
> banner dizia *"plano escrito em 2026-09-14, nenhuma fase executada"*. O que a
> execução mudou está **na seção que mudou**, com a data e o que ela dizia
> antes; o índice dessas mudanças são as tasks e as `CORR-LOOKS-*` que cada
> seção cita. O que ficou aberto está na §6, com a razão e o que destravaria
> cada item; a definição de pronto da §0 foi percorrida item a item, com o
> resultado ao lado.
>
> **E reaberto em 2026-09-17 para a v2**, a pedido do usuário: a **tela
> `LOOKS SET`** do jogo, com as linhas que trocam pele, cabelo e o resto, e o
> boneco **montado**, **vestido** e **andando** dentro dela. O escopo, as
> incógnitas e as fases estão na §10; as tasks são as `LOOKS-TASK-21` a `35`,
> no mesmo ciclo.
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
  **Revogado para a v2 em 2026-09-17**, por decisão do usuário: animar a
  caminhada da tela `LOOKS SET` passou a ser objetivo, e é a §10. A v1 fechou
  como estava escrito aqui; o que continua valendo para a v2 é o resto desta
  lista — não grava, não toca `roms/`, não estende o `we2002_core`.
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
3. `python tools/looks/ui/app.py --screenshot out.png --looks A-I3-A-E-A`
   produz um boneco reconhecível, com a pele e o cabelo daquela tupla — **e**
   `--looks A-H1-A-A-A` **recusa**, com a mensagem da tabela e saída **2**. As
   duas metades são o critério. A **tela** do `FACE` oferece **sete** valores,
   `A` a `G`, andada letra a letra nos dois slots pela
   [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md), e a
   **tabela** sabe aplicar os sete: `A` a `E` são as faixas 0 a 4 dos dois
   quads de barba que a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)
   mediu, e `F` e `G` desenham o **gêmeo** da cabeça — a seção ímpar seguinte
   —, com os quads de barba dele na faixa do disco e uma adiante
   ([`CORR-LOOKS-048`](/docs/tasks/looks/CORR-LOOKS-048.md)). A metade que
   recusa é o `H1`, que não escreveu nada nas duas figuras.

   **Este item pedia a recusa de `A-I3-A-F-A` até 2026-09-16.** Ela era honesta
   enquanto ninguém tinha lido `F` e `G` — a recusa dizia "não medido" desde a
   [`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md), e antes disso
   "fora de alcance" —, e dezesseis das cinquenta tuplas do corpus caíam nela.
   Medido, `A-I3-A-F-A` **desenha**; a recusa que continua sendo critério é a
   de um estilo que não escreveu nada, e desenhar um `A1` calado no lugar de um
   `H1` é a falha que este projeto existe para não cometer.
   `scene.py --corpus` passou de **31 desenhadas e 19 recusadas** para
   **47 e 3**: as duas de `H1` e o `0.jpg`.
4. `ctest -R looks` numa máquina limpa: **1 passed, 3 skipped**. Dizia *2
   skipped* até 2026-09-17, quando a
   [`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) registrou o
   quarto alvo, `looks_live` (§4.4).
5. O confronto da §5.3 roda: nosso quadro contra o quadro do emulador na mesma
   tupla, com a diferença medida e registrada — não necessariamente zero, mas
   **medida e explicada**.

#### A definição de pronto, percorrida em 2026-09-17

Pela [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md),
item a item, com a ferramenta de cada um:

| item | resultado | medido por |
|---|---|---|
| 1 | **cumprido.** `EDT_MOD.BIN` a partir de 216: 20 seções, 1.218 vértices, 1.074 primitivas, para em 36.072, o fim do arquivo; `MODEL.BIN` a partir de 1816: 106 seções, 2.461, 1.767, para em 64.800, o fim do arquivo | `cli.py sections` |
| 2 | **cumprido.** As onze de cada lista nomeadas, e o jogo concorda | `pieces.py --check-image`, dentro do `cli.py check` |
| 3 | **cumprido na metade que o item mede, com uma ressalva na palavra "boneco".** `A-I3-A-E-A` sai 0 e grava o PNG; a cabeça traz a pele, o cabelo e a barba da tupla, olhada. `A-H1-A-A-A` recusa com a mensagem do `assembly.HAIR_MAP` e sai **2**. O que a imagem **não** é: um boneco montado. As peças saem numa prateleira, porque a pose não está em arquivo lido (§6 (e)), e 237 primitivas saem sem textura, porque as páginas delas são dos `TEX_*.BIN` (§6 (f)) | `ui/app.py --screenshot --looks` |
| 4 | **cumprido.** 1 passed, 3 skipped numa máquina limpa, os quatro alvos listados pelo nome | `ctest -R looks`, no Log da LOOKS-TASK-20 |
| 5 | **cumprido.** Os dois slots se repetem pixel a pixel a partir do `load_state`; cinco tuplas pontuadas e uma recusa em cada: 3 `win`, 2 `ranked`, 0 sem explicação; e a display list decide a diagonal pela ordem guardada | `confront.py --score` |

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

E duas correções ao formato da primitiva, medidas na mesma corrida — a primeira
delas **revista uma segunda vez** em 2026-09-14:

- **Os dezesseis primeiros bytes não são quatro cores.** São quatro pares
  `(u, v)` mais um CLUT id e uma página de textura, na ordem do `POLY_FT4` do
  hardware. Esta seção dizia outra coisa: *"o quarto byte de cada cor não é
  `pad` — é um byte de modo por primitiva, guardado na primeira cor"*, com a
  observação de que na cor 0 ele é 120, 121, 122 ou 127 e nas outras três é
  sempre zero. **A observação estava certa e a conclusão errada:** aqueles
  valores são `0x78..0x7F`, o byte **alto do CLUT id**, e o "sempre zero" das
  outras três é o que o pacote da GPU manda zerar. A leitura inteira, com as
  três medições que a sustentam, está na §1.6, que era a contradição que ela
  resolve; quem a reescreveu foi a
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md).

  Vale o registro de **por que a primeira leitura resistiu**: ela vinha do
  `we3d`, batia com uma estatística real, e nada no parser dependia de estar
  certa. Só o jogo, reescrevendo esses bytes ao vivo, desempatou.
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

**E as posições da tabela abaixo têm nome desde 2026-09-15** (§6, incógnita
(b)): 0 é o tronco; 1 e 3 os braços, 2 e 4 os antebraços; 5 e 8 as coxas, 6 e 9
as pernas, 7 e 10 os pés — que são justamente as duas compartilhadas, porque os
dois bonecos calçam a mesma chuteira. A **lista A é o jogador de linha e a
lista B é o goleiro**, medido pela LOOKS-TASK-08.

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
  contagens de **dois** dos cinco pares — `30/24` e `80/78` na A contra `40/34`
  e `88/86` na B —, e duas peças são **literalmente a mesma seção**.

  **Mesma forma não é mesma malha, e a diferença é de dois pares e só deles.**
  Comparadas posição a posição pelo `pieces.py --check-image`, que imprime a
  conta desde 2026-09-15
  ([`CORR-LOOKS-021`](/docs/tasks/looks/CORR-LOOKS-021.md)):

  ```text
  pos  0:  0 vs 11  same size, 505 of 2384 byte(s) differ, 2 of them vertex
  pos  1:  1 vs 12  DIFFERENT MESH  30/24 vs 40/34 vert/prim, 824 vs 1144 byte(s)
  pos  2:  3 vs 14  DIFFERENT MESH  80/78 vs 88/86 vert/prim, 2520 vs 2776 byte(s)
  pos  5:  5 vs 16  same size, 250 of 2000 byte(s) differ, 22 of them vertex
  pos  6:  7 vs 18  same size, 240 of 1168 byte(s) differ, 0 of them vertex
  pos  7: section 9 is SHARED by both lists
  ```

  Ou seja: **braço e antebraço são malha diferente** — manga comprida contra
  manga curta —, o tronco difere em **2** bytes de vértice, a coxa em **22**, e
  a perna em **nenhum**. O goleiro é o mesmo esqueleto com **duas peças
  remodeladas**, não um remapeamento de textura do jogador de linha. Quem
  escrever montagem lendo "mesma forma" como "mesma malha" carrega uma malha só
  e desenha o goleiro com o braço errado; o `mesh_agrees()` do `pieces.py`
  recusa se essa correspondência deixar de valer.
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

#### O cabeçalho do `MODEL.BIN`: 18 listas, o slot vazio, e **duas** corridas

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
`0x80`, e essas entradas miram **duas** corridas diferentes — remedido em
2026-09-14 pela
[`CORR-LOOKS-013`](/docs/tasks/looks/CORR-LOOKS-013.md), que achou esta seção
dizendo *"mirando o offset 104"* no singular:

```
open with tag 0x80        : 16 of 18
open with (0x80 -> 104)   : 12 of 18      corrida de 64 ponteiros
open with (0x80 -> 232)   :  4 of 18      corrida de 32 ponteiros
```

```
secao em 104?  nao -> claims 2148999984 vertices and 2149000600 primitives
words em 104:  80172330 80172598 80172800 80172b30 ... -> 15152 15768 16384 17200 ...
words em 232:  8017aac0 8017aac0 8017ac40 8017ac40 ... -> 49856 49856 50240 50240 ...
```

As duas são **corridas de ponteiros KSEG0 crus** — sem tag, sem terminador —,
uma **terceira forma** de tabela neste arquivo, e nenhuma das duas é seção.
Logo `min` sobre **todos** os alvos responde 104, e o `geometry_start()`
entregaria a uma varredura um início dentro da tabela de ponteiros: exatamente a
falha que derivar o início existe para impedir. Por isso o
`layout.is_derivable()` recusa este arquivo.

**Mas as listas declaram o 1816.** As outras duas do cabeçalho têm **uma
entrada só**, com tag `0x02`, e essas nomeiam seção:

```
  list@72  n=1  first=(0x02 -> 1816)     1816: SECTION 107 vert  88 prim, ends 4792
  list@88  n=1  first=(0x02 -> 4792)     4792: SECTION  50 vert  48 prim, ends 6352

min target with tag 0x02: 1816   (144 entradas nas 16 listas distintas, 58 alvos)
min de todos os alvos   : 104
```

Esta seção dizia que o 1816 é *"fato medido e não algo que as listas declarem"*,
e as listas o declaram. O `MODEL_GEOMETRY_START` fica por ser barato e porque a
derivação por tag `0x02` não foi exercitada em nenhum segundo arquivo — não por
a informação faltar. Motivo falso é o que impede alguém de reabrir a questão
com dado na mão.

**O que fica aberto, e quem responde.** Ninguém mediu o que essas **duas**
corridas agrupam, nem por que são duas, de 64 e de 32 ponteiros. Se a incógnita (a) concluir que o boneco vem do `MODEL.BIN`, é ela que
diz **qual** dos modelos de lá — e é onde a hipótese do `we3d`, de 14 jogadores
de 11 peças, se confere. A linha está escrita na
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md).

**Veredito de 2026-09-17, na reconciliação
([`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md)):
continua aberto, e deixou de ser pergunta do visualizador.** A incógnita (a)
concluiu que o boneco vem dos **dois** arquivos: do `MODEL.BIN` só a cabeça, e
qual cabeça é escolhida pelo `HAIR` entre as seções do bloco 24..55 (§6 (c)).
Nenhuma medição do ciclo leu as duas corridas nem conferiu os 14 jogadores, e
nada no código depende deles — a hipótese do `we3d` fica como ele a escreveu,
não confirmada. Destravaria: um breakpoint de leitura nas duas corridas, com a
tela mudando de time.

### 1.6 A primitiva **tem** UV — a contradição era de leitura

Esta seção se chamava *"A tela desenha com textura, e o formato de seção não tem
textura"* e descrevia a contradição de maior risco do plano. Ela foi **resolvida
em 2026-09-14** pela
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md), e não havia
contradição nenhuma: o que estava errado era a leitura da primitiva, herdada da
análise do `we3d`.

O que a seção media continua valendo, e é o lado direito da conta. Com o jogo na
tela `LOOKS SET`, `get_gpu_state --aspect draw` responde
**`texture_color_mode: "4-bit CLUT"`**, `texture_disable: false`. **Isso é uma
amostra de um desenho num instante, e não generaliza para o arquivo** — ver a
profundidade por página logo abaixo.

O que estava errado é o lado esquerdo. A primitiva de 24 bytes **não** é
*"gradation, no-texture"* — ela é a metade de textura de um `POLY_FT4` do
hardware, com os campos na ordem em que o pacote da GPU os põe:

```text
bytes  0, 1   u0, v0        bytes  2, 3   CLUT id      (u16)
bytes  4, 5   u1, v1        bytes  6, 7   texture page (u16)
bytes  8, 9   u2, v2        bytes 10, 11  zero
bytes 12, 13  u3, v3        bytes 14, 15  zero
bytes 16..23  quatro índices de vértice u16
```

Três medições independentes concordam, e cada uma sozinha seria fraca:

1. **Nos 2.841 primitivas dos dois arquivos**, os bytes 10, 11, 14 e 15 são zero
   **todas as vezes**. É a forma do pacote; quatro cores independentes não teriam
   por que zerar sempre os mesmos quatro bytes.
2. **O "mode byte"** que a leitura anterior guardava — sempre 120, 121, 122 ou
   127 na cor 0, sempre zero nas outras três — é o byte **alto do CLUT id**:
   `0x78..0x7F`, linhas de paleta perto de y=480 na VRAM. E a palavra em 6..7 é
   `0x18`, `0x1A` ou `0x99` — páginas de textura em VRAM (512, 256), (640, 256)
   e (576, 256). **A primeira é o gráfico do `DAT2D.BIN` no offset 8**, que é a
   entrada que a tabela do CARP chama de *"Pelos Cuerpos y botines"* (§1.7).
3. **O jogo, perguntado ao vivo, mexe exatamente nesses campos**: trocar `SKIN`
   anda o byte baixo do CLUT de `0x40` em `0x40`, quatro valores ao todo;
   trocar `HAIR` anda `v` de `0x20` em `0x20`. Paleta e faixa do atlas — não
   recoloração.

**A palavra de página traz mais do que a posição: os bits 7-8 são a
profundidade da CLUT**, e as três páginas **não concordam**. Contado sobre os
dois arquivos em 2026-09-15 ([`CORR-LOOKS-018`](/docs/tasks/looks/CORR-LOOKS-018.md)),
pelo `section.py` commitado:

| `tpage` | VRAM | profundidade | `EDT_MOD.BIN` | `MODEL.BIN` | total |
|---|---|---|---:|---:|---:|
| `0x0018` | (512, 256) | **4 bits** | 408 | 1.258 | 1.666 |
| `0x001A` | (640, 256) | **4 bits** | — | 136 | 136 |
| `0x0099` | (576, 256) | **8 bits** | 666 | 373 | **1.039** |

São **1.039 de 2.841 primitivas — 36,6% — amostrando em CLUT de 8 bits**, e no
`EDT_MOD.BIN` elas são a **maioria**: 666 de 1.074. A semitransparência (bits
5-6) é zero nas três.

**Isso decide a largura da paleta**, e é por isso que está aqui e não num
comentário: CLUT de 4 bits tem 16 entradas (32 bytes), a de 8 bits tem 256 (512
bytes). Uma varredura de paletas que assuma dezesseis lê um dezesseis avos da
que existe e acha paleta onde não há — sem mensagem nenhuma. O
`Primitive.tpage_depth` e o `tpage_abr` carregam a leitura, e o `self_check()`
afirma as duas profundidades.

**E os quatro TMDs de `0x00168xxx` não existem nos dois save states.** Medido por
`python tools/looks/oracle.py --tmds`: os quatro endereços que esta seção
registrava estão **zerados** nos dois slots. Os TMDs que de fato vivem na RAM
dessa tela são **29**, entre `0x800C1678` e `0x800C4948`, de 4 a 54 vértices, e
**nenhum campo de LOOKS toca um deles**.

**Essa última frase é medição, e é o mesmo comando que a faz.** Desde
2026-09-15 ([`CORR-LOOKS-019`](/docs/tasks/looks/CORR-LOOKS-019.md)) o `--tmds`
percorre cada TMD **até o fim** — cabeçalho, tabela de objetos, vértices e os
pacotes de primitiva, que são de tamanho variável — e depois mexe em campo,
cruzando o resíduo do `field_diff()` com esse mapa:

```text
TMDs actually in RAM: 29
    from 0x800c1678 to 0x800c4948, 4..54 vertices
    walked to their ends: 96..896 byte(s) each, 13104 byte(s) of RAM in all
HAIR, slot 1 (goalkeeper): 132 byte(s)
    in a TMD: 0 byte(s)
    in neither: 124 byte(s)
SKIN, slot 2 (outfield player): 326 byte(s)
    in a TMD: 0 byte(s)
    in neither: 202 byte(s)
```

O `--fields` imprime os mesmos **três** baldes. Antes eram dois — arquivo de
modelo e "fora" —, e *"fora dos arquivos de modelo"* não é *"fora dos TMDs"*:
a metade negativa do veredito era leitura de dois relatórios que não se
cruzavam.

Os quatro de 92/261/30/18 vértices foram
medidos numa sessão que não se reproduz a partir dos states, e **nada deste ciclo
pode ser construído sobre eles** — continuam registrados aqui como o que foram, e
o `layout.TMD_CLAIMED` carrega a mesma ressalva ao lado dos endereços.

### 1.7 As texturas de aparência moram no `DAT2D.BIN`, e a lista de paletas — ACHADA

```sh
MSYS_NO_PATHCONV=1 python tools/pes2/bin_archive.py ls \
  roms/japanese-shift-jis.bin --file /BIN/DAT2D.BIN
#  /BIN/DAT2D.BIN   81124 B   23 image(s), 0 clut(s)
```

*O título desta seção dizia "e falta a lista de paletas" até 2026-09-17; a
lista foi achada em 2026-09-15, abaixo.*

As 23 imagens saem inteiras, com as coordenadas de VRAM que o modelo vai
precisar. O que o `bin_archive.py` imprime de cada uma é
`128x128 px 4bpp / 64x128 8bpp`, e as duas leituras são do mesmo bloco de 8.192
bytes: **qual delas vale depende da profundidade da página que a amostra**, que
a §1.6 mede primitiva a primitiva. Esta seção dizia "128×128 a 4 bpp cada" até
2026-09-15, e isso decidia por conta própria uma coisa que a geometria já
respondia de outro jeito
([`CORR-LOOKS-018`](/docs/tasks/looks/CORR-LOOKS-018.md)).

**E duas das três páginas que a geometria nomeia não têm entrada aqui.** Em
y=256 o `DAT2D.BIN` ocupa (512, 256), (544, 256), (896, 256) e (928, 256) —
nada em (576, 256) nem em (640, 256).

**São 1.039 primitivas amostrando de fora deste arquivo, e não 1.175** — medido
em 2026-09-15 pelo `atlas.py --check-image`
([`CORR-LOOKS-024`](/docs/tasks/looks/CORR-LOOKS-024.md)). A diferença são as
**136** primitivas da página `0x1A`, e ela ensina a regra que a Fase 4 vai
precisar: **o que resolve um registro é o texel, não a base da página**. Uma
página de 4 bits cobre 256 texels e as imagens do arquivo têm 128, então um `u`
alto atravessa para o registro seguinte. Essas 136 são das seções **0 e 1 do
`MODEL.BIN`**, com `u` 130..186 e `v` 130..187 — VRAM x 672..686, y 386..443,
**dentro** do registro em 10.248 (672, 384), que a §1.8 lista como a terceira
imagem que a geometria amostra. Contar por base de página as dava como
ausentes.

As três primeiras são as que interessam, segundo a tabela do CARP
(`Offsets\Offsets WE2002 - CARP\Dat\DAT2D.BIN.txt`):

| offset | VRAM | rótulo do CARP | o que foi medido |
|---:|---|---|---|
| 8 | (512, 256) | *"Pelos Cuerpos y botines"* | **não é o cabelo** — §1.8 |
| 3.568 | (544, 256) | *"Caras"* | **cabelo e rosto**, os dois — §1.8 |
| 7.456 | (512, 384) | *"Cuerpo"* | sem veredito |

A coluna do meio é **transcrição** do rótulo de terceiro, que é o objeto do
confronto, e nada mais: a tradução *"cabelos, corpos e chuteiras"* que esta
tabela trazia ao lado do 8 é exatamente a leitura que a §1.8 derrubou em
2026-09-15 ([`CORR-LOOKS-024`](/docs/tasks/looks/CORR-LOOKS-024.md)). Quem lia
esta seção e parava aqui saía com a resposta errada da contradição que a seção
seguinte resolve.

**O `0 clut(s)` era verdade sobre o varredor e mentira sobre o arquivo — medido
em 2026-09-15** pela
[`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md). Esta seção
dizia que o `entries()` do `bin_archive.py` "não acha a lista de paletas deste
arquivo", e a lista está lá: **267 registros**, do offset 76.836 até o fim do
arquivo. O que a esconde é uma palavra do registro, que o
`tools/pes2/bin_archive.py` documenta assim:

```text
[7] 0x800f    a constant tag, and the thing that makes the record
              findable without knowing where the list is
```

**Não é constante e não é tag.** É o **banco de 64 KiB** do offset de 16 bits do
campo 6, com viés para que o banco 0 valha `0x800f`:

```text
offset = campo[6] + (campo[7] - 0x800F) * 0x10000
```

A prova não é a aritmética — é o que cai no endereço resolvido. Com o banco, o
fluxo LZSS de cada registro de imagem descomprime **exatamente** para o
retângulo que o próprio registro declara; sem ele, não:

| arquivo | bytes | campo 7 | banco | imagens que descomprimem para o retângulo declarado |
|---|---:|---|---:|---|
| `DAT2D.BIN` | 81.124 | `0x800f` | +0 | 23 de 23 |
| `DATSEL3.BIN` | 65.884 | `0x800f` | +0 | 20 de 20 |
| `EDTR_2D.BIN` | 73.856 | `0x8010` | +1 | 2 de 2 |
| `DATSEL2.BIN` | 124.812 | `0x8010` | +1 | 15 de 15 |
| `DAT_CG.BIN` | 101.416 | `0x8010` | +1 | 9 de 9 |
| `DATSEL.BIN` | 223.496 | `0x8012` | +3 | 6 de 6 |

A constante `0x800f` funciona em todo contêiner cujo payload cabe nos primeiros
64 KiB. **Nos discos de PES2 isso não é todo contêiner** — medido em 2026-09-17
pela [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md),
numa cópia da `(EsIt)`. Esta frase dizia *"que é todo contêiner dos quatro
discos da família PES2 que o outro projeto mediu. Ela nunca esteve errada lá"*,
e a própria seção, parágrafos abaixo, dizia o contrário:

```text
$ python tools/looks/texture.py --survey "<copia>/…(Es,It) (Track 1).bin"
  the sweep as it stands: 1828 record(s) in 144 file(s)
  a fixed tag word would find 1750 -- so reading the bank as a bank costs 78 record(s) in 5 file(s)
      outside /BIN/DAT2D.BIN: 78 record(s) in 5 file(s) -- DAT_CG.BIN 39, ENDCSR.BIN 16, EDTR_2D.BIN 11, DATSEL_I.BIN 7, DATSEL2I.BIN 5

$ python tools/pes2/bin_archive.py ls "<copia>/…(Es,It) (Track 1).bin" --file /BIN/<X>.BIN
/BIN/DAT_CG.BIN          101124 B   0 image(s), 0 clut(s)
/BIN/ENDCSR.BIN          136492 B   13 image(s), 0 clut(s), 1 of another kind
/BIN/EDTR_2D.BIN          98240 B   0 image(s), 0 clut(s)
/BIN/DATSEL_I.BIN        214232 B   0 image(s), 0 clut(s)
/BIN/DATSEL2I.BIN        143848 B   0 image(s), 0 clut(s)
```

Quatro contêineres de PES2 **inteiros** fora do índice, e um em parte. A dívida
está registrada no [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md), na seção do
índice do contêiner; o conserto é decisão do usuário.

**O que o arquivo guarda, e como se sabe que a leitura fechou.** A lista de
imagens termina em 65.878; o banco de paletas começa em **65.892**, depois de
catorze bytes de zero. Dali até 76.836 os payloads **ladrilham exato** —
**262 paletas de 16 entradas e 5 de 256**, que dão 10.944 bytes, e
65.892 + 10.944 = 76.836, onde a lista de CLUTs começa. **A conferência é o
ladrilho, não o offset:** uma resolução errada por um banco, ou uma largura lida
na profundidade errada, deixa buraco ou sobreposição na hora.

As paletas caem na VRAM em três formas, e a geometria usa as três:

| linhas de VRAM | registros | entradas | o que a geometria faz com elas |
|---|---:|---:|---|
| 480, 481, 482, 483 | 1 cada | 256 | as quatro peles |
| 484 | 7 | 256 e 16 | as chuteiras, e seis paletas estreitas ao lado |
| 496 a 511 | 16 cada | 16 | 256 paletas estreitas numa grade 16×16 |

**Um CLUT id de 4 bits pode apontar para DENTRO de uma paleta de 256 entradas**,
e este disco faz isso o tempo todo: a pele nua amostra (0, 480), a cabeça
amostra (16, 480) e (144, 480), e as três são entradas do **mesmo** registro
largo em (0, 480). Então "qual paleta" não é busca por igualdade — é o registro
cujo intervalo **cobre** o id, na largura que a profundidade da página da
primitiva pede. Errar isso é a falha silenciosa desta fase: as dezesseis
entradas erradas continuam sendo dezesseis entradas, e continuam desenhando.

**E um registro de 256 entradas é uma fileira de dezesseis CLUTs de 4 bits**, o
que a §6(d) fechou em 2026-09-15: os três campos de cor da tela são duas
coordenadas dessa grade — `SKIN` anda a linha, `H.COL` e `H.F.COL.` andam a
coluna —, e os três **alcançam** as dezesseis colunas de um registro: 1 janela
de pele nua, 8 de cabelo e 7 de barba.

**Alcance não é identidade, e a diferença tem número.** A conta acima diz para
onde os campos vão; não diz o que cada coluna é. Medido pelo
`skin.py --check-image`: na linha 480, a coluna **1** — *"cabelo 0"* pelo lado
do campo — é onde **948 primitivas de 50 seções do `MODEL.BIN`** repousam, e só
**16** delas são a cabeça. As outras 932 nunca são tocadas por campo de cor
nenhum. E as colunas 2..8 e 10..15 **não têm primitiva nenhuma no disco**: elas
existem como destino de tecla, não como estado gravado. Quem escrever a tabela
de montagem (§4) a partir de *"colunas 1..8 são as oito cores de cabelo"* dá a
932 primitivas uma cor de cabelo que elas não têm, e o boneco **desenha
perfeitamente** ([`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md)).

**A regra do "mais estreito ganha" é a da própria GPU, e isso foi medido.** O
`oracle.py --palettes` compara as **21 linhas de CLUT** deste contêiner contra a
VRAM do jogo parado na tela, resolvendo cada `x` pelo `texture.covering`: **zero
entradas diferentes em todas as 21**. A linha 484 é o caso que decide — seis
registros de 16 entradas ficam **por cima** do de 256 ali, e comparar contra o
largo dá **71** entradas diferentes. O desempate que a LOOKS-TASK-10 escolheu
por elegância é o que o console faz.

Das nove ids distintas que a geometria nomeia, **cinco resolvem neste arquivo e
quatro vêm de outro lugar** — as três de 8 bits em (0, 485), (0, 486) e
(0, 488), que são os uniformes, e uma estreita em (336, 510). É a mesma lacuna
que as duas páginas de textura ausentes já apontavam, agora com as paletas
juntas.

**E ela fechou em 2026-09-15**, pela
[`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md), com
`python tools/looks/atlas.py --elsewhere` varrendo os 235 contêineres do disco:

| o que falta aqui | quem tem |
|---|---|
| VRAM (576, 256), (576, 384) e (608, 256) | **105 `TEX_*.BIN`** (mais `DATSEL2.BIN` e `SELECT2.BIN` em duas delas) |
| CLUT (0, 486) e (0, 488), 256 entradas | **105 `TEX_*.BIN`, duas de cada id por arquivo** |
| CLUT (0, 485) e (336, 510) | **contêiner nenhum deste disco** |

A resposta é uma frase: **o uniforme é por time**, e por isso não mora no
arquivo comum — mora nos 105 contêineres de textura de time.

**Cada `TEX_*.BIN` tem cinco paletas de 256, não duas** — duas em (0, 486),
duas em (0, 488) e uma em **(256, 480), que a geometria não nomeia** —, o mesmo
nos 105. Esta seção dizia "as duas paletas de 256 por arquivo", lendo o `x2` do
`--elsewhere` como o total do arquivo; medido em 2026-09-15
([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)), o `x2` é quantas
respondem àquela id. O comando imprime as duas contagens uma linha abaixo da
outra desde então.

**E "casa e fora" é hipótese, não medição.** Ninguém trocou o uniforme do time
na tela para ver qual das duas de uma id se move, que é o método da
LOOKS-TASK-09 — e é o que a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md)
vai precisar, porque o uniforme é o único campo com **duas candidatas por id**.
A quinta paleta fica como pergunta aberta ao lado.

As duas ids que não estão em lugar nenhum ficam abertas, e a de (336, 510) é
justamente a das 136 primitivas das seções 0 e 1 do `MODEL.BIN`.

**E os dois rótulos do CARP viraram medição, nenhum por confiança:**

- **"Pieles" em 65.892 / 66.404 / 66.916 / 67.428** são os quatro registros em
  VRAM (0, 480) a (0, 483), 256 entradas cada. (A tabela do CARP transcreve os
  oito campos do quarto registro certos e **erra a própria aritmética**:
  escreve 67.248 onde os campos dizem 67.428. Dois dígitos trocados, achado ao
  ler a transcrição em vez de resumi-la, 2026-09-15.) O que confirma não é o passo de
  512 bytes: é que a [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md)
  mediu o `SKIN` somando `0x40` ao CLUT id, que é **exatamente uma linha de
  VRAM**, e que quem ele move são as peças de pele nua.
- **"Botines" em 67.940** é o quinto registro largo, em VRAM (0, 484). A
  confirmação é independente do rótulo: as seções 9 e 10 — as que a
  [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) nomeou pé, por
  espelho e por serem as duas únicas que os dois bonecos compartilham — amostram
  **(0, 484) e mais nada**, e nenhuma outra **peça nomeada** a toca. A
  exclusividade vale dentro do `EDT_MOD.BIN`, que é onde moram as peças
  nomeadas: **seis seções do `MODEL.BIN` — 11, 12, 22, 23, 63 e 64, cinco
  primitivas cada — também amostram (0, 484)**, e `112 + 30 = 142` fecha o total
  que o `--check-image` imprime para esse id
  ([`CORR-LOOKS-023`](/docs/tasks/looks/CORR-LOOKS-023.md)). Quem são essas
  seis é pergunta da Fase 3, e a cabeça não está entre elas.

**O conserto não foi para o `bin_archive.py`, e a razão é de escopo.** Quem lê
as paletas é o `tools/looks/texture.py`, que acha a lista pelo mesmo marcador e
lê o banco do próprio registro. Generalizar o `entries()` para aceitar qualquer
palavra de banco custa **80 registros a mais em cinco contêineres deste disco**
— `DAT_CG.BIN` 41, `ENDCSR.BIN` 16, `DATSEL2.BIN` 15, `DATSEL.BIN` 6 e
`EDTR_2D.BIN` 2 —, **nenhum deles estádio**, medido pelo `texture.py --survey`.
Esta seção dizia *"2.151 em 40, os `GDC_*` incluídos"* até 2026-09-15, e esse
número não reproduzia por leitura nenhuma
([`CORR-LOOKS-022`](/docs/tasks/looks/CORR-LOOKS-022.md)). O que decide é o
escopo: o `bin_archive.py` é o varredor de outro projeto, cujo gate não é
medido aqui, e mexer nele para servir a um arquivo de um quinto disco moveria o
chão de um gate alheio sem entregar nada que o `texture.py` já não entregue.
**A correção do modelo de registro — o campo 7 é banco, não tag — é dívida com o
ciclo de PES2**, onde ela vale para `DAT_CG.BIN`, `DATSEL2I.BIN`, `DATSEL_I.BIN`
e `EDTR_2D.BIN` também — e para o `ENDCSR.BIN`, em parte, que esta lista não
tinha até a medição de 2026-09-17 acima. A
[`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md) a
registrou no [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md).

### 1.8 A contradição da cena — RESPONDIDA: o cabelo é o 3.568

O tutorial de cabelo do `zeta`
(`MCR\Apariencia fisica jugadores\Tutorial para pintar el cabello a jugadores WE2002 - zeta.pdf`)
manda abrir o gráfico no **offset 3.568** para achar os cabelos. A tabela do
CARP rotula o 3.568 como *"Caras"* e o **8** como *"Pelos"*. Os dois não podiam
estar certos.

**Medido em 2026-09-15** pela
[`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md), por
`python tools/looks/atlas.py --check-image`: **o cabelo é o 3.568. O tutorial do
`zeta` está certo; o *"Pelos"* que o CARP põe no offset 8 está errado.**

#### Por que a página decide, e não o olho

Uma página de textura do PSX tem **64 halfwords de VRAM** de largura. A 4 bits
por texel isso são **256 texels**, então o `u` de 0 a 255 atravessa **duas** das
imagens de 32 unidades deste arquivo, lado a lado:

```text
página (512, 256)   u   0..127  ->  VRAM x 512..543  ->  o registro em 8
                    u 128..255  ->  VRAM x 544..575  ->  o registro em 3.568
```

As dezoito primitivas da seção 24 do `MODEL.BIN` — a cabeça, nomeada pela
[`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) — declaram todas
a página `0x0018`, que é essa, a 4 bits. Então a pergunta vira uma subtração:

| campo | primitivas | passo | `u` | registro |
|---|---|---|---|---|
| `HAIR` | 1 e 14 | `v` `+0x20` | 176..199 | **3.568** |
| `FACE` | 8 e 13 | `v` `+0x10` | 152..174 | **3.568** |
| — | as outras catorze | — | 16..62 | 8 |

As primitivas de `HAIR` vêm da [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md);
as de `FACE` foram medidas aqui, nos dois save states. **Nenhum dos dois campos
toca o registro em 8.**

#### Duas testemunhas independentes, e nenhuma é nossa ferramenta

- **O tutorial, lido em vez de resumido:** *"ubiquémonos en el gráfico en el
  offset 3568 ... Tendremos la imagen base de los cabellos"*, e as **32 linhas**
  da tabela dele têm 3.568 em toda a coluna *Gráfico*.
- **A tabela de paletas do mesmo tutorial reproduz o que a LOOKS-TASK-10 mediu**,
  sem ter sido perguntada: as quatro colunas dele são *blanca, amarilla, canela,
  negra* em **65.892 / 66.404 / 66.916 / 67.428** — as quatro "Pieles" da §1.7 —
  e os oito tipos de cabelo andam **32 bytes** dentro de cada uma, que são 16
  halfwords de VRAM, que é exatamente o CLUT id **(16, 480)** que as primitivas
  da cabeça carregam. Duas medições feitas com dezenove anos de distância e
  métodos sem nada em comum chegando ao mesmo lugar.

#### O arquivo com o nome da resposta é a outra imagem

`Caras - zeta/cabellowe2002.bmp` — *"cabelo we2002"*, 128×128 a 4 bits — é
**byte a byte o registro em 8**, e não o cabelo: 100,0% dos índices batem com
esse registro no `DAT2D.BIN` que o próprio `zeta` distribui, e 85,7% no de
fábrica. Contra o 3.568 ele dá **9,2%**, que é *pior* que os 16,4% de chutar o
índice mais comum em toda parte.

**O nulo é o ponto.** Numa folha em que um índice cobre um quinto dos texels,
85,7% só se lê como acerto, e 9,2% só se lê como erro, depois de saber quanto
vale concordar por acaso — e é por isso que o
`python tools/looks/atlas.py --compare` imprime o nulo ao lado de cada linha.
**Nome de arquivo de terceiro é rótulo como qualquer outro**, e este está errado
enquanto o tutorial ao lado dele está certo.

#### O que sobra rotulado por opinião

Das 23 imagens, a geometria amostra **três**: 8, 3.568 e 10.248. As outras
vinte não têm veredito, e o `atlas.py --labels` as imprime pelo que são —
**três** com o rótulo do CARP marcado *scene opinion* e **dezessete** sem
rótulo nenhum, que com as três medidas fecham as 23. A tabela
`DAT2D_SCENE_LABELS` tem seis linhas, mas três delas caem justamente nos
registros já medidos, e opinião sobre o que foi medido deixa de ser o que a
imagem carrega. Esta frase dizia "seis e dezessete" — 6 + 17 = 23 sobre um
conjunto de 20 —, e foi corrigida em 2026-09-15
([`CORR-LOOKS-024`](/docs/tasks/looks/CORR-LOOKS-024.md)). Inclusive
a 10.248, que **136 primitivas** amostram: elas são todas das seções 0 e 1 do
`MODEL.BIN`, nenhuma das doze peças, e "bandeirinha de escanteio e bolas" é o
que o CARP diz, não o que se mediu.

E a tabela do CARP tem um erro de transcrição que vale saber antes de confiar
numa linha dela: a linha 20 lê o próprio hex `D59C` e escreve 23.964, que não é
54.684. O hex está certo e o decimal, errado.

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

**Três campos têm menos rótulo do que valor, e isso não é erro de transcrição:**
`facialhair` e `facialhaircolor` guardam três bits — oito — e têm sete nomes;
`foot` guarda dois e tem três. **O disco concorda**: nos 1.449 registros, a
barba chega a 6, a cor de barba a 3 e o pé a 2, e nenhum passa do último
rótulo. E a tela concorda por um terceiro caminho — a
[`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md) andou
`H.F.COL.` de ponta a ponta e ele oferece **sete**. Índice sem rótulo é lacuna
de nomenclatura de terceiro, não defeito.

**O rótulo da tela e o nome do campo não são a mesma coisa:** a linha `FACE` é
o `beard_style` e a `H.F.COL.` é o `beard_colour` — medido, as duas movem as
**mesmas duas primitivas** da seção 24, que amostram a folha de cabelo.

**E duas das doze linhas da tela não são campo nenhum.** `DEFAUL` e `NAT` são
as duas metades do *default look por nacionalidade* — a tabela que este
repositório já versiona como `data/defaultlook.txt`, 95 nações, cujas cinco
colunas de aparência são **exatamente as cinco da tupla do corpus**. São dez
campos guardados, não doze.

No disco, os registros ficam em `/SELECT.BIN`, offset **157.164** — e desde
2026-09-15 as duas metades dessa frase têm medição, pela
[`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md):

- **o offset está certo, e não por confiança**: o `OFS_PLAYER_ATTR` do
  `src/core/include/we2002/Offsets.hpp` resolve para **exatamente esse byte
  desse arquivo** (`python tools/pes2/ofs_map.py`), e é um offset que os golden
  conferem contra o `ed.exe`;
- **a contagem estava errada.** Esta seção dizia *"1.242 jogadores × 12 bytes =
  14.904 B"*, do `Offsets We2002.txt`, e são **1.449 × 12 = 17.388 B**, de
  157.164 a 174.552. É o `PLAYERS_TOTAL - PLAYERS_NC` que o `Database::Load`
  percorre, e o disco diz o mesmo sem ser perguntado: os 1.449 primeiros
  decodificam para altura entre 155 e 202, e o de índice 1.449 é o primeiro
  todo zerado.

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

**Desde 2026-09-14 isto é código**, no
[`tools/looks/oracle.py`](../tools/looks/oracle.py), e o que a
[`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) mediu ao
escrevê-lo muda três coisas desta receita:

- **A chegada se confere pelo quadro, e o quadro diz qual slot é.** A média da
  tela inteira **não** distingue os dois states — 0,182425 contra 0,183158, que
  é do tamanho do balanço da própria animação. A placa de posição embaixo do
  nome da camisa (`GK` num, `CB` no outro) difere em **0,119963**, e é por ela
  que o `load_looks()` recusa um state carregado no lugar do outro.
- **Recarregar devolve a mesma imagem até o último bit.** Dois `load_state` do
  slot 1 dão diferença **0,000000** sobre o quadro inteiro. O baseline que esta
  seção prometia está medido, e é o que autoriza a Fase 2 a ler um diff como
  "só o campo que eu troquei".
- **O state amarra imagem *e* build do emulador.** Ele guarda o caminho do
  `.cue` e o estado interno da versão que o gravou: trocar de disco, de release
  ou de binário do fork pode fazê-lo não carregar, e aí a rota manual acima
  volta a ser o caminho. É por isso que ela fica escrita aqui mesmo depois de os
  states existirem.

E os dois `.sav` passaram a ter **cópia dentro do projeto**, em
`work/looks-states/`, apontada por `WE2002_LOOKS_STATES`: o diretório de save
states é o mesmo do trabalho de PES2, slot nu é sobrescrevível por acidente, e
regravá-los custa uma navegação à mão que ferramenta nenhuma deste ciclo
reproduz. A cópia do projeto é a mestra; o slot do emulador é posição de
rascunho, restaurada dela quando divergir.

**Uma armadilha de console, medida na mesma sessão:** o `get_status` do MCP
devolve o título do jogo, que é japonês, e o console do Windows é cp1252 —
imprimir a resposta crua mata o script com `UnicodeEncodeError`, num traceback
que fala de `charmap` e não do emulador.

**E não é só o título do emulador: texto medido também não cabe no console.**
A ajuda de cada linha da tela traz o glifo de botão `■`, e com ele o
`screen.py --report` morria na terceira das doze linhas — e a mensagem de falha
que o `oracle._walk_row` levanta morreria no mesmo lugar, no `print` da própria
falha. Desde 2026-09-17
([`CORR-LOOKS-055`](/docs/tasks/looks/CORR-LOOKS-055.md)) o `main()` dos dois
passa as saídas por `screen.printable_output()` — UTF-8 com `replace` —, então
**a ferramenta não precisa mais de `PYTHONIOENCODING`**. Script de sondagem
escrito à mão continua precisando, ou da mesma chamada.

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
atlas.py        qual registro de imagem cada primitiva amostra (a §1.8)
skin.py         a grade de 16 janelas dentro de uma paleta larga, e qual
                coordenada dela cada campo de cor anda (a incógnita (d))
pieces.py       qual seção é qual peça, por espelho e pelo jogo (a incógnita (b))
looks.py        os 12 campos, seus domínios e os rótulos (A1..P1, A..D, ...),
                a tupla do corpus, e os registros de /SELECT.BIN
assembly.py     campo de LOOKS -> a edição medida que ele faz na primitiva,
                e daí a lista de desenho. O coração, e a Fase 4
confront.py     o confronto da §5.3: rota na tela do jogo, captura contada,
                histograma de cor contra os nossos renders, e a display list
corpus.py       os 50 JPGs da §5.4 pela mesma métrica, com o controle dos
                quadros do emulador ao lado
scene.py        a lista de desenho virando pontos, (u, v) e textura RGBA --
                ainda sem Qt, que é o que deixa o render conferível sem tela
oracle.py       o emulador por MCP: capturar quadro, ler RAM, comparar
harness.py      Checker: ok/attempt/refuses/skip/report   (molde: tools/mcr)
controls.py     controles negativos por substituição literal no fonte
selftest.py     o agregador -- alvo looks_selftest
superpack_count.py  o tamanho do Superpack que o NOTICE.md afirma, contado
                (LOOKS-TASK-01), e não somado à mão
cli.py          sections | pieces | texture | looks | check -- e o check,
                que roda os oito --check-image, é o alvo looks_image (4.4)
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
| `scene.py` | pontos, texel e paleta resolvidos | Qt, e endereço próprio |
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

### 4.4 Os quatro alvos de `ctest`

Mesma divisão por custo que o repositório já usa:

| alvo | precisa | pula? | roda | existe desde |
|---|---|---|---|---|
| `looks_selftest` | nada | nunca | `selftest.py --quiet` | LOOKS-TASK-06 |
| `looks_image` | `WE2002_LOOKS_IMAGE` | 77 | `cli.py check` | **2026-09-14** |
| `looks_ui` | venv + display + `WE2002_LOOKS_IMAGE` | 77 | `ui_check.py` | **2026-09-16** |
| `looks_live` | as duas variáveis, os dois states e o fork | 77 | `oracle.py --check-live` | **2026-09-17** |

**Eram três até 2026-09-17**, e esta seção se chamava *"Os três alvos"*. A
[`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) tinha de
decidir o que fazer com o `oracle.py --check-live`, que existia desde a
[`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) e não era
alvo nenhum — um gate que só roda quem se lembra dele, a forma que a
[`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) abriu. Ele virou o
quarto alvo, e o que decidiu foi medido: ele confere os quatro pré-requisitos
**antes** de subir processo nenhum, e pula com 77 nomeando o que falta; com
tudo no lugar, custa **8,77 s** pelo `ctest`, com a janela fora da tela e o
emulador derrubado na saída. Tem `RESOURCE_LOCK duckstation`, e o `pes2_boot`
ganhou o mesmo: o DuckStation tem um diretório de dados só.

Numa máquina limpa, `ctest -R looks` dá **1 passed, 3 skipped** — medido em
2026-09-17, com os quatro alvos listados pelo nome:

```text
1/4 Test #10: looks_selftest ...................   Passed
2/4 Test #11: looks_image ......................***Skipped
3/4 Test #12: looks_ui .........................***Skipped
4/4 Test #13: looks_live .......................***Skipped
100% tests passed out of 4
```

Com as duas variáveis apontadas, o venv e o fork no lugar, os quatro passam —
o `looks_ui` é o caro, pelas janelas que abre (quatro para medir, e uma árvore
plantada por controle negativo).

**O `looks_live` perdeu a sessão MCP uma vez em catorze corridas**, no primeiro
`pause` depois de o emulador subir, e as outras treze passaram. A causa não foi
separada; está aberta na
[`CORR-LOOKS-051`](/docs/tasks/looks/CORR-LOOKS-051.md). O que aquela corrida
também mostrou — o emulador ficando de pé quando a exceção sai do
`Oracle.__enter__`, onde o `__exit__` não roda — foi consertado na própria
LOOKS-TASK-19.

**O `looks_ui` precisa da imagem, e não só do venv e do display.** A linha da
tabela acima dizia "venv + display" enquanto a 16 não existia; quando ela
passou a medir, o que faltava era o disco: um visualizador sem disco não tem o
que desenhar, e o alvo **pula** em vez de subir a janela vazia e passar. É a
distinção que a [`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md)
existe para não errar — o `mcr_ui` passava com a janela sozinha e imprimia um
`note:` que ninguém lia.

**E o número tem de sair de uma corrida que listou os alvos pelo nome.**
`ctest -R <padrão>` que não casa nada imprime `No tests were found!!!` e **sai
0** — indistinguível de verde, e já passou por verde duas vezes neste ciclo
([`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md),
[`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md)). Nenhum diretório de
build do worktree lista os alvos de `looks`; a receita que funciona nesta
máquina — build fora da árvore, `-G Ninja` com o toolchain do vcpkg — está na
tabela de gates do
[`perfil-looks.md`](/docs/prompts/perfil-looks.md).

**O `looks_image` roda os oito `--check-image`, e não um.** Até 2026-09-17 ele
rodava só o `modelfile.py --check-image`, e esta seção dizia que *"um módulo a
mais só para chamar esse seria cerimônia"* — o que era verdade enquanto ele era
o único. Quando a LOOKS-TASK-19 fechou, sete outros módulos tinham o seu —
`texture`, `atlas`, `skin`, `looks`, `assembly`, `pieces` e `scene` —, e
nenhum estava em alvo: verde no `looks_image` media um oitavo do que o gate de
disco sabe. Quem roda os oito é o `cli.py check`, e a lista não fica por
confiança: o self-check dele lê os fontes atrás de todo módulo que responde
`--check-image` e falha se algum não estiver na corrida. Três regras do
agregador, cada uma com controle negativo:

- **o `modelfile` está na corrida**, porque a primeira leitura dele é um
  arquivo **só-japonês** pela guarda. Geometria é idêntica nos dois discos, e
  sem essa leitura o disco inglês dependeria dos outros para ser notado
  ([`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md)). Medido: contra o
  `.bin` inglês, **sete dos oito falham e o `pieces` passa** — ele só lê
  geometria, e a resposta dele está certa nos dois discos. **A posição não
  importa:** o `check` roda os oito até o fim, e com o `modelfile` por último o
  veredito é o mesmo, `1 ok, 7 failed -- FAILED`. Esta regra dizia "o
  `modelfile` roda **primeiro**" até 2026-09-17, com um controle da posição
  ([`CORR-LOOKS-052`](/docs/tasks/looks/CORR-LOOKS-052.md)); o controle agora
  tira o `modelfile` da lista;
- **pulo parcial é falha**: com a imagem dada, um módulo que ainda responde 77
  está sem algo que os outros têm, e oito resultados com um pulo no meio não
  são o verde de oito. Só os oito pulando é pulo;
- **nada rodado não é verde.**

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

O `MODEL.BIN` percorrido **a partir de 1816** tem de dar **106 seções
terminando em 64.800**, e o `EDT_MOD.BIN` **a partir de 216**, **20 terminando
em 36.072**. É a asserção mais barata do plano e pega qualquer erro de tamanho
de primitiva ou de vértice: errar 24 por 20 desalinha na primeira seção e o fim
não bate.

**Esta seção dizia "`EDT_MOD.BIN` 11 terminando em 36.072", sem offset de
partida**, e ficou assim até 2026-09-14, quando a
[`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) a releu.
A §1.5 já tinha sido corrigida pela
[`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md) e esta não: 11 é o que
uma varredura começando em 15.704 acha, e ela **também** fecha em 36.072
exato. Contagem sem o offset de onde a varredura partiu não é medição — é
justamente por isso que os dois números andam juntos aqui agora.

### 5.2 A RAM bate com o disco

`EDT_MOD.BIN` em `0x8011C000` e `MODEL.BIN` em `0x8016E800`. É reconferível a
qualquer momento por MCP — `python tools/looks/oracle.py --check-live` —, e é o
que amarra "o que eu li do arquivo" a "o que o jogo está desenhando".

**Mas não é byte a byte, e a diferença é o achado.** Esta seção prometia
igualdade total até 2026-09-14, quando a
[`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md) mediu pela
primeira vez, com o jogo parado na tela `LOOKS SET`:

```text
/BIN/EDT_MOD.BIN at 0x8011c000: 203 of 36072 byte(s) differ (99.44% equal), in section(s) 0, 3, 4, 5, 6, 7, 8, 9, 10
    every one of them at byte [2] of a 24-byte primitive
/BIN/MODEL.BIN at 0x8016e800: 20 of 64800 byte(s) differ (99.97% equal), in section(s) 24, 32
    every one of them at byte [1, 2, 5, 9] of a 24-byte primitive
```

Três coisas decorrem, e as três importam mais do que a igualdade prometida:

1. **O cabeçalho e as listas de ponteiro são idênticos nos dois arquivos.** É
   isso que prova que o arquivo está carregado naquele endereço, e é o que o
   `oracle.verify_load()` **exige**; endereço errado falha aí.
2. **Todo byte que difere cai dentro de uma seção, e em posição de primitiva**
   — nunca num cabeçalho de seção, nunca na folga entre duas. O que o jogo
   reescreve é o **CLUT id** da primitiva (byte 2) e o `v` das quinas (bytes 1,
   5, 9, 13), que é exatamente onde a aparência mora. Esta linha dizia "cor de
   primitiva" até 2026-09-15, e uma primitiva deste formato não tem cor: é a
   última sobra da leitura que a §1.6 corrigiu.
3. **O `EDT_MOD.BIN` difere entre os dois save states e o `MODEL.BIN` não.**
   Goleiro e jogador de linha divergem em 162 corridas dentro do `EDT_MOD.BIN`;
   os 20 bytes do `MODEL.BIN` são os mesmos nos dois. A incógnita (a) da §6
   começa daí, e a
   [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) tem a linha.

E a diferença **reproduz**: dois `load_state` do mesmo slot devolvem RAM
idêntica, o que é o baseline que a §1.11 promete, agora medido.

### 5.3 O emulador é o gabarito vivo

O ciclo: escolher uma tupla de LOOKS na tela do jogo por `press_button`,
capturar o quadro por `take_screenshot`, renderizar a mesma tupla no nosso
visualizador, e comparar. A diferença **não precisa ser zero** — resolução,
filtro e câmera diferem —, mas precisa ser **medida, registrada e explicada**.
Um número que ninguém olhou não é verificação.

**Medido em 2026-09-16 pela
[`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md)**, e o
comando é `python tools/looks/confront.py --run` (capturas e veredito) ou
`--score` (só o veredito, sobre as capturas guardadas).

**A métrica não é diferença de pixel, e não pode ser.** Nosso quadro é uma
prateleira sob câmera livre; o do jogo é uma figura posada, animada, sob o
enquadramento dele — quase todo pixel difere pela pose e pela câmera, e nada
disso é a tupla. O que sobrevive a pose, câmera e resolução é **quais cores
aparecem e em que proporção**, e nesta tela isso é a tupla inteira: as catorze
cores de 15 bits da nossa cabeça `A-A1-A-A-A` aparecem **exatas** no quadro do
jogo, porque o PSX desenha esses quads sem modulação. A métrica é a
**interseção de histogramas de cor de 15 bits** (Swain e Ballard), sobre as
cores que o nosso lado desenha, e **nunca lida sozinha**: cada quadro do jogo é
pontuado contra todos os nossos renders do slot, e o veredito é se a tupla
certa vence a própria linha.

| slot | vence por ≥ 0,02 | em primeiro, abaixo da margem | resíduo nomeado | falha |
|---|---|---|---|---|
| 2 — jogador de linha | `B-A1-A-A-A` (0,536), `A-A1-C-A-A` (0,253), `A-I3-A-A-A` (0,028) | `A-A1-A-A-A` (0,016), `A-A1-A-B-E` (0,010) | — | 0 |
| 1 — goleiro | `B-A1-A-A-A` (0,550), `A-A1-C-A-A` (0,247), `A-I3-A-A-A` (0,028) | `A-A1-A-A-A` (0,016), `A-A1-A-B-E` (0,010) | — | 0 |

As vitórias "abaixo da margem" são o limite da métrica e não do render:
`I(g, a) − I(g, b) ≤ 1 − I(a, b)`, e os nossos renders da referência e da barba
`B`/`E` distam só **0,039** — a barba move 2,39% da cabeça
([`CORR-LOOKS-038`](/docs/tasks/looks/CORR-LOOKS-038.md)). O `A-H1-A-A-A` é
**recusa**, não pontuação, nos dois slots. A linha do goleiro dizia
`A-I3-A-A-A` recusado e vitórias de 0,536 e 0,265 até 2026-09-16: a
[`CORR-LOOKS-047`](/docs/tasks/looks/CORR-LOOKS-047.md) mediu o mapa de cabelo
dele, o `I3` voltou a desenhar, e o slot 1 foi re-julgado com o nosso lado
re-renderizado (a paleta da matriz cresceu com as cores do `I3`, daí os números
novos). A captura se repete **pixel a pixel** a
partir do `load_state`, nos dois slots.

**E a display list decidiu a diagonal:** dos quads da cabeça que um pacote
identifica sem ambiguidade, **sete** vêm na ordem em que o arquivo guarda e
**nenhum** na do `we3d`. O `scene.TRIANGLES` estava certo. Quatro são gêmeos
de espelho (mesmo conjunto de `(u, v)`, e um pacote não diz qual dos dois é) e
sete não aparecem nas duas faixas lidas.

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

**Quem mede os nomes é `looks.py --corpus`**, com a pasta por argumento ou em
`WE2002_LOOKS_CORPUS`, e sem ela o comando pula com 77 — o Superpack não entra
no git (§2). Ele conta quantos parseiam, quantos recusam e quantos formatam de
volta para o próprio nome, imprime a cobertura por campo, e **falha se nada for
recusado**: um parser permissivo devolveria 50 de 50 e a linha leria melhor que
a verdadeira ([`CORR-LOOKS-027`](/docs/tasks/looks/CORR-LOOKS-027.md)).

**Quem compara os desenhos é `corpus.py --run`** (e `--score`, sobre os renders
guardados), medido em 2026-09-16 pela
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md). O
`0.jpg` é **um quadro branco**, uma cor só e nenhuma figura: fica fora da conta,
dito pela ferramenta. Das 49 tuplas, **47** desenham e 2 recusam (`H1`).

A métrica é a da §5.3, com um passo a mais que o JPEG exige: compressão com
perda tira as cores da paleta, então cada pixel vai para a cor mais próxima de
onde **poderia** ter vindo — a paleta que desenhamos, **ou** o fundo e a camisa
lidos do próprio JPEG, que não contam. Nenhum limiar escolhido à mão.

**E o veredito é por campo, por causa de um controle.** Os mesmos 47 renders,
contra os quadros **do emulador** da §5.3 — cores exatas, tupla conhecida —,
põem a própria verdade em 3º e 4º lugar: histograma de cor resolve **cor** e
não resolve **forma**, porque câmera e pose mexem na proporção entre as cores
mais do que um estilo mexe. Os campos de cor são julgados; os de forma, só
reportados. **E o que a linha mede é a letra do vencedor**, não a cor do
render: "pele 47/47" quer dizer que o render de **maior nota** para cada JPEG
tem a letra de pele do nome — um render que pinta a pele só na testa perde para
o de outra cabeça com a pele inteira, e a letra bate assim mesmo
([`CORR-LOOKS-050`](/docs/tasks/looks/CORR-LOOKS-050.md)):

| | pele | cor de cabelo | cor de barba | estilo (reportado) | barba (reportado) |
|---|---|---|---|---|---|
| corpus, 47 | 47/47 | 47/47 | 26/26 | 26/47 | 23/47 |
| controle, 4 quadros do emulador | 4/4 | 4/4 | 0/0 | 2/4 | 3/4 |

A cor de barba só é julgada onde o nome tem barba: sem ela, os quads da barba
não amostram nenhuma entrada que a cor mexe
([`CORR-LOOKS-038`](/docs/tasks/looks/CORR-LOOKS-038.md)).

**O corpus achou um erro sistemático, e é o que ele existe para achar.** A nota
de cada JPEG contra o próprio render, agrupada: cabeça `A1` com pele `A` 0,721;
cabeça `A1` com outra pele 0,641; outra cabeça com pele `A` 0,697; **outra
cabeça com outra pele, 0,411**. Olhadas as seis piores, a pele nova pinta só a
testa e o rosto fica na pele `A` — os índices de cor medidos na seção 24 e
aplicados às outras cabeças por empréstimo erram
([`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md)). **Consertado em
2026-09-16:** medidos cabeça a cabeça, os índices de cada uma entram no
`layout.COLOUR_PRIMITIVES`, e o grupo sobe de 0,411 para **0,659** (os outros:
0,721, 0,641, 0,713); a tira dos piores mostra o rosto inteiro na pele do nome.

**E desde 2026-09-16 isso é asserção, não tabela impressa**
([`CORR-LOOKS-050`](/docs/tasks/looks/CORR-LOOKS-050.md)). Um grupo falha quando
a **média** dele fica abaixo da **pior nota** de todos os outros grupos — a pior
imagem de qualquer outro lugar, que já paga pose, câmera e JPEG; nenhum número
escolhido à mão. Com o empréstimo presente, 0,411 contra 0,540, vermelho, e o
grupo saiu como **resíduo nomeado** apontando a CORR-LOOKS-049
(`corpus.GROUP_RESIDUES`). O resíduo **expira**: grupo que deixa de ser outlier
com o resíduo ainda lá também falha — e foi o que aconteceu com o conserto da
049, que esvaziou o `GROUP_RESIDUES`. Um resíduo não entra no piso dos
outros, para não esconder um segundo defeito.

### 5.5 Controle negativo

Pelo molde do `tools/mcr/controls.py`: cada guarda ganha uma injeção que a faz
ficar **vermelha**, plantada por substituição literal numa cópia da árvore.
*Guarda que nunca ficou vermelha é decoração.* Os primeiros três, óbvios:
trocar 24 por 20 no tamanho de primitiva; inverter a ordem da lista de
montagem; trocar uma paleta por outra.

**Os três existem, e são vinte e três no total** — contados pelo
`python tools/looks/controls.py`, que imprime a linha. O terceiro ficou em
aberto até haver o que derrubar, e acabou virando dois, um por jeito de trocar
uma paleta por outra: `texture-clut-any-record` ignora o intervalo do registro
(LOOKS-TASK-10) e `skin-matrix-at-the-record` começa a matriz de cabelo no
registro em vez de uma janela adiante (LOOKS-TASK-12) — que é o erro que o
critério da própria task trazia escrito.

### 5.6 O que não tem oráculo — dito antes de começar

1. **A pose — e é pior do que "pose neutra", medido em 2026-09-16 pela
   [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md).** Não é só a
   animação que falta: **nenhum dos dois arquivos de modelo diz onde uma peça
   fica.** Cada seção é modelada em torno da **própria origem** — nas
   coordenadas do arquivo, a cabeça vai de y **-48 a 15** e a chuteira de
   **-18 a 15**; no render elas aparecem viradas, porque o `scene.UP` é `-1`
   ([`CORR-LOOKS-037`](/docs/tasks/looks/CORR-LOOKS-037.md)) —, então desenhar
   as doze peças nas coordenadas do arquivo empilha o boneco inteiro num ponto
   só. Quem posiciona
   é o jogo, na display list da §6(a), em tempo de desenho.

   **O confronto da §5.3 não precisou dela.** A métrica escolhida é de cor, e
   cor não depende de onde a peça fica; a pose continua **não medida**, e
   passa à [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md)
   como incógnita aberta com a razão.

   A v1 desenha então uma **prateleira**, não uma pose: as peças em fila, cada
   uma inteira, nenhuma sobre a outra (`scene.shelf`). O nome é escolhido para
   não mentir — inventar articulação plausível desenharia um boneco que parece
   certo e é de ninguém, que é exatamente o que o `head_of` recusa fazer com os
   três estilos de cabelo não medidos. A pose de verdade, se for querida, sai da
   display list e é medição da
   [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md). E a
   comparação da §5.3 continua não batendo pixel a pixel, agora por dois
   motivos em vez de um.
2. **A câmera.** O jogo escolhe enquadramento por campo — fecha no rosto em
   `SKIN` e `HAIR`, abre o corpo em `BODY`. Reproduzir isso é adivinhação até
   alguém achar a tabela; a v1 usa câmera orbital livre.
3. **`NAT` e `AGE` — medidos em 2026-09-15**, e "provavelmente" saiu.
   `python tools/looks/oracle.py --fields NAT AGE`: nos dois slots, **nenhum
   dos dois toca um único byte** de `EDT_MOD.BIN`, de `MODEL.BIN` ou de
   qualquer TMD. O `AGE` move **4 bytes** em toda a RAM, o `NAT` move 70 e 138,
   e todos fora da geometria. Eles não entram no render, e não custou nada
   saber.

---

## 6. As incógnitas, em ordem de risco

**(a) O que são os quatro TMDs texturizados de `0x00168xxx` — RESPONDIDA em
2026-09-14**, pela
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md). **O boneco vem
dos dois arquivos de modelo, e não de TMD nenhum.** Trocar um campo na tela
reescreve bytes *dentro* de `EDT_MOD.BIN` e de `MODEL.BIN` nos endereços de
carga, de forma reprodutível, e **zero** bytes em qualquer TMD — que, nos dois
save states, nem sequer estão nos endereços registrados (§1.6). Por campo, com
o ruído da animação filtrado (`oracle.py --fields`):

| campo | onde escreve | o que escreve |
| --- | --- | --- |
| `SKIN` | `EDT_MOD.BIN`, 5 a 7 seções, **mais** `MODEL.BIN` seção 24 | byte 2 — o byte baixo do CLUT, `+0x40` por passo |
| `HAIR` | **só** `MODEL.BIN` seção 24, primitivas 1 e 14 | bytes 1, 5, 9, 13 — o `v` das quatro quinas, `+0x20` |
| `FACE` | **só** `MODEL.BIN` seção 24 | os mesmos bytes de `v` |
| `BODY` | **nenhum dos dois** | trabalha em buffers, não na geometria carregada |

E o estímulo dos dois save states respondeu de graça a pergunta que a task
guardava sobre as **duas listas** do `EDT_MOD.BIN`: mudar `SKIN` no goleiro toca
as seções 11, 16, 17, 18 e 19, que são **da lista 1**; no jogador de linha toca
as seções 0, 3, 4, 5, 6, 7 e 8, que são **da lista 0**. Interseção vazia. **A
lista 0 é o jogador de linha e a lista 1 é o goleiro**, medido e não deduzido do
tamanho.

O que sobra em aberto, e agora com nome: o `MODEL.BIN` seção 24 é a peça que
`HAIR`, `FACE` e `SKIN` compartilham — a cabeça —, e as ~130 a 320 bytes por
campo que caem **fora** dos dois arquivos são buffers de trabalho, com duas
faixas constantes (`0x80153000+` e `0x80162000+`, a 0xF000 uma da outra). Quem
as nomeia é a [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md).

**(b) Qual peça é qual — RESPONDIDA em 2026-09-15**, pela
[`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md), por
`python tools/looks/pieces.py --check-image`. Onze seções por boneco, e nenhuma
nomeada pelo tamanho:

| posição na lista | seções (lista 0 / lista 1) | peça |
|---|---|---|
| 0 | 0 / 11 | **tronco** |
| 1 e 3 | 1, 2 / 12, 13 | **braço** (parte alta) |
| 2 e 4 | 3, 4 / 14, 15 | **antebraço** |
| 5 e 8 | 5, 6 / 16, 17 | **coxa** |
| 6 e 9 | 7, 8 / 18, 19 | **perna** |
| 7 e 10 | 9, 10 (compartilhadas) | **pé** |
| — | `MODEL.BIN` seção 24 | **cabeça** |

Cinco argumentos independentes, e o módulo implementa os três primeiros e
confere os dois últimos:

1. **Os pares são espelhos exatos em `z`** — conjunto de vértices igual, vértice
   a vértice, com `z` negado; nove pares em nove. O eixo é **procurado**, não
   suposto: `x` é o palpite, e `x` não é. O que sobra sem par em cada lista é
   uma seção só: o tronco.
2. **A lista do cabeçalho é uma cadeia, não um saco.** `0 | 1 3 | 2 4 | 5 7 9 |
   6 8 10`: tronco, depois um membro, depois o espelho dele, e dentro do membro
   de dentro para fora. O corte sai de onde o lado troca, o que não exige saber
   o que é um membro.
3. **O que as duas listas compartilham são as seções 9 e 10**, byte a byte
   iguais: as chuteiras. Membro que termina em seção compartilhada é perna.
4. **E o jogo concorda.** `SKIN` reescreve o CLUT exatamente das peças de pele
   nua: no jogador de linha o antebraço e **não** o braço — manga curta —, no
   goleiro **nenhum dos dois** — manga comprida —, as pernas nos dois, e o pé em
   nenhum, por causa da chuteira. É a testemunha que separa braço de antebraço,
   que a regra 2 sozinha teria de tomar por confiança.
5. **E `BOOTS` concorda sem ter sido perguntado:** as únicas seções que ele toca
   são a 9 e a 10, nos dois slots — as mesmas a que a regra 3 chegou pelo outro
   lado.

**(c) A tabela de montagem — MEDIDA, 2026-09-16, com resíduo nomeado**, pela
[`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md), em quatro
passagens: a primeira mediu os cinco campos que reescrevem CLUT e `v`
(2026-09-15) e a quarta fechou a âncora do cabelo, os quads e o cross-check
contra o corpus. O que liga `HAIR = B3` à peça e à paleta certas é o coração do
projeto, e está medido — com quatro buracos **nomeados**, nenhum preenchido por
dedução:

- **três estilos** — `H1`, `M1`, `N1` — não escreveram nada, e **três seções
  pares** — 38, 40, 42 — nunca foram nomeadas; o `head_of` **recusa** os três
  em vez de devolver a cabeça de outro. Esta linha apontava para a
  [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md); o
  confronto **não** os resolveu — o `A-H1-A-A-A` é a recusa das duas linhas da
  matriz dele. **Continua ABERTO em 2026-09-17**: `scene.py --corpus` ainda
  recusa `A-H1-A-A-A` e `D-H1-A-A-A`. Destravaria: ler, com o estilo na tela,
  **o que o jogo desenha** — a display list ou a VRAM —, já que nenhum dos dois
  arquivos de modelo é escrito;
- **os quads de nove das treze cabeças**, cujo escritor o breakpoint não
  achou, e — para os dez estilos de faixa múltipla — **qual quad recebe qual
  faixa** ([`CORR-LOOKS-028`](/docs/tasks/looks/CORR-LOOKS-028.md)). A
  [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md) desenha com a
  marca `BAND NOT MEASURED`, e o `layout.HAIR_QUADS` continua com as quatro
  cabeças de 2026-09-16. **ABERTO**; destravaria um watchpoint de escrita no `v`
  dos quads de uma das nove — a seção 30 é a candidata, porque é onde a regra
  óbvia está medida como errada;
- ~~o mapa foi medido só no jogador de linha~~ — **fechado em 2026-09-16**
  ([`CORR-LOOKS-047`](/docs/tasks/looks/CORR-LOOKS-047.md)): andado no goleiro
  (`oracle.py --patched HAIR 1`), o mapa volta **igual valor a valor**, nas
  **mesmas** seções do primeiro bloco (24..55) — nada do segundo bloco
  (74..105) se mexe — e com as mesmas faixas; `H1`, `M1` e `N1` também não
  escrevem nada lá. O `--writes HAIR 1` acha os mesmos quads nas mesmas quatro
  cabeças. A figura 1 veste o `assembly.HAIR_MAP_GOALKEEPER`, e os goleiros do
  disco recusados por estilo de cabelo caíram de **136 para 4** dos 179;
- **a comparação desenho contra desenho** do corpus, que aqui foi feita por
  altura de malha e não por pixel — **feita em 2026-09-16**, pela
  [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md) contra o
  emulador (§5.3) e pela
  [`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) contra
  os 50 JPGs (§5.4), por histograma de cor. O que ela não alcança é a (h)
  abaixo.

O que se sabe é isto:

**A geometria nunca muda.** Nenhum vértice se mexeu em nenhum dos seis campos
andados de ponta a ponta (`oracle.py --assembly`), e campo nenhum troca uma
seção por outra. Um campo de LOOKS reescreve o **CLUT id** de algumas
primitivas ou o **`v`** de algumas primitivas, e nada mais — de modo que a
lista de desenho é **as seções do disco com uma edição pequena aplicada**, e
não uma escolha entre malhas.

| campo | o que anda | passo | alcance na tela | quem ele move |
|---|---|---|---:|---|
| `SKIN` | linha do CLUT | `+0x40` | 4 de 4 | 8 primitivas da cabeça, mais a pele nua da figura |
| `H.COL` | coluna do CLUT | `+1` | 8 de 8 | 7 primitivas da cabeça |
| `H.F.COL.` | coluna do CLUT | `+1` | 7 de 7 nomeadas | as 2 da barba |
| `BOOTS` | coluna do CLUT | `+1` | 8 de 8 | 42 das 56 primitivas de cada pé |
| `FACE` | `v` e, em `F`/`G`, **a seção** | 16 linhas | **7** de 7 na tela, **7** aplicados | `A`–`E`: as 2 da barba, nas faixas 0 a 4. `F` e `G`: **o gêmeo** da cabeça (seção + 1), com os quads de barba dele (`layout.FACE_TWIN_QUADS`) na faixa 5 do disco e na 6 — medido nas treze cabeças e nas duas figuras ([`CORR-LOOKS-048`](/docs/tasks/looks/CORR-LOOKS-048.md)); até ela, "`F` e `G` escrevem outra coisa, não lida" |
| `HAIR` | **escolhe a seção** | — | 32 de 32 | a cabeça inteira — ver abaixo |

**E o fundo de cada campo é o estado que o disco guarda** — descer a linha até
o fim devolve byte a byte o que o arquivo tem, o que torna a tabela absoluta em
vez de relativa. Os seis **travam nas pontas**; nenhum dá a volta.

**A âncora do cabelo, medida em 2026-09-16.** O `HAIR` **não edita uma seção:
ele escolhe uma.** Quem mediu foi o `oracle.py --patched HAIR`, que anda a linha
do fundo ao topo e lê o **arquivo inteiro** depois de cada tecla — o que muda na
tecla N é a seção que o valor N usa:

- a **letra** do rótulo é uma seção **par** do primeiro bloco de cabeças:
  A é a 24, B a 26, C a 30, D a 48, F a 52, G a 28, I a 34, J a 36, K a 32,
  L a 46, O a 44 e P a 50 — e o **`E` é a exceção, partido em duas**: o `E1`
  cai na 48, que é do `D`, e o `E2` na **54**, que é só dele. São **treze**
  seções: doze letras inteiras e uma partida;
- o **dígito** é uma faixa de dezesseis linhas da folha em 3.568, escrita nos
  quads de cabelo daquela seção;
- e a seção **24 é a família A sozinha** — três valores de 32. É exatamente a
  origem dos "três estados" que toda varredura anterior leu como alcance do
  campo: elas olhavam uma seção só. **A tela andava os 32**, medido duas vezes
  pelo `oracle.py --hair`: a célula de valor se mexe em 32 de 32 teclas enquanto
  a seção 24 assenta em três estados.

E o escritor está no jogo, achado por **breakpoint de escrita** — o primeiro
deste ciclo — em `0x80011580`: `andi v0, a2, 0xff` / `sll v0, v0, 4` /
`addiu v1, v0, 15` e quatro `sb` nos quatro cantos do quad. As dezesseis linhas
por faixa deixam de ser observação e viram aritmética do próprio jogo.

**O bloco 24..55 é dezesseis PARES, não 32 cabeças independentes.** Medido pelo
`assembly.head_pairs`: 91 primitivas diferem dentro de um par e o que as separa
é a barba — 32 saem da coluna 1 do CLUT (cor de cabelo) para a 9 (cor de barba),
41 já estavam na 9 e nenhuma volta da 9 para a 1.

**Quais primitivas recebem a faixa, para quatro das treze cabeças.** Um
breakpoint de **execução** na própria instrução, com a linha andada inteira
(`oracle.py --writes`), lê o `a0` a cada escrita e nomeia a primitiva: a seção
24 são a 1 e a 14, a 26 são a 1 e a 3, a 34 são a 0, a 1 e a 12, e a 46 são a 0,
a 9 e a 17. As outras nove **nunca pararam aquela instrução**, então quem as
escreve é outro trecho de código e o `draw_list` deixa a janela delas como o
disco a tem. A regra óbvia está medida como **errada**: a seção 30 tem doze
primitivas na folha de cabelo com a cor do cabelo, e o jogo reescreve **duas**.

**O cross-check contra o corpus fechou, e sem desenhar.** `assembly.py --corpus`
usa sete pares dos 50 renders que diferem da referência `A-A1-A-A-A` em **um
campo só**, e confronta três coisas independentes: a tabela diz quais primitivas
cada linha tem, a malha do disco diz a que altura elas ficam, e os JPGs de
terceiro dizem onde a imagem muda.

| linha | a malha põe em | os renders mudam em |
|---|---:|---:|
| `HAIR` | 0,246 | 0,361 |
| `H.COL` | 0,438 | 0,353 |
| `SKIN` | 0,447 | 0,576 |
| `FACE` | 0,710 | 0,660 |

As duas ordens concordam com **rho = 0,80** (piso 0,80): a barba é a mais baixa
das quatro nos dois lados, e o cabelo está na metade de cima nos dois. A única
inversão é `HAIR` × `H.COL`, que na imagem distam 0,008 — dentro do ruído das
duas medições.

**O que continua aberto, e passa às tasks seguintes:** **três** valores de 32 —
`H1`, `M1` e `N1` — não escreveram nada em arquivo nenhum, e **três** seções
pares — 38, 40 e 42 — nunca foram nomeadas. **A aritmética fecha com as treze
contadas:** o bloco 24..55 tem dezesseis seções pares, e 16 − 13 = 3. O par de
treses é sugestivo e não é medição, então o `assembly.head_of` **recusa** esses
três em vez de devolver uma cabeça que desenharia perfeitamente e seria de
outro. O `E1` é uma quarta esquisitice, e a pergunta é **por que ele usa a
seção do `D`** — não se o `E` tem seção: tem, a 54, nomeada pelo `E2`
([`CORR-LOOKS-030`](/docs/tasks/looks/CORR-LOOKS-030.md)). E o mapa foi medido no **jogador de
linha** e, desde 2026-09-16, também no **goleiro**, onde volta igual e nas
mesmas seções do primeiro bloco
([`CORR-LOOKS-047`](/docs/tasks/looks/CORR-LOOKS-047.md)); esta frase dizia
que o segundo bloco de cabeças, o do goleiro, ninguém tinha andado.

**As quatro linhas de cor pintam a cabeça que a tupla veste, e não a 24.** O
`assembly.EFFECTS` endereçava `SKIN`, `H.COL`, `H.F.COL.` e `FACE` à constante
`(MODEL.BIN, 24)`, que é a cabeça da família `A` e de nenhuma outra — para os
29 estilos restantes o plano voltava vazio e **nenhum campo de cor movia um
pixel**, com o boneco desenhando perfeitamente. O `edits()` recebe a seção
escolhida e re-endereça a chave
([`CORR-LOOKS-034`](/docs/tasks/looks/CORR-LOOKS-034.md)); medido depois do
conserto, `SKIN` move 14,54% da cabeça `I3` e `H.COL` 2,90%, onde antes os dois
moviam zero.

**E os índices de primitiva das quatro linhas são os de cada cabeça**, desde
2026-09-16 ([`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md)). Até ali
eles tinham sido medidos só na seção 24 e aplicados às outras doze por
empréstimo, marcados **`COLOUR BY BORROWED INDEX`** — e o corpus mostrou o que
isso desenhava: pele nova só na testa. O `oracle.py --colour` anda cada linha
nas treze cabeças e nos treze gêmeos e compara as duas pontas assentadas; a
tabela é o `layout.COLOUR_PRIMITIVES`, e cabeça fora dela **recusa**. A marca
saiu da tabela e da cena.

**E a faixa 0 do `FACE` é o rosto SEM BARBA — medido, não suposto.** Com a
`H.F.COL.` de volta no plano, ela troca a janela de CLUT e **não muda um
pixel** quando o `FACE` é `A`. Isso está certo, e o que decide são os índices
que os dois quads da barba amostram: uma cor de barba mexe em **seis** das
dezesseis entradas da janela (`[2, 5, 12, 13, 14, 15]`), e a faixa 0 **não
amostra nenhuma delas**; as faixas 1 a 4 amostram cinco ou seis. Na tela:
`A-A1-A-A-E` contra `A-A1-A-A-A` move 0,00% dos pixels e `A-A1-A-B-E` contra
`A-A1-A-B-A` move **2,39%**
([`CORR-LOOKS-038`](/docs/tasks/looks/CORR-LOOKS-038.md)). O
`scene --check-image` afirma as duas metades, de modo que uma cor de barba que
parasse de funcionar apareceria como as faixas 1..4 esvaziando.

**A chave do plano é (linha, primitivas).** `H.F.COL.` e `FACE` nomeiam as
mesmas duas primitivas da barba — uma anda a coluna do CLUT, a outra a faixa —
e, com o plano guardado por primitivas, a segunda substituía a primeira:
**`H.F.COL.` não movia nada em cabeça nenhuma**, nem na 24. Achado ao afirmar
que as quatro linhas chegam à cabeça, na mesma correção.

**E há um resíduo dentro do que foi medido: a faixa por quad.** O `--patched`
diz em **quais** faixas os quads reescritos de um estilo caíram, e **dez** dos
29 mapeados caíram em duas ou mais. Qual quad recebe qual, ninguém mediu. Hoje
isso alcança **um** estilo — o `B1`, seção 26, o único de faixa múltipla cujos
quads o `layout.HAIR_QUADS` conhece —, e o `draw_list` aplica a primeira: o
`--tuple` marca essa linha com **`BAND NOT MEASURED`** em vez de imprimir um
`band +0` igual aos outros
([`CORR-LOOKS-028`](/docs/tasks/looks/CORR-LOOKS-028.md)). A medição é de uma
corrida: o `oracle.py --writes` lê `a0` — a primitiva — e `a2` — a faixa — no
**mesmo** acerto do breakpoint, então o par sai junto.

**(d) Pele: paleta ou cor de vértice? — PALETA**, medido em 2026-09-14 pela
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) como
subproduto da (a): cada passo de `SKIN` soma `0x40` ao byte baixo do CLUT id
das primitivas da pele, em quatro valores — que são as quatro peles do
`kSkin[4]`. Não há cor de vértice nenhuma em jogo; a pergunta nasceu da leitura
errada da primitiva, corrigida na §1.6.

**E fechada em 2026-09-15** pela
[`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md), que mediu os
outros dois campos de cor e o lado da GPU. As quatro paletas estão no disco
(§1.7) — os quatro registros de **256 entradas** em VRAM (0, 480) a (0, 483),
offsets 65.892, 66.404, 66.916 e 67.428 —, e um registro de 256 entradas não é
uma paleta: é uma **fileira de dezesseis CLUTs de 4 bits**, porque o CLUT id
endereça `x` em passos de dezesseis entradas. Os três campos são **duas
coordenadas dessa grade**, medidas com o jogo rodando
(`oracle.py --fields`, `oracle.py --palettes`):

| campo | o que anda | passo no CLUT id | alcance medido | quem ele move |
|---|---|---|---|---|
| `SKIN` | a **linha** | `+0x40` | 4 (linhas 480..483) | toda pele nua dos dois bonecos, mais 14 das 18 primitivas da cabeça 24 |
| `H.COL` | a **coluna** | `+1` | 8 (colunas 1..8) | 12 primitivas da cabeça 24, as duas do `HAIR` entre elas |
| `H.F.COL.` | a **coluna** | `+1` | 7 (colunas 9..15) | exatamente as duas primitivas que o `FACE` move |

**Os três campos alcançam as dezesseis colunas:** 1 janela de pele nua + 8
cabelos + 7 barbas = 16. **Isso é sobre os campos, não sobre as colunas** — a
coluna 1 é também a janela de repouso de 948 primitivas em 50 seções do
`MODEL.BIN`, das quais 16 são a cabeça, e as colunas 2..8 e 10..15 não têm
primitiva nenhuma no disco (§1.7,
[`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md)). O
alcance de cada campo foi **andado até as duas pontas**, não deduzido — e aí
apareceu uma propriedade da tela que não estava escrita em lugar nenhum: **os
campos de LOOKS travam nas pontas, não dão a volta.** O quarto `Right` no `SKIN`
deixa o id onde o terceiro o pôs.

**Quatro das dezoito primitivas da cabeça 24 não andam com campo de cor
nenhum: 3, 6, 10 e 11.** A união dos três é
`{0, 1, 2, 4, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17}`, e as quatro ficam na linha
480 **inclusive depois de trocar a pele**. Achado por subtração — o que um campo
**não** move é tão medido quanto o que ele move.

**Este parágrafo dizia nove, e uma exceção, até 2026-09-16:** a união
`{0, 1, 4, 8, 9, 13, 14, 16, 17}`, `SKIN` com 8 e `H.COL` com 7, e a
primitiva 4 andando com `H.COL` e não com `SKIN`
([`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md)). As listas tinham
sido lidas **antes de o jogo terminar de reescrever a cabeça** (armadilha 18 do
perfil); das duas pontas assentadas, `SKIN` move 14, `H.COL` 12, todas as de
`H.COL` andam também com a linha, e a exceção some
([`CORR-LOOKS-049`](/docs/tasks/looks/CORR-LOOKS-049.md)).

**Nenhum byte de vértice se mexe em nenhum dos seis pares campo × slot.** Todo
acerto cai no **byte 2 da primitiva**, que é o byte baixo do CLUT id. Uma
primitiva deste formato não tem cor nenhuma para trocar (§1.6): a pergunta da
incógnita só existia enquanto a leitura da primitiva estava errada.

**E a paleta em si não se mexe.** Medido pelo lado da GPU: as **21 linhas de
CLUT** do `DAT2D.BIN` batem com a VRAM **entrada por entrada**, resolvidas pela
mesma regra que o renderizador vai usar — `texture.covering`, registro mais
estreito ganha —, e um passo de `H.COL` reescreve **zero** das 256 entradas. A
linha 484 é o que torna isso um teste e não uma formalidade: seis registros de
16 entradas ficam **por cima** de um de 256 ali, e o que a VRAM guarda são os
estreitos — comparar contra o largo dá 71 entradas diferentes, e comparar pela
regra dá zero.

**O que o renderizador tem de implementar, em uma frase:** textura com CLUT e
nenhuma cor de vértice — o índice sai do texel, e a cor sai da **janela de
dezesseis entradas** que o CLUT id da primitiva nomeia dentro do registro de
256, nunca do registro inteiro.

### As que ficaram abertas

Esta seção tinha quatro incógnitas, e as quatro estão respondidas acima. A
execução abriu outras cinco, que **não** estavam aqui até 2026-09-17: a
[`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md) e a
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) as
encaminharam à
[`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md), que as
escreve aqui. Nenhuma é respondida; cada uma diz **por que** está aberta e o que
a destravaria.

**(e) A pose — a FONTE está medida desde 2026-09-17, o resto continua aberto.**
A §10.3 (j) tem a cadeia: `ANIME.BIN` na RAM, a entrada 5 do cabeçalho, a lista
de quadros que dá a volta, os ângulos empacotados e as duas instruções que
carregam o GTE. O que esta alínea dizia — e continua valendo para o *arquivo* —
é que onde cada peça fica **não está em arquivo lido pelo visualizador**:
cada seção é modelada em torno da própria origem, e desenhar as doze nas
coordenadas do disco empilha o boneco num ponto só (armadilha 24 do perfil). O
visualizador desenha uma **prateleira** (`scene.shelf`) e diz que é uma. O
confronto não precisou da pose porque a métrica é de cor. *Por que está
aberta:* quem posiciona é o jogo, e o que se leu dele — a display list — dá
coordenada de **tela**, depois da transformação, não de modelo. *Destravaria:*
achar a matriz por peça em RAM, ou a animação parada do `ANIME.BIN`, que o §0
põe fora do escopo.

**(f) O uniforme — FECHADA em 2026-09-20.** Das 593 primitivas da figura 0,
**237** amostravam páginas que não são do `DAT2D.BIN` (629 e 429 na figura 1),
medido pelo `assembly.py --check-image`; são as dos 105 `TEX_*.BIN`, e saíam
sem textura.

> **Fechada pela [`LOOKS-TASK-30`](/docs/tasks/looks/30-o-uniforme.md).** Os
> 105 contêineres entraram na guarda com digest medido — todos **form 1** e
> **idênticos nos dois discos**, o que é por que o `--check-discs` os aceita
> dos dois lados —, e qual deles a tela veste passou a ser **medido na VRAM**
> e não deduzido: `oracle.py --kit` compara cada retângulo que cada contêiner
> declara com o que o console tem no frame buffer, halfword a halfword. Nos
> dois states o vencedor é o **`TEX_A4`**, que reproduz **a página (576, 384)
> e as paletas (0, 486) e (0, 488) exatamente**, e nenhum outro contêiner
> reproduz nenhuma das três — o mais próximo, `TEX_95`, erra 789 halfwords
> delas. Com ele no `draw_list`, o boneco sai **vestido**: 593 de 593
> primitivas texturizadas na figura 0 e 629 de 629 na figura 1, zero
> `no image` e zero `no palette`.
>
> Três coisas que a medição trouxe junto: das sete rectângulos de um
> contêiner a tela **sobe três** (os outros quatro diferem em milhares para
> todos os 105, e somá-los decidia nada — 12.138 contra 13.274); a página
> (576, 256) tem um bloco de 48 linhas que a tela **sobrescreve**, igual nos
> dois states; e os dois conjuntos que cada arquivo guarda são, no `TEX_A4`,
> byte a byte iguais entre si, então qual dos dois o console subiu não se
> distingue aqui.

**(g) Sete quads da cabeça fora da display list — ABERTA.** No quadro de
referência, das 18 primitivas da cabeça, 7 vêm na ordem guardada, 4 são gêmeas
de espelho e **7 não aparecem** nas duas faixas lidas (`confront.py --score`,
`absent 7`). *Por que está aberta:* a hipótese é descarte de face de costas para
a câmera do jogo, e não foi medida. *Destravaria:* girar a câmera do jogo — ou
ler a display list noutro quadro da animação — e ver se o conjunto ausente
muda.

**(h) A forma não tem testemunha — FECHADA em 2026-09-18: a pose no corpo inteiro, o cabelo no close-up.** Histograma de cor resolve pele,
cor de cabelo e cor de barba, e **não** resolve estilo de cabelo nem barba —
nem contra os quadros do emulador, onde a verdade é conhecida
(`corpus.py --score`, o controle; §5.4). Nenhum dos dois confrontos verifica,
então, que a **malha** desenhada é a do estilo certo; quem verifica isso hoje é
só o `oracle.py --patched` da
[`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md), pela seção que o
jogo escreve. *O que a silhueta testemunha, e o que não:* com a pose da (e) e da
[`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) e a câmera da
[`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), a silhueta no
mesmo quadro (`confront.py --silhouette`) **testemunha a pose e o corpo**: seis
comparações, dois slots, 7% a 18% da tinta, mínimo nítido em todas.

**E NÃO testemunha o estilo de cabelo no corpo inteiro.** Esta seção foi dada
como fechada em 2026-09-18 com um controle de estilo trocado que pontuava 696 a
834 contra 179 a 426 — e esses números eram artefato: o `pose()` só posava a
cabeça de referência, e a cabeça do `I3` estava na origem do arquivo, fora do
pescoço. Com todas as cabeças posadas (`scene.place_for`), as fotos do próprio
jogo com `A1`, `C1` e `I3` diferem só **15 e 29 pixels**, e a foto `A1` do jogo
casa com o nosso `I3` (378) melhor que com o nosso `A1` (399). No corpo inteiro,
estilo de cabelo é um punhado de pixels.

*Como fechou para o cabelo:* no **close-up** que o jogo mostra com uma linha de
cabeça sob o cursor, onde o estilo é grande — as fotos do jogo diferem 422 e
1.843 pixels ali. A primeira tentativa escolheu o estilo certo em **2 de 3**, e o
que faltava era medida: **o close-up gira o modelo**, um ângulo diferente a cada
captura (+18,3°, −16,9°, +16,9°), e o giro está composto em cada peça e
**ausente** da carga de câmera que o `--camera` lê — composta com ela, a
translação espalha 29 unidades; com a câmera derivada das próprias peças
(`oracle.camera_from_pieces`), menos de uma. Com foto e câmera da **mesma
parada**, cada foto do jogo escolhe o próprio estilo entre os três, nos dois
slots: **6 de 6**, por 1,36x a 4,10x contra o estilo errado mais próximo
(`confront.py --silhouette-styles`). O
gate fecha um **controle antes** — o mesmo close-up duas vezes, 0 pixel e a
mesma câmera derivada — e confere margem contra o estilo errado mais próximo
(`CLOSEUP_MARGIN`) e teto para o certo (`CLOSEUP_SHARE`), desde a
[`CORR-LOOKS-063`](/docs/tasks/looks/CORR-LOOKS-063.md): antes ele perguntava
só qual dos três escores era o menor.

**(i) As duas corridas de ponteiros do `MODEL.BIN` — ABERTA.** A de 64 e a de 32
ponteiros (§1.5), onde a hipótese do `we3d` de 14 jogadores de 11 peças seria
conferida. *Por que está aberta:* a (a) respondeu de onde vem o boneco sem
passar por elas, e nada no visualizador as usa. *Destravaria:* um breakpoint de
leitura nas duas, com a tela trocando de time.

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
| 8 | **v2** — a tela `LOOKS SET`: as doze linhas medidas no jogo, a janela que as reproduz, e o default por nacionalidade (§10) |
| 9 | **v2** — o boneco montado: de onde vem a pose, a pose de referência, o `ANIME.BIN`, as peças no lugar, a câmera, e altura e corpo (§10) |
| 10 | **v2** — o uniforme dos `TEX_*.BIN`, e o painel e o cenário da tela (§10) |
| 11 | **v2** — a caminhada: o ciclo medido, a janela animada, o goleiro, e o fechamento (§10) |

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
   errado. É a **corrida de palavras zero** entre grupos (§1.4) — 8 bytes no
   `MODEL.BIN`, 12 nas duas primeiras folgas do `EDT_MOD.BIN`. Dizia *"o par de
   zeros"* até 2026-09-17, e um varredor que consome um par fixo cai 4 bytes
   dentro do cabeçalho seguinte do `EDT_MOD.BIN`.
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
   **No disco japonês e na tradução inglesa, não**: medido em 2026-09-20
   (`iso_source.py --check-discs`), os 105 são form 1 nos dois e idênticos
   entre eles, que é o que torna o uniforme legível aqui (§6 f).
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
- **Quatro alvos** em `tests/CMakeLists.txt`, na convenção de brackets já
  usada: um que não precisa de nada, e três com `SKIP_RETURN_CODE 77` — o de
  disco, o de UI e o do emulador —, todos sob `if(Python3_FOUND)` (§4.4). Este
  item dizia *"três alvos"* e *"um de UI sob `if(UNIX AND Python3_FOUND)`"* até
  2026-09-17: o `UNIX` estava medido como errado desde a
  [`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md) — a janela sobe
  nativa no Windows —, e o quarto alvo é da
  [`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md).
- Os controles negativos, contados pela ferramenta e nunca escritos em prosa.
- [NOTICE.md](../NOTICE.md) com a linhagem do `we3d` (MIT, com crédito) e a
  ressalva do Superpack.
- O ciclo `docs/tasks/looks/` com `progresso.md` e
  `/docs/prompts/perfil-looks.md`.
- Este plano, mantido: **o que a execução mudar, muda aqui, na seção que
  mudou.**

**Conferidos contra o disco em 2026-09-17** pela
[`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md):

| entregável | estado |
|---|---|
| os módulos da §3.2 | **todos no disco**, e só eles — a lista da §3.2 foi comparada com `tools/looks/*.py` e `ui/*.py`; faltava o `superpack_count.py`, que entrou nela |
| os quatro alvos | registrados e medidos: 1 passed, 3 skipped numa máquina limpa |
| os controles negativos | contados pelo `selftest.py`, e nenhum número deles escrito aqui |
| `NOTICE.md` | conferido contra o que o projeto de fato usou; a linha do `we3d` deixou de dizer que tomou o agrupamento em 14 modelos, que nada aqui usa, e passou a dizer o que dele foi medido errado |
| o ciclo e o perfil | `check_tasks.py` verde; o perfil com as armadilhas que o ciclo encontrou |
| `CLAUDE.md` | ganhou a seção do projeto, que não tinha |

---

## 10. v2 — a tela `LOOKS SET`, com o boneco montado, vestido e andando

### 10.1 O pedido, e o que ele muda

Em 2026-09-17, com a v1 fechada, o usuário pediu duas coisas, e a segunda na
mesma conversa:

1. que o visualizador mostre o jogador **como a tela `LOOKS SET` do jogo
   mostra**: **montado** — não uma prateleira de peças — e **animado,
   caminhando**. A referência é uma gravação de tela do usuário,
   `Gravação de Tela 2026-09-17 130706.mp4`, que **fica na pasta dele e não
   entra no git**, pela mesma regra do Superpack;
2. que a janela **seja a própria tela `LOOKS SET`**, como os dois save states a
   mostram: as doze linhas, com o cursor, onde se escolhe a cor da pele, o
   cabelo e o resto, e o boneco redesenhado a cada troca.

**A tela, como os dois save states a mostram** — captura do
`oracle.py --check-live`, que se repete pixel a pixel a partir do `load_state`
(§1.11):

- uma barra de título, que desenha `S SET` — o objeto de texto guarda
  `LOOKS SET`, e a fonte do título não tem glifo para `L`, `O` nem `K`
  (§10.3 (q), [`CORR-LOOKS-054`](/docs/tasks/looks/CORR-LOOKS-054.md)). Esta
  linha dizia "uma barra de título com `LOOKS SET`" até 2026-09-17, e era o
  texto do objeto, não o da tela;
- em cima, à esquerda, a **placa de posição** — `GK` no slot 1, `CB` no slot 2
  — e o nome da camisa;
- à esquerda, o **painel** com degradê azul e borda clara, e o boneco dentro;
- à direita, as **doze linhas**, rótulo e valor, com um retângulo de cursor e
  uma seta no valor da linha selecionada. Os valores que os dois states
  mostram: `DEFAUL O.K.`, `NAT Unknown`, `SKIN A TYPE`, `HAIR A1 TYPE`,
  `H.COL A TYPE`, `FACE A TYPE`, `H.F.COL. A TYPE`, `HEIG 175 cm`,
  `BODY A TYPE`, `AGE 23`, `BOOTS A TYPE`, `FOOT RIGHT`;
- embaixo, uma **caixa de ajuda** com um texto sobre a linha — `Visual` nas
  capturas.

**O que a gravação mostra**, olhado quadro a quadro (e **nenhum número dela
entra aqui**: quem mede ritmo, quadros e ângulo é o emulador, na
[`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md)):

- o jogador **caminha parado no lugar**, de frente para a câmera, balançando o
  tronco e os braços — um ciclo de passada que se repete;
- as peças estão **montadas**: cabeça no pescoço, braços nos ombros, pernas no
  quadril;
- o **uniforme tem cor**: camisa, calção e meião num lilás, com dobras
  desenhadas na textura — são as primitivas que a v1 deixa cinza (§6 (f)).

**A ordem das fases segue o pedido, não o risco.** A tela vem primeiro porque
se constrói sobre a v1 como ela está — as linhas de cor e de cabelo já andam no
`assembly.py` — e o usuário a usa enquanto a pose é medida. O risco maior da v2
continua sendo a (j), e ela abre a Fase 9.

**O que a v2 não muda:** continua só lendo, lendo do disco japonês, sem tocar
`roms/`, sem estender o `we2002_core`, e cada número vindo de ferramenta.

### 10.2 O que já se sabe, e de onde

- **As doze linhas, os domínios e os rótulos** estão no `looks.py` desde a
  [`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md), conferidos mecanicamente contra
  o `src/core/Player.cpp`; `DEFAUL` e `NAT` não guardam nada e são o default por
  nacionalidade do `data/defaultlook.txt` (armadilha 17 do perfil). O que
  **não** está medido é o **texto** que a tela escreve para cada valor —
  `A1 TYPE`, `175 cm`, `RIGHT` —, nem a caixa de ajuda.
- **Os campos travam nas pontas e não dão a volta** (armadilha 14), medido nas
  linhas de cor e de cabelo; nas outras seis, não.
- **A pose não está nos dois arquivos de modelo.** Cada seção é modelada em
  torno da própria origem (§6 (e)); a v1 desenha uma prateleira por isso.
- **O `ANIME.BIN` existe no disco japonês e é cru.** Medido em 2026-09-17:

  ```sh
  MSYS_NO_PATHCONV=1 python tools/pes2/iso.py ls roms/japanese-shift-jis.bin
  #  /BIN/ANIME.BIN   lba=3000   size=396804   form1
  MSYS_NO_PATHCONV=1 python tools/pes2/lzss.py roms/japanese-shift-jis.bin --file /BIN/ANIME.BIN
  #  /BIN/ANIME.BIN   396804 B  header 204 w -> stream at 816  none  0 block(s), 396804 B outside
  ```

  Cabeçalho de **204 palavras** de ponteiro KSEG0 — a mesma forma dos dois
  arquivos de modelo (§1.2), com a largura que a §6.13 do
  [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) já contava. **Que o `ANIME.BIN`
  é o que a tela usa é hipótese, pelo nome**: a
  [`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md) mede antes de qualquer leitor ser
  escrito, como a [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) mediu os modelos antes
  da Fase 3.
- **`BODY` não escreve em nenhum dos dois arquivos de modelo** (§6 (a)), e
  `HEIG` também não foi visto escrevendo; se os dois mudam o desenho, é na
  transformação, e é por isso que a (s) mora na Fase 9.
  > **Medido em 2026-09-18** ([`LOOKS-TASK-29`](/docs/tasks/looks/29-altura-e-corpo.md)):
  > é na transformação, e é na **câmera** — ver a (s).
- **O uniforme mora nos `TEX_*.BIN`**, que não têm digest na guarda (§6 (f)).
- **A forma não tem testemunha** (§6 (h)). Um boneco montado na pose do jogo é
  o que a dá: a mesma silhueta no mesmo quadro passa a ser comparável.
- **O emulador já chega à tela** pelos dois save states, com a captura
  repetível pixel a pixel (§5.3), e o fork tem breakpoint de execução e de
  escrita, leitura de registrador e de VRAM.

### 10.3 As incógnitas da v2

**(q) A tela — o que ela escreve e como anda.** O texto de cada valor de cada
linha, o da caixa de ajuda, o comportamento do cursor nas pontas das doze
linhas, e os valores iniciais que cada save state carrega. Texto de tela
inventado a partir do rótulo é o erro que a armadilha 17 descreve.
[`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md).

> **Respondida em 2026-09-17**, por `oracle.py --screen --write`, e a resposta
> é o [`tools/looks/screen.json`](../tools/looks/screen.json) — escrito pela
> ferramenta, remedido por `oracle.py --screen`. O que se aprendeu:
>
> - **O texto sai de onde o jogo o imprime.** A rotina `layout.SCREEN_PRINT`
>   recebe oito objetos de texto por quadro — os doze rótulos num só, as
>   unidades noutro, os valores de `SKIN` a `BOOTS` num terceiro, `NAT` e
>   `FOOT` um cada, mais placa, nome da camisa e título. As strings trazem
>   três códigos de controle (`\n`, `\t`+1, `\r`+3), e o que o
>   `screen.decode` faz delas é conferido, a cada corrida, contra os glifos que
>   a rotina `layout.SCREEN_GLYPH` desenha: 34 strings, nos dois states e na
>   ponta de cada uma das doze linhas. **A placa e o nome da camisa entram
>   nessa conferência** desde a [`CORR-LOOKS-054`](/docs/tasks/looks/CORR-LOOKS-054.md);
>   o título não pode entrar, e é o item seguinte.
> - **O título não é o que o objeto diz: o objeto guarda `LOOKS SET` e a tela
>   mostra `S SET`.** Medido em 2026-09-17
>   ([`CORR-LOOKS-054`](/docs/tasks/looks/CORR-LOOKS-054.md)), escrevendo
>   marcador de onze bytes sobre a string na RAM do jogo em execução e lendo a
>   faixa de volta da VRAM: o título é impresso pela **segunda** fonte ASCII
>   (`kind` 33), que não passa pela rotina de glifos, e ela tem glifo para
>   **nove** dos 71 caracteres imprimíveis varridos — `AEJSTW12-`. Caractere
>   sem glifo **não desenha e não anda com a caneta**; espaço anda sem
>   desenhar. Por isso `LOOK` some. Não é captura cortada: a faixa mostra as
>   mesmas quatro letras ao longo de 600 quadros. O `screen.json` guarda o que
>   a tela desenha (`title`), o que o objeto guarda (`title_object`) e o que a
>   fonte pula (`title_skipped`); o `screen.py --check` recusa tabela em que os
>   três não concordem, e o `--screen` conta as letras da faixa contra o que a
>   fonte desenharia.
> - **As doze linhas travam nas duas pontas**, e **o cursor vertical dá a
>   volta** nos dois sentidos — lido pela caixa amarela na VRAM, não pela
>   contagem de teclas. Nenhuma linha de valor mexe em outra ao ser andada,
>   `NAT` inclusive.
> - **O alcance da tela, com o valor guardado ao lado de cada texto:**
>   `DEFAUL` 1 (`O.K.`), `NAT` 80 (de `Unknown` a `New Zeland`, com os nomes
>   truncados que o jogo escreve — `Swi`, `Cze`, `Portuga`), `SKIN` 4,
>   `HAIR` 32, `H.COL` 8, `FACE` 7, `H.F.COL.` 7, `HEIG` **56** (155 a 210 cm,
>   de um campo que guarda 148 a 211), `BODY` 8, `AGE` 32, `BOOTS` 8, `FOOT` 3.
>   **Todo rótulo de terceiro do `looks.py` é o que o jogo escreve** em cada
>   valor alcançável — agora checado pelo `screen.py --check`.
> - **A ajuda de cada linha** é única — `Confirm`, `Nation`,
>   `Skin Colour ■ Turn`… — e é a testemunha de qual linha o cursor ocupa.
>   **Ao carregar o state ela mostra `Visual`**, sobra do menu anterior, até a
>   primeira tecla.
> - **Os dois states começam iguais em tudo menos a placa** (`GK`, `CB`): cursor
>   em `NAT`, `Unknown`, `A`, `A1`, `175 cm`, `23`, `RIGHT`; o registro do
>   jogador, lido das duas cópias vivas (`layout.PLAYER_RAM`), diz o mesmo.
> - **As caixas, em pixels do display nativo de 512×240**, e não em frações da
>   captura, que corta overscan: painel `(16,66)-(161,185)`, linhas
>   `(176,37)-(496,185)`, ajuda `(16,187)-(496,221)`, cursor na linha `NAT`
>   `(314,53)-(476,64)` e um passo de 12 por linha. Os textos estão em
>   coordenadas do centro do display, com as linhas a partir de `y=-79`.
>   **A caixa do cursor é por linha**, e o passo só a desce: ela começa em
>   x 314 em `NAT`, 436 em `AGE`, 428 em `FOOT` e 396 nas outras nove, igual
>   nos dois slots e em todo valor da linha — medido em 2026-09-22
>   ([CORR-LOOKS-070](/docs/tasks/looks/CORR-LOOKS-070.md)). Até essa data
>   este item dava só a de `NAT` e o passo, e a tabela carregava aquela caixa
>   para as outras onze linhas.

**(r) `DEFAUL` e `NAT`.** Qual nação é qual valor da linha `NAT`, e se `DEFAUL`
aplica exatamente a linha do `data/defaultlook.txt` — medido no jogo, nunca
suposto pelo nome da coluna. [`LOOKS-TASK-23`](/docs/tasks/looks/23-default-por-nacionalidade.md).

> **Respondida em 2026-09-17**, por `oracle.py --default`, e a resposta desmente
> a pergunta em três pontos. O que se mediu:
>
> - **`DEFAUL` não aplica default nenhum: é o botão de confirmar da tela.** Um
>   valor só (`O.K.`), ajuda `Confirm`, e `Circle` sobre ele **sai** do
>   `LOOKS SET` para o menu de edição do jogador. Medido em **seis** nações
>   espalhadas, incluindo três cuja linha do arquivo não é toda `A`: as doze
>   linhas e os doze bytes do registro saem da tecla **iguais** — `0 de 6`.
> - **`NAT` escolhe a nacionalidade, e ela é guardada fora dos doze bytes**, em
>   `layout.PLAYER_NATION`, sobrevivendo à saída da tela (o menu mostra
>   `NAT. BRA`). Um dos dois endereços é `0x800E9450 + 27`, ou seja: o registro
>   de 12 bytes que este ciclo lê mora dentro de uma estrutura maior.
> - **O código da nação não é a posição na linha.** Andando os **80** valores e
>   lendo o byte em cada um: os valores 1 a 54 guardam 0 a 53, e aí o código
>   **salta 41** — `Iceland` (valor 55) guarda 95, e a linha acaba em 119. Os
>   códigos 54 a 94 nomeiam algo que a tela não oferece. `Algeria` é o valor 65
>   e guarda 105. Está em `looks.NATION_CODES`, e o comando reanda a linha
>   inteira a cada corrida.
> - **O `data/defaultlook.txt` é a tabela do EDITOR, não do jogo**, e o
>   cabeçalho dele diz: `TEAM;NAME;…`. São 95 **times** — nações e clubes
>   juntos (`Inter`, `Bayern`, `Clas. Brazil`, `Euro All Stars`) —, enquanto a
>   linha `NAT` é a lista de nacionalidades do jogo, com países que o arquivo
>   não tem (`Senegal`, `Uzbekistan`, `Trin y Tobago`) e nomes cortados pela
>   largura da célula (`Portuga`, `Netherl`, `Swi`, `Cze`). Casadas **por
>   nome** (`looks.nation_lines`): **44** dos 80 valores da tela têm linha, 12
>   deles por truncamento; **36** não têm; e **51** linhas do arquivo não têm
>   valor na tela.
> - **Casar por índice é o erro caro, e ele tem cara de certo.** Pulando
>   `Unknown` e pareando por posição, a correspondência **vale até o valor 16**
>   (`Sweden`) e depois desanda: no 17 o jogo diz `Finland` e a linha do
>   arquivo é `Islanda`, e mais adiante `Algeria` receberia a linha do
>   **Arsenal**. Medido: 2 times trocados e 35 valores recebendo uma linha que
>   não é deles.
>
> O controle da medição é a mesma nação alcançada duas vezes a partir do
> `load_state`, que tem de ler igual; e o vermelho existe — com a regra ingênua
> (`código = índice − 1` até o fim) plantada numa cópia da árvore, a corrida
> acusa **25 problemas**, um por valor depois do salto.
>
> **O que fica aberto:** se alguma outra tela do jogo aplica um default a
> partir da nacionalidade (criar jogador novo, `RESET`, `BASE COPY` do menu de
> edição) não foi medido — esta task mediu a tela `LOOKS SET`. E o que a tela
> mostra para um código que não é de nação: no `load_state` as duas cópias do
> byte nem concordam (253 e 139) e a linha diz `Unknown`, mas não se escreveu
> valor nenhum na RAM para varrer o resto.

**(j) De onde vem a pose — o maior risco.** Três candidatos, e nenhum medido:
o `ANIME.BIN` lido a cada quadro; matrizes calculadas em código a partir de
poucos parâmetros; ou uma tabela noutro arquivo. Escrever um leitor de
`ANIME.BIN` antes de saber é o erro que a
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) existiu para não cometer.
[`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md).

> **Respondida em 2026-09-17**, por `oracle.py --pose`, e a resposta é o
> primeiro candidato — **com o terceiro dentro dele**: a pose vem do
> `ANIME.BIN`, mas não como nove números por peça. A cadeia medida, ponta a
> ponta, nos dois save states:
>
> 1. **O arquivo está na RAM byte a byte** — 396.804 de 396.804 — em
>    `layout.ANIME_BASE` = `0x8017EE00`, logo depois do `MODEL.BIN`. A base foi
>    medida **por conteúdo**: uma corrida de 64 bytes do offset 1.000 aparece
>    uma única vez nos dois megabytes. O `derive_base()` **não** a deriva, e as
>    duas razões são **sequenciais, não paralelas** — a primeira acontece antes
>    de a segunda ter vez:
>
>    - a corrida de ponteiros é reconhecida por "bit alto", e o payload deste
>      arquivo abre com `0x9000040A`, que tem o bit. A corrida não para no fim
>      do cabeçalho, e a função **recusa o arquivo** com
>      `WrongBase: base 0x8017ee2c puts header pointer 204 (0x9000040a) at
>      266868190, outside the file's 396804 bytes`. É isso que se vê ao chamá-la;
>    - **cortada a corrida em 204 palavras**, onde os ponteiros de fato acabam,
>      a segunda metade da regra ainda erra: ela supõe que o ponteiro mais baixo
>      mire logo depois da corrida, e o deste arquivo mira o offset 912, não o
>      816. Daí sairia `0x8017EE60`, 96 bytes alto — e é essa base, escrita à
>      mão numa cópia da árvore, que dá o controle vermelho do comando:
>      **279.034 de 396.804 bytes diferem** e nenhuma das 204 entradas é lida.
>
>    Esta frase dizia que a função *"responde `0x8017EE60`"* até 2026-09-18
>    ([`CORR-LOOKS-059`](/docs/tasks/looks/CORR-LOOKS-059.md)), e ninguém obtém
>    essa resposta: quem chamar recebe a exceção.
> 2. **O cabeçalho é de 204 entradas, uma por animação, e a tela toca a de
>    índice 5.** Medido com um watchpoint de leitura nas 204 de uma vez:
>    nenhuma outra é lida. O leitor é `0x800270B8`, que guarda o ponteiro no
>    estado de animação.
> 3. **O estado (`layout.ANIME_STATE`) toca uma lista de quadros:** a lista em
>    +0x18, o quadro corrente em +0x1C e o índice em +0x329, que anda a cada
>    quadro e **volta a zero** quando a entrada ao lado marca o fim. É a
>    passada se repetindo, e é por isso que o boneco caminha sem que nada seja
>    apertado.
> 4. **O quadro é lido por quatro instruções** (`0x80011E80`, `0x80011E94`,
>    `0x80011EB0`, `0x80011ECC`), e o código ao redor **desempacota ângulos**
>    de uma palavra com `sll`/`sra`, guardando-os no scratchpad (`0x1F800120`
>    em diante). **Os nove números não estão no arquivo:** o que está são
>    ângulos empacotados, e a matriz é calculada deles — o que explica o
>    "matrizes calculadas em código" do segundo candidato sem que ele seja a
>    fonte.
> 5. **A matriz chega ao GTE em duas instruções**, de 30 `ctc2` que escrevem o
>    primeiro registrador dela e 5 que rodam nesta tela:
>    `layout.POSE_MATRIX` (`0x80012168`) e `POSE_MATRIX_SECOND`
>    (`0x8001229C`), 18 e 18 de 40 paradas.
>
> **O controle do instrumento vem antes da conclusão**, e é o que separa "medi"
> de "não achei": um watchpoint de leitura sobre um objeto de texto que a
> rotina de impressão recebe **dispara** nesta build, então o silêncio sobre
> uma faixa é silêncio do jogo e não do fork. A primeira tentativa vigiou
> **quatro** endereços do arquivo, não viu nada e quase virou "o `ANIME.BIN`
> não é lido"; a entrada que o jogo lê é a sexta palavra do cabeçalho.
>
> **O que fica para a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md):** qual carga de matriz é de qual peça. A 24
> conta paradas, e o número antes de a sequência se repetir varia entre
> corridas (207 e 408), então ele não é contagem de quadro.

**(k) A hierarquia e a convenção.** Rotação em ponto fixo 4.12, `y` para
baixo — a v1 já desenha com `UP = -1` —, e se a matriz de cada peça é absoluta
ou relativa à peça-mãe. [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md).

> **Respondida em 2026-09-18**, por `oracle.py --pose <SLOT> <N> [N ...]`, e a
> resposta é **absoluta**: o que chega ao GTE por peça já é a câmera composta
> com a volta daquela peça, e um leitor nosso não compõe hierarquia nenhuma —
> reproduz doze transformações prontas. O que se mediu, nos dois slots, em oito
> quadros contados a partir do `load_state`:
>
> - **As duas cargas de matriz da §10.3 (j) não são duas do mesmo tipo.**
>   `layout.POSE_MATRIX` entrega a **mesma** rotação em toda parada de uma
>   passada, enquanto a translação anda pelas peças — é a câmera;
>   `layout.POSE_PIECE_MATRIX` (o `POSE_MATRIX_SECOND`) entrega uma rotação
>   **diferente por peça**, mudando a cada quadro. Ler a pose da primeira daria
>   doze peças com a mesma orientação.
> - **A matriz não está na instrução nem ainda no GTE:** cinco pares
>   `lw`/`ctc2` a copiam de uma struct de 32 bytes — nove meias-palavras 4.12
>   de rotação nos offsets 0 a 0x10, dois de enchimento, e três palavras de
>   translação em 0x14, 0x18 e 0x1C. A captura lê **a struct**, pelo registrador
>   base (`v1` na da peça, `a0` na da câmera): ler o GTE na parada traz a
>   matriz da peça **anterior**, porque a carga ainda não aconteceu.
> - **Quem é a peça, o ponteiro diz.** Na parada, os registradores de ponteiro
>   caem dentro da seção que está sendo desenhada, e o `pieces.py` a nomeia —
>   nenhum nome sai de tamanho nem de ordem suposta. A passada tem **12 cargas**
>   nos dois slots: as onze peças da figura daquele slot (o goleiro usa as
>   seções 11 a 19 e o jogador de linha as 0 a 8, e os dois compartilham a 9) e
>   uma que **não carrega ponteiro nenhum** — a carga da **segunda chuteira**,
>   a seção 10. Ponteiro não a nomeia porque cada carga é nomeada pela parada
>   seguinte e a primeira parada de uma passada vem com os três registradores
>   zerados; quem a nomeia é a junta. Esta linha dizia *"a raiz"*, com matriz
>   *"igual à da câmera a menos de uma volta pequena"*, até 2026-09-18
>   ([`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)): a rotação dessa
>   parada balança **4362** ao longo de oito quadros, acompanhando os 4074 da
>   canela `b`, enquanto a da câmera é constante — quem quase não se mexe é o
>   tronco, com 185.
> - **A passada se fecha pela sequência se repetindo**, nunca pelo contador de
>   quadros: o `internal_frame_number` vira **no meio** da passada, e cortar por
>   ele entrega cinco peças em vez de doze.
> - **Absoluta, e a prova é aritmética.** Se `M = C x R` com `R` uma rotação
>   verdadeira, então `M x Mt = C x Ct` — e é o que se mede: o pior caso das
>   duas corridas fica em **0,0071** da maior entrada (a segunda pior, 0,0015),
>   contra **0,99** de uma matriz que não é a câmera composta com nada. O
>   arredondamento para meia-palavra é toda a folga.
> - **A hierarquia se mede pelo quadro da mãe**, não pela anatomia: a origem da
>   filha vista de dentro da mãe, `d = M_mãe⁻¹ (t_filha − t_mãe)`, é constante
>   se há junta e balança se não há. **Cinco pares se separam nos dois slots** —
>   cabeça↔tronco (14,5x e 14,6x), chuteira a↔canela a (10,5x e 9,2x),
>   chuteira b↔canela b (9,9x e 12,8x), antebraço a↔braço a (5,3x e 4,9x) e
>   antebraço b↔braço b (5,0x e 4,6x) —, e **nenhuma linha fora desses cinco
>   pares passa de 3,3x** (3,3x no slot 1, o tronco; 2,5x no slot 2), o que é
>   dizer que não se separam. A folga é de **4,6x contra 3,3x**. Os nomes destes
>   pares eram outros — *raiz↔cabeça, canela a↔coxa a, canela b↔coxa b,
>   braço a↔tronco, braço b↔antebraço a* —, e cada um estava um elo fora: são os
>   mesmos números lidos com a nomeação de antes do atraso de desenho, que só
>   foi corrigida no fim de 2026-09-18
>   ([`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)). O teto de fora
>   também mudou com a nomeação: foi *"2,3x"* até
>   [`CORR-LOOKS-060`](/docs/tasks/looks/CORR-LOOKS-060.md), depois 2,5x, e a
>   corrida com os nomes certos imprime 3,3x. **O esqueleto do jogo não é rígido**: os pés, os antebraços
>   restantes, as coxas e o tronco não ficam a distância fixa de candidato
>   nenhum. Isso é resultado, e é justamente por isso que o leitor não compõe.
> - **`y` cresce para baixo**, como o `UP = -1` do `scene.py` já supunha: a
>   cabeça em `y = −8` e o pé mais baixo em `y = 60`. E **nenhuma das doze
>   matrizes tem determinante negativo** — o espelho das peças `b` está na
>   geometria, não num eixo invertido na matriz.
> - **Distância entre peças não mede osso.** A câmera escala `y` por 0,61 e `x`
>   e `z` por ~0,80, então `|t_filha − t_mãe|` varia 25% com a peça girando,
>   sem osso nenhum esticar. Quem desfaz a câmera é o `M_mãe⁻¹` acima.
>
> **O que ficou aberto aqui, e fechou em 2026-09-18**
> ([`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)): esta seção dizia
> que a tela desenha **duas** chuteiras e só **uma** seção de chuteira carrega
> matriz, e que a segunda seria desenhada *"sem carga de matriz própria,
> reaproveitando a rotação que já está no GTE"*. As seções 9 e 10 são lidas as
> duas — watchpoint de leitura, uma corrida por seção, 2 e 2, com uma seção
> desenhada como controle —, e **as duas carregam matriz**: são doze cargas
> para doze seções desenhadas. O que falta à segunda é **nome**, não carga.
>
> A carga sem ponteiro é o **par 12** de cada quadro do `ANIME.BIN`, lido até
> então como uma raiz que não desenha nada. Ele é a chuteira `b`, e a junta o
> diz três vezes: no **arquivo**, sobre os dezessete quadros da caminhada, a
> origem dele no referencial da canela `b` fica em (0,2, 69,1, −2,2) com
> dispersão máxima **5,6** — o mesmo tornozelo que a canela `a` segura a
> (0,3, 68,2, 3,3) com 5,1 —, contra 356 medido da canela errada e 229 do
> tronco; nas **capturas**, 16,8 no slot 1 e 15,6 no slot 2, contra 212 e 195
> da canela errada; e a aritmética fecha, porque a seção que captura nenhuma
> nomeia é justamente a 10.

**(l) O formato do `ANIME.BIN`.** Os 204 ponteiros, o que cada um nomeia, e se a
varredura fecha no EOF — o rito da Fase 1 (§1.4).
[`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md).

> **Medida em 2026-09-18, e a incógnita continua ABERTA em um ponto.** O
> `tools/looks/anime.py` lê o arquivo inteiro; o que falta é reproduzir a
> matriz do jogo número a número. O formato:
>
> ```text
> offset 0     204 palavras, uma por animação, cada uma um endereço ABSOLUTO
>              dentro da imagem de carga do próprio arquivo (ANIME_BASE).
>              197 são distintas — sete animações são nomeadas duas vezes.
> offset 816   o payload, um bloco por animação e mais nada:
>                  quadro[N]     96 bytes cada
>                  ponteiro[N]   um por quadro, absoluto como o cabeçalho
>                  0x0000000B    uma palavra, fechando o bloco
>              A entrada do cabeçalho aponta a LISTA, não os quadros: eles
>              ficam imediatamente antes dela.
> ```
>
> - **A varredura fecha exato.** A partir do offset **816**: **197 blocos,
>   3.952 quadros, terminando em 396.804 = EOF, com ZERO buraco.** O offset de
>   partida anda junto com a contagem, como a §1.4 exige.
> - **Um quadro é doze pares de palavras, um par por peça desenhada**, na
>   ordem em que a tela as desenha (`anime.PIECE_ORDER`) — a mesma ordem das
>   doze cargas de matriz da §10.3 (k). A correspondência **foi medida**: a
>   captura da pose lê os três ângulos do scratchpad em cada carga, e eles são,
>   par por par, os doze pares do quadro que o estado estava tocando.
> - **A primeira palavra do par traz três ângulos de 10 bits com sinal**, nos
>   bits 9:0, 19:10 e 29:20, cada um deslocado quatro para a esquerda. Não é
>   leitura de formato: é o que o código em `0x80011D48` faz, instrução por
>   instrução (`sll 22 / sra 18`, `sll 12 / sra 22 / sll 4`, `sll 2 / sra 22 /
>   sll 4`). Os dois bits de cima são bandeira e este leitor não os lê.
> - **A matriz não está no arquivo, e a rotina que a constrói é `0x8003D4BC`**,
>   chamada com os ângulos no scratchpad (`layout.POSE_ANGLES`) e o destino em
>   `0x1F8000D0`. Ela indexa uma tabela de 4.096 palavras em `0x8005B148`,
>   cada uma `(cos << 16) | sin` em 4.12. **A tabela é gerada, não versionada:**
>   despejada da RAM e comparada com `round(sin(2πi/4096) × 4096)`, dá **0
>   divergência em 4.096** (contra 3.080 se fosse truncamento).
> - **A ordem da composição é `Rz · Ry · Rx`**, e isso foi medido pelo outro
>   lado: decompondo as matrizes que o jogo carregou, os ângulos que voltam são
>   **múltiplos de 16** — que é o que o arquivo guarda — só sob essa ordem.
>
> **A ponte, e a correção que ela exigiu.** Esta passagem dizia, mais cedo no
> mesmo dia, que *"96 de 192 peças trazem ângulos que quadro nenhum do arquivo
> guarda — são os quadros que o jogo constrói entre os quadros-chave"*. **Era
> artefato da ponte**, e a lição é dela:
>
> - a primeira ponte entre a captura e o arquivo foi o **quadro que o estado
>   de animação nomeia** (`layout.ANIME_STATE`). Ele está certo para o jogador
>   de linha e **errado para o goleiro**, cujos ângulos então não casavam com
>   nada em 3.952 quadros;
> - a ponte que vale é o **ponteiro que o jogo está lendo**: `s0` na instrução
>   `0x80011D48` (`layout.ANIME_UNPACK`), que anda o arquivo de oito em oito,
>   um par por peça, nos dois slots. Com ela, **96 de 96 peças trazem os
>   ângulos que o par guarda, inteiro por inteiro** — 96 das **192**
>   capturadas, porque oito das dezesseis capturas são postas de lado: a
>   passada delas não parou no desempacotamento, e o que está gravado ali é
>   o scratchpad anterior, não o que aquele quadro desenhou. O
>   `--against-pose` imprime as duas contas e **reprova** se menos de um
>   terço das capturas carregar par
>   ([`CORR-LOOKS-061`](/docs/tasks/looks/CORR-LOOKS-061.md));
> - e **dez variantes de desempacotamento** dividem o mesmo dispatch
>   (`0x80011DA0`): a peça que toma outra não para na instrução vigiada, e
>   herdar o par da peça anterior nomeia bytes errados com cara de certo.
>
> **A matriz sai EXATA, e a exatidão está na ordem dos deslocamentos.** A
> `RotMatrix` do jogo (`0x8003D4BC`) carrega seis entradas da tabela, roda três
> `gpf sf` — a interpolação do GTE, `IRn = (IR0 × IRn) >> 12` — e monta as nove
> meias-palavras deslocando doze a cada passo. Escrita assim, ela reproduz
> **90 das 96** matrizes julgadas **entrada por entrada** (das 192
> capturadas; ver a nota das oito postas de lado acima); escrita com um
> deslocamento só no fim, ou com a composição em outra ordem, erra por **uma**
> unidade em dois terços das peças (5 de 13 exatas). Uma unidade de 4.096 é
> invisível no desenho e total na comparação.
>
> **As outras seis são misturas que o jogo faz**, não erro do leitor: o
> caminho em `0x80011F90` **soma a matriz recém-construída com a que ele
> guardou e desloca um bit**, e a média de duas voltas não é a volta de coisa
> nenhuma guardada. Quem diz isso não é a distância — é uma varredura de
> **todos** os pares do arquivo (`anime.no_pair_explains`): nenhum deles
> reproduz aquelas seis. A primeira testemunha era mais barata — ler a volta de
> volta e exigir múltiplos de 16 — e **errou uma em seis**, porque a média de
> dois trios a 32 de distância também é múltipla de 16. O que decide essa
> mistura é o estado da animação entre quadros, e isso é a
> [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md).

**(m) A câmera do jogo — FECHADA em 2026-09-18.** Projeção, deslocamento de tela
e a translação da câmera, para que o nosso quadro e o do emulador sejam o mesmo
desenho. [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md).

> **Medido:** `H = 1376 px`, a matriz `[3195, 0, 635, -27, 2488, 133, -635,
> -268, 3195]` e a translação `[-480, 192, 4125]`, iguais nos dois slots, lidos
> do GTE na carga da matriz por peça — com o mesmo quadro capturado duas vezes,
> as doze cargas de uma passada carregando a mesma projeção, e um quadro
> contado adiante concordando (`oracle.py --camera`).
>
> **E o deslocamento de tela do GTE é ZERO.** `OFX` e `OFY` valem 0,00, então
> a projeção sai com a origem no eixo da câmera e **quem põe o boneco dentro do
> painel é o deslocamento de desenho da GPU**, não o GTE. Isso e a nossa
> escolha de medir lugares a partir de uma peça (a segunda chuteira,
> [`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)) somam **uma**
> translação, e ela é **ajustada a cada comparação**, não fixada — ver
> abaixo. Esta frase dizia que a translação era medida uma vez e fixada, até a
> [`CORR-LOOKS-064`](/docs/tasks/looks/CORR-LOOKS-064.md), que é o que a
> primeira sessão fez e o que a segunda mediu ser pior.
>
> **A projeção confere na largura:** a nossa figura projeta **50,5 px** de
> largura onde a do jogo mede **50** no painel.
>
> **E a silhueta fecha.** Em três quadros contados de cada slot, o quadro da
> caminhada que o par do próprio jogo nomeia está **0 a 2 quadros à frente** do
> que a foto mostra — a foto é o buffer anterior, e um quadro da caminhada dura
> ~3,5 do emulador —, com mínimo interior e nítido em todas as seis varreduras
> e **7% a 18%** da tinta do jogo de diferença. Os controles fecham antes: o
> mesmo quadro contado duas vezes dá **0** pixel, quadros diferentes dão 603 a
> 1.483 no slot 2 e 670 a 1.452 no slot 1.
>
> Duas coisas custaram a chegar lá e ficam escritas: o segundo buffer de quadro
> começa na linha **240** da VRAM e não na 256 — lido errado, a caixa de ajuda
> entra no recorte do painel e a máscara não casa com nada —, e a comparação
> tem de ser **livre de translação**, alinhada por comparação. Uma translação
> única mantida fixa soa mais rigorosa e mede outra coisa: o melhor casamento
> foi de 13% da tinta para 72%.
>
> **E a janela desenha com ela**, desde a terceira sessão: o núcleo constrói a
> 4x4 no tamanho **nativo** do painel e a janela só a envia ao shader, com um
> self-check que exige o mesmo pixel que o `project()` — pior caso 0,000000 px.
>
> **E há duas câmeras, não uma.** Com uma linha de cabeça sob o cursor **o jogo
> aproxima a câmera na cabeça** — o mesmo `H`, z em 999 contra 4125 — e **gira o
> modelo**, um ângulo por captura que a carga de câmera não traz. A câmera que
> vale para o close-up sai das próprias peças (`oracle.camera_from_pieces`),
> conferida contra as doze: rotação a 3,7/4096, translação a meia unidade. No
> corpo inteiro as duas leituras coincidem (controle: giro de ±0,03°). A
> primeira leitura dos estilos no corpo inteiro era defeito nosso — o `pose()`
> só posava a cabeça de referência —, e corrigido, no corpo inteiro os estilos
> não se separam; no close-up, sim (§6 h).

**(s) `HEIG` e `BODY` — FECHADA em 2026-09-18.** O que mudam no desenho — escala na matriz, troca de
peça, ou nada — medido pela pose de dois valores de cada.
[`LOOKS-TASK-29`](/docs/tasks/looks/29-altura-e-corpo.md).

> **Veredito: uma escala por eixo, dentro da câmera.** Nenhuma peça muda e a
> pose não muda: o jogo guarda um vetor de escala da figura e o aplica às
> **colunas** da rotação da figura, truncando para zero, antes de multiplicar
> a vista (`stature.py`):
>
> ```text
> h     = HEIG + 148
> x = z = (h << 12) / (tabela[BODY] + 10)     tabela = 210 200 195 190 185 180 175 170
> y     = (h << 12) / 180
> câmera = (VISTA · trunc(Ry(128) · diag(x, y, z))) >> 12
> peça   = (câmera · pose) >> 12
> ```
>
> Então **`HEIG` escala os três eixos** — o jogador alto é também largo — e
> **`BODY` só largura e profundidade**; `H TYPE` é o único corpo tão largo
> quanto alto. O que não muda: a translação da câmera, o `y` com o `BODY`, a
> pose e as peças. A regra não está escrita em lugar nenhum do código nosso:
> bias, deslocamento, os dois divisores e a tabela saem das instruções do
> `/SELECT8.BIN` (base `0x800CB000`), que o `stature.rule` decodifica e
> recusa se não forem as medidas — o `/180` é a multiplicação mágica
> `0xB60B60B7` com `sra 7`, não um `div`.
>
> Medido por `oracle.py --stature`, os dois slots:
>
> - **a caminhada** — os 56 valores de `HEIG` (155 a 210 cm) e os 8 de
>   `BODY`, 62 teclas por slot: vetor de escala e carga de câmera contra a
>   regra, **0 fora**, e **62 cargas diferentes**;
> - **a pose** — o estado duas vezes (controle), as pontas de `HEIG`, os oito
>   `BODY` e `155 cm` com `H TYPE` juntos, nos **mesmos quadros da
>   caminhada** que o controle: **12 de 12 peças exatas** em cada uma das 12
>   capturas dos dois slots, rotação e translação, inteiro por inteiro;
> - **a janela** — o `looks_ui` fotografa a tela nas pontas e exige a razão da
>   regra na tinta do painel: 88×165 a 155 cm, 100×187 a 175, 122×222 a 210 e
>   123×188 em `H TYPE`, com os dois controles plantados vermelhos.
>
> E a silhueta (`confront.py --silhouette-stature`), pelos limiares da
> LOOKS-TASK-28: 155 cm a 18% e 16% da tinta, 210 cm a 12% e 11%, `D TYPE` a
> 16% e 18%, `H TYPE` a 6% e 7% (slot 2 e slot 1), atraso de 0 a 2 quadros.
> A nossa figura **na estatura do estado** pontua 897/801, 969/989 e 754/784
> contra essas fotos, todas acima do que a estatura certa erra. `D TYPE` fica **abaixo da
> resolução**: a foto do jogo muda 405 e 408 pixels, menos que os 428 e 457
> que a nossa melhor comparação já erra, e aí a ordem não se afirma
> (armadilha 76 do perfil).
>
> Três coisas que a medição teve de aprender, no perfil como armadilhas 73 a
> 75: depois de trocar um valor, o mesmo quadro contado **não** é o mesmo
> quadro da caminhada, e uma passada desenha dois quadros do `ANIME.BIN`
> cortados numa peça que muda; no goleiro o quadro 0 é mistura (o controle o
> recusa: `foot b` 92 de 4096 fora, com os ângulos iguais aos do arquivo); e
> escalar linhas ou colunas dá a mesma matriz nesta tela, então nenhum
> controle separa as duas.

**(n) Qual `TEX_*.BIN` a tela veste — FECHADA em 2026-09-20.** A §6 (f):
digest na guarda, o arquivo que o time dos save states usa, e as primitivas
resolvidas. [`LOOKS-TASK-30`](/docs/tasks/looks/30-o-uniforme.md).

> **É o `TEX_A4`, nos dois states, medido na VRAM** (§6 f). O desenho o lê
> pelo `layout.KIT_ON_SCREEN`, e o que isso vale está medido dos dois lados:
> o `scene.py --check-image` exige as duas figuras inteiramente texturizadas
> **e** imprime o caso sem kit ao lado (356 de 593, as 237 do corpo cinzas);
> o `looks_ui` exige `textured == primitives` na figura inteira, com o
> controle plantado *"o kit chegando ao corpo"*; e o `confront.py
> --kit-control` desenha a mesma tupla no uniforme de outros dois times e
> mede que a foto do jogo fica **0,218, 0,218, 0,148 e 0,063** mais longe.
>
> **O confronto de cor da §5.3 não testa o uniforme**, e vale dizer por quê:
> ele desenha `--piece head` por decisão medida, então trocar o kit não move
> nenhum dos seus números — re-rodado com o uniforme ele fica onde estava,
> 3 vitórias e 2 ranqueadas por slot, **0 inexplicadas**. Quem cobra o kit é
> o controle de figura inteira acima.
>
> **Qual contêiner cada time veste continua sem medida.** O que está medido é
> qual deles estes dois screens subiram; a regra por time é outra pergunta, e
> nenhuma task aberta a faz.

**(o) O painel e o cenário — FECHADA em 2026-09-21.** Se o degradê, a borda, a
barra de título, as faixas das linhas e a fonte são imagem do `DAT2D.BIN` ou do
`EDT_2D.BIN`, ou polígonos da GPU.
[`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md), que fecha a medição e a mobília; o
resto da tela é das [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) a
[`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md).

> **Três elementos respondidos, e são polígonos.** O `oracle.py --scenery` lê a
> display list na RAM e fica só com os pacotes cujas cores são as que o
> console mostrou dentro do retângulo deles — o que separa a lista viva das
> sobras, porque as bandas guardam também a lista da tela anterior (as linhas
> dela ficam a 9 pixels onde as desta ficam a 12). Sobram **28 pacotes**, os
> mesmos nas duas leituras:
>
> | o que | pacote | cores |
> |---|---|---|
> | o painel do boneco, (17,66)-(160,185) | um quad gouraud | (0,48,128) no topo a (48,40,80) embaixo |
> | a caixa de ajuda, (16,187)-(496,221) | um quad gouraud | (0,24,40) a (16,80,120) |
> | as doze faixas das linhas, x 177 a 495 | 26 quads chatos | (0,53,55) e (0,38,45) alternando, e a primeira linha em preto |
>
> **Nenhum deles é imagem**: não há registro de `DAT2D.BIN` envolvido, e o
> desenho é do próprio GPU. Os pacotes texturizados que a varredura acha são
> **o boneco**, e as páginas que eles amostram confirmam a
> [`LOOKS-TASK-30`](/docs/tasks/looks/30-o-uniforme.md) de graça: a cabeça sai
> da página (512,256) do `DAT2D.BIN` e o corpo da (576,256), que é do kit e
> que o `DAT2D.BIN` não tem.
>
> **A fonte dos textos é imagem, e do disco.** Parando o jogo na passada que
> DESENHA do `layout.SCREEN_GLYPH` e lendo o estado do próprio GPU, a página
> em vigor é a de **VRAM (704, 0), 4 bits com CLUT**, e o `DAT2D.BIN` tem um
> registro nela. Perguntar ao GPU é o caminho que resta: nesta tela o texto
> não deixa pacote na RAM para ler.
>
> **O que falta, e por que não saiu daqui.** A barra de título, a placa
> (`GK`/`CB`), a caixa da camisa e as setas `◀ ▶` **não estão em lista nenhuma
> da RAM** — varrida inteira (`layout.SCENERY_SWEEP`), com quads, triângulos e
> sprites, e nada cai fora do painel. E não é que sejam pintados uma vez: o
> `oracle.py --repaint` sobrescreve os **dois** buffers e a tela **inteira**
> volta, então tudo é redesenhado a cada quadro. Nem são cópia de VRAM: o mapa
> de procedência do `--scenery` procura cada ladrilho da tela no resto da VRAM
> e **não acha nenhum** (o texto, que é desenhado por CLUT, também não aparece
> ali — uma cópia apareceria).
>
> E o `oracle.py --pages` estraga uma página de VRAM por vez e mede o que a
> tela perde, com duas corridas sem dano de controle: as páginas do boneco
> (512,256) e do kit (576,256) derrubam 17 ladrilhos cada no slot 2, e 12 e 18
> no slot 1, todos sobre a ajuda e o painel
> ([`CORR-LOOKS-066`](/docs/tasks/looks/CORR-LOOKS-066.md)), três
> páginas vizinhas não derrubam nada — e a da fonte derruba **um** ladrilho
> só, o que diz que ela é reenviada a cada quadro. Medir o que o caminho de
> impressão manda ao GPU, comando a comando, é a continuação desta task.
>
> **E a janela, comparada com o jogo fora do boneco** (`confront.py
> --outside`, 2026-09-21): o chão de cada região — a mediana de cada canal,
> sem os pixels do boneco — no quadro do jogo e na janela em escala nativa,
> com o jogo fotografado duas vezes de controle. O painel fica a **4**, a
> caixa de ajuda a **3** e as faixas a **11**, nos dois slots; as cores que a
> v2 tinha escolhido a olho ficavam a 24 e a 142.
>
> **A lista que o quadro entrega ao GPU, e a barra de título está nela**
> (2026-09-21). Um watchpoint de escrita no registrador de endereço do DMA do
> GPU para só em `layout.GPU_LIST_SUBMIT` (`sw a0, 0x0(v0)`), e o `a0` dali é
> a cabeça da lista: três por quadro, uma tabela de ordenação que alterna
> entre dois buffers e uma lista de um nó. Andada da cabeça, ela dá **43
> pacotes** de mobília, os mesmos nas duas leituras e nos dois slots, **em
> ordem de desenho** — e corrige a varredura acima em duas coisas:
>
> | o que | pacote | cores |
> |---|---|---|
> | o fundo, oito peças em volta do painel e das faixas | 8 quads gouraud | (0,0,0), (14,8,49) e (29,22,99) |
> | a barra de título, y 16 a 36 | 3 quads gouraud **aditivos** (blend 1) | cinza (192,192,192) a preto, teal (0,112,80) a preto, cinza a preto — **através** da tela, não para baixo |
> | a área das faixas, (192,66)-(528,186) | 2 quads gouraud aditivos | (14,8,49) e (29,22,99) |
> | a borda do painel | 4 polilinhas | (192,192,192), duas por lado, em x 16/17 e 160/161 |
> | as faixas das linhas | **24** quads chatos, não 26 | os mesmos dois tons |
>
> A barra de título **não aparecia** na varredura por um motivo só: ela é
> semitransparente, e o quadro mostra a **mistura**, nunca a cor que o pacote
> declara — o filtro de cor a descartava. E duas das 26 faixas eram sobra. A
> janela agora desenha a mobília do jeito que o GPU desenha — cada quad em dois
> triângulos 0,1,2 e 1,2,3, sombreados entre os cantos, misturados pelo blend
> do pacote — num núcleo (`scene.furniture_picture`), uma vez. O `confront.py
> --outside` ganhou três regiões da mobília que o `screen.json` não nomeia:
> **barra de título a 3, fundo a 3 e 3**, painel a 4, ajuda a 4, faixas a 6
> (eram 11), nos dois slots.
>
> **E a página da fonte não está resolvida.** A mesma pergunta ao GPU na
> passada que desenha do `SCREEN_GLYPH`, em três corridas, deu (704, 256) e
> (832, 256) no slot 2 e as duas mais (704, 0) no slot 1 — só a (704, 0) tem
> registro no `DAT2D.BIN`. O "(704, 0)" acima veio de **uma** corrida. O que o
> GPU tem em vigor na parada não é necessariamente o que o glifo seguinte usa.
> Texto, placa, caixa da camisa e setas continuam fora da lista: nenhum
> pacote texturizado cai fora do painel.
>
> **Estavam na lista o tempo todo, e são sprites** (2026-09-21, quinta
> passada). A frase acima está errada. Quem a desmentiu foi o código do jogo:
> a rotina de glifo (`layout.SCREEN_GLYPH`) só preenche uma estrutura
> `GsSPRITE` no scratchpad, e quem a manda para a lista é uma chamada ao sort
> de sprite com o `GsOT` cuja etiqueta é a própria cabeça que o quadro entrega
> ao DMA. Um watchpoint de escrita na porta de comando do GPU confirmou o
> resto: **nada** escreve nela durante a tela. O que escondia os sprites era o
> leitor. A libgs põe o **E1** que escolhe a página e o **sprite** no mesmo
> nó, e o `--scenery` classificava o nó pela primeira palavra: via uma troca de
> modo e nada mais. Partido em comandos (`oracle.commands_of`), o quadro traz
> **142 sprites**, os mesmos nas duas leituras e nos dois slots. Cada grupo
> teve os texels amostrados decodificados do disco japonês, pela guarda, e
> comparados com a VRAM da tela de pé; o controle, a mesma comparação três
> linhas abaixo, diverge em 1.502 de 2.128 texels:
>
> | o que | sprites | página, CLUT | de onde vêm os texels |
> |---|---|---|---|
> | a **fonte**: rótulos, valores, `SHIRT N`, `CB` | 121 | (704,256) 4 bits, (0,497) | **`EDT_2D.BIN`**, 1.068 de 1.068 iguais |
> | o título `S SET` | 4 | (768,256), (128,498) | `EDT_2D.BIN`, 180 de 180 |
> | o ícone à esquerda da camisa | 1 | (768,256), (80,499) | `EDT_2D.BIN`, 96 de 96 |
> | a barra vazia ao lado da placa | 1 | (960,256), (0,497) | `EDT_2D.BIN`, 288 de 288, chapada (o controle não a distingue) — e **toda transparente**, medido na LOOKS-TASK-36 (abaixo) |
> | as caixas verdes da camisa | 4 | (576,0), (176,496) | `DAT2D.BIN`, 384 de 384 |
> | a **placa** `CB`/`GK` | 4 | (576,0), **(208,499) no jogador de linha e (192,499) no goleiro** | `DAT2D.BIN`, 96 de 96 |
> | a seta `▶` do valor sob o cursor | 1 | (704,0), (80,497) — e a `◀` também, medida em `DEFAUL` nos dois slots na CORR-LOOKS-068 | `DAT2D.BIN`, 16 de 16 |
> | o texto da **ajuda** (`Visual`) | 6 ladrilhos 16×16 | (832,256), (64,496) | **nenhuma imagem do disco**: o jogo o escreve na VRAM em tempo de execução |
>
> As oito CLUTs estão no `DAT2D.BIN` e batem 16 de 16. O `EDT_2D.BIN` é
> idêntico nos dois discos e entrou na guarda (`layout.SCREEN_ART_FILES`). E a
> "página da fonte não resolvida" se resolve: os três valores que o estado do
> GPU deu eram **três sprites diferentes** — a fonte (704,256), a ajuda
> (832,256) e a seta (704,0) —, e o estado lido na parada era o do último
> sprite desenhado. **Falta desenhá-los**: a janela ainda escreve com uma fonte
> do Qt, e o texto muda com a tecla, então o que a janela precisa é da tabela
> de glifos do jogo (código → `u`, `v` e largura), não da foto de um quadro.
>
> **A fonte, lida da rotina** (2026-09-22,
> [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md)). A rotina de
> glifo não está no `/SELECT8.BIN`: está no **`/SELECTC.BIN`**, carregado em
> 0x800FC000, achado por conteúdo nos dois discos. O arquivo difere entre eles
> em 5.201 bytes, que são o texto traduzido. A rotina (0x8010BB04-0x8010C0D8)
> e a tabela (0x8010D008) são iguais byte a byte nos dois discos e na RAM do
> jogo, e a regra se lê do **japonês**, pela guarda. Para os códigos 32 a 126,
> `u` e largura vêm de um par de bytes da tabela (`código − 32`), e o `v` de
> uma faixa de códigos. `A` a `J` ficam na linha dos dígitos (146), `K` a `Z`
> na 158, e as minúsculas a partir de `g` na 170. `@`, `^` e `~` têm largura
> 0. De 161 a 223 a rotina calcula por aritmética, e acima disso procura
> Shift-JIS de dois bytes: **está lido e não está implementado**, porque
> nenhuma string desta tela chega lá. O espaço tem largura 4 e não gera
> sprite. O `oracle.py --glyphs` confere a regra contra o quadro: 121 de 121
> sprites de fonte iguais em `uv`, tamanho e CLUT nos dois slots, com a tabela
> lida um par adiante casando 0.
>
> **O avanço é a largura mais o espaçamento do objeto.** O objeto de texto
> guarda, depois do `kind`, o que parece o **alinhamento** no byte 13 (0, 2
> ou 3); o **espaçamento** no byte 14 (2 nos rótulos, 1 em `Unknown`, 0 em
> `SHIRT N` e nos dígitos); e a **cor** dos glifos nos bytes 16 a 18
> ((128,128,128) em rótulos, placa e camisa; (112,112,240) nos valores). O
> `screen.json` grava o estilo de cada texto. Um valor pode ser montado de
> vários objetos: `A1 TYPE` é o `A1` de um e o `TYPE` de outro. O estilo
> gravado por linha é o do objeto do último pedaço. A janela escreve com
> esses glifos, e os rótulos, alinhados à esquerda no x do objeto, batem
> **pixel a pixel** com o quadro do jogo (0 de 16.416 nos dois slots, com o
> quadro deslocado um pixel divergindo em 2.875). Onde cada valor, a placa e
> a camisa **começam** dentro da caixa é a
> [`LOOKS-TASK-38`](/docs/tasks/looks/38-o-alinhamento-dos-valores.md).
>
> **Os estáticos e as setas, desenhados** (2026-09-21,
> [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md)). O
> `sprites.py` monta cada sprite do disco como o GPU o corta — quatro texels
> por halfword, a entrada `0x0000` da CLUT transparente, a cor do sprite
> modulando cada canal (128 é um) —, e a janela pinta título, ícone, caixas da
> camisa, barra e placa **por cima da mobília**, que é a ordem da lista: a
> barra de título aditiva é o comando 301, a placa o 307 e o título o 384. A
> CLUT da placa vem da **posição** que a tela mostra (`layout.PLATE_CLUT`), não
> da tabela de um slot. Quem julga não é o `sprites.py`: o `--scenery --write`
> grava, por sprite estático, até 32 pixels opacos que nenhum sprite posterior
> cobre, com a cor que o **frame buffer do jogo** mostra ali — 359 por slot —,
> e o `looks_ui` exige a janela dentro de 8 em todos, nos dois slots.
>
> **A "barra vazia ao lado da placa" não desenha nada**: os 1.152 texels do
> sprite são transparentes (`sprites.py`, decodificado do `EDT_2D.BIN`). O
> verde que se vê ali é a primeira caixa da camisa, 96×16 do `DAT2D.BIN`.
>
> **As setas seguem o que uma tecla faria.** O walk do `--screen` lê as setas
> da lista a cada tecla e grava, por linha, as da chegada, das duas pontas e
> de entre elas, recusando se as de entre variarem. Nas onze linhas de
> valores, o ▶ aparece em x 480 enquanto houver valor à direita, e o ◀ enquanto
> houver à esquerda, num x **fixo por linha**, que não acompanha o texto: 302
> em `NAT`, 424 em `AGE`, 416 em `FOOT` e 384 nas outras oito. A cor delas
> pulsa de quadro a quadro; a janela as desenha a 128, sem pulso. E o
> `DEFAUL` mostra o ◀ com um valor só, porque `Left` **não** trava ali: leva o
> cursor ao rótulo, com a ajuda `Undo` e o ▶ em x 276 —
> [`CORR-LOOKS-067`](/docs/tasks/looks/CORR-LOOKS-067.md).
>
> **Veredito (2026-09-21): a tela é polígono e imagem, e o que é imagem é do
> disco — menos a ajuda.** O painel, a caixa de ajuda, o fundo, a barra de título, as
> faixas e a borda são 43 pacotes sem textura, desenhados pela janela como o
> GPU os desenha. Texto, título, ícone, caixas, barra, placa e seta são 142
> sprites cortados do `EDT_2D.BIN` e do `DAT2D.BIN`, com as paletas do
> `DAT2D.BIN`. O texto da ajuda é escrito na VRAM pelo jogo em tempo de
> execução. A [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md) fecha com a medição e a mobília; desenhar
> os sprites, o texto, o alinhamento, a ajuda e a câmera do close-up são as
> [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) a [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md).

**(p) O ritmo do ciclo.** Quantos quadros do jogo dura uma passada, se o jogo
interpola entre quadros-chave, e se o tronco que balança é da animação ou da
câmera. [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md).

### 10.4 Como se verifica

**O gabarito é o emulador, no mesmo estado.** O `load_state` dá o baseline, e o
`frame_step` e as teclas contadas a partir dele dão o estado N — é o que as
Fases 2 e 6 já fazem. A v2 acrescenta três comparações, todas com controle
antes do teste:

1. **Tecla contra tecla, na tela.** A mesma sequência de teclas a partir do
   `load_state`, no jogo e na nossa janela, e o texto de cada linha comparado
   — o do jogo lido por ferramenta, nunca transcrito à mão. O controle é a
   mesma sequência duas vezes no jogo, que tem de dar o mesmo texto.

   > **Fechada em 2026-09-17** pela
   > [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md), e o comando é
   > `oracle.py --keys [SEQUÊNCIA [SLOT]]`, ~30 s por corrida. Ele compara
   > **três** lados depois de uma sequência de 19 teclas: o jogo, o
   > `screen.json` e a nossa janela — as doze linhas e a caixa de ajuda.
   > Medido: **0 diferença** no slot 2 e **0 no slot 1**, com o controle —
   > a mesma sequência duas vezes no jogo — concordando linha a linha antes.
   > E o vermelho existe: com **uma** mentira plantada na tabela de uma cópia
   > da árvore (`HEIG=178` escrito `178 CM`), a corrida dá **2 diferenças**,
   > uma contra o `screen.json` e outra contra a janela que acreditou nele,
   > com o controle ainda verde — que é o que mostra que quem julga é o jogo.
   >
   > A sequência default sai de `oracle.KEY_SEQUENCE` e é escolhida para ser
   > incômoda: sai da linha em que o state carrega, anda para cima e para
   > baixo, e aperta `Left` onde a linha já está na ponta esquerda — uma tecla
   > que o jogo ignora e que uma janela ingênua atenderia.
2. **Matriz contra matriz.** O que o nosso leitor diz para a peça P no quadro N
   contra o que o GTE carregou para P no quadro N, lido por breakpoint. Ponto
   fixo é inteiro: a comparação é **exata**, e qualquer diferença é achado.
   > **Fechada em 2026-09-18** pela
   > [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md), e o que ela
   > acrescentou não estava previsto aqui: a comparação exata de matriz já
   > estava verde na
   > [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md) — 90 de
   > 96 exatas — **e a figura montada com elas não ficava em pé**. Faltava
   > dizer de *qual peça* é cada matriz, e essa pergunta não é sobre números:
   > o ponteiro de modelo que o jogo carrega na parada da carga nomeia a peça
   > que ele **acabou de desenhar**, uma parada atrás (`oracle.DRAW_LAG`).
   > Lido na hora, a chuteira herda a matriz do quadril, cada peça continua
   > individualmente perfeita e nenhum número sai da faixa.
   >
   > **O que desempata é medido e não é o desenho**, porque usar o desenho
   > seria decidir pelo critério que se quer afirmar: a origem da chuteira no
   > referencial da própria canela tem dispersão **5,0** unidades no atraso 1
   > e **158,8** no atraso 0, sobre oito quadros espalhados dos dois slots,
   > com a **outra** canela de controle ficando solta em 357,3
   > (`oracle.py --pose-lag`). Corrigido o atraso, os pares `a`/`b` ficam
   > simétricos — quadris a −224 e −217, ombros a −341 e −342 — e os lugares
   > do próprio arquivo empilham a figura da cabeça em −420 à chuteira em 0,
   > que é a chuteira contra a qual todos os outros lugares são medidos
   > ([`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md); esta linha dizia
   > "o chão em que a raiz se apoia", e a raiz é a segunda chuteira).
3. **Silhueta contra silhueta.** A máscara do boneco no nosso quadro contra a
   do emulador, no mesmo N, com a câmera da (m). O controle é o emulador contra
   ele mesmo em dois `load_state` — que já dá **zero pixel** (§5.3) — e um
   quadro deslocado de propósito, que tem de dar diferença. **O limiar sai do
   controle, e é escrito depois de medido e dito que foi.**

**E a caminhada se confere em vários N, não em um.** Um quadro certo é pose;
vários quadros certos em sequência é animação.

### 10.5 As fases da v2

| Fase | Tasks | O que entrega |
|---|---|---|
| 8 — a tela | 21 a 23 | a tela medida no jogo, a janela que a reproduz sobre a v1, e o default por nacionalidade |
| 9 — montado | 24 a 29 | a fonte da pose, a pose de referência, o leitor do `ANIME.BIN`, as peças no lugar, a câmera do jogo, e altura e corpo |
| 10 — vestido | 30 a 31 | o uniforme, e o painel e o cenário da tela |
| 11 — andando | 32 a 35 | o ciclo medido, a janela animada, o goleiro, e o fechamento |

**O que não pode ser pulado:**

- **A 21 antes da 22.** Uma janela escrita antes de a tela ser medida inventa
  o texto de cada valor, e o gate dela confere a invenção contra ela mesma.
- **A 24 antes de tudo da Fase 9.** Leitor de formato escrito para o arquivo
  errado lê perfeitamente e desenha outra coisa.
- **A 25 antes da 26.** A pose capturada do jogo é o gabarito do leitor; sem
  ela, um leitor plausível passa.
- **A 28 antes de qualquer silhueta.** Comparar desenho com câmera diferente
  mede a câmera.
- **A 32 antes da 33.** Animar num ritmo inventado produz caminhada bonita e
  errada.
