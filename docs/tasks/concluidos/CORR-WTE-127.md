---
id: CORR-WTE-127
title: "Correção: o Escape da CORR-WTE-125 continua divergindo nos dez combos de papel, e a razão dada para excluí-los não bate com o código"
type: correção
category: ui
status: concluído
depends_on: []
---

# CORR-WTE-127: o mesmo `Escape`, o outro combo — medido divergindo

## Problema identificado

A [CORR-WTE-125](/docs/tasks/concluidos/CORR-WTE-125.md) consertou o `Escape` nos **seis
combos de cobrador** e declarou escopo estreito, com esta razão (mensagem do
commit `1c7e656`):

> Escopo estreito de proposito -- os dez combos de papel gravam por
> `currentIndexChanged`, outro caminho, e sao medidos na §8.7.

**As duas metades da frase estão erradas.**

**1. Os combos de papel não gravam por `currentIndexChanged`.** Eles gravam em
perda de foco, pelo **mesmo** `eventFilter` e no **mesmo** `QEvent::FocusOut`
que os de cobrador. O `currentIndexChanged` só repinta a legenda do marcador do
campinho — não toca em dado nenhum. A estrutura é idêntica nos dois lados, e é
a do original:

| | legenda | gravação |
|---|---|---|
| legado, papel | `ON_CBN_SELCHANGE(CMB_TAT2)` → `OnSelchangeTat2` (só `SetWindowText`) | `ON_CBN_KILLFOCUS(CMB_TAT2)` → `OnKillfocusTat2` |
| port, papel | `currentIndexChanged` → `OnRoleShown` (só `setText`) | `FocusOut` → **`OnRoleCommitted`** |
| port, cobrador | — | `FocusOut` → `OnKickerChanged` |

**2. A §8.7 não mede isto.** O único item dela sobre papel é "Trocar papel e
conferir a legenda do marcador" — troca e legenda, não `Escape`. O adiamento
não tem destinatário: quando a [PAR-TASK-06](/docs/tasks/concluidos/PAR-TASK-06.md) rodar,
ela não vai exercitar este caminho.

**E a divergência está lá.** Medida nesta revisão, com o mesmo estímulo da
CORR-WTE-125 apontado para o `CMB_SLOT_ROLE2` em vez do `CMB_KICK_LONG_FK`:
o golden **reprova**.

## Evidência

Roteiro idêntico ao `tools/par/8.3-escape-cobrador.sh`, trocando só o combo
(`CMB_SLOT_ROLE2`, `CMB_TAT2` no `.rc`, em `428,43,38,12` DLU):

```text
$ GOLDEN_EDIT="$R" GOLDEN_GUI_EDIT="$R" WE2002_GOLDEN_MODE=gui \
    bash tools/golden_check.sh roms/ptbr-remaster.bin
FALHOU: 1 divergencia(s) nao esperada(s):
  2303700..2303700  1 byte(s)  data  OFS_FORMATIONS+0
```

O controle positivo mostra de que lado está a diferença — o port **não mexeu**:

```text
$ dump_cpp roms/ptbr-remaster.bin | grep 'teams\[0\].raw_formation'
teams[0].raw_formation = 31:020607080e...
$ dump_cpp <cópia gravada pelo port> | grep 'teams\[0\].raw_formation'
teams[0].raw_formation = 31:020607080e...      <- idêntico

$ byte cru em 2303700:   orig 2   port 2
```

Três `Down` a partir do papel `2` e `Escape`: o port grava **2** (o Qt desfez),
e o `ed.exe` grava o item navegado — a única divergência do golden, no byte que
guarda esse slot. É **exatamente** o quadro que a CORR-WTE-125 descreve para o
`kick_long_fk` de 3 a 6, no outro combo.

Para comparação, os três roteiros da §8.3 rodados nesta mesma revisão, todos
verdes depois do conserto:

| roteiro | golden | `kick_long_fk` | `OFS_KICKER+0` |
|---|---|---:|---|
| `8.3-escape-cobrador.sh` | `OK` | 3 → **6** | presente |
| `8.3-escape-sem-navegar.sh` | `OK` | **3** | ausente |
| `8.3-escolher-e-tab.sh` | `OK` | 3 → **5** | presente |

O conserto funciona. O que falta é alcance.

## Causa raiz

O `eventFilter` instala o filtro de `Escape` em `cmb_kicker_[i]->view()` e não
em `cmb_role_[i]->view()`, e a justificativa para parar aí descreveu o
`currentIndexChanged` da legenda como se fosse o caminho de gravação.

## Correção

### Arquivo: `src/app/MainWindow.cpp`

Instalar o mesmo filtro na view dos dez combos de papel, ao lado do
`cmb_role_[i]->installEventFilter(this)` que já existe:

```cpp
cmb_role_[i]->installEventFilter(this);
// ...e o popup, pelo mesmo Escape dos combos de cobrador (CORR-WTE-127).
cmb_role_[i]->view()->installEventFilter(this);
```

E estender o laço do `KeyPress` de `Escape` para percorrer os dez, como já
percorre os seis. O corpo é o mesmo — ler `currentIndex().row()`, `hidePopup()`,
repor o índice — porque o problema é o mesmo.

**Cuidado com o `OnRoleShown`.** Repor o índice com `setCurrentIndex` dispara
`currentIndexChanged`, que repinta a legenda do marcador; é o comportamento
desejado (a legenda tem de mostrar o papel navegado, como no original, onde o
`CBN_SELCHANGE` já a repintou durante a navegação). Não bloquear o sinal aqui.

### Arquivo: `tools/par/8.7-escape-papel.sh` (novo)

O roteiro acima, versionado no molde dos da §8.3, para o item virar gate.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md`

Um item novo na §8.7 — "`Escape` depois de navegar um combo de papel" — porque
hoje nenhum item cobre este caminho; e a nota da §8.3 passa a dizer que a
emenda vale para os dezesseis combos, não só para os seis.

### Arquivo: `docs/tasks/concluidos/PAR-TASK-06.md`

O item novo, para quem executar a §8.7 encontrá-lo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/MainWindow.cpp` | modificar |
| `tools/par/8.7-escape-papel.sh` | criar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar |
| `docs/tasks/concluidos/PAR-TASK-06.md` | modificar |

## Verificação

- [x] O golden com o roteiro do papel sai `OK`, e não mais
      `FALHOU ... OFS_FORMATIONS+0`
- [x] O controle positivo mostra `raw_formation[0]` indo de `2` ao papel
      navegado, e os outros nove slots intactos
- [x] Os três roteiros da §8.3 continuam `OK` — a emenda não pode regredir os
      cobradores
- [x] `Escape` sem navegar num combo de papel continua sem gravar nada
- [x] A legenda do marcador mostra o papel navegado depois do `Escape`, como no
      `ed.exe`
- [x] `ctest --preset debug -E golden` 4/4
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-29

**Resumo do que foi feito:**

O achado se confirmou antes de qualquer edição: o roteiro do papel reprovava o
golden com `2303700..2303700  OFS_FORMATIONS+0`, e o `dump_estado` mostrava
`raw_formation[0]` indo de `0x02` a `0x05` no oráculo e ficando em `0x02` no
port — o mesmo quadro do `kick_long_fk`, no outro combo.

O filtro do `Escape` passou a cobrir os **dezesseis**. Em vez de repetir o laço,
o corpo virou um `QComboBox* combo` resolvido pelos dez de papel e depois pelos
seis de cobrador; o resto é o que já estava — ler `currentIndex().row()`,
`hidePopup()`, repor o índice, consumir o evento.

| Roteiro | Golden | Medido |
|---|---|---|
| `8.7-escape-papel.sh` | antes `FALHOU ... OFS_FORMATIONS+0`; depois **`OK`** | `raw_formation[0]` `0x02 → 0x05` nos dois; os outros nove slots intactos |
| `8.7-escape-papel-sem-navegar.sh` | `OK` | `raw_formation` **inteiro intacto** nos dois; sem `OFS_FORMATIONS+0` no controle |
| `8.3-escape-cobrador.sh` | `OK` | sem regressão |
| `8.3-escape-sem-navegar.sh` | `OK` | sem regressão |
| `8.3-escolher-e-tab.sh` | `OK` | sem regressão |

**A legenda do marcador foi conferida em captura**, que é a única forma: o
`setCurrentIndex` da reposição dispara `currentIndexChanged` e repinta o
campinho, e era preciso ver que ele mostra o papel **navegado**, como no
original. Depois do `Escape`, o combo lê `LIB` nos dois lados e o campinho
inteiro sai com as mesmas dez legendas — `LB`, `LIB`, `CB DX`, `RB`, `DH SX`,
`DH DX`, `OH SX`, `OH DX`, `CF SX`, `CF DX` — no `ed.exe` e no port.

`ctest --test-dir build -E golden` 4/4; `we2002_tests` 69 checks, 0 falhas.

**Problemas encontrados:**

**A `PAR-TASK-06` ainda não rodou, e o item novo já está fechado.** Marcá-lo
`[x]` na task de outra pessoa seria dar por conferido o que ela não conferiu, e
deixá-lo `[ ]` mandaria refazer o que já tem gate. O item entrou com o `[x]` e a
nota de que foi fechado **fora** da task, mais a condição em que ela deve
re-rodá-lo: se o item 2 (trocar papel e conferir a legenda) mexer no
`OnRoleShown` ou no `eventFilter`.

**A varredura puxou três documentos que a CORR não previa**, todos afirmando
"os seis": a §3.5 e a §8.3 do inventário, o §Fase 5 do
[/docs/PLAN-LINUX.md](/docs/PLAN-LINUX.md) e a nota de sinais do `CLAUDE.md`.
Os quatro passaram a dizer dezesseis, e o `CLAUDE.md` ganhou a armadilha por
extenso — o `currentIndexChanged` dos combos de papel engana, porque parece o
caminho de gravação e não é.

**O parágrafo "escopo deliberadamente estreito" da
[CORR-WTE-125](/docs/tasks/concluidos/CORR-WTE-125.md) ficou falso** e recebeu a ressalva
no próprio Log dela, em vez de ser reescrito: ele registra o que se pensou
ontem, e apagá-lo perderia a lição de que a razão dada não tinha sido medida.

**Arquivos criados/modificados:**

- `src/app/MainWindow.cpp` — o `installEventFilter` na `view()` dos dez de
  papel e o laço do `Escape` cobrindo os dezesseis
- `tools/par/8.7-escape-papel.sh` e `tools/par/8.7-escape-papel-sem-navegar.sh`
  — criados (o segundo não estava na lista da CORR, mas a Verificação pede a
  medição, e a convenção do `tools/par/` manda versioná-la)
- `docs/PARIDADE-FUNCIONAL.md` — o item novo na §8.7, a linha do `Escape` na
  tabela da §3.7, e as notas da §3.5 e da §8.3 falando em dezesseis
- `docs/tasks/concluidos/PAR-TASK-06.md` — o item novo, já fechado, com a condição de
  re-rodagem
- `docs/tasks/concluidos/CORR-WTE-125.md` — a ressalva no parágrafo do escopo
- `docs/PLAN-LINUX.md`, `CLAUDE.md` — reconciliação do "seis" para "dezesseis"
