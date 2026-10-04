---
id: CORR-KITS-045
---

# CORR-KITS-045 — Consertar o TypeError de formatação no ramo "Plan mudou" do off_judge

Origin: [KITS-TASK-25](/docs/tasks/kits/25-aba-3d.md)

## Problem

Em `tools/kits/ui_check.py:488-489`, o `off_judge` monta a mensagem como `"... %d ... %dx%d ... row %d ..." % (len(above),) + box`. `%` liga mais forte que `+`, então a string de quatro marcadores recebe um argumento só. Quando a aba Plano muda fora do rótulo da aba — exatamente o caso que esse juiz existe para pegar — ele levanta `TypeError` em vez de reportar falha. Nenhuma planta cobre esse ramo (as duas novas cobrem "3D set ignored" e "3D tab never off"), então esse veredito nunca foi visto vermelho.

## Evidência

```text
$ sed -n 488,489p tools/kits/ui_check.py
                    bad.append("%d pixel(s) differ above the note rows, in a %dx%d box down to "
                               "row %d: more than the tab label" % (len(above),) + box)
$ python3 - <<'PY'
above=[(0,0)]*3; box=(50, 30, 90)
try:
    print("%d pixel(s) differ above the note rows, in a %dx%d box down to "
          "row %d: more than the tab label" % (len(above),) + box)
except Exception as e: print(type(e).__name__, e)
PY
TypeError not enough arguments for format string
$ S=$(mktemp -d); DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 - <<PY
import sys, os
sys.path.insert(0, "tools/kits")
import ui_check as u
env = u.environment()
python = u.find_upward(os.path.join(u.VENV, u.VENV_PYTHON))
old = "        self.tabs.setTabEnabled(1, self.geometry is not None)\n"
new = old + "        self.zones_box.setEnabled(self.geometry is not None)  # planted: Plan changes\n"
app = u.sandbox("$S", old, new)
try:
    print("judge:", u.off_judge(python, os.path.abspath("roms/japanese-shift-jis.bin"), env, "$S", app))
except Exception as e:
    print("CRASH", type(e).__name__, e)
PY
CRASH TypeError not enough arguments for format string
```

## Root cause

Precedência de operador: o pretendido era `% ((len(above),) + box)`. Passou porque nenhuma planta exercita o ramo "more than the tab label".

## Fix

No `off_judge` de `tools/kits/ui_check.py`, escrever `% ((len(above),) + box)`. Acrescentar a `PLANTS` uma terceira planta 3D, julgada pelo juiz OFF, que muda um widget da aba Plano só quando `geometry` é `None` (por exemplo a do `zones_box` acima), para o Log mostrar esse ramo vermelho com a mensagem dele.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`

## Verificação

O heredoc da caixa de areia acima imprime `CRASH TypeError…` hoje; depois do conserto tem de imprimir `judge: ['N pixel(s) differ above the note rows, … more than the tab label']`, e `python3 tools/kits/ui_check.py` tem de mostrar a planta nova como `ok plant '…' fails the 3D off judge`.

## Log de Execução
