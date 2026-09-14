---
id: CORR-LOOKS-001
title: "Correção: a raiz do Superpack tem treze pastas de jogo, não catorze"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-LOOKS-001: a raiz do Superpack tem treze pastas de jogo, não catorze

## Problema identificado

Três arquivos afirmam que a raiz `C:\games\we2002\Superpackv6\` tem **catorze**
pastas de jogo. São **treze** — a décima quarta linha da saída do
`superpack_count.py` é o arquivo `Cronologia We-Pes-IssPro.htm`, que a
ferramenta lista como entrada de topo e não como pasta.

O erro é da própria LOOKS-TASK-01, que existia para remedir os números do
Superpack: as catorze **linhas** da saída viraram catorze **pastas** ao serem
transcritas.

Onde ele está:

| arquivo | o que diz |
|---|---|
| `NOTICE.md`, tabela da seção *"Lineage of the appearance viewer"* | *"spanning fourteen games of the ISS/PES/WE line"* |
| `docs/PLAN-LOOKS-PY.md` §2 | *"repartidos em catorze pastas de jogo (`Iss1`, … `We4`) mais um `.htm` de cronologia"* |
| `docs/tasks/looks/01-base-legal-e-linhagem.md`, Log | *"em catorze pastas de jogo da linha ISS/PES/WE"* |

A frase do plano se desmente sozinha: ela diz "catorze" e em seguida **lista
treze nomes**, e ainda soma o `.htm` por fora.

Nenhuma leitura do número fecha em catorze: são treze pastas, e **onze** jogos
distintos, porque `We2000 1st`, `We2000 2nd` e `We2000 u23` são três pastas do
mesmo jogo.

## Evidência

```
$ python tools/looks/superpack_count.py "C:/games/we2002/Superpackv6"
Cronologia We-Pes-IssPro.htm        1 files          76552 B
Iss1                               67 files        2726085 B
...
We4                               144 files       27976934 B
--------------------------------------------------------------
TOTAL                           31790 files     4830420054 B  (4.50 GiB)
```

Catorze linhas, das quais uma é arquivo. Separando por tipo:

```
$ python -c "import os; r='C:/games/we2002/Superpackv6'; \
d=[e for e in sorted(os.listdir(r)) if os.path.isdir(os.path.join(r,e))]; \
print(len(d), d)"
13 ['Iss1', 'Iss2', 'Iss98', 'Mls', 'Pes1', 'Pes2', 'We2000 1st',
    'We2000 2nd', 'We2000 u23', 'We2001', 'We2002', 'We3', 'We4']
```

Os outros números da task **batem** e foram reproduzidos nesta revisão:
31.790 arquivos, 4.830.420.054 B na raiz; 28.720 arquivos e 4.452.185.957 B na
linha `We2002`.

## Causa raiz

A contagem de pastas foi lida do número de linhas da saída, e a saída lista
também os arquivos de topo.

## Correção

### Arquivo: `NOTICE.md`

Na linha do Superpack da tabela, trocar *"spanning fourteen games of the
ISS/PES/WE line"* por *"spanning thirteen folders of the ISS/PES/WE line"* —
"folders", não "games", porque as três pastas `We2000 *` são um jogo só.

### Arquivo: `docs/PLAN-LOOKS-PY.md` §2

Trocar *"repartidos em catorze pastas de jogo"* por *"repartidos em treze
pastas"*, mantendo a lista dos treze nomes e o `.htm` por fora, como já está.

### Arquivo: `docs/tasks/looks/01-base-legal-e-linhagem.md`

Corrigir a mesma frase no Log, com a nota de que a revisão a remediu.

**A mensagem do commit `90287ca` também diz "fourteen"**, e não se reescreve:
histórico é registro do que se afirmou.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `NOTICE.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/01-base-legal-e-linhagem.md` | modificar |

## Verificação

- [ ] `python tools/looks/superpack_count.py "C:/games/we2002/Superpackv6"` e o
      `os.listdir` acima concordam com o número escrito nos três arquivos
- [ ] `python tools/check_tasks.py` verde
- [ ] a conferência de links do `.claude/rules/links.md` sai vazia
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
