---
id: MCR-TASK-05
title: "`layout.py` e o cross-check dos 17 destinos"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-04"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.2"
status: pendente
---

# MCR-TASK-05: Os endereços, e a única fonte deles

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.2 e §3.3
  (Regra 1).
- Os 17 destinos estão medidos em [`../wte/re/mcr.md`](../../../wte/re/mcr.md),
  do `we-team-editor.exe`. O upstream chega **independentemente** aos mesmos
  números onde as duas listas se tocam — 21508, 22788 passo 32, os cinco
  cobradores, 25256/25266/25557.
- **Esta task trava a 06, a 07 e a 08.** Decodificador escrito contra endereço
  não conferido produz campo plausível e errado, e o sintoma só aparece no jogo.
- **O contêiner já responde em que bloco cada endereço cai**, e a MCR-TASK-04
  mediu: o save declarado ocupa os blocos **1 e 2** (16.384 B), e o bloco 3 —
  onde caem 14 dos 17 destinos — está **fora da cadeia declarada**, com 41
  bytes não-zero num quadro que o diretório marca `0xA0`. Use
  `card.Card.find_save()` e `python3 tools/mcr/card.py <cartão> --blocks` em vez
  de dividir endereço por 8192 na mão; e note que a divisão simples continua
  certa para o **número** do bloco, mas não diz se ele é declarado.

---

## Objetivo

`tools/mcr/layout.py` como **fonte única de endereço**, com um `--check` que se
mede contra o nosso RE.

---

## Critério de conclusão

- [ ] Nenhum outro módulo de `tools/mcr/` tem constante de endereço — guarda
      mecânica no `selftest`.
- [ ] `layout.py --check` compara com a tabela de `wte/re/mcr.md`: **17/17**,
      `(endereço, bytes)` iguais, e **conjunto idêntico nos dois sentidos** —
      destino presente de um lado e ausente do outro é falha.
- [ ] Duas asserções que a `mcr.md` já cobra: a tabela de cobradores **não é
      crescente**, e os deslocamentos de bit do dorsal são `[0,5,2,7,4,1]` =
      `(5·(j mod 6)) mod 8`.
- [ ] Um caso vermelho: mudar um endereço na mão faz o `--check` falhar dizendo
      qual.

---

## Log de Execução

*(a preencher)*
