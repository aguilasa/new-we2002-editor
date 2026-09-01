---
id: CORR-PES2-008
title: "Correção: a varredura do `poke.py` só enxerga registro delimitado por NUL, e o disco tem tabela de largura fixa"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-PES2-008: a varredura que mede o conjunto de cópias assume um esquema de registro

## Problema identificado

`leftovers()` é a guarda que transforma "todas as cópias" de afirmação em
medição — foi ela que achou as três listas que ninguém conhecia. Ela conta uma
ocorrência como cópia viva só quando o casamento é um **registro inteiro**, e o
teste de "inteiro" é NUL de um lado e NUL do outro:

```python
whole = (i == 0 or data[i - 1] == 0) \
    and i + len(raw) < len(data) and data[i + len(raw)] == 0
```

O mesmo arquivo, dez linhas acima, diz que **o esquema de registro é
propriedade da tabela** — e o disco tem tabelas de largura fixa em que o nome
que enche a largura **não tem terminador**: `SELECT.BIN` @5320 são 463
registros de 10 B, onde `NachtegallHeggem` se lê corrido. Num registro assim, o
byte anterior é a última letra do vizinho e o seguinte é a primeira letra do
próximo: a varredura não vê a ocorrência, e **cala**.

Hoje isso não morde — as oito listas de nome de time são todas
`string + terminador`. Morde na primeira entidade guardada em tabela fixa, e a
Fase 3 vai direto para uma delas (`player-names-boot`, 1.449 registros de 10 B).
Uma guarda que fica em silêncio no caso que ela existe para pegar é pior que
guarda nenhuma, porque o silêncio se lê como "varri e não sobrou".

## Evidência

As tabelas de largura fixa que `tables.py` já descreve:

```
$ python3 tools/pes2/tables.py "<track1.bin>" --check
  abbreviations          /SELECT.BIN    @   4292 n=   95 span=   379 7cdfb5d4be0c40f1
  club-players           /SELECT.BIN    @   5320 n=  463 span=  4625 3e406786e53525ed
  player-names-boot      /SLES_039.57   @ 284720 n= 1449 span= 14490 2861ded7b6949ab7

$ grep -n '("fixed"' tools/pes2/tables.py
74:          "/SELECT.BIN", b"PTA\x00MRA\x00BZA\x00", 0, ("fixed", 4),
79:          "/SELECT.BIN", b"Oranges001", -1740, ("fixed", 10),
88:          "/SELECT8.BIN", b"PTA\x00MRA\x00BZA\x00", 0, ("fixed", 4),
91:          "/REPLAYS.BIN", b"PTA\x00MRA\x00BZA\x00", 0, ("fixed", 4),
133:          BOOT, b"Given\x00\x00\x00\x00\x00Staunton\x00\x00", 0, ("fixed", 10),
```

E o que o próprio `tables.py` escreve sobre elas:

```python
"""`McAllister`, `S.Caldwell` and `Eddington` are exactly 10 characters
and carry no terminator at all, so "ends with NUL" is not the test."""
```

`leftovers()` faz exatamente o teste que essa linha diz não servir.

## Causa raiz

A varredura foi escrita para o caso em mãos — as oito listas de nome de time,
todas `cstr` — e generalizou o delimitador em vez de generalizar o esquema.

## Correção

### Arquivo: `tools/pes2/poke.py`

`leftovers()` passa a aceitar duas formas de "registro inteiro", e a segunda é
a de largura fixa:

- **`cstr`**: o teste de hoje — NUL antes (ou início do arquivo) e NUL depois.
- **largura fixa**: a ocorrência começa num múltiplo da largura a partir do
  início de alguma tabela fixa **daquele arquivo**, e o resto do registro é
  NUL ou nada.

A informação necessária já existe: `T.TABLES` diz quais tabelas do arquivo são
fixas, e `T.resolve_full()` dá o início de cada uma. Onde nenhuma tabela fixa
do arquivo cobre o offset, vale o teste `cstr` de hoje.

O comentário da função passa a dizer qual é o alcance da varredura, para que a
próxima entidade não herde a suposição em silêncio.

### Alternativa aceitável

Se a forma acima ficar cara, a correção mínima é **declarar o limite alto**: a
varredura recusa (não apenas avisa) quando o nome procurado tem exatamente a
largura de alguma tabela fixa do arquivo, dizendo que não sabe medir esse caso.
Silêncio é o que esta correção existe para eliminar; recusa explícita serve.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/poke.py` | modificar |

## Verificação

- [ ] um caso sintético — um nome de exatamente 10 caracteres plantado num
      registro de `club-players` numa **cópia** — é achado pela varredura
- [ ] `python3 tools/pes2/poke.py "<track1.bin>" --self-check --tmpdir <dir>`
      continua verde nas duas releases, com a varredura sem sobra
- [ ] `ctest --test-dir build -R pes2` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
