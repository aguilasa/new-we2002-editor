# As opções de partida no option file do WE2002

**Medido em 2026-09-13**, sobre a release japonesa `SLPM-87056`, em **27
cartões** gravados pelo jogo rodando sob o fork do DuckStation.

São as sete opções da tela que antecede cada partida — hora, clima, duração,
dificuldade, prorrogação, gol de ouro e pênaltis. O jogo as grava **ao fim de
uma partida**, não ao sair da tela.

Este arquivo é a **medição**; o mapa consolidado do save é o
[`/docs/MCR-OPTION-FILE.md`](/docs/MCR-OPTION-FILE.md).

## Os campos: **cinco bytes**, todos no registro 0

| offset | addr | campo | valores |
|---:|---|---|---|
| **109** | `0x02170` | **Time**, e os bits de Weather | tabela abaixo |
| **123** | `0x0217E` | **Match Length** | `0..5` → 5, 10, 15, 20, 25, 30 min |
| **124** | `0x0217F` | **Level** | `0` = Easy, `1` = **Normal**, `2` = Hard |
| **125** | `0x02180` | **Extra Time / Golden Goal / Penalty Kicks** | três bits, abaixo |
| **126** | `0x02181` | **Weather** | `0` = Short, `1` = Long, `2` = **Random** |

Os valores em negrito são o default do cartão limpo, que vale `10 · 01 · 01 ·
07 · 02`.

`123`, `124`, `125` e `126` são **consecutivos**; o `109` fica catorze bytes
antes, no mesmo bloco de opções que a velocidade e o som
([`/docs/MCR-OPCOES-JOGO.md`](/docs/MCR-OPCOES-JOGO.md)).

### O offset 109 — Time, e metade do Weather

| bit | máscara | o que é | valores |
|---:|---|---|---|
| 0 | `0x01` | Time | `0` = Day, `1` = Night |
| 1 | `0x02` | — | zero em todos os cartões |
| 2 | `0x04` | Weather, chuva | `0` = Sunny, `1` = Rainny |
| 3 | `0x08` | Weather, duração | `0` = Short, `1` = Long |
| **4** | `0x10` | **Time é Random** | `1` = Random, e os bits 0 a 3 param de valer para o Time |
| 7–5 | `0xE0` | — | zero em todos |

### O offset 125 — as três perguntas de Yes/No

| bit | máscara | campo |
|---:|---|---|
| 0 | `0x01` | **Golden Goal** |
| 1 | `0x02` | **Extra Time** |
| 2 | `0x04` | **Penalty Kicks** |

`1` é *Yes* nos três. Bits 3 a 7 são zero em todos os cartões.

**Desligar Extra Time arrasta o Golden Goal**, e isso é o jogo, não o formato:
`entrada-extra-time-no` e `entrada-golden-no` são o **mesmo** `0x04`. Faz
sentido — o gol de ouro só existe na prorrogação.

Foi por isso que os dois bits precisaram de uma sonda para serem separados: nos
cartões do jogo eles só aparecem como `11` ou `00`. Escrevendo `0x06` — bit 0
desligado, bit 1 ligado — o jogo mostrou **Extra Time Yes, Golden Goal No**, o
que fixa qual é qual.

---

## Time e Weather têm **cada um o seu Random**, em lugares diferentes

Esta é a parte que engana, e é a explicação do cartão `entrada-estranha`.

```
Time é Random     ←  bit 4 do offset 109
Weather é Random  ←  offset 126 == 2
```

**São campos independentes**, e o jogo consegue deixá-los em desacordo. O
`entrada-estranha` é exatamente esse estado:

| | valor | lê como |
|---|---|---|
| offset 109 | `0x10` | bit 4 ligado → **Time = Random**; bit 2 = 0 → Sunny |
| offset 126 | `0x00` | → **Weather = Short** |

Na tela: `Time: Random`, `Weather: Short/Sunny`. O Time continuou em Random e o
Weather foi **concretizado** em Short/Sunny.

Foi o que aconteceu ao trocar o Time de Random para Day e jogar: o jogo gravou
o Time de volta como Random e deixou o Weather concreto. Repor o Weather em
Random devolve `126 = 2` e os dois voltam a exibir Random — que é o
`entrada-normalizada`.

**O bit 3 do 109 não é cópia do 126.** Quando o Weather é Random, o `126` vale
`2` e o bit 3 fica `0`. O bit 3 guarda o Short/Long de dentro do `109`; o `126`
guarda o que a tela selecionou, incluindo o Random que o `109` não sabe
expressar para o clima.

### Como ler, então

```python
time    = "Random" if b109 & 0x10 else ("Night" if b109 & 0x01 else "Day")
weather = "Random" if b126 == 2 else f"{('Short','Long')[b126]}/" \
                                     f"{('Sunny','Rainny')[b109 >> 2 & 1]}"
```

Decodificados assim, os **27 cartões batem com o próprio nome**, o
`entrada-estranha` incluído.

---

## O que não vai para o cartão

`entrada-kits-type1` e `entrada-stadium-key-square` são **idênticos** ao
`entrada-normalizada` nos cinco offsets. Uniforme e estádio se escolhem na mesma
tela e **não** são gravados — o que a série mediu em vez de assumir.

---

## Como a medição foi feita

Uma opção por cartão, cada um uma partida jogada até o fim, e o diff contra o
`entrada-normalizada`. Vinte e sete cartões, e três deles são controle:

| cartão | papel |
|---|---|
| `entrada-normalizada` | a base: tudo no default, Time e Weather concordando em Random |
| `entrada-level-normal` | **controle** — volta o Level ao default e o cartão fica idêntico à base fora do padding do título |
| `entrada-kits-type1`, `entrada-stadium-key-square` | **controles negativos** — mudam coisas que não deviam ser gravadas, e nenhum byte se move |

Os bytes que se movem em toda gravação e **não são dado** são o padding do
título (`0x02034..0x02044`) e o checksum do registro
([`/docs/MCR-CAMERA.md`](/docs/MCR-CAMERA.md#o-padding-do-título-que-não-é-dado)).

**Duas perguntas não foram respondidas pelos cartões do jogo**, e as duas
saíram de sonda escrita por fora:

- **qual bit é Golden e qual é Extra** — a interface só produz `11` e `00`;
- (a mesma técnica que separou o arredondamento dos volumes em
  [`/docs/MCR-OPCOES-JOGO.md`](/docs/MCR-OPCOES-JOGO.md): escrever um valor que
  o jogo não sabe gerar e olhar a tela).

### Reproduzir

```sh
python3 - <<'EOF'
import sys; sys.path.insert(0, "tools/mcr")
import options
from card import Card

c = Card.from_file("work/cards/entrada-normalizada.mcr")
rec = options.record(c, 0)

c.write(rec.payload + 109, bytes([0x0D]))   # Night, Long/Rainny (sem Random)
c.write(rec.payload + 123, bytes([5]))      # 30 min
c.write(rec.payload + 124, bytes([2]))      # Hard
c.write(rec.payload + 125, bytes([0x06]))   # Extra Yes, Golden No, Penalty Yes
c.write(rec.payload + 126, bytes([1]))      # Long

c.write(rec.header + 2,                     # SEM ISTO, o jogo da ERROR
        bytes([options.checksum(bytes(c.data[rec.payload:rec.payload + rec.size]))]))
open("work/sonda.mcr", "wb").write(c.to_bytes())
EOF

python3 tools/mcr/options.py work/sonda.mcr     # confere a soma antes de trocar
cp work/sonda.mcr "<memcards>/World Soccer Winning Eleven 2002 (Japan)_1.mcd"
```

**Feche o emulador antes de trocar o arquivo** — ele reescreve o cartão ao sair.

Os cinco bytes caem dentro do payload do registro 0, então **a soma tem de ser
refeita**; sem isso o jogo põe `ERROR` na carga do option file e para ali.

## O que fica em aberto

- **O bit 1 do offset 109** (`0x02`): zero nos 27 cartões. A tela tem três
  opções de Time e duas cabem no bit 0 — este bit não tem função conhecida.
- **Os bits 3–7 dos offsets 123, 125 e 126**: zero em todos. O `123` guarda
  `0..5` em três bits e sobram cinco.
- **O que o jogo faz com valor fora da faixa**: `123 = 6`, `124 = 3`, `126 = 3`
  não foram testados.
- **Por que o Time volta a Random** depois de ser posto em Day: o mecanismo não
  foi investigado, só o estado que ele deixa no cartão.
