---
id: CORR-LOOKS-009
title: "Correção: a varredura da regra 1 não tem caso vermelho, e nada diz quanto ela varreu"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-03
severity: high
done_on: 2026-09-14
done_commit: f6db86f
---

# CORR-LOOKS-009: a varredura da regra 1 não tem caso vermelho, e nada diz quanto ela varreu

## Problema identificado

O `sweep_addresses()` do `tools/looks/layout.py` é o que faz a **regra 1** do
plano — só `layout.py` carrega endereço — ser conferida em vez de prometida. É
a peça certa, e ela é a única coisa do módulo **sem caso vermelho**.

O `self_check()` do `layout.py` tem sete casos vermelhos, uma varredura de
dicas e uma de coerência entre tabelas. Nenhum deles toca o
`sweep_addresses()`:

```
$ grep -n "sweep" tools/looks/layout.py
...
482:def sweep_addresses(root: str | None = None) ...
555:def _sweep(root: str | None = None) -> int:
571:    if len(argv) == 2 and argv[1] == "--sweep":
```

Nenhuma ocorrência dentro do `self_check()`. O `--sweep` só é rodado contra a
árvore de verdade, que hoje está limpa — então ele **só é observado verde**.
Uma varredura que nunca foi vista achando nada é indistinguível de uma
varredura quebrada:

- o filtro é `name.endswith(".py")`. Se ele parar de casar, a saída é
  `no address outside layout.py`;
- o `_strip_strings_and_comments()` blanqueia demais numa linha esquisita, e a
  saída é `no address outside layout.py`;
- a raiz resolve para pasta errada — `os.walk` sobre pasta vazia não levanta
  nada —, e a saída é `no address outside layout.py`.

Nos três casos o comando sai 0, imprimindo a frase que quem lê entende como
"a regra 1 está sendo cumprida". É o contrato que o perfil deste ciclo nomeia:
*"nenhum alvo pode passar sem ter medido"*.

Duas coisas agravam:

1. **A varredura não diz quanto varreu.** Não há contagem de arquivos nem de
   linhas na saída, então o caso "varreu zero" e o caso "varreu tudo e está
   limpo" imprimem o mesmo texto. É a mesma falha que a
   [`CORR-LOOKS-003`](/docs/tasks/looks/CORR-LOOKS-003.md) fechou no
   `superpack_count.py`, e o critério da
   [`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md) já
   diz a regra em geral: *"a contagem é impressa pela ferramenta, nunca escrita
   em prosa"*.
2. **Nenhum alvo roda o `--sweep`.** O `looks_selftest` nasce na LOOKS-TASK-06,
   e o critério dela — *"as três regras de desenho da §3.3 varridas
   mecanicamente, com `os.walk`"* — **não nomeia** o `sweep_addresses()`. Ele
   autoriza escrever um segundo varredor, e aí ficam dois: um que isenta o
   `layout.py` e outro que talvez não, com o `--sweep` virando código morto. É
   a mesma forma da [`CORR-LOOKS-005`](/docs/tasks/looks/CORR-LOOKS-005.md) —
   peça correta, sem contrato que a torne inevitável.

## Evidência

A varredura **funciona**: plantada uma árvore com endereço, ela acha, enxerga
subpasta e respeita o escape (medido nesta revisão, em `tempfile`):

```
caught: ('bad.py', 1, 'BASE = 0x8011C000')
caught: ('ui\deep.py', 1, 'OFFSET = 157164')
```

`ok.py` (com `# not-an-address:`) e `layout.py` ficaram de fora, como devem.
**Este é justamente o teste que deveria estar no `self_check()` e não está** —
esta revisão teve de escrevê-lo à mão, e ele não fica.

Contra a árvore real:

```
$ python tools/looks/layout.py --sweep
layout --sweep: no address outside layout.py
```

Mesma frase que sairia de uma varredura que não abriu arquivo nenhum.

De quebra, uma fresta pequena da mesma função: a isenção do dono é por **nome
de arquivo** (`name == ADDRESS_OWNER`, com `ADDRESS_OWNER = "layout.py"`), e o
`os.walk` desce em subpasta — então um `tools/looks/ui/layout.py`, se algum dia
existir, sai da varredura de graça. Comparar o caminho relativo à raiz fecha
isso em uma linha.

## Causa raiz

A varredura foi escrita como comando e não como caso do `self_check()`, então
nunca foi observada ficando vermelha por um teste que fica na árvore.

## Correção

### Arquivo: `tools/looks/layout.py`

1. **Caso vermelho no `self_check()`**, sobre uma árvore sintética em
   `tempfile` — é o que os outros sete casos já fazem, e roda sem imagem, sem
   venv e sem display:
   - um `.py` com literal hexadecimal → **achado**;
   - um `.py` em subpasta com decimal de quatro dígitos → **achado** (é o que
     prova o `os.walk`, e o ciclo do `.mcr` perdeu uma pasta inteira por
     `os.listdir`);
   - um `.py` com `# not-an-address:` na mesma linha → **não** achado;
   - a anotação escrita na linha **de cima** → achado, porque o escape é por
     linha e isso já enganou uma vez;
   - um `layout.py` sintético com endereço → **não** achado.
2. **Contagem na saída:** `layout --sweep: no address outside layout.py (N
   file(s), M line(s) swept)`. Varredura que não abriu arquivo passa a ser
   visível, e a linha vira a evidência que o Log copia.
3. **A isenção do dono por caminho, não por nome** — comparar contra o caminho
   relativo à raiz, para subpasta homônima não sair de graça.

### Arquivo: `docs/tasks/looks/06-harness-controles-e-selftest.md`

Acrescentar ao critério: o agregador **reusa o `layout.sweep_addresses()`**
para a regra 1, não escreve um segundo varredor, e o `looks_selftest` falha se
ele achar alguma coisa. Dois varredores da mesma regra divergem em silêncio, e
o que sobra sem chamador vira código morto que ninguém percebe apodrecer.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |
| `docs/tasks/looks/06-harness-controles-e-selftest.md` | modificar |

## Verificação

- [x] `python tools/looks/layout.py --check` verde, agora com o caso vermelho da
      varredura (os cinco sub-casos acima)
- [x] `python tools/looks/layout.py --sweep` diz quantos arquivos e linhas
      varreu, e continua achando zero na árvore real
- [x] plantar um `0x8011C000` num módulo qualquer de `tools/looks/` faz o
      `--sweep` sair != 0 (controle manual, não commitado)
- [x] a 06 tem por critério reusar o `sweep_addresses()`
- [x] `python tools/looks/iso_source.py --check` continua verde
- [x] `python tools/check_tasks.py` verde

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

As três partes.

**1. Caso vermelho 8**, sobre uma árvore plantada em `tempfile` — sem imagem,
sem venv, sem display, como os outros sete. São seis arquivos e cada um prova
uma coisa:

| plantado | esperado | o que prova |
|---|---|---|
| `bad.py` com `0x8011C000` | achado | o literal hexadecimal |
| `ui/deep.py` com `157164` | achado | o decimal, **e que o `os.walk` desce** |
| `ok.py` com `# not-an-address:` na linha | **não** achado | o escape funciona |
| `above.py` com a anotação na linha **de cima** | achado | o escape é por linha |
| `layout.py` na raiz, com endereço | **não** achado | o dono é isento |
| `ui/layout.py`, com endereço | **achado** | a isenção é por caminho |

**2. A contagem na saída.** `sweep_addresses()` ganhou um parâmetro `stats`
opcional — o mesmo padrão que a
[`CORR-LOOKS-003`](/docs/tasks/looks/CORR-LOOKS-003.md) usou no
`superpack_count.py` —, e o `--sweep` imprime:

```
layout --sweep: no address outside layout.py (2 file(s), 500 line(s) swept)
```

Varredura que não abriu arquivo nenhum passou a ser **visível**, em vez de
imprimir a mesma frase de uma árvore limpa. O `self_check()` exige isso nos dois
sentidos: `stats["files"] == 5` e `stats["lines"] == 6` na árvore plantada, e
`{"files": 0, "lines": 0}` numa pasta vazia.

**3. A isenção do dono por caminho**, `os.path.relpath(path, root) ==
ADDRESS_OWNER` em vez de `name ==`. A fresta que a CORR nomeou está fechada e
tem caso vermelho.

Gates e controles, nesta máquina:

```
$ python tools/looks/layout.py --check
layout: self_check ok                                              (exit 0)
$ python tools/looks/layout.py --sweep
layout --sweep: no address outside layout.py (2 file(s), 500 line(s) swept)
$ python tools/looks/iso_source.py --check
iso_source: self_check ok
```

**Três controles**, nenhum commitado. O primeiro troca `.py` por `.pyx` no
filtro — a varredura para de achar, e o caso novo pega:
`AssertionError: set()`. O segundo devolve a isenção para `name ==` — e o caso
pega o `ui/layout.py` escapando:
`AssertionError: {('above.py', 2), ('bad.py', 1), ('ui\deep.py', 1)}`. O
terceiro é o da CORR: um `PLANTED = 0x8011C000` acrescentado ao
`iso_source.py` real, e o comando sai **1**:

```
  iso_source.py:297: PLANTED = 0x8011C000
layout --sweep: 1 line(s) carrying an address outside layout.py (2 file(s), 502 line(s) swept)
```

O arquivo foi restaurado e o `git status` confirmou árvore igual à commitada
antes de qualquer `git add`.

**4. O contrato da 06.** A
[`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md) ganhou
dois itens: o agregador **reusa** o `layout.sweep_addresses()` em vez de
escrever um segundo varredor, e o `looks_selftest` falha se ele achar alguma
coisa, com a linha da contagem copiada para o Log. Sem isso o `--sweep` viraria
código morto ao lado de um varredor concorrente — a mesma forma da
[`CORR-LOOKS-005`](/docs/tasks/looks/CORR-LOOKS-005.md).

**Problemas encontrados:**

A varredura de discrepância achou a §4.5 do plano dizendo **quatro** casos
vermelhos. São **oito** — a contagem já estava atrasada em três desde a
LOOKS-TASK-03, que acrescentou os de `derive_base()` sem remedir a frase, e o
caso 8 desta CORR seria o quinto erro em cima. Os oito estão enumerados agora, e
a seção diz por que **dois** deles são varredura e não caso de propriedade: a
falha que fecham é por omissão. O parágrafo do `--sweep` ganhou a contagem e a
regra da isenção por caminho.

Duas menções a "três casos vermelhos" ficaram: as duas do Log da
[`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md), que
registram o que aquela execução entregou. Pelo mesmo motivo, a transcrição do
`--sweep` no Log da LOOKS-TASK-03 continua sem a contagem — é a saída da corrida
que a produziu.

**Arquivos criados/modificados:**

- `tools/looks/layout.py` — caso vermelho 8, `stats` no `sweep_addresses()`,
  isenção por caminho, e a contagem no `_sweep()`
- `docs/tasks/looks/06-harness-controles-e-selftest.md` — dois itens de critério
- `docs/PLAN-LOOKS-PY.md` — §4.5, a contagem de casos vermelhos e o `--sweep`
- `docs/tasks/looks/CORR-LOOKS-009.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
