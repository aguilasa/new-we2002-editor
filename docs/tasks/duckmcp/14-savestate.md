---
id: DMCP-TASK-14
---

# DMCP-TASK-14 — `savestate.py` movido para a lib, com shim no `pes2`

## Goal

`tools/pes2/savestate.py` vai inteiro para `tools/duckmcp/savestate.py` (`git mv` + shim), sem nada de jogo, e o `savestate.self_check` passa a rodar no selftest da lib.

## Arquivos a criar ou modificar

- In:
  - o move e o shim
- Out:
  - trocar quem importa `savestate` (Fases 5 a 7)

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/pes2/selftest.py` sai 0
- [x] `git log --follow --oneline tools/duckmcp/savestate.py | tail -1` mostra o primeiro commit do arquivo original
- [x] `python3 tools/duckmcp/savestate.py info <um .sav do looks>` dá a mesma saída que o `tools/pes2/savestate.py info` dava na HEAD anterior, colada no Log

## Notes

## Log de Execução

### 2026-10-22 — HEAD 74cfe939

`tools/pes2/savestate.py` foi copiado para `tools/duckmcp/savestate.py` e
adaptado com o mínimo: 57 das 647 linhas originais mudam
(`diff <(git show HEAD:tools/pes2/savestate.py) tools/duckmcp/savestate.py | grep -c '^<'`
→ `57`), para o git ver o rename quando o commit fizer o move. O
`tools/pes2/savestate.py` virou shim que reexporta os objetos da lib (mesma
identidade: `SaveState`, `Skip`, `BadState`, `scan`, `diff`, `mask_address`,
`_synth`, `_unzstd`, `main`), com um `self_check` que mantém o contrato antigo
(lista de rótulos que falharam, `verbose`).

O que a adaptação mudou, e por quê:

- **numpy saiu.** A regra (a) julga também import dentro de função, e o
  `scan`/`diff`/`self_check` importavam numpy. Os dois foram reescritos sobre
  `bytes` (`find` em toda posição, sobreposição incluída; `diff` pulando blocos
  iguais de 4 KiB). `scan` devolve `list` de `int` em vez de array. Conferido
  contra a versão numpy da HEAD nos dois `.sav` do looks: `diff` dá as mesmas
  8715 corridas, e `scan` dá a mesma lista em larguras 1, 2 e 4, com e sem
  sinal, para cinco pares de valores. O self-check deixou de levantar `Skip`
  por falta de numpy e ganhou um caso de valor de 2 bytes em índice ímpar.
- **Pillow saiu do `shot`**, que agora grava o PNG com `duckmcp.png.encode`
  (RGB, sem filtro). Mesmos pixels; os bytes do arquivo não são os do Pillow.
- `self_check` da lib devolve `(nome, passou, detalhe)` como os outros
  módulos, e roda no `duckmcp/selftest.py`.
- Regra (c): o serial sintético virou `NONE-00000`; `MAGIC` é
  `int.from_bytes(b"DUCC", "little")`; `PSX_RAM` é `psx.RAM_SIZE` e
  `mask_address` delega a `psx.mask_address`; "looks like" virou "reads like";
  as menções a task e CORR de outros ciclos foram para um bloco `# lineage:`.
- `Skip` vem de `duckmcp.errors`; `BadState` ficou local (é do formato).

Vermelho visto (cópia da árvore em scratchpad, desligando a guarda do marcador
deslocado e repondo o serial antigo):

```
$ python3 <cópia>/tools/duckmcp/selftest.py --quiet; echo exit=$?
  FAIL  savestate: a kernel mark 45 bytes off is refused  accepted it -- this is the bug that shipped
  FAIL  rule (c): savestate.py holds no game serial  line 468: SLES-00000
duckmcp_selftest: 361 check(s) ran, 2 failure(s)
exit=1
```

Verde, na árvore:

```
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 361 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/pes2/selftest.py; echo exit=$?
  ok   savestate.py reader, scan and guards
...
OK
exit=0
$ python3 tools/duckmcp/controls.py; echo exit=$?
duckmcp_controls: 21 control(s), 21 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3, (live) 1/1, (session) 1/1
exit=0
$ python3 tools/looks/selftest.py --quiet | tail -1
looks_selftest: 0 failure(s)
$ ctest --test-dir build -R 'duckmcp_selftest|pes2_selftest'
100% tests passed, 0 tests failed out of 2
```

Saída de `info` idêntica à da HEAD anterior: as referências foram capturadas
com o arquivo antigo (`python3 tools/pes2/savestate.py info
work/looks-states/SLPM-87056_<n>.sav`) antes da mudança, e comparadas com
`cmp` contra a lib e contra o shim:

```
$ python3 tools/duckmcp/savestate.py info work/looks-states/SLPM-87056_1.sav > lib_1.txt; cmp lib_1.txt sav_info_before_1.txt  -> identical
$ python3 tools/pes2/savestate.py info work/looks-states/SLPM-87056_1.sav > shim_1.txt; cmp shim_1.txt sav_info_before_1.txt -> identical
$ (idem para _2)                                                                                                       -> identical
3104c3e8d1a35b61759b51cb92267a984232d8d5908ea2c56f368155388a9242  lib_1.txt = shim_1.txt = sav_info_before_1.txt
38a70d7dddc0932d757ce311c69a5368b5b93808fd7baa1adecd5bb3b8ff6ceb  lib_2.txt = shim_2.txt = sav_info_before_2.txt
```

O critério do `git log --follow` fica aberto: só se confere depois do commit
que registra o move, e quem commita é o fluxo principal.

Critério do `git log --follow`, medido pelo fio principal depois do commit de trabalho `3495bb77`: `git log --follow --oneline tools/duckmcp/savestate.py | tail -1` → `d9d090e9 feat(pes2): read PSX RAM out of a save state, and drop the emulator fork`, o mesmo de `git log --oneline --diff-filter=A -- tools/pes2/savestate.py | tail -1` (o primeiro commit do arquivo original). Um commit só basta: com o caminho antigo virando shim no mesmo commit, o `--follow` acha a cópia — testado antes numa worktree descartável, contra a alternativa de dois commits (rename puro, depois o shim), e as duas dão a mesma linha.
