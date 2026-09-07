---
id: MCR-TASK-07
title: "`numbers.py` e `text.py` — os 5 bits e o cp932"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-05"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.5"
status: pendente
---

# MCR-TASK-07: Dorsais e nome

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.5 e §1.6.
- **O dorsal está gravado duas vezes** e os dois concordam 23/23 na fixture. É
  a melhor tripwire do plano, e custa uma subtração.
- **O nome de 10 bytes é cp932**, medido: o slot 0 é `50 a5 83 57 ae b0 d9 83
  59 00` = `P･ジｮｰﾙズ`, mistura de ASCII, katakana meia-largura e Shift-JIS de 2
  bytes. O `KanjiToAscii` do `we2002_core` devolve **cinco espaços** para ele; o
  upstream assume ASCII e ainda filtra por `[^a-zA-Z.]`.
- O campo **não é cadeia terminada em NUL**: o slot 20 usa os 10 bytes.

---

## Objetivo

`numbers.py` (leitura e gravação dos 24 valores de 5 bits) e `text.py` (o nome
de 10 bytes ↔ `str`).

---

## Critério de conclusão

- [ ] `numbers.py` lê os 4 grupos de 4 B com `int.from_bytes(..., "little")` e
      os deslocamentos `[0,5,2,7,4,1]`, somando 1; grava subtraindo 1.
      **Simetria obrigatória** — o `+1` sem `−1` do upstream é divergência
      registrada.
- [ ] Os 23 dorsais da tabela batem com os 23 do bit-field do registro:
      **23/23**.
- [ ] `text.py` decodifica os 23 nomes da fixture em cp932 sem exceção, e
      `encode(decode(b)) == b` nos 23 — inclusive o slot 20, que enche os 10
      bytes.
- [ ] Nome maior que 10 bytes **recusa**, não trunca em silêncio.
- [ ] Um comentário no módulo dizendo por que o `TextCodec` do `we2002_core`
      **não** serve aqui, com o exemplo do slot 0.
- [ ] Caso vermelho: remover o `−1` da gravação rompe o par dos dois
      codificadores.

---

## Log de Execução

*(a preencher)*
