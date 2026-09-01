---
id: CORR-WTE-040
title: "Correção: o GABARITO diz quatro famílias de `BitBtnNClick`, e são três"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-040: o número que justifica o nome de arquivo não foi medido

## Problema identificado

O [`wte/re/spec/GABARITO.md`](../../../wte/re/spec/GABARITO.md), linhas 12-14,
justifica o nome `<formulario>.<handler>.md`:

> Os 96 pares são únicos, mas os nomes soltos não: há 16 `FormCreate`, 2
> `FormShow` e quatro famílias de `BitBtnNClick` espalhadas por formulários
> diferentes.

Dos três números, dois batem e o terceiro não. O `published_methods.tsv` tem
**três** nomes `BitBtnNClick` — `BitBtn1Click`, `BitBtn2Click`,
`BitBtn3Click` —, com 4, 2 e 3 ocorrências. Não há `BitBtn4Click`, e nenhuma
leitura de "família" dá quatro: por nome distinto são 3, por ocorrência são 9.

A frase é a justificativa da convenção de nome de arquivo, que é a decisão
central da task. Ela sobrevive intacta com o número certo — o ponto ("nome
solto não é único") continua de pé —, e é por isso que o erro passa
despercebido: nada quebra, só fica um número inventado no documento que a fase
4 inteira vai ler antes de escrever cada spec.

## Evidência

Medido sobre a fonte canônica, `wte/re/published_methods.tsv` (WTE-TASK-04):

```
FormCreate: 16   FormShow: 2
familias BitBtnNClick: {'BitBtn1Click': 4, 'BitBtn2Click': 2, 'BitBtn3Click': 3}
BitBtn* todos: ['BitBtn1Click', 'BitBtn2Click', 'BitBtn3Click']
nomes repetidos (todos): FormCreate 16, BitBtn1Click 4, BitBtn3Click 3,
                         SpeedButton1Click 3, FormShow 2, BitBtn2Click 2
```

| Afirmado no `GABARITO.md` | Medido no TSV | Fonte da medição |
|---|---|---|
| 16 `FormCreate` | 16 | `collections.Counter` sobre a coluna `handler` |
| 2 `FormShow` | 2 | idem |
| **quatro** famílias de `BitBtnNClick` | **três** nomes (9 ocorrências) | idem |

Há um quarto nome repetido fora da família `BitBtn`: `SpeedButton1Click`, com
3 ocorrências. Se a intenção era "quatro nomes de botão repetidos", a frase
precisa dizer isso — hoje ela diz `BitBtnNClick`.

## Causa raiz

O número foi escrito de memória ao redigir o gabarito, sem passar pelo TSV que
o próprio `spec_index.py` lê três linhas adiante.

## Correção

### Arquivo: `wte/re/spec/GABARITO.md`

Trocar por uma frase medida. Uma forma que sobrevive a recontagem:

> Os 96 pares são únicos, mas os nomes soltos não: há 16 `FormCreate`, 2
> `FormShow`, três nomes `BitBtnNClick` (`BitBtn1Click` em quatro formulários,
> `BitBtn3Click` em três, `BitBtn2Click` em dois) e `SpeedButton1Click` em
> três.

O mesmo trecho aparece no
[`wte/re/spec/README.md`](../../../wte/re/spec/README.md) na forma curta — "há 16
`FormCreate`" —, que está correta e não precisa mudar.

O enunciado da [WTE-TASK-23](/docs/tasks/concluidos/23-formato-da-spec.md) repete o número
no **Log de Execução**, que é história de tarefa executada e fica fora do
perímetro do `check_fase1.py`: não mexer lá.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/GABARITO.md` | modificar |

## Verificação

- [ ] O número no `GABARITO.md` bate com `Counter` sobre a coluna `handler` do
      `published_methods.tsv`
- [ ] `python3 wte/tools/spec_index.py --check` verde
- [ ] `make -C wte check` verde (o `check_fase1.py` varre este arquivo)
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A frase do `GABARITO.md` passou a ser a medida, nomeando as três famílias e o
quarto nome de botão repetido que estava fora da família `BitBtn`:

> há 16 `FormCreate`, 2 `FormShow`, três nomes `BitBtnNClick` (`BitBtn1Click`
> em quatro formulários, `BitBtn3Click` em três, `BitBtn2Click` em dois) e
> `SpeedButton1Click` em três.

Com a rota de remedição ao lado — `collections.Counter` sobre a coluna
`handler` do `published_methods.tsv` —, que é o que faltava para o número ter
dono. Remedido agora:

```
FormCreate: 16   FormShow: 2
BitBtn*: {'BitBtn1Click': 4, 'BitBtn2Click': 2, 'BitBtn3Click': 3}
repetidos: BitBtn1Click 4, FormCreate 16, FormShow 2, BitBtn2Click 2,
           BitBtn3Click 3, SpeedButton1Click 3
```

**Problemas encontrados:**

Nenhum. A varredura achou o mesmo número em
`docs/tasks/concluidos/23-formato-da-spec.md:133`, **dentro do Log de Execução** (o Log
começa na linha 96) — história de tarefa executada, que esta correção manda
explicitamente não tocar. `wte/re/spec/README.md` traz a forma curta ("há 16
`FormCreate`") e já estava certo.

`spec_index.py --check` verde (96 handlers, 0 com spec, 96 abertos);
`make -C wte check` rc=0, com o `check_fase1.py` varrendo este arquivo.

**Arquivos criados/modificados:**

- `wte/re/spec/GABARITO.md`
