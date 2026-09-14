---
id: LOOKS-TASK-13
title: "`looks.py` — os doze campos, seus domínios e os rótulos"
type: implementação
category: núcleo
phase: 4
depends_on: ["LOOKS-TASK-09"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.9"
status: pendente
---

# LOOKS-TASK-13: Os campos e seus domínios

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.9.
- **Esta é a task barata do ciclo**, e é de propósito: o lado dos bits já tem
  **quatro implementações concordando** — `src/core/Player.cpp`,
  `src/app/Commands.cpp` (`kHair[32]`, `kSkin[4]`, `kLetters[8]`),
  `tools/mcr/domains.py` e o fonte `en_we2000edit` do Superpack.
- Não é engenharia reversa. É transcrição conferida.

---

## Objetivo

`tools/looks/looks.py`: a tupla de aparência, com domínio e rótulo de cada
campo, e a conversão de e para os 12 bytes.

---

## Critério de conclusão

- [ ] Os doze campos da tela representados, com os domínios medidos: 4 peles,
      **32 cabelos** (`A1`…`P1`), 8 cores de cabelo, 7 barbas, 7 cores de
      barba, 8 corpos, 8 chuteiras, altura a partir de 148, idade a partir de
      15, e o pé.
- [ ] Decodificação dos 12 bytes **conferida campo a campo** contra
      `src/core/Player.cpp`, com o cross-check no `self_check()`.
- [ ] A tupla de texto do corpus (`A-I3-A-F-A`) é lida e escrita — é o formato
      dos 50 JPGs da LOOKS-TASK-18 e do `--looks` da UI.
- [ ] Os registros no disco (`/SELECT.BIN` offset **157.164**, 1.242 × 12 B)
      são conferidos: a contagem tem de fechar com o tamanho do arquivo. **É
      opinião de terceiro até esta task medir.**
- [ ] `self_check()` com caso vermelho.

---

## Log de Execução

*(preencher ao executar)*
