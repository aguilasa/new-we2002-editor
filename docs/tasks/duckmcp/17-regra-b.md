---
id: DMCP-TASK-17
---

# DMCP-TASK-17 — Regra (b) como gate, e os controles da lib completos

## Goal

A regra (b) existe como check com lista de pendências: os sítios que o `audit.py` acha fora da lib só passam se estiverem na lista `PENDING` do selftest, com o ID da task que os remove; sítio novo fora da lista é vermelho. A lista encolhe a cada migração e é vazia na DMCP-TASK-30.

## Arquivos a criar ou modificar

- In:
  - o check e a lista
- Out:
  - remover os sítios (Fases 5 a 7)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/duckmcp/controls.py` sai 0, e a última linha diz quantos controles cobrem as regras (a) a (d)
- [ ] um `import fork` novo em `tools/kit2d/` (fora da lista) deixa o selftest vermelho, visto no Log
- [ ] o tamanho da lista `PENDING` bate com o total do `audit.py`, os dois colados no Log

## Notes

## Log de Execução
