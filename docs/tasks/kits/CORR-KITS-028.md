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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `eaeb6838`)

```text
$ grep -c "\-\-map" tools/kits/selftest.py
0
$ grep -n "Os dois rodam" docs/PLAN-KITS-PY.md
541:de zona). Os dois rodam no `kits_image`.
```

REPRODUCED. O PNG existe nesta máquina, fora de onde a revisão procurou: `C:/games/we2002/Superpackv6/We2002/TEX/Zonas kits y tex - polipoli/We2002/Zonas We2002.png` (2.039 bytes). Com ele os dois números do Log se reproduzem:

```text
$ python tools/kits/cli.py zones --map ".../Zonas We2002.png" | tail -2; echo exit ${PIPESTATUS[0]}
map: 0 pixel(s) painted and in no zone, 1 zone(s) holding the background (numbers 0-9 by design)
verdict: every row of the map is the picture
exit 0
$ python tools/kits/cli.py zones --map ".../Zonas We2002.png" --negative | grep -i "pixel\|held"
map: 248 pixel(s) painted and in no zone, 30 zone(s) holding the background
control red, held: the moved map fails
```

### O que foi feito

Primeira forma do conserto (gate, não frase):

- `tools/kits/selftest.py`: `_zones_map_checks`, chamado do `_zones_checks` do `kits_image`. Com `WE2002_KITS_ZONES_PNG` definida, roda `zones --map` (exige "every row of the map is the picture") e `zones --map --negative` (exige "control red, held"); variável definida e caminho que não é arquivo é falha; sem a variável, imprime que não rodou.
- §4.6 do plano: "Os dois rodam no `kits_image`" diz agora em que condição o `--map` roda.
- KITS-TASK-16: o `<…>` do Log ganhou o caminho desta máquina e a variável.

### Verificação

```text
$ grep -n "\-\-map" tools/kits/selftest.py
(as chamadas "zones", "--map", png e "zones", "--map", png, "--negative" do _zones_map_checks)
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_KITS_ZONES_PNG=".../Zonas We2002.png" python tools/kits/selftest.py --image | tail -5; echo exit $?
  ok    section 5 control 4: the zone map moved 1 px fails section 4.6
  ok    WE2002_KITS_ZONES_PNG points at a file
  ok    zones --map: every row of the map is polipoli's picture
  ok    zones --map --negative: the map moved 1 px fails against the picture
kits_image: 0 failure(s)
exit 0
```

O check visto falhando — a variável apontando outro mapa do polipoli (`Pes2009/Zonas Pes2009.png`), e um caminho que não existe:

```text
  FAIL  zones --map: every row of the map is polipoli's picture  exit 1
  FAIL  zones --map --negative: the map moved 1 px fails against the picture  exit 1
zones-map: 2 failure(s)
---
  FAIL  WE2002_KITS_ZONES_PNG points at a file  C:/nope/z.png
zones-map: 1 failure(s)
---  (sem a variável)
  ..... zones --map: not run, WE2002_KITS_ZONES_PNG is not set (polipoli's Zonas We2002.png)
zones-map: 0 failure(s)
```
- **Closed** — commit `9ca8ef33` (2026-10-02): fix(kits): run zones --map in kits_image when WE2002_KITS_ZONES_PNG is set
  - Files (`git show --name-status 9ca8ef33`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/16-zonas.md`
    - `M docs/tasks/kits/CORR-KITS-028.md`
    - `M tools/kits/selftest.py`
