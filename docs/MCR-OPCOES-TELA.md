# As opções de tela no option file do WE2002

**Medido em 2026-09-12**, sobre a release japonesa `SLPM-87056`, num cartão do
usuário gravado pelo jogo rodando sob o fork do DuckStation.

O que este arquivo diz é onde o option file guarda as **cinco opções da tela de
jogo** — radar, nome do jogador, cronômetro, placar e estratégia — e como
reescrevê-las sem que o jogo recuse o cartão.

É o papel que [`../wte/re/mcr.md`](../wte/re/mcr.md) faz para os 17 destinos do
editor do Obocaman: **fonte de endereços**, para a ferramenta citar.

## O campo: **um byte**, no offset 115 do registro 0

As cinco opções cabem num byte só. **Não é um endereço absoluto**: o save
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
| 7–6 | `0xC0` | — | `00` nos dezesseis cartões medidos; não identificados |

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

## Como a medição foi feita

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

- **Bits 6–7**: `00` nos dezesseis cartões. Mesma situação dos bits 11..15 dos
  desbloqueios, e a mesma ressalva: o bit 9 daquele mapa ficou dois dias como
  "nada observável" e saiu de lá quando se olhou **outra tela**. Tratar estes
  dois como *não procurados o bastante*, não como vazios.
- **Radar `3`**: o quarto valor dos dois bits não existe na tela e não foi
  testado. Pode ser DOWN de novo, ou outra coisa.
- **Os offsets 106, 109 e 126** do registro 0: variam entre os cartões e não
  foram identificados. O mapa do registro está em
  [`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md#o-mapa-do-registro-0).
- **Marcar e desmarcar pela ferramenta**: o `tools/mcr/options.py` lê e grava a
  câmera, e ainda não tem API para estas cinco. A sonda acima usa as peças dele
  (`record`, `checksum`) diretamente.
