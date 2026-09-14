---
id: CORR-LOOKS-009
title: "Correção: a varredura da regra 1 não tem caso vermelho, e nada diz quanto ela varreu"
type: correção
category: verificação
status: pendente
depends_on: []
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

- [ ] `python tools/looks/layout.py --check` verde, agora com o caso vermelho da
      varredura (os cinco sub-casos acima)
- [ ] `python tools/looks/layout.py --sweep` diz quantos arquivos e linhas
      varreu, e continua achando zero na árvore real
- [ ] plantar um `0x8011C000` num módulo qualquer de `tools/looks/` faz o
      `--sweep` sair != 0 (controle manual, não commitado)
- [ ] a 06 tem por critério reusar o `sweep_addresses()`
- [ ] `python tools/looks/iso_source.py --check` continua verde
- [ ] `python tools/check_tasks.py` verde

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
