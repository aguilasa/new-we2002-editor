---
id: CORR-LOOKS-056
title: "Correção: o `CLAUDE.md` descreve um ciclo fechado e um visualizador de tupla, e o que existe é a tela `LOOKS SET` num ciclo aberto"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-056: a porta de entrada do repositório ficou na v1

## Problema identificado

A seção do sexto projeto no `CLAUDE.md` foi escrita pela
[`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md) com o
argumento de que é **o arquivo que quem chega lê primeiro**. Desde então a v2
abriu (quinze tasks novas) e a
[`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) entregou o que o
usuário pediu — a janela **é** a tela `LOOKS SET`, com as doze linhas, o cursor
e a caixa de ajuda, aberta por `.\make.ps1 looks`. Nada disso chegou lá.

O que a seção diz hoje, e o que existe:

```text
CLAUDE.md
  "Um sexto projeto, aberto em 2026-09-14 e com o ciclo fechado em 2026-09-17"
      -> o ciclo reabriu no mesmo dia: 21 a 35 no progresso.md, quatro fases
         (8 a 11), e duas já concluídas

  "| work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --looks
     A-I3-A-E-A --screenshot out.png | desenha uma tupla fora da tela"
      -> `--looks` deixou de ter default na LOOKS-TASK-22: sem ele o app abre
         a TELA, com ele o visualizador de uma tupla.  A linha descreve o modo
         que virou a exceção, e nenhuma linha descreve o default

  "| python tools/looks/ui_check.py | o alvo looks_ui: julga os PNGs de fora"
      -> desde a LOOKS-TASK-22 ele também anda as doze linhas até as duas
         pontas nos dois slots, por tecla sintética, e compara o texto com o
         screen.json (96 s de alvo, contra os 48 s de antes)
```

E não há menção nenhuma a `screen.py`, ao `screen.json` — **o único arquivo
gerado do ciclo**, que o perfil já registra como tal —, ao
`oracle.py --screen`, ao `oracle.py --keys`, nem ao alvo `make.ps1 looks`, que
é a única forma documentada de ver a tela.

Nada disso é contradição interna do ciclo: o plano, o perfil e as tasks estão
reconciliados. É a porta de entrada que ficou velha, e ela é lida por quem
ainda não sabe que existe plano.

## Evidência

```text
$ sed -n '/## Visualizador de aparência/,/^$/p' CLAUDE.md | head -3
## Visualizador de aparência — projeto separado, em `tools/looks/`

Um **sexto projeto**, aberto em 2026-09-14 e com o ciclo fechado em 2026-09-17:

$ grep -c "screen.py\|screen.json\|make.ps1 looks\|--keys" CLAUDE.md
0

$ grep -n "LOOKS-TASK-2[12]" docs/tasks/looks/progresso.md | cut -c1-90
64:| [LOOKS-TASK-21](/docs/tasks/looks/21-a-tela-medida.md) | ... ✅ Concluído
65:| [LOOKS-TASK-22](/docs/tasks/looks/22-a-tela-na-janela.md) | ... ✅ Concluído
```

O último commit do `CLAUDE.md` é o `4023c65`, da LOOKS-TASK-20; a v2 abriu no
`46f828a` e a tela chegou no `1fb8488`, os dois depois.

## Causa raiz

A abertura da v2 e a primeira entrega dela mudaram o plano, o perfil e as
tasks, que é onde o rito manda mexer, e o `CLAUDE.md` não é nenhum dos três —
ninguém é dono dele por convenção.

## Correção

### Arquivo: `CLAUDE.md`

Na seção do sexto projeto:

- o ciclo está **aberto** na v2, com as fases 8 a 11 e o que elas entregam;
- a tela `LOOKS SET` na janela, e `.\make.ps1 looks` (`-State 1|2`,
  `-Tuple` para o visualizador de uma tupla só) como a forma de abri-la — com
  a ressalva de que é o único alvo que mostra janela ao usuário;
- `screen.py` e `screen.json` na lista de comandos, com o `screen.json` dito
  **gerado** por `oracle.py --screen --write`;
- `oracle.py --screen` e `oracle.py --keys` na lista, com o que cada um mede;
- a linha do `ui_check.py` passa a dizer que ele também anda a tela por tecla.

O tamanho fica o de hoje: a seção é índice, não plano.

### Arquivo: `docs/prompts/perfil-looks.md`

Uma linha na seção de arquivos quentes dizendo que **o `CLAUDE.md` tem seção
deste ciclo** e envelhece com ele — que é a única forma de a próxima task saber
que precisa olhar para lá.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `CLAUDE.md` | modificar |
| `docs/prompts/perfil-looks.md` | modificar |

## Verificação

- [ ] `grep -n "ciclo fechado" CLAUDE.md` não acha a frase na seção do `looks`
- [ ] `screen.py`, `screen.json`, `--screen`, `--keys` e `make.ps1 looks`
      aparecem na seção
- [ ] a linha do `app.py` diz o que o default faz hoje
- [ ] `python tools/check_tasks.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
