---
id: CORR-PES2-006
title: "Correção: o `poke.py` mede oito listas e continua dizendo cinco — inclusive no que imprime"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-PES2-006: o `poke.py` afirma cinco listas e trabalha com oito

## Problema identificado

O achado que dominou a [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md)
foi que o conjunto de cópias de nome de time era **cinco no papel e é oito no
disco**. `tables.py`, `team_map.py`, `iso.py`, `check_image.py` e os documentos
principais foram atualizados; o **próprio `poke.py`** ficou para trás em nove
lugares, dois deles em texto que o usuário lê na tela.

O pior é o `--self-check`, que imprime uma contagem contradita pela linha
seguinte da mesma saída:

```
canonical team 3 = 'MARMARA', in all five lists
…
-- the poke: 7 characters, the tightest of the 8 slots --
canonical team 'MARMARA' -- 8 copy/copies
```

E o docstring do módulo repete a lista antiga como se fosse a medida:

```python
And the word "copy" is the trap. The five team-name lists hold 106, 99,
95, 94 and 123 entries and differ in *content*: …
```

São 106, 99, 95, 94, 123, **32, 99 e 99** — os números que a §6.1 do plano já
traz corrigidos e que o `team_map.py --check` imprime a cada corrida.

## Evidência

```
$ grep -n "five" tools/pes2/poke.py
10:  And the word "copy" is the trap. The five team-name lists hold 106, 99,
22:  **the record scheme is a property of the table** (1.10). These five are
53:  # The five lists, and the case each one stores.        ← o dict CASE tem 8
89:      """key -> (path, offset, entries, end) for the five team-name lists."""
159:     the disc, makes two of the five tables unfindable.
374:     """The lowest canonical index in all five lists that the guards allow.
376:     Not merely "in all five": canonical team 2 is `PATAGONIA`, …
389:     raise Refused("no canonical team can be written in all five lists")
415:     print(f"canonical team {team} = {original!r}, in all five lists")
```

As duas últimas são **saída para o usuário**. Contra elas, o mesmo arquivo:

```
$ python3 tools/pes2/team_map.py "<track1.bin>" --check | head -1
canonical  /SELECT.BIN    106 entries        (+ 7 cópias = 8 listas)
$ grep -n "eight" tools/pes2/check_image.py
66:    print("\n== the eight team-name lists, aligned (plan 6.1) ==")
```

`team_map.py` já registra a correção em prosa (*"**Eight, not five.** The plan
measured five until 2026-09-01…"*), o que mostra que a atualização foi feita
arquivo a arquivo e parou antes do `poke.py`.

## Causa raiz

A contagem está escrita à mão em nove comentários e duas strings, quando o
número existe em tempo de execução: `len(KEYS)` — que o próprio arquivo já usa
corretamente na linha do `-- the poke: … the tightest of the {len(KEYS)} slots`.

## Correção

### Arquivo: `tools/pes2/poke.py`

- As duas strings de saída passam a derivar a contagem em vez de afirmá-la:

```python
print(f"canonical team {team} = {original!r}, in all {len(KEYS)} lists")
…
raise Refused(f"no canonical team can be written in all {len(KEYS)} lists")
```

- O docstring do módulo passa a listar as oito e as suas contagens
  (106, 99, 95, 94, 123, 32, 99, 99), com a data da medição, como faz a §6.1.
- Os comentários de `CASE`, `resolve_all`, `anchor_ranges` e `_first_pokeable`
  passam a dizer oito. O de `leftovers` **já está certo** e não se toca — é
  ele que conta a história de como as três apareceram.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/poke.py` | modificar |

## Verificação

- [ ] `grep -n "five" tools/pes2/poke.py` devolve só a linha do `leftovers`
      que narra o achado ("the five lists the plan listed were not all of them")
- [ ] `python3 tools/pes2/poke.py "<track1.bin>" --self-check --tmpdir <dir>`
      verde nas duas releases, e a primeira linha diz oito
- [ ] `ctest --test-dir build -R pes2` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
