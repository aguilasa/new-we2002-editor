---
id: CORR-KITS-042
---

# CORR-KITS-042 — Tornar a evidência do Log reproduzível a partir da HEAD

Origin: [KITS-TASK-24](/docs/tasks/concluidos/kits/24-figura.md)

## Problem

Três peças de evidência do Log da KITS-TASK-24 não se reproduzem a partir da HEAD. (a) A medição AST do critério 1 aparece como `python3 - <<'X'` com a saída do script no lugar do corpo. (b) O vermelho em disco do critério 3 foi rodado "numa cópia da árvore" sem os passos para refazê-lo, e nenhuma sonda versionada o reproduz: o controle `figure-swap-noop` do `controls.py` planta só contra o contêiner sintético do selftest, não contra `--image`. (c) As transcrições foram editadas: a saída do `grep -E 'TEX_00|figure:'` omite três das quatro linhas `ok` de `TEX_00` e a linha `ok section 5 control 4 on /BIN/TEX_00.BIN`, que o mesmo grep casa; as linhas FAIL e a de `GeometryRefused` têm `…`.

## Evidência

```text
$ grep -n "python3 - <<'X'\|^X$\|numa cópia da árvore\|…" docs/tasks/kits/24-figura.md
40:$ python3 - <<'X'   # módulos de tools/looks importados por cada arquivo de tools/kits/core
44:X
64:GeometryRefused: ... read d0ff5ac291e1818c… from ro…
81:O vermelho, numa cópia da árvore com `swapped_palettes` devolvendo o kit intacto:
85-87:  FAIL  TEX_00 set ... figure ...: …  record ...
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image | grep -E 'TEX_|figure:'
ok    section 5 control 4 on /BIN/TEX_00.BIN on ...   <- ausente do Log
ok    TEX_00 set 2 figure 0 / set 1 figure 1 / set 2 figure 1 ...  <- ausentes do Log
$ python3 tools/kits/controls.py --help
(só --list/--only; nenhum controle roda --image)
$ grep -c '…' docs/tasks/kits/24-figura.md
4
```

O vermelho em si reproduz: numa cópia `git archive HEAD tools`, trocar `    return bytes(out)\n` por `    return bytes(data)\n` em `tools/kits/core/figure.py` e rodar `selftest.py --image` dá 4 FAIL e `figure: 4 failure(s)`. Mas essa medição foi feita à mão pelo revisor.

## Root cause

Hipótese: o Log foi escrito à mão a partir das corridas, em vez de colado da saída da ferramenta na HEAD entregue.

## Fix

Em `docs/tasks/kits/24-figura.md`: pôr o script AST inteiro dentro do heredoc; escrever o vermelho em disco como passos a partir da HEAD (`git archive` + troca + `selftest.py --image`), ou dar ao `tools/kits/controls.py` uma opção que rode o `figure-swap-noop` contra `selftest.py --image` e citá-la; colar a saída do grep sem edição.

## Arquivos a criar ou modificar

- `docs/tasks/kits/24-figura.md`
- `tools/kits/controls.py` (se a sonda for acrescentada)

## Verificação

`grep -c '…' docs/tasks/kits/24-figura.md` dá 0 (hoje 4), e as linhas `$` do Log, rodadas como estão, reproduzem cada bloco colado.

## Log de Execução

### 2026-10-03

Reproduzido na HEAD `ea8e6e0`: `grep -c '…' docs/tasks/kits/24-figura.md` dá `4`; o heredoc AST sem corpo, o vermelho em disco sem passos e o grep de `TEX_00` sem quatro das linhas que ele casa, como a Evidência diz.

Conserto, só no Log (o `controls.py` não muda — o vermelho em disco ficou escrito como passos):

- (a) o script AST inteiro dentro do heredoc, rodado numa cópia `git archive 3cfb2c4 tools` (a base "antes desta task"). A saída lista os nove arquivos; os dois com import do `looks` são os que o Log já dizia (`survey.py`, `teams.py`), os outros sete `[]`.
- (b) o vermelho em disco como três comandos a partir da HEAD (`git archive` + `sed` em `return bytes(out)` + `selftest.py --image`), rodados aqui: 4 `FAIL`, `figure: 4 failure(s)`, linha a linha a saída colada.
- (c) o grep de `TEX_00` colado sem edição (dez linhas, com a de `section 5 control 4` e as três `ok` que faltavam); as duas linhas do critério 2 como comandos inteiros com `2>&1 | tail -1`, que imprimem a exceção qualificada (`core.errors.NoGeometry`, `core.errors.GeometryRefused`) e a mensagem inteira, sem `…`.

```
$ grep -c '…' docs/tasks/kits/24-figura.md
0
```
- **Closed** — commit `5d9f2a3` (2026-10-03): docs(kits): make the KITS-TASK-24 log evidence reproducible from HEAD
  - Files (`git show --name-status 5d9f2a3`):
    - `M docs/tasks/kits/24-figura.md`
    - `M docs/tasks/kits/CORR-KITS-042.md`
