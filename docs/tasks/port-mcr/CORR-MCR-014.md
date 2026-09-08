---
id: CORR-MCR-014
title: "Correção: as duas varreduras de desenho param no topo, e a `tools/mcr/ui/` que a MCR-TASK-11 vai criar fica invisível para as duas"
type: correção
category: verificação
status: concluído
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

- [x] com o `_probe.py` da Evidência em `tools/mcr/ui/`: `layout.py --rule1`
      acusa **dois** endereços, `glossary.py` acusa o espanhol, e
      `selftest.py` sai `rc=1`
- [x] sem ele: os três verdes, e as contagens de check dos doze módulos
      inalteradas (27, 29, 22, 17, 23, 15, 25, 19, 17, 13, 10, 5)
- [x] `python3 tools/mcr/controls.py` continua **todos vermelhos**, com o
      número novo declarado no Log da task
- [x] `ctest -R mcr` sem cartão = **1 passed, 2 skipped**; com cartão =
      2 passed, 1 skipped
- [x] `make test` verde
- [x] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

O sintoma reproduziu. Com o `_probe.py` da Evidência em `tools/mcr/ui/`,
`layout.py --rule1` deu `0 address(es)`, `glossary.py` deu `0 complaint(s)`, e
o `selftest.py` saiu `rc=0` — as três guardas verdes sobre uma árvore com dois
endereços de save e espanhol dentro.

As duas varreduras descem com `os.walk`, pulando `__pycache__` e o próprio
arquivo, e as queixas passaram a nomear o caminho **relativo** — `ui/_probe.py`
identifica, `_probe.py` não. As duas docstrings dizem por que a descida existe.

**A varredura de discrepância puxou uma terceira, que a CORR dava como boa.** A
tabela do "Problema identificado" credita a Regra 3 do `selftest.py` com
alcançar a `ui/` — e alcança, mas com o mesmo `os.listdir`: um `ui/widgets/`
seria invisível também. É o mesmo defeito, no arquivo que a CORR não listou.
Desceu junto, e nenhum `os.listdir` sobrou nas três.

**Problemas encontrados:**

**1. A Evidência da CORR conta quatro queixas do `glossary.py`, e o arquivo que
ela mostra produz uma.** As duas palavras aparecem lá só como `JUGADOR_X` e
`CANCHA_Y`, e o casamento é `\bjugador\b` — o `_` é caractere de palavra, então
não há fronteira e nenhuma das duas dispara; o que sobra é o acento de
`notação`. A transcrição também põe o acento na linha 1 e as palavras nas 2 e
3, quando o acento está na última. **O sintoma central não depende disso** — as
duas varreduras param no topo, medido —, e a Evidência do revisor fica como
está. O que mudou foi o plantio: o controle usa um comentário onde as palavras
têm fronteira, e aí as três guardas acendem de verdade.

**2. O controle 15 não é substituição, e o motor não sabia criar arquivo.** O
defeito é uma pasta que a varredura não desce; nenhuma troca de linha num
módulo existente exprime isso. O `Control` ganhou `creates`, e ali "casou uma
vez" quer dizer **caminho livre e escrito** — caminho ocupado é controle
quebrado, do mesmo jeito que um literal que casa duas vezes. O `_checks` do
`controls.py` ganhou a asserção espelhada (o caminho de um controle criador tem
de estar livre), e por isso ele passou de 5 para **6** checks: é a única
contagem de módulo que mudou, e mudou de propósito.

**3. O payload literal fez o próprio catálogo tropeçar na varredura que ele
exercita.** Escritas por extenso no `controls.py`, as duas palavras espanholas
davam **2 queixas sobre o `controls.py`**, com o `selftest` vermelho sem nada
plantado. A saída fácil — pular o `controls.py` como o `glossary.py` pula a si
mesmo — deixaria um vazamento de verdade sem vigilância no arquivo mais
propenso a carregá-lo. As palavras passaram a sair do **dicionário do
`glossary.py` em tempo de execução**, o que ainda torna o controle mais forte:
se o dicionário for reescrito, ele continua plantando algo que a varredura tem
de pegar. O acento vai como escape no fonte e sai como letra no arquivo escrito.
Uma segunda passada foi precisa: a docstring que eu escrevera para explicar
isso citava as palavras e o acento por extenso, e tropeçava igual.

**Medições:**

| gate | número |
|---|---|
| o caso vermelho, `_probe.py` em `ui/` | `--rule1` **2 endereços**, `glossary.py` **3 queixas**, `selftest.py` `rc=1` com **7** falhas |
| sem ele | `--rule1` **0**, `glossary.py` **0**, `selftest.py` `rc=0`, `0 failure(s)` sobre 12 módulos |
| `controls.py` | **15 de 15 vermelhos**; o novo, sozinho, 1 de 1 |
| contagens dos 12 módulos | 27, 29, 22, 17, 23, 15, 25, 19, 17, 13, **6**, 10 — só o `controls` mudou (5 → 6), pela asserção nova |
| `ctest -R mcr` sem cartão | **1 passed, 2 skipped** |
| `ctest -R mcr` com cartão (caminho absoluto) | **2 passed, 1 skipped** |
| `make test` | **10/10**, `100% tests passed` |
| fixture | `sha256 e53f4895…c47546`, intocada; `roms/` sem alteração |

**Arquivos criados/modificados:**

- `tools/mcr/layout.py` — `address_monopoly()` desce, e nomeia o caminho relativo
- `tools/mcr/glossary.py` — `sweep()` idem
- `tools/mcr/selftest.py` — a Regra 3 desce também (varredura de discrepância)
- `tools/mcr/controls.py` — o campo `creates`, o décimo quinto controle, o
  payload vindo do dicionário, e a asserção espelhada
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — quinze controles, o escopo
  recursivo das duas varreduras, e o `controls` em 6 checks
- `docs/tasks/port-mcr/05-layout-e-cross-check.md` — o escopo da Regra 1
- `docs/prompts/perfil-mcr.md` — 15 substituições, e a armadilha do controle
  que cria arquivo
- `docs/tasks/port-mcr/progresso.md` — a linha dos controles negativos
