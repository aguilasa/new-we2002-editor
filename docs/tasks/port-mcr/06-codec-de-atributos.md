---
id: MCR-TASK-06
title: "`attributes.py` — o codec de 12 bytes, contra `Player::Decode/Encode`"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-05"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.4"
status: pendente
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

- [ ] Os 30 campos decodificados, com os domínios do upstream (altura 148..211,
      idade 15..46, atributos exibidos 12..19 sobre índice 0..7).
- [ ] **Cross-check, 0 divergências**, nas três medições da §5.4: os 23
      registros da fixture campo a campo; 100.000 blobs de 12 B com semente
      fixa; e `encode(decode(b)) == b` para os dois nos mesmos 100.000.
- [ ] A tripwire: `1 + ((raw[3]>>2)&0x1f)` igual ao dorsal da tabela de
      `0x5404` nos 23 slots.
- [ ] **Divergência deliberada registrada:** o Speed/Dribble trocado da
      gravação da v4.2 **não** é reproduzido, com a razão no comentário e na §6
      do plano.
- [ ] O `encode` preserva bit que ninguém decodifica — read-modify-write, nunca
      montagem do zero.
- [ ] Caso vermelho: trocar `speed` e `dribble` no encoder faz o round-trip com
      edição falhar.

---

## Log de Execução

*(a preencher)*
