---
id: CORR-MCR-024
title: "Correção: o `mcr_container` entrou e o plano continua com três alvos de `ctest`, e o perfil com `1 passed, 2 skipped`"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-MCR-024: o quarto gate não chegou ao plano nem ao perfil

## Problema identificado

A MCR-TASK-16 registrou o `mcr_container` no `tests/CMakeLists.txt`, na tabela
de gates do perfil, no `CLAUDE.md` e no `tools/mcr/README.md` — e **não** nos
três lugares que ainda descrevem a bateria como sendo de três alvos:

| onde | o que diz | o que a ferramenta mede |
|---|---|---|
| `docs/PLAN-MCR-PY.md:58`, item **6 da definição de pronto** | "`ctest -R mcr` numa máquina sem venv e sem fixture: **1 passed, 2 skipped**" | **2 passed, 2 skipped** |
| `docs/PLAN-MCR-PY.md:519`, título da §4.4 e a tabela abaixo dele | "Os **três** alvos de `ctest`", com três linhas | **quatro** alvos |
| `docs/PLAN-MCR-PY.md:528` | "máquina limpa … → `ctest -R mcr` dá **1 passed, 2 skipped** — nunca `0 tests`, nunca erro" | **2 passed, 2 skipped** |
| `docs/prompts/perfil-mcr.md:225`, verificação da **Fase 2** | "máquina sem venv e sem fixture: `ctest -R mcr` = 1 passed, 2 skipped" | **2 passed, 2 skipped** |

**A mesma task escreveu o número certo em dois outros arquivos** — o
`CLAUDE.md` ("numa máquina sem venv e sem fixture, `ctest -R mcr` dá **2
passed, 2 skipped**") e o `tools/mcr/README.md:422` — e a §9 do próprio plano,
que ela editou, já diz "**quatro** alvos em `tests/CMakeLists.txt`". Então o
plano se contradiz internamente: a §9 diz quatro, a §4.4 diz três.

Isto importa por dois motivos concretos, e nenhum é estética:

1. **O item 6 é da definição de pronto**, que a Fase 5 não reabre — e a
   Fase 5 **mudou o valor dele**. O perfil manda dizer isso quando acontece:
   "se uma task daqui derrubar um passo das fases 3 ou 4, isso é o achado".
   Aqui o passo não caiu, o número dele mudou, e ninguém o reescreveu.
2. **A linha do perfil é a que o `/revisar` lê** ao rever qualquer task de
   Fase 2. É a mesma família da
   [CORR-MCR-017](/docs/tasks/port-mcr/CORR-MCR-017.md) e da
   [CORR-MCR-021](/docs/tasks/port-mcr/CORR-MCR-021.md): número copiado que
   envelhece no arquivo onde se lê o gate.

## Evidência

Os quatro alvos, com a fixture e o `:98`:

```
$ WE2002_MCR_CARD=$PWD/work/entrada.mcr ctest --test-dir build -R mcr
1/4 Test  #9: mcr_selftest ..... Passed  61.49 sec
2/4 Test #10: mcr_card ......... Passed   0.50 sec
3/4 Test #11: mcr_container .... Passed   0.16 sec
4/4 Test #12: mcr_ui ........... Passed  15.33 sec
100% tests passed, 0 tests failed out of 4
```

Sem a fixture, com venv e display presentes — **3 passed, 1 skipped**:

```
$ env -u WE2002_MCR_CARD ctest --test-dir build -R mcr
2/4 Test #10: mcr_card ......... ***Skipped  0.12 sec
3/4 Test #11: mcr_container .... Passed     0.18 sec
4/4 Test #12: mcr_ui ........... Passed      2.44 sec
```

Sem venv e sem display, o `mcr_ui` também pula (`SKIP_RETURN_CODE 77` no
`tests/CMakeLists.txt`), e sobram `mcr_selftest` e `mcr_container` passando:
**2 passed, 2 skipped**, que é o que o `CLAUDE.md` e o `tools/mcr/README.md`
já dizem.

E o plano discordando de si mesmo:

```
$ grep -n "quatro alvos\|três alvos\|1 passed, 2 skipped" docs/PLAN-MCR-PY.md
58:6. `ctest -R mcr` numa máquina sem venv e sem fixture: **1 passed, 2 skipped**.
519:### 4.4 Os três alvos de `ctest`
528:**1 passed, 2 skipped** — nunca `0 tests`, nunca erro.
733:- quatro alvos em `tests/CMakeLists.txt` — o `mcr_container` entrou com a
```

## Causa raiz

O total de alvos e o resultado da bateria limpa vivem copiados em quatro
documentos; a task atualizou dois deles e a §9 do plano, e as três linhas que
descrevem a bateria em outro lugar do mesmo plano ficaram.

## Correção

### Arquivo: `docs/PLAN-MCR-PY.md`

- item 6 da definição de pronto: **2 passed, 2 skipped**, com a nota de que o
  segundo `passed` é o `mcr_container`, que não precisa de fixture porque a
  entrada dele é versionada;
- §4.4: título "Os **quatro** alvos de `ctest`" e a linha nova na tabela —
  `mcr_container` | `mcr/*.gme`, versionado | `SKIP_RETURN_CODE 77`, só se o
  diretório não existir;
- o critério logo abaixo da tabela: **2 passed, 2 skipped**.

### Arquivo: `docs/prompts/perfil-mcr.md`

A verificação da Fase 2: `ctest -R mcr` = **2 passed, 2 skipped** numa máquina
sem venv e sem fixture, e **3 passed, 1 skipped** quando há venv e display mas
não há cartão. O segundo par vale a pena estar escrito: é o que se vê nesta
máquina ao rodar sem exportar a variável, e sem ele a leitura de "2 passed"
parece falha.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-MCR-PY.md` | modificar |
| `docs/prompts/perfil-mcr.md` | modificar |

## Verificação

- [ ] `grep -n "1 passed, 2 skipped" docs/PLAN-MCR-PY.md docs/prompts/perfil-mcr.md`
      sai vazio
- [ ] `grep -n "três alvos" docs/PLAN-MCR-PY.md` sai vazio, e a tabela da §4.4
      tem quatro linhas
- [ ] `env -u WE2002_MCR_CARD ctest --test-dir build -R mcr` reproduz o par
      escrito no perfil para esta máquina
- [ ] `python3 tools/check_tasks.py` e `ctest -R tasks` verdes
- [ ] a conferência de link de `.claude/rules/links.md` sai vazia
- [ ] `mcr/` e `roms/` intocadas

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
