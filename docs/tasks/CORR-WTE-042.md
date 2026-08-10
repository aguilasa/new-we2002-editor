---
id: CORR-WTE-042
title: "Correção: o Log da WTE-TASK-18 diz que os testes do transpilador eram 33, e eram 38"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-042: o número de partida dos testes não foi medido

## Problema identificado

O Log de Execução da [WTE-TASK-18](/docs/tasks/18-camada-de-dados-gerada.md),
na tabela de arquivos, registra:

> `wte/tools/test_port_database_pas.py` | 58 testes (eram 33)

O **58** bate. O **33** não bate com nenhum commit do arquivo: eram **35** no
commit que fechou a WTE-TASK-17 (`8ae9170`) e **38** no commit imediatamente
anterior à WTE-TASK-18 (`d8af56a`), depois que a
[CORR-WTE-034](/docs/tasks/CORR-WTE-034.md) acrescentou três.

É o mesmo defeito que a [CORR-WTE-038](/docs/tasks/CORR-WTE-038.md) abriu no Log
da WTE-TASK-17 — número de tamanho de suíte escrito de memória —, e a
consequência é a mesma: o delta que o Log anuncia (25 testes novos) fica errado,
e é justamente o delta que justifica a frase seguinte, sobre os sete defeitos
que a task descobriu.

O enunciado da própria WTE-TASK-18 cita o número certo três parágrafos acima —
"41 regras, os dois guards, **38 testes**" (linha 29) —, de modo que o arquivo
se contradiz sozinho.

## Evidência

```
$ git show 8ae9170:wte/tools/test_port_database_pas.py | grep -cE '^[[:space:]]+def test_'
35
$ git show 102dd1d:wte/tools/test_port_database_pas.py | grep -cE '^[[:space:]]+def test_'
38
$ git show d8af56a:wte/tools/test_port_database_pas.py | grep -cE '^[[:space:]]+def test_'
38
$ grep -cE '^[[:space:]]+def test_' wte/tools/test_port_database_pas.py
58
```

| Afirmado | Medido | Fonte |
|---|---|---|
| 58 testes agora | 58 | `grep -c` no arquivo commitado |
| **eram 33** | **38** (35 no commit da 17) | `git show` dos dois commits |

A suíte inteira roda verde: `Ran 58 tests … OK`, incluindo os dois casos que
chamam o `fpc` de verdade (`test_as_seis_unidades_compilam`,
`test_as_decisoes_de_tipo_valem_em_execucao` — nenhum `skip`).

## Causa raiz

O número de partida foi lembrado, não medido; a WTE-TASK-17 fechou com 35 e
ganhou mais três antes da 18 começar.

## Correção

### Arquivo: `docs/tasks/18-camada-de-dados-gerada.md`

Trocar `(eram 33)` por `(eram 38)`, e dizer ao lado como remedir, para que a
próxima revisão não precise reconstruir o histórico:

> | `wte/tools/test_port_database_pas.py` | 58 testes (eram 38 —
> `git show d8af56a:… \| grep -cE '^[[:space:]]+def test_'`) |

O número **58** e os demais do Log (498 recusas, 454 estruturais, 6 unidades, 23
casos Pascal) foram remedidos nesta revisão e batem; só o 33 muda.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/18-camada-de-dados-gerada.md` | modificar |

## Verificação

- [ ] `grep -cE '^[[:space:]]+def test_' wte/tools/test_port_database_pas.py`
      bate com o número corrente escrito no Log
- [ ] O número de partida bate com `git show d8af56a:…`
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

`(eram 33)` virou `(eram **38**)` na tabela de arquivos do Log da WTE-TASK-18,
com a rota de remedição ao lado. A rota vale para os **dois** números da célula,
não só para o de partida:

```console
$ git show d8af56a:wte/tools/test_port_database_pas.py | grep -cE '^[[:space:]]+def test_'
38
$ git show 7b642f7:wte/tools/test_port_database_pas.py | grep -cE '^[[:space:]]+def test_'
58
```

**Problemas encontrados:**

A verificação desta correção pedia que o `grep -c` sobre o arquivo no `HEAD`
batesse com o número corrente do Log. Não bate mais, e não deveria: a
[CORR-WTE-036](/docs/tasks/CORR-WTE-036.md), executada neste mesmo lote e antes
desta, acrescentou dois testes — o `HEAD` está em 60. Os dois números da célula
são desta task, e por isso a rota escrita fixa o commit em vez de olhar o
`HEAD`. Mesmo desenho da [CORR-WTE-038](/docs/tasks/CORR-WTE-038.md), que é o
mesmo defeito no Log da WTE-TASK-17.

O "41 regras" do enunciado da 18 (linha 28) foi corrigido para 47 no commit da
CORR-WTE-038, pela varredura de lá.

**Arquivos criados/modificados:**

- `docs/tasks/18-camada-de-dados-gerada.md`
