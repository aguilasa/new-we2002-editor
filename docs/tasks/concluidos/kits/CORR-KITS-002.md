---
id: CORR-KITS-002
---

# CORR-KITS-002 — Version the survey's negative controls instead of an ad hoc probe

Origin: [KITS-TASK-01](/docs/tasks/concluidos/kits/01-levantamento-do-tex.md)

## Problem

O Log da KITS-TASK-01 mostra resultados de controle negativo (`clean {...}` / `planted {...}`, e o árbitro indo de 1 para 2 variantes), mas o script que os produziu não está no repositório nem no Log. Nenhum selftest nem alvo de `ctest` exercita `survey_files`. A regra do projeto ("sonda que produziu um número vira opção de uma ferramenta versionada"; "verificador sem vermelho visto não é gate") exige que o vermelho seja reproduzível da HEAD.

## Evidência

```text
$ git ls-files tools/kits
tools/kits/cli.py
tools/kits/core/__init__.py
tools/kits/core/survey.py
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin
cli.py: error: unrecognized arguments: --negative
```

O revisor replantou os mesmos bits de CLUT numa sonda própria e obteve `planted 105 () 103 ('98','A4') () 1` e `ref 2` — o verificador fica vermelho —, mas os 104/102 do Log vêm de uma edição extra de retângulo que não se reconstrói a partir do Log.

## Root cause

Hipótese: o controle rodou como sonda descartável em memória — exatamente o padrão que a task existia para eliminar no §1.1.

## Fix

Adicionar um controle versionado (`tools/kits/selftest.py` ou `cli.py survey --negative <imagem>`) que plante, via `survey_files`, os três defeitos — bit de CLUT no conjunto 2 do `TEX_A4`, bit de CLUT de goleiro no conjunto 1 do `TEX_A4`, e o árbitro do `TEX_00` — e afirme que as contagens se movem. Colar a saída dele no Log no lugar dos dicionários da sonda.

## Arquivos a criar ou modificar

- `tools/kits/cli.py` (ou novo `tools/kits/selftest.py`)
- `docs/tasks/kits/01-levantamento-do-tex.md`

## Verificação

```text
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin
```

Hoje: erro do argparse. Depois: cada defeito plantado imprime o vermelho, saída 0.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `a384fe67`)

```text
$ git ls-files tools/kits
tools/kits/cli.py
tools/kits/core/__init__.py
tools/kits/core/survey.py
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin
usage: cli.py [-h] {survey} ...
cli.py: error: unrecognized arguments: --negative
```

REPRODUCED (exit 2). Causa raiz confirmada: nenhum arquivo versionado planta defeito; a sonda do Log não existe na árvore.

### O que foi feito

- `tools/kits/core/survey.py`: `NEGATIVE_CONTROLS` (os quatro defeitos do Log — bit na CLUT de jogador do 2º conjunto do `TEX_A4`, bit na CLUT de goleiro do 1º, bit no fluxo LZSS do árbitro do `TEX_00` em +3, e `x` do retângulo do árbitro do `TEX_00` + 1), `negative_controls(files)` puro, que planta **um por vez** e devolve `ControlResult` com a figura antes e depois, e `negative_controls_image(path)`. Sem `print`: a medição fica no núcleo, como o resto do levantamento. `survey.py` não estava nos arquivos previstos; a alternativa era pôr lógica de plantio no `cli.py`, que só imprime.
- `tools/kits/cli.py survey --negative <imagem>`: imprime cada controle; sai 1 se algum ficar verde.
- KITS-TASK-01, Evidência: os dicionários da sonda trocados pela saída do comando. A figura muda de forma: antes os defeitos eram plantados juntos (104/102 somados); agora cada um move a sua.

### Verificação

```text
$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin; echo "exit $?"
  A4 player CLUT, second set       TEX_A4   first set == second set: ('A4',) -> ()  red
  A4 goalkeeper CLUT, first set    TEX_A4   player palette == keeper palette: ('A4',) -> ()  red
  00 referee LZSS stream, +3       TEX_00   referee variants / problems: (1, ()) -> (2, ())  red
  00 referee rect x + 1            TEX_00   shape ok: 105 -> 104  red
4 of 4 controls red
exit 0
```

O verificador visto falhando — o primeiro plantio trocado por identidade:

```text
$ python -c "import sys; sys.path.insert(0,'tools/kits'); import cli; from core import survey as s
s.NEGATIVE_CONTROLS = tuple((n,t,(lambda d:d),f,m) for n,t,_,f,m in s.NEGATIVE_CONTROLS[:1]) + s.NEGATIVE_CONTROLS[1:]
raise SystemExit(cli.main(['survey','--negative','roms/japanese-shift-jis.bin']))"; echo "exit $?"
  A4 player CLUT, second set       TEX_A4   first set == second set: ('A4',) -> ('A4',)  GREEN (control failed)
  ...
3 of 4 controls red
exit 1
$ grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py
(sem saída, exit 1)
```

Ligar o comando ao `ctest` (`kits_image`) é da KITS-TASK-08.
- **Closed** — commit `b9bce55b` (2026-09-30): fix(kits): version the survey negative controls as cli.py survey --negative
  - Files (`git show --name-status b9bce55b`):
    - `M docs/tasks/kits/01-levantamento-do-tex.md`
    - `M docs/tasks/kits/CORR-KITS-002.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/survey.py`
