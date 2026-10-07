---
id: KITS-TASK-12
---

# KITS-TASK-12 — Gerador de `generated/` a partir do C++, com `--check` no ctest

## Goal

Os offsets de nome de time (`OFS_TEAM_NAME_*`), os comprimentos e o `TEAM_NAMES[120][20]` saem de `Offsets.hpp`/`Tables.cpp` para `core/generated/` por gerador; o `--check` entra no ctest como o `rc2ui.py`.

## Arquivos a criar ou modificar

- `tools/kits/gen_tables.py`
- `tools/kits/core/generated/`
- `tests/CMakeLists.txt`
- `NOTICE.md`, `docs/prompts/perfil-kits.md` (a seção "Generated artifacts")

## Done criteria

- [x] `python tools/kits/gen_tables.py --check` sai 0 na HEAD
- [x] Controle: um nome de `TEAM_NAMES` alterado numa cópia do `Tables.cpp` faz o `--check` sair diferente de 0 (vermelho no Log)
- [x] `ctest -R kits` lista o alvo do gerador pelo nome
- [x] As linhas de `TEAM_NAMES` que valem para cada time foram conferidas no `legacy/mfc/edDlg.cpp` e a referência (arquivo:linha) está no Log
- [x] A seção do `kits` no `NOTICE.md` ganha, no mesmo commit, a linha da tabela `TEAM_NAMES` (Francesco Moriero, `legacy/mfc/`, sem licença)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.3).

O que o gerador copia, e de onde (`tools/kits/gen_tables.py`, saída em `tools/kits/core/generated/team_names.py`):

- de `src/core/include/we2002/Offsets.hpp`: os 17 offsets de nome de time — `OFS_TEAM_NAME_*` (com os `_A`/`_B`/`_END` dos saltos de setor), `OFS_TEAM_NAME_KANJI*`, `OFS_TEAM_MIXED_CASE_NAME`, `OFS_ML_TEAM_NAME_*`;
- de `src/core/include/we2002/Types.hpp`: `TEAMS_NATIONAL` (54), `TEAMS_ALLSTAR` (9), `TEAMS_ML` (32);
- de `src/core/Tables.cpp`: as dez tabelas de comprimento (`TEAM_NAME_LEN_1..6`, `TEAM_NAME_KANJI_LEN`, `TEAM_MIXED_CASE_NAME_LEN`, `ML_TEAM_NAME_LEN_7/8`) e o `TEAM_NAMES[120][20]`. O `PICKER_TEAM_NAMES` fica de fora: é a grafia do diálogo de escolha de jogador, não do combobox de times.

Ele lê o C++ que o port compila, não o `legacy/` — o C++ já é gerado do `edDlg.cpp` pelo `extract_legacy_data.py`, e ler o mesmo arquivo que o `we2002_core` impede o Python de divergir dele. Os saltos de setor (`i == 40`, `i == 57`, …) do `Database::Load` são lógica, não constante, e não entram no gerador: são da KITS-TASK-13, que lê os nomes.

**Quais linhas do `TEAM_NAMES` valem para qual time**, conferido no legado:

- `legacy/mfc/edDlg.cpp:170-172` — `#define SQUADRE_NAZ 54`, `SQUADRE_ALLS 9`, `SQUADRE_ML 32`;
- `legacy/mfc/edDlg.cpp:411` — `char nomi_squadre[120][20]` (o `TEAM_NAMES`; o mapa está em `tools/extract_legacy_data.py:175`);
- `legacy/mfc/edDlg.cpp:1341-1368` — o combobox de times: `nomi_squadre[i]` para as seleções (`:1348`, "Nation 1..54"), `nomi_squadre[i+54]` para as all-star (`:1357`) e `nomi_squadre[i+63]` para os clubes da ML (`:1366`).

Então o índice de time `t` em 0..94 é a linha `t` da tabela — seleções 0..53, all-star 54..62, ML 63..94 — e as **linhas 95..119 não são usadas** pelo combobox (o legado as marca a partir de `"Island", //95`). O port faz o mesmo em `src/app/MainWindow.cpp:354-364`. O `team_names.py` diz isso no comentário da tabela.

## Log de Execução

### 2026-10-01

```
$ python tools/kits/gen_tables.py
gen_tables: wrote tools\kits\core\generated\team_names.py
$ python tools/kits/gen_tables.py --check; echo exit=$?
gen_tables: tools\kits\core\generated\team_names.py is up to date
exit=0
```

O controle, numa cópia dos três fontes C++ (`--negative`):

```
$ python tools/kits/gen_tables.py --negative; echo exit=$?
control: TEAM_NAMES row 1 'Scotland' -> 'ScotlandX' in a copy of src/core/Tables.cpp
gen_tables: tools\kits\core\generated\team_names.py is stale -- rerun python tools/kits/gen_tables.py
  --- committed
  +++ regenerated
  @@ -121,3 +121,3 @@
   TEAM_NAMES = (
  -    'Ireland', 'Scotland', 'Wales', 'England',
  +    'Ireland', 'ScotlandX', 'Wales', 'England',
       'Portugal', 'Spain', 'France', 'Belgium',
control: --check --src <copy> exit 1, 1 generated line(s) differ -- red, held
exit=0
```

(Antes de virar opção, a primeira tentativa foi um `sed` sobre `"Scotland",` numa cópia, que trocou **três** linhas — o `TEAM_NAMES`, o `PICKER_TEAM_NAMES` e uma terceira. O `--negative` troca só a linha do `TEAM_NAMES`, achada depois do `{` dele.)

O alvo no `ctest` (build fora da árvore, `%TEMP%/build-kits08`):

```
$ ctest -N -R kits
  Test #14: kits_selftest
  Test #15: kits_image
  Test #16: kits_gen
Total Tests: 3
$ ctest -R kits_gen
1/1 Test #16: kits_gen .........................   Passed    0.10 sec
```

O que a tabela gerada dá nos limites das três faixas:

```
$ python -c "import sys;sys.path.insert(0,'tools/kits');from core.generated import team_names as t;print(len(t.TEAM_NAMES), t.TEAM_NAMES[53], t.TEAM_NAMES[54], t.TEAM_NAMES[62], t.TEAM_NAMES[63], t.TEAM_NAMES[94])"
120 Australia Euro All Stars Clas. Argentina Manchester U. Basilea
```
- **Closed** — commit `a700d248` (2026-10-01): feat(kits): generate the team-name constants from the C++ core, with --check in ctest
  - Files (`git show --name-status a700d248`):
    - `M NOTICE.md`
    - `M docs/prompts/perfil-kits.md`
    - `M docs/tasks/kits/12-gerador-de-nomes.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tests/CMakeLists.txt`
    - `A tools/kits/core/generated/__init__.py`
    - `A tools/kits/core/generated/team_names.py`
    - `A tools/kits/gen_tables.py`
- **Reviewed** (2026-10-01) at `7db6d0bc`: no finding
