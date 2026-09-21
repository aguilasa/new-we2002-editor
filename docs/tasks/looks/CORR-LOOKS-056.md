---
id: CORR-LOOKS-056
title: "Correção: o `CLAUDE.md` descreve um ciclo fechado e um visualizador de tupla, e o que existe é a tela `LOOKS SET` num ciclo aberto"
type: correção
category: processo
status: done
depends_on: []
origin: LOOKS-TASK-22
severity: low
done_on: 2026-09-17
done_commit: 06749b0
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

- [x] `grep -n "ciclo fechado" CLAUDE.md` não acha a frase na seção do `looks`
- [x] `screen.py`, `screen.json`, `--screen`, `--keys` e `make.ps1 looks`
      aparecem na seção
- [x] a linha do `app.py` diz o que o default faz hoje
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

A evidência reproduz em `06749b0`: `"ciclo fechado em 2026-09-17"` na linha 810
do `CLAUDE.md`, **zero** menções a `screen.py`, `screen.json`, `make.ps1 looks`
ou `--keys`, e o último commit do arquivo é o `4023c65`, da LOOKS-TASK-20 —
anterior à abertura da v2 (`46f828a`) e à tela na janela (`1fb8488`).

A seção do sexto projeto passou a dizer o que existe:

- **o ciclo está aberto**, com a v1 fechada em 2026-09-17, a v2 aberta no mesmo
  dia, as fases 8 a 11 (tasks 21 a 35), o que já saiu (21 e 22) e o que falta —
  pose e boneco montado, uniforme e cenário, caminhada. "Só lê" continua, e
  deixou de estar preso à v1;
- **`.\make.ps1 looks`** entrou na tabela como o que abre a tela, com
  `-State 1|2` e `-Tuple` para o visualizador de uma tupla, e a ressalva de ser
  o único alvo do ciclo que mostra janela — opção de visualizador sem `-Tuple`
  é recusada, não ignorada;
- **a linha do `app.py` diz o default de hoje**: sem `--looks` abre a tela, com
  `--looks` desenha uma tupla fora da tela;
- **`screen.py --check`/`--report`, `oracle.py --screen` e `oracle.py --keys`**
  entraram, com o que cada um mede, e um parágrafo diz que o `screen.json` é o
  **único arquivo gerado do ciclo**, escrito por `--screen --write` e não à mão;
- a linha do `ui_check.py` passou a dizer que ele anda as doze linhas até as
  duas pontas nos dois slots por tecla sintética;
- e entrou a armadilha que a LOOKS-TASK-22 mediu: **janela e tabela concordam
  de graça; quem julga a tela é o `--keys`, contra o emulador.** Sem ela, a
  linha do `looks_ui` ali convida a ler o verde dele como "a tela está certa".

O cabeçalho da lista virou "Cinco coisas", que é quantas são.

No perfil, o `CLAUDE.md` entrou nos **arquivos quentes**, com a razão: ele é a
porta de entrada de quem ainda não sabe que existe plano, nenhuma varredura do
rito o alcança, e foi exatamente assim que ele ficou para trás.

### Gates

```text
$ grep -n "ciclo fechado" CLAUDE.md
                                   # nada
$ grep -c "screen.py\|screen.json\|make.ps1 looks\|--keys" CLAUDE.md
8                                  # era 0
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
$ python tools/looks/selftest.py --quiet
  ..... 71 of 71 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada; correção de documentação, nenhum emulador subiu.

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `CLAUDE.md` — a seção do sexto projeto
- `docs/prompts/perfil-looks.md` — o `CLAUDE.md` nos arquivos quentes
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
