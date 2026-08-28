---
id: CORR-WTE-122
title: "Correção: o progresso.md ainda chama o hook do lado do port de GOLDEN_EDIT, nome que o golden_gui.sh não lê"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-122: o nome do hook que a PAR-TASK-01 corrigiu num arquivo e deixou no outro

## Problema identificado

A prosa que abre a série `PAR-TASK-*` no
[/docs/tasks/progresso.md](/docs/tasks/progresso.md) (linha 1267) diz que a
régua desta série é **"`golden_gui` com `GOLDEN_EDIT`"**. O `golden_gui.sh`
não lê essa variável. Ele lê **`GOLDEN_GUI_EDIT`**; `GOLDEN_EDIT` é o hook do
`golden_run.sh`, do lado do `ed.exe`.

Este é exatamente o erro que a própria [PAR-TASK-01](/docs/tasks/PAR-TASK-01.md)
identificou e corrigiu — o Log dela registra o achado sob "Problemas
encontrados" e o texto da task foi ajustado. O commit que fechou a task
(`b5997b7`) **tocou o `progresso.md`**, mas só a célula de status da linha da
tabela; a frase errada, duas linhas acima da mesma tabela, ficou.

Quem executa a PAR-TASK-02 entra pelo `progresso.md`, não pelo Log da 01.
Exportar `GOLDEN_EDIT` sozinho num modo `gui` não dá erro: o
`golden_run.sh` aplica o roteiro no oráculo, o `golden_gui.sh` não aplica nada
no port, e **os dois lados divergem em toda faixa editada** — um falso vermelho
que parece bug do port.

## Evidência

O que o `progresso.md` afirma:

```text
$ sed -n '1267p' docs/tasks/progresso.md
e a régua (`golden_gui` com `GOLDEN_EDIT`) já está pronta e rodou nas três
```

O que a ferramenta lê:

```text
$ grep -rn "GOLDEN_GUI_EDIT\|GOLDEN_EDIT" tools/
tools/golden_gui.sh:112:if [ -n "${GOLDEN_GUI_EDIT:-}" ]; then
tools/golden_gui.sh:113:    echo "gui: aplicando GOLDEN_GUI_EDIT"
tools/golden_gui.sh:114:    eval "$GOLDEN_GUI_EDIT"
tools/golden_run.sh:150:if [ -n "${GOLDEN_EDIT:-}" ]; then
tools/golden_run.sh:152:    eval "$GOLDEN_EDIT"
```

E o que a própria task já diz, no arquivo vizinho:

```text
$ sed -n '131,133p' docs/tasks/PAR-TASK-01.md
**O markdown desta task afirmava que o `golden_gui` aceita `GOLDEN_EDIT`.**
Não aceita: o hook do lado do port chama-se **`GOLDEN_GUI_EDIT`**
```

## Causa raiz

A correção do nome foi aplicada no arquivo da task, e o `progresso.md` — que
carrega a mesma frase, escrita no commit anterior (`cac09df`) — não foi
reconciliado no commit que fechou a task.

## Correção

### Arquivo: `docs/tasks/progresso.md`

Na frase "A **01 é a primeira** por três razões que convergem", trocar o nome
do hook e dizer que são **dois**, que é a informação que a série usa:

```markdown
e a régua (`golden_gui.sh` com `GOLDEN_GUI_EDIT` no lado do port, e
`golden_run.sh` com `GOLDEN_EDIT` no lado do `ed.exe`) já está pronta e rodou
nas três imagens.
```

Os dois recebem `$MAIN` em escopo e definem `dlu_x`/`dlu_y` com a mesma
conversão, então o **mesmo** trecho de shell serve aos dois — é o que faz a
série medir os dois lados com o mesmo estímulo, e é o que a frase precisa dizer.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/progresso.md` | modificar |

## Verificação

- [ ] `grep -n 'GOLDEN_EDIT' docs/tasks/progresso.md` não devolve mais nenhuma
      linha que atribua `GOLDEN_EDIT` ao `golden_gui`
- [ ] Os dois nomes aparecem com o script que os lê ao lado
- [ ] `python3 tools/check_tasks.py` continua `ok`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
