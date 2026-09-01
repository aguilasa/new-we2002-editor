---
id: CORR-PES2-011
title: "Correção: o prefixo de registro citado na §1.14(e) é o do quarto registro, não a forma deles"
type: correção
category: formato
status: concluído
depends_on: []
---

# CORR-PES2-011: `0f 80 0a 00 20 02 80 01` é uma instância, não o formato

## Problema identificado

A §1.14(e) do plano descreve a cauda que sobra depois do último fluxo, e é ela
que a PES2-TASK-27 vai abrir:

> **O que fica fora de qualquer fluxo é a tabela de entradas**, não defeito:
> registros de 16 bytes que começam `0f 80 0a 00 20 02 80 01`, 15.538 bytes
> deles depois do último bloco de `DAT2D.BIN` no PES2 `(EsIt)`.

Os 15.538 bytes **conferem exatamente**. O prefixo, não: ele é o do **quarto**
registro. O primeiro começa `00 00 0a 00 00 02 00 01`, e os quatro primeiros
diferem entre si justamente nos oito bytes citados.

Quem abrir a task 27 procurando o literal acha a tabela tarde, ou conclui que
ela começa 48 bytes adiante de onde começa.

## Evidência

```
$ # DAT2D.BIN de (EsIt): 68.556 B, 21 blocos, último termina em 53018
file 68556 blocks 21 last ends at 53018 tail 15538          ← o número confere
pattern 0f800a0020028001 anywhere in file: 53066            ← 3 registros depois

tail, os quatro primeiros registros de 16 B:
   00 00 0a 00 00 02 00 01 20 00 80 00 00 00 08 00
   0f 80 0a 00 20 02 00 01 20 00 80 00 00 00 1c 0e
   0f 80 0a 00 00 02 80 01 20 00 80 00 00 00 4c 1d
   0f 80 0a 00 20 02 80 01 20 00 80 00 00 00 7c 24   ← o citado
```

O que **é** comum aos quatro: bytes 2-3 = `0a 00`, bytes 8-11 =
`20 00 80 00`, e os últimos quatro crescem monotonicamente
(`0800`, `0e1c`, `1d4c`, `247c` lidos como little-endian de 16 bits em pares)
— o que casa com deslocamento acumulado, e é exatamente a pista que a task 27
quer.

## Causa raiz

O registro foi copiado de um dump que começava no meio da tabela, e a frase o
apresentou como a forma de todos.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`

A frase da §1.14(e) passa a citar o **primeiro** registro da cauda e a dizer o
que é comum entre eles, em vez de um literal que só um tem:

> registros de 16 bytes — o primeiro deles `00 00 0a 00 00 02 00 01 20 00 80
> 00 00 00 08 00` —, com `0a 00` nos bytes 2-3 e `20 00 80 00` nos bytes 8-11
> em todos, e os quatro últimos crescendo de registro a registro; 15.538 bytes
> deles depois do último bloco de `DAT2D.BIN` no PES2 `(EsIt)`.

### Arquivo: `docs/tasks/27-conteiner-e-tim.md`

Se o repasse da task 27 repetir o literal, ele acompanha a correção.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `docs/tasks/27-conteiner-e-tim.md` | modificar, se repetir o literal |

## Verificação

- [x] o primeiro registro citado bate com o disco:
      `python3 tools/pes2/lzss.py "<track1.bin>" --file /BIN/DAT2D.BIN` mais o
      dump da cauda
- [x] os 15.538 continuam conferindo
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** A frase da §1.14(e) passou a citar o **primeiro**
registro da cauda e a dizer o que é comum aos quatro, em vez de um literal que
só um tem. Medido: o registro citado,
`00 00 0a 00 00 02 00 01 20 00 80 00 00 00 08 00`, está em **53018** — que é
exatamente onde a cauda começa —, e a cauda tem os **15.538** bytes que a
frase sempre afirmou. O literal antigo está em 53066, três registros adiante.

**Problemas encontrados.** Três, e o primeiro é maior do que a CORR viu:

1. **A `docs/tasks/27-conteiner-e-tim.md` não repetia o literal do plano — ela
   repetia um híbrido que não existe no disco.** Ela cita
   `0f 80 0a 00 20 02 80 01 20 00 80 00 00 00 4c 1d`: os oito primeiros bytes
   do quarto registro com os oito últimos do terceiro. Medido,
   `count=0` no arquivo, contra `count=1` para cada um dos dois reais (53050 e
   53066). O do plano ao menos era um registro de verdade; este não.
2. **O mesmo literal estava em código**, no docstring de `classify()` de
   `tools/pes2/lzss.py`, fora da lista da CORR. Corrigido junto — é a mesma
   afirmação, e é a que alguém lê ao mexer na ferramenta.
3. **15.538 e 15.574 são duas medidas diferentes, as duas certas.** A coluna
   `outside` do `lzss.py` diz 15.574 para `DAT2D.BIN`, porque conta tudo o que
   fica fora de fluxo — inclusive os 36 bytes de cabeçalho de contêiner. Os
   15.538 são o que vem depois do **último bloco**. A distinção entrou no
   plano, porque quem conferir o número na ferramenta encontra o outro.

**Gates.** `lzss.py --file /BIN/DAT2D.BIN`: 21 blocos, último termina em
53018; primeiro registro citado encontrado em 53018. `--check` verde.
`check_tasks.py` 82 tasks ok; conferência de link sem quebrado novo. `roms/`
intocada — leitura pura.

**Arquivos criados/modificados:**

- `docs/PLAN-PES2-PSX.md`
- `docs/tasks/27-conteiner-e-tim.md`
- `tools/pes2/lzss.py` (o docstring de `classify`, não previsto pela CORR)
