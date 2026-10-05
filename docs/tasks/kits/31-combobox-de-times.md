---
id: KITS-TASK-31
---

# KITS-TASK-31 — O combobox passa a listar times, na ordem do jogo

## Goal

`TeamEntry.tag` preenchido; com a tabela, o combobox lista times; tag sem time continua acessível.

## Arquivos a criar ou modificar

- `tools/kits/core/teams.py`
- `tools/kits/ui/*.py`
- `tools/kits/core/api.py` — exporta `kit_order` e as constantes da ordem (a janela só importa a fachada)
- `tools/kits/cli.py` — a coluna da tag no `cli.py teams` (critério 1)
- `tools/kits/selftest.py` — as checagens da ordem do seletor
- `docs/PLAN-KITS-PY.md` — a §3.2 diz que o combobox passou a listar times

## Done criteria

- [x] `cli.py teams` mostra `tag` preenchida em N linhas (N da task 30)
- [x] Captura da janela com o combobox de times
- [x] `kits_ui` verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.2).

Da KITS-TASK-30: a tabela é `tools/kits/core/generated/team_kits.py` (`TEAM_KIT`, um tag por índice de time 0 a 94; `ML_DEFAULT_KIT` = `A4`; `UNREACHED_KITS` = `95`..`A3`, que nenhum time veste e continuam acessíveis por tag). O N é **95**, dito por `python tools/kits/gen_tables.py --report`. `core/teams.py` a lê de `generated/`, como já lê `team_names.py`.

## Log de Execução

### 2026-10-04

`TeamEntry.tag` vem de `generated/team_kits.py` (`core/teams.py`); a ordem do
seletor é `api.kit_order(teams, tags)`: os times na ordem do jogo, o padrão da
Master League (`ML_DEFAULT_KIT`), as tags sem time em ordem de disco, cada tag
uma vez só. A janela só rotula: duas chaves novas no catálogo, nas duas línguas
(`kit_team`, `kit_ml_default`), e a `kit_tag_teams`, que ninguém mais usa, saiu.

**Critério 1** — `python3 tools/kits/cli.py teams roms/japanese-shift-jis.bin`:

```
  0  national table TEX_00  Ireland
  1  national table TEX_01  Scotland
 41  national table TEX_41  Brazil
95 teams: 95 table; 0 empty name(s); 95 with a kit tag
```

Na European Deluxe: `95 teams: 95 rom; 0 empty name(s); 95 with a kit tag`.
N = 95, o da KITS-TASK-30.

**Critério 2** — a janela no `:98` (`work/venv-looks/bin/python
tools/kits/ui/app.py roms/japanese-shift-jis.bin --visible`), o combo aberto
por clique e capturado com `import -window root`:
`work/kits-combo-teams-top.png` (do "Ireland — TEX_00" ao "Chile — TEX_43",
sha256 `461f0cbede9cf201…`) e, com `End`, `work/kits-combo-teams-end.png`
(do "Clas. Brazil — TEX_61" ao "Basilea — TEX_94", depois "Master League
default — TEX_A4" e `TEX_95` … `TEX_A3`; sha256 `9dbc0595bf0ff484…`). Fechado,
o combo mostra "Ireland — TEX_00" e o plano verde da Irlanda.

**Critério 3** — `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:

```
4/4 Test #21: kits_ui ..........................   Passed   25.77 sec
100% tests passed, 0 tests failed out of 4
```

Gate novo no `kits_selftest`, três checagens da ordem (toda tag uma vez; os 95
times primeiro e depois o `A4`; time sem tag no disco fica de fora). Vermelho
visto: com o filtro das tags já listadas tirado do `kit_order`, `FAIL kit_order
lists every tag of the disc once  201 items` e `FAIL kit_order leaves a team
whose tag is not on the disc out`, `kits_selftest: 5 failure(s)`; restaurado,
`kits_selftest: 0 failure(s)`.
- **Closed** — commit `6484655` (2026-10-04): feat(kits): the kit selector lists teams in game order
  - Files (`git show --name-status 6484655`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/31-combobox-de-times.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/teams.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
- **Reviewed** (2026-10-04) at `1e827ec`: CORR-KITS-056, CORR-KITS-057, CORR-KITS-058
