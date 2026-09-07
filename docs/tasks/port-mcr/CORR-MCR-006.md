---
id: CORR-MCR-006
title: "Correção: a citação da fixture compartilhada aponta para a linha errada, e para um arquivo que não tem a variável"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-MCR-006: quem aponta para `work/entrada.mcr` do lado `wte/`

## Problema identificado

O Log da [MCR-TASK-03](/docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md), no
`Problemas encontrados` §2, registra a armadilha da fixture compartilhada — que
é boa e foi promovida ao perfil — com esta citação:

> `work/entrada.mcr` é apontada aqui por `WE2002_MCR_CARD` e lá por
> `WTE_MCR_ENTRADA` e `WTE_MCR_FIXTURE` (`wte/tools/test_dump_mcr.py:341`,
> `wte/tests/roteiros/golden-1{2,3}-*.txt`).

Duas imprecisões, e a segunda apaga a parte mais afiada da armadilha:

1. **`wte/tools/test_dump_mcr.py:341` não é nenhuma das duas variáveis.**
   `WTE_MCR_FIXTURE` é lida na **354** (e citada na 369); `WTE_MCR_ENTRADA`
   **não existe nesse arquivo** — quem a lê é
   `wte/src/impl/ep2002_mainform.FormShow.inc:146`, e quem a define são os
   roteiros, que o Log cita corretamente.
2. **A 341 é outra coisa, e é a pior:** `ENTRADA = M.ROOT / "work" /
   "entrada.mcr"`, um caminho **cravado**. Ou seja, o lado `wte/` alcança a
   fixture sem variável nenhuma — trocar `WTE_MCR_FIXTURE` não o desvia. A
   armadilha é mais forte do que o texto diz, e o texto aponta justamente para
   a linha que prova isso, atribuindo-a a outra coisa.

O `perfil-mcr.md` (armadilha 9) **não erra**: ele nomeia as duas variáveis sem
citar arquivo nem linha. O conserto é só no Log da task, e vale acrescentar ali
o caminho cravado, que é o que decide a suspeita.

## Evidência

```
$ grep -n 'WTE_MCR_FIXTURE\|WTE_MCR_ENTRADA\|entrada.mcr' wte/tools/test_dump_mcr.py
341:    ENTRADA = M.ROOT / "work" / "entrada.mcr"
351:        copia estavel e a `work/entrada.mcr`, que o cabecalho do
354:        do_ambiente = os.environ.get("WTE_MCR_FIXTURE")
369:                "confrontadas. Procurado: $WTE_MCR_FIXTURE, "

$ git grep -n 'WTE_MCR_ENTRADA' -- wte/tools
(vazio)

$ git grep -n 'WTE_MCR_ENTRADA' -- wte/src
wte/src/impl/ep2002_mainform.FormShow.inc:146:  cartao := GetEnvironmentVariable('WTE_MCR_ENTRADA');
```

| afirmado | medido |
|---|---|
| `WTE_MCR_ENTRADA` em `test_dump_mcr.py:341` | não está no arquivo; está em `wte/src/impl/ep2002_mainform.FormShow.inc:146` e nos roteiros |
| `WTE_MCR_FIXTURE` em `test_dump_mcr.py:341` | linha **354** |
| — | a **341** é `ENTRADA = M.ROOT / "work" / "entrada.mcr"`, caminho cravado |

O arquivo não mudou desde a execução da task: o último commit que o tocou é
`d653878`, anterior a este ciclo.

Todo o resto do Log remediu exato — venv 3.13.13 / PySide6 6.11.2 (`pip freeze`
com as quatro linhas), 663 MB, `QApplication OK, Qt 6.11.2 platform xcb` no
`:98`, `make -n mcr-98` e `make -n fresh`, a guarda do cartão ausente
alcançável, `cmp` da cópia, e o digest
`e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546` / 131.072 B.

## Causa raiz

A citação juntou duas variáveis de arquivos diferentes num par de parênteses e
pegou o número da linha da constante vizinha, que casa pelo `grep` do caminho e
não pelo da variável.

## Correção

### Arquivo: `docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md`

No `Problemas encontrados` §2, trocar a frase da citação por:

```markdown
`work/entrada.mcr` é apontada aqui por `WE2002_MCR_CARD` e alcançada do lado
`wte/` de três formas: por `WTE_MCR_FIXTURE`
(`wte/tools/test_dump_mcr.py:354`), por `WTE_MCR_ENTRADA`
(`wte/src/impl/ep2002_mainform.FormShow.inc:146`, alimentada pelos
`wte/tests/roteiros/golden-1{2,3}-*.txt`) e — o que decide — por **caminho
cravado**, em `wte/tools/test_dump_mcr.py:341`
(`ENTRADA = M.ROOT / "work" / "entrada.mcr"`). Trocar a variável não desvia o
lado de lá; só o digest resolve a suspeita.
```

O `perfil-mcr.md` pode ficar como está — ele não cita arquivo nem linha — ou
ganhar a oração do caminho cravado, que é a razão de o digest ser a régua.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md` | modificar |
| `docs/prompts/perfil-mcr.md` | modificar (opcional — só a oração do caminho cravado) |

## Verificação

- [ ] `grep -n 'WTE_MCR_FIXTURE\|WTE_MCR_ENTRADA\|entrada.mcr'
      wte/tools/test_dump_mcr.py` devolve as linhas que o doc cita
- [ ] `git grep -n 'WTE_MCR_ENTRADA' -- wte/tools` continua vazio, e o doc não
      atribui essa variável àquele arquivo
- [ ] `python3 tools/check_tasks.py` verde e `ctest -R tasks` verde
- [ ] nada em `wte/` foi modificado — é leitura pura aqui
- [ ] `roms/` e `work/entrada.mcr` intocados

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
