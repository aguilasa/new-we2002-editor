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

Varredura (refeita pela [CORR-K3D-001](/docs/tasks/kits-3d/CORR-K3D-001.md)): nenhum
rótulo do seletor 3D diz mais "Set"/"Conjunto"/"titular"/"suplente". O que sobra na
árvore, e por que fica:

```text
$ grep -rlI -i 'titular\|suplente' tools docs --include='*.py' --include='*.md' | grep -v 'concluidos\|kits-3d\|tasks/pes2' | sort
docs/biblia-we2002/07-times.md
docs/biblia-we2002/08-uniformes.md
docs/KITS-AJUSTES-3D.md
docs/KITS-INICIAR-CICLO.md
docs/PARIDADE-FUNCIONAL.md
docs/PLAN-KIT2D-PY.md
docs/PLAN-KITS-PY.md
docs/prompts/perfil-kits.md
docs/SUPERPACK-UNIFORMES.md
```

- `PLAN-KITS-PY.md`, a seção "Hoje" do `KITS-AJUSTES-3D.md`, `KITS-INICIAR-CICLO.md`
  e `perfil-kits.md` são registro do ciclo `kits`, escritos antes deste.
- `SUPERPACK-UNIFORMES.md` descreve o formato do `TEX_*.BIN` e o vocabulário do WETex
  (Titular/Suplente); `biblia-we2002/08-uniformes.md` transcreve o tutorial da
  comunidade. São nomes de terceiro, não rótulo nosso.
- `PLAN-KIT2D-PY.md` é o plano de outro projeto (o 2D), com vocabulário próprio.
- `biblia-we2002/07-times.md` e `PARIDADE-FUNCIONAL.md` dizem "titulares" no sentido
  de onze iniciais, não de uniforme.
- `tools/kits/ui/i18n.py:112-113` — `work_set_1`/`work_set_2` ("1º/2º conjunto",
  "1st/2nd set") rotulam a lista de **bitmaps de trabalho**, fora do G1, que só fala
  do seletor 3D. Trocá-los por Casa/Visitante seria task nova.
- Docstrings e mensagens de formato em `tools/kits` ("set 1", "first set") falam do
  registro do TEX, não do rótulo, e ficam.

O "conjunto" no resto de `docs/` (`subconjunto`, "conjunto de cópias" do PES2) é
outra palavra, e a varredura ampla da CORR o mostra junto.

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
- **Reviewed** (2026-10-07) at `50341a4`: CORR-K3D-001
