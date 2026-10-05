---
id: CORR-KITS-068
---

# CORR-KITS-068 — Contar braçadeira e manga longa de forma exclusiva no --sleeves

Origin: [KITS-TASK-39](/docs/tasks/kits/39-medir-bracadeira.md)

## Problem

Em `sleeves_tally` (`tools/kits/oracle.py:511-512`), uma primitiva conta como "manga longa" se qualquer zona tocada começa com "long sleeve", e como "braçadeira" se qualquer uma começa com "armband". Os quads da braçadeira cobrem v 142–155: "long sleeve, left, captain" (y 14–19), "armband, long sleeve" (y 20–24) e "…under the armband" (y 25–27). Então as 8 primitivas da braçadeira também contam como manga longa, enquanto 8 primitivas de cotovelo não contam como nenhuma. A tabela da §4.3 (88 | 8) se lê como partição de 96, mas é 80 só-manga + 8 ambas + 8 nenhuma — e o critério pedia as duas contadas separadas. Duas frases da §4.3 vêm da mesma causa:

- "As zonas de capitão … também são amostradas, por 4 primitivas cada" (linha 580): esses 4+4 são os próprios quads da braçadeira, não outra geometria.
- "seção 93: 6 quads, todos na zona 'armband, long sleeve'" (linha 573): cada um também toca uma zona de capitão.

A tabela por seção não é afetada, porque `model_sections` dá prioridade à braçadeira.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/kits/oracle.py --sleeves 5 --expect-sleeves drawn
  kit pages: uniform image 154, sleeves image 96, both 0; other pages 539
  of those touching the sleeves image: long sleeve zones 88, armband zones 8
  zone armband, long sleeve                             8 primitive(s)
  zone long sleeve, left, captain, under the armband    4 primitive(s)
  zone elbow, right                                     4 primitive(s)
  zone long sleeve, left, captain                       4 primitive(s)
  zone elbow, left                                      4 primitive(s)
$ grep -n "def sleeves_tally" -A14 tools/kits/oracle.py | grep "any("
511-            out["long sleeve"] += any(n.startswith("long sleeve") for n in names)
512-            out["armband"] += any(n.startswith("armband") for n in names)
```

Sonda do revisor (mesmo ambiente, emulador no `:98`; a HEAD não tem opção que imprima isto):

```text
$ python3 - <<'PY'
import sys, os, collections, importlib.util
spec = importlib.util.spec_from_file_location("kits_oracle", "tools/kits/oracle.py")
o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
s = o.read_frame(5, os.environ["WE2002_LOOKS_DRIVE_IMAGE"])
c = collections.Counter()
for one in s:
    if o.kit_image_of(one) in ("sleeves","both"):
        n = o.sample_zones(one)
        ls = any(x.startswith("long sleeve") for x in n); ab = any(x.startswith("armband") for x in n)
        c[(ls, ab)] += 1
print("(long sleeve?, armband?) -> primitives:", dict(c))
PY
(long sleeve?, armband?) -> primitives: {(True, False): 80, (True, True): 8, (False, False): 8}
```

Uma segunda sonda listando as primitivas que tocam zona de capitão ou de braçadeira devolveu 8, cada uma com 'armband, long sleeve' mais uma zona de capitão — por exemplo uv ((40,142),(46,142),(40,151),(47,151)) → ('armband, long sleeve', 'long sleeve, left, captain').

## Root cause

`sleeves_tally` soma dois booleanos `any()` independentes sobre as zonas que a caixa de texels toca, sem prioridade e sem balde "nenhuma". `model_sections` usa prioridade braçadeira-primeiro, então as duas saídas classificam diferente. A tabela da §4.3 foi transcrita da linha do tally sem conferir a sobreposição.

## Fix

Em `tools/kits/oracle.py`, fazer `sleeves_tally`/`run_sleeves` classificar cada primitiva de forma exclusiva, com a mesma regra braçadeira-primeiro de `model_sections`, imprimir uma contagem "outras (cotovelo…)" para que as três somem o total da imagem de mangas, e fazer `sleeves_judge` afirmar essa soma. Em `tools/kits/selftest.py`, um caso com quad atravessando braçadeira e capitão. Depois recolar a tabela da §4.3 (esperado 80 | 8 | 8 outras) e corrigir as duas frases da §4.3 sobre zonas de capitão e "todos na zona 'armband, long sleeve'" em `docs/PLAN-KITS-PY.md`, e a frase correspondente no Log da KITS-TASK-39 se ela se repetir lá.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `tools/kits/selftest.py`
- `docs/PLAN-KITS-PY.md`

## Verificação

`python3 tools/kits/oracle.py --sleeves 5 --expect-sleeves drawn` imprime contagens de manga longa, braçadeira e outras que somam o total da imagem de mangas (96 = 80 + 8 + 8); hoje imprime 88 + 8 sem "outras". `python3 tools/kits/selftest.py` inclui um caso de quad atravessado que falha com o tally não exclusivo de hoje.

## Log de Execução
