---
id: DMCP-TASK-03
---

# DMCP-TASK-03 — Regras de desenho (a), (c), (d) no selftest, e o `controls.py` da lib

## Goal

O selftest afirma as regras (a) sem dependência fora da stdlib no import, (c) nada de jogo dentro de `tools/duckmcp/` — serial no padrão `S[LC][EPU][SM]-\d{5}`, nome de projeto, endereço fora das faixas de hardware — e (d) só `env.py` lê ambiente. `tools/duckmcp/controls.py` planta cada uma numa cópia da árvore e exige o vermelho.

## Arquivos a criar ou modificar

- In:
  - as três regras e os controles delas
- Out:
  - a regra (b), que só fecha na Fase 4

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/duckmcp/controls.py` sai 0 e a última linha diz quantos controles e de que regra
- [ ] cada controle aparece vermelho no Log: `import PIL` em `errors.py`; `SLES-03957` num comentário que não é de linhagem; `os.environ` fora do `env.py`
- [ ] `grep -rnE 'S[LC][EPU][SM]-[0-9]{5}|pes2|looks|kits' tools/duckmcp --include='*.py'` lista só linhas marcadas como linhagem ou dentro do próprio `selftest.py`/`controls.py`

## Notes

A faixa de endereço permitida mora no `psx.py`, que nasce na Fase 3; até lá a regra usa as faixas de RAM, scratchpad e I/O escritas no próprio selftest, e a DMCP-TASK-13 as move.

## Log de Execução
