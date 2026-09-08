---
id: CORR-MCR-014
title: "Correção: as duas varreduras de desenho param no topo, e a `tools/mcr/ui/` que a MCR-TASK-11 vai criar fica invisível para as duas"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-MCR-014: `os.listdir` no lugar de `os.walk`, nas duas varreduras que julgam a árvore

## Problema identificado

As três guardas de desenho que o `selftest.py` agrega julgam escopos
**diferentes**, e nada no código diz isso:

| guarda | como acha os arquivos | alcança `tools/mcr/ui/`? |
|---|---|---|
| Regra 1 — `layout.address_monopoly()` | `os.listdir(directory)` | **não** |
| idioma — `glossary.sweep()` | `os.listdir(directory)` | **não** |
| Regra 3 — o teste de import do `selftest.py` | varre a pasta `ui/` | sim |

A pasta `tools/mcr/ui/` é criada pela **MCR-TASK-11**, a próxima do ciclo. A
partir dali, a metade da Regra 3 que verifica import continua vendo a UI e as
outras duas param de ver — sem aviso, sem `skip`, sem mudança de contagem. Os
três gates continuam verdes.

É o pior formato possível: a UI é justamente onde a transcrição literal do
WinForms do upstream tem mais chance de trazer espanhol cru, e a Regra 3 do
plano diz em letras que **"a UI não conhece endereço"** — que é o que a Regra 1
existe para medir.

O critério de conclusão desta task escreve o escopo com `**`:

> A varredura de idioma no `selftest`: nenhum espanhol remanescente e nenhuma
> prosa portuguesa em `tools/mcr/**.py`

`**` é recursivo; `os.listdir` não é.

## Evidência

Um arquivo em `tools/mcr/ui/` com endereço de save nas duas notações que a
`address_monopoly()` diz varrer, mais espanhol que está no dicionário:

```python
# tools/mcr/ui/_probe.py
JUGADOR_X = 0x62A8      # FORMATION_XY, um dos 17 destinos
CANCHA_Y = 25266        # 0x62B2 em decimal -- a notação do upstream
```

Resultado, com o arquivo no lugar:

```
$ python3 tools/mcr/layout.py --rule1
layout.py --rule1: 0 address(es) outside layout.py

$ python3 tools/mcr/glossary.py
glossary.py: 0 complaint(s) in .../tools/mcr

$ python3 tools/mcr/selftest.py
mcr selftest: 0 failure(s) over 12 modules plus the design rules

$ ctest --test-dir build -R mcr_selftest
100% tests passed, 0 tests failed out of 1
```

Com prosa em vez de endereço — acento português e duas palavras do dicionário
espanhol no mesmo arquivo — o `selftest` imprime, textualmente:

```
  ok    Rule 3: the UI imports no core module that knows an address
  ok    no Spanish and no Portuguese in tools/mcr/*.py
design rules: 0 failure(s)
```

A primeira linha prova que o `selftest` **viu** a pasta aparecer: ela deixou de
ser `skip  Rule 3: the UI does not exist yet (MCR-TASK-11)`. A segunda diz que
não há espanhol, sobre uma árvore onde há.

E o mesmo arquivo, apontado à mão, é acusado corretamente — as palavras estão
no dicionário, o que falta é o arquivo chegar até ele:

```
$ python3 tools/mcr/glossary.py tools/mcr/ui
_probe.py:1: 'ç' is a Latin accented letter; the code of this port is en-US
_probe.py:2: Spanish 'jugador' -- the port calls it 'player'
_probe.py:3: Spanish 'cancha' -- the port calls it 'pitch'
glossary.py: 4 complaint(s) in tools/mcr/ui
```

## Causa raiz

As duas varreduras enumeram com `os.listdir`, que não desce; o escopo que os
documentos e o critério descrevem é recursivo.

## Correção

### Arquivo: `tools/mcr/layout.py` — `address_monopoly()`

Trocar a enumeração por uma descida, mantendo as duas exclusões que existem (o
próprio `layout.py`, e `__pycache__`):

```python
    for root, dirs, names in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(names):
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            if os.path.samefile(path, __file__):
                continue
            rel = os.path.relpath(path, directory)
            ...          # `rel` no lugar de `name` nas mensagens
```

O `rel` importa: com a descida, `app.py` sozinho deixa de identificar o
arquivo — `ui/app.py` identifica.

### Arquivo: `tools/mcr/glossary.py` — `sweep()`

A mesma descida, com a mesma exclusão do próprio arquivo e o mesmo `rel` nas
queixas.

### O caso vermelho, que é o que fecha esta correção

Plantar o `_probe.py` da Evidência em `tools/mcr/ui/` e exigir que **os três**
saiam vermelhos: `--rule1` com dois endereços, `glossary.py` com as queixas de
espanhol, e o `selftest.py` com falha nomeada. Depois removê-lo.

Vale registrar isso como **controle** em `controls.py`, junto dos catorze —
é a única forma de o caso continuar exercitado depois que a `ui/` existir de
verdade e o plantio à mão deixar de ser possível sem sujar a árvore.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/layout.py` | modificar |
| `tools/mcr/glossary.py` | modificar |
| `tools/mcr/controls.py` | modificar (o décimo quinto controle) |
| `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` | modificar (a contagem de controles) |

## Verificação

- [ ] com o `_probe.py` da Evidência em `tools/mcr/ui/`: `layout.py --rule1`
      acusa **dois** endereços, `glossary.py` acusa o espanhol, e
      `selftest.py` sai `rc=1`
- [ ] sem ele: os três verdes, e as contagens de check dos doze módulos
      inalteradas (27, 29, 22, 17, 23, 15, 25, 19, 17, 13, 10, 5)
- [ ] `python3 tools/mcr/controls.py` continua **todos vermelhos**, com o
      número novo declarado no Log da task
- [ ] `ctest -R mcr` sem cartão = **1 passed, 2 skipped**; com cartão =
      2 passed, 1 skipped
- [ ] `make test` verde
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
