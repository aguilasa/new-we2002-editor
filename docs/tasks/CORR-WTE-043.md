---
id: CORR-WTE-043
title: "Correção: `players[i].cost := Ord(buf1[0])` perde o sinal que o C++ tem"
type: correção
category: dados
status: concluído
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

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

Rota 1 — a regra geral, não a tabela por par. `ajustar_atribuicao()` passou a
separar destino **largo** de destino de um byte:

```python
if ta.base in UM_BYTE:          # {"Byte", "ShortInt"}
    return f"Ord({valor})"
return f"ShortInt({valor})"
```

`UM_BYTE` é novo, ao lado de `INTEIROS`, com a razão escrita: recebendo de
`AnsiChar`, num destino de um byte os bits são os mesmos com ou sem sinal.

Saída: **um** site mudou nas seis unidades, exatamente o que a correção nomeia.

```diff
-    players[i].cost := Ord(buf1[0]);
+    players[i].cost := ShortInt(buf1[0]);
```

Os outros 34 `:= Ord(` continuam como estavam — todos com destino `Byte`, entre
eles `ml_teams[i].link[j]`.

Testes, nos dois sentidos:

- `TestCharParaInteiro.test_destino_largo_estende_o_sinal` (`LongInt`,
  `SmallInt`, `Int64`) e `test_destino_de_um_byte_continua_com_ord` (`Byte`,
  `ShortInt`), sobre `ajustar_atribuicao` direto;
- `test_a_saida_real_estende_o_sinal_so_no_custo`, que fixa na saída commitada
  que o `ShortInt(buf` é **um** e que o `link[j]` continua `Ord`;
- `wte/tests/test_camada_dados.pas`, procedimento `CustoNcEntraComSinal`: monta
  uma imagem esparsa de 3.069.514 bytes com `0xC8` no custo do jogador 0 e
  `0x24` no do 1, roda o `TDatabase.Load` **gerado** e exige `-56` e `36`.

Controle negativo rodado: com o `Ord(buf1[0])` de volta no `.pas`, o caso sai
`FALHA	custo_nc/sinal	200`. O teste morde.

O programa Pascal foi de 23 para 26 casos, e a asserção de contagem de
`test_as_decisoes_de_tipo_valem_em_execucao` acompanhou — ela existe justamente
para que caso sumido não passe em silêncio.

Gates: `port_database_pas.py --check` verde, duas execuções com bytes iguais;
bateria do `wte/tools/` 305 → 308, verde, com `test_as_seis_unidades_compilam`
e `test_as_decisoes_de_tipo_valem_em_execucao` **rodando** (sem `skip`);
`make -C wte check` rc=0; `src/core/` e `roms/` intocados.

**Problemas encontrados:**

O `we2002_offsets` faltava no `uses` do `test_camada_dados.pas` — o programa não
precisava de `OFS_*` até agora. Acrescentado.

A varredura pegou dois sítios do "23 casos": o de `wte/re/recusas.md` §"O que
ficou medido", que é afirmação viva e virou 26 com a origem dos 3 novos; e o de
`docs/tasks/18-camada-de-dados-gerada.md:164`, que está **dentro do Log de
Execução** (linha 113) — história de tarefa executada, deixada como está, pelo
mesmo critério da [CORR-WTE-040](/docs/tasks/CORR-WTE-040.md).

A linha nova de `recusas.md` levava link `/docs/...`; corrigida para
`../../docs/...`, que é o que a [CORR-WTE-027](/docs/tasks/CORR-WTE-027.md)
fixou para markdown de dentro de `wte/re/`. A prosa da seção diz "sete
defeitos" e continua verdadeira: ganhou a linha que explica que a última da
tabela não é da WTE-TASK-18, e sim da revisão dela.

**Arquivos criados/modificados:**

- `wte/tools/port_database_pas.py`
- `wte/tools/test_port_database_pas.py`
- `wte/tests/test_camada_dados.pas`
- `wte/src/we2002_database.pas` (regerado)
- `wte/re/recusas.md`
