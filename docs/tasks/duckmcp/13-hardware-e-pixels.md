---
id: DMCP-TASK-13
---

# DMCP-TASK-13 — `psx.py`, `gpu.py`, `png.py` e `vram.py`

## Goal

As constantes de hardware PS1 moram em `psx.py` (e a regra (c) passa a lê-las dali); `gpu.py` anda uma lista GP0 a partir de `read(address, size)`; `png.py` é o leitor PNG stdlib único; `vram.py` faz BGR555 ↔ RGB.

## Arquivos a criar ou modificar

- In:
  - os quatro módulos
- Out:
  - trocar `atlas.read_png` e `asset_write.read_png` pelos da lib (Fases 5 e 6)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] o selftest decodifica com `png.py` um PNG gerado pelo próprio teste e compara pixel a pixel; e `vram` faz ida e volta de todos os 32768 valores de 15 bits
- [ ] `gpu.py` anda uma lista sintética com um pacote de cada tamanho e termina no marcador de fim, e uma lista em laço é recusada
- [ ] a regra (c) importa as faixas de `psx.py`; plantar uma faixa a mais em `selftest.py` não muda o veredito, visto no Log

## Notes

## Log de Execução
