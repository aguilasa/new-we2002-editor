# Plano — `tools/duckmcp/`, a lib comum para o MCP do DuckStation

Proposta de 2026-10-22. **Nenhuma fase foi executada.** O inventário do §1 foi
levantado nesta data lendo o código na HEAD `12202189`, e as contagens de
linha do §1.1 refeitas com `wc -l` na `50b3a35a`, depois do `f21182ea`; os números de linha
valem para elas e mudam com as migrações. Quem dá o número oficial de sítios
crus é a sonda versionada da Fase 0 (`tools/duckmcp/audit.py`), e é ela que o
Log da primeira task cola — este plano não é fonte de contagem.

## 0. Escopo

### Objetivo

Um pacote Python **stdlib puro** em `tools/duckmcp/` com tudo o que é preciso
para subir o fork do DuckStation com servidor MCP, falar com ele e dirigir
**qualquer jogo de PlayStation** — e todos os projetos do repositório que hoje
falam com o emulador (`pes2`, `looks`, `kits`, e o `kit2d` que está nascendo)
passando a usá-lo, sem cópia própria de transporte, lançador, sessão, botão,
captura, leitura de memória, breakpoint ou caminho de save state.

No fim do ciclo `tools/pes2/mcp.py`, `tools/pes2/fork.py` e
`tools/pes2/savestate.py` **não existem mais**, e um gate recusa qualquer
import deles.

### Não-objetivos

- **Nada de jogo.** A lib não conhece PES2, WE2002, serial, título de janela,
  endereço de RAM de jogo, rota de menu, tela ou slot de fixture. Ver §2.1.
- **Não muda o que as ferramentas medem.** Cada migração é refatoração: a
  saída das rotas, dos oráculos e dos gates tem de ser a mesma de antes (§5.2).
- **Não substitui o AppImage oficial.** `run_duckstation.sh` + `drive.py`
  continuam sendo o caminho que um terceiro reproduz sem o fork (§6.14 do
  [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md)); a lib só tira deles as
  constantes e a regra do `:98` duplicadas.
- **Não versiona o fork.** Licença CC-BY-NC-ND-4.0; continua fora do git,
  como hoje.
- **Não configura o DuckStation.** Decisão de 2026-09-02, mantida: a
  configuração da máquina é a que vale.

### Definição de pronto

1. `tools/duckmcp/` existe com os módulos do §3, e `duckmcp_selftest` passa
   sem nada instalado além de Python.
2. `duckmcp_live` sobe o fork contra **dois jogos de digest diferente** — o
   WE2002 japonês e o PES2 —, lista as ferramentas, avança quadro com
   `frame_step`, lê RAM e VRAM, e mata; nenhuma linha do código mudou entre as
   duas corridas.
3. `tools/duckmcp/audit.py` imprime **zero** sítio cru fora de
   `tools/duckmcp/` (§3.3), e cada regra do §3.3 foi vista vermelha com
   defeito plantado.
4. `tools/pes2/mcp.py`, `fork.py` e `savestate.py` apagados; nenhum import
   deles sobrou em `tools/`, `tests/`, `Makefile`, `make.ps1` nem nos `.sh`.
5. Os gates de antes continuam com o mesmo veredito: `pes2_selftest`,
   `pes2_boot`, `looks_selftest`, `looks_live`, `kits_selftest`,
   `kits_replay`, `kit2d_selftest` — e os que pulavam por falta de ambiente
   continuam pulando pelo mesmo motivo, não por erro de import.
6. `CLAUDE.md`, `Makefile`, `make.ps1` e o `perfil-kit2d.md` apontam para a
   lib; as variáveis `DUCKSTATION_*` estão documentadas e as `PES2_*` marcadas
   como legado aceito.

## 1. O que já se sabe — o inventário da duplicação

### 1.1 Onde mora hoje

O transporte e o lançador já são quase genéricos, e moram no projeto errado:

| arquivo | linhas | o que é |
|---|---|---|
| `tools/pes2/mcp.py` | 518 | `Client` (Streamable HTTP, `MCP-Session-Id`), `NotRunning`, `ToolError`, CLI `--list/--status/--call` |
| `tools/pes2/fork.py` | 921 | `launch`, `kill`, `status`, `recipe`, `which`, joystick, janela X e Win32, diálogo `Automatic Updater` |
| `tools/pes2/savestate.py` | 647 | o `.sav` do DuckStation: RAM, miniatura, mídia, `scan`, `diff` — sem nada de jogo |
| `tools/pes2/who_writes.py` | 492 | watchpoint de escrita e os auxiliares `hx`, `parse_address`, `register_value`, `split_store`, `is_paused` |
| `tools/pes2/mcp_drive.py` | 1391 | `McpSession` + rotas de PES2 |
| `tools/pes2/pad.py` | 200 | `Live`: um comando por vez ao fork já aberto |
| `tools/looks/oracle.py` | 10776 | `OneSession`, `Oracle`, ~30 funções que dirigem o fork |
| `tools/kits/oracle.py` | 3921 | `dump_slot`, `matrix_stops`, `pose_capture` e uso de `looks/oracle.py` |

Quem não usa: `tools/mcr/` (cartão, não emulador) e, por enquanto,
`tools/kit2d/` — mas a K2D-TASK-03 cria `tools/kit2d/oracle.py` sobre o MCP.

Como se chega lá: `sys.path.insert` de `tools/pes2` em `looks/oracle.py:74`,
`looks/atlas.py:105`, `looks/iso_source.py:27`, `looks/sprites.py:45`,
`kits/oracle.py:130`, `kits/core/tex.py:32`, `kit2d/selftest.py:40`; e
`importlib` por caminho em `kits/replay.py`, `kits/oracle.py`,
`kits/selftest.py` por causa do choque de nomes (`oracle`, `core`,
`confront`, `cli`, `layout` existem em mais de um projeto).

### 1.2 O que está repetido

- **Abrir sessão** (`Client()` + `initialize()`): `pad.py:113`,
  `mcp_drive.py:333`, `who_writes.py:264`, `fork.py:541`, `fork.py:752`.
- **Apertar e andar quadros**: `pad.Live.press` (`pad.py:69`, pausa antes de
  cada aperto), `McpSession.press` (`mcp_drive.py:382`, não pausa),
  `Oracle.press` (`looks/oracle.py:731`, confere que a tela mudou) e
  `oracle.tap` (`:4511`). Nome do botão normalizado por `capitalize()` em
  três lugares com regras diferentes. `PRESS_FRAMES=3`/`AFTER_FRAMES=17` em
  `pad.py` e `mcp_drive.py`; `CONFIRM_FRAMES=8`/`SETTLE_FRAMES=20` no `looks`.
- **Capturar**: `pad.Live.capture`, `McpSession.capture`, `Oracle.capture` —
  `take_screenshot(path=)`, confere o arquivo, embrulha em `drive.Frame`.
- **Esperar o emulador parar**: `who_writes.wait_for_hit` (`:190`, dorme 1 s,
  confere se o processo vive, cutuca com botão), `looks/oracle._wait_for_hit`
  (`:1509`, laço quente sem pausa e sem conferir vida) e uma terceira cópia
  inline em `_stops` (`:4258`).
- **Breakpoint de execução e leitura de registradores**, com o mesmo
  `finally: breakpoint clear; pause`: ~15 cópias — `gpu_list_heads`,
  `_burst`, `_stops`, `krom_answers`, `_watch_reads`, `_fired_among`,
  `_pose_cycle`, `_camera_matrix`, `_walk_stops`, `pose_builds`,
  `capture_camera`, `_camera_chain` em `looks/oracle.py`; `game_at`,
  `walk_photo` em `looks/confront.py`; `matrix_stops`, `pose_capture` em
  `kits/oracle.py`. `looks/oracle.catch_write` (`:1527`) é cópia de
  `who_writes.who_writes` (`:259`), refeita porque esta imprime em vez de
  devolver.
- **Sessão roubada**: `looks/oracle.OneSession` (`:628`) refaz o handshake
  quando o servidor responde `invalid MCP-Session-Id`; o `Client.reclaim` que
  a PES2-TASK-03 acrescenta ao `mcp.py` faz o mesmo. Com os dois, a perda é
  tratada duas vezes (armadilha 46, §1.3).
- **Lançar e matar**: `McpSession.__enter__`, `Oracle.__enter__` e
  `kits/oracle.dump_slot` (`:427`) — o último **sem** a guarda de joystick.
- **Janela**: `looks/oracle.hide_window`/`size_window` (`:553`, `:584`)
  refazem o ambiente X que `fork.env_for`/`_xdotool` já montam.
- **Constantes**: `SKIP=77` em `mcp.py`, `fork.py`, `who_writes.py`,
  `drive.py`, `boot_check.sh` e literal em `pad.py`; `Fail`/`Skip` definidos
  em `drive.py`, `fork.py`, `who_writes.py`, `savestate.py`;
  `~/.local/share/duckstation/savestates` em `drive.py:186`,
  `mcp_drive.py:267`, `looks/oracle.py:352`; a regra `:98` →
  `XAUTHORITY=""` três vezes dentro do próprio `fork.py` e aplicada a **todo**
  display em `drive.py`, o que contradiz a regra do `CLAUDE.md`; o AppImage
  em `fork.py`, `run_duckstation.sh`, `boot_check.sh`, `drive.py`.
- **Pixels**: BGR555 → RGB em `kits/oracle.vram_rows`, `_edit_page` e
  `looks/oracle._halfword`/`_vram_halfwords`; leitor de PNG em
  `looks/atlas.read_png` e `pes2/asset_write.read_png`.
- **Lista GP0**: `kits/oracle.read_frame` (`:694`) é quase literal o
  `looks/oracle.frame_commands` (`:5197`).

### 1.3 As armadilhas que são do emulador, não do jogo

Da §6.11 do [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md), estas valem para
qualquer jogo e passam a ser da lib — o código que as trata migra, e as
mensagens de erro passam a citar este plano:

| nº | o que diz | quem trata hoje |
|---|---|---|
| 5 | a janela nasce fora da tela sem window manager | `fork.launch` (`windowmove 0 0`) |
| 6, 27 | instância morta ainda responde ao `xdotool`; `windowkill` mata o processo | `fork.launch` por `_NET_WM_PID` |
| 7, 25 | `pkill -f`/`pgrep -f` casam o próprio shell | `fork.running_pids` (`pgrep -x`) |
| 8, 9, 31 | `SIGTERM` para num "Confirm Exit"; o processo é `AppRun`; filtro de nome | `fork.kill`, `run_duckstation.sh` |
| 14, 20 | `XDG_DATA_HOME` não isola; dados virgens param no assistente | `fork.RECIPE` |
| 28 | o binário do fork não acha as próprias bibliotecas | `fork.env_for` |
| 29, 30 | o diálogo é o `Automatic Updater`; a porta abre antes dele | `fork._dismiss_dialogs`, `wait_for_mcp` |
| 34 | `frame_step` custa ~57 ms | documentação de `Session.step` |
| 35 | o fork cai sozinho em execução livre, sem log | `mcp.Client._post`, `who_writes.wait_for_hit` |
| 36 | `press_button` sem `duration_frames` prende o botão | os quatro `press` |
| 46 | o servidor guarda uma sessão só; outro cliente a rouba | `Client.reclaim`, `OneSession` |

E a do joystick (`refuse_joysticks`, CORR-K3D-031): pad físico plugado
injeta entrada no jogo dirigido.

## 2. A decisão

Pacote novo em `tools/duckmcp/`, e não promover `tools/pes2/` a lib: o nome
do diretório já é o problema — `looks` e `kits` importando "do PES2" é como o
acoplamento começou. Decisões do usuário, 2026-10-22:

1. **Nome e forma**: `tools/duckmcp/`, pacote, importado como `import duckmcp`
   (ou `from duckmcp import session`). Quem usa insere **`tools/`** no
   `sys.path`, nunca `tools/duckmcp/` — assim `duckmcp/cli.py` não colide com
   o `cli.py` de outro projeto.
2. **Shims só durante o ciclo**: `tools/pes2/mcp.py`, `fork.py` e
   `savestate.py` viram re-exports enquanto as migrações correm; a task de
   fechamento os apaga.
3. **Variáveis neutras com fallback**: `DUCKSTATION_MCP_HOST`,
   `DUCKSTATION_MCP_PORT`, `DUCKSTATION_FORK`, `DUCKSTATION_APPIMAGE`,
   `DUCKSTATION_DISPLAY`. As `PES2_MCP_HOST`, `PES2_MCP_PORT`, `PES2_FORK`,
   `PES2_DUCKSTATION`, `PES2_DISPLAY` continuam lidas quando a nova não está
   definida, e ficam documentadas como legado. A nova ganha da velha.
4. **Parte do `mcp.py` da PES2-TASK-03**: ela estava em andamento ao se
   escrever este plano, com `SessionLost`, `Client(reclaim=True)` e o servidor
   de teste `_OneSessionServer` ainda não commitados. **Fechou em 2026-10-22,
   no commit `f21182ea`**, e o cliente da lib parte do `mcp.py` dessa versão.
   `depends_on` não atravessa ciclo; a task 01 confere no Log que a HEAD
   contém `f21182ea`.
5. **Agnóstico de jogo** — §2.1.

### 2.1 Agnóstico de jogo

A lib tem de dirigir **qualquer** jogo de PS1 no fork. Isso decide o que
entra:

- **Entra hardware e emulador**: RAM em `0x80000000`, 2 MiB, espelhos
  `KSEG0`/`KSEG1`; scratchpad; VRAM 1024×512 em BGR555; registradores do
  R3000A e do GTE; o formato dos pacotes GP0 e o andar de uma lista de
  comandos a partir de uma função de leitura de RAM; o formato `.sav` do
  DuckStation; os botões do DualShock; os diretórios, processos e diálogos do
  DuckStation.
- **Fica fora**: endereço de RAM de jogo, rota de menu, reconhecimento de
  tela, slot de fixture, `work/*-states`, serial, título de janela.
- **Nenhum default de jogo.** `launch(cue)` acha a janela pelo PID do filho e
  pega a mais larga que não é diálogo do emulador — o `ANY_WINDOW` de hoje
  vira o comportamento padrão. Título é filtro opcional do chamador; o
  `^Pro Evolution Soccer 2$` de `fork.py:126` muda para o `pes2`.
- **O serial vem do disco ou do emulador.** `Session.game()` devolve serial e
  título do que está carregado (`get_status`, ou a mídia do `.sav`);
  `state_path(serial, slot)` recebe o serial. `SLES-03957` e `SLPM-87056`
  ficam nos projetos.

## 3. Arquitetura

### 3.1 Os módulos

| módulo | conteúdo | vem de |
|---|---|---|
| `__init__.py` | versão; reexporta `Session`, `Client`, os erros | — |
| `errors.py` | `SKIP = 77`, `Fail`, `Skip`, `NotRunning`, `ToolError`, `SessionLost` | `mcp.py`, `fork.py`, `drive.py`, `who_writes.py` |
| `env.py` | as variáveis do §2 com fallback; `display()`; `x_env(display)` — a regra `:98` → `XAUTHORITY=""` em **um** lugar; `fork_home()`, `appimage()`, `data_dir()`, `savestates_dir()` por SO; `state_path(serial, slot)`; `is_roms(path)` | `fork.py:107-246`, `looks/oracle.py:330-352`, `drive.py:186`, `mcp_drive.py:267` |
| `client.py` | `Client`: transporte, `initialize`, `tools()`, `call()`, `reclaim`, decodificação JSON/SSE, diagnóstico de `NotRunning` (processo vivo × morto, armadilha 35) | `pes2/mcp.py` depois da PES2-TASK-03 |
| `fork.py` | `launch(image, match=None, ...)`, `kill`, `running_pids`, `status`, `which_binary`, `RECIPE`, `joysticks`/`refuse_joysticks`, achar janela (X e Win32), dispensar o `Automatic Updater`, `hide_window`, `size_window` | `pes2/fork.py`, `looks/oracle.py:553-616` |
| `buttons.py` | os nomes que o `press_button` aceita, e `canonical(name)` | `pad.BUTTONS`, os três `capitalize()` |
| `session.py` | `Session`: context manager (recusa joystick, lança, pausa, mata na saída) e `Session.attach()` para um fork já aberto; `pause`, `resume`, `step(n)`, `frame()`, `run(seconds, fast)`, `press(button, frames, after)`, `capture(path)`, `read_ram`, `read_vram_region`, `dump_vram`, `write_vram_region`, `gpu_state`, `gte_registers`, `load_state`, `save_state` (espera o arquivo mudar), `game()`, e `call()` como escape documentado para ferramenta sem método | `McpSession`, `pad.Live`, `Oracle`, `kits/oracle.dump_slot` |
| `debug.py` | `wait_for_pause` (uma só: dorme, confere vida, cutuca se pedido); `breakpoints(session, addresses, type)` — context manager que limpa e pausa **sempre**, no `finally`; `stops(...)`; `who_writes(...)` devolvendo dict (cobre `catch_write`); `watch_reads`; `vram_watch`; `hx`, `parse_address`, `register_value`, `split_store`, `is_paused` | `who_writes.py`, `looks/oracle.py:1509-1600, 4229, 6484` |
| `psx.py` | constantes de hardware: faixas de RAM, scratchpad, VRAM, `mask_address` | `looks/oracle.py:84`, `savestate.py:89, 270` |
| `gpu.py` | pacotes GP0 e o andar de uma lista de comandos dada `read(address, size)` | a parte de `looks/oracle.walk_gpu_list`/`commands_of` que não depende de `layout` |
| `png.py`, `vram.py` | um leitor de PNG stdlib; BGR555 ↔ RGB | `looks/atlas.read_png`, `pes2/asset_write.read_png`, `kits/oracle.vram_rows`, `looks/oracle._halfword` |
| `savestate.py` | o `.sav` inteiro | `tools/pes2/savestate.py`, movido |
| `cli.py` | `list`, `status`, `call TOOL k=v`, `launch`, `kill`, `recipe`, `which` | `mcp.py main`, `fork.py main` |
| `audit.py` | conta, por projeto, os sítios crus do §3.3 | — |
| `selftest.py`, `controls.py` | o gate e os defeitos plantados | — |

Captura devolve **caminho**, não imagem: PIL é dependência de quem decodifica
(`drive.Frame` no `pes2`, `atlas` no `looks`), e o import da lib nunca a pede.

### 3.2 O que continua nos projetos

- `pes2`: `drive.py` (`Frame`, AppImage, `xdotool`), as rotas de
  `mcp_drive.py` sobre `Session`, `pad.py` sobre `Session.attach`, o título
  de janela do jogo, serial, slots.
- `looks`: `Oracle` como camada fina sobre `Session` (preflight, estados de
  `work/looks-states`, reconhecimento da `LOOKS SET`), e toda a análise.
- `kits`: os oráculos sobre `looks.Oracle` e `duckmcp.debug`.
- `kit2d`: o `oracle.py` que a K2D-TASK-03 cria, já sobre a lib.

### 3.3 Regras de desenho

Cada uma afirmada pelo `selftest.py` e com defeito plantado no `controls.py`:

- **(a)** importar `duckmcp` e qualquer módulo dele não importa PIL, Qt,
  numpy nem nada fora da stdlib;
- **(b)** fora de `tools/duckmcp/`, nenhum `import mcp`, `import fork`,
  `import savestate` vindo de `tools/pes2/`, e nenhum `.client.call(` nem
  `Client(` cru — o resto do repositório fala com `Session` ou `debug`;
- **(c)** dentro de `tools/duckmcp/`, nenhum serial de jogo (padrão
  `S[LC][EPU][SM]-\d{5}`), nenhum nome de projeto (`pes2`, `looks`, `kits`,
  `kit2d`, `WE2002`, `PES2` — fora de comentário de linhagem marcado), e
  nenhum endereço literal fora das faixas de `psx.py`. **Exceção única**: os
  cinco nomes legados `PES2_MCP_HOST`, `PES2_MCP_PORT`, `PES2_FORK`,
  `PES2_DUCKSTATION` e `PES2_DISPLAY`, como código e só no `env.py`, porque a
  decisão 3 do §2 os lê como fallback; um sexto nome, ou um deles fora do
  `env.py`, é vermelho;
- **(d)** só `env.py` lê variável de ambiente, e só `env.py` monta
  `XAUTHORITY`.

O `audit.py` é a sonda versionada da regra (b): imprime os sítios por projeto,
e é o número que cada task de migração cola no Log antes e depois.

## 4. Riscos de migração

### 4.1 Controles plantados por caminho e por texto

Os controles negativos dos projetos acham o defeito por caminho de arquivo e
por linha exata. Mover o código os quebra **em silêncio**: o controle deixa de
casar e o selftest acusa "controle não aplica", ou pior, passa a plantar num
arquivo que ninguém mais usa.

- `kits/controls.py`: `fork-joystick-let-through` (`pes2/fork.py`,
  `refuse_joysticks`), `looks-oracle-joystick-unasked` (`looks/oracle.py`,
  `fork.refuse_joysticks()` no `Oracle.__enter__`),
  `replay-capture-joystick-late` (`kits/replay.py`),
  `oracle-replay-colour-unread`; e `COPIED` em `kits/controls.py:31` e
  `kits/ui_check.py:93`, que precisam ganhar `tools/duckmcp`.
- `looks/controls.py`: `oracle-session-never-renewed` (a linha
  `if SESSION_LOST not in str(exc):` do `OneSession`), `oracle-preflight-late`,
  `oracle-any-screen`; e o `_sandbox` de `:1115`.

Regra: a task que move o código reaponta o controle **na mesma task** e mostra
o vermelho no Log. O de sessão roubada migra para o `duckmcp/controls.py`,
porque o `OneSession` deixa de existir.

### 4.2 Monkeypatch e falsos

- `kits/selftest.py:2078-2115` troca `fork.joysticks`, `fork.launch` e
  `looks_oracle.model_maps` por atributo de módulo. Depois da migração o
  atributo certo é o de `duckmcp.fork`; trocar o do shim não teria efeito.
- `looks/oracle.py:9990-10035` e `who_writes.self_check` usam clientes falsos.
  `Session` aceita qualquer objeto com `initialize`, `call`, `session`,
  `server`, e os falsos migram para o `duckmcp/selftest.py`.
- `looks/oracle.py:10309-10327` troca `globals()["PREREQUISITES"]`;
  `PREREQUISITES` continua global do `looks`.

### 4.3 Comportamento que difere entre as cópias

Unificar é escolher. Cada uma das diferenças abaixo é decidida na task que a
unifica, com o porquê no Log, e a escolha é a que preserva a saída medida:

- `pad.Live.press` pausa antes de cada aperto; `McpSession.press` não.
- `looks._wait_for_hit` não dorme nem confere vida; `who_writes.wait_for_hit`
  sim. A versão única confere vida (armadilha 35) e o intervalo é parâmetro;
  o `looks` mede antes e depois que a contagem de paradas não muda.
- `drive.py` zera `XAUTHORITY` em todo display; a regra é só no `:98`.
- `looks/oracle.main` não mapeia `Fail`/`NotRunning`/`ToolError` para 77/1.

### 4.4 Outros

- **Varredura de endereços**: a regra 1 do `looks/selftest.py` só varre
  `tools/looks/`. Endereço que migrar para a lib escaparia dela; a regra (c)
  do §3.3 é a que o pega.
- **kit2d vivo**: a K2D-TASK-03 e as tasks de emulador do `kit2d` estão
  pendentes. Uma task deste ciclo registra a decisão no
  `perfil-kit2d.md` (arquivo declarado), sem tocar em task do `kit2d`.
- **Windows**: `fork.py` tem ramos Win32, e o `make.ps1` da raiz o chama
  (`run-…`, `pes2`); `make.ps1`, `Makefile`, `boot_check.sh` e
  `run_duckstation.sh` mudam de caminho junto com a Fase 2.
- **Uma instância por vez**: toda task que sobe o fork declara o recurso
  `emulador` e, se usar fixture, `save-states`; os testes vivos têm
  `RESOURCE_LOCK duckstation`.

## 5. Como se verifica

### 5.1 A lib

- `python3 tools/duckmcp/selftest.py` — sai 0 e a última linha diz quantos
  checks rodaram. Cobre: as regras do §3.3; decodificação JSON e SSE; o
  servidor de teste (sessão roubada recuperada uma vez, segunda perda é erro,
  outros erros passam sem novo handshake); `wait_for_pause` com processo morto
  falhando com a armadilha 35 no texto; `breakpoints` limpando e pausando
  depois de exceção; `env` com variável nova ganhando da velha e a velha
  valendo sozinha; `x_env` só zerando `XAUTHORITY` no `:98`; `launch`
  recusando `roms/` e joystick.
- `python3 tools/duckmcp/controls.py` — planta cada defeito numa cópia da
  árvore e exige o vermelho; a última linha diz quantos.
- `duckmcp_live`, com `DUCKSTATION_TEST_IMAGE` apontando um `.cue` de cópia:
  sobe, conta as ferramentas que o servidor declara, `frame_step` avança
  `frame_number`, `read_ram` devolve 2 MiB, `dump_vram` devolve 1024×512,
  `game()` devolve o serial do disco, mata. *Skip* 77 sem a variável, sem o
  fork ou sem display. Na verificação final, corre duas vezes, com dois jogos
  de digest diferente.

### 5.2 As migrações não mudam o que se mede

| projeto | antes e depois, igual |
|---|---|
| `pes2` | as rotas de `mcp_drive.py` (`title`, `main-menu`, `team-select`, `edit`, `result`, `ending`, `replay`) dão PNG idêntico byte a byte; `pes2_selftest` e `pes2_boot` com o mesmo veredito |
| `looks` | `oracle.py --check-live` passa; `oracle.py --screen` sem diferença contra `tools/looks/screen.json`; `looks_selftest` com a mesma contagem de controles |
| `kits` | `kits_replay` e `kits_selftest` com o mesmo veredito; `dump_slot` ganha a guarda de joystick e o controle dela fica vermelho com o defeito |
| `kit2d` | `kit2d_selftest` igual |

### 5.3 O ciclo

`ctest -R tasks` verde antes de todo commit; `python3 tools/duckmcp/audit.py`
colado no Log de cada task de migração.

## 6. Fases

| fase | entrega | depende de |
|---|---|---|
| 0 | **esqueleto**: `__init__.py`, `errors.py`, `env.py`, `audit.py` (o número do "antes"), `selftest.py` com as regras (a), (c), (d) e plantas, `duckmcp_selftest` no `ctest` | PES2-TASK-03 (`f21182ea`) |
| 1 | **transporte**: `client.py` com `reclaim`, `cli.py list/status/call`, servidor de teste no selftest; `pes2/mcp.py` vira shim | 0 |
| 2 | **lançador**: `fork.py` sem título de jogo, `hide_window`/`size_window`, `cli.py launch/kill/status/recipe/which`; `pes2/fork.py` vira shim que passa o título do PES2; `make.ps1`, `Makefile`, `boot_check.sh`, `run_duckstation.sh` apontados; `duckmcp_live` no `ctest` | 1 |
| 3 | **primitivas**: `buttons.py`, `session.py` (com `game()`), `psx.py`, `gpu.py`, `png.py`, `vram.py`; `savestate.py` movido, shim no `pes2` | 2 |
| 4 | **depuração**: `debug.py`; a regra (b) e o `controls.py` da lib completos | 3 |
| 5 | **migração do `pes2`**: `mcp_drive.py`, `pad.py`, `who_writes.py`, `drive.py`, `selftest.py` | 4 |
| 6 | **migração do `looks`**: `Oracle` sobre `Session`, `OneSession` some, as esperas e os laços de breakpoint sobre `debug`, estados por `env`; `confront.py`; controles reapontados | 4 |
| 7 | **migração do `kits`**: `dump_slot`, `matrix_stops`, `pose_capture`, `read_frame`, `vram`; controles, `COPIED` e monkeypatch reapontados | 6 |
| 8 | **documentação e `kit2d`**: `CLAUDE.md` (seção nova da lib, tabelas do PES2 e do `looks`), decisão no `perfil-kit2d.md`, `docs/PLAN-PES2-PSX.md` §6.11 remetendo ao §1.3 daqui | 5, 6, 7 |
| 9 | **fechamento**: shims apagados, `audit.py` em zero, regra (b) vermelha com import antigo plantado, `duckmcp_live` verde com os dois jogos, toda a bateria do §5.2 | 8 |

As fases 5 e 6 não dividem arquivo e podem andar em ondas, mas não ao mesmo
tempo no emulador. **O que não pode ser pulado**: a Fase 0, sem a qual não há
número de antes para o zero do fim, e a Fase 9, sem a qual os shims ficam e a
duplicação volta pela porta dos fundos.

## 7. Como iniciar o ciclo

1. `/rite:new-cycle duckmcp --prefix DMCP` — pasta `docs/tasks/duckmcp/`,
   perfil `docs/prompts/perfil-duckmcp.md` com uma entrada por fase (0 a 9) em
   "Verificações específicas por fase", e os recursos serializados `emulador`,
   `save-states` e `tela` nas tasks que sobem o fork.
2. `/rite:plan-to-tasks duckmcp docs/PLAN-DUCKMCP-PY.md` — `source_of_truth`
   com âncora de seção (`rite anchors docs/PLAN-DUCKMCP-PY.md` lista as
   válidas).
3. A primeira task confere que a HEAD contém o commit da PES2-TASK-03
   (`f21182ea`, §2, decisão 4).
4. As regras que valem o ciclo todo são as cinco do `CLAUDE.md` ("Convenções
   da documentação"). Duas pesam mais aqui: **número colado da ferramenta**
   (o `audit.py` é a ferramenta; a contagem do §1.2 não é número de Log), e
   **fechar um veredito é varrer quem dizia o anterior** — cada caminho que
   muda (`tools/pes2/mcp.py`, `fork.py`, `savestate.py`, as variáveis
   `PES2_*`) aparece em `CLAUDE.md`, em planos, perfis e receitas.
