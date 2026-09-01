---
id: PAR-TASK-08
title: "Operações em massa"
type: verificação
category: core
projeto: newWe2002
depends_on: ["PAR-TASK-04", "PAR-TASK-07"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.9"
status: bloqueado
---

# PAR-TASK-08: Operações em massa

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.9.
- **Projeto:** `newWe2002` (port Qt do `ed.exe`), **não** o `wte/` Lazarus.

---

## Método

O mesmo para toda a série, e é o que a §8 do inventário já fixa: **fazer a
mesma coisa no `ed.exe` sob Wine e no port, gravar as duas cópias e comparar
com `tools/golden_compare.py`.**

```sh
cp roms/ptbr-remaster.bin  "$SCRATCH/v.bin"
DISPLAY=:98 ./build/src/app/newWe2002 "$SCRATCH/v.bin"
```

**Critério de aprovação:** a única divergência é `405724..405739`, o slot 64 do
array de 63. Qualquer outra faixa é achado, e vira CORR.

**Sempre sobre cópia, sempre no `:98`.** O `roms/` nunca é alvo. Feche qualquer
editor aberto no display antes: os dois lados acham o diálogo principal pelo
tamanho, e uma janela esquecida é dirigida no lugar da que está sob teste.

**A imagem preferida desta série é a `ptbr-remaster.bin`.** Ela é a única com
oráculo vivo nos dois editores e com os ramos do codec exercitados — medido na
[PROPOSTA-IMAGEM-GOLDEN](/docs/PROPOSTA-IMAGEM-GOLDEN.md) §8.4. Onde o item
pedir nome latino legível, é ela; onde pedir kanji, a `japanese-shift-jis.bin`.

---

## Itens a conferir

- [ ] `CMD_SORT_RESERVES` numa seleção e num clube (a ordem torta é a certa)
      ← **BLOQUEADO, encaminhado ao Windows.** O botão é invisível nos dois;
      exige build de teste com o controle visível dos dois lados, e o lado
      `ed.exe` pede MSVC com MFC estático. Não commitar a build
- [ ] Clube com 1 goleiro na reserva × com 2  ← **BLOQUEADO, mesmo handler**
- [x] `CMD_UPDATE_COSTS`
- [x] `CMB_EDITALLLOOK`
- [x] `CMB_EDITALLBARS` — conferir que 57..63 ficaram intactos

**O primeiro item exige build descartável dos dois lados**, e o enunciado é
explícito: não commitar. O `ed.exe` precisa do controle visível também, o que
significa editar o `.rc` e recompilar com MSVC — se isso não for viável, o item
fica registrado como não-medido, com a razão. Não invente medição por outro
caminho.

`CMD_SORT_RESERVES` tem uma **divergência deliberada** da Fase 5: o swap fora do
array. A "ordem torta é a certa" do enunciado se refere a isso — conferir contra
o oráculo, não contra o que parece ordenado.

---

## Definição de pronto

- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.9
- [ ] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [ ] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01 (itens 3-5) e 2026-08-31 (fechamento do estado) —
**BLOQUEADA: 3 de 5 fechados, 2 encaminhados ao Windows.**
(O item 4 fechou em 2026-09-01, pela CORR-WTE-133.)

**Resumo:**

| item | resultado |
|---|---|
| `CMD_SORT_RESERVES` | **não medido** — botão `NOT WS_VISIBLE` nos dois; exige MSVC |
| 1 goleiro × 2 | **não medido** — mesmo handler do anterior |
| `CMD_UPDATE_COSTS` | golden `OK` |
| `CMB_EDITALLLOOK` | golden `OK` depois da [CORR-WTE-133](/docs/tasks/concluidos/CORR-WTE-133.md), que era fixture, não código |
| `CMB_EDITALLBARS` | golden `OK`, e 57..63 intactos |

**Os dois não medidos, e por que não se inventou caminho.** O enunciado é
explícito: *"se isso não for viável, o item fica registrado como não-medido,
com a razão. Não invente medição por outro caminho."* O item 2 cai junto com o
1 porque é o mesmo `OnSortReserves` — o comentário do handler descreve
exatamente o caso de um goleiro só.

### Segunda passagem, 2026-08-31 — o bloqueio, medido e encaminhado

A primeira passagem disse "exige MSVC" e parou aí. Conferido por ferramenta, o
bloqueio é **mais forte do que se pensava**: o comando não é alcançável por
usuário nenhum, em nenhum dos dois programas.

| conferência | resultado |
|---|---|
| `ed.rc:370-371` | `PUSHBUTTON "sort reserve",CMD_CALCFORZA2,439,243,72,15,NOT WS_VISIBLE` |
| `grep -an CALCFORZA legacy/mfc/*` | só o `ON_BN_CLICKED` (`edDlg.cpp:1287`) e o `#define` (`resource.h:320`) — **nenhum `ShowWindow`** |
| tabela `ACCELERATORS` no `.rc` | **não existe** — não há caminho por teclado |
| `ui_MainDialog.h:1131` | `CMD_SORT_RESERVES->setVisible(false);` |
| `grep -rn CMD_SORT_RESERVES src/app/` | só o `connect` e o `.ui` — o port também nunca o mostra |
| controles `NOT WS_VISIBLE` no diálogo principal | **6 de 248**, e os outros cinco são os campos extras de ML, que o `OnTeamSelected` mostra em runtime |

Ou seja: a paridade **observável** está cumprida — o botão está escondido nos
dois. O que não se pode medir é o comportamento de um comando que nenhum
usuário dispara.

**Encaminhado para o Windows**, onde o MSVC existe: a linha está escrita na
seção "Bônus que só o Windows consegue" do
[/docs/PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md), com os dois itens, as duas
ressalvas (não commitar a build; o `ctest -R ui_forms` quebra) e a observação
de que **uma das quatro divergências deliberadas da Fase 5 mora nesse
handler** — o swap fora do array — e portanto nunca foi observada em execução.

**E uma armadilha de ferramenta que quase inverteu a leitura:** `grep` no
`ed.rc` **sem `-a`** não imprime nada. O arquivo é ISO-8859-1 e o grep o trata
como binário; por um momento o `CMD_CALCFORZA2` pareceu ausente do `.rc`, o que
teria sido um achado falso e grave (handler ligado a controle inexistente).
Ele está lá, na linha 370.

### Discrepância consertada nesta passagem

A nota da §8.9 e o comentário do `8.9-update-bars.sh` diziam que um `Return`
seco é *"inócuo no diálogo do original, que não tem `DEFPUSHBUTTON`"*. **É o
contrário**: sem `DEFPUSHBUTTON` o Enter cai em `CDialog::OnOK` e **encerra o
editor** — medido no item 4 da §8.10 ([CORR-WTE-141](/docs/tasks/concluidos/CORR-WTE-141.md)).

O que torna o `Return` inócuo nesses roteiros é o **ponteiro**: ele acabou de
clicar o botão da operação e continua sobre ele, e no Win32 um pushbutton com
foco vira o default temporário — o `Return` re-clica esse botão, idempotente,
em vez de alcançar o `IDOK`. As duas medições que estabelecem isso já existiam
e diferem **só em onde o ponteiro estava**: a corrida verde do
`8.9-update-bars.sh` e a sonda do item 4 da §8.10. A razão certa está agora nos
dois sítios, e importa: mexer no `par_click` daquele roteiro sem mexer no
`Return` pode fechar o oráculo antes de gravar.

**O que se aprendeu, e custou três corridas erradas:**

**Nem toda operação em massa abre a caixa `"Operation done!"`, e os dois lados
discordam sobre quais.** O `CMD_UPDATE_COSTS` abre nos dois; o
`CMB_EDITALLBARS` abre **só no port** e não no `ed.exe`. Isso quebra as duas
soluções óbvias: sem dispensar, o port não grava; dispensando com o
`dispensa_modal` da §8.2, o **oráculo** deixa de gravar. Um `Return` seco
resolve os dois.

**E o `dispensa_modal` é ativamente perigoso no lado do Wine.** Os controles do
MFC ali são janelas X de verdade, e vários caem na faixa que o `acha_modal`
procura (206×80, 148×82). Sem caixa na tela, ele acha um **controle**, clica
nele, e a gravação não acontece: a cópia sai `IDENTICAL` enquanto o port grava,
e o golden acusa o port por uma divergência que é do roteiro. Foi o que
produziu, em sequência, um vermelho falso e depois um **verde vazio** — os dois
lados sem gravar, saindo iguais.

**Problemas encontrados:** o item 4 reprovou na primeira medição e foi fechado
pela [CORR-WTE-133](/docs/tasks/concluidos/CORR-WTE-133.md), que achou a causa **fora do
código**: o legado abre `defaultlook.txt` por caminho relativo, lê a cópia
gitignored de `Debug/`, e ela tinha 4 linhas diferentes da versionada. Cada
lado gravava certo o que lia.

A task fica **bloqueada** pelos dois itens que exigem MSVC, e o destino deles
está escrito no `PLAN-WINDOWS.md` — não só neste Log.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os cinco itens da §8.9 e a nota dos modais
- `docs/tasks/concluidos/CORR-WTE-133.md` e `docs/tasks/concluidos/correcoes-progresso.md` — o achado
- `docs/tasks/concluidos/PAR-TASK-08.md` — este Log
- `tools/par/8.9-prelude.sh` — o prelúdio, com `acha_modal`/`dispensa_modal` e
  a nota de quando **não** usá-los
- `tools/par/8.9-update-costs.sh`, `8.9-reset-look.sh`, `8.9-update-bars.sh`
