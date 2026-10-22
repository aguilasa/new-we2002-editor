---
id: DMCP-TASK-12
---

# DMCP-TASK-12 — `buttons.py` e `session.py` — a sessão, com `game()`

## Goal

`Session` é context manager (recusa joystick, lança, pausa, mata na saída) e tem `Session.attach()` para um fork já aberto, com `pause`, `resume`, `step`, `frame`, `run`, `press`, `capture`, `read_ram`, `read_vram_region`, `dump_vram`, `write_vram_region`, `gpu_state`, `gte_registers`, `load_state`, `save_state`, `game()` e `call()`. `buttons.canonical()` é o único lugar que normaliza nome de botão.

## Arquivos a criar ou modificar

- In:
  - os dois módulos e os checks com cliente falso
- Out:
  - migrar quem usa `McpSession`, `pad.Live`, `Oracle` (Fases 5 a 7)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] o selftest, com cliente falso, afirma que `press` sempre manda `duration_frames` (armadilha 36) e anda `frames + after` quadros; `Session(fake)` aceita qualquer objeto com `initialize`, `call`, `session`, `server`
- [ ] `capture` devolve caminho e não importa PIL — o check de imports da Fase 1 continua `[]`
- [ ] o controle `press-without-duration` fica vermelho, visto no Log

## Notes

As diferenças entre as cópias de `press` (§4.3) se decidem nas tasks de migração, com parâmetro aqui.

## Log de Execução
