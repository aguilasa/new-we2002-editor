---
id: CORR-WTE-096
title: "Correção: chave duplicada no GOLDEN_DE apaga o gate do base_teamClick, e o fase-4.md publica \"nenhum\""
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-096: chave duplicada no `GOLDEN_DE` apaga o gate do `base_teamClick`

## Problema identificado

A [WTE-TASK-32](/docs/tasks/concluidos/32-preco-do-jogador.md) criou o
[`golden-22-precos`](../../../wte/tests/roteiros/golden-22-precos.txt) — a régua de
byte da feature de preço — e o registrou no `GOLDEN_DE` do
[`check_fase4.py`](../../../wte/tools/check_fase4.py). **O registro é inerte:** o
dicionário tem `"MainForm.base_teamClick"` **duas vezes**, e em Python a última
ocorrência ganha. A segunda é a entrada velha, da época em que o handler estava
`aberto`, e o valor dela é a tupla vazia.

O efeito é visível no documento gerado: o
[`wte/re/fase-4.md`](../../../wte/re/fase-4.md) publica

```text
| `0x00410ff4` | MainForm.base_teamClick | auxiliar | implementado | **nenhum** |
```

— o único escritor da tabela sem gate — três linhas abaixo da frase que diz
*"handler que a spec diz que grava e não tem linha aqui **aborta** o
fechamento"*. A guarda não abortou porque a chave **existe**; o que ficou vazio
foi o valor, e vazio é renderizado como `**nenhum**` em vez de recusado.

O gate existe e está verde — medido nesta revisão, nos três modos.

## Evidência

A chave duplicada:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
python3 -c "
import ast
from collections import Counter
t = ast.parse(open('wte/tools/check_fase4.py',encoding='utf-8').read())
for n in ast.walk(t):
    if isinstance(n, ast.AnnAssign) and getattr(n.target,'id','')=='GOLDEN_DE':
        k=[x.value for x in n.value.keys]
        print('chaves',len(k),'unicas',len(set(k)),
              [a for a,c in Counter(k).items() if c>1])
"
```

```text
chaves 18 unicas 17 ['MainForm.base_teamClick']
```

O valor que sobrevive:

```text
GOLDEN_DE['MainForm.base_teamClick'] = ()
```

As duas linhas, como estão hoje (`wte/tools/check_fase4.py:189` e `:208`):

```python
    # WTE-TASK-32 -- o preco do time inteiro, a nona rota de escrita.
    "MainForm.base_teamClick": ("golden-22-precos",),
    ...
    # aberto, e o gate vem com o dono -- ver a coluna `pendente` na saida
    "MainForm.base_teamClick": (),
```

E o gate que a tabela diz não existir, rodado em 2026-08-24:

```text
controle: PASSOU: byte-identico
golden:   PASSOU: byte-identico
positivo --plantar 3067450:
  REPROVOU: 1 divergencia(s) que ninguem declarou:
    3067450..3067450  1 byte(s)  data  OFS_COST_NATIONAL+46
  OK: o gate DETECTOU o byte plantado.
```

| Sítio | O que diz | Fonte |
|---|---|---|
| `check_fase4.py:189` | gate = `golden-22-precos` | intenção da WTE-TASK-32 |
| `check_fase4.py:208` | gate = nenhum | resíduo de quando era `aberto` |
| `wte/re/fase-4.md` | **nenhum** | gerado, com o valor efetivo |
| `wte/re/fase-4-golden.tsv` | duas corridas de `golden-22-precos`, PASSOU | a bateria |

## Causa raiz

A entrada nova foi acrescentada no bloco dos escritores sem remover a entrada
antiga do bloco dos `aberto`, e nem o Python nem o gerador reclamam de chave
repetida em literal de dicionário.

## Correção

### Arquivo: `wte/tools/check_fase4.py`

Apagar a segunda ocorrência — o bloco

```python
    # aberto, e o gate vem com o dono -- ver a coluna `pendente` na saida
    "MainForm.base_teamClick": (),
```

que é resíduo duas vezes: o handler não está mais `aberto` (o índice fecha em
96 de 96) e o gate dele existe.

**E fechar a porta**, porque a lição não é sobre esta chave. Duas guardas
baratas, as duas no próprio gerador:

1. **Recusar chave repetida.** O literal já foi lido pelo interpretador quando
   o gerador roda, então a conferência é sobre o fonte:
   `ast.parse(__file__)` e comparar `len(keys)` com `len(set(keys))`, abortando
   com o nome da chave. É o mesmo desenho do `check_seeks()` do
   `port_database_pas.py` — conferir a **fonte**, não o resultado.
2. **Recusar gate vazio para quem grava e está `implementado`.** Hoje a tupla
   vazia vira `**nenhum**` na tabela; ela só faz sentido para handler `aberto`,
   e é isso que a guarda deve exigir. Escritor `implementado` sem roteiro é
   exatamente o buraco que a WTE-TASK-30 pagou para descobrir.

Com as duas, um caso plantado (chave repetida; e escritor `implementado` com
tupla vazia) tem de reprovar — guarda nunca exercitada é guarda ausente.

### Arquivo: `wte/re/fase-4.md`

**Não editar.** É gerado; sai certo quando o gerador for corrigido e
reexecutado.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase4.py` | modificar |
| `wte/tools/test_check_fase4.py` | modificar — os dois casos plantados |
| `wte/re/fase-4.md` | regerar |

## Verificação

- [x] `python3 -c` do bloco de evidência acima imprime `chaves 17 unicas 17 []`
- [x] `grep -n 'base_teamClick' wte/re/fase-4.md` mostra
      `[golden-22-precos](../tests/roteiros/golden-22-precos.txt)`, não `**nenhum**`
      — linha 83 do documento regerado
- [x] O `test_check_fase4.py` reprova com uma chave repetida plantada, e o
      **gerador** também: plantada a segunda entrada, o `--check` sai com
      `ERRO: GOLDEN_DE tem chave repetida: MainForm.base_teamClick`
- [x] O `test_check_fase4.py` reprova com um escritor `implementado` de gate
      vazio, e o gerador idem: `ERRO: escritor 'implementado' sem roteiro em
      GOLDEN_DE: MainForm.base_teamClick`
- [x] `make -C wte check` verde — **764** testes, `OK (skipped=1)`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-24

**Resumo do que foi feito:**

A segunda entrada saiu, e o `fase-4.md` regerado publica o gate na linha do
`base_teamClick`. Nenhum outro número do documento mudou — o diff é de uma
linha.

As duas guardas entraram no próprio gerador, como a correção pedia:

1. **`chaves_repetidas_no_fonte()`** lê o **fonte** com `ast`, não o `dict` em
   memória. Tinha de ser assim: quando o módulo roda, o interpretador já
   colapsou o literal e a duplicata é invisível. É o mesmo desenho do
   `check_seeks()` do `port_database_pas.py`, que confere o legado e não a
   saída;
2. **`gates_vazios()`** recusa tupla vazia em escritor `implementado`. Ela
   continua válida no `aberto`, onde quer dizer "o gate vem com o dono" — e é
   por isso que a guarda pergunta pelo veredito, e não só pela tupla.

Provadas nos dois sentidos, contra o gerador de verdade e não só contra o
teste: com cada plantio o `--check` aborta nomeando a chave; desfeitos os dois,
volta a `check_fase4: wte/re/fase-4.md: ok` e a saída é byte-idêntica em duas
escritas.

**Problemas encontrados:**

1. **Nenhuma das guardas que já existiam podia pegar isto, e vale dizer por
   quê:** as duas — "escritor fora da tabela" e "tabela cita quem não grava" —
   perguntam sobre **chave**, e a chave existia. O que estava vazio era o
   **valor**, e valor vazio era renderizado como `**nenhum**` em vez de
   recusado. A guarda nova é a primeira do arquivo que olha o valor.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase4.py` | modificado — a chave duplicada apagada e as duas guardas |
| `wte/tools/test_check_fase4.py` | modificado — cinco casos, dois deles plantados |
| `wte/re/fase-4.md` | regerado — uma linha |
