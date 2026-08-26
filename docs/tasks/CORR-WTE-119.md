---
id: CORR-WTE-119
title: "Correção: o nativo.md repete os sete valores do nativo.tsv e nada amarra os dois"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-119: a evidência da condição 3 não tem `--check`

## Problema identificado

A [WTE-TASK-40](/docs/tasks/40-verificacao-final.md) mediu a condição 3 com
ferramenta — o [`nativo_check.sh`](../../wte/tools/nativo_check.sh) escreve as
sete medidas em [`nativo.tsv`](../../wte/re/nativo.tsv) — e escreveu o
[`nativo.md`](../../wte/re/nativo.md) à mão, declarando isso no topo:

> **Escrito à mão; todo número vem de ferramenta.**

A primeira metade é verdade; a segunda **não é conferida por nada**. O `.md`
**repete os sete valores** do `.tsv` numa tabela própria, e nenhuma ferramenta
compara as duas. O `make -C wte check` não alcança nenhum dos dois: o
`GENERATORS` do `Makefile` é `wildcard tools/*.py`, e o `nativo_check.sh` é
shell, sem `--check`.

Consequência: uma corrida futura que mude um valor — `56 bibliotecas` viram 58
ao trocar de GTK, a janela muda de tamanho, o número de cargas muda — atualiza o
`.tsv` e deixa o `.md` afirmando o valor velho, **em verde**. É a prosa vencida
de novo, e desta vez no documento que sustenta uma das três condições da §0.

O projeto já resolveu isto duas vezes, e do mesmo jeito: o `divergencias.md`
também é escrito à mão, e ganhou o
[`check_divergencias.py`](../../wte/tools/check_divergencias.py) para amarrar o
que dá para amarrar ([CORR-WTE-106](/docs/tasks/CORR-WTE-106.md)). O
`buffers.md` e o `golden.md` nascem de gerador com `--check`. O `nativo.md` é o
único documento de fechamento sem nenhum dos dois.

## Evidência

Os sete valores, duplicados:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
cat wte/re/nativo.tsv
grep -n '^| `' wte/re/nativo.md
```

```text
medida	valor	veredito
formato	ELF 64-bit x86-64	ok
ldd-wine	0 de 56 bibliotecas	ok
ldd-32	0 de 56 bibliotecas	ok
guarda	wine/wine64/wineserver ausentes	ok
janela	522x475, titulo conferido	ok
carga	3 cargas de time para 3 teclas	ok
maps	0 mapeamentos de Wine ou 32 bits	ok

56:| `formato` | ELF 64-bit x86-64 | ok |
57:| `ldd-wine` | 0 de 56 bibliotecas | ok |
58:| `ldd-32` | 0 de 56 bibliotecas | ok |
59:| `guarda` | `wine`/`wine64`/`wineserver` ausentes no namespace | ok |
60:| `janela` | 522×475, título conferido | ok |
61:| `carga` | 3 cargas de time para 3 teclas | ok |
62:| `maps` | 0 mapeamentos de Wine ou 32 bits | ok |
```

E ninguém confere:

```bash
ls wte/tools/check_nativo.py 2>&1
grep -c "nativo" wte/Makefile
```

```text
ls: cannot access 'wte/tools/check_nativo.py': No such file or directory
0
```

**A medição em si reproduz** — rodada nesta revisão sobre uma cópia da ROM
japonesa, com o prefixo instalado dentro do namespace:

```text
formato      ok        ELF 64-bit x86-64
ldd-wine     ok        0 de 56 bibliotecas
ldd-32       ok        0 de 56 bibliotecas
guarda       ok        wine/wine64/wineserver ausentes
janela       ok        522x475, titulo conferido
carga        ok        3 cargas de time para 3 teclas
maps         ok        0 mapeamentos de Wine ou 32 bits

>> condicao 3: as 7 medidas passaram.
```

O TSV que ela produziu é **idêntico** ao commitado (`diff` vazio). O problema
não é o número de hoje; é não haver quem o defenda amanhã.

| Documento de fechamento | Como o número é defendido |
|---|---|
| `fase-1..4.md`, `golden.md`, `buffers.md`, `carregado.md`, `retorno.md` | gerador com `--check` |
| `divergencias.md` | escrito à mão + `check_divergencias.py` |
| **`nativo.md`** | **nada** |

## Causa raiz

A condição 3 ganhou ferramenta de **medição** e não ganhou ferramenta de
**conferência**, e o documento que a publica repete os valores à mão.

## Correção

### Arquivo: `wte/tools/check_nativo.py` *(criar)*

No molde do `check_divergencias.py`: lê o `nativo.tsv`, lê a tabela do
`nativo.md`, e **aborta** quando

1. uma medida do TSV não aparece no `.md`, ou o valor/veredito diferem;
2. o `.md` cita uma medida que o TSV não tem;
3. alguma linha do TSV tem veredito diferente de `ok` — a condição 3 é do
   fechamento, e um `reprovou` que ficou no arquivo tem de derrubar o gate, não
   esperar leitura.

Como é `tools/*.py`, ele entra sozinho no `make -C wte check` pelo `wildcard`.

### Arquivo: `wte/tools/test_check_nativo.py` *(criar)*

As três recusas plantadas, que é o que esta casa cobra desde a
[CORR-WTE-106](/docs/tasks/CORR-WTE-106.md): valor divergente, medida a mais no
`.md`, e veredito `reprovou` no TSV.

**Vale medir junto a guarda do [`sem_wine.sh`](../../wte/tools/sem_wine.sh)**,
que também não tem teste: rodar o script com um alvo fora da lista de máscaras e
exigir a recusa. Feito à mão nesta revisão, ela sai como
`ERRO: /home/ingmar/.var/app/com.usebottles.bottles nao ficou vazio` — o caso
existe, só não está versionado.

### Alternativa mais barata, se o `.md` não precisar da tabela

Tirar a tabela do `nativo.md` e deixá-lo apontar para o `nativo.tsv`. Sem
duplicata não há o que divergir. Perde-se a leitura de uma página só, que é o
que os outros documentos de fechamento oferecem — por isso a recomendada é a
primeira.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_nativo.py` | criar |
| `wte/tools/test_check_nativo.py` | criar |
| `wte/re/nativo.md` | modificar, se a tabela mudar de forma |
| `wte/tools/README.md` | modificar — a ferramenta nova na tabela |

## Verificação

- [ ] `python3 wte/tools/check_nativo.py --check` verde sobre a árvore de hoje
- [ ] Um valor plantado no `.md` diferente do `.tsv` faz o `--check` sair 2
- [ ] Um veredito `reprovou` plantado no TSV faz o `--check` sair 2
- [ ] `make -C wte check` alcança a ferramenta nova (ela é `tools/*.py`)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
