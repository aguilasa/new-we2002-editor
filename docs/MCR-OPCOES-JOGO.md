# As opções de jogo no option file do WE2002

**Medido em 2026-09-12**, sobre a release japonesa `SLPM-87056`, num cartão do
usuário gravado pelo jogo rodando sob o fork do DuckStation.

O que este arquivo diz é onde o option file guarda as opções do menu de jogo e
como reescrevê-las sem que o jogo recuse o cartão:

- as **cinco opções de tela** — radar, nome do jogador, cronômetro, placar e
  estratégia —, todas num byte;
- a **velocidade do jogo**, a barra de dezesseis divisões, num `u16`;
- as **cinco opções de som** — modo, narração e os três volumes —, em cinco
  bytes consecutivos.

Tudo isso vive no **registro 0** do save, em onze bytes entre os offsets 106 e
115. O mapa consolidado do registro está em
[`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md#o-mapa-do-registro-0).

É o papel que [`../wte/re/mcr.md`](../wte/re/mcr.md) faz para os 17 destinos do
editor do Obocaman: **fonte de endereços**, para a ferramenta citar.

## As opções de tela: **um byte**, no offset 115 do registro 0

As cinco cabem num byte só. **Não é um endereço absoluto**: o save
`BISLPM-87056WEW-OPT` pode morar em qualquer bloco, medido em
[`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md#onde-o-save-mora), então o que vale
é o offset.

```
byte 115 (0x73) do payload do registro 0
```

Nos cartões desta máquina, com o save no bloco 1, isso cai em **`0x02176`**.

| Bits | Máscara | Opção | Valores |
|---|---|---|---|
| 1–0 | `0x03` | **Radar** | `0` = OFF, `1` = UP, `2` = DOWN |
| 2 | `0x04` | **Player Name** | `1` = ON, `0` = OFF |
| 3 | `0x08` | **Timer** | `1` = ON, `0` = OFF |
| 4 | `0x10` | **Score** | `1` = ON, `0` = OFF |
| 5 | `0x20` | **Strategy** | `1` = ON, `0` = OFF |
| 7–6 | `0xC0` | — | `00` nos dezenove cartões medidos; não identificados |

O cartão limpo vale **`0x3E`** = `0011 1110`: radar em `10` = DOWN, e os quatro
flags ligados.

**A ordem do valor não é a da tela.** A tela mostra *DOWN, OFF, UP*; o byte
guarda `OFF = 0`, `UP = 1`, `DOWN = 2`. Quem tomar a posição na tela como o
valor grava a opção errada e ela ainda parece plausível.

**O radar é o único campo de dois bits.** Os outros quatro são flag, e todos com
a mesma polaridade: `1` é ligado.

## A verificação: sem refazer a soma, o jogo dá `ERROR`

O byte cai dentro do payload do registro 0, e todo registro carrega o próprio
checksum na frente. A regra, e a busca de faixa que a sustenta, estão em
[`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md#a-verificação-sem-recalcular-o-jogo-recusa-o-cartão);
a forma que o módulo usa é:

```
byte(header + 2) = ( soma do payload que o header declara ) mod 256
```

Gravar este byte sem refazer a soma produz **`ERROR`** ao carregar o option
file — medido sobre o byte da câmera, que vive no mesmo registro, e registrado
em [`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md).

**Essa dependência aparece sozinha nos dados**, e é o que confirma que a leitura
está certa. Em cada um dos seis cartões, a soma se moveu **exatamente** o mesmo
tanto que o byte:

| cartão | byte | checksum |
|---|---:|---:|
| `radar-off` | −2 | −2 |
| `radar-up` | −1 | −1 |
| `player-name-off` | −4 | −4 |
| `timer-off` | −8 | −8 |
| `score-off` | −16 | −16 |
| `strategy-off` | −32 | −32 |

Se algum outro byte do registro tivesse mudado junto, os dois deltas
divergiriam. Não divergem em nenhum dos seis.

## A velocidade do jogo: um `u16`, nos offsets 106–107

A barra de velocidade tem **dezesseis divisões** e vai de 0 a 16 acesas. O
cartão limpo tem 8.

```
u16 little-endian nos bytes 106..107 (0x6A..0x6B) do payload do registro 0
```

Nos cartões desta máquina, com o save no bloco 1, isso cai em
**`0x0216D..0x0216E`**.

```
u16 = 552 - 8 × barras
```

Quatro pontos medidos, e a reta passa exatamente pelos quatro:

| barras | bytes | `u16` | `552 − 8×barras` |
|---:|---|---:|---:|
| 0 | `28 02` | 552 (`0x0228`) | 552 |
| 4 | `08 02` | 520 (`0x0208`) | 520 |
| 8 | `e8 01` | 488 (`0x01E8`) | 488 |
| 16 | `a8 01` | 424 (`0x01A8`) | 424 |

**O valor cresce quando as barras diminuem.** Zero barras é o maior número, e
isso tem cara de **intervalo** e não de velocidade — mais barras, passo menor.
É leitura da forma do dado, não medição: nada aqui olhou o que o motor faz com
o número.

**Só quatro bits se mexem**, os 6 a 9; os outros doze ficam em `0x0028` nos
quatro cartões. Os três de baixo serem sempre zero é o que faz o passo ser 8:
lido como `u16 >> 3`, o campo é simplesmente **`69 − barras`**, e vai de 69 a
53. Qual das duas leituras o jogo usa não foi determinado, e para escrever dá
no mesmo.

### O quarto ponto é que fecha isso, e ele veio do lado inverso

Os três primeiros cartões eram `0`, `8` e `16` — **todos múltiplos de 8**. A
reta passava pelos três, mas "cada barra vale 8" era interpolação: um jogo que
só gravasse em degraus de oito barras produziria dados idênticos.

Em vez de pedir mais um cartão ao jogo, a sonda foi montada do outro lado:
gravar `520`, que a reta prevê como **4 barras**, e olhar a tela. Apareceram
quatro. Uma corrida, e a escala deixa de ser interpolação.

## As opções de som: **cinco bytes**, nos offsets 110 a 114

Cinco campos independentes, um byte cada, consecutivos. Nenhum compartilha bits
com outro: cada sonda moveu exatamente um byte.

| offset | addr | campo | valores |
|---:|---|---|---|
| 110 | `0x02171` | **Sound Volume** | 0..31 |
| 111 | `0x02172` | **BGM Volume** | 0..31 |
| 112 | `0x02173` | **Commentary Volume** | 0..31 |
| 113 | `0x02174` | **Commentary** | `1` = ON, `0` = OFF |
| 114 | `0x02175` | **Audio** | `0` = STEREO, `1` = MONO |

Os três volumes cabem em **5 bits** — os bits 5 a 7 são zero nos dezenove
cartões, e nenhum valor passa de `0x1F`.

### A escala dos volumes, e os dois sentidos dela

A barra tem dezesseis divisões e o cartão limpo tem doze.

```
leitura   barras = ceil(valor / 2) = (valor + 1) // 2
escrita   valor  = min(2 × barras, 31)
```

Seis pontos medidos, e os seis batem:

| valor | barras | de onde |
|---:|---:|---|
| 0 | 0 | `sound-*-volume-0` |
| 2 | 1 | sonda |
| 10 | 5 | sonda |
| 13 | **7** | sonda, valor **ímpar** |
| 24 | 12 | o limpo |
| 31 | 16 | `sound-*-volume-16` |

**As duas fórmulas não são inversas exatas, e o topo é o que as separa.** As
quinze primeiras barras andam de dois em dois; a décima sexta anda **um**,
porque `32` não cabe em 5 bits. Ler `31` devolve 16, então o par fecha — mas
`31` é o **único valor ímpar que o jogo produz**.

**Valor ímpar não é estável.** Gravar `13` mostra 7 barras, e se o jogador
mexer em qualquer coisa e salvar, o jogo escreve `14` no lugar. Quem editar
esses bytes por fora deve escrever pares, ou aceitar que o número muda sozinho
na primeira gravação.

### O valor ímpar é que deu a regra

Os três cartões originais eram `0`, `12` e `16` barras — e `min(2 × barras, 31)`
os explica, mas `ceil(valor/2)` também, e qualquer curva que passe pelos três.
Nenhum deles diz o que acontece **entre** as barras, porque a interface do jogo
não consegue produzir um valor ímpar.

A sonda levou os três volumes de uma vez, com valores diferentes: `10`, `13` e
`2`. Uma corrida, três respostas — e a do meio, o `13`, é a que fixou o
arredondamento em `ceil`. Com `floor` teria mostrado 6.

## Como a medição das cinco de tela foi feita

O jogo é a única fonte de cartão válido. A série parte de um cartão limpo — o
`limpo.mcr`, com radar em DOWN e as quatro opções em ON — e cada sonda é uma
sessão do jogo com **uma** opção mudada na tela e o option file salvo.

Sete corridas, e a sétima é o controle:

| cartão | opção mudada | byte | binário |
|---|---|---|---|
| `limpo` | — (radar DOWN, tudo ON) | `0x3E` | `0011 1110` |
| `radar-off` | Radar → OFF | `0x3C` | `0011 11`**`00`** |
| `radar-up` | Radar → UP | `0x3D` | `0011 11`**`01`** |
| `player-name-off` | Player Name → OFF | `0x3A` | `0011 1`**`0`**`10` |
| `timer-off` | Timer → OFF | `0x36` | `0011 `**`0`**`110` |
| `score-off` | Score → OFF | `0x2E` | `001`**`0`** `1110` |
| `strategy-off` | Strategy → OFF | `0x1E` | `00`**`0`**`1 1110` |
| `radar-dow` | Radar → DOWN de volta | `0x3E` | `0011 1110` |

**Uma opção por corrida, e não em grupo.** São cinco observáveis distintos e
todos visíveis na mesma tela, então o teste em grupo — que o
[`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md) usou para os bits de
desbloqueio — não economizaria boot nenhum: lá havia dez bits e um observável
por vez; aqui cada corrida já mostra as cinco.

**A última corrida é o controle, e é ela que fecha.** Devolver o radar a DOWN
devolve `0x3E`, e o cartão volta a ser idêntico ao limpo — os únicos 12 bytes
diferentes estão no padding do título, que não é dado
([`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md#o-padding-do-título-que-não-é-dado)).
Sem ela, uma leitura que acertasse os valores por acaso passaria igual.

### Reproduzir

A sonda, montada pelo módulo — que já refaz a soma deste registro:

```sh
python3 - <<'EOF'
import sys; sys.path.insert(0, "tools/mcr")
import options, layout
from card import Card

OPT = 115                                   # offset no payload do registro 0
c = Card.from_file("work/cards/limpo.mcr")
rec = options.record(c, 0)

v = c.data[rec.payload + OPT]
v = (v & ~0x03) | 1                         # radar -> UP
v &= ~0x08                                  # timer -> OFF
c.write(rec.payload + OPT, bytes([v]))

SPEED = 106                                 # o u16 da barra de velocidade
c.write(rec.payload + SPEED, (552 - 8 * 12).to_bytes(2, "little"))   # 12 barras

for off, barras in ((110, 5), (111, 16), (112, 0)):   # sound, BGM, narracao
    c.write(rec.payload + off, bytes([min(2 * barras, 31)]))
c.write(rec.payload + 113, bytes([0]))      # narracao OFF
c.write(rec.payload + 114, bytes([1]))      # audio MONO

c.write(rec.header + 2,
        bytes([options.checksum(bytes(c.data[rec.payload:rec.payload + rec.size]))]))
open("work/sonda.mcr", "wb").write(c.to_bytes())
EOF

cp work/sonda.mcr "<memcards>/World Soccer Winning Eleven 2002 (Japan)_1.mcd"
```

**Feche o emulador antes de trocar o arquivo** — ele reescreve o cartão ao sair,
e a sonda vai junto.

E a conferência, que não precisa do jogo:

```sh
python3 tools/mcr/options.py work/sonda.mcr     # o registro, e se a soma bate
```

## O que fica em aberto

- **Bits 6–7**: `00` nos dezenove cartões. Mesma situação dos bits 11..15 dos
  desbloqueios, e a mesma ressalva: o bit 9 daquele mapa ficou dois dias como
  "nada observável" e saiu de lá quando se olhou **outra tela**. Tratar estes
  dois como *não procurados o bastante*, não como vazios.
- **Radar `3`**: o quarto valor dos dois bits não existe na tela e não foi
  testado. Pode ser DOWN de novo, ou outra coisa.
- **A velocidade fora de `0..16`**: a fórmula é uma reta, e nada diz o que o
  jogo faz com um valor abaixo de 424 ou acima de 552. Nem se ele o corrige ao
  gravar de volta.
- **O que o número significa para o motor**: ler "552 menos oito por barra" não
  é saber o que o jogo faz com 488. A forma sugere intervalo; isso é conjectura.
- **Os offsets 109 e 126** do registro 0: variam entre os cartões e não foram
  identificados. O mapa do registro está em
  [`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md#o-mapa-do-registro-0).
- **Marcar e desmarcar pela ferramenta**: o `tools/mcr/options.py` lê e grava a
  câmera, e ainda não tem API para as cinco nem para a velocidade. A sonda acima
  usa as peças dele (`record`, `checksum`) diretamente.
