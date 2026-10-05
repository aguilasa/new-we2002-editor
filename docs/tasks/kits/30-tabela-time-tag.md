---
id: KITS-TASK-30
---

# KITS-TASK-30 — §4.2: qual TEX cada time veste

## Goal

A tabela índice de time → tag, medida (editor do Obocaman em `we-team-editor/`, e/ou o emulador pelo `--kit`), versionada como dado com proveniência.

## Arquivos a criar ou modificar

- `tools/kits/core/generated/`
- `tools/kits/gen_tables.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] A tabela cobre N times, número da ferramenta, e cada linha diz de onde veio
- [x] Pelo menos três linhas conferidas no emulador, comando e saída no Log
- [x] A §4.2 do plano tem veredito
- [x] A seção do `kits` no `NOTICE.md` credita, no mesmo commit, de onde a tabela veio: Obocaman (`we-team-editor.exe`, sem licença; dado medido, não código) e Wetigre, se a ordem de cabeça do WE2000 for usada

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.2). Nada do `we-team-editor.exe` entra no git; só o dado medido.

Duas linhas já medidas no emulador pela KITS-TASK-27 (§4.1), pela bandeira e pela paleta na VRAM: **Escócia → `TEX_01`**, **Dinamarca → `TEX_13`** (`python3 tools/kits/oracle.py --slot 3`, state em `work/kits-states/SLPM-87056_3.sav`). Contam para as "três conferidas no emulador" do perfil.

## Log de Execução

### 2026-10-04

**De onde a tabela veio.** O `we-team-editor.exe` acha o TEX de um time numa
conta, não numa tabela: no diálogo de textura ele lê o `ItemIndex` do combobox
de times e calcula `n = índice + 9 × (índice div 95)` e o byte
`0x12D7718 + n × 47040` — o primeiro byte de dados do `TEX_00` (LBA 8400) mais
`n` passos de 20 setores. `iso.py ls` confirma o passo até o fim: `TEX_94` em
LBA 10280, `TEX_A4` em 10480 (= 8400 + 20 × 104). O combobox tem 95 times e um
96º item, `95 Master L.` / `95 Default ML` (são três combos de 96 itens no
`.dfm`), que a conta manda para `n = 104`, o `TEX_A4`. A regra vira dado em
`gen_tables.py` (`EDITOR_RULE`), e `--editor` a relê das instruções do exe:

```
$ python3 tools/kits/gen_tables.py --editor
gen_tables --editor: 2 site(s) at 0xd451, 0xe5db give {'divisor': 95, 'skip': 9, 'base': 19756824, 'stride': 47040}
gen_tables --editor: the exe computes EDITOR_RULE
$ python3 tools/kits/gen_tables.py --negative-editor
control: divisor + 1 at 2 site(s) of a copy
gen_tables --editor: FAIL -- EDITOR_RULE says {'divisor': 95, 'skip': 9, 'base': 19756824, 'stride': 47040}
control: --editor <copy> exit 1 -- red, held
```

O exe não entra no git; sem ele o `--editor` sai 77.

**Critério 1** — `python3 tools/kits/gen_tables.py --report`:

```
team_kits: 95 teams with a TEX, from the editor's rule; 4 of them confirmed in the game (0 -> TEX_00, 1 -> TEX_01, 13 -> TEX_13, 41 -> TEX_41); the editor's ML default item -> TEX_A4; 9 tags no item reaches (95 96 97 98 99 A0 A1 A2 A3)
```

Cada linha diz de onde veio: todas da regra do editor (cabeçalho do
`generated/team_kits.py`), e as quatro conferidas no jogo têm o comando e o
state em `TEAM_KIT_EMULATOR`. O gerador recusa uma linha medida que a regra
contradiga — plantada `(2, '05')` em `EMULATOR_ROWS`: `red: the rule gives team
2 TEX_02, and the game wore TEX_05 (planted)`. O `--check` cobre os dois
arquivos gerados (`team_kits.py is up to date`), e com `'41'` trocado por
`'14'` no arquivo commitado: `team_kits.py is stale`.

**Critério 2** — a terceira conferência no emulador é uma partida nova,
dirigida pelo MCP a partir do slot 3: pausa → `EXIT MATCH` → `MATCH` →
`EXHIBITION` → Irlanda (casa) × Brasil (fora), primeiro uniforme os dois, e o
state gravado no slot 4 já com a bola rolando (cópia mestra
`work/kits-states/SLPM-87056_4.sav`, sha256 `40bcf3d630c673eb…`).
`python3 tools/kits/oracle.py --slot 4 --cue $PWD/work/we2002-english.cue --out work/kits-oracle/match-4 --flags --expect 00=1 --expect 41=1`, exit 0:

```
  control: two dumps a frame apart give the same 10 match(es)
  TEX_00  record  2 player palette     set 1  at (0,486), (0,490)
  TEX_00  record  8 flag               set -  at (704,256)
  TEX_41  record  2 player palette     set 1  at (0,487), (0,491)
  TEX_41  record  8 flag               set -  at (704,320)
  TEX_00 uniform  at (576,256): set 1 differs in 2640 of 8192 halfwords, set 2 in 7056 -- set 1 nearer
  TEX_41 uniform  at (640,256): set 1 differs in 4793 of 8192 halfwords, set 2 in 5050 -- set 1 nearer
  TEX_00 flag, black left out: (165, 123, 41) 21 %, (222, 222, 222) 19 %, (16, 99, 49) 15 %
  TEX_41 flag, black left out: (16, 99, 66) 28 %, (16, 90, 66) 10 %, (173, 156, 41) 7 %
  ok    TEX_00 in set 1, TEX_41 in set 1
```

A bandeira laranja, branca e verde é a da Irlanda; a verde e amarela, a do
Brasil. O `TEX_61` também aparece, só pela bandeira e pela paleta dela: é o
Brasil clássico (time 61), que divide a bandeira com o 41; as páginas e a paleta
de jogador dele não estão lá. Com as duas da task 27 (Escócia → `TEX_01`,
Dinamarca → `TEX_13`, slot 3) são quatro linhas conferidas, as quatro na regra.

De passagem, sem pergunta que dependa disso: o goleiro do Brasil, time de fora,
veste a paleta de goleiro do **conjunto 2** (`TEX_41 record 7`), e o da Irlanda,
de casa, a do 1. Na partida da task 27 era o goleiro da Escócia, de casa, que
vestia o 2. Então a escolha do goleiro não é "o de fora usa o 2" nem "o de casa
usa o 2" — fica registrado, sem regra.

**Critério 3** — veredito na §4.2 do plano: índice `i` → `TEX_i` para 0 a 94,
item 95 do editor → `TEX_A4`, nove tags sem dono. A ordem do WE2000 (Wetigre)
não vale aqui: ela põe a Irlanda do Norte no `01`, e o jogo mostrou a Escócia.

**Critério 4** — linha do Obocaman na seção do `kits` do `NOTICE.md`, neste
commit: dado (a regra, três números), não código; o exe não entra no git. O
Wetigre não foi usado, então não ganha linha.
- **Closed** — commit `aefc8ae` (2026-10-04): feat(kits): team -> TEX table from Obocaman's editor rule
  - Files (`git show --name-status aefc8ae`):
    - `M NOTICE.md`
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/prompts/perfil-kits.md`
    - `M docs/tasks/kits/30-tabela-time-tag.md`
    - `M docs/tasks/kits/31-combobox-de-times.md`
    - `A tools/kits/core/generated/team_kits.py`
    - `M tools/kits/gen_tables.py`
