---
id: CORR-KRP-024
---

# CORR-KRP-024 — head_judge não pega painel de cabeça largo demais, e o exit 2 de --player-looks inválido não tem gate

Origin: [KRP-TASK-22](/docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md)

## Problem

A §3.3 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#3.3) diz que a largura é reajustada "para
o rótulo mais longo não cortar nem o painel sobrar". O `head_judge` afirma só duas coisas: que nenhum
rótulo é mais estreito que o próprio texto, e que as larguras das duas línguas diferem. Um painel
ajustado mais largo que o necessário nas duas línguas passa.

O commit também acrescenta a recusa de um `--player-looks` inválido (frase no stderr, exit 2), e
nenhum gate a confere. Medido: `--player-looks X-Y` dá "--player-looks: 'X-Y' is not a looks tuple
like A-A1-A-A-A: …", com exit 2.

## Evidência

```text
$ grep -n "did not refit\|width < needs" tools/kits/ui_check.py
1101:                if width < needs:
1107:        bad.append("the head panel is %d px in both languages: the switch did not refit it"
$ grep -n "player-looks" tools/kits/ui_check.py tools/kits/selftest.py
```

O último `grep` acha 5 ocorrências, e nenhuma é caso de tupla inválida.

## Root cause

O juiz cobre a redação do critério de pronto ("muda a largura … nenhum rótulo corta"), mas não o "nem
o painel sobrar" do plano. O caminho do exit 2 entrou sem sonda.

## Fix

- No `head_judge` de `tools/kits/ui_check.py`, afirmar que a largura do painel é igual à largura
  ajustada. Por exemplo: imprimir o `sizeHint` ao lado de `width` na linha de painel de cabeça do
  `--list-combos` em `tools/kits/ui/app.py`, e exigir igualdade.
- Plantar algo como `setFixedWidth(self.head_panel.sizeHint().width() + 60)` e vê-lo vermelho.
- Acrescentar uma corrida com `--player-looks` inválido que exija exit 2 e a frase.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tools/kits/ui/app.py`

## Verificação

```sh
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep "head panel width oversized"
```

Hoje esse plant não existe. Depois do conserto tem de aparecer
`ok    plant 'head panel width oversized' fails the head panel judge`.

## Log de Execução

**Reprodução, na HEAD `107cd1ff`, antes de qualquer edição.** O juiz só conhece `width < needs` e a
diferença entre as duas línguas, e nenhum `grep` acha caso de tupla inválida:

```text
$ grep -n "did not refit\|width < needs" tools/kits/ui_check.py
1101:                if width < needs:
1107:        bad.append("the head panel is %d px in both languages: the switch did not refit it"
$ grep -n "player-looks" tools/kits/ui_check.py tools/kits/selftest.py
tools/kits/ui_check.py:1013:    """(failures, what was seen): `--player-looks` changes the 3D view against
tools/kits/ui_check.py:1021:                                + (["--player-looks", looks_tuple] if looks_tuple else []),
tools/kits/ui_check.py:1050:"""A tuple --player-looks puts on the combos, and what two of them then show."""
tools/kits/ui_check.py:1056:    of HEAD_WANT set by --player-looks; and after each live switch every label
tools/kits/ui_check.py:1062:            args += ["--player-looks", HEAD_LOOKS[0]] if ticked else []
tools/kits/ui_check.py:1087:                                             "--player-looks", HEAD_LOOKS[0],
```

O caso inválido, medido com o mínimo de argumentos — a imagem e a tupla; a recusa sai antes de
qualquer janela:

```text
$ DISPLAY=:98 XAUTHORITY= timeout 60 work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --player-looks X-Y; echo "exit $?"
--player-looks: 'X-Y' is not a looks tuple like A-A1-A-A-A: 'X-Y' has 2 part(s) and a tuple has 5: skin_colour, hair_style, hair_colour, beard_style, beard_colour, and optionally boots
exit 2
```

**Conserto.**

- `tools/kits/ui/app.py`: a linha `head panel:` do `--list-combos` passa a trazer, ao lado de
  `width`, o `fits` — o `sizeHint().width()` do painel, a largura que o conteúdo pede. É o mesmo
  número que o `fit_head_panel` fixa, então painel ajustado dá os dois iguais:

  ```text
  $ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 14 --tab 3d --lang en-US --switch-to pt-BR --player-looks A-L3-H-A-A --list-combos | grep "head panel"
    head panel: shown True, width 172, fits 172
  $ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 14 --tab 3d --lang pt-BR --switch-to en-US --player-looks A-L3-H-A-A --list-combos | grep "head panel"
    head panel: shown True, width 148, fits 148
  ```

- `tools/kits/ui_check.py`, no `head_judge`: depois de cada troca de língua, nas duas direções, exige
  `width == fits` — o "nem o painel sobrar" da §3.3, que o `width < needs` dos rótulos não cobria. E
  uma corrida nova com `--player-looks X-Y` (`HEAD_BAD_LOOKS`) que exige exit 2 e o começo da frase.
  Essa corrida leva `--list-3d`, para que uma janela que aceite a tupla saia na hora em vez de
  esperar o `TIMEOUT` de 180 s na tela.
- Dois plants novos no juiz do painel de cabeça: `head panel width oversized` (o `setFixedWidth` do
  `fit_head_panel` com `+ 60`) e `invalid player looks accepted` (o `return 2` da recusa trocado por
  `pass`).

**Sonda** usada para ver o juiz e os quatro plants dele antes da corrida inteira — o corpo, em
`probe024.py` no scratchpad, não versionado:

```python
import os, sys, tempfile
sys.path.insert(0, "tools/kits")
import ui_check as u
python = os.path.abspath("work/venv-looks/bin/python")
image = os.path.abspath("roms/japanese-shift-jis.bin")
env = u.environment()
bad, seen = u.head_judge(python, image, env)
print("real:", bad or "pass", "|", seen)
for name, judge, old, new, *target in u.PLANTS:
    if judge != u.HEAD:
        continue
    with tempfile.TemporaryDirectory(prefix="kits-ui-plant-") as box:
        app = u.sandbox(box, old, new, *target)
        red = u.head_judge(python, image, env, app)[0]
        print("plant %r:" % name, "; ".join(red)[:300] or "judge passed")
```

A mesma informação sai da corrida inteira do `ui_check.py`, que é a que conta:

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
  ok    the head panel: no text field on the 3D tab, hidden unticked and shown ticked with the five combos and their labels in en-US and pt-BR, and refitted on a live switch (--player-looks X-Y exit 2, panel width after the switch en-US 148, pt-BR 172)
…
        plant 'head panel width oversized': en-US to pt-BR: the head panel is 232 px and its contents need 172; pt-BR to en-US: the head panel is 208 px and its contents need 148
  ok    plant 'head panel width oversized' fails the head panel judge
        plant 'invalid player looks accepted': --player-looks X-Y: exit 0, ' combo width 40, 7 items, current A\n  head beard_colour: Beard Color, label width 71, combo width 40, 7 items, current A\n  figure selector: Figure: player | goalkeeper\n  kit selector: Kit: Home | Away', not exit 2 with "--player-looks: 'X-Y' is not a looks tuple like 
  ok    plant 'invalid player looks accepted' fails the head panel judge
…
kits_ui: 0 failure(s)
```

O plant antigo `head panel width fixed` agora fica vermelho também pela igualdade nova (`the head
panel is 148 px and its contents need 172`), além dos rótulos cortados que já o pegavam.
- **Closed** — commit `b271c87f` (2026-10-16): test(kits): head panel judge requires the fitted width and gates the invalid --player-looks refusal
  - Files (`git show --name-status b271c87f`):
    - `M docs/tasks/kits-replay/CORR-KRP-024.md`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui_check.py`
