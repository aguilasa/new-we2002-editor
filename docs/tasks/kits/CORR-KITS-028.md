---
id: CORR-KITS-028
---

# CORR-KITS-028 — Gate the zone-map-vs-PNG check, or stop saying kits_image runs it

Origin: [KITS-TASK-16](/docs/tasks/kits/16-zonas.md)

## Problem

O §4.6 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) e a mensagem do commit dizem que a conferência `--map` roda no `kits_image`. Não roda: o `_zones_checks` de `tools/kits/selftest.py` só executa `cli.py zones <img>` e `cli.py zones --negative <img>`. Nenhum gate confere que as linhas do `ZONES` são o desenho do polipoli, e os números "0 pixel(s) painted and in no zone" e "248 pixel(s)" do Log vêm de um PNG numa pasta do usuário que o Log deixa como `<…>`. O revisor não achou `Zonas We2002.png` nesta máquina, então nenhum dos dois números foi reproduzido.

## Evidência

```text
$ grep -c "\-\-map" tools/kits/selftest.py
0
$ sed -n 475,490p tools/kits/selftest.py
proc = subprocess.run([sys.executable, cli, "zones", image_path], ...
proc = subprocess.run([sys.executable, cli, "zones", "--negative", image_path], ...
$ grep -n "Os dois rodam" docs/PLAN-KITS-PY.md
...; o `--map --negative` faz o mesmo contra o PNG (248 pixels pintados fora de zona). Os dois rodam no `kits_image`.
$ find /c/Users/ingcvs /c/github /d /e -maxdepth 8 -iname "Zonas We2002*.png"
(vazio)
```

## Root cause

Hipótese: o caminho `--map` precisa de um arquivo de terceiro fora do repositório, por isso nunca foi ligado a um gate, e a frase foi escrita como se tivesse sido.

## Fix

Acrescentar ao `kits_image` (ou a um teste separado) uma conferência que rode `cli.py zones --map` e `--map --negative` contra um PNG apontado por variável de ambiente (por exemplo `WE2002_KITS_ZONES_PNG`), pulando quando ela não estiver definida, e nomear essa variável no Log para que o 0 e o 248 se reproduzam. Se não entrar gate, corrigir a frase no §4.6 do plano e no Log da task para dizer que o `--map` é conferência manual.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `docs/PLAN-KITS-PY.md`
- `docs/tasks/kits/16-zonas.md`

## Verificação

```text
$ grep -n "\-\-map" tools/kits/selftest.py
```

Hoje não sai nada; depois tem de mostrar as chamadas `--map` e `--map --negative`. Na alternativa sem gate, `grep -c "Os dois rodam no" docs/PLAN-KITS-PY.md` vai de 1 a 0.

## Log de Execução
