---
id: CORR-KRP-010
---

# CORR-KRP-010 — confront --tab só guarda game_side; a escolha de buffer em game_pixels não tem asserção nem controle

Origin: [KRP-TASK-06](/docs/tasks/concluidos/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md)

## Problem

O pareamento frente/costas é decidido em dois lugares: `game_side` escolhe a captura, e
`game_pixels` escolhe, dentro dela, `"buffer"` ou `"back_buffer"`. A única asserção nova
(`selftest.py:1611`) compara `game_side` nos focos constantes 0 e 3 contra uma cópia da própria
tabela. Nada testa `game_pixels`, `confront_tab` nem `back_buffer`.

Com `game_pixels` plantado para ler sempre o buffer da primeira captura:

- a corrida sai 0;
- o JSON continua rotulando o lado da frente como `game_capture: "back"`;
- a interseção cai em silêncio de 0,439 para 0,317;
- a asserção do selftest continua `True`.

É a lacuna da CORR-K3D-034 voltando com todo gate verde. A K2 da §9 do
[PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#9) pede "uma planta que a derruba com dado real".

## Evidência

```text
$ grep -rn "confront_tab\|game_pixels\|back_buffer\|tab_args\|game_side" tools/ tests/ | grep -v "^tools/kits/replay.py"
tools/kits/controls.py:622:        "replay-tab-sides-crossed", "kits/replay.py", "game_side",
tools/kits/selftest.py:1611:    pairs = {(focus, side): cli.game_side(side, focus) for focus in (0, 3)
$ S=$(mktemp -d); git archive HEAD tools | tar -x -C "$S"; python3 - "$S" <<'PY'
import sys; p = sys.argv[1] + '/tools/kits/replay.py'; s = open(p).read()
old = 'buffer = capture.data.get("buffer" if which == "front" else "back_buffer")'
assert s.count(old) == 1
open(p, 'w').write(s.replace(old, 'buffer = capture.data.get("buffer")'))
PY
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 "$S/tools/kits/replay.py" confront work/kits-replay/tab/replay-9-3-R1.json --tab --json --out "$S/tab"
exit 0; sides: back<-front 3520 px 0.4064, front<-back 3200 px 0.3174   (HEAD: front<-back 0.439)
$ cd "$S/tools/kits" && python3 -c "import replay as cli; print({(f,s): cli.game_side(s,f) for f in (0,3) for s in cli.TAB_SIDES} == {(0,'front'):'front',(0,'back'):'back',(3,'front'):'back',(3,'back'):'front'})"
True
```

## Root cause

(Hipótese.) A asserção foi escrita contra o helper puro porque `confront_tab` lança o `app.py`. A
metade do pareamento que vai da captura ao buffer (`game_pixels`) nunca foi exercitada.

## Fix

- Em `tools/kits/selftest.py`, chamar `game_pixels` sobre uma captura sintética cujos `buffer` e
  `back_buffer` tenham cores diferentes, e conferir que cada `which` lê o próprio buffer.
- Em `tools/kits/controls.py`, um controle `replay-tab-buffer-crossed` que plante a linha acima.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`

## Verificação

```sh
python3 tools/kits/controls.py --only replay-tab-buffer-crossed
```

Hoje falha com escolha desconhecida. Depois do conserto tem de imprimir `RED`.

## Log de Execução

### 2026-10-15

**Reprodução na HEAD** (antes do conserto, um shell só): plantar
`buffer = capture.data.get("buffer")` em `game_pixels` deixa a asserção de `game_side` do selftest
em `True`, e o controle pedido não existia — o argparse o recusava como escolha desconhecida
(lista de escolhas cortada aqui):

```text
$ python3 tools/kits/controls.py --only replay-tab-buffer-crossed
controls.py: error: argument --only: invalid choice: 'replay-tab-buffer-crossed' (choose from …)
```

**Conserto.**

- `tools/kits/selftest.py`, em `_replay_reader_checks`, logo depois da asserção de `game_side`:
  monta a captura sintética de `_replay_reader_capture` com as duas poses e dois buffers sob a
  mesma figura, `buffer` em (1, 2, 3) e `back_buffer` em (4, 5, 6), e chama `game_pixels` com
  cada `which` de `TAB_SIDES`. A asserção nova (`confront --tab reads the first capture's buffer,
  and the second's back_buffer`) exige `front` → `[(8, 16, 24)]` e `back` → `[(32, 40, 48)]`.
- `tools/kits/controls.py`: controle `replay-tab-buffer-crossed`, que planta exatamente a linha
  da evidência (`buffer = capture.data.get("buffer")`) em `game_pixels`.

**Verificação.**

```text
$ python3 tools/kits/controls.py --only replay-tab-buffer-crossed
  base   unplanted sandbox            selftest exit 0
  RED    replay-tab-buffer-crossed    kits/replay.py :: game_pixels
controls: 1 of 1 red
$ python3 tools/kits/selftest.py | grep back_buffer
  ok    confront --tab reads the first capture's buffer, and the second's back_buffer
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
$ python3 tools/kits/controls.py | tail -1
controls: 70 of 70 red
```

A HEAD tinha 69 entradas em `CONTROLS` (`git show HEAD:tools/kits/controls.py | grep -c
"^    Control("` → 69); com esta, 70.

**Não rodado:** a corrida `replay.py confront … --tab` da evidência precisa do `:98` e de
`work/kits-replay/tab/`, e ficou fora deste item por instrução; a asserção nova mede o mesmo
cruzamento sobre captura sintética, sem janela.
- **Closed** — commit `73cc5cac` (2026-10-15): test(kits): assert game_pixels reads each capture's own buffer, with a planted control
  - Files (`git show --name-status 73cc5cac`):
    - `M docs/tasks/kits-replay/CORR-KRP-010.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
