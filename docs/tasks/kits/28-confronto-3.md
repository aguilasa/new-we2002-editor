---
id: KITS-TASK-28
---

# KITS-TASK-28 — Confronto 3: `confront.py --score` com um uniforme que não é o `A4`

## Goal

O confronto por histograma de cor do `looks` refeito com o time da §4.1, titular e suplente, contra o quadro do emulador.

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Os escores de titular e suplente colados, com o limiar que o `looks` usa
- [ ] Controle: nosso titular contra o quadro do suplente do jogo reprova

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

Da KITS-TASK-10: o `tools/kits/confront.py` já existe e é o confronto 2 (os pares de bandeira, `WE2002_KITS_CORPUS`), sem subcomando — rodar sem opção confronta os pares. O `--score` desta task entra como modo novo dele, sem mudar o que a corrida sem opção faz; o arquivo está na regra da fachada (`FACADE_CLIENTS` do `selftest.py`), então só importa `core.api`.

## Log de Execução
