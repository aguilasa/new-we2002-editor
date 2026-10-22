---
id: DMCP-TASK-08
---

# DMCP-TASK-08 — `fork.py` agnóstico de jogo — janela pelo PID, título opcional, `hide_window` e `size_window`

## Goal

`tools/duckmcp/fork.py` tem `launch(image, match=None, ...)`, `kill`, `running_pids`, `status`, `which_binary`, `RECIPE`, `joysticks`/`refuse_joysticks`, achar janela (X e Win32), dispensar o `Automatic Updater`, e `hide_window`/`size_window` vindos do `looks/oracle.py`. Sem `match`, a janela é a mais larga do PID que não é diálogo do emulador; nenhum título de jogo no arquivo.

## Arquivos a criar ou modificar

- In:
  - `tools/duckmcp/fork.py` e os checks do `fork.self_check`
- Out:
  - mudar `tools/pes2/fork.py` (DMCP-TASK-09)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] o selftest cobre o que o `fork.self_check` cobria: lançar sem fork instalado é `Skip`; `roms/` recusado nos dois separadores; joystick recusado; os nomes de processo no `kill`; `running_pids` nunca devolve o próprio PID
- [ ] `grep -n 'Pro Evolution' tools/duckmcp/fork.py` não acha nada
- [ ] o controle da regra (c) plantando `GAME_WINDOW = "^Pro Evolution Soccer 2$"` no `fork.py` da lib fica vermelho, visto no Log

## Notes

Os ramos Win32 não se medem nesta máquina; o Log diz isso em vez de dizer que passaram.

## Log de Execução
