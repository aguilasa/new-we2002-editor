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

- **`[0,5,2,7,4,1]` é a posição DENTRO DO BYTE, não o offset dentro do grupo.**
  Medido na MCR-TASK-06, e custou um vermelho: o offset do valor `j` dentro do
  grupo de 4 bytes é `5·(j mod 6)` — 0, 5, 10, 15, 20, 25 —, que cai nos bytes
  0, 0, 1, 1, 2, 3 com os deslocamentos 0, 5, 2, 7, 4, 1. Usar a tabela
  documentada **como se fosse o offset do grupo** devolve
  `1 5 1 26 9 1 6 11 18 …` na fixture: números que parecem dorsais e não são.
  A leitura certa dá `1 5 4 3 2 7 6 11 10 9 8 16 17 13 19 22 12 18 20 14 15 21 23`,
  que é o que a §1.5 do plano registra. Há uma leitura mínima de referência em
  `attributes.shirt_numbers_from_table()`, escrita só para a tripwire; o
  `numbers.py` é quem a implementa de verdade, com domínio e gravação.
- **O upstream monta os bytes `+0..+3` concatenando dígitos hexadecimais como
  string**, não somando pesos — `cuartobite = idfeedoutside.Text &
  idheigth2.Text`. É onde moram o dorsal (5 bits) e o `out_of_position`, e é
  por isso que os pesos `id*` daqueles quatro bytes **não** são
  `índice << shift` como os dos oito seguintes (`idfeedoutside` vale `[0, 9]`).
  Se algo do dorsal do upstream não fechar, é aqui que ele difere do nosso.

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
