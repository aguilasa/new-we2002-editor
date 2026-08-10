---
id: CORR-WTE-049
title: "Correção: o parágrafo de dependência da WTE-TASK-20 troca as duas populações de offset, e cita a 19 como bloqueada"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-049: os 36 "que o `we2002_core` não tem" são justamente os que ele tem

## Problema identificado

A seção **"A dependência da WTE-TASK-19 é a parte que já veio"** do enunciado da
[WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) justifica por que a task
seguiu com a 19 em aberto. O argumento é bom e a decisão está certa — nenhum dos
seis critérios da 20 toca o oráculo A. O texto é que tem dois defeitos.

**1. Ele troca duas populações de offset.** Diz:

> Os 36 restantes são exatamente os que o `we2002_core` **não tem** — não podem
> aparecer num diff de dump Pascal × dump C++ nem se estivessem medidos, porque
> não há lado C++ para eles.

Os "36 restantes" saem dos **50 `OFS_*` que a WTE-TASK-06 marcou `ausente`**, e
esses 50 são nomes do **nosso** `src/core/include/we2002/Offsets.hpp` — a
tabela de vereditos do
[`offsets-novos.md`](../../wte/re/offsets-novos.md) tem `Offsets.hpp` como
primeira coluna. `ausente` ali quer dizer *não casa com a tabela em `.data` do
`wte.exe`*, não *falta no `we2002_core`*. Existe **lado C++ para todos os 50**.

Quem o `we2002_core` de fato não tem são as **faixas sem dono** — regiões que o
`wte.exe` endereça e nenhum `OFS_*` explica, como a região do uniforme em
`21168024..21203815`. A frase descreve essa população e aponta para a outra.

**2. O status e os números estão vencidos.** O parágrafo abre dizendo que a
WTE-TASK-19 está `❌ Bloqueado`; ela está **✅ Concluído** desde 2026-08-10, e o
`progresso.md` registra a passagem `❌` → `🔄` → `✅` no mesmo dia. Os números
seguiram junto: **28 confirmados por execução** virou **33 endereçados**, e os
**36 restantes** viraram **17**, todos com veredito estrutural tirado do
`Database.cpp`.

Nada disso muda o resultado da WTE-TASK-20 — o dump é Pascal × C++ sobre o mesmo
`Offsets.hpp`, e a cobertura dos 50 não entra na conta em nenhum dos dois
sentidos. O que muda é o que o leitor conclui: o parágrafo é a única explicação
escrita de por que a 20 rodou antes de a 19 fechar, e hoje ele explica com um
status falso e uma categoria trocada.

## Evidência

O texto, em `docs/tasks/20-round-trip-headless.md:25-38`:

```
A [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) está
`❌ Bloqueado` — o `wte.exe` morre ao trocar de time, e dois dos seis critérios
dela dependem disso.
...
O que a 20 precisaria da 19 são os offsets novos, e esses vieram: **28
confirmados por execução**, 14 deles antes classificados como `ausente`. Os 36
restantes são exatamente os que o `we2002_core` **não tem** [...]
```

O estado real da 19, no `progresso.md`:

```
| [WTE-TASK-19](...) | Os offsets que o Obocaman tem e nós não | 3 | 06, 18 | ✅ Concluído | 2026-08-10 | 2026-08-10 |
```

E o que os 50 são, medido:

```
$ awk '/## Os 50, um a um/,0' wte/re/offsets-novos.md | grep "^| \`OFS_" | awk -F'|' '{print $4}' | sort | uniq -c
      3  base de varredura
     33  endereçado
     14  retomada de fronteira

$ grep -c "OFS_PLAYER_ATTR_1\b" src/core/include/we2002/Offsets.hpp
1
```

Os 50 estão todos no `Offsets.hpp`, e portanto todos têm lado C++ no dump.

## Causa raiz

O parágrafo foi escrito com o estado de 2026-08-10 pela manhã e descreve a
população das *faixas sem dono* usando o nome da população dos *50 `ausente`*.

## Correção

### Arquivo: `docs/tasks/20-round-trip-headless.md`

Reescrever a seção, mantendo o argumento (que é válido) e trocando o que está
errado:

- a 19 está **concluída**; o que a 20 antecipou foi a ordem, não o resultado — o
  `progresso.md` já registra isso em "A WTE-TASK-20 foi executada antes de a 19
  fechar", e o enunciado deve apontar para lá em vez de repetir estado;
- separar as duas populações por nome: os **50 `OFS_*` `ausente`** (todos no
  `Offsets.hpp`, todos com lado C++, e por isso **todos** dentro do dump desta
  task) e as **faixas sem dono** (o que o `we2002_core` não nomeia, e sobre o
  que esta task realmente não pode afirmar cobertura);
- os números correntes, se forem repetidos: 33 endereçados, 17 com veredito
  estrutural.

A ressalva final — *"o que **não** pode acontecer é esta task afirmar cobertura
sobre eles"* — continua valendo, e passa a valer sobre a população certa.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/20-round-trip-headless.md` | modificar |

## Verificação

- [x] o enunciado não afirma status de outra tarefa que o `progresso.md`
      contradiga — `grep -n "Bloqueado" docs/tasks/20-round-trip-headless.md`
      sai vazio (`rc=1`)
- [x] a frase sobre "não há lado C++ para eles" só se refere às faixas sem dono
- [x] `python3 wte/tools/check_fase1.py --check` verde — *0 sitio com numero
      velho*
- [x] `make -C wte check` verde — 383 testes, `rc=0`
- [x] nenhuma célula do `progresso.md` alterada — `git status --short
      docs/tasks/progresso.md` vazio

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A seção foi reescrita mantendo o argumento — a WTE-TASK-20 rodou antes de a 19
fechar porque nenhum dos seis critérios dela toca o oráculo A — e trocando as
três coisas erradas:

1. **Status.** Em vez de repetir o estado da 19 (que já estava vencido pela
   segunda vez), o texto aponta para a nota do `progresso.md`, *"A WTE-TASK-20
   foi executada antes de a 19 fechar"*, que é onde a decisão está registrada.
   Repetir status de outra tarefa é o que faz o parágrafo envelhecer sozinho.
2. **As duas populações, separadas por nome.** Os **50 `OFS_*` `ausente`** são
   todos nomes do `src/core/include/we2002/Offsets.hpp` — têm lado C++ e
   **entram** no dump desta task; `ausente` quer dizer *não casa com a tabela
   em `.data` do `wte.exe`*. As **faixas sem dono** são a população sobre a
   qual a task não pode afirmar cobertura, e é a elas que a frase "não há lado
   C++ para eles" se aplica. A região da camisa (`21168024..21203815`) entrou
   como o exemplo concreto.
3. **Números correntes:** 33 endereçados e 17 com veredito estrutural (14
   `retomada de fronteira` + 3 `base de varredura`), medidos na tabela do
   `offsets-novos.md`, no lugar de 28 / 36.

**Problemas encontrados:**

A primeira redação fechava dizendo que as faixas sem dono *"voltam pela
CORR-WTE-044 ou pela WTE-TASK-32"* — herdando o "voltam pela 19 ou pela
CORR-WTE-044" do texto velho. A CORR-WTE-044 está **concluída** desde
2026-08-10: apontar uma correção fechada como rota de trabalho futuro é
exatamente o defeito que esta CORR existe para consertar, só que com outro
alvo. Ficou só a [WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md), que o
`progresso.md` já declara dona da região da camisa.

**Arquivos criados/modificados:**

- `docs/tasks/20-round-trip-headless.md` — a seção "A dependência da
  WTE-TASK-19 é a parte que já veio"
