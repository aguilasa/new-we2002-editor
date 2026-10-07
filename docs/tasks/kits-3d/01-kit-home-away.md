---
id: K3D-TASK-01
---

# K3D-TASK-01 — Kit Home/Away na aba e --kit home|away no CLI

## Goal

O seletor "Set" da aba 3D vira **Kit** (pt-BR **Uniforme**) com **Home**/**Away** (**Casa**/**Visitante**), e o CLI ganha `--kit home|away` ao lado de `--set 1|2`, com o mesmo efeito.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/i18n.py`, `tools/kits/ui/app.py`
  - `tools/kits/cli.py`
  - `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`
- Out: trocar `--set` (continua aceito); os Logs e CORRs do ciclo `kits` arquivado

## Done criteria

- [x] `kits_ui` lê nas capturas `Kit` com `Home`/`Away` em en-US e `Uniforme` com `Casa`/`Visitante` em pt-BR; a planta que devolve `set_first` = "first" fica vermelha
- [x] `python3 tools/kits/cli.py figure --kit away <args>` imprime o mesmo `_scene_digest` que `--set 2`, e `--kit home` o de `--set 1` (caso no `selftest.py`, com planta vermelha)
- [x] `cli.py figure --help` diz que 1 é home e 2 é away
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Convenção do futebol, não medição (usuário, 2026-10-07).

**Como o `kits_ui` lê o seletor.** Pelo `app.py --list-3d`, que passou a imprimir
`kit selector: <rótulo>: <item 1> | <item 2>` — o mesmo canal do juiz das caixas de
vestimenta, que já lia o texto dos widgets assim. O esperado (`KIT_WANT`) é escrito
no `ui_check.py`, não lido do catálogo. Não é OCR do PNG.

Evidência (2026-10-07, HEAD de trabalho):

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
  ok    the dressing boxes: ... and the kit selector Kit Home/Away, Uniforme Casa/Visitante, in en-US and pt-BR
        plant 'kit 1 labelled first': figure 0 en-US: the kit selector says 'Kit: first | Away', not 'Kit: Home | Away'; ...
  ok    plant 'kit 1 labelled first' fails the dressing boxes judge
kits_ui: 0 failure(s)

$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image
  ..... cli.py figure TEX_00 figure 0: --kit home ab81491bd0f6, --set 1 ab81491bd0f6, --kit away cdc020a505c8, --set 2 cdc020a505c8
  ok    cli.py figure --kit home draws --set 1's digest and --kit away --set 2's, and the two differ

$ python3 tools/kits/selftest.py --no-plant
  ok    cli.py figure --kit home is --set 1 and --kit away is --set 2
  ok    cli.py figure --help says 1 is home and 2 is away
$ python3 tools/kits/controls.py --only cli-kit-swapped
  RED    cli-kit-swapped              kits/cli.py :: module constant

$ python3 tools/kits/cli.py figure --help
  --set {1,2}           1 the home kit, 2 the away kit (default both;
  --kit {home,away}     home (= --set 1) or away (= --set 2); repeatable, and

$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4

$ python3 tools/kits/controls.py
controls: 29 of 29 red
```

Varredura: "Set"/"Conjunto"/"titular"/"suplente" só sobram em `PLAN-KITS-PY.md` e na
seção "Hoje" do `KITS-AJUSTES-3D.md`, que são registro; docstrings de formato
("first set") no `cli.py` falam do registro do TEX, não do rótulo, e ficam.

## Log de Execução

- **Closed** — commit `5669790` (2026-10-07): feat(kits): name the 3D set selector Kit Home/Away, add figure --kit
  - Files (`git show --name-status 5669790`):
    - `M docs/tasks/kits-3d/01-kit-home-away.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
