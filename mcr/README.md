# Saves de memory card — WE2002 (Japão) e PES2 (Europa)

Nove cartões de PlayStation. **Oito baixados prontos**, e um **gravado aqui**
pelo próprio jogo — `we2002-english-first-boot.mcr`, que tem seção própria mais
abaixo e é o único desta pasta cuja procedência é esta máquina.

Os oito baixados **não são todos do mesmo jogo**, apesar de todos os arquivos se
chamarem `pro-evolution-soccer-2.*`: o nome vem de quem publicou o pacote, não
do cartão. Quem diz de que jogo cada um é são as entradas do diretório, e elas
dizem **dois jogos e três discos**:

| Código na entrada | Disco | Cartões | Projeto que os usa |
|---|---|---|---|
| `BISLPM-87056WEW-*` | `SLPM-87056` — World Soccer Winning Eleven 2002 (Japan) | `29939`, `34218`, `34978`, **`first-boot`** | o port do editor de `.mcr`, `tools/mcr/` |
| `BESLES-03946PES-*` | `SLES-03946` — Pro Evolution Soccer 2 (Europe) **(EnFrDe)** | `17738`, `18432`, `22507`, `7110` | o projeto PES2, `tools/pes2/` |
| `BESLES-03957PES-*` | `SLES-03957` — Pro Evolution Soccer 2 (Europe) **(EsIt)** | `29818` | idem |

Os dois códigos de PES2 são exatamente as **duas releases de trabalho** do
projeto PES2 ([docs/PLAN-PES2-PSX.md](../docs/PLAN-PES2-PSX.md)) — as duas que
moram em `roms/`. `SLES_039.46` foi lido do `(Track 1).bin` da `(EnFrDe)`, e
`SLES-03957` é o da `(EsIt)`, que o plano já registra.

**Nenhum cartão de PES2 serve ao `tools/mcr/`, e nenhum de WE2002 serve ao
`tools/pes2/`.** O `cli.py` procura entrada terminada em `WEW-OPT`; o
`memcard.py` alinha nome de jogador contra o `SELECTC.BIN` do disco de PES2.
Cruzar os dois não dá erro bonito — dá vermelho que parece bug.

## Nem todo cartão é um option file

**Oito dos nove trazem `*-OPT`**, e a maioria carrega outros saves junto. Um não
traz option file nenhum:

| Cartão | Jogo | Tem `*-OPT`? | O que mais tem |
|---|---|---|---|
| `29939` | WE2002 JP | sim | **nada** — só o OPT |
| `first-boot` | WE2002 JP | sim | **nada** — só o OPT |
| `18432` | PES2 EnFrDe | sim | **nada** — só o OPT |
| `17738` | PES2 EnFrDe | sim | ML (`D2A`) |
| `22507` | PES2 EnFrDe | sim | ML (`D2A`) |
| `29818` | PES2 EsIt | sim | ML (`D2A`) |
| `34218` | WE2002 JP | sim | 2 ML (`D2A`, `D2B`) + formação (`D4A`) |
| `7110` | PES2 EnFrDe | sim | ML (`D2A`) + formação (`D4B`) + replay (`R0A`) |
| **`34978`** | WE2002 JP | **não** | **só cup data (`D0A`)** |

Se o critério for "só option file, sem ruído": **`29939`** e
**`we2002-english-first-boot`** (WE2002) e **`18432`** (PES2).

### O que o `*-OPT` guarda, e o que não guarda

O option file é a **tabela de nomes editável** mais as opções — ~1.100 nomes
ASCII por cartão, seleções na ordem do jogo (`Given`, `Dunne`, `Staunton` …
`Nihat`, `Sergen`, `Emre`). É onde mora o "renamed players correctly" de todas
as descrições. **O `29939` (WE2002 japonês) e o `29818` (PES2 EsIt) trazem os
mesmos nomes na mesma ordem** — mesma engine.

O save de Master League **não** guarda nome: 4.331 bytes não-nulos em 16.384, e
9 strings ASCII no cartão inteiro. Elenco por **índice**.

E o cartão não guarda a base do jogo — escalação de clube, atributos, times,
uniformes e bandeiras moram na **imagem de CD**, que é o que o `newWe2002`
edita. Uma consequência a saber antes de estranhar: o `tools/mcr/cli.py dump`
destes cartões sai vazio —

```
   0   1               gk  175   38   15   15   15   15
   1   5               gk  175   38   15   15   15   15
```

Nome em branco, todos `gk`, atributos idênticos. Os 17 destinos de
[wte/re/mcr.md](../wte/re/mcr.md) apontam para a área de **jogador criado /
time editado**, e nenhum destes cartões tem isso — eles têm nome trocado e time
desbloqueado. O dump está lendo área não usada; **não é bug**. Fixture com time
editado de verdade continua sendo cartão gravado à mão.

## Formato: `.gme` nos oito, `.mcr` no nono

Os **oito baixados** são **DexDrive `.gme`**: 134.976 bytes = **3.904 de
cabeçalho** + os 131.072 do cartão cru, que começa em `MC`. O nono é o cartão
cru direto, 131.072 bytes, porque foi assim que o DuckStation o escreveu.

Uma consequência mecânica: o `gme.py --check` varre `mcr/*.gme` e portanto
**não enxerga o `.mcr`** — o gate `mcr_container` continua dizendo `8/8`, e é o
certo, já que não há contêiner nenhum para desmontar ali.

**Desde a [MCR-TASK-16](../docs/tasks/port-mcr/16-conteiner-gme.md) o
`tools/mcr/` lê `.gme` direto** — a decisão é por conteúdo (o tamanho, e o `MC`
em 3904), então a extensão nem precisa estar certa:

```sh
python3 tools/mcr/cli.py info mcr/pro-evolution-soccer-2.29939.gme
python3 tools/mcr/cli.py convert mcr/pro-evolution-soccer-2.29939.gme work/c.mcr
python3 tools/mcr/gme.py --check          # os oito, desmontados e remontados
```

Gravar segue a extensão do destino, e `.gme` sai `.gme` de verdade. O
`tools/pes2/` continua querendo o cartão cru, e para ele o corte manual vale:

```sh
tail -c 131072 mcr/pro-evolution-soccer-2.29939.gme > work/entrada.mcr
```

**Corte pelo fim, não pelo começo**, e o motivo está medido: três dos oito
(`17738`, `18432`, `22507`) têm o **cabeçalho inteiramente zerado** — sem a
assinatura `123-456-STD` que os outros cinco trazem. O `MC` está em 3904 nos
oito assim mesmo, mas um script que valide a assinatura antes de cortar recusa
três arquivos bons. `tail -c 131072` não olha para o cabeçalho.

E é por causa desses três que **o caminho de volta preserva o cabeçalho em vez
de regerá-lo**: síntese assina o que faz, e nenhum cabeçalho sintetizado é
3.904 zeros. Medido: `.gme` → cartão → `.gme` dá o **mesmo arquivo nos oito**
quando o cabeçalho viaja junto, e em **dois dos oito** quando ele é
sintetizado. Os bytes de `0x27` a `0x34` — quase todos `0xFF`, com um `0x03`,
`0x05` ou `0x07` avulso — não são entendidos.

## Winning Eleven 2002 (Japão), `SLPM-87056`

Mesma release de `roms/japanese-shift-jis.bin`. Descrição do publicador em
itálico; o resto é o que o diretório do cartão diz.

### `pro-evolution-soccer-2.29939.gme`

*All teams unlocked. All team names edited to english.*

| Bloco | Estado | Entrada | Título (Shift-JIS) |
|---|---|---|---|
| 1–2 | `0x51`/`0x53` | `…WEW-OPT` | ＷＳウイニングイレブン２００２オプションファイル |

Um save só, o **option file** de 16.384 bytes — exatamente o que o `tools/mcr/`
edita. `cli.py info` acha e reporta `bad checksums none`. Os outros 13 blocos
livres (`0xA0`).

### `pro-evolution-soccer-2.34218.gme`

*National team players' names are in English with loads of typos corrected.
Bonus teams and secret stadium unlocked. Manual cursor, hard difficulty, normal
speed, wide camera by default. Two Master League clubs with 175-200 transfer
credits.*

O mais cheio dos três — **quatro saves**, 9 blocos usados:

| Bloco | Entrada | Título | Tamanho |
|---|---|---|---|
| 1–2 | `…WEW-D2A` | ＷＳウイニングイレブン２００２ｏｆ Ｍａｓｔｅｒ ｌ１ | 16.384 |
| 3–4 | `…WEW-D2B` | ＷＳウイニングイレブン２００２ｏｆ Ｍａｓｔｅｒ ｌ２ | 16.384 |
| 5 | `…WEW-D4A` | ＷＳウイニングイレブン２００２フォーメーションデータ１ | 8.192 |
| 7–8 | `…WEW-OPT` | ＷＳウイニングイレブン２００２オプションファイル | 16.384 |

`D2A`/`D2B` são os **dois clubes de Master League** que a descrição cita; `D4A`
é o arquivo de formações. O `cli.py info` pega o `OPT` nos blocos 7–8 e lista os
demais como `outside chain`, que é o certo: ele edita o option file e não sabe o
que é o resto.

**É o melhor candidato a `WE2002_MCR_CARD`** — tem o option file *e* vizinhos
que exercitam o "não escrever fora da cadeia".

### `pro-evolution-soccer-2.34978.gme`

*Very strong master league team.*

| Bloco | Entrada | Título |
|---|---|---|
| 1–2 | `…WEW-D0A` | ＷＳウイニングイレブン２００２カップデータ１ |

**Não serve para o `tools/mcr/`**: o único save é `D0A` — *cup data* —, e **não
há `WEW-OPT` no cartão**. O `cli.py info` recusa com a mensagem certa:

```
error: no WE2002 save in the directory. The 15 entries in use or not are named
['BISLPM-87056WEW-D0A', 'BASCUS-94254PRO-00']; what is looked for is a
first-block entry whose name ends in WEW-OPT.
```

**`カップデータ` não é Master League.** A descrição diz "very strong master
league team", mas no diretório não há `D2A`/`D2B`. Ou o time forte foi gravado
dentro do save de copa, ou a descrição é do pacote e não do arquivo. Não foi
investigado — este README diz o que o cartão diz.

### `we2002-english-first-boot.mcr`

**Um option file criado pelo próprio jogo, na primeira execução, a partir de uma
ROM traduzida para o inglês.** Não veio de pacote de terceiro nem de editor:
saiu de `roms/we2002-english/we2002-english.bin` rodando sob o fork do
DuckStation, por `make we2002-play-fresh`, com o diretório de cartões vazio; o
jogo criou o cartão e gravou nele. 2026-09-10.

| Bloco | Estado | Entrada | Tamanho |
|---|---|---|---|
| 1–2 | `0x51`/`0x53` | `BISLPM-87056WEW-OPT` | 16.384 |

Um save só, e `cli.py info` reporta `bad checksums none`.

**Por que ele estava faltando.** A [MCR-TASK-13](../docs/tasks/port-mcr/13-oraculo-e-veredito.md)
fechou com o veredito do console **não obtido**, e a razão era de código de
produto: a fixture do ciclo é `BISLPM-86600WEW-OPT`, e os discos desta máquina
são `SLPM-87056`. Um jogo de PSX acha o save dele pelo nome, então aquele
cartão é invisível para eles. A rota que a task deixou escrita — subir um disco
`SLPM-87056` com cartão vazio e deixar o jogo criar o seu — é exatamente o que
produziu este arquivo. **Ele é o primeiro `BISLPM-87056WEW-OPT` desta pasta que
o jogo escreveu**, e é a entrada dos dois passos que faltam: editá-lo com o
port e devolvê-lo ao jogo.

**O `dump` dele sai vazio, e não é bug** — mesma razão dos outros oito, descrita
na seção "O que o `*-OPT` guarda": não há time editado, e os 17 destinos de
[wte/re/mcr.md](../wte/re/mcr.md) apontam para a área de jogador criado.

**O que ele mostra e nenhum dos oito mostrava: bloco livre de cartão de
emulador é `0xFF`, não zero.**

```
outside chain   block 3, state 0xa0, 8192 non-zero bytes
...
outside chain   block 15, state 0xa0, 8192 non-zero bytes
```

Treze linhas dessas, e o `29939` — que também tem só o `OPT` — não emite
nenhuma, porque os blocos livres dele são zeros. Os 8.192 "não-zero" aqui são
`0xFF` puro, o preenchimento do DuckStation.

Isso importa por um motivo concreto: o editor do Obocaman grava **formação,
tática, cobradores e capitão** em `0x6102`–`0x6500`, que é **bloco 3** — fora
da cadeia declarada `[1, 2]`. O molde `dat.bin` dele entrega esse bloco
**zerado**; um cartão de verdade o entrega `0xFF`. É o estado que a MCR-TASK-13
manda levar ao experimento, e ainda falta o passo que o preenche.

## Pro Evolution Soccer 2 (Europa)

Os cinco trazem o mesmo `PES-OPT` de 16 KiB, título
`ＰｒｏＥｖｏｌｕｔｉｏｎＳｏｃｃｅｒ２　ＯＰＴＩＯＮ　ＦＩＬＥ` — é a
**tabela de nomes editável** — o plano de PES2 descreve esse mesmo
`BESLES-03957PES-OPT` de 16 KiB como "as opções e a tabela de nomes editável".
É onde mora o "renamed players" de todas as descrições.

### `pro-evolution-soccer-2.17738.gme` — `SLES-03946` (EnFrDe)

*Edited renaming every players correctly, unlocked 8hiden teams*

| Bloco | Entrada | Título |
|---|---|---|
| 1–2 | `…PES-OPT` | ＯＰＴＩＯＮ ＦＩＬＥ |
| 3–4 | `…PES-D2A` | ＭＡＳＴＥＲ Ｌ．１ |

### `pro-evolution-soccer-2.18432.gme` — `SLES-03946` (EnFrDe)

*GOOD saved file ~ Unlocked 9hiden teams & Renamed players correctly*

Só o `PES-OPT` nos blocos 1–2; 13 blocos livres. **É o cartão mais limpo dos
cinco** — nenhum save de Master League para confundir uma leitura de elenco.

### `pro-evolution-soccer-2.22507.gme` — `SLES-03946` (EnFrDe)

*BEST saved file - 9hiden teams & 32 Clubs. With mega-mix AS ROMA (ML) built-up
good in the Div.2*

| Bloco | Entrada | Título |
|---|---|---|
| 1–2 | `…PES-OPT` | ＯＰＴＩＯＮ ＦＩＬＥ |
| 3–4 | `…PES-D2A` | ＭＡＳＴＥＲ Ｌ．１ |

Mesma forma do `17738`. A AS Roma da descrição está no `D2A`.

### `pro-evolution-soccer-2.29818.gme` — `SLES-03957` (EsIt)

*Save game for Pro Evolution Soccer 2 (Es-It). Real names & 9 hidden teams
unlocked.*

| Bloco | Entrada | Estado | Título |
|---|---|---|---|
| 1–2 | `…PES-OPT` | `0x51`/`0x53` | ＯＰＴＩＯＮ ＦＩＬＥ |
| 3–4 | `…PES-D2A` | `0x51`/`0x53` | ＭＡＳＴＥＲ Ｌ．１ |

**É o único que casa com a `(EsIt)` de `roms/`**, e por isso o único que o
`tools/pes2/memcard.py` pode alinhar contra um disco que temos:

```sh
tail -c 131072 mcr/pro-evolution-soccer-2.29818.gme > work/29818.mcd
python3 tools/pes2/memcard.py work/29818.mcd \
  "roms/Pro Evolution Soccer 2 (Europe) (EsIt)/"*"(Track 1).bin" --check
```

O `--check` **falha**, e é o esperado — vale entender antes de perder tempo:

```
CHECK FAILED: {'exact': 1, 'selectc': 1, 'boot': 0, 'partial': 4}
            != {'exact': 54, 'selectc': 49, 'boot': 5, 'partial': 0}
```

O gate espera um cartão **de fábrica**, cujos 115 nomes (5 elencos × 23) batem
byte a byte com o `SELECTC.BIN` do disco. Este cartão tem "real names" —
editados de propósito —, então quatro dos cinco elencos casam **parcialmente**
(22/23) e um não casa. **Não é bug do cartão nem da ferramenta: é a edição.**
Consequência prática: **não aponte `WE2002_PES2_CARD` para cá** — o `pes2_image`
do `ctest` ficaria vermelho. O cartão do gate é o do próprio DuckStation, em
`~/.local/share/duckstation/memcards/`.

Para leitura ele serve bem, e serve para uma coisa que o cartão de fábrica não
faz: mostrar **como um nome editado sai** de dentro do `PES-OPT`.

### `pro-evolution-soccer-2.7110.gme` — `SLES-03946` (EnFrDe)

*Promoted to Div.1 n' built up a fairly good team. Good luck in the first div!!*

| Bloco | Entrada | Título |
|---|---|---|
| 1–2 | `…PES-OPT` | ＯＰＴＩＯＮ ＦＩＬＥ |
| 4 | `…PES-D4B` | ＦＯＲＭＡＴＩＯＮ２ |
| 5–6 | `…PES-D2A` | ＭＡＳＴＥＲ Ｌ．１ |
| 7–8 | `…PES-R0A` | ＲＥＰＬＡＹ１ |

O mais variado dos cinco: tem **formação** e **replay** além do option file e da
Master League, e um buraco no bloco 3 (livre entre saves usados).

**A descrição diz "North America" e o cartão diz outra coisa.** A entrada é
`BESLES-03946PES-*` — prefixo `BE`, disco `SLES`, o europeu `(EnFrDe)`. Um save
norte-americano traria `BASLUS-*`. Trate-o como europeu; foi assim que ele foi
gravado.

## Ruído de diretório que engana

Duas coisas aparecem como se fossem save e não são. As duas já custaram leitura
errada:

- **`N.Kanu`, `Kanu`, `BASCUS-94254PRO-00`.** Bloco de continuação (estado
  `0x53`) **não tem título nem nome próprios** — o que se lê ali é o que sobrou
  do save que ocupava o bloco antes. `N.Kanu` aparece em cinco dos oito
  cartões, e `BASCUS-94254PRO-00` no bloco 2 do `34978`, que **pertence ao
  `D0A`**.
- **Ler nome de entrada sem olhar o estado inventa saves que não existem.** É a
  distinção que a mensagem de erro do `cli.py` faz questão de explicar: *"an
  entry whose state is not 0x51 is not a first block, however right the name
  looks."*

## Versionamento

**Esta pasta entra no git**, os oito `.gme` inclusive — decisão de 2026-09-09.
São 8 × 132 KiB de fixture de leitura com procedência conhecida, e um clone que
os traga junto reproduz o que este README mede sem depender de download.

**O nono entrou em 2026-09-10, e é de outra natureza.** Os oito são públicos e
baixados; o `we2002-english-first-boot.mcr` foi gravado nesta máquina. O que o
mantém dentro da exceção é o resto do critério: 128 KiB, checksum registrado
abaixo, e é o estímulo de uma medição que nenhum dos oito consegue ser — o
único `BISLPM-87056WEW-OPT` que existe. E o que o separa de "save do usuário"
é ele não ter partida nenhuma dentro: um option file de primeira execução, sem
Master League e sem time editado.

**É exceção, e a regra continua valendo para o resto.** Cartão de jogo do
usuário — `work/entrada.mcr`, o `WE2002_MCR_CARD`, e o do DuckStation — fica
fora, como `roms/` e `we-team-editor/` (ver [CLAUDE.md](../CLAUDE.md)). O que
separa: aqui são arquivos públicos, pequenos, com checksum registrado, e são o
estímulo de uma medição; lá é o save do usuário e são centenas de MB.

Checksums, para conferir que ninguém gravou por cima:

```
69dc7387448cd44e0795d8fcf2906f76  pro-evolution-soccer-2.17738.gme
e4633df68dfd9c92835c61a7643df955  pro-evolution-soccer-2.18432.gme
791fcf129928a7efc3e3bfebaa876827  pro-evolution-soccer-2.22507.gme
99630cd3d919771d38084fa6aeaa1367  pro-evolution-soccer-2.29818.gme
3fb863239635235294cf56de6a49b771  pro-evolution-soccer-2.29939.gme
c16f4d8cc9b8ad30ce63c913fece4c76  pro-evolution-soccer-2.34218.gme
6f16010ac3b9c51f62781d3d4bc83fc3  pro-evolution-soccer-2.34978.gme
e38289da6bf579bd90ac44cdf3956f84  pro-evolution-soccer-2.7110.gme
72626c3bed4c773d8d9ca383f11a1661  we2002-english-first-boot.mcr
```

**Trabalhe sobre cópia**, como em todo o resto do repositório: os editores
gravam in-place.
