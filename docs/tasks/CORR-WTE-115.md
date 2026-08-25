---
id: CORR-WTE-115
title: "Correção: o check_carregado.py aborta e não tem teste, enquanto o irmão nascido no mesmo commit tem"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-115: o `check_carregado.py` não tem par de teste

## Problema identificado

A [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) criou **dois**
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

É a mesma situação que a [CORR-WTE-106](/docs/tasks/CORR-WTE-106.md) abriu para
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

- [ ] `python3 -m unittest discover -p 'test_*.py'` em `wte/tools` conta os
      casos novos e passa
- [ ] Cada recusa reprova com a plantação e passa sem ela
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
