---
id: CORR-PES2-005
title: "Correção: duas das cinco recusas do `--self-check` do `poke.py` medem a mesma coisa; a regra de fim e o último registro nunca são exercitados"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-PES2-005: o `--self-check` não exercita duas das guardas que o `poke.py` tem

## Problema identificado

`tools/pes2/poke.py` tem **seis** recusas no caminho de planejamento: nome
vazio, byte não imprimível, time ausente de alguma lista, nome maior que o
slot, registro em que a regra de fim de alguma tabela para, registro que é o
**último** da tabela, e registro que se sobrepõe a um marcador.

O `self_check()` afirma exercitar cinco delas, e o Log da
[PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) repete:
*"Cinco recusas, todas exercitadas pelo `--self-check`"*.

Medido: são **quatro** guardas distintas. O caso escrito para a regra de fim —

```python
bad += _expect_refusal(img, "the record an end rule stops on",
                       team=96, value="Eire")
```

— é interceptado antes pela guarda de **time ausente**, porque o canônico 96
(`IRELAND`) não está em `team-names-select2`, a lista dos 32 clubes. A linha
imprime "refused the record an end rule stops on" e o texto da recusa é o da
guarda anterior, que a linha de cima já tinha testado.

A guarda de **último registro da tabela** não tem caso nenhum.

## Evidência

Saída real do `--self-check` nas duas releases (`(EsIt)` e `(EnFrDe)`,
idênticas nesta parte):

```
  refused a partial team without --allow-partial: canonical team 102 ('CLASSIC FRANCE') is not in team-names-selectc, … -- pass --allow-partial to write the 1 list(s) that do have it
  refused the record an end rule stops on: canonical team 96 ('IRELAND') is not in team-names-select2 -- pass --allow-partial to write the 7 list(s) that do have it
```

As duas linhas são a **mesma** guarda. As duas guardas não exercitadas
funcionam — o que falta é o caso que as alcança:

```
$ python3 - "<track1.bin>"   # plan() com allow_partial=True
refused 96 -> team-names-selectc: 'Ireland' is the value that table's end rule
              stops on -- renaming it makes the table unreadable. --force …
refused 105 -> team-names: 'EURO ALLSTARS' is the last record of the table, and
               no table on this disc has a sentinel -- --force to insist
```

`stop_values()` medido no disco confirma que a guarda tem objeto em dez
tabelas: `IRL` em três, `Ireland` em cinco, `IRELAND` em `team-names-ending`,
`Aragon` em `team-names-select2`.

## Causa raiz

O caso foi escolhido pelo **valor** que a regra de fim consome (`IRELAND`) sem
notar que esse mesmo time está fora de uma das oito listas, e a ordem das
guardas em `plan()` põe a de ausência antes. `_expect_refusal` só confere que
`Refused` subiu — não confere **qual** recusa foi.

## Correção

### Arquivo: `tools/pes2/poke.py`

1. `_expect_refusal` passa a receber um trecho esperado da mensagem e a falhar
   quando a recusa que subiu não é a que o caso pretende medir. É o que impede
   o modo de falha desta correção de voltar:

```python
def _expect_refusal(img, what, expect, **kw):
    try:
        plan(img, **kw)
    except Refused as exc:
        if expect not in str(exc):
            print(f"  FAILED: {what} was refused for the wrong reason: {exc}")
            return 1
        print(f"  refused {what}: {exc}")
        return 0
    print(f"  FAILED: {what} was accepted and should have been refused")
    return 1
```

2. O caso da regra de fim passa `allow_partial=True` (ou escolhe um time que
   esteja nas oito listas e seja valor de parada de alguma), com
   `expect="end rule stops on"`.

3. Entra um caso para o **último registro**: `team=105` (`EURO ALLSTARS`),
   `expect="last record of the table"`.

4. Os demais casos ganham o `expect` correspondente.

### Arquivo: `docs/tasks/02-poke-por-conjunto-de-copias.md`

A frase do Log passa a dizer o que o `--self-check` mede de fato, depois da
correção — seis recusas, cada uma conferida pela mensagem.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/poke.py` | modificar |
| `docs/tasks/02-poke-por-conjunto-de-copias.md` | modificar |

## Verificação

- [ ] `python3 tools/pes2/poke.py "<track1.bin>" --self-check --tmpdir <dir>`
      verde nas **duas** releases, imprimindo uma recusa distinta por guarda
- [ ] trocar `expect` por um texto errado faz o `--self-check` ficar vermelho
      (a prova de que a conferência de mensagem não é decorativa)
- [ ] `ctest --test-dir build -R pes2` verde, com `WE2002_PES2_IMAGE` e
      `WE2002_PES2_TMPDIR` **absolutos**
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
