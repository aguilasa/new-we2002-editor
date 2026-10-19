---
id: K2D-TASK-08
---

# K2D-TASK-08 — graphics.py e palette.py: os três streams do DATSEL.BIN e BGR555

## Goal

Os streams 21/22/23 do `DATSEL.BIN` saem descomprimidos pelo `lzss.py` como três imagens 128×128 a 4 bpp (nibble baixo primeiro), e `palette.py` converte BGR555 ↔ RGB pela regra do `wte/re/render2d.md` e guarda as 8 cores do radar com a regra de pareamento.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/core/graphics.py`
  - `tools/kit2d/core/palette.py`
  - `tools/kit2d/selftest.py`
- Out:
  - —

## Done criteria

- [ ] `cli.py` ou selftest imprime o tamanho descomprimido de cada stream (8192 bytes cada) e o sha256, colados no Log
- [ ] os três sha256 são iguais nos discos de `roms/` medidos, com o digest de cada `DATSEL.BIN` no Log
- [ ] BGR555 → RGB → BGR555 é identidade nas 32768 cores; teto 248 conferido
- [ ] planta: stream truncado é recusado com mensagem, visto vermelho

## Notes

—

## Log de Execução
