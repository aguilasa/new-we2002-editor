---
id: CORR-LOOKS-087
title: Dizer qual interpretador roda o confront.py --outside
origin: LOOKS-TASK-39
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-087 — Dizer qual interpretador roda o confront.py --outside

Origin: [LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)

## Problema identificado

A linha do `confront.py --outside` no perfil — editada por este commit — lista
"o venv" entre o que o comando precisa, e a regra do ciclo é chamar o
interpretador do venv **por caminho**. Rodar assim o terceiro critério de
conclusão da task estoura num traceback que não nomeia nem o Pillow nem o
venv: o venv tem PySide6 e não tem Pillow, e o `python` principal tem Pillow e
não tem PySide6 (a ferramenta lança o do venv para desenhar). Quem re-rodar o
critério perde tempo num erro que parece captura quebrada.

## Evidência

```text
$ work/venv-looks/Scripts/python.exe tools/looks/confront.py --outside 2
  File "C:\github\new-we2002-editor\tools\pes2\drive.py", line 191, in __init__
    with PILImage.open(path) as im:
AttributeError: 'NoneType' object has no attribute 'open'

$ work/venv-looks/Scripts/python.exe -c "import PIL"   -> ModuleNotFoundError: No module named 'PIL'
$ python -c "import PySide6"                            -> ModuleNotFoundError: No module named 'PySide6'
$ python tools/looks/confront.py --outside 2            -> confront --outside: 0 problem(s) over 1 slot(s)
```

## Causa raiz

O `tools/pes2/drive.py` deixa o Pillow opcional (`PILImage = None`) e adia a
falha para o acesso de atributo; e a linha da receita não diz que o comando em
si roda sob o interpretador principal, lançando o do venv só para a janela.

## Correção

Recusar cedo, no `drive.py`/`confront.py`, com "Pillow is not installed in this
interpreter — run confront.py with the main python; the venv is spawned for the
window". Nomear o interpretador na linha do `--outside` do perfil (e na tabela
do `CLAUDE.md`) é o remendo; a recusa cedo é o durável, e vale fazer os dois.

## Arquivos

- tools/pes2/drive.py
- tools/looks/confront.py
- docs/prompts/perfil-looks.md

## Verificação

`work/venv-looks/Scripts/python.exe tools/looks/confront.py --outside 2` sai
com mensagem nomeando o Pillow e o interpretador certo, em vez do
`AttributeError`.

## Log de Execução
