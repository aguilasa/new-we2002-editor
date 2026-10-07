---
id: CORR-KITS-004
---

# CORR-KITS-004 — Paste the rects transcript as the tool prints it

Origin: [KITS-TASK-02](/docs/tasks/concluidos/kits/02-retangulos-608-e-704.md)

## Problem

O bloco `$ python tools/kits/cli.py rects ...` do Log da KITS-TASK-02 não é o que o comando imprime: falta o cabeçalho `VRAM point owners: roms/japanese-shift-jis.bin`, as nove linhas `skipped ...` viraram uma nota escrita à mão ("(1 Form 2, 8 fora da trilha)"), os três nomes de cada grupo foram cortados para "/BIN/TEX_00.BIN, ..." e as linhas dos grupos (576,256) e (576,384) sumiram. O primeiro critério de pronto diz que a saída é "colada no Log"; transcrição editada à mão contraria a regra "número em Log é colado da ferramenta".

## Evidência

```text
$ python tools/kits/cli.py rects roms/japanese-shift-jis.bin 608,256 704,256 576,256 576,384
VRAM point owners: roms/japanese-shift-jis.bin
  236 files read, 131 hold records; 9 skipped
    skipped /MOVIE/WE2002.STR (Form 2)
    skipped /SD/DA/01GOALDM.DA (outside the track)
...
$ grep -c 'VRAM point owners' docs/tasks/kits/02-retangulos-608-e-704.md
0
$ grep -n 'fora da trilha' docs/tasks/kits/02-retangulos-608-e-704.md
51:  236 files read, 131 hold records; 9 skipped        (1 Form 2, 8 fora da trilha)
```

## Root cause

Hipótese: a saída foi condensada à mão ao entrar no Log.

## Fix

Trocar o bloco de evidência da task pela saída literal do mesmo comando na HEAD; comentário vai fora do bloco de código. Só o bloco de evidência muda, sem mexer no frontmatter.

## Arquivos a criar ou modificar

- `docs/tasks/kits/02-retangulos-608-e-704.md`

## Verificação

```text
$ grep -c 'VRAM point owners' docs/tasks/kits/02-retangulos-608-e-704.md
```

Hoje dá 0; depois, pelo menos 1, e `grep -n 'fora da trilha'` não acha nada dentro do bloco `$`.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `10bd0e3a`)

```text
$ grep -c 'VRAM point owners' docs/tasks/kits/02-retangulos-608-e-704.md
0
$ grep -n 'fora da trilha' docs/tasks/kits/02-retangulos-608-e-704.md
51:  236 files read, 131 hold records; 9 skipped        (1 Form 2, 8 fora da trilha)
```

REPRODUCED. Causa raiz confirmada: a saída do comando (cabeçalho, nove `skipped`, três nomes por grupo, as linhas de (576,256) e (576,384)) não bate com o bloco.

### O que foi feito

Bloco `$ python tools/kits/cli.py rects ...` da KITS-TASK-02 trocado pela saída literal do mesmo comando na HEAD `498109fa` (exit 0). Nada fora dele mudou; o `atlas.py --elsewhere` logo abaixo segue como trecho de duas linhas, fora do escopo desta CORR.

### Verificação

```text
$ grep -c 'VRAM point owners' docs/tasks/kits/02-retangulos-608-e-704.md
1
$ grep -n 'fora da trilha' docs/tasks/kits/02-retangulos-608-e-704.md
(sem saída, exit 1)
```
- **Closed** — commit `fc984d0a` (2026-09-30): docs(kits): paste the rects transcript of KITS-TASK-02 as the tool prints it
  - Files (`git show --name-status fc984d0a`):
    - `M docs/tasks/kits/02-retangulos-608-e-704.md`
    - `M docs/tasks/kits/CORR-KITS-004.md`
