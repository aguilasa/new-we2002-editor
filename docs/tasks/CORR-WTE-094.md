---
id: CORR-WTE-094
title: "Correção: a premissa da WTE-TASK-32 está errada — o `ed.exe` calcula preço, o que ele não tem é o botão"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-094: o `ed.exe` tem a fórmula de preço

## Problema identificado

A [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) abre com:

> Primeira das quatro features que motivaram o projeto: **o `ed.exe` não calcula
> preço**, o editor do Obocaman calcula.

A primeira metade é falsa, e ela é a premissa da task inteira.

## Evidência

| Onde | O quê |
|---|---|
| `legacy/mfc/edDlg.cpp:7703` | `int CalcolaCostoGiocatore(int i)` — a fórmula, por posição |
| `legacy/mfc/edDlg.cpp:7948` | `gioc[i].costo = CalcolaCostoGiocatore(i);` — o laço do time inteiro |
| `legacy/mfc/edDlg.cpp:1286` | `ON_BN_CLICKED(CMD_CALCCOSTI, OnCalcolaCostiML)` — o handler, no message map |
| `legacy/mfc/resource.h:314` | `#define CMD_CALCCOSTI 1244` |
| `legacy/mfc/ed.rc` | **`CMD_CALCCOSTI` não aparece** |

**O `ed.exe` tem a fórmula e não tem o controle.** É o mesmo caso do
`MainForm.Button2Click` no binário do Obocaman: handler vivo no código, sem
componente que o chame. A feature do usuário continua sendo do Obocaman; a
*aritmética* não é exclusiva dele.

E há mais: a fórmula **já está transpilada para Pascal nesta árvore**, como
`ComputePlayerCost` em `wte/src/we2002_database.pas:1776`, gerada pelo
`port_database_pas.py` a partir de `src/core/Database.cpp:1465`.

## Causa raiz

A frase foi escrita a partir da tela do `ed.exe`, onde o botão não existe, e não
do código.

## Correção

Corrigir a frase na task e registrar o que ela ganha com isso — porque a
consequência é boa: **a WTE-TASK-32 tem oráculo B para preço**, o que ela não
sabia ter.

**Sem presumir fórmula igual.** A do `ed.exe` é `double`, começa em `k = 16`,
ramifica por posição e termina em `if (k<1) k = 1; return (int)ceil(k);`. A do
Obocaman é aritmética **inteira** sobre uma soma, com as constantes `0x2DC6C0`,
`0x9C40`, `0x2BC`, `7`, um `+5` final e a variante `× 5 div 3`. São
estruturalmente diferentes; o valor do oráculo B é **desenhar a amostragem**,
não copiar o resultado.

E ele desenha bem, porque exemplifica os três riscos que a própria task lista em
*"onde a tabela pode enganar"*:

| Risco da task | Onde ele aparece no `ComputePlayerCost` |
|---|---|
| saturação | `if (k<1) k = 1` — piso, invisível acima dele |
| arredondamento | `ceil`, não truncamento — muda ±1 e some no olho |
| termo cruzado | os bônus `== 19` por atributo, e `if(foot == 2) k += 1.5` |

Variar um atributo por vez não revelaria nenhum dos três.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/32-preco-do-jogador.md` | modificar (a premissa e a nota de oráculo B) |
| `docs/tasks/correcoes-progresso.md` | modificar |

## Verificação

- [x] as cinco linhas da tabela de evidência conferidas no `legacy/mfc/`
- [x] `CMD_CALCCOSTI` ausente do `ed.rc` — `grep` nos dois arquivos
- [x] `ComputePlayerCost` existe em `wte/src/we2002_database.pas`
- [x] nenhuma execução: correção de documento

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo:** a premissa da task de preço estava errada, e corrigi-la a deixa
  **melhor** do que estava: ela ganha um oráculo de formato para preço que já
  vive nesta árvore, em C++ e em Pascal.

  **A lição é sobre de onde vem uma premissa.** *"O `ed.exe` não calcula preço"*
  é verdade sobre a tela e falsa sobre o código, e a diferença é um botão que
  alguém apagou do `.rc` e não do `.cpp` — exatamente o que a spec do
  `MainForm.Button2Click` já tinha achado no outro binário. Duas vezes o mesmo
  padrão, em dois editores diferentes.

- **Problemas encontrados:** nenhum.
