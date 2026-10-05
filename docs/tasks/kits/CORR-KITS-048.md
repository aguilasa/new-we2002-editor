---
id: CORR-KITS-048
---

# CORR-KITS-048 — Levar os números de sondas descartáveis do Log para opção versionada do oracle.py

Origin: [KITS-TASK-27](/docs/tasks/kits/27-titular-e-suplente-no-jogo.md)

## Problem

O Log da KITS-TASK-27 diz que "as 79 linhas não planas do uniforme do conjunto 2 do `TEX_13` estão todas na VRAM". Com "não plana" = mais de um valor distinto, o mesmo dump tem 80, todas exatas; o Log não define "plana", e nenhum comando versionado imprime essa contagem. O mesmo vale para as cores da bandeira `(24, 90, 132)` / `(140, 33, 41)` "via `api.flat(8, 9)`" — `tools/kits/core/api.py` não tem função `flat`, só `kit.flat(image, palette)` — e para `pl1==pl2 False, gk1==gk2 False, img0==img4 False`. Número que entra em Log sai de ferramenta versionada na HEAD entregue.

## Evidência

```text
$ cat > $S/probe2.py <<'PY'
import sys, os, struct
sys.path.insert(0, "tools/kits")
import oracle as o
bodies = o.read_kits(os.environ["WE2002_LOOKS_IMAGE"])
vram = o.vram_rows(sys.argv[1])
for t, x in (("01", 576), ("13", 640)):
    b = bodies[t]; recs = o.records_of(b)
    for rec in (0, 4, 1, 5):
        r = recs[rec]; w = o.payload(b, r); y = 256 if rec in (0, 4) else 384
        nonflat = full = 0
        for k in range(r.h):
            line = w[k*r.w:(k+1)*r.w]
            if len(set(o.five(v) for v in line)) <= 1: continue
            nonflat += 1
            vr = struct.unpack("<%dH" % r.w, vram[y+k][2*x:2*(x+r.w)])
            full += all(a == o.five(v) for a, v in zip(vr, line))
        print(t, rec, "set", 1 if rec < 4 else 2, "nonflat", nonflat, "exact lines", full)
PY
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $S/probe2.py $S/match-3/vram-0.png
  01 0 set 1 nonflat 80 exact lines 12
  01 4 set 2 nonflat 80 exact lines 0
  13 0 set 1 nonflat 80 exact lines 0
  13 4 set 2 nonflat 80 exact lines 80
$ grep -n "def flat" tools/kits/core/api.py
(sem saída)
$ grep -n "as 79 linhas" docs/tasks/kits/27-titular-e-suplente-no-jogo.md
72:...
```

(`vram-0.png` sai da corrida `--slot 3` da CORR-KITS-047.)

## Root cause

Hipótese: a primeira corrida na partida foi examinada com um script descartável cuja definição de linha plana nunca foi escrita; as cores da bandeira vieram de chamada interativa.

## Fix

Em `tools/kits/oracle.py`, uma opção (por exemplo `--lines` e `--flags`) que imprima as linhas exatas por conjunto, com "plana" definida em código, as cores dominantes da bandeira e as comparações de igualdade de pares. Colar a saída dela no Log no lugar do 79 e dos valores de sonda.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/tasks/kits/27-titular-e-suplente-no-jogo.md`

## Verificação

`python3 tools/kits/oracle.py --png <dump da partida> --lines` imprime as contagens de linha que o Log cita (hoje: `unrecognized arguments`), e `grep -c "as 79 linhas" docs/tasks/kits/27-titular-e-suplente-no-jogo.md` dá 0.

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `516d1ab`: `oracle.py --lines` dava `unrecognized arguments`, o Log dizia `as 79 linhas` e citava `api.flat(8, 9)`, função que o `api.py` não tem; a sonda da Evidência, sobre `work/kits-oracle/match-3/vram-0.png`, dá 80 linhas não planas e exatas no conjunto 2 do `TEX_13`.

Conserto: duas opções do `oracle.py`, com "plana" definida em código (`is_flat_line`: um só valor de 15 bits).

- `--lines`: para uniforme e mangas dos dois conjuntos de cada kit achado, as linhas não planas e quantas estão na VRAM halfword a halfword, no lugar que o `closest_sets` escolhe.
- `--flags`: as três cores mais comuns da bandeira (registro 8 pintado com o 9 por `kit.flat`, preto fora) e, por par, se o registro do conjunto 1 é igual ao do 2.

No Log da KITS-TASK-27, o 79 virou 80 com a definição, e o parágrafo da bandeira passou a ser o comando e a saída dele; o `api.flat` e os `pl1==pl2` de sonda saíram.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png --lines --flags | sed -n '/lines not flat/,$p'
  TEX_01 uniform  set 1 at (576,256):  80 of 128 lines not flat,  12 of them exact
  TEX_01 uniform  set 2 at (576,256):  80 of 128 lines not flat,   0 of them exact
  TEX_01 sleeves  set 1 at (576,384): 128 of 128 lines not flat,   0 of them exact
  TEX_01 sleeves  set 2 at (576,384): 128 of 128 lines not flat,   0 of them exact
  TEX_13 uniform  set 1 at (640,256):  80 of 128 lines not flat,   0 of them exact
  TEX_13 uniform  set 2 at (640,256):  80 of 128 lines not flat,  80 of them exact
  TEX_13 sleeves  set 1 at (640,384): 128 of 128 lines not flat,   0 of them exact
  TEX_13 sleeves  set 2 at (640,384): 128 of 128 lines not flat,   0 of them exact
  TEX_01 flag, black left out: (24, 90, 132) 20 %, (222, 222, 222) 18 %, (33, 90, 132) 8 %
  TEX_01 uniform 1==2 False, sleeves 1==2 False, player palette 1==2 False, goalkeeper palette 1==2 False
  TEX_13 flag, black left out: (140, 33, 41) 46 %, (156, 41, 41) 7 %, (165, 41, 49) 6 %
  TEX_13 uniform 1==2 False, sleeves 1==2 False, player palette 1==2 False, goalkeeper palette 1==2 False
$ grep -c "as 79 linhas" docs/tasks/kits/27-titular-e-suplente-no-jogo.md
0
```

Os números batem com a sonda da Evidência (80/12 e 80/80) e com as cores que o Log já citava.
- **Closed** — commit `45f008d` (2026-10-04): feat(kits): oracle.py --lines and --flags replace the KITS-TASK-27 probes
  - Files (`git show --name-status 45f008d`):
    - `M docs/tasks/kits/27-titular-e-suplente-no-jogo.md`
    - `M docs/tasks/kits/CORR-KITS-048.md`
    - `M tools/kits/oracle.py`
