---
id: DMCP-TASK-10
---

# DMCP-TASK-10 — `duckmcp_live` — subir o fork com um `.cue` qualquer, andar, ler e matar

## Goal

`tools/duckmcp/live.py` é o alvo `duckmcp_live`: com `DUCKSTATION_TEST_IMAGE` apontando o `.cue` de uma cópia, sobe o fork, lista as ferramentas, pausa, dá `frame_step` e confere que `frame_number` avançou, e mata. Sai 77 sem a variável, sem o fork ou sem display. `RESOURCE_LOCK duckstation`. A Fase 3 acrescenta RAM, VRAM e `game()`.

## Arquivos a criar ou modificar

- In:
  - `live.py` e o `add_test`
- Out:
  - RAM, VRAM, `game()` (DMCP-TASK-15)

## Done criteria

- [ ] `ctest --test-dir build -R duckmcp_live` sem a variável: *skipped*, com a razão impressa
- [ ] com `DUCKSTATION_TEST_IMAGE=<cópia do WE2002 japonês>.cue DISPLAY=:98 XAUTHORITY=` dentro do comando: `Passed`, e a saída do `live.py` colada no Log com o número de ferramentas que o servidor declarou
- [ ] uma planta (`frame_step` trocado por `pause`) deixa o `live.py` vermelho, visto no Log
- [ ] depois da corrida, `python3 tools/duckmcp/cli.py status` dá `pids: []`

## Notes

A imagem é **cópia**, nunca `roms/`; o `launch` recusa. O teste usa só o que a lib tem, nada de jogo.

## Log de Execução
