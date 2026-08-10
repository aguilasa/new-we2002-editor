---
id: CORR-WTE-043
title: "Correção: `players[i].cost := Ord(buf1[0])` perde o sinal que o C++ tem"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-WTE-043: o custo do jogador NC entra sem sinal na camada Pascal

## Problema identificado

`src/core/Database.cpp:770`, no `Load`:

```cpp
char buf[50], buf1[50], name_buf[11];   // linha 108 -- `char`, com sinal no x86
…
image_file.Read(buf1, 1);
players[i].cost = buf1[0];              // char COM SINAL -> int
```

A camada gerada (`wte/src/we2002_database.pas:962`):

```pascal
players[i].cost := Ord(buf1[0]);        { AnsiChar SEM sinal -> LongInt }
```

`buf1` está classificado como `AnsiChar` na tabela `CHAR_LOCAL`
(`wte/tools/port_database_pas.py:701-704`), o que é certo para os usos de
texto que ele tem — mas neste ponto ele alimenta um campo **`int`**. Para
byte ≥ 128 os dois lados divergem: o C++ estende o sinal (200 → **-56**), o
Pascal não (200 → **200**).

É exatamente o caso que a decisão 4 do [`tipos.md`](../../wte/re/tipos.md)
existe para impedir — "o `char` do x86 tem sinal e a UI alarga com
`static_cast<int>`: 200 tem de chegar como -56" — aplicada aos **campos**
`char` e aos locais, mas não a esta conversão, que é local→campo largo.

**A divergência é latente, e por isso perigosa.** Nas duas ROMs nenhum byte
desta região chega a 128, então nada quebra hoje; e o `Save` grava só o byte
baixo (`Write(players[i].cost, 1)`), então a imagem sai idêntica dos dois lados
mesmo se o valor divergir. O round-trip da
[WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) **não pega isto** — ele
compara bytes de imagem, e os bytes são os mesmos. Quem veria a diferença é a
tela: o custo do jogador é uma das quatro features da fase 5
([WTE-TASK-30](/docs/tasks/30-preco-do-jogador.md)).

Vizinhos que **não** têm o problema, e que ajudam a delimitar o alvo:

- `ml_teams[…].link[j] := Ord(buf[j])` — o destino é `unsigned char` no C++
  (`Team.hpp:78`) e `Byte` no Pascal: mesma conversão dos dois lados;
- o custo de ML (`Database.cpp:764`) é lido **direto** no campo
  (`Read(players[i].cost, 1)`), sem passar por `char`, e fica 0..255 nos dois;
- `TPlayer.Decode` usa `shr`/`and` sobre `ShortInt` negativo, e é
  bit-equivalente ao C++ porque toda máscara descarta os bits de extensão de
  sinal — conferido linha a linha nesta revisão.

## Evidência

Os 462 bytes de custo NC (`OFS_COST_NC` = 3.069.512, `PLAYERS_NC` = 462),
lidos das duas imagens **sem escrever nada**:

```
roms/golden-european-deluxe.bin: 462 bytes lidos, 0 >=128, max=36
roms/japanese-shift-jis.bin:     462 bytes lidos, 0 >=128, max=36
```

Tipos, dos dois lados:

| Símbolo | C++ | Pascal |
|---|---|---|
| `buf1` | `char` (com sinal no x86-64) | `array[0..49] of AnsiChar` (sem sinal) |
| `players[].cost` | `int` (`Player.hpp:89`) | `cost: LongInt` |
| resultado para `0xC8` | `-56` | `200` |

## Causa raiz

A classificação de `char` local é por **variável**, e `buf1` é texto na maior
parte dos usos e número neste; a conversão local→campo largo não passa por
nenhuma das duas tabelas de `char`.

## Correção

### Arquivo: `wte/tools/port_database_pas.py`

Fazer a atribuição de um `AnsiChar` para campo inteiro **largo** emitir a
conversão com sinal — `ShortInt(buf1[0])` em vez de `Ord(buf1[0])` — ou, se a
regra geral for cara, registrar o par (função, expressão) numa tabela como a
`CHAR_LOCAL` já faz, com a razão escrita.

O critério é o da decisão 4: onde o C++ estende sinal, o Pascal estende sinal.
Onde o destino é `Byte` (o caso do `link`), `Ord` continua certo — a correção
não pode virar `ShortInt` em toda parte.

**Terceira rota possível, e mais barata:** recusar. Um `AnsiChar` atribuído a
campo maior que um byte sem decisão escrita é o mesmo tipo de silêncio que o
`FORBIDDEN` já pega em outro lugar; hoje passa sem nota.

### Arquivo: `wte/tools/test_port_database_pas.py`

Teste da conversão nos dois sentidos: destino `LongInt` mantém o sinal, destino
`Byte` não ganha um `ShortInt` que o C++ não tem.

### Arquivo: `wte/tests/test_camada_dados.pas`

Um caso que planta `0xC8` no byte de custo e exige `-56`, ao lado do
`char_numerico/sinal` que já existe. É o mesmo teste, um nível acima: hoje ele
prova o campo, não a conversão.

### Arquivo: `wte/re/recusas.md`

Uma linha em "Achados que **não** eram recusa", que é onde os defeitos desta
classe já estão registrados.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/port_database_pas.py` | modificar |
| `wte/tools/test_port_database_pas.py` | modificar |
| `wte/tests/test_camada_dados.pas` | modificar |
| `wte/src/we2002_database.pas` | regerado (**não** editar à mão) |
| `wte/re/recusas.md` | modificar |

## Verificação

- [ ] `players[i].cost` recebe `-56` para o byte `0xC8`, igual ao `we2002_core`
- [ ] `ml_teams[…].link[j]` continua `Ord(...)` — destino `Byte`
- [ ] `python3 wte/tools/port_database_pas.py --check` verde depois de regerar
- [ ] `cd wte/tools && python3 -m unittest test_port_database_pas` verde,
      com os dois casos de `fpc` rodando (sem `skip`)
- [ ] `make -C wte check` verde
- [ ] `src/core/` intocado (rota 2 continua não usada)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
