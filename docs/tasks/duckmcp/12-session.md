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

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] o selftest, com cliente falso, afirma que `press` sempre manda `duration_frames` (armadilha 36) e anda `frames + after` quadros; `Session(fake)` aceita qualquer objeto com `initialize`, `call`, `session`, `server`
- [x] `capture` devolve caminho e não importa PIL — o check de imports da Fase 1 continua `[]`
- [x] o controle `press-without-duration` fica vermelho, visto no Log

## Notes

As diferenças entre as cópias de `press` (§4.3) se decidem nas tasks de migração, com parâmetro aqui.

## Log de Execução

### 2026-10-22 — HEAD `791ca241`

**Feito.** `tools/duckmcp/buttons.py` novo: `BUTTONS` com os dezesseis nomes
na grafia do enum do `press_button`, e `canonical(name)`, que casa sem olhar
caixa e recusa com `UnknownButton` (um `ValueError`) listando os nomes. A
grafia foi lida do próprio schema que o fork compila no binário
(`strings -a ~/Applications/duckstation-mcp/bin/duckstation-qt | grep
'"name":"press_button"'`): `Cross, Circle, Square, Triangle, Up, Down, Left,
Right, L1, L2, R1, R2, Start, Select, L3, R3` — a mesma lista de
`pad.BUTTONS`. O self-check afirma que `canonical()` concorda com a regra
`capitalize()` que substitui em todo nome válido, então a troca nas tasks de
migração não muda o que se manda ao servidor.

`tools/duckmcp/session.py` novo, com `Session` em três entradas: `Session(image)`
como context manager (recusa joystick, `fork.launch`, pausa; mata na saída só
se lançou — se o `launch` levanta, mata só quando apareceu pid novo, a regra
da CORR-DMCP-011; se a primeira pausa falha, mata antes de o erro sair do
`__enter__`); `Session(client)` / `Session(client=...)`, que embrulha qualquer
objeto com `initialize`, `call`, `session` e `server`, handshake e pausa no
enter, nunca mata; e `Session.attach(client=None)`, que não pausa nem mata.
Métodos: `pause`, `resume` (`continue`), `step`, `frame`, `run`, `press`,
`capture`, `read_ram`, `read_vram_region`, `dump_vram`, `write_vram_region`,
`gpu_state`, `gte_registers`, `load_state`, `save_state`, `game()` e `call()`.
Os nomes de ferramenta e de argumento são os dos schemas do binário, lidos na
mesma corrida de `strings`. `Session` é reexportada do `__init__`, que sobe
para a versão 0.2.0.

**Decisões.**

- `press(button, frames=3, after=17, pause_first=False, slot=None)` manda
  **sempre** `duration_frames` e anda `frames + after` quadros. O default 3/17
  é o par medido em 2026-09-03 e usado pelas rotas e pelo `pad`; quem mede com
  outro par (confirmação mais longa, assentamento mais longo) passa `frames=` e
  `after=`, e o `pause_first=True` reproduz o `pad.Live.press`, que pausa antes
  de cada aperto. Qual par e qual pausa cada chamador mantém fica para as tasks
  de migração (§4.3).
- `capture(path)` devolve o caminho, apaga o arquivo velho antes (achar o
  arquivo prova que esta chamada o escreveu, como o `dump_slot` fazia) e todo
  caminho vai absoluto ao servidor, que resolve relativo contra o diretório do
  emulador.
- `read_vram_region` não recebe caminho no schema: o servidor escolhe um
  temporário e devolve `output_path`; com `path=` o arquivo é movido para lá.
- `load_state(slot, settle=0, path=None)`: o `settle` é parâmetro porque as
  cópias andam 2, 30 ou a constante do chamador depois do load.
- `save_state(slot, wait_for=None, serial=None)` espera o mtime do arquivo
  passar o de antes; sem `wait_for` o caminho é `env.state_path(serial, slot)`
  com o serial dado ou lido do `game()`.
- `game()` devolve `Game(serial, title)` de `get_status` `game_serial` e
  `game_title`, os dois campos que o schema do `get_status` promete no
  `detail='basic'`; campo vazio ou ausente vira `None`. Isso está medido
  contra o schema, não contra um fork rodando: a confirmação viva é da
  DMCP-TASK-15.

**Verificação** (comandos e saída decisiva no relatório do worker): o
`selftest.py` sai 0; as linhas nomeadas de `session:` e `buttons:` passam
(press manda `duration_frames` e anda `frames + after`, `Session(fake)` aceita
qualquer objeto com os quatro atributos, `capture` devolve caminho, a saída
mata só quando lançou, `canonical()` faz ida e volta e recusa lixo); o import
de `duckmcp.session` e `duckmcp.buttons` não carrega PIL, PySide6 nem numpy; e
o controle `press-without-duration`, que tira `duration_frames` do `press` numa
substituição exata, fica vermelho na asserção
`session: press always sends duration_frames (pitfall 36)`.
- **Closed** — commit `0c58ebd7` (2026-10-22): feat(duckmcp): add Session and buttons.canonical; press always sends duration_frames
  - Files (`git show --name-status 0c58ebd7`):
    - `M docs/tasks/duckmcp/12-session.md`
    - `M tools/duckmcp/__init__.py`
    - `A tools/duckmcp/buttons.py`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/selftest.py`
    - `A tools/duckmcp/session.py`
- **Reviewed** (2026-10-22) at `225d5145`: CORR-DMCP-012

**Transcrição refeita em 2026-10-22, na HEAD `004cc884`** (CORR-DMCP-012; antes, o Log só resumia e remetia ao relatório do worker):

```text
$ python3 tools/duckmcp/selftest.py | grep -E '  (ok|FAIL) +(session|buttons):'
  ok    buttons: there are sixteen distinct buttons
  ok    buttons: canonical() round-trips every name in any capitalisation
  ok    buttons: canonical() agrees with the old capitalize() rule on every valid name
  ok    buttons: canonical() rejects junk with the list of names
  ok    buttons: UnknownButton is a ValueError
  ok    session: press always sends duration_frames (pitfall 36)
  ok    session: press sends the canonical button name
  ok    session: press steps frames + after (3+17, 5+0, 1+40)
  ok    session: press pauses only with pause_first
  ok    session: press refuses an unknown button before any call
  ok    session: press refuses a hold of zero frames
  ok    session: Session(fake) takes any object with initialize, call, session, server
  ok    session: Session(client=...) refuses an object without server
  ok    session: Session('a.cue') keeps a string as the image
  ok    session: capture returns the path, as a str
  ok    session: capture refuses a screenshot that wrote no file
  ok    session: read_ram returns exactly size bytes
  ok    session: read_ram refuses a short file
  ok    session: read_ram refuses more than read_memory's 2 MiB
  ok    session: read_vram_region moves the server's file to the path given
  ok    session: read_vram_region refuses a rectangle outside VRAM
  ok    session: dump_vram returns the path
  ok    session: write_vram_region sends raw from a file of w*h*2 bytes
  ok    session: write_vram_region refuses data of the wrong size
  ok    session: game() reads game_serial and game_title
  ok    session: game() answers None for an empty serial
  ok    session: save_state waits for the state file and returns it
  ok    session: save_state fails when the file never moves
  ok    session: load_state loads, then steps settle frames
  ok    session: exit does not kill a wrapped or attached client
  ok    session: exit kills the fork this session launched, once
  ok    session: a launch that fails after its Popen stops the new pid
  ok    session: a skipped launch leaves another session's emulator alive
  ok    session: a pause that fails in __enter__ kills what it launched
  ok    session: attach handshakes and does not pause
  ok    session: importing duckmcp.session loads no PIL, PySide6 or numpy
$ python3 tools/duckmcp/selftest.py | tail -1
duckmcp_selftest: 361 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/controls.py --only press-without-duration
baseline: the untouched sandbox is green
red    press-without-duration (rule session): FAIL  session: press always sends duration_frames (pitfall 36)  [{'button': 'Down'}, {'button': 'Cross'}, {'button': 'Start'}]
duckmcp_controls: 1 control(s), 1 red as required; per rule (session) 1/1
```
