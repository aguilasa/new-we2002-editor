---
id: CORR-WTE-111
title: "Correção: o campo `faixa` do CAMPOS é dado morto, e dois dos quatro valores contradizem o medido"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-111: `faixa` no `CAMPOS` — ninguém lê, e dois estão errados

## Problema identificado

A tabela `CAMPOS` do
[`dump_buffers.py`](../../wte/tools/dump_buffers.py) declara uma chave `faixa`
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
   [`buffers.md`](../../wte/re/buffers.md) diz *"todo número daqui saiu do
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
[CORR-WTE-096](/docs/tasks/CORR-WTE-096.md) (chave repetida que ninguém via) e
da [CORR-WTE-020](/docs/tasks/CORR-WTE-020.md).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_buffers.py` | modificar |
| `wte/tools/test_check_bordas.py` | modificar — a guarda |
| `wte/re/buffers.md`, `wte/re/buffers.tsv` | regerar, se a saída mudar |

## Verificação

- [ ] `grep -c "faixa" wte/tools/dump_buffers.py` só encontra as ocorrências de
      `NUMERICOS`, ou a chave virou `esperado` **conferida**
- [ ] Se virar guarda: um valor plantado fora do medido faz o gerador abortar
- [ ] `python3 wte/tools/dump_buffers.py --check` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
