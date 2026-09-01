---
id: CORR-WTE-139
title: "Correção: `Return` depois de clicar um botão do `DefaultTacticsDialog` reabre o botão no port e fecha o diálogo no original"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-139: o botão focado come o `Return` no port

## Problema identificado

No `DefaultTacticsDialog`, depois de **clicar** `CMD_IMP` ou `CMD_EXP`, a tecla
`Return` faz coisas diferentes nos dois lados:

| | o que `Return` faz |
|---|---|
| `ed.exe` | vai para o botão **default** do diálogo — o `IDOK`, invisível — e **fecha** o diálogo |
| port | o `QPushButton` clicado ficou com o foco, e um botão focado **se auto-clica**: reabre o diálogo de arquivo |

No Win32 o `Return` de um diálogo vai para o `DEFPUSHBUTTON`, não para o
controle focado; no Qt um `QPushButton` com foco trata `Return` como ativação
antes de o evento chegar ao `keyPressEvent` do diálogo — que é onde a
[CORR-WTE-131](/docs/tasks/concluidos/CORR-WTE-131.md) pôs o `accept()`.

O efeito prático é que **o diálogo não tem saída pelo teclado enquanto o foco
estiver num botão**: cada `Return` reabre o diálogo de arquivo, indefinidamente.
E como o diálogo é modal, o `CMB_WRITE` do diálogo principal fica inalcançável —
a imagem nunca é gravada.

## Evidência

Medido em 2026-08-31, durante a [CORR-WTE-135](/docs/tasks/concluidos/CORR-WTE-135.md).
Roteiro: prelúdio da §8.7, `CMD_EDIT_PRESETS`, `CMD_EXP`, digitar o caminho,
e três `Return`.

Janelas no fim do roteiro, lado do port — o diálogo de arquivo **de volta**
depois de cinco `Return`:

```text
  2097158 Geometry: 1077x547 :: WE2002 Editor
  2097178 Geometry: 481x297  ::  Modify default tactics — WE2002 Editor
  4195823 Geometry: 1124x822 :: TACTIC FILE TO EXPORT
foco: 4195823
```

E o resultado na imagem, contra a original:

```text
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin port-img.bin
IDENTICAL
```

`IDENTICAL` apesar de o `.t2002` de 52 bytes ter sido gravado em disco: o
arquivo saiu, a imagem não. Do lado do oráculo, o mesmo roteiro grava 6 faixas /
56 bytes.

Com um clique no `TXT_FORMATION_NAME` antes do `Return` — que tira o foco do
botão — o port passa a gravar 5 faixas / 41 bytes, e o golden da perna de
exportar sai `OK`. É o contorno que os roteiros
`tools/par/8.7-t2002-exportar.sh` e `8.7-t2002-importar.sh` usam hoje, e o
mesmo que o `8.7-preset-renomear.sh` já usava — lá sem que ninguém tivesse
medido por quê.

## Causa raiz

`QAbstractButton` trata `Qt::Key_Return` como ativação quando tem foco, e
consome o evento. O `keyPressEvent` do `DefaultTacticsDialog` só vê a tecla
depois de o widget focado a ignorar — que é o caso do `QLineEdit`, e não o do
botão.

No MFC não há esse caminho: `CDialog` roteia o `Return` para o
`DEFPUSHBUTTON`, e o foco do botão clicado não participa da decisão.

## Correção

O `autoDefault=false` que o `rc2ui.py` já põe nos `PUSHBUTTON` **não resolve**:
ele governa o botão default, não a ativação por foco. O caminho é o
`keyPressEvent` do diálogo — que já existe — **ver o `Return` antes do botão**,
por `eventFilter` nos botões ou por `Qt::Key_Return` interceptado no filtro do
diálogo, chamando `accept()` como a CORR-WTE-131 faz.

**Cuidado com o alcance.** O `MainWindow` tem 86 botões e a mesma mecânica; e
lá `Return` não deve fechar nada, porque o `IDD_ED_DIALOG` não tem
`DEFPUSHBUTTON` — no MFC o Enter cai em `CDialog::OnOK` e **encerra o editor**
(medido: é o que produz `nao consegui focar a janela` no `golden_run.sh`).
Reproduzir isso no port é decisão à parte, e **não** é o que esta CORR pede.
O escopo aqui é o `DefaultTacticsDialog`.

Ao fechar, os dois roteiros do `.t2002` podem perder o clique de foco — mas só
depois de o golden mostrar que perdem sem mudar o veredito.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | modificar |
| `tools/par/8.7-t2002-exportar.sh` | modificar, se o contorno puder sair |
| `tools/par/8.7-t2002-importar.sh` | idem |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — a §8.7 |

## Verificação

- [x] Com o foco em `CMD_EXP`, `Return` fecha o diálogo no port, como no
      `ed.exe` — antes: restavam quatro janelas, com `TACTIC FILE TO EXPORT`
      reaberto; depois: restam a raiz e o diálogo principal
- [x] A perna de exportar continua `OK` no golden, com controle positivo
      **não** vazio — 5 faixas / 41 bytes
- [x] `tools/par/8.7-preset-renomear.sh` e
      `tools/par/8.7-escape-papel-preset.sh` continuam `OK`
- [x] O `MainWindow` não mudou de comportamento — `git diff` vazio nos dois
      arquivos dele
- [x] `ctest --preset debug` verde — 9/9
- [x] `roms/` intocada — md5 `7d49ff4e50a951dacd456096df4a2896`

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-31

**Resumo do que foi feito:**

Reproduzido primeiro: com o foco no `CMD_EXP`, o `Return` reabria
`TACTIC FILE TO EXPORT` em vez de fechar o diálogo — quatro janelas na tela onde
deviam restar duas.

O conserto é o `eventFilter` que o diálogo já tinha, agora instalado também em
**todos os seus `QPushButton`**, tratando `Return`/`Enter` com `accept()` antes
de o botão se ativar. Um `QAbstractButton` focado consome a tecla, então o
`keyPressEvent` do diálogo — que a
[CORR-WTE-131](/docs/tasks/concluidos/CORR-WTE-131.md) escreveu — nunca a via.

Filtrar **todos** os botões, e não só `CMD_IMP`/`CMD_EXP`, é o que reproduz o
original: no MFC o `Return` vai para o `DEFPUSHBUTTON` qualquer que seja o botão
focado, inclusive os dez marcadores do campinho.

**Problemas encontrados:**

Nenhum. O escopo ficou no `DefaultTacticsDialog`, como a CORR pede: o
`MainWindow` tem 86 botões e a mesma mecânica, mas lá `Return` **não** deve
fechar nada — o `IDD_ED_DIALOG` não tem `DEFPUSHBUTTON`, e no MFC o Enter cai em
`CDialog::OnOK` e encerra o editor. Reproduzir isso é decisão à parte.

**O contorno dos dois roteiros do `.t2002` ficou onde está.** A CORR permitia
tirá-lo depois de medir, mas o clique no `TXT_FORMATION_NAME` também serve ao
oráculo e sair dali custaria duas corridas de golden para provar que não muda o
veredito. Com ele, a perna de exportar segue `OK`.

**Arquivos criados/modificados:**

| Arquivo | O quê |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | o filtro nos botões e o ramo de `Return` no `eventFilter` |
| `docs/PARIDADE-FUNCIONAL.md` | a nota da §8.7, ao lado da CORR-WTE-131 |
