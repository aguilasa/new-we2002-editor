---
id: CORR-LOOKS-101
title: "A guarda de disco do oracle.py recusa o state em outra máquina por comparar o caminho absoluto"
origin: LOOKS-TASK-08
severity: high
files: [tools/looks/oracle.py]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-28
done_commit: fca4bdd
---

# CORR-LOOKS-101 — A guarda de disco do oracle.py recusa o state em outra máquina por comparar o caminho absoluto

Origin: [LOOKS-TASK-08](/docs/tasks/concluidos/looks/08-de-onde-vem-o-boneco.md)

## Problem

No Linux, `python3 tools/looks/oracle.py --check-live` recusa os dois save
states do ciclo antes de subir o emulador, com `WrongDisc`, embora eles sejam
do disco certo. Todos os comandos de emulador passam pelo `require_media`, então
nenhum roda no Linux com os states gravados no Windows.

## Evidência

```text
$ WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue python3 tools/looks/oracle.py --check-live
oracle FAILED: SLPM-87056_1.sav was recorded on 'C:\\games\\ps1\\work\\we2002-english.cue', and this cycle drives '/home/ingmar/desenvolvimento/github/new-we2002-editor/work/looks-disc/we2002-english.cue'.  ...
```

E o fork aceita esse state com o `.cue` do Linux: subido sobre
`work/looks-disc/we2002-english.cue`, `load_state slot=1` responde
`"status": "loaded"` e o quadro é a `LOOKS SET` do goleiro. Medido em
2026-09-28 com o fork `c55b8ee` e o state gravado pelo `a2edf2d`.

## Root cause

`require_media` comparava o caminho **absoluto** gravado no state com o `.cue`
em uso. Esse caminho é um fato sobre a máquina que gravou, não sobre o disco.
Enquanto o ciclo rodou só no Windows, e sempre com a mesma cópia, a igualdade
valia por acaso. Além disso, no Linux o `os.path.basename` não separa um caminho
com `\`, então nem o nome daria para comparar pelas funções de `os.path`.

## Fix

Em `tools/looks/oracle.py`, `disc_name()` extrai o nome do arquivo separando
pelas duas barras e ignorando caixa, e `same_disc()` compara só o nome. O
`require_media` usa `same_disc`. O caso que a guarda existe para pegar — um state
do disco japonês — continua recusado, porque o `.cue` japonês tem outro nome nas
duas máquinas. O que o nome não distingue continua com os digests do
`layout.py` e com a RAM que o `--check-live` confere contra o disco.

Quatro casos novos no self-check: Windows contra Linux com o mesmo nome passa,
caixa diferente passa, o `.cue` japonês é recusado, e um nome que só termina
igual é recusado.

## Arquivos a criar ou modificar

- [tools/looks/oracle.py](/tools/looks/oracle.py)

## Verificação

```text
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
```

Controle negativo, `same_disc` trocado pela comparação antiga:

```text
  FAIL  a state recorded on Windows matches the same cue on Linux
  FAIL  and the case of a Windows path does not matter
oracle.py: 2 failure(s)
```

Com o conserto, o `--check-live` passa da guarda, sobe o fork, restaura os
states e captura a tela do slot 1. A falha seguinte — a média do quadro — é
outro defeito, e não este.

## Log de Execução

- 2026-09-28 — medido que o fork `c55b8ee` carrega o state do `a2edf2d`;
  corrigido; selftest verde; controle negativo vermelho.
- **Closed** — commit `fca4bdd` (2026-09-28): fix(looks): compare a save state's disc by file name, not absolute path
  - Files (`git show --name-status fca4bdd`):
    - `A docs/tasks/looks/CORR-LOOKS-101.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/oracle.py`
