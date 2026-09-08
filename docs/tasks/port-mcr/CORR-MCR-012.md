---
id: CORR-MCR-012
title: "Correção: o check chamado \"e nada mais\" só afirma \"algo mudou\", e a exclusividade do dorsal fica sem guarda"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-MCR-012: o check que promete exclusividade e não a mede

## Problema identificado

`tools/mcr/model.py:285` tem o check

```python
ok("a number touches the record and the table, and nothing else",
   len([i for i, (a, b) in enumerate(zip(c.to_bytes(), before2))
        if a != b]) > 0)
```

O nome afirma **três** coisas — o registro, a tabela, e nada além disso — e a
condição afirma **uma**: que ao menos um byte mudou. Qualquer escrita perdida
em qualquer lugar do cartão satisfaz `> 0`.

O contraste está no próprio arquivo, doze linhas acima: o check do atributo
comum mede exclusividade de verdade, com `all(...)`:

```python
ok("editing one attribute stays inside that player's 12-byte record",
   moved and all(base <= i < base + attributes.BLOB_BYTES for i in moved), ...)
```

E o par do `mcrio.py:384` — `"a shirt number moves the record AND the table"`
— usa `any(...) and any(...)`, que também não fecha o conjunto, mas ao menos
**não promete** que fecha.

Resultado: o caminho do dorsal, que é o único que escreve em **dois** lugares,
é o único cujo "e nada mais" **nenhum check afirma**. É exatamente a
propriedade da Regra 2, e é o que a task afirmou ter medido no critério de
conclusão ("muda **exatamente** os bytes esperados, e nada mais").

## Evidência

Cópia da árvore em sandbox dentro do repositório, `PYTHONPATH=tools/mcr`,
`WE2002_MCR_CARD` apontando para a fixture — os dois `--self-check` verdes e
sem `skip` antes de plantar.

Plantio em `Save._write_number`, escolhido para sobreviver ao round-trip
(escreve só quando o dorsal **muda**, e o round-trip regrava os mesmos
valores), sobre os dez bytes intocados do registro do jogador 5 — a região que
a Regra 2 existe para proteger:

```python
        table = list(numbers_mod.read(self.card))
+       if table[index] != number:
+           self.card.write(layout.player_attribute_address(5) + 22, b"\x7f")
        table[index] = number
```

A substituição casou 1×. Resultado:

```
model rc=0 FAIL=0
mcrio rc=0 FAIL=0
  ok    a number touches the record and the table, and nothing else
```

Os dois gates saem **verdes**, e o check que nomeia o defeito diz `ok`. Quem
enxerga o estrago é só o CLI, e só porque um humano conta:

```
$ python3 tools/mcr/mcrio.py <cópia> --edit-probe 0 number 30
number=30 on slot 0: 3 byte(s) moved
  0x05404
  0x05907
  0x059ba      <- o byte plantado, dentro dos dez intocados do jogador 5
```

Contra os **2 bytes** que o Log da MCR-TASK-09 registra, e que a §1.5 prevê.

Os seis controles de substituição literal do Log **reproduzem** (2, 1, 2, 2, 3,
e 1 em cada módulo no sexto); nenhum deles alcança este caso, porque nenhum
mexe no conjunto de bytes que uma gravação de dorsal toca.

## Causa raiz

O check foi escrito com a condição de "o escritor rodou" e batizado com a
afirmação de "e nada mais"; as duas frases descrevem asserções diferentes, e a
que ficou no código é a fraca.

## Correção

### Arquivo: `tools/mcr/model.py`

Fechar o conjunto, como o check do atributo já faz. Os dois destinos legítimos
são o registro de 12 bytes do jogador e os 4 grupos da tabela de 5 bits:

```python
    moved_n = [i for i, (a, b) in enumerate(zip(c.to_bytes(), before2))
               if a != b]
    base1 = layout.player_attribute_address(1)
    n = layout.SHIRT_NUMBERS
    ok("a number touches the record and the table, and nothing else",
       moved_n
       and any(base1 <= i < base1 + attributes.BLOB_BYTES for i in moved_n)
       and any(n.address <= i < n.address + n.total_bytes for i in moved_n)
       and all(base1 <= i < base1 + attributes.BLOB_BYTES
               or n.address <= i < n.address + n.total_bytes
               for i in moved_n),
       f"moved={moved_n}")
```

### Arquivo: `tools/mcr/mcrio.py`

O par da linha 384 mede a mesma coisa por outro caminho e deve fechar o
conjunto junto — senão o defeito continua passando por um dos dois gates.

### Arquivo: `docs/tasks/port-mcr/09-modelo-e-round-trip.md`

Acrescentar o plantio acima à tabela de controles: **substituição literal**,
com a função (`Save._write_number`) e a contagem de falhas que ele passa a
produzir depois do conserto.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/model.py` | modificar |
| `tools/mcr/mcrio.py` | modificar |
| `docs/tasks/port-mcr/09-modelo-e-round-trip.md` | modificar |

## Verificação

- [x] `python3 tools/mcr/model.py --self-check` verde, e a contagem de checks
      registrada no Log da MCR-TASK-09 reconciliada se mudar
- [x] `python3 tools/mcr/mcrio.py --self-check` verde
- [x] **o caso vermelho:** com o plantio da Evidência aplicado numa cópia da
      árvore, `model.py --self-check` e `mcrio.py --self-check` saem `rc=1`,
      cada um acusando o check nomeado
- [x] os seis controles do Log continuam reproduzindo as mesmas contagens
- [x] `python3 tools/mcr/mcrio.py <cópia> --roundtrip` = 0 bytes nas duas formas
- [x] `layout.py --rule1` = 0, com o caso vermelho exercitado
- [x] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

O sintoma reproduziu exatamente. Com o plantio da Evidência aplicado numa cópia
da árvore em `work/sbx012/` (raiz do repositório, `PYTHONPATH` apontando para a
cópia, `WE2002_MCR_CARD=work/entrada.mcr`), a substituição casou **1×** e os
dois gates saíram `rc=0`, `0 failure(s)`, **sem nenhum `skip`** — e o check
nomeado dizendo `ok`. O `--edit-probe 0 number 30` reportou os **3** bytes da
CORR, `0x05404 0x05907 0x059ba`.

Os dois checks passaram a fechar o conjunto. O do `model.py` mede sobre o
registro do jogador **1** (é ele que o `set_number` do `self_check` edita) e
sobre os 16 bytes da tabela de dorsais; o do `mcrio.py`, sobre o registro do
jogador **0** e a mesma tabela. Os dois agora exigem as três coisas que o nome
promete: tocar o registro, tocar a tabela, e **nada fora dos dois**. O nome do
check do `mcrio.py` mudou junto — era `"moves the record AND the table"`, que
não prometia fechamento; agora diz `and nothing else`, como o do `model.py`. E
o `detalhe` dos dois passou a imprimir os offsets em hexadecimal, que é a forma
em que o `--edit-probe` e o Log da task já falam.

Depois do conserto, com o mesmo plantio: `rc=1` nos dois, 1 falha cada,
`moved=['0x5404', '0x5405', '0x5927', '0x59ba']` no `model.py` e
`moved=['0x5404', '0x5907', '0x59ba']` no `mcrio.py` — o byte plantado
aparecendo nomeado nos dois. A contagem de checks não mudou: 19 e 17.

**Problemas encontrados:**

**1. O controle 5 do Log da MCR-TASK-09 estava subcontado, e não por causa
desta correção.** A tabela registra "🔴 model, 3 falhas". Replantando-o contra
o `HEAD` — `git show HEAD:tools/mcr/model.py` numa cópia, para separar o que é
meu do que já estava lá — ele dá **3 falhas no `model.py` e 1 no `mcrio.py`**:
o par do `mcrio` já era vermelho e a linha não o dizia. Depois do conserto o
`model.py` vai a **4**, porque o conjunto fechado também acusa a metade que o
controle 5 desliga (o registro deixa de ser tocado). A linha da tabela passou a
trazer os dois módulos e as duas contagens, com a distinção de qual é nova.

**2. O plantio entrou na tabela como controle 7, e a razão de ele existir é o
que os outros seis não alcançam.** Nenhum dos seis mexe no conjunto de bytes
que uma gravação de dorsal toca — é por isso que 6/6 vermelhos convivia com o
defeito. A escolha do plantio importa: escrever **só quando o dorsal muda** é o
que o faz sobreviver ao round-trip, que regrava os mesmos valores e nunca entra
no ramo.

**Medições:**

| gate | número |
|---|---|
| `model.py --self-check` | 19 checks, `rc=0`, `0 failure(s)` |
| `mcrio.py --self-check` | 17 checks, `rc=0`, `0 failure(s)` |
| o caso vermelho, com o plantio | `rc=1` nos dois, **1 falha cada**, 0 `skip` |
| os sete controles literais | **7/7 vermelhos**: 2, 1, 2, 2, (4+1), (1+1), (1+1) |
| `mcrio.py <cópia> --roundtrip` | form 1 e form 2, **0 byte(s) differ** |
| `mcrio.py <cópia> --edit-probe 0 number 30` | **2** bytes, `0x05404` e `0x05907` |
| `layout.py --rule1` | **0** endereços fora de `layout.py` |
| `layout.py --check` | **17/17** destinos |
| os nove módulos | todos `0 failure(s)` |
| fixture | `sha256 e53f4895…c47546`, intocada |

**Arquivos criados/modificados:**

- `tools/mcr/model.py` — o check fecha o conjunto
- `tools/mcr/mcrio.py` — o par fecha o conjunto, e o nome passa a prometer o
  que mede
- `docs/tasks/port-mcr/09-modelo-e-round-trip.md` — o controle 7, a contagem
  reconciliada do controle 5, e "seis" → "sete" nos dois lugares
