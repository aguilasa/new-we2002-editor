---
id: MCR-TASK-04
title: "`card.py` — diretório, blocos, quadros, checksum e as recusas"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-03"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.1"
status: pendente
---

# MCR-TASK-04: O contêiner do cartão

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.1 e §1.10.
- **Não é engenharia reversa:** o contêiner do memory card PSX é documentação
  pública (nocash), e `wte/tools/dump_mcr.py` já o implementa em Python — com o
  dicionário **completo** de estados (`0x51/0x52/0x53`, `0xA0..0xA3`, `0xFF`).
  `tools/pes2/memcard.py` conhece só o `0x51`, e é leitura pura.
- **O upstream não conhece nada disso**, e é por isso que ele grava nos bytes
  `0..137` — que são, medido, o quadro `MC` inteiro mais `state`+`size`+`link`
  da entrada 1.

---

## Objetivo

`tools/mcr/card.py`: abrir um `.mcr`, enxergar o diretório, achar o save do
WE2002 pelo nome, e **recusar** o que não deve ser escrito.

---

## Critério de conclusão

- [ ] Lê os 15 quadros de diretório, com os oito estados nomeados, o `link` e o
      tamanho declarado.
- [ ] Acha o save por nome (`B?SLPM-86600WEW-OPT`, `B?SLES-…`, `B?SLUS-…`) e
      **diz em que bloco ele está** — o upstream assume o bloco e quebra em
      silêncio se ele mudar.
- [ ] Calcula o checksum XOR de quadro e **relata** divergência sem consertar —
      preservar é o comportamento medido do original (§6 do plano).
- [ ] **Recusa toda escrita abaixo de `0x800`**, com mensagem que diz o que há
      lá. É caso de controle negativo, não comentário.
- [ ] Recusa arquivo cujo tamanho não seja 131.072 B, e arquivo sem `MC`.
- [ ] `self_check()` importável, com as recusas exercitadas contra um cartão
      sintético montado em memória — sem depender da fixture.

---

## Log de Execução

*(a preencher)*
