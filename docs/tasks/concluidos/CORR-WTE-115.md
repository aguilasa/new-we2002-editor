---
id: CORR-WTE-115
title: "Correção: o check_carregado.py aborta e não tem teste, enquanto o irmão nascido no mesmo commit tem"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-115: o `check_carregado.py` não tem par de teste

## Problema identificado

A [WTE-TASK-37](/docs/tasks/concluidos/37-reconferencia-de-ui.md) criou **dois**
conferidores no mesmo commit. Um deles ganhou teste, o outro não:

| Ferramenta | Recusa que implementa | `test_*.py` |
|---|---|---|
| `check_retorno.py` | `Default`/`Cancel`/ordem de tabulação | **`test_check_retorno.py`** |
| `check_carregado.py` | alcance, tamanho de captura, cor de fundo | **não existe** |

E o `check_carregado.py` é o que tem a recusa mais fácil de quebrar sem
ninguém ver — o Log da task a descreve como achado:

> A moldura do Wine é 6×32 e é preciso saber disso para medir qualquer coisa.
> […] o `check_carregado.py` **aborta** se uma captura não for nem o cliente
> nem o cliente mais a moldura — a alternativa era medir 3 px à esquerda do
> lugar e publicar o resultado.

É a mesma situação que a [CORR-WTE-106](/docs/tasks/concluidos/CORR-WTE-106.md) abriu para
o `check_divergencias.py` uma task antes, e que já foi executada: *recusa vista
sem artefato é afirmação sobre o passado.*

**A recusa funciona — foi exercitada nesta revisão.** O que falta é mantê-la
exercitada.

## Evidência

O que não existe:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
ls wte/tools/test_check_carregado.py wte/tools/test_check_retorno.py
```

```text
ls: cannot access 'wte/tools/test_check_carregado.py': No such file or directory
wte/tools/test_check_retorno.py
```

A recusa da moldura, plantada em 2026-08-25 sobre um espelho da árvore em
`/tmp` (o repositório não foi tocado) — uma captura encolhida em **um** pixel:

```text
antes:  (135, 153)
depois: (134, 153)

EXIT=2
check_carregado: oraculo/ficha_dorsal.png: a captura mede 134x153 e o cliente
do DFM mede 129x121 -- nao e nem um nem o outro mais a moldura 6x32.
Coordenada de controle sobre essa captura mediria o lugar errado.
```

Antes da plantação, o mesmo espelho fechava verde:

```text
check_carregado: wte/re/carregado.tsv: ok
check_carregado: 18 formularios, 15 fotografados dos dois lados
```

## Causa raiz

Dos dois conferidores escritos na mesma passagem, só o `check_retorno.py`
ganhou o par de teste que a família toda tem.

## Correção

### Arquivo: `wte/tools/test_check_carregado.py` *(criar)*

No molde do `test_check_retorno.py`, com a entrada montada em `tempfile` — o
`check_carregado.py` lê PNG e `.dfm`, e os dois se fabricam pequenos:

1. **captura de tamanho impossível** → recusa, com o nome do arquivo e as duas
   medidas (é a plantação de um pixel acima);
2. **captura exatamente do cliente** e **captura cliente + moldura** → as duas
   passam, e o deslocamento devolvido é `(0,0)` e `(3,29)`. É o par que impede
   alguém de "consertar" a recusa afrouxando os dois casos bons;
3. **formulário sem `ClientWidth` nem `Width`** → a outra recusa que o módulo
   tem, hoje sem exercício.

Vale ainda o caso do estado de hoje — os 18 formulários e as 15 fotografias
casando —, que é o que pega alguém apagando uma captura sem regerar o TSV.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_check_carregado.py` | criar |

## Verificação

- [x] `python3 -m unittest discover -p 'test_*.py'` em `wte/tools` conta os
      casos novos e passa — a bateria foi de **850** para **858**
- [x] Cada recusa reprova com a plantação e passa sem ela — a do `cliente()` em
      `tempfile`, a da moldura com a captura encolhida em **um** pixel
      (135×153 → 134×153) num espelho, com `wte/re/visual/` intocado
- [x] `make -C wte check` verde — `18 formularios, 15 fotografados dos dois lados`
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

Criado o `wte/tools/test_check_carregado.py` com **12 casos**. A bateria do
`make -C wte check` foi de 850 para 858 — oito a mais, e não doze, pela razão
abaixo.

Genuinamente novo é o que a CORR listou como item 3: a recusa do `cliente()` —
formulário sem `ClientWidth` nem `Width` —, que era a única do módulo sem
exercício nenhum, mais os dois caminhos bons dela (os 13 que declaram
`ClientWidth` e os 5 que declaram `Width`, cujo cliente é o declarado menos a
moldura). Mais o estado de hoje: 18 formulários, 15 fotografados dos dois
lados, e o TSV em disco batendo com a medida.

**Problemas encontrados:**

**Metade do que a CORR pedia já existia, e o achado é *onde*.** Os itens 1 e 2
— a captura de tamanho impossível recusada, e as duas boas devolvendo `(0,0)` e
`(3,29)` — estavam no **`test_check_retorno.py`**, cujo docstring dizia, com
todas as letras, testar *"as partes puras do `check_carregado.py`"*.

A CORR não errou o diagnóstico por descuido: o comando de evidência dela é um
`ls` dos dois `test_*.py`, e o `test_check_carregado.py` de fato não existia.
**Testar um módulo do arquivo de outro é exatamente como se acredita que uma
recusa não é exercitada** — o `ls` não a acha, e ela está lá o tempo todo.

Por isso os casos foram **trazidos** para o arquivo novo em vez de duplicados,
e o irmão voltou a ser só sobre o `check_retorno`. É a diferença entre oito
casos novos e doze: quatro mudaram de casa.

Dois casos acrescentei além da lista, e os dois vêm da própria evidência da
CORR: **um pixel a menos já aborta** (a recusa é por igualdade, não por ordem
de grandeza) e **a mensagem diz por que isso importa** — recusa sem a razão
vira `--force` na cabeça de quem a vê.

**Arquivos criados/modificados:**

- `wte/tools/test_check_carregado.py` — criado, 12 casos
- `wte/tools/test_check_retorno.py` — as quatro que mudaram de casa, e o
  docstring que anunciava a mistura
