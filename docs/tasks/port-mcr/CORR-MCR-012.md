---
id: CORR-MCR-012
title: "Correção: o check chamado \"e nada mais\" só afirma \"algo mudou\", e a exclusividade do dorsal fica sem guarda"
type: correção
category: verificação
status: pendente
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

- [ ] `python3 tools/mcr/model.py --self-check` verde, e a contagem de checks
      registrada no Log da MCR-TASK-09 reconciliada se mudar
- [ ] `python3 tools/mcr/mcrio.py --self-check` verde
- [ ] **o caso vermelho:** com o plantio da Evidência aplicado numa cópia da
      árvore, `model.py --self-check` e `mcrio.py --self-check` saem `rc=1`,
      cada um acusando o check nomeado
- [ ] os seis controles do Log continuam reproduzindo as mesmas contagens
- [ ] `python3 tools/mcr/mcrio.py <cópia> --roundtrip` = 0 bytes nas duas formas
- [ ] `layout.py --rule1` = 0, com o caso vermelho exercitado
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
