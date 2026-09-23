---
id: CORR-LOOKS-087
title: Dizer qual interpretador roda o confront.py --outside
origin: LOOKS-TASK-39
severity: low
files: [tools/pes2/drive.py, tools/looks/confront.py, docs/prompts/perfil-looks.md, CLAUDE.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

Triagem do `/rite:fix-all looks` em 2026-09-23, HEAD `dca4a96e`: **reproduzida**, as quatro linhas.

```text
$ work/venv-looks/Scripts/python.exe tools/looks/confront.py --outside 2
  ... drive.py:191, in __init__ -> AttributeError: 'NoneType' object has no attribute 'open'   (saída 1,
  depois de subir o fork e mover a janela para fora da tela)
$ work/venv-looks/Scripts/python.exe -c "import PIL"    -> ModuleNotFoundError: No module named 'PIL'
$ python -c "import PySide6"                            -> ModuleNotFoundError: No module named 'PySide6'
$ python tools/looks/confront.py --outside 2
confront --outside: 0 problem(s) over 1 slot(s)    (13 regiões; help 323/14787, labels 0/16416, values 0/23472)
```

Uma diferença de forma: sem as duas `WE2002_LOOKS_*` exportadas, a primeira
linha pula com saída 77 antes de chegar ao traceback.

### Correção aplicada em 2026-09-23

Os dois lados que a correção pedia, e nessa ordem de durabilidade.

**A recusa cedo.** `tools/pes2/drive.py` ganhou `require_pil()`, que nomeia o
Pillow **e o interpretador** (`sys.executable`) e levanta o `Skip` que o módulo
já usava para PIL ausente. Ela é chamada no `Frame.__init__` — a primeira coisa
que toca o Pillow, e o ponto exato do traceback — e substitui os dois
`if PILImage is None: raise Skip("PIL is missing")` do `self_check` e do
`preflight`, que agora dizem a mesma frase. A mensagem é **genérica**: o
`drive.py` é do projeto PES2 e não sabe o que é o ciclo `looks`. O `PILImage =
None` continua existindo, porque o `mcp_drive.py` o importa por nome.

Em `tools/looks/confront.py`, `_require_pillow()` recusa **antes de subir o
fork**, com a frase que só faz sentido aqui: `run confront.py with the main
python; the venv interpreter is spawned for the window`. Ela roda no `main()`
para os sete comandos que dirigem o emulador (`LIVE`), e não para `--check`,
`--score` e `--render`, que leem PNG sem Pillow.

```text
$ work/venv-looks/Scripts/python.exe tools/looks/confront.py --outside 2
confront FAILED: Pillow is not installed in C:\github\new-we2002-editor\work\venv-looks\Scripts\python.exe
-- run confront.py with the main python; the venv interpreter is spawned for the window   (saída 1, sem
subir o fork; a mesma linha com e sem as duas WE2002_LOOKS_* exportadas)

$ work/venv-looks/Scripts/python.exe tools/pes2/drive.py --self-check
skipping: Pillow (PIL) is not installed in C:\github\new-we2002-editor\work\venv-looks\Scripts\python.exe
-- install it there, or run this tool with an interpreter that has it            (saída 77, como antes)
```

**As linhas de receita.** A coluna do que o `--outside` precisa, no perfil, e a
linha dele na tabela do `CLAUDE.md` deixaram de dizer "o venv" e passam a dizer
que o comando roda no `python` principal — é quem tem Pillow — e que o do venv
é lançado só para a janela.

O caminho verde continua verde, remedido inteiro (~4 min, os mesmos números da
triagem):

```text
$ python tools/looks/confront.py --outside 2
    control: the game photographed twice, the same ground in all 13 region(s)
    help   323 of 14787 differ    labels 0 of 16416    values 0 of 23472
confront --outside: 0 problem(s) over 1 slot(s)                                   (saída 0)
```

Portões: `tools/looks/selftest.py` 0 failure(s) (104 controles vermelhos),
`cli.py check` 12 módulos ok, `rite check --quick --cycle looks` 0 erros — o
perfil ficou a 875 bytes do limite. Do lado do PES2, `drive.py --self-check`
sai `SELF-CHECK OK` no interpretador principal; o `tools/pes2/selftest.py`
inteiro não roda **nesta máquina** por um motivo anterior a isto (lê
`/proc/self/fd`).

Fica para quem passar: o `tools/pes2/mcp_drive.py` ainda tem o seu próprio
`raise Skip("PIL is missing")`, que podia chamar o `drive.require_pil()` e
ganhar o nome do interpretador de graça.
