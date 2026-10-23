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

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/duckmcp/controls.py` sai 0, e a última linha diz quantos controles cobrem as regras (a) a (d)
- [x] um `import fork` novo em `tools/kit2d/` (fora da lista) deixa o selftest vermelho, visto no Log
- [x] o tamanho da lista `PENDING` bate com o total do `audit.py`, os dois colados no Log

## Notes

## Log de Execução

### 2026-10-23 — execução

**O que mudou.**

- `tools/duckmcp/audit.py`: `site_keys(doc)` devolve o `Counter` de
  `(arquivo, categoria, linha impressa)` — a chave da regra (b), **sem número
  de linha**, para uma edição alheia acima do sítio não mexer na lista; e
  `--keys` imprime essas chaves com a contagem, no formato do `PENDING`. O
  `self_check` ganhou a asserção da chave; a docstring deixou de dizer que o
  gate "vem depois".
- `tools/duckmcp/selftest.py`: `MIGRATIONS` (as tasks que removem sítio: 19,
  20, 22, 23, 25, 26, 30) e `PENDING`, uma entrada
  `(task, arquivo, categoria, linha, contagem)` por chave — linhas iguais no
  mesmo arquivo são uma entrada com a contagem. O check novo, item 8 da
  docstring (a frase "Rule (b) lives outside this package and closes in
  phase 4" saiu), é igualdade de multiconjunto nos dois sentidos: sítio além
  da lista é vermelho (**novo**), entrada além do que o audit acha é vermelha
  (**velha**, para a lista encolher no mesmo commit de cada migração), task
  fora de `MIGRATIONS` é vermelha, e o tamanho — a soma das contagens — tem de
  bater com o total do `audit.py`.
- `tools/duckmcp/controls.py`: o sandbox agora leva, ao lado do pacote, todo
  `.py` de `tools/` (o audit da regra (b) precisa da mesma árvore; sem isso
  toda entrada do `PENDING` sairia velha); controle pode plantar só um arquivo
  (`file` None), e é BROKEN se o diretório não existe no sandbox ou o arquivo
  já existe; quatro controles da regra (b); a última linha diz quantos cobrem
  as regras (a) a (d).

**Quem remove cada sítio** (a task da entrada é a remoção planejada, pelo §6):
`pes2/mcp_drive.py` e `pad.py` → 19; `pes2/who_writes.py` e
`pes2/selftest.py` → 20; `looks/oracle.py` → 22, menos as chamadas da família
de breakpoint (`breakpoint`, `continue`, `wait_for_pause`, `read_registers`,
`get_gte_registers`, `vram_watch`, `disassemble`) → 23; `looks/confront.py` →
23; `kits/oracle.py` → 25; `kits/replay.py` e `kits/selftest.py` → 26; todo
`sys.path` → 30, porque ele aponta para `tools/pes2/`, que só deixa de ser a
casa dos módulos quando os shims somem. Nota para as tasks seguintes: a
`kits/replay.py` não é nomeada por nenhuma task de migração — ficou com a 26
porque é ela que replanta `replay-capture-joystick-late`; a task que de fato a
migrar move as duas entradas, dizendo no Log. A divisão 22/23 dentro do
`looks/oracle.py` é previsão: uma task que remover sítio marcado para a outra
encolhe a entrada do mesmo jeito. Para refazer uma entrada depois de editar,
`python3 tools/duckmcp/audit.py --keys` imprime a chave pronta.

**Critério 1 e 4** — o selftest, e o tamanho da lista contra o audit:

```
$ python3 tools/duckmcp/selftest.py | grep 'rule (b)'
  ok    rule (b): no raw site outside PENDING
  ok    rule (b): no stale PENDING entry (listed, no longer found)
  ok    rule (b): every PENDING entry names a migration task
  ok    rule (b): every PENDING count is at least 1
  ok    rule (b): no key appears twice in PENDING
  ok    rule (b): PENDING lists 206 site(s) in 108 entries, audit.py counts 206
$ python3 tools/duckmcp/selftest.py --quiet; echo exit $?
duckmcp_selftest: 434 check(s) ran, 0 failure(s)
exit 0
$ python3 tools/duckmcp/audit.py | tail -1
audit: 206 raw site(s) in 14 file(s)
$ python3 tools/duckmcp/audit.py --keys | tail -1
audit: 206 raw site(s) under 108 key(s)
```

**Critério 3** — `import fork` num arquivo novo de `tools/kit2d/`:

```
$ python3 tools/duckmcp/controls.py --only b-import-fork-kit2d
baseline: the untouched sandbox is green
red    b-import-fork-kit2d (rule b): FAIL  rule (b): no raw site outside PENDING  tools/kit2d/dmcp_probe_b.py: import: import fork # planted (x1)
duckmcp_controls: 1 control(s), 1 red as required; 1/1 cover rules (a) to (d); per rule (b) 1/1
```

Os outros três da regra (b):

```
red    b-client-call-kit2d (rule b): FAIL  rule (b): no raw site outside PENDING  tools/kit2d/dmcp_probe_b.py: client: return client.call("pause") (x1)
red    b-stale-entry (rule b): FAIL  rule (b): no stale PENDING entry (listed, no longer found)  tools/pes2/pad.py: import: from mcp import Client, NotRunning # noqa: E402 (x1)
red    b-unknown-task (rule b): FAIL  rule (b): every PENDING entry names a migration task  ['DMCP-TASK-99']
```

**Critério 2** — a bateria inteira (5 min 39 s):

```
$ python3 tools/duckmcp/controls.py; echo exit $?
duckmcp_controls: 37 control(s), 37 red as required; 18/18 cover rules (a) to (d); per rule (a) 2/2, (b) 4/4, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
exit 0
```

Gates: `ctest --test-dir build -R 'duckmcp_selftest|tasks'` e
`ctest --test-dir build -R kits_selftest` passaram.
- **Closed** — commit `1b3ad31a` (2026-10-23): feat(duckmcp): rule (b) as a selftest gate with a PENDING list
  - Files (`git show --name-status 1b3ad31a`):
    - `M docs/tasks/duckmcp/17-regra-b.md`
    - `M tools/duckmcp/audit.py`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/selftest.py`
