# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Regra obrigatória: validação visual no display `:99`

**Toda execução com GUI — rodar o editor, tirar screenshot, dirigir a janela com
`xdotool` — deve acontecer no `DISPLAY=:99`.** O `:1` é a sessão real do usuário;
abrir janelas nele atrapalha o uso da máquina.

Já existe um Xvfb rodando:

```
Xvfb :99 -screen 0 960x672x24
```

Se por qualquer motivo não for possível usar o `:99` — servidor caído, resolução
insuficiente, app que exige compositor Wayland, ferramenta que não respeita
`DISPLAY` — **pergunte ao usuário antes de cair para o `:1`**. Nunca faça esse
fallback silenciosamente.

Limitação conhecida: o diálogo principal `IDD_ED_DIALOG` tem 718×337 DLU ≈
**1077×548 px**, mais largo que os 960 px do `:99` atual. Para validar a janela
principal inteira é preciso um screen maior. Isso exige reiniciar o Xvfb —
**pergunte antes**.

Screenshot de uma janela específica:

```sh
DISPLAY=:99 xdotool search --pid <PID> | while read i; do \
  echo "$i :: $(DISPLAY=:99 xdotool getwindowname $i)"; done
DISPLAY=:99 import -window <WINDOW_ID> out.png
```

Disponível no host: `Xvfb`, `xvfb-run`, `xdotool`, `import` (ImageMagick),
`ffmpeg`. **Não** instalados: `wmctrl`, `scrot`, `x11vnc`.

---

## O que é este repositório

Editor binário do **Winning Eleven 2002 (PSX)** — edita times, jogadores,
táticas, uniformes e bandeiras gravando direto na imagem de CD. Escrito em
2002 por Francesco Moriero (ver `readme.txt`), como app **MFC** do Visual C++ 6
migrado para VS2010. Fork com feature adicional de importar dados do SoFIFA.

O código é Windows-only. Há um plano de port para Linux em
[PLAN-LINUX.md](PLAN-LINUX.md) — **leia antes de mexer em qualquer coisa de
portabilidade**; ele contém o diagnóstico completo, as armadilhas já mapeadas e
o faseamento acordado.

### Upstream

O código original vive em
**<https://github.com/thyddralisk/WE2002-editor-2.0>** — repo público, parado
desde 2015-05-24, com os dois commits originais (`dbba1c8` "Loaded my original
files", `46f097b` ".gitattributes") e a árvore intacta sob `ed-eng2/`.

Essa é a **fonte canônica** para comparar contra o estado original ou recuperar
qualquer coisa perdida no caminho:

```sh
git clone https://github.com/thyddralisk/WE2002-editor-2.0.git
```

Este repositório já foi um fork dele. O vínculo foi cortado: o histórico local
foi reescrito a partir de um commit raiz novo, e o fork antigo
(`aguilasa/WE2002-editor-2.0`) foi deletado para tirar da rede de forks os
~340 MB de artefatos de build. Nada exclusivo se perdeu — como era fork, todo o
histórico apagado era do thyddralisk e continua lá.

### Licença: não existe

Nem Moriero (2002) nem thyddralisk (2015, que publicou no GitHub e adicionou o
import do SoFIFA) concederam licença — o código herdado é
todos-os-direitos-reservados. Por isso o repo **não tem `LICENSE`**; a linhagem
e as ressalvas estão em [NOTICE.md](NOTICE.md). Não adicione um arquivo de
licença nem headers de licença aos fontes.

## Rodar o editor

Não existe build para Linux. O binário pré-compilado `Debug/ed.exe` (PE32+
x86-64, MFC estático) roda sob o runner Wine do Bottles:

```sh
export DISPLAY=:99
export WINEPREFIX=<prefix dedicado>
export WINEDEBUG=-all
WINE=/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin
cd Debug && "$WINE/wine64" ed.exe
```

Encerrar: `WINEPREFIX=<prefix> "$WINE/wineserver" -k`

Notas:

- **Não reusar a bottle `DiztinGUIsh`.** `ed.cpp:75` chama
  `COleObjectFactory::UpdateRegistryAll()`, que escreve no registry do prefix.
- O runner soda só tem `x86_64-windows`; o `ed.exe` é x64, então casa. Não há
  suporte 32-bit nesse runner.
- `wineboot` reclama de FreeType e `/etc/ld.so.preload` reclama de
  `libAppProtection.so` (Citrix). Ambos benignos — as fontes renderizam.
- `Debug/ed.exe` é o **oráculo de referência** para os golden tests do port.
  Manter no disco mesmo depois de adicionar `.gitignore`.

Rebuild do `.exe` exige MSVC + MFC estático no Windows. MinGW e Winelib não
servem: nenhum dos dois distribui MFC.

## Imagens de CD para teste

| Caminho em `~/ROMs/psx/` | Uso |
|---|---|
| `Winning Eleven 2002 - European Deluxe 2002-03/` | **Imagem golden.** Todos os offsets batem, nomes latinos. |
| `World Soccer Winning Eleven 2002/` | **Melhor imagem japonesa para testes** (arquivo único, SLPM-87056). Valida `kanjitoascii`/`asciitokanji`. ECC íntegro — use esta para testar que o port reproduz o mesmo ECC inválido que o `ed.exe` ao gravar. Só track de dados, sem `.cue`: não serve para jogar. |
| `World Soccer Winning Eleven 2002 (Japan)/` | Mesma release, dump multi-track completo (9 tracks + `.cue` válido). É a de jogar. Para testes é redundante e tem ECC degradado (211/300 setores zerados). |
| `Pro Evolution Soccer 2 (Europe) (EnFrDe)/` | **NÃO USAR.** Layout diverge após ~2 MB; o editor corrompe a imagem. |

Os dois dumps japoneses divergem em 3 bytes de dados (um patch de
anti-pirataria em código MIPS), fora de qualquer região do editor. Detalhe da
comparação na seção 3 do [PLAN-LINUX.md](PLAN-LINUX.md).

**Sempre trabalhar sobre cópia** — o editor grava in-place e cada imagem tem
~474 MB.

## Arquitetura

### Camadas

O app é um diálogo MFC único e gigante mais 5 diálogos filhos. Não há separação
entre UI e dados: `edDlg.cpp` (8.456 linhas, 60% do código) contém a UI, os
offsets do formato binário, a lógica de codificação e o estado global.

- `ed.cpp` — `CWinApp::InitInstance`. O bloco OLE (`AfxOleInit`,
  `COleTemplateServer`, `COleObjectFactory`) é **vestigial**:
  `CEdDlgAutoProxy` só é forward-declared em `edDlg.h:14`, nunca implementado.
- `edDlg.cpp` / `edDlg.h` — diálogo principal. Contém os 69 `#define OFS_*`,
  `carica_dabin()` (leitura), `OnWriteCD()` (gravação),
  `kanjitoascii`/`asciitokanji` (`edDlg.cpp:732-773`), cálculo de custo,
  import SoFIFA.
- `giocatore` / `squadra` / `squadra_ml` / `tattica` — structs de domínio.
  `squadra.h:15-45` define `struct NUMERI` com bitfields `DWORD` lidos crus
  do disco (16 bytes).
- `graf.cpp`, `tattDlg.cpp`, `carattDlg.cpp`, `selezDlg.cpp`,
  `editOptForm.cpp` — diálogos filhos (bandeira/uniforme, táticas, atributos
  do jogador, seleção, opções).
- `myiotxt.cpp` — o único código já portável: libcurl + helpers de string.
- `ed.rc` — 6 diálogos, 393 controles. Continua em **ISO-8859-1** (14 × `°`
  em labels). Deliberado: o consumidor dele é o script conversor da Fase 4
  (que declara o encoding) e o `rc.exe` do MSVC, que quebraria com UTF-8 sem
  BOM. Ler sempre com encoding explícito.

### Formato da imagem: MODE2/2352 sector-aware

Setor PSX = 2352 bytes = 24 header + 2048 dados + 280 EDC/ECC. Os offsets
hardcoded **pulam os cabeçalhos de setor manualmente**:

```
OFS_NOMI_SQ1   = 1012640  → setor 430, byte 1280 (região de dados = 24..2071)
OFS_NOMI_SQ1_F = 1013431  → último byte de dados do setor 430
OFS_NOMI_SQ1A  = 1013736  → 1011360 + 2352 + 24 = 1º byte de dados do setor 431
```

Os `if (i == 40) fil_ctrl.Seek(OFS_NOMI_SQ1A, ...)` (`edDlg.cpp:1665-1667`) são
exatamente esses saltos. Consequências:

1. Não dá para extrair o arquivo do ISO9660 e editar — tem que ser o `.bin` cru.
2. O editor **não recalcula EDC/ECC** ao gravar. Comportamento original: um
   port deve **preservar**, não "corrigir".
3. Se um teste de round-trip falhar, a primeira suspeita é fronteira de setor.

### Padrões de código a conhecer

- **Repetição indexada em massa.** Handlers como `OnCarat1..23`,
  `OnSost1..23`, `OnChangeURL1..23`, `OnKillfocusNum1..23`,
  `OnKillfocusTatx2..11` são cópias literais que só variam o índice. 376
  `afx_msg` / 303 macros `ON_*`. Ao editar um, verifique se os 22 irmãos
  precisam da mesma mudança.
- **MSVC-only**: `_itoa` × 241.
- **Inseguro por design**: `strcpy`/`strcat` × 198 em buffers `char` fixos.
  MSVC tolerava. Não "consertar" isoladamente sem golden test — o
  comportamento de truncamento pode ser load-bearing no formato.
- Nomes de identificadores em **italiano** (`giocatore` = jogador, `squadra` =
  time, `tattica` = tática, `bandiera` = bandeira, `maglia` = camisa,
  `carat`/`caratteristiche` = atributos, `sost`/`sostituzione` =
  substituição, `nomi` = nomes, `costi` = custos, `numeri` = números).
- Zero desenho GDI. O único `OnPaint` (`edDlg.cpp:1493`) só desenha o ícone
  quando minimizado. O "campo tático" move `CButton`s com `MoveWindow`.

## Estado do repositório

Fase 1 (higiene) aplicada: `.gitignore` criado, artefatos de build fora do
versionamento. Rastreados 60 arquivos / ~1,2 MB; `.git` em ~470 KB.

Os artefatos continuam **no disco** (worktree ~276 MB) — `Debug/ed.exe` é o
oráculo dos golden tests, `ed.sdf` (68 MB) e `ipch/` são só peso morto
ignorado.

Remote: `git@github.com:aguilasa/new-we2002-editor.git`, branch padrão `main`.
O diretório local ainda se chama `WE2002-editor-2.0` — descasado do nome do
repo, mas inofensivo.

Encoding: `edDlg.cpp` e `selezDlg.cpp` foram convertidos para UTF-8. O resto
dos fontes é ASCII puro. Exceções que devem permanecer como estão:

- `ed.rc` — ISO-8859-1 (ver seção de arquitetura).
- `defaultlook.txt` — contém um `0x92` (apóstrofo curvo cp1252, em
  "Costa d'Avorio"). É **dado lido em runtime** por `edDlg.cpp:5165`;
  converter muda o que o parser enxerga.

Arquivos `debugio*.txt` / `debugread*.txt` na raiz são dumps de depuração do
autor, não fixtures de teste.
