---
id: KITS-TASK-13
---

# KITS-TASK-13 — `teams.py` e `cli.py teams`: nome da ROM ou tabela inglesa, decidido pelo disco

## Goal

`source.teams()` devolve `TeamEntry(index, name, name_origin, tag)`; o disco japonês (boot `SLPM_870.56`) dá nomes da tabela, os outros dão o nome da ROM, disco desconhecido cai no nome da ROM com `name_origin` dizendo isso.

## Arquivos a criar ou modificar

- `tools/kits/core/teams.py`
- `tools/kits/core/source.py`
- `tools/kits/core/api.py`
- `tools/kits/cli.py`
- `tests/golden_tool.cpp` — o verbo `names`, que imprime os nomes como o `Database::Load` os leu; é o outro lado da conferência

## Done criteria

- [x] `cli.py teams roms/japanese-shift-jis.bin` sai com `name_origin` `table` em todas as linhas; primeiras linhas coladas
- [x] `cli.py teams roms/golden-european-deluxe.bin` sai com `rom`, e os nomes batem com os que o `we2002_core` lê (comando de conferência e contagem no Log)
- [x] Nenhum nome vazio na japonesa (contagem da ferramenta)
- [x] `tag` é `None` em toda linha enquanto a §4.2 não fechar

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.3).

O que ficou decidido, medido antes:

- **"Japonês" é o digest do executável de boot, não o nome dele.** Os três discos de `roms/` bootam `/SLPM_870.56` (o `SYSTEM.CNF` dos três diz `BOOT = cdrom:SLPM_870.56;1`); o arquivo tem 337.920 bytes nos três, e o sha256 é `7da7745d…` só no japonês (`52f5e0da…` na European Deluxe, `76a47d64…` na PT-BR). O digest japonês já morava no `layout.py` do `looks` (`layout.BOOT`, `layout.expected_digest`), e é de lá que o `teams.is_japanese` lê — endereço e digest num lugar só.
- **O nome da ROM é o `mixed_case_name`** ("Inter", não o "INTER" de `names[0]`), lido onde o `Database::Load` o lê: `OFS_TEAM_MIXED_CASE_NAME`, os 32 clubes de trás para frente, depois os 63 de trás para frente, cada um `TEAM_MIXED_CASE_NAME_LEN[i]` bytes e cortado no primeiro NUL. Offsets e comprimentos vêm do `generated/team_names.py` (KITS-TASK-12).
- **Por que a tabela no japonês:** lá o `mixed_case_name` é katakana de meia largura em todo time, e o clube 63 vem vazio nos dois campos — `we2002_golden_tool names roms/japanese-shift-jis.bin` mostra `63` seguido de dois campos vazios.
- **Disco desconhecido cai no nome da ROM**, e o `name_origin == "rom"` diz isso: a PT-BR, que também boota `SLPM_870.56`, sai `95 rom` com "Irlanda", "Escocia".
- O `golden_tool names` precisou de um conserto antes de servir: `db.teams` tem 64 posições (`TEAMS_NATIONAL_ALLSTAR_SLOTS`, a vaga a mais do array), e a primeira versão imprimia as 64 — 96 linhas, e os 32 clubes saíam deslocados de um (`63 of 95 ROM names equal`, com `DIFFER 93: 'Kiev' here, 'Galatasaray' in we2002_core`). Ele imprime só os 63 que o editor lista.
- O `golden_tool` roda pelo PowerShell; pelo Git Bash o mesmo `.exe` sai 127 sem imprimir nada.

## Log de Execução

### 2026-10-01

O japonês:

```
$ python tools/kits/cli.py teams roms/japanese-shift-jis.bin      # exit 0
  0  national table Ireland
  1  national table Scotland
  2  national table Wales
  3  national table England
  4  national table Portugal
  5  national table Spain
...
95 teams: 95 table; 0 empty name(s); 0 with a kit tag
```

A European Deluxe contra o `we2002_core` (`we2002_golden_tool` compilado em `%TEMP%/build-kits08`):

```
PS> & $env:TEMP\build-kits08\tests\we2002_golden_tool.exe names roms\golden-european-deluxe.bin > $env:TEMP\core_names_eu.tsv   # 95 linhas
$ python tools/kits/cli.py teams --against $TEMP/core_names_eu.tsv roms/golden-european-deluxe.bin      # exit 0
  0  national rom   Inter
  1  national rom   Juventus
  2  national rom   Milan
...
95 teams: 95 rom; 0 empty name(s); 0 with a kit tag
against we2002_core: 95 of 95 ROM names equal (95 lines in core_names_eu.tsv)
```

O controle da conferência — um nome trocado numa cópia do dump:

```
$ sed 's/^1\tJuventus\t/1\tJuventuz\t/' core_names_eu.tsv > core_names_eu_planted.tsv
$ python tools/kits/cli.py teams --against $TEMP/core_names_eu_planted.tsv roms/golden-european-deluxe.bin | tail -2      # exit 1
  DIFFER   1: 'Juventus' here, 'Juventuz' in we2002_core
against we2002_core: 94 of 95 ROM names equal (95 lines in core_names_eu_planted.tsv)
```

O controle da decisão pelo disco — a PT-BR boota o mesmo arquivo, com outro digest — e a mesma imagem aberta pela folha `.cue`:

```
$ python tools/kits/cli.py teams roms/ptbr-remaster.bin | sed -n '1,2p;$p'
  0  national rom   Irlanda
  1  national rom   Escocia
95 teams: 95 rom; 0 empty name(s); 0 with a kit tag
$ python tools/kits/cli.py teams roms/golden-european-deluxe.cue | tail -1
95 teams: 95 rom; 0 empty name(s); 0 with a kit tag
```

`kits_selftest` (a regra da fachada sobre o `cli.py` e os controles numa cópia que já leva o `teams.py`):

```
$ python tools/kits/selftest.py --quiet | grep -E "FAIL|controls red|kits_selftest:"
  ..... 12 of 12 controls red
kits_selftest: 0 failure(s)
```
