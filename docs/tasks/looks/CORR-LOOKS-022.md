---
id: CORR-LOOKS-022
title: "Correção: os \"2.151 registros a mais em 40 contêineres\" que justificam não tocar o `bin_archive.py` não reproduzem por nenhuma leitura"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-022: o número que decide onde o conserto mora não reproduz

## Problema identificado

A task decidiu a única questão de arquitetura que tinha — **consertar o modelo
de registro no `tools/looks/texture.py` e não no `tools/pes2/bin_archive.py`** —
apoiada num número, e o número aparece duas vezes, atribuído a **dois
mecanismos diferentes**:

No Log, a causa é aceitar qualquer palavra de banco:

> uma regra de varredura geral o bastante para achar esta lista — **aceitar
> qualquer palavra de banco**, validando cada registro pelo que ele declara —
> faz aparecerem **2.151 registros a mais em 40 outros contêineres** deste mesmo
> disco, os estádios `GDC_*` incluídos

No código, a causa é o próprio filtro `plausible()`:

```python
def plausible(fields, size: int) -> bool:
    """Is this eight-field tuple a record, or a coincidence in a stream?

    ...  Without this the same sweep over this disc reports 2,151 more
    "records" in 40 other files, the stadium meshes included.
    """
```

**Nenhuma das duas leituras dá 2.151 em 40**, e a diferença entre elas não é de
arredondamento:

| leitura | registros a mais | contêineres | estádios `GDC_*` |
|---|---:|---:|---:|
| aceitar qualquer banco, com `plausible()` (a do Log) | **80** | **5** | **0** |
| sem `plausible()` inteiro (a do código) | **70.978** | **228** | 34 |
| sem o teste de `kind` de `plausible()`, o resto igual | **197** | **54** | 3 |
| *(afirmado)* | *2.151* | *40* | *incluídos* |

E a leitura do Log é a que decide a questão — é ela que descreve o conserto que
o `bin_archive.py` **receberia**. Medida, ela custa **80 registros a mais em
cinco contêineres**, e nenhum deles é estádio: `DAT_CG.BIN` (41),
`ENDCSR.BIN` (16), `DATSEL2.BIN` (15), `DATSEL.BIN` (6) e `EDTR_2D.BIN` (2).

Isso não desfaz a decisão — mexer no varredor de outro projeto para servir um
arquivo deste continua sendo mudança no chão de um gate alheio, e 80 registros
novos em cinco arquivos ainda são 80. Mas a decisão passa a se justificar por
**outro argumento**, e o argumento escrito é o que a próxima pessoa vai reler
quando a dívida com o ciclo de PES2 voltar à mesa — que a própria task deixou
registrada na [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md).

**Um segundo achado sai da mesma corrida, e ele é sobre o filtro.** Das cinco
condições do `plausible()`, **só o teste de `kind` suprime alguma coisa neste
disco**. Retirar qualquer uma das outras — a forma (`fields[5] == 0`, largura e
altura não-nulas), os limites de VRAM, as regras de CLUT, o `fields[6] < size` —
e mesmo três delas juntas, muda **zero** registros nos 245 arquivos do disco. O
docstring credita ao filtro inteiro uma supressão que, medida, é do primeiro
`if`.

## Evidência

Tudo remedido nesta revisão, chamando o `texture.tables()` commitado sobre os
245 arquivos do disco japonês, trocando só o `plausible()`:

```text
files with >=1 record (strict): 135     total records: 1711

drop size                     extra      0 in   0 file(s)  GDC 0
drop vram                     extra      0 in   0 file(s)  GDC 0
drop clut                     extra      0 in   0 file(s)  GDC 0
drop shape                    extra      0 in   0 file(s)  GDC 0
drop vram+clut                extra      0 in   0 file(s)  GDC 0
drop clut+size                extra      0 in   0 file(s)  GDC 0
drop vram+clut+size           extra      0 in   0 file(s)  GDC 0
kind only (o resto do filtro fora) extra 197 in  54 file(s)  GDC 3
sem plausible() nenhum             extra 70978 in 228 file(s)  GDC 34
```

E a leitura do Log — `tables()` como está contra um `tables()` que só aceite
`tag == 0x800f`, que é o que o `bin_archive.py` faz:

```text
any-bank minus fixed-tag: 347 extra record(s) in 6 file(s)
  excluding /BIN/DAT2D.BIN: 80 extra in 5 file(s)
  GDC files among them: 0
  top: DAT_CG.BIN 41, ENDCSR.BIN 16, DATSEL2.BIN 15, DATSEL.BIN 6, EDTR_2D.BIN 2
```

Não é um número de outro disco: na trilha de dados do PES2 `(EsIt)` a mesma
varredura dá `54.332 em 233` sem o filtro e `180 em 51` só com o teste de
`kind` — também não 2.151 em 40.

**O resto da task reproduz inteiro**, e é o que dá contexto à criticidade: as
267 paletas, o ladrilho `65.892..76.836`, os 262 × 16 e 5 × 256, os nove ids de
CLUT com as contagens somando 2.841, as quatro "Pieles", o "Botines" em
(0, 484), e o banco — que remedi pelo caminho mais forte que existe, o do
próprio Log: com o banco, **23/20/2/15/9/6** imagens dos seis contêineres
descomprimem para o retângulo declarado; sem ele, só as dos dois contêineres de
banco 0.

## Causa raiz

Dois números escritos de memória a partir de uma corrida exploratória que não
ficou como comando, e cada um dos dois lugares atribuiu a supressão a um
mecanismo diferente.

## Correção

### Arquivo: `tools/looks/texture.py`

1. Corrigir o docstring do `plausible()` com o que a medição dá — e dizer o que
   ela revela: **só o teste de `kind` suprime neste disco**, e as outras quatro
   condições estão lá para o registro que este disco não tem, não para o que
   ele tem. Condição que nunca separou nada é candidata a virar asserção ou a
   sair; qualquer dos dois é melhor do que um crédito que não se mede.
2. Deixar a conta **alcançável por comando**, que é o que faltou: um
   `--survey` (ou uma linha do `--report`) que varra os contêineres do disco e
   imprima quantos registros a varredura acha, quantos um `tag` fixo acharia, e
   em quantos arquivos. É uma conta de disco, sem emulador, e é o que impede o
   próximo número de envelhecer em prosa.

### Arquivo: `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md`

O parágrafo "Onde o conserto mora, e por quê" com o número medido — **80
registros a mais em cinco contêineres, nenhum deles estádio** — e a decisão
mantida com o argumento que sobrevive à correção: o `bin_archive.py` é o
varredor de outro projeto, cujo gate não é medido aqui, e o `texture.py` já
entrega o que este ciclo precisa.

### Arquivo: `docs/PLAN-LOOKS-PY.md`

Se a §1.7 ou a §1.8 repetirem o número, corrigir lá também — no lugar, como o
ciclo faz.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/texture.py` | modificar |
| `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [x] o docstring do `plausible()` não credita mais 2.151 a si mesmo, e diz qual
      das condições mede
- [x] existe comando que imprime a conta — `texture.py --survey` —, e o número
      do Log sai dele
- [x] o parágrafo da decisão traz o número medido e os cinco arquivos nomeados
- [x] `python tools/looks/texture.py --check` e `--check-image` continuam verdes
- [x] `python tools/looks/selftest.py` verde, **19 de 19** controles vermelhos
- [x] `tools/pes2/` continua intocado (`git status --short tools/pes2` vazio)
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

O número saiu da prosa e virou comando. `texture.py --survey` varre os 245
arquivos do disco e imprime as três contas que estavam escritas de memória:
quantos registros a varredura acha, quanto custa ler o banco como banco em vez
de casar um tag fixo, e **o que cada uma das cinco condições do `plausible()`
suprime**.

```text
  245 file(s) on the disc, 236 readable
  the sweep as it stands: 1711 record(s) in 135 file(s)
  a fixed tag word would find 1364 -- so reading the bank as a bank costs 347
      record(s) in 6 file(s)
      outside /BIN/DAT2D.BIN: 80 record(s) in 5 file(s) -- DAT_CG.BIN 41,
          ENDCSR.BIN 16, DATSEL2.BIN 15, DATSEL.BIN 6, EDTR_2D.BIN 2
      stadium (GDC*) file(s) among them: 0
  what each condition of plausible() suppresses:
      without kind     +123 record(s), 44 file(s) change
      without shape      +0 record(s), 0 file(s) change
      without vram       +0 record(s), 0 file(s) change
      without clut       +0 record(s), 0 file(s) change
      without size       +0 record(s), 0 file(s) change
      with ONLY kind      +197 record(s)
      with none of them  +70978 record(s)
```

**80 em cinco, nenhum estádio** — não 2.151 em 40. Para o `--survey` poder
soltar uma condição de cada vez, o `plausible()` foi decomposto em cinco testes
nomeados (`CONDITIONS`), e o `tables()` ganhou um `skip`. A lógica é a mesma
linha por linha; o que mudou é poder perguntar a ela.

### A decisão, com o argumento que sobrevive ao número

O conserto continua em `tools/looks/texture.py`, e o `tools/pes2/bin_archive.py`
continua intocado — mas por **escopo**, não por volume: aquele varredor é de
outro projeto, cujo gate (`pes2_selftest`) não é medido por este ciclo, e o
`texture.py` já entrega o que este ciclo precisa. Oitenta registros novos em
cinco arquivos ainda são oitenta, e nenhum deles foi conferido contra nada.

A dívida com o ciclo de PES2 — o campo 7 é banco e não tag — continua escrita
onde estava, na LOOKS-TASK-20 e na §1.7.

### Problemas encontrados

**A tabela da própria CORR tem os dois números de `kind` trocados**, e o
`--survey` mostra por quê: são perguntas diferentes.

- *sem o teste de `kind`, as outras quatro mantidas*: **+123**
- *só o teste de `kind`, as outras quatro fora*: **+197**

A CORR rotula o 197 como "sem o teste de `kind` de `plausible()`, o resto
igual", que é a primeira pergunta e dá 123. A conclusão que ela tira — **só o
`kind` suprime alguma coisa neste disco** — está certa e é o que importa:
soltar qualquer uma das outras quatro, ou três juntas, muda **zero** registros
nos 245 arquivos. O `--survey` imprime as duas leituras lado a lado justamente
para a confusão não voltar.

### Arquivos criados/modificados

- `tools/looks/texture.py` — `CONDITIONS` e os cinco testes nomeados, o `skip`
  do `plausible()`/`tables()`, o `_survey()` e o `--survey`; os docstrings com
  os números medidos
- `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md` — "Onde o conserto mora" com
  a saída do comando e o argumento de escopo
- `docs/PLAN-LOOKS-PY.md` — §1.8, o mesmo número no lugar
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-022.md` — este arquivo
