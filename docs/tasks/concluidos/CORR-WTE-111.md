---
id: CORR-WTE-111
title: "Correção: o campo `faixa` do CAMPOS é dado morto, e dois dos quatro valores contradizem o medido"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-111: `faixa` no `CAMPOS` — ninguém lê, e dois estão errados

## Problema identificado

A tabela `CAMPOS` do
[`dump_buffers.py`](../../../wte/tools/dump_buffers.py) declara uma chave `faixa`
nos quatro campos de texto. **Nada a lê.** Os limites publicados saem de
`lim_min`/`lim_max`, que o gerador **mede** das tabelas
`TEAM_NAME_KANJI_LEN` e `TEAM_NAME_LEN_3`; a `faixa` fica na estrutura sem
consumidor.

E dois dos quatro valores **contradizem o que foi medido**:

| Campo | Medido pelo gerador | Declarado em `CAMPOS["faixa"]` |
|---|---|---|
| `edit_nombre1` | **5..13** | `(5, 19)` ✗ |
| `edit_nombre2` | **7..19** | `(5, 19)` ✗ |
| `edit_nombre3` | 3..3 | `(3, 3)` ✓ |
| `casilla_nombre` | 10..10 | `(10, 10)` ✓ |

Hoje isso não quebra nada, e é por isso que é fácil de deixar passar: valor
morto não aparece em saída nenhuma. O risco é o de sempre nesta árvore —
alguém escrever a próxima guarda **sobre** a `faixa`, achando que ela é dado
medido, e prender o limite em `19` para um campo que nunca passa de `13`.

**A mesma chave é viva na tabela vizinha**, o que torna a confusão provável: em
`NUMERICOS`, `faixa` é lida e sai na mensagem de erro
(*"a validacao de faixa (1..250) sumiu de …"*). Duas tabelas no mesmo arquivo,
a mesma chave, uma medida e outra decorativa.

## Evidência

Que ninguém lê:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n 'c\["faixa"\]\|c\[.faixa.\]' wte/tools/dump_buffers.py wte/tools/test_check_bordas.py
```

```text
(nenhuma saída)
```

E o confronto, com os dois números lado a lado:

```bash
python3 -c "
import sys; sys.path.insert(0,'wte/tools')
import dump_buffers as D
for l in D.mede()['linhas']:
    dec = [c['faixa'] for c in D.CAMPOS if c['controle'] == l['controle']][0]
    print(f\"{l['controle']:16s} medido {l['lim_min']:>2}..{l['lim_max']:<2}  CAMPOS {dec}\")"
```

```text
edit_nombre1     medido  5..13  CAMPOS (5, 19)
edit_nombre2     medido  7..19  CAMPOS (5, 19)
edit_nombre3     medido  3..3   CAMPOS (3, 3)
casilla_nombre   medido 10..10  CAMPOS (10, 10)
```

Que a chave é viva na outra tabela:

```bash
grep -n "n\['faixa'\]\|n\[.faixa.\]" wte/tools/dump_buffers.py
```

```text
293:                f"{n['controle']}: a validacao de faixa ({n['faixa']}) sumiu de "
```

## Causa raiz

A `faixa` foi escrita à mão na primeira versão da tabela, antes de o gerador
passar a medir os limites das duas tabelas por time, e ficou.

## Correção

### Arquivo: `wte/tools/dump_buffers.py`

Duas saídas, e a escolha muda o que a chave significa:

1. **Apagar a chave dos quatro** — é a mais simples e a que o resto do arquivo
   já pratica: o limite é medido, não declarado. O banner do
   [`buffers.md`](../../../wte/re/buffers.md) diz *"todo número daqui saiu do
   script"*, e dado declarado ao lado de dado medido enfraquece a frase.
2. **Mantê-la como expectativa, e conferi-la** — vira `esperado`, e o gerador
   **aborta** quando o medido sai dela, com a mensagem dizendo os dois números.
   Aí ela deixa de ser decoração e passa a ser guarda; e os dois valores de hoje
   têm de ser corrigidos para `(5, 13)` e `(7, 19)` antes, senão nasce vermelha.

A primeira é a recomendada: a segunda inventa uma segunda fonte de verdade para
um número que já tem uma.

### Guarda

Qualquer que seja a saída, um caso em `test_check_bordas.py` que percorra
`CAMPOS` e recuse chave que nenhum código lê — hoje `faixa`, amanhã outra —
custa três linhas e fecha a classe, que é a mesma da
[CORR-WTE-096](/docs/tasks/concluidos/CORR-WTE-096.md) (chave repetida que ninguém via) e
da [CORR-WTE-020](/docs/tasks/concluidos/CORR-WTE-020.md).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_buffers.py` | modificar |
| `wte/tools/test_check_bordas.py` | modificar — a guarda |
| `wte/re/buffers.md`, `wte/re/buffers.tsv` | regerar, se a saída mudar |

## Verificação

- [x] `grep -n '"faixa"' wte/tools/dump_buffers.py` só encontra as duas
      ocorrências de `NUMERICOS` (linhas 144 e 154)
- [x] Guarda exercitada: chave `inventada` plantada em `CAMPOS` faz o caso
      reprovar com a mensagem certa
- [x] `python3 wte/tools/dump_buffers.py --check` verde; duas execuções dão
      md5 igual nos dois arquivos
- [x] `make -C wte check` verde (828 testes, era 823)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

Escolhida a **saída 1** da CORR — apagar a chave dos quatro campos de texto —,
que era a recomendada. A segunda inventaria uma segunda fonte de verdade para
um número que já tem uma: os limites destes campos são medidos das tabelas por
time, e dado declarado ao lado de dado medido enfraquece o banner do
`buffers.md`, que promete que todo número de lá saiu do script.

Ficou registrado no próprio arquivo por que a chave não existe mais, e — o que
importa mais — **que a chave de mesmo nome na tabela vizinha é viva**: nos
numéricos a faixa não se mede de lugar nenhum, é a regra que o handler aplica,
e o gerador a cobra do `.inc`. Mesma palavra, dois papéis, no mesmo arquivo.

A guarda (`TestChaveMorta`) percorre as duas tabelas e recusa chave que nenhum
código lê, procurando a leitura na fonte — no molde do
`chaves_repetidas_no_fonte` do `check_fase4.py`. Plantando uma chave
`inventada` em `CAMPOS`, ela reprova com a mensagem certa.

**Problemas encontrados:**

**A guarda achou mais duas chaves mortas na primeira corrida, e as duas em
`NUMERICOS`** — que a CORR não previa, porque ela olhou só a `faixa`:

- **`formulario`** — declarado nos dois numéricos e nunca lido, enquanto a
  tabela de texto o publica. Não apaguei: **tornei vivo**, acrescentando a
  coluna `Formulário` à tabela dos numéricos no `buffers.md`. Apagar perderia
  informação verdadeira, e as duas tabelas ficam consistentes.
- **`filtro`** — é o assunto da
  [CORR-WTE-112](/docs/tasks/concluidos/CORR-WTE-112.md), que vai confrontá-lo com o
  `KeyPress`. Deixado como **pendência com dono nomeado** numa lista
  `PENDENTES` da guarda, e não como buraco.

**E a exceção se limpa sozinha**, que é a parte que vale copiar: há um caso que
**reprova quando a chave passar a ser lida**, forçando quem a tornou viva a
tirar a linha da lista. É a lição literal do grupo `pendente_32` da
WTE-TASK-35 — isenção que sobrevive à própria causa deixa de proteger qualquer
coisa e esconde a regressão seguinte.

**Arquivos criados/modificados:**

- `wte/tools/dump_buffers.py` — a chave apagada, a nota, o `formulario` vivo
- `wte/tools/test_check_bordas.py` — `TestChaveMorta`, 4 casos
- `wte/re/buffers.md` — regerado (a coluna nova)
