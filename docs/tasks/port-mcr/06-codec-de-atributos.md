---
id: MCR-TASK-06
title: "`attributes.py` — o codec de 12 bytes, contra `Player::Decode/Encode`"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-05"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.4"
status: concluído
---

# MCR-TASK-06: O codec de atributos

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.4 e §5.4.
- **Esta é a única parte do port que já nasce com oráculo dentro de casa.**
  [`src/core/Player.cpp`](../../../src/core/Player.cpp) decodifica o mesmo blob
  de 12 bytes — `skin_colour = raw[4]&0x03`, `strength = 12 + ((raw[5]>>6)&0x03)
  + ((raw[6]<<2)&0x04)`, `foot = (raw[11]>>6)&0x03`,
  `out_of_position = (raw[3]>>7)&0x01` — e ainda decodifica o dorsal que o
  upstream trata como tabela separada: `number = 1 + ((raw[3]>>2)&0x1f)`.
- O upstream expressa o mesmo em duas formas: nibbles diretos nos bytes `+0..+3`
  e um bitstream com carry (`algoritmo1`/`algoritmo2`) nos `+4..+11`, com as
  tabelas de peso explícitas na árvore `lite/`. A versão nova delega a uma DLL
  sem fonte; **é a `lite/` que documenta**.
- `Player::Encode()` é read-modify-write com pares sobrepostos numa ordem
  específica — reordenar duas linhas muda o resultado. O comentário no topo do
  arquivo avisa.

---

## Objetivo

`tools/mcr/attributes.py` com `decode(blob) -> dict` e `encode(dict, blob) -> blob`,
transcrito do upstream e **normativo pelo `Player.cpp`**.

---

## Critério de conclusão

- [x] Os **29** campos decodificados, com os domínios do upstream (altura
      148..211, idade 15..46, atributos exibidos 12..19 sobre índice 0..7).
      *(Dizia 30 até 2026-09-07. `Player::Decode()` atribui **29** — contado
      por ferramenta, não à mão:*
      `awk '/^void Player::Decode/,/^}/' src/core/Player.cpp | grep -oE '^\t[a-z_]+ =' | sed 's/[ \t=]//g' | sort -u | wc -l`.
      *A §5.4 do plano repete o 30, e a recontagem é da MCR-TASK-14.)*
- [x] **Cross-check, 0 divergências**, nas três medições da §5.4: os 23
      registros da fixture campo a campo; 100.000 blobs de 12 B com semente
      fixa; e `encode(decode(b)) == b` para os dois nos mesmos 100.000.
- [x] A tripwire: `1 + ((raw[3]>>2)&0x1f)` igual ao dorsal da tabela de
      `0x5404` nos 23 slots.
- [x] **Divergência deliberada registrada:** o Speed/Dribble trocado da
      gravação da v4.2 **não** é reproduzido, com a razão no comentário e na §6
      do plano.
- [x] O `encode` preserva bit que ninguém decodifica — read-modify-write, nunca
      montagem do zero.
- [x] Caso vermelho: trocar `speed` e `dribble` no encoder faz o round-trip com
      edição falhar.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

`tools/mcr/attributes.py` (650 linhas, en-US): o codec escrito **duas vezes de
propósito** — o fluxo de bits do upstream e as máscaras do `Player.cpp`, verbatim —
e conferido um contra o outro. **100.000 blobs com semente fixa, 0
divergências**, nos quatro sentidos; os 23 registros da fixture, 0
divergências; e a tripwire dos dorsais **23/23**.

Duas coisas que a execução mediu e que não estavam escritas: os pesos do
upstream **são** `índice << shift` e batem com o `Player.cpp` nos 21 campos do
fluxo — agora é medição e não afirmação —, e a tabela `[0,5,2,7,4,1]` **não é o
offset dentro do grupo**, o que a tripwire pegou em vermelho.

### As duas implementações, e por que são realmente duas

| | forma | fonte |
|---|---|---|
| `decode_stream`/`encode_stream` | os 12 bytes como **um fluxo de 96 bits little-endian**, cada campo num `(offset, largura)` declarado | a forma do upstream (§1.4) |
| `decode_masks`/`encode_masks` | máscara a máscara, deslocamento a deslocamento, **na ordem dos pares de read-modify-write** | `src/core/Player.cpp`, verbatim |

Nenhuma deriva da outra. Concordância entre uma tabela de offsets e um monte de
máscaras escritas à mão é evidência; entre duas grafias da mesma expressão não
seria.

```
$ WE2002_MCR_CARD=work/mcr-entrada.mcr python3 tools/mcr/attributes.py --self-check
  ok    100,000 blobs: stream and masks decode the same
  ok    100,000 blobs: encode_stream(decode_stream(b)) == b
  ok    100,000 blobs: encode_masks(decode_masks(b)) == b
  ok    100,000 blobs: the two encoders agree byte for byte
  ok    the 23 records decode the same both ways
  ok    and re-encode to the same bytes
  ok    tripwire: 23/23 shirt numbers agree between the record and the table
  ok    all 21 upstream weight tables are `index << shift` with our shifts
attributes.py: 0 failure(s)
```

As três medições da §5.4 fecham: os 23 registros campo a campo, os 100.000
blobs, e `encode(decode(b)) == b` nos dois. Mais uma quarta que a §5.4 não pede
e sai de graça: **os dois encoders produzem os mesmos bytes**, o que é mais
forte que cada um fechar o próprio round-trip.

### O que o upstream diz, agora medido

A §1.4 afirmava que o mapa de bits do zetaprog é o mesmo codec do
`Player.cpp`. Passou a ser **conferível por comando**:

```
$ python3 tools/mcr/attributes.py --upstream-weights work/easy-mcr
attributes.py --upstream-weights: 21/21 weight tables are `index << shift`
with our shifts
```

O upstream guarda o peso de cada campo numa combo escondida, e o `algoritmo1`/
`algoritmo2` soma esses pesos com carry — que é um fluxo de bits little-endian
escrito de outro jeito. Os valores são literais: `idbodybalance` vale
`0, 64, 128, …, 448` (= `i << 6`), `idage` vale `0, 32, …, 992` (= `i << 5`),
`idskincolor` vale `0, 1, 2, 3`. **Os 21 batem com o deslocamento que a nossa
tabela declara.**

**Os bytes `+0..+3` ficam de fora, e por um motivo**: ali o upstream monta o
byte **concatenando dígitos hexadecimais como string**, não somando pesos
(`cuartobite = idfeedoutside.Text & idheigth2.Text`), então não há
deslocamento a comparar. É onde moram o dorsal e o `out_of_position`, e a
observação foi encaminhada para a MCR-TASK-07.

### Os 4 bits que ninguém decodifica

`GAP_BITS` é **calculado** a partir da tabela, não escrito: são os bits `3, 12,
16, 45` — byte 0 bit 3, byte 1 bit 4, byte 2 bit 0 e byte 5 bit 5. Nenhuma das
duas implementações os lê, e o `encode` é read-modify-write, então eles
atravessam intactos. Há check para isso, e o controle 4 (gravar a partir de um
buffer zerado em vez do original) o deixa vermelho em 93.748 dos 100.000 blobs.

O bit 45 é o `gap(1)` que a §1.4 já listava no mapa do upstream; os outros três
são dos nibbles e o plano não os mencionava.

### Os controles negativos

Cinco defeitos plantados numa cópia em `/tmp`:

| defeito plantado | resultado |
|---|---|
| **o bug da v4.2**: `speed`/`dribbling` trocados no encoder | 🔴 4 falhas, 87.484/100.000 blobs divergindo |
| tirar o `-1` do dorsal no `encode_masks` | 🔴 2 falhas, **100.000/100.000** |
| mover `stamina` um bit | 🔴 6 falhas, e o `GAP_BITS` denuncia o bit órfão |
| gravar a partir de buffer zerado (mata os gaps) | 🔴 2 falhas, 93.748/100.000 |
| `bias=11` no `jump` | 🔴 2 falhas, e os 23 registros divergem |

**5/5 vermelhos, `rc=1` em todos.** O primeiro é o caso vermelho que o critério
pede, e o segundo é a divergência deliberada da §6 pelo outro lado.

### Divergências deliberadas, mantidas

- **O Speed/Dribble trocado da gravação da v4.2 não é reproduzido.** O
  `Player::Encode` é normativo, e a leitura da própria v4.2 é direta — é
  defeito de gravação, não formato. Está no comentário do módulo e é o
  controle 1.
- **O dorsal grava com `-1` e lê com `+1`.** O upstream diverge só na gravação;
  aqui os dois lados são simétricos, e a tripwire da §1.5 é quem cobra.

### Arquivos criados/modificados

- `tools/mcr/attributes.py` — **novo**, o módulo inteiro
- `docs/tasks/port-mcr/07-dorsais-e-nome.md` — a armadilha do `[0,5,2,7,4,1]` e
  a nota sobre os bytes `+0..+3` do upstream
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — `attempt()` e `refuses()`
  agora em três módulos
- `docs/tasks/port-mcr/14-verificacao-final.md` — a recontagem do "30 campos"
- `docs/tasks/port-mcr/progresso.md` — a linha desta task

### Problemas encontrados

**1. O critério dizia 30 campos e são 29.** Contado por ferramenta contra o
próprio `Player.cpp`, que é quem define o conjunto:

```
$ awk '/^void Player::Decode/,/^}/' src/core/Player.cpp \
    | grep -oE '^\t[a-z_]+ =' | sed 's/[ \t=]//g' | sort -u | wc -l
29
```

O texto do critério foi corrigido. **A §5.4 do plano repete o 30**, e a
recontagem é da MCR-TASK-14 — com a linha escrita **no arquivo dela**, não só
aqui.

**2. A tripwire ficou vermelha, e estava certa.** A primeira leitura da tabela
de dorsais usava `[0,5,2,7,4,1]` como offset dentro do grupo de 4 bytes e
devolvia `1 5 1 26 9 1 6 11 18 …` — números que **parecem** dorsais. O lado do
registro devolvia `1 5 4 3 2 7 6 11 10 9 8 …`, que é exatamente o que a §1.5
registra, então o erro era meu leitor.

A tabela documentada é o deslocamento **dentro do byte**; o offset dentro do
grupo é `5·(j mod 6)` = 0, 5, 10, 15, 20, 25, que cai nos bytes 0, 0, 1, 1, 2,
3 justamente nesses deslocamentos. Consertado, com o porquê no comentário, e
encaminhado para a MCR-TASK-07 — que é quem escreve o `numbers.py` de verdade.

**Vale o registro de método:** essa é a única checagem desta task que ficou
vermelha por si, e ela não mede o codec — mede um leitor de dez linhas escrito
de passagem. Foi a redundância do formato, não o cuidado de quem escreveu, que
pegou.

**3. O `try/except` de recusa escrito à mão matou a corrida.** Ao plantar o
controle 1, o bloco de refutação levantou `KeyError` em vez de
`AttributeError_`, e como o `except` nomeava só o tipo esperado a exceção
escapou: o self-check morreu no meio e **três checks não rodaram**. É a mesma
fragilidade que a MCR-TASK-04 já tinha medido, reencenada no único ponto que
este módulo escreveu à mão. Virou `refuses()`, que trata tipo errado como falha
nomeada. Depois do conserto o mesmo controle reporta 4 falhas em vez de morrer.

**4. A fixture não foi tocada.** Tudo rodou sobre `work/mcr-entrada.mcr`; o
digest da fixture continua `e53f4895…c47546`.

