# O option file do WE2002, mapeado

**Medido entre 2026-09-10 e 2026-09-12**, sobre a release japonesa
`SLPM-87056`, em **trinta cartões** — a maioria gravada pelo jogo rodando sob o
fork do DuckStation, o resto montado por sonda e confirmado na tela.

Este é o **mapa consolidado**: a estrutura do save, o que cada byte conhecido
significa, e o que continua obscuro. A medição de cada campo, com as corridas
que a sustentam, fica nos três arquivos ao lado:

| arquivo | o que mede |
|---|---|
| [`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md) | a câmera, e a série de testes que provou a gravação nos dois sentidos |
| [`/docs/MCR-OPCOES-JOGO.md`](/docs/MCR-OPCOES-JOGO.md) | as cinco de tela, a velocidade e as cinco de som |
| [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md) | os times secretos, o Club House e os times de ML no modo exibição |

Quem lê e grava é o [`../tools/mcr/options.py`](../tools/mcr/options.py) — hoje
só a câmera tem API; os outros campos se alcançam pelas peças dele.

---

## 1. Onde o save mora

```
BISLPM-87056WEW-OPT     state 0x51     16.384 bytes     cadeia [1, 2]
```

**O bloco não é o endereço, e isso é medido.** O save foi movido para os blocos
3-4 e o jogo **carregou e gravou** normalmente — o console segue o diretório, na
leitura e na escrita. Os cartões desta máquina o têm no bloco **1**; os 17
destinos absolutos do editor do Obocaman o esperam no **2**.

Por isso **todo endereço desta página é derivado**, não constante:

```
bloco do save          ← a entrada do diretório
+ 128                  ← o cabeçalho do save PSX
+ 128 × quadros_icone  ← o próprio cabeçalho diz quantos são (1, aqui)
= primeiro byte de dados
```

Com o save no bloco 1 isso dá `0x02100`; no bloco 3, `0x06100`. **As colunas
`addr` desta página valem para o bloco 1.**

### O cabeçalho, antes dos dados

| faixa (bloco 1) | o que é |
|---|---|
| `0x02000..0x02004` | `"SC"`, o byte de quadros de ícone (`0x11`) e a contagem de blocos |
| `0x02004..0x02044` | o título, em Shift-JIS, terminado em `00 00` |
| `0x02034..0x02044` | **o padding do título — não é dado** (ver §6) |
| `0x02060..0x02080` | a CLUT do ícone |
| `0x02080..0x02100` | o ícone, 16×16 4bpp |

---

## 2. O formato: registros com soma própria

Os dados são uma sequência de registros, cada um com o tamanho e a verificação
na frente:

```
[u16 tamanho, little-endian][u8 checksum][payload]
```

```
checksum = ( soma dos bytes do payload ) mod 256
```

**Dois registros**, e eles **não são contíguos**:

| # | header | tamanho | payload | checksum | conteúdo |
|---|---|---:|---|---|---|
| 0 | `0x02100` | 134 | `0x02103..0x02189` | `0x02102` | **as opções** (§3) |
| 1 | `0x02200` | 12.420 | `0x02203..0x05287` | `0x02202` | os nomes editados (§4) |

Entre o fim do registro 0 e o começo do registro 1 há **119 bytes de zeros**.
Quem percorrer a cadeia por `offset + 3 + tamanho` cai nesse buraco, lê tamanho
zero e conclui que o save tem **um** registro só. Os offsets `0x000` e `0x100`
são uma tabela por esse motivo.

### O jogo confere a soma, e reclama alto

Gravar dentro de um payload sem refazer o byte de checksum produz **`ERROR` na
carga do option file**, e o jogo para ali. Medido trocando um byte só.

Três coisas que essa medição deu de brinde:

- **ele não encosta no cartão** — o digest depois da recusa é o de antes;
- **a soma que ele produz é a nossa** — gravando pela tela do jogo, ele escreveu
  o mesmo byte que o `options.checksum()` calcula;
- o sintoma é **alto**, não silencioso. A documentação já disse o contrário, por
  dedução, e estava errada.

> **O `0x02202` do [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md) é
> este `checksum` do registro 1.** Aquela medição chegou nele por busca de faixa
> somada, achou `27.250` faixas consistentes e registrou o começo e o fim
> **mínimos** — `0x02186` e `0x04e30` —, deixando o fim "indeterminado ao byte".
> O header do registro declara o fim: **`0x05287`**. As duas leituras são a
> mesma regra, uma achada sem conhecer o formato e a outra explicada por ele.

---

## 3. O registro 0 — as opções

**134 bytes.** Nos trinta cartões, **treze** offsets variam: onze com nome, dois
sem. Os outros 121 são iguais em todos — o que não quer dizer que sejam fixos, e
sim que nenhuma sonda os moveu.

| offset | addr | campo | valores |
|---:|---|---|---|
| 0 | `0x02103` | — | `00` em todos |
| **1** | `0x02104` | **câmera** | 0..8, tabela abaixo |
| 2..105 | `0x02105..0x0216C` | — | 50 × `u16` LE, constantes; têm cara de máscaras de pad |
| **106..107** | `0x0216D..6E` | **velocidade do jogo** | `u16` = `552 − 8 × barras` |
| 108 | `0x0216F` | — | `00` em todos |
| **109** | `0x02170` | ❓ **obscuro** | `0x00` ou `0x10` |
| **110** | `0x02171` | **Sound Volume** | 0..31 |
| **111** | `0x02172` | **BGM Volume** | 0..31 |
| **112** | `0x02173` | **Commentary Volume** | 0..31 |
| **113** | `0x02174` | **Commentary** | `1` = ON, `0` = OFF |
| **114** | `0x02175` | **Audio** | `0` = STEREO, `1` = MONO |
| **115** | `0x02176` | **opções de tela** | 5 campos num byte, abaixo |
| 116..125 | `0x02177..0x02180` | — | `c0 00 f0 00 00 00 01 01 01 07` |
| **126** | `0x02181` | ❓ **obscuro** | `0x00` ou `0x02` |
| 127..128 | `0x02182..83` | — | `00 00` |
| **129..130** | `0x02184..85` | **desbloqueios** | 16 bits, abaixo |
| 131..133 | `0x02186..88` | — | `00 00 00` |

**Os offsets 106 a 115 são um bloco contíguo de opções**, e o **109** está sem
nome no meio dele, cercado dos dois lados.

### 3.1 A câmera — offset 1

| valor | câmera | | valor | câmera |
|---:|---|---|---:|---|
| 0 | `normal-near` | | 5 | `zoom` |
| 1 | `normal-mid` ← default | | 6 | `ov-near` |
| 2 | `normal-far` | | 7 | `ov-mid` |
| 3 | `wide` | | 8 | `ov-far` |
| 4 | `tv` | | | |

**As nove foram vistas na tela**, por três rotas: quatro lidas do que o jogo
gravou, quatro escritas por nós e reconhecidas por ele, e o `tv` que o jogo
escreveu num cartão que já tínhamos editado. Nenhuma resta por inferência.

### 3.2 A velocidade — offsets 106..107

```
u16 little-endian = 552 − 8 × barras        (0 a 16 barras)
```

`0x0228` em zero barras, `0x01E8` em oito, `0x01A8` em dezesseis. Só os bits 6
a 9 se mexem. **O valor cresce quando as barras diminuem** — tem cara de
intervalo, não de velocidade, mas isso é leitura da forma, não medição.

### 3.3 Os volumes — offsets 110..112

```
leitura   barras = ceil(valor / 2)
escrita   valor  = min(2 × barras, 31)
```

Cinco bits; os bits 5 a 7 são zero em todos os cartões. As quinze primeiras
barras andam de dois em dois e a décima sexta anda **um**, porque `32` não cabe
em cinco bits.

**Valor ímpar não é estável.** `31` é o único ímpar que o jogo produz; gravar
`13` mostra 7 barras, e na próxima vez que o jogador salvar qualquer coisa o
jogo escreve `14` por cima.

### 3.4 As opções de tela — offset 115

| bits | máscara | campo | valores |
|---|---|---|---|
| 1–0 | `0x03` | **Radar** | `0` = OFF, `1` = UP, `2` = DOWN |
| 2 | `0x04` | **Player Name** | `1` = ON |
| 3 | `0x08` | **Timer** | `1` = ON |
| 4 | `0x10` | **Score** | `1` = ON |
| 5 | `0x20` | **Strategy** | `1` = ON |
| 7–6 | `0xC0` | ❓ **obscuro** | `00` em todos |

O limpo vale `0x3E`. **A ordem do valor do radar não é a da tela** — a tela
mostra *DOWN, OFF, UP*.

### 3.5 Os desbloqueios — offsets 129..130

`u16` little-endian, um bit por item.

| bit | máscara | o que liga | | bit | máscara | o que liga |
|---:|---|---|---|---:|---|---|
| 0 | `0x0001` | Euro A.S. | | 6 | `0x0040` | Clas. Brazil |
| 1 | `0x0002` | Class. England | | 7 | `0x0080` | Cl. Argentina |
| 2 | `0x0004` | Clas. France | | 8 | `0x0100` | **times de ML no modo exibição** |
| 3 | `0x0008` | Clas. Nether | | 9 | `0x0200` | **estádio Club House** |
| 4 | `0x0010` | Class. Italy | | 10 | `0x0400` | World A.S. |
| 5 | `0x0020` | C. Germany | | 11..15 | `0xF800` | ❓ **obscuro** |

Os onze conhecidos ligados de uma vez são `ff 07`.

---

## 4. O registro 1 — os nomes

**12.420 bytes**, `0x02203..0x05287`. São os nomes editados de jogador, em
texto legível (`Given`, `Dunne`, `Staunton`, …). **Nada além disso foi
mapeado**: não se sabe a estrutura de entrada, se há índice, nem se há outros
campos junto.

É o maior pedaço não mapeado do save — 12.420 dos 16.384 bytes.

---

## 5. O que fica fora dos registros

### 5.1 Dentro do save, depois do registro 1

`0x05287..0x06000` — **3.449 bytes**, dos quais 2.447 não são zero. Essa região
**não segue o formato de registro**: uma varredura por header com soma válida
devolve só falsos positivos em áreas zeradas.

É onde caem **três** dos 17 destinos do editor de time:

| addr | o que é |
|---|---|
| `0x05404` | os 23 dorsais, 5 bits cada |
| `0x05904` | os atributos, 12 B por jogador, stride 32 |
| `0x05910` | os nomes, 10 B por jogador, stride 32 |

**Os três estão fora das duas somas conhecidas**, porque caem depois do fim do
registro 1. Isso é evidência — não prova — de que o editor de time pode gravar
ali sem refazer verificação nenhuma. Ver §7.

### 5.2 Fora da cadeia: o bloco 3

Os outros **catorze** destinos do editor de time caem no bloco 3, que o
diretório marca como **livre** (`0xA0`): formação, cobradores, táticas e
capitão. O `card.py` os reporta como `stray_blocks`.

---

## 6. O padding do título — ruído, não dado

`0x02034..0x02044`, os bytes depois do `00 00` que fecha o título. Memória não
inicializada que o jogo deixa ali; muda a cada gravação.

**Quem prova que não é dado é o próprio jogo:** duas gravações dele sem mudança
nenhuma de conteúdo diferem nessa faixa. Todo diff de option file mostra esses
bytes; descarte-os, mas **conte-os** — diferença que passe dessa faixa é
diferença de verdade.

> Isto aperta uma frase do [`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md):
> "a gravação do jogo é determinística — salvar sem mudar nada devolve o mesmo
> md5". Vale **quando o padding está zerado**, que é o caso dos cartões de
> primeira execução daquela medição.

---

## 7. O que continua obscuro

Em ordem do que parece mais alcançável:

| o quê | onde | o que se sabe |
|---|---|---|
| **offset 109** | `0x02170` | dois valores, `0x00` e `0x10`. Está **dentro** do bloco de opções, entre a velocidade e os volumes — se houver uma opção nesse menu ainda não mexida, é o candidato |
| **offset 126** | `0x02181` | dois valores, `0x00` e `0x02` |
| **bits 6–7** das opções de tela | `0x02176` | `00` em todos |
| **bits 11–15** dos desbloqueios | `0x02185` | nada observável — mas ver a ressalva abaixo |
| **radar `3`** | `0x02176` | o quarto valor dos dois bits não existe na tela |
| **velocidade fora de `0..16`** | `0x0216D` | nada diz o que o jogo faz abaixo de 424 ou acima de 552 |
| **os 121 bytes constantes** | registro 0 | iguais em trinta cartões; os 104 de `0x02105` têm cara de máscaras de pad |
| **o registro 1** | `0x02203..0x05287` | 12.420 bytes; sabe-se que são nomes, e nada da estrutura |
| **a região `0x05287..0x06000`** | — | 2.447 bytes não-zero, sem formato de registro; contém a área de jogador |
| **o padding do título** | `0x02034` | 15 bytes; zero é aceito pelo jogo |

> **"Nada observável" não quer dizer "vazio".** O bit 9 dos desbloqueios ficou
> dois dias nesta lista e saiu dela quando se olhou **outra tela** — ele é o
> Club House, e o teste em grupo que o mapeou já tinha a resposta: a coluna de
> observação registrava a tela de seleção de times, e um estádio não aparece
> nela. Todo item acima deve ser lido como *não procurado o bastante*.

### A pergunta em aberto que mais importa

**O editor de time nunca foi aberto no console.** O `tools/mcr/` grava dorsais,
atributos, nomes, formação, cobradores e capitão, e **nenhum caminho de escrita
dele refaz soma alguma**.

A §5.1 mostra que os três destinos dentro do save caem **fora** das duas somas
conhecidas, e os catorze restantes caem fora do save inteiro. Isso é evidência
a favor — não prova, porque pode haver verificação que esta medição não achou.

O teste é uma corrida: gravar um atributo pelo `cli.py set`, trocar o cartão,
abrir. Se der `ERROR`, o editor precisa refazer a soma, e o formato do §2 já dá
a ferramenta pronta.

---

## 8. Como se mede

O jogo é a **única** fonte de cartão válido, então toda série parte de um
cartão que ele gravou. Duas formas, e as duas foram usadas:

**Do jogo para nós** — mudar uma opção na tela, salvar, e comparar com o limpo.
Prova o decodificador, e só ele: cartão que o jogo salvou é cartão que ele já
aceitou.

**De nós para o jogo** — montar a sonda, trocar o cartão, e olhar a tela. É a
direção que importa para uma ferramenta de escrita, e a única que alcança
valores que a interface do jogo **não consegue produzir** — foi assim que o
arredondamento dos volumes saiu de `ceil` ou `floor` para `ceil`, com um valor
ímpar.

```sh
python3 - <<'EOF'
import sys; sys.path.insert(0, "tools/mcr")
import options
from card import Card

c = Card.from_file("work/cards/limpo.mcr")
rec = options.record(c, 0)

c.write(rec.payload + 1, bytes([5]))                 # camera zoom
c.write(rec.payload + 115, bytes([0x3D]))            # radar UP, resto ON
c.write(rec.payload + 110, bytes([min(2 * 8, 31)]))  # sound volume, 8 barras
c.write(rec.payload + 129, (0x07ff).to_bytes(2, "little"))   # tudo desbloqueado

c.write(rec.header + 2,                              # SEM ISTO, o jogo da ERROR
        bytes([options.checksum(bytes(c.data[rec.payload:rec.payload + rec.size]))]))
open("work/sonda.mcr", "wb").write(c.to_bytes())
EOF

python3 tools/mcr/options.py work/sonda.mcr          # confere a soma antes de trocar
cp work/sonda.mcr "<memcards>/World Soccer Winning Eleven 2002 (Japan)_1.mcd"
```

**Feche o emulador antes de trocar o arquivo** — ele reescreve o cartão ao
sair, e a sonda vai junto.

Três hábitos que pagaram, cada um depois de custar:

- **um controle que volta ao valor original**, na mesma série. Devolver o radar
  a DOWN devolve o byte e o cartão fica idêntico ao limpo; sem isso, uma leitura
  certa por acaso passa igual;
- **um ponto entre os que o jogo produz**. Amostras em `0`, `8` e `16` barras
  são todas múltiplas de oito e não distinguem escala nenhuma — a sonda em 4
  barras é que tirou o passo de interpolação;
- **conferir a soma antes de trocar o cartão**. `options.py <arquivo>` diz `ok`
  ou `BAD` em uma linha, e poupa um boot que ia dar `ERROR`.
