# Plano de portabilidade — WE2002 Editor

> **Objetivo: aplicação multiplataforma, Linux e Windows.**
>
> | Plataforma | Situação |
> |---|---|
> | **Linux** (Debian/Ubuntu) | Alvo primário. Todo o esforço inicial vai aqui. |
> | **Windows** | Alvo suportado, atacado **depois** que o Linux estiver redondo. |
> | **macOS** | **Fora de escopo.** Não portar, não testar, não empacotar. |
>
> Windows ser "depois" é ordem de trabalho, não segunda classe: as decisões
> técnicas são tomadas desde já sem barrar o Windows. Na prática isso significa
> um único `CMakeLists.txt` para as duas plataformas, nada de API específica de
> SO fora de uma camada isolada, e nenhuma suposição de caminho estilo POSIX.
> O que **não** significa é gastar tempo com Windows antes do Linux fechar.
>
> Fora de escopo não é "talvez depois": macOS não entra nas matrizes de CI, nem
> nos scripts de empacotamento, nem justifica `#ifdef`.
>
> Data da análise: 2026-07-30
> Estratégia acordada: **A (Bottles/Wine agora) + C (port real para Qt6)**
>
> Progresso: Fases 0 a **7 concluídas**. O escopo Linux fechou na Fase 6; a
> Fase 7 (Windows) foi executada em 2026-08-04 e o registro está na seção 11 do
> [PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md).
>
> O Qt6 (6.4.2) foi instalado na Fase 5; o `find_package(Qt6)` do
> `CMakeLists.txt` da raiz acha e compila o `src/app`.
>
> **Desde 2026-08-05 o import do SoFIFA está desligado**, por decisão: fica em
> último plano até a paridade com o `ed.exe` estar conferida tela a tela. O
> código continua compilado; só ficou inalcançável pela janela, via
> `app::SOFIFA_ENABLED` em [src/app/Features.hpp](../src/app/Features.hpp). O
> inventário de paridade e o roteiro do que falta clicar estão em
> [PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md).

---

## 1. Diagnóstico do código

App MFC clássico (VC6 → migrado para VS2010). Editor de imagem de CD do
Winning Eleven 2002 (PSX).

### Métricas

| Item | Valor |
|---|---|
| C++ total | 13.929 linhas |
| `edDlg.cpp` | 8.456 linhas (60% do total) |
| Diálogos em `ed.rc` | 6 |
| Controles no `.rc` | 434 (ver Fase 4; a contagem antiga de 393 estava baixa) |
| `DDX_Control` | 319 |
| `afx_msg` handlers | 376 |
| Macros `ON_*` | 303 |
| `Get/SetWindowText` | 799 |
| `CFile::` | 199 |
| `_itoa` (MSVC-only) | 241 |
| `strcpy` / `strcat` | 198 |
| `#define OFS_*` | 69 |

Config do projeto: `UseOfMfc=Static`, `CharacterSet=MultiByte` (MBCS, não
Unicode), linka `libcurl.lib`. O binário publicado em `Debug/ed.exe` é
**PE32+ x86-64**.

### Dependências Windows

**Bloqueadores reais**

- MFC inteiro: `CWinApp`, `CDialog`, DDX/DDV, message maps,
  `CEdit`/`CComboBox`/`CButton`/`CStatic`, `CFileDialog`, `AfxMessageBox`,
  `CFile`.
- CRT MSVC: `_itoa` × 241.

**Triviais**

- `GetModuleFileName` × 11, `GetSystemMetrics`, `DrawIcon`, `IsIconic`,
  `MoveWindow` × 12.
- OLE: `AfxOleInit`, `COleTemplateServer::RegisterAll`,
  `COleObjectFactory::UpdateRegistryAll` em `ed.cpp:42-76`. **Vestigial** —
  `CEdDlgAutoProxy` só é forward-declared em `edDlg.h:14`, nunca implementado.
  Deletar tudo.

**Já portável**

- libcurl em `myiotxt.cpp` — host tem libcurl 8.5.0.
- `<fstream>`, `<string>`, `<vector>`, `<map>`.

**Notícia boa: zero desenho GDI.** Nenhum `CDC`, `CPen`, `CBrush`, `CBitmap`,
`BitBlt`. O único `OnPaint` (`edDlg.cpp:1493`) só desenha o ícone quando
minimizado. O campo tático usa `MoveWindow` sobre `CButton`, não pintura.

### Armadilhas de portabilidade

1. **Bitfields `DWORD`** em `struct NUMERI` (`squadra.h:15-45`) lidos crus:
   `fil_ctrl.Read(&squad_nazall[i].stc_numeri, 16)` (`edDlg.cpp:1929`).
   MSVC e GCC concordam em x86-64 little-endian para bitfields do mesmo tipo,
   mas precisa `static_assert` + teste golden. Não assumir.
2. **Encoding dos fontes**: `.cpp`/`.rc` são ISO-8859-1 (strings tipo
   `"1° Name"`). Converter para UTF-8 ou usar `-finput-charset=ISO-8859-1`.
3. **`char` signedness**: MSVC e GCC/x86 = signed. Fixar `-fsigned-char`
   (ARM difere).
4. **`strcpy` em buffers fixos** × 146. MSVC tolerava; GCC com
   `_FORTIFY_SOURCE` + ASan vai expor bugs latentes reais.
5. **Estado global** espalhado em `edDlg.cpp` — dificulta extrair o core.

### Higiene do repositório

347 MB. Artefatos commitados: `ed.sdf` (68 MB), `ipch/`, `Debug/` (com
`ed.exe`), `Release/`, `ed.suo`, `ed.ncb`, `ed.opt`,
`_UpgradeReport_Files/`. Sem `.gitignore`.

---

## 2. Formato da imagem — descoberta crítica

Formato: **MODE2/2352 raw** (sync `00 FF×10 00` no byte 0, confirmado pelo
`.cue`). Setor de 2352 bytes = 24 header + 2048 dados + 280 EDC/ECC.

Os offsets do autor são **calibrados nas fronteiras de setor**:

```
OFS_NOMI_SQ1   = 1012640  → setor 430, byte 1280 (dentro da região 24..2071)
OFS_NOMI_SQ1_F = 1013431  → exatamente o último byte de dados do setor 430
OFS_NOMI_SQ1A  = 1013736  → 1011360 + 2352 + 24 = 1º byte de dados do setor 431
```

Os `if(i == 40) fil_ctrl.Seek(OFS_NOMI_SQ1A, ...)` em `edDlg.cpp:1665-1667`
são pulos manuais de cabeçalho de setor. Presumir que os 69 `OFS_*` seguem a
mesma lógica.

Os nomes acima são os do legado. No port eles se chamam `OFS_TEAM_NAME_1`,
`_1_END` e `_1_A` desde a Fase 3.5; `Offsets.hpp` carrega o nome antigo em
comentário para os dois lados continuarem grepáveis.

**Duas consequências para o port:**

1. Não dá para extrair o arquivo do ISO9660 e editar. Tem que ser o `.bin` cru.
2. O editor **não recalcula EDC/ECC** ao gravar. Comportamento original — o
   port deve **preservar**, não "corrigir". Se um golden test falhar, a
   primeira suspeita é fronteira de setor.

---

## 3. Ambiente validado

### Dependências do host

Zorin OS 18.1, base Ubuntu noble.

| O quê | Situação | Para quê |
|---|---|---|
| GCC, CMake ≥ 3.21 | ✅ | core e testes |
| libcurl | ✅ 8.5.0 | import do SoFIFA |
| Python 3 | ✅ | os geradores em `tools/` |
| Wine (runner soda do Bottles) | ✅ | rodar o `ed.exe`, oráculo dos golden tests |
| Xvfb no `:98`, `xdotool`, `import` | ✅ | validação visual |
| Qt 5.15.13 | ✅ | fallback do `tools/uipreview` da Fase 4 |
| Qt6 6.4.2 | ✅ instalado na Fase 5 | a aplicação |

```sh
sudo apt install qt6-base-dev qt6-base-dev-tools qt6-tools-dev
```

O `universe` do noble tem Qt **6.4.2**, que serve: o
`qt_standard_project_setup()` usado pelo `CMakeLists.txt` da raiz existe desde
o 6.3. Sem Qt6 o `find_package(Qt6)` falha e a raiz pula `src/app` — o core e
os testes continuam compilando, mas não há aplicação.

### Bottles / Wine — Fase 0 **já testada e funcionando**

Runner `soda-9.0-1` invocável direto do host com `WINEPREFIX`, mesmo padrão
usado em `/home/ingmar/desenvolvimento/snes/Makefile:55-56`.

```sh
WINEPREFIX=<prefix> \
/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin/wine64 \
  ed.exe
```

Verificado em 2026-07-30: `ed.exe` sobe e abre o diálogo
`IMAGE CD SELECTION`; fontes e controles renderizam corretamente.

Observações:

- `ed.exe` é x86-64; o runner soda só tem `x86_64-windows`. Casa perfeito,
  sem necessidade de WoW64 / 32-bit.
- `wineboot` reclama de FreeType — benigno, as fontes renderizaram.
- `/etc/ld.so.preload` tem `libAppProtection.so` (Citrix) gerando ruído no
  stderr. Ignorável.
- **Usar bottle dedicada, não reusar a `DiztinGUIsh`**: `ed.cpp:75` chama
  `COleObjectFactory::UpdateRegistryAll()`, que escreve no registry do prefix.
- Existe `Debug/WE2002.bin.lnk` (atalho do autor original). Recriar apontando
  para a imagem local.

### Imagens de CD disponíveis

Testados 4 offsets do editor em cada imagem:

| Offset | European Deluxe | Japan multi-track | Japan arquivo único | PES2 Europe |
|---|---|---|---|---|
| `1012640` `NOMI_SQ1` | `AEK KIEV GALATASARAY` ✅ | `PATAGONIA MARMARA` ✅ | `PATAGONIA MARMARA` ✅ | idem Japan ✅ |
| `387792` `NOMI_G` | `Toldo` ✅ | Shift-JIS ✅ | Shift-JIS ✅ | `Dyer` ✅ |
| `2002316` `NOMI_SQK` | Shift-JIS ✅ | Shift-JIS ✅ | Shift-JIS ✅ | tabela de ponteiros ❌ |
| `5651448` `NOMI_SQ6` | `AEK KIEV` ✅ | katakana ✅ | katakana ✅ | texto de erro francês ❌ |

**Veredito:**

- Winning Eleven 2002 – European Deluxe 2002-03 → **imagem golden.** Todos os
  offsets batem, nomes latinos, fácil de inspecionar visualmente.
- World Soccer Winning Eleven 2002 (Japan), dump de arquivo único → **melhor
  imagem japonesa.** Ver comparação abaixo.
- A mesma release em dump multi-track → compatível, mas redundante com a
  anterior e com ECC degradado.
- `Pro Evolution Soccer 2 (Europe) (EnFrDe)` → **NÃO USAR.** Layout diverge
  depois de ~2 MB; o editor grava por cima de outros dados e corrompe a imagem.

As duas escolhidas ficam em **`roms/`, na raiz do repositório** — pasta fora do
versionamento (`.gitignore`), mantida pelo usuário. As outras duas não estão
lá, de propósito. Os arquivos foram renomeados pelo papel que cumprem:

| Arquivo | Release |
|---|---|
| `golden-european-deluxe.bin` (+ `.cue`) | European Deluxe 2002-03 |
| `japanese-shift-jis.bin` | SLPM-87056, arquivo único |

### Os dois dumps japoneses

São a **mesma release** (SLPM-87056), dumps diferentes. Comparação byte-a-byte
dos primeiros 14 MiB — a faixa que cobre todos os 69 offsets do editor, o maior
sendo `OFS_BANDIERE_COLORE2` = 12552648:

| | `World Soccer Winning Eleven 2002/` | `... 2002 (Japan)/` |
|---|---|---|
| Forma | arquivo único, 307.187.664 B | 9 tracks, Track 1 = 306.834.864 B |
| Setores | 130.607 | 130.457 |
| Origem | CoolROM (tem `readme.html` deles) | — |
| Tracks de áudio | **ausentes** (~160 MiB não estão no arquivo) | presentes (tracks 2–9) |
| `.cue` | nenhum — o que vinha era inválido e foi removido | válido |
| ECC | íntegro (0/300 setores amostrados zerados) | **degradado (211/300 zerados)** |

Divergências nos 14 MiB, classificadas por posição dentro do setor:

| Região do setor | Bytes divergentes |
|---|---|
| ECC (2076..2351) | 14.356 |
| EDC (2072..2075) | 8 |
| **Dados (24..2071)** | **3** |

Os 3 bytes de dados estão em `1922552`, `1922553` e `1924018` — no vão entre
`OFS_NOMI_SQ2` (1881968) e `OFS_BANDIERE_FORMA1` (1929004), ou seja, **fora de
qualquer região que o editor toca**. São instruções MIPS: em `1924018` o
`0x1040` (`BEQ`) vira `0x1000` (`BEQ $zero,$zero`, salto incondicional). É o
padrão de um patch de anti-pirataria. O dump de arquivo único é a versão
modificada.

Os 352.800 bytes a mais (150 setores, o pregap de 2 s) são **zeros no fim** do
arquivo — não deslocam nada.

**Qual usar:** `World Soccer Winning Eleven 2002/` (arquivo único), pelo ECC
íntegro. E aqui está o ponto que importa: o editor **não recalcula EDC/ECC ao
gravar** (seção 2). Num dump com ECC já zerado esse comportamento fica
invisível — não há o que corromper. Com ECC íntegro, gravar produz ECC
inválido de um jeito específico, e o golden test passa a verificar que o port
reproduz **exatamente** o mesmo ECC inválido que o `ed.exe`. É um teste
estritamente mais forte.

Esse dump **não serve para jogar**: contém só a track de dados. As 8 tracks de
áudio (167.949.264 B) não estão no arquivo — uma imagem completa teria
474.784.128 B. O `.cue` que vinha junto declarava 9 tracks apontando para
arquivos inexistentes; foi removido, já que qualquer `.cue` válido ali
produziria um jogo sem música.

Irrelevante para este projeto: o editor abre o `.bin` direto e nunca lê `.cue`.
Para jogar a versão japonesa em emulador, usar
`World Soccer Winning Eleven 2002 (Japan)/`, que tem as 9 tracks e um `.cue`
válido.

---

## 4. Opções avaliadas

| Opção | Esforço | Resultado |
|---|---|---|
| **A. Bottles/Wine** | feito | Roda hoje. Não é port, e sem caminho de rebuild (MFC estático exige MSVC). Serve como **oráculo de referência**. |
| **B. MinGW-w64 cross** | — | **Inviável.** MinGW não tem MFC. Winelib idem — Wine não distribui MFC. |
| **C. Core portável + Qt6** | ~1,5–2 semanas | Port real, nativo. **Escolhido.** |
| **D. Core portável + CLI/web** | ~1 semana | Modernização; perde paridade de UI. |

---

## 5. Estrutura do projeto

### Por que a atual não serve

Hoje os 60 arquivos estão todos jogados na raiz: fonte, projeto do Visual
Studio, ícones, dados de runtime e dumps de depuração misturados. Isso
funcionava porque o Visual Studio lia o `ed.vcxproj` e não se importava com
pastas. Para um projeto C++/Qt multiplataforma, três coisas faltam:

1. **Separação entre biblioteca e aplicação.** O objetivo do port é ter a
   lógica de leitura/gravação do `.bin` isolada da interface. Se tudo mora no
   mesmo lugar, é fácil a UI vazar para dentro da lógica — que é exatamente a
   doença do `edDlg.cpp` atual.
2. **Um build que funcione fora do Visual Studio.** Não existe `CMakeLists.txt`;
   sem ele não há como compilar no Linux nem no Windows com outro compilador.
3. **Lugar para o que não é código de produção** — testes, scripts, dados de
   fixture, e o próprio código MFC antigo que vira material de referência.

### Vocabulário mínimo

Termos que aparecem daqui pra frente:

| Termo | O que é |
|---|---|
| **Header** (`.hpp`) | Arquivo que **declara** o que existe (nomes de funções, classes). Outros arquivos fazem `#include` dele para saber que aquilo existe. |
| **Implementação** (`.cpp`) | Arquivo que **define** como aquilo funciona. É o que de fato é compilado. |
| **Header público vs privado** | Público = fica em `include/`, é a API que o resto do projeto pode usar. Privado = fica junto do `.cpp`, é detalhe interno. |
| **Target** | Unidade que o CMake constrói: uma biblioteca ou um executável. Este projeto terá três. |
| **CMake** | O sistema de build padrão de C++ hoje. Um `CMakeLists.txt` descreve os targets; o CMake gera Makefiles no Linux e projetos do Visual Studio no Windows a partir do **mesmo** arquivo. É isso que dá o multiplataforma. |
| **Build out-of-source** | Compilar dentro de `build/`, nunca misturado ao fonte. É o que permite jogar tudo fora com `rm -rf build/`. |
| **moc / uic / rcc** | Geradores de código do Qt. `moc` processa classes com sinais e slots; `uic` transforma arquivos `.ui` (layout) em C++; `rcc` embute recursos (ícones) no binário. O CMake roda os três sozinho — ver `AUTOMOC` abaixo. |

### Árvore alvo

```
new-we2002-editor/
├─ CMakeLists.txt              # raiz: acha o Qt, agrega os subdiretorios
├─ CMakePresets.json           # perfis nomeados: debug-asan, release, ...
│
├─ src/
│  ├─ core/                    # libwe2002 — logica pura. ZERO Qt, ZERO UI.
│  │  ├─ CMakeLists.txt
│  │  ├─ include/we2002/       # API publica
│  │  │  ├─ CdImage.hpp        #   abrir/ler/gravar a imagem MODE2/2352
│  │  │  ├─ Offsets.hpp        #   os 69 OFS_*, hoje presos no edDlg.cpp
│  │  │  ├─ Player.hpp         #   ex-giocatore
│  │  │  ├─ Team.hpp           #   ex-squadra / squadra_ml
│  │  │  ├─ Tactics.hpp        #   ex-tattica
│  │  │  ├─ TextCodec.hpp      #   kanjitoascii / asciitokanji
│  │  │  └─ SofifaImport.hpp   #   ex-myiotxt + parser
│  │  └─ *.cpp
│  │
│  └─ app/                     # o executavel Qt
│     ├─ CMakeLists.txt
│     ├─ main.cpp
│     ├─ MainWindow.{hpp,cpp}
│     ├─ ui/                   # .ui gerados na Fase 4 a partir do ed.rc
│     │  └─ controls.json      #   estilos Win32 que o .ui nao expressa
│     └─ resources/app.qrc     # icone etc, embutidos no binario
│
├─ tests/                      # golden tests da Fase 3
│  ├─ CMakeLists.txt
│  ├─ test_main.cpp            # os 61 checks
│  ├─ golden_tool.cpp          # metade headless do golden test
│  └─ fixtures/                # dados pequenos; NUNCA imagens de CD
│
├─ tools/                      # scripts de apoio, nao entram no binario
│  ├─ rc2ui.py                 # conversor .rc -> .ui (Fase 4)
│  ├─ uipreview/               # renderiza um .ui em PNG p/ conferir (Fase 4)
│  ├─ golden_run.sh            # dirige o ed.exe sob Wine (Fase 3)
│  ├─ golden_compare.py        # diff anotado por OFS_/setor (Fase 3)
│  ├─ golden_check.sh          # oraculo + port + diff = o teste `golden`
│  ├─ glossary.py              # o mapa italiano->ingles (Fase 3.5)
│  └─ apply_glossary.py        # aplica o mapa nos fontes escritos a mao
│
├─ legacy/                     # fonte MFC original — referencia, nao compila
│  └─ mfc/                     # edDlg.cpp, ed.rc, res/, ed.vcxproj...
│
├─ data/                       # dados lidos em runtime
│  ├─ defaultlook.txt
│  └─ naz.txt
│
└─ docs/                       # PLAN-LINUX.md, notas de formato
```

### A regra que mais importa

**`src/core/` não pode incluir nada de Qt.** Nem `QString`, nem `QFile`. Só
biblioteca padrão de C++ e libcurl.

Isso não é purismo. É o que torna a Fase 3 possível: os golden tests precisam
rodar sem abrir janela nenhuma, comparando bytes. Se o núcleo depender do Qt,
todo teste vira teste de GUI — lento, frágil e impossível de rodar em CI. É
também o que deixa a porta aberta para uma versão CLI ou web depois, sem
reescrever a lógica.

A direção de dependência é de mão única: `app` → `core`. Nunca o contrário.

### Os três targets

| Target | Tipo | Depende de |
|---|---|---|
| `we2002_core` | biblioteca estática | libcurl |
| `newWe2002` | executável | `we2002_core`, `Qt6::Widgets` |
| `we2002_tests` | executável de teste | `we2002_core` |

Esqueleto do `CMakeLists.txt` da raiz:

```cmake
cmake_minimum_required(VERSION 3.21)
project(newWe2002 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# O codigo herdado assume char SIGNED (padrao do MSVC e do GCC em x86).
# GCC/Clang: fixar explicitamente, porque em ARM o padrao e unsigned.
# MSVC: nao mexer — ja e signed; a flag /J inverteria isso e quebraria tudo.
if(NOT MSVC)
    add_compile_options(-fsigned-char)
else()
    add_compile_options(/utf-8)   # fontes sao UTF-8; sem isso o MSVC assume a codepage ANSI
endif()

find_package(Qt6 REQUIRED COMPONENTS Widgets)
qt_standard_project_setup()      # liga AUTOMOC/AUTOUIC/AUTORCC

add_subdirectory(src/core)
add_subdirectory(src/app)

enable_testing()
add_subdirectory(tests)
```

Compilar (idêntico nas duas plataformas):

```sh
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build
```

O mesmo `CMakeLists.txt` gera Makefile no Linux e solução do Visual Studio no
Windows. É esse o mecanismo que entrega o multiplataforma — não há projeto
separado a manter.

### Suporte a plataformas

O que muda entre as duas, e o que precisa estar decidido desde já para não
travar o Windows depois.

| | Linux (primário) | Windows (depois) |
|---|---|---|
| Compilador | GCC ou Clang | MSVC preferido; MinGW-w64 também serve |
| Qt 6 | `apt install qt6-base-dev` (6.4.2 no Zorin/Ubuntu atual) | Instalador oficial do Qt, ou vcpkg |
| libcurl | `apt install libcurl4-openssl-dev` (8.5.0) | vcpkg, ou `FetchContent` no CMake |
| CMake | `apt install cmake` (3.28.3) | acompanha o Visual Studio |
| Empacotamento | AppImage ou Flatpak | `windeployqt` + Inno Setup, ou zip portátil |

Com o MFC fora do caminho, o MinGW-w64 volta a ser viável — era descartado
(seção 4, opção B) só porque não distribui MFC. Isso abre inclusive a
possibilidade de *cross-compilar* o `.exe` a partir do Linux, útil para
smoke-test antes de ter uma máquina Windows na mão.

Regras para não criar dívida de portabilidade enquanto se trabalha só no Linux:

- **Caminhos**: `std::filesystem::path`, nunca concatenação de string com `/`.
  O código herdado usa `char[MAX_PATH]` e `strcat`; isso morre na Fase 2.
- **Arquivos binários**: sempre `std::ios::binary`. No Windows, sem isso o
  runtime traduz `0x0A` ↔ `0x0D 0x0A` e **corrompe a imagem de CD**. É a
  armadilha mais séria da lista.
- **`#ifdef`**: só dentro de uma camada fina e isolada. Se começar a espalhar
  pelo `core`, o desenho está errado.
- **Nada de `windows.h` nem de POSIX no `core`.** Só biblioteca padrão e
  libcurl — a mesma regra que já proíbe o Qt ali.
- **CI**: matriz com `ubuntu-latest` e `windows-latest` desde o primeiro
  workflow, mesmo que o Windows comece vermelho. Sem macOS. (Desde a Fase 7 a
  matriz existe mas só roda por `workflow_dispatch` — ver a seção do `ci.yml`
  na Fase 6.)

### Para onde vai cada arquivo de hoje

| Hoje na raiz | Destino |
|---|---|
| `edDlg.cpp`, `edDlg.h` | Fatiado: offsets e I/O → `src/core/`; UI → `src/app/`. Cópia integral fica em `legacy/mfc/`. |
| `giocatore.*`, `squadra*.*`, `tattica.*` | `src/core/` (renomeados para inglês) |
| `myiotxt.*` | `src/core/` — já é portável |
| `graf.cpp`, `tattDlg.cpp`, `carattDlg.cpp`, `selezDlg.cpp`, `editOptForm.cpp` | Reescritos em `src/app/`; originais em `legacy/mfc/` |
| `ed.cpp`, `StdAfx.*`, `gui.*` | Descartados. `main.cpp` novo os substitui. |
| `ed.rc`, `resource.h`, `res/` | `legacy/mfc/` — vira entrada do `tools/rc2ui.py` |
| `ed.vcxproj`, `ed.sln`, `ed.dsp`, `ed.dsw`, `ed.vcproj`, `ed.clw`, `ed.odl`, `ed.reg` | `legacy/mfc/`. Substituídos pelo CMake. |
| `defaultlook.txt`, `naz.txt` | `data/` |
| `SOFIFA attributes.txt`, `WE attributes conversion rules.txt` | `data/` |
| `libcurl.dll` | Removido. No Linux vem do sistema; no Windows, do gerenciador de pacotes do CMake. |
| `debugio*.txt`, `debugread*.txt` | `docs/samples/` ou apagados — são dumps HTML do SoFIFA de 2015 |
| `Debug/ed.exe` | Fora do git, mas **fica no disco**: é o oráculo da Fase 3 |

### Quando fazer

**No início da Fase 2, antes de escrever qualquer código novo.** Mover arquivo
depois que já existe código novo referenciando os caminhos antigos custa mais.

Duas consequências a lembrar: mover os fontes MFC para `legacy/mfc/` invalida
todas as referências de caminho do `CLAUDE.md`, que precisa ser atualizado no
mesmo commit; e como o git detecta renomeação, o histórico dos arquivos
sobrevive desde que o movimento seja commitado sem alterações de conteúdo
misturadas.

---

## 6. Fases

### Fase 0 — Rodar via Bottles ✅ validado

Falta apenas: criar a bottle dedicada e o wrapper (`Makefile` no padrão do
projeto snes).

### Fase 1 — Higiene ✅ concluída

- `.gitignore` criado; artefatos fora do versionamento (60 arquivos / ~1,2 MB).
- `Debug/ed.exe` mantido no disco, fora do git — é o oráculo da Fase 3.
- `edDlg.cpp` e `selezDlg.cpp` convertidos para UTF-8. `ed.rc` (entrada do
  `rc2ui.py`) e `defaultlook.txt` (dado de runtime) mantidos no encoding
  original de propósito.
- Histórico reescrito a partir de um commit raiz novo; `.git` de 72 MB → 470 KB.
- Repo movido para `aguilasa/new-we2002-editor` (standalone, branch `main`); o
  fork antigo foi deletado. Original permanece em
  `thyddralisk/WE2002-editor-2.0`.
- `README.md` e `NOTICE.md` documentando linhagem e ausência de licença.

### Fase 2 — Core portável `libwe2002` ✅ concluída

Árvore reorganizada conforme a seção 5. `we2002_core` compila com g++ sob
`-Wall -Wextra` sem um único warning, e não linka Qt nem API de plataforma.

Como foi feito: `carica_dabin` (696 linhas) e `OnWriteCD` (663) **não foram
retipadas**. `tools/port_database.py` extrai os corpos verbatim do legacy e
aplica uma lista auditável de substituições; o que ele não reconhece sobra e
quebra a compilação de propósito. `tools/extract_legacy_data.py` faz o mesmo
com os 69 offsets e as 15 tabelas. Ambos são reexecutáveis e o resultado é
commitado.

- `CFile` → `CdImage` (`std::fstream`, sempre `std::ios::binary`), com
  `Seek`/`SeekCurrent`/`Read`/`Write` imitando a semântica do `CFile`,
  inclusive ponteiro de arquivo único e leitura curta não sendo erro.
- `AfxMessageBox` → `Reporter` (`std::function`) injetado.
- `CString`/`_itoa` eliminados; caminho é `std::filesystem::path`.
- OLE de `ed.cpp` descartado junto com o resto do app MFC.
- Estado global (`gioc[]`, `squad_nazall[]`, `squad_ml[]`, `tattpred[]`) virou
  a classe `Database`.
- Testes: 61 checks, sem framework externo. Cobrem layout de bits de
  `SquadNumbers`, aritmética de setor, round-trip do codec, empacotamento de
  atributos, `CdImage` e as tabelas geradas.

**Dois bugs reais encontrados:**

1. **`DWORD` nos bitfields de `NUMERI`.** `DWORD` é 32-bit no Windows e 64-bit
   no Linux LP64 — manter o tipo teria embaralhado todos os números de camisa
   silenciosamente. Agora é `std::uint32_t`, com `static_assert` de tamanho e
   teste de posição de bits.
2. **Estouro de array no original.** `squadra squad_nazall[63]` com três laços
   indo até 64 (`edDlg.cpp:1928`, `:5821`, `:7667`), lendo e gravando 16 bytes
   além do fim. É UB, não comportamento: no Windows sujava o global seguinte,
   no Linux cai em outro lugar. Corrigido dando ao array os 64 slots que o
   disco realmente tem (`TEAMS_NAZALL_SLOTS`).

**Resultado dos sanitizers:** ASan + UBSan rodam **limpos**, tanto na suíte
completa contra a imagem real quanto num ciclo `Load` + `Save` — zero erros de
memória nas duas funções geradas.

Chegar lá exigiu contornar a Citrix. Ela põe `libAppProtection.so` em
`/etc/ld.so.preload`, e essa lib exporta o próprio `dlsym`. O runtime do ASan
chama `dlsym(RTLD_NEXT, "malloc")` antes de libc subir, e com o `dlsym` da
Citrix no caminho o processo morre antes do `main`, sem output —
`-static-libasan` não ajuda, porque o problema não é ordem de carregamento.
`tools/run-sanitized.sh` resolve entrando num user+mount namespace sem
privilégio e mascarando o `/etc/ld.so.preload` só para aquele processo. Em CI
não há preload nenhum e o wrapper vira no-op.

### Fase 3 — Golden tests ✅ concluída

O método: rodar o `ed.exe` original sob Wine e o port headless sobre **cópias
da mesma imagem**, no mesmo ciclo abrir → gravar, e comparar byte a byte. Onde
os dois discordam, o port está errado até prova em contrário.

Três peças novas:

| Arquivo | Papel |
|---|---|
| `tests/golden_tool.cpp` | metade headless — `roundtrip` e `digest` sobre o core |
| `tools/golden_run.sh` | metade oráculo — dirige o `ed.exe` com `xdotool` no `:98` |
| `tools/golden_compare.py` | diff que agrupa em faixas e anota `OFS_*`, setor e se caiu em dados ou em EDC/ECC |
| `tools/golden_check.sh` | junta os três e decide passa/falha; é o teste `golden` do ctest |

Dirigir uma caixa de diálogo MFC com `xdotool` funciona porque o layout é fixo
em tempo de compilação: as coordenadas saem direto do `ed.rc`, convertidas de
DLU com as base units 6×13 do "MS Sans Serif" 8pt. Daí `IDD_ED_DIALOG` de
718×337 DLU virar 1077×548 px e o `CMB_WRITE` cair em (315, 521).

**Resultado.** Oráculo e port produzem imagens **byte-idênticas**, com uma
única exceção documentada:

| Caso | Divergência |
|---|---|
| European Deluxe, gravação limpa | só a faixa `405724..405739` |
| Japonesa (SLPM-87056, arquivo único) | só a faixa `405724..405739` |
| European Deluxe com uma edição de nome pela GUI | **nenhuma** |
| Oráculo aplicado 2× vs oráculo depois port | **nenhuma** |

A imagem japonesa importa mais do que parece: nela o oráculo reescreve 1.097
bytes de nomes em Shift-JIS (`OFS_NOMI_SQK`) e o port reescreve exatamente os
mesmos. `kanjitoascii`/`asciitokanji` estão fiéis.

#### O bug que os golden tests pegaram

O `Load` posicionava a tabela de custos da Master League no lugar errado.
Causa: uma substituição do `tools/port_database.py`. A classe `[^,]` casa
`\n`, então depois que a regra de `CFile::begin` reescreveu a primeira linha,
a regra de `CFile::current` casou a partir *dela* atravessando a quebra de
linha até o `, CFile::current)` da linha seguinte — trocando as duas:

```c
// legacy                                    // gerado, errado
Seek(OFS_COSTI_NAZ, CFile::begin);           SeekCurrent(OFS_COSTI_NAZ);
    Seek(2, CFile::current);                     Seek(2);
```

Compilava, passava nos 61 checks e passava limpo no ASan — só a comparação
contra o `ed.exe` expôs os 1.394 bytes errados. Corrigido em duas frentes:
`[^,\n]` nas duas regras, e um guard novo, `check_seeks()`, que conta seeks
absolutos e relativos no legado e na saída e recusa gerar se os números não
baterem. O `FORBIDDEN` não pegava isso porque nenhum token MFC sobrava.

#### As três faixas que o "ponto de partida" apontava

Todas explicadas, nenhuma é bug do port:

| Faixa | Veredicto |
|---|---|
| `OFS_PLAYER_ATTR_8` (204 bytes) | comportamento original — as all-star são reconstruídas a partir dos links no `Save`. Oráculo faz igual. |
| `OFS_KICKER` (66 bytes) | **bug do original, reproduzido de propósito.** Ver abaixo. |
| `OFS_COST_NATIONAL` (1.394 bytes) | era o bug do gerador. Zerado. |

O `OFS_KICKER` merece nota: `Load` lê os cobradores de ML trocados
(`kik_punl = auxstr[1]`, `kik_punc = auxstr[0]`) e `Save` grava na ordem
declarada, então **cada gravação troca o par**. O editor não é idempotente:
gravar duas vezes devolve o estado inicial. Confirmado nos dois lados — o
oráculo aplicado duas vezes dá um arquivo idêntico ao oráculo seguido do port.

#### A única divergência aceita

`405724..405739`, 16 bytes, `OFS_SQUAD_NUMBERS_NATIONAL+1008` — o slot 64 de
um array de
63. É o estouro já descrito na Fase 2 (`edDlg.cpp:1928`, `:5821`, `:7667`). O
original lê e grava 16 bytes do que vier depois na memória, que é
`squad_ml[0]`; daí os bytes Shift-JIS de nome de clube que aparecem lá
(`5a6b 5a6b 5a6b 734e …`). É determinístico no Windows por acidente do layout
do linker, não por design.

O port dá ao array os 64 slots que o disco tem, lê esses 16 bytes da imagem e
grava de volta sem mexer. Reproduzir o estouro seria reproduzir comportamento
indefinido cujo valor depende do compilador — recusado de propósito e fixado
no `tools/golden_check.sh` como a **única** faixa tolerada.

#### Como rodar

```sh
WE2002_GOLDEN_IMAGE=/caminho/imagem.bin ctest --test-dir build -R golden
```

Sem a variável o teste se reporta como *skipped*, não como falha: ele precisa
de uma imagem de ~474 MB, do `Debug/ed.exe` e de Wine com display X — nada
disso existe em CI. A imagem de origem não é tocada; o script faz duas cópias
num diretório temporário e apaga no fim. Rodando na European Deluxe leva ~20 s.

### Fase 3.5 — Nomenclatura em inglês ✅ concluída

**Não existe mais identificador em italiano fora de `legacy/`.** Membros,
offsets, tabelas, variáveis locais e comentários do código gerado, todos
traduzidos. Feito aqui e não antes porque os golden tests da Fase 3 são a rede
de segurança: uma renomeação em massa que não muda comportamento é exatamente
o que eles sabem provar. E antes da Fase 5, porque é lá que se escreve o
grosso do código de UI referenciando esses campos.

O escopo passou do que estava listado: além dos membros e dos comentários,
foram os 69 `OFS_*` e as 15 tabelas geradas. Deixar `OFS_NOMI_SQ1` e
`LUN_NOMI1` de fora atenderia à letra da lista mas não ao critério de pronto,
e são exatamente os nomes que a Fase 5 vai ler o tempo todo.

#### Método

O mapa vive num lugar só, [tools/glossary.py](../tools/glossary.py), porque
tem três consumidores:

| Consumidor | O que renomeia |
|---|---|
| `tools/port_database.py` | `Database.cpp` (gerado a cada execução) |
| `tools/extract_legacy_data.py` | `Offsets.hpp`, `Tables.hpp`, `Tables.cpp` |
| `tools/apply_glossary.py` | os fontes escritos à mão |

Renomear os arquivos gerados à mão seria jogar o trabalho fora na próxima
execução do gerador — daí o mapa compartilhado. `apply_glossary.py --check`
acusa italiano que tenha voltado, e roda sobre os arquivos gerados também.

Três detalhes que custaram uma iteração cada:

1. **Renomear dentro de string literal.** O rename cego trocou
   `"clubes ML com nome"` por `"...com name"` nas mensagens em português do
   teste. Regra final: nome em CAIXA ALTA é renomeado em todo lugar (dentro
   de string ele quase sempre é um rótulo espelhando o identificador, como em
   `{"OFS_NOMI_SQ1", OFS_NOMI_SQ1}`); nome em minúscula, só fora de string.
2. **Ordem em relação aos guards.** O glossário roda **depois** de
   `check_forbidden` e `check_seeks` no `port_database.py`. Esses guards são
   escritos contra a grafia do legado; rodar antes obrigaria a manter duas
   versões de cada padrão.
3. **Rastreabilidade.** `legacy/mfc/` fica na árvore para sempre, então cada
   offset renomeado carrega o nome antigo em comentário — `// was
   OFS_NOMI_SQ1` — e grepar um nome nas duas árvores continua achando as duas
   pontas.

#### Duas correções de semântica

A tradução obrigou a ler o que cada campo faz, e dois nomes estavam
documentados errado:

- **`nome_m` não é "long name".** O `_m` é de *minuscolo*. O campo tem o nome
  do time em caixa mista — "Bayern", "Galatasaray" — contra os slots
  `nomi[]` em caixa alta ("INTER"). Virou `mixed_case_name`, e a tabela de
  comprimentos `LUN_NOMI_MIN` virou `TEAM_MIXED_CASE_NAME_LEN`.
- **`OFS_NOMI_PML1/2` não são nomes de jogador**, apesar do prefixo `NOMI_`.
  Carregam `squad_ml[].nomi[6]` e `[7]`: são o 7º e o 8º slot de nome de um
  clube de ML. Viraram `OFS_ML_TEAM_NAME_7/8`.

Também ficou explícito o que já se sabia: o decodificador do original se
chamava `codifica_carat()` e o codificador `decodifica()`. São `Decode()` e
`Encode()`.

#### Convenção de sufixo dos offsets

Renomear expôs que o legado usava dígito para duas coisas diferentes.
Separadas:

| Sufixo | Significado |
|---|---|
| `_A` / `_B` / `_C` | continuação: a leitura cruzaria fronteira de setor e o original salta os 304 bytes de header + EDC/ECC à mão |
| `_COPY_n` | uma de várias cópias idênticas que o disco realmente guarda (o caso da tabela de formato de bandeira, gravada 5 vezes) |
| `_1` .. `_n` | registros distintos, não continuações |

`OFS_BAR1`, por exemplo, era continuação apesar do dígito: virou
`OFS_TEAM_BARS_A`.

#### Verificação

Nenhuma mudança de comportamento, e não por inspeção:

- 61 checks unitários passam;
- o golden test passa contra a European Deluxe **e** contra a japonesa — a
  saída continua byte-idêntica à do `ed.exe` salvo a faixa de 16 bytes
  conhecida;
- ASan + UBSan limpos;
- compilação sem um único warning.

### Fase 4 — `.rc` → Qt `.ui` ✅ concluída

[tools/rc2ui.py](../tools/rc2ui.py) converte os 6 diálogos de `ed.rc` em
`src/app/ui/*.ui`. Layout absoluto: os 434 controles foram posicionados à mão
em 2002, o original não tem comportamento de redimensionamento a preservar, e
manter as coordenadas é o que torna o resultado revisável contra uma captura
do `ed.exe`.

Saída:

| Arquivo | Conteúdo |
|---|---|
| `src/app/ui/*.ui` | os 6 formulários, consumidos pelo `uic` |
| `src/app/ui/controls.json` | o que o `.ui` não expressa |

O manifesto existe porque estilos Win32 carregam informação sem propriedade Qt
equivalente: `ES_NUMBER` e `ES_UPPERCASE` são validadores, não flags de widget.
A Fase 5 lê o JSON em vez de voltar ao `.rc`. Ele também guarda, por controle,
o símbolo de recurso, o keyword `.rc` de origem, o estilo cru e a geometria em
DLU e em px.

#### Contagem

O plano falava em 393 controles; são **434**. A métrica antiga vinha de uma
contagem crua que perdia continuações e um `PUSHBUTTON` indentado com tab. O
conversor confere a sua saída contra o `.rc` por keyword:

| | EDITTEXT | PUSHBUTTON | LTEXT | COMBOBOX | RTEXT | GROUPBOX | CTEXT | CONTROL | LISTBOX | DEFPUSH | total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ed.rc` | 193 | 106 | 41 | 39 | 23 | 10 | 10 | 8 | 2 | 2 | **434** |
| `.ui` | 193 | 106 | 41 | 39 | 23 | 10 | 10 | 8 | 2 | 2 | **434** |

#### Três armadilhas do formato `.rc`

1. **`COMBOBOX` guarda a altura do *dropdown*, não do controle.** Win32 desenha
   o combo fechado com uma linha de texto e só usa o resto com a lista aberta.
   Levado ao pé da letra, o `CMB_NSQUADRE` de 64 DLU vira uma caixa de 104 px
   que engole o grupo `DEFAULT TACTICS` atrás dele — foi exatamente o que a
   primeira renderização mostrou. Os 39 combos são desenhados com 12 DLU, que é
   o que o `ed.exe` mede sob Wine, e a altura original fica no manifesto como
   `dropdown_dlu`.
2. **Continuação de linha não dá para detectar por indentação.** 192 dos 434
   controles quebram em várias linhas, um deles partindo `NOT WS_VISIBLE` no
   meio, e um `PUSHBUTTON` é indentado com tab em vez de quatro espaços. O
   conversor reconhece início de statement pela palavra-chave; linha
   continuada sempre retoma dentro de uma expressão de estilo, começando com
   `WS_`/`BS_`/`ES_`/`CBS_`/`LBS_`/`NOT`.
3. **Há controles comentados com `//` dentro dos diálogos.** Precisam sair
   antes de juntar continuações, senão um `PUSHBUTTON` morto cola nas
   coordenadas do vivo acima dele.

Mais duas, do lado do Qt: a legenda de um `QGroupBox` é `title`, não `text` (o
`uic` emite `setText()` alegremente e quem reclama é o compilador), e `--` é
proibido dentro de comentário XML — o `uic` rejeita o arquivo inteiro.

#### Validação

O ponto da fase é fidelidade visual, então a verificação é olhar.
[tools/uipreview](../tools/uipreview) compila um executável por formulário que
renderiza o diálogo com `QWidget::grab()` e grava um PNG:

```sh
cmake -B build-uipreview -S tools/uipreview
cmake --build build-uipreview -j
DISPLAY=:98 ./build-uipreview/preview_MainDialog /tmp/main.png
```

`grab()` pinta fora da tela, então o diálogo principal de 1077 px sai inteiro
mesmo com o Xvfb em 960 — coisa que a captura do `ed.exe` não consegue. O
`tools/uipreview` usa Qt6 se existir e cai para Qt5, que é o que há na máquina
até a Fase 5.

Resultados:

- os 6 formulários renderizam **exatamente** no tamanho derivado das DLU
  (1077×547, 390×404, 493×323, 358×315, 481×297, 195×146);
- o `uic` aceita os 6;
- comparação lado a lado do diálogo principal contra a captura do `ed.exe`
  sob Wine: mesmos grupos, mesmas linhas, mesmas colunas.

A confirmação mais objetiva veio de graça: o centro do `CMB_WRITE` calculado
pelo conversor é (314, 521), e o `tools/golden_run.sh` da Fase 3 clica em
(315, 521) no `ed.exe` real há semanas. A conversão DLU→px acerta o pixel.

#### O que não foi feito, de propósito

- **Nomes de controle continuam sendo os símbolos do `.rc`** (`TXT_NSQUAD1`,
  `CMD_CARAT1`, `CMB_KIK_PUNC`). Vários são abreviações italianas, então isso
  contraria o critério da Fase 3.5 — mas ali a renomeação era gratuita porque
  o golden test provava que nada mudava, e aqui não há prova equivalente. O
  `.ui` precisa ficar diffável contra `ed.rc` e `resource.h` enquanto os 376
  handlers são portados. Renomear controles ficou para depois, com o
  `controls.json` como ponto de mapeamento — foi o que a Fase 5.5 fez, já com
  o `golden_gui` para provar que nada mudou.
- **Sem layouts Qt.** Geometria absoluta, como no original.
- **A fonte não é a original.** Os `.ui` declaram `MS Sans Serif` 8pt
  fielmente, mas ela não está instalada e o Qt substitui, o que corta o texto
  de alguns rótulos apertados — `Position` vira `Positior`. O `ed.exe` sob
  Wine corta exatamente os mesmos, pelo mesmo motivo. A política de fonte
  continua sem decidir; nem a Fase 5 nem a 5.5 mexeram nisso.

#### Guarda

`ctest -R ui_forms` roda `rc2ui.py --check`: regenera em memória e compara com
o que está commitado. Editar um `.ui` à mão, ou mexer no `ed.rc` sem
regenerar, falha aqui em vez de silenciosamente na hora de compilar o app. O
`--check` também revalida o XML, sem precisar de Qt.

O `tools/uipreview` desta fase compila com Qt5 ou Qt6. Foi escrito quando só
havia Qt5 na máquina; o Qt6 chegou na Fase 5 e o `find_package` prefere ele.


### Fase 5 — Portar handlers ✅ concluída

O Qt6 6.4.2 foi instalado no começo desta fase
(`qt6-base-dev qt6-base-dev-tools qt6-tools-dev` do `universe` do noble); o
`CMakeLists.txt` da raiz passou a achar o Qt e a compilar o `src/app`.

#### O que existe agora

`src/app/` tem o executável `newWe2002`: 12 fontes, ~3.100 linhas contra as
~9.800 do MFC (`edDlg.cpp` + os cinco diálogos + `giocatore.cpp` +
`myiotxt.cpp`).

| Arquivo | Origem no legado |
|---|---|
| `main.cpp` | `ed.cpp` |
| `MainWindow.{hpp,cpp}` | `CEdDlg` — construção, ligação dos widgets, `OnInitDialog` |
| `TeamView.cpp` | `OnSelezioneSquadraV` e as famílias de killfocus de nome/barra/cobrador/número |
| `TacticsView.cpp` | tudo de tática, incluindo `muovitattica` e `applica_tatt` |
| `Commands.cpp` | write, reload, custos, ordenar banco, números default, copiar nomes, `OnEditAll*` |
| `SofifaView.cpp` | os quatro botões de SoFIFA |
| `PlayerSelectDialog.{hpp,cpp}` | `selezDlg` |
| `PlayerSkillsDialog.{hpp,cpp}` | `carattDlg` |
| `FlagKitDialog.{hpp,cpp}` | `graf` |
| `DefaultTacticsDialog.{hpp,cpp}` | `tattDlg` |
| `EditOptionsDialog.{hpp,cpp}` | `editOptForm` |
| `PlayerFields.hpp` | a cópia campo-a-campo que o legado abria à mão 4 vezes |

O core ganhou `Sofifa.{hpp,cpp}` — o motor de conversão FIFA→WE, o scraper e
`FetchUrl`, vindos de `giocatore.cpp` e `myiotxt.cpp`. É o único lugar do
`src/core/` que usa libcurl, e continua sem Qt.

#### A redução

As 376 `afx_msg` viraram um punhado de métodos indexados. Onde o original
tinha `OnCarat1()`..`OnCarat23()`, cada um chamando `caratteristiche(k)` com
um literal diferente, agora há `OnPlayerSkills(int)` ligado num laço:

```cpp
for (int i = 0; i < 23; ++i) {
    connect(cmd_skills_[i], &QPushButton::clicked, this,
            [this, i] { OnPlayerSkills(i); });
}
```

Os arrays de widget (`txt_player_[23]`, `cmb_role_[10]`, ...) são resolvidos
uma vez por `findChild<T*>()` a partir do nome de objeto do `.ui`. O comentário
que abria `OnSelezioneSquadraV` — *"accidenti a non poter usare i vettori!!!!"*
— era exatamente sobre isso.

#### Onde o Qt não bate com o MFC

Três diferenças de sinal precisaram de decisão explícita:

- **`SetWindowText` não dispara `EN_KILLFOCUS`; `setText` também não dispara
  `editingFinished`.** Coincidem, então os handlers de commit usam
  `editingFinished` direto, sem flag de "estou carregando".
- **`EN_CHANGE` dispara em `SetWindowText`.** É o que redesenha o campinho ao
  trocar de time, então esses ficaram em `textChanged` (e não em `textEdited`),
  de propósito.
- **`QComboBox` não tem `killFocus`.** Os combos de papel e de cobrador
  gravavam em `CBN_KILLFOCUS`, então navegar a lista não escreve no banco **na
  hora**; um `eventFilter` de `FocusOut` no `MainWindow` reproduz o momento.
  `SetCurSel` não dispara `CBN_SELCHANGE`, mas `setCurrentIndex` dispara
  `currentIndexChanged` — por isso as cargas de time usam `QSignalBlocker`.
  **Reproduzir o momento não bastou:** `Escape` mantém o item navegado no MFC e
  o desfazia no `QComboBox`, então o killfocus recebia valores diferentes nos
  dois lados. O port intercepta o `Escape` no popup dos **dezesseis** combos do
  `MainWindow` que gravam assim — os seis de cobrador (CORR-WTE-125) e os dez
  de papel (CORR-WTE-127), que usam o mesmo `FocusOut`. **Há um segundo filtro,
  no `DefaultTacticsDialog`**, para os outros dez combos de papel, os dos
  presets: eles gravam por outro caminho — `currentIndexChanged` guardado por
  `hasFocus()` —, e por isso o filtro de lá repõe o foco antes de repor o
  índice (CORR-WTE-134).

#### Verificação

`tools/golden_gui.sh` é a contraparte de `golden_run.sh` da Fase 3: dirige a
janela Qt pelo mesmo ciclo abrir → *Write into CD image*, com `xdotool` no
`:98`. O `golden_check.sh` aceita `WE2002_GOLDEN_MODE=gui` para pôr a janela no
lugar do `we2002_golden_tool`, e o `ctest` ganhou o alvo `golden_gui`.

Isso é o que a Fase 3 não cobria: ela provou que o **core** grava o que o
`ed.exe` grava; o `golden_gui` prova que a camada de widgets no meio não muda a
resposta — que nenhum sinal dispara durante a carga e regrava um campo velho.

Resultado na imagem European Deluxe:

| Caso | Divergência |
|---|---|
| `ed.exe` vs janela Qt, gravação limpa | só `405724..405739` |
| `ed.exe` vs janela Qt, ambos com o mesmo nome de time editado na tela | só `405724..405739` |

O nome editado cai em `OFS_TEAM_NAME_1_A+200`, 7 bytes, idêntico nos dois.

Armadilha de quem for repetir o teste: **`Ctrl+A` não seleciona tudo num
`CEdit` do Win32.** Mandar `ctrl+a` para o `ed.exe` sob Wine e para o Qt produz
textos diferentes (`INTERZO` contra `ZORINFC`) e o diff acusa uma divergência
que não existe. Limpar com `End`, `shift+Home`, `BackSpace` funciona nos dois.

Para o teste ser dirigível, o `newWe2002` aceita o caminho da imagem como
argumento e pula o `QFileDialog`. O original não tinha argumento nenhum.

#### Divergências deliberadas

Além do slot 64 herdado da Fase 3, quatro da própria Fase 5 e **duas decididas
depois**, em 2026-08-31, pela paridade de tela
([PAR-TASK-09](/docs/tasks/PAR-TASK-09.md)) — as duas de ciclo de vida, nenhuma
delas grava byte:

- **`editFromFIFA` terminava com `costo = CalcolaCostoGiocatore(i)`**, onde `i`
  era o contador que sobrou da varredura de posições — sempre 8. Todo jogador
  importado saía com o preço do jogador 8. O port usa o índice do próprio
  jogador. Não afeta os golden tests (não há SoFIFA neles) e o botão
  *upd. player cost* recalcula tudo de qualquer jeito.
- **`OnOrdinaPanchina` gravava `auxlk[1]` e `auxlk[2]` num `char[2]`** — um
  byte além do fim. O port usa `std::swap`, mesmo efeito sem sair do array.
- ~~**As URLs do SoFIFA agora são gravadas** no `<imagem>_url.txt` junto com a
  imagem. O original só lia esse arquivo, nunca escrevia.~~ **Errado, corrigido
  em 2026-08-05:** `OnWriteCD` grava o sidecar desde 2015
  (`legacy/mfc/edDlg.cpp:6207-6214`), e o `Database::Save()` gerado herda isso
  verbatim. O `MainWindow::SaveUrls()` que a Fase 5 acrescentou só reescreve o
  mesmo arquivo com o mesmo conteúdo — redundante, não divergência. Está
  desligado junto com o resto do SoFIFA. A **leitura** (`LoadUrls()`) continua
  rodando mesmo assim: o `Save()` monta o sidecar a partir de `players[].url`,
  então pular a carga truncaria o arquivo do usuário para 1.911 linhas em
  branco.
- **`FlagKitDialog` usa um único teste para "tem bandeira própria"** (`id>0 &&
  id!=69 && id!=86 && (id<56 || id>63)`). O original tinha dois que discordavam
  na borda: o `OnInitDialog` desabilitava as caixas para 57..63 e o
  import/export recusava 56..63. 56 é a World All-Stars, que também não tem
  bandeira própria, então o teste mais largo é o certo.
- **Cancelar o diálogo de abertura encerra o port; o original fica de pé com o
  diálogo principal vazio.** `OnInitDialog` faz `return FALSE`
  (`legacy/mfc/edDlg.cpp:1331`), e em MFC esse retorno **não fecha diálogo** —
  só diz que o foco já foi tratado, e nenhum `EndDialog` é chamado. O `ed.exe`
  segue com o combo de times sem itens, os campos em branco e `Write into CD
  image` clicável. O port encerra depois do mesmo aviso. Decidido em 2026-08-31
  ([CORR-WTE-140](/docs/tasks/CORR-WTE-140.md)): botão de gravar clicável sem
  imagem carregada é pior que nenhuma janela, e o que o original faz nesse
  clique nunca foi medido. Não muda byte — os dois avisam igual antes.
- **`Return` no diálogo principal encerra o `ed.exe` e não faz nada no port.**
  `IDD_ED_DIALOG` não tem `DEFPUSHBUTTON` nem controle `IDOK`, então o Enter cai
  em `CDialog::OnOK`; o `CEdDlg` sobrescreve esse handler
  (`legacy/mfc/edDlg.cpp:1529`) só para consultar `CanExit()`, que devolve
  `TRUE` sempre — o editor fecha sem gravar. No port nenhum dos 86 botões é
  default (`autoDefault=false`, emitido pelo `rc2ui.py`), e a tecla não encontra
  destino. Decidido em 2026-08-31
  ([CORR-WTE-141](/docs/tasks/CORR-WTE-141.md)): reproduzir faria uma tecla
  acidental descartar o trabalho não gravado, que é justamente o defeito do
  original. O `Escape` **concorda** e fecha nos dois. Vale só para o
  `MainWindow` — no `DefaultTacticsDialog` o `Return` confirma, e deve, porque
  lá o `.rc` declara um `DEFPUSHBUTTON` (invisível, mas declarado).

#### O que não foi portado, e por quê

`OnEsporta`/`OnImporta` (time em `.2002`) e `OnImportaTot`/`OnEsportaTot`
(`.tt2002`) ficaram de fora. Dois motivos, ambos suficientes:

1. **Os botões não existem.** `ed.rc:347,348,368,369` tem os quatro
   `PUSHBUTTON` comentados com `//`. O `ON_BN_CLICKED` continua no message map,
   mas não há controle para clicar: são código morto no binário que os usuários
   receberam.
2. **O formato não é reproduzível.** Os quatro gravam `sizeof(squadra)` /
   `sizeof(giocatore)` cru no arquivo — imagem de memória do MSVC 32-bit,
   incluindo padding. Reimplementar exigiria inventar uma serialização, e o
   resultado não leria os arquivos antigos nem seria lido por eles.

O `.t2002` de tática (`tattDlg`) e o `.b2002`/`.m2002` de bandeira e uniforme
(`graf`) **foram** portados, porque ali os botões existem. O `.t2002` também é
uma imagem de memória, mas de uma classe com destrutor virtual: 4 bytes de
vptr, depois `nome[7]`, `ruoli[11]`, `x[10]`, `y[10]`, 2 de padding, 44 no
total. O port escreve os 4 bytes de vptr como zero e os ignora na leitura — o
vptr era um endereço de processo, não significava nada no arquivo nem então.

Os 4 bytes são os do fonte original, que é de 32 bits, e o arquivo tem 52 bytes
— o número que `tattDlg.cpp:701` valida ao importar. O `Debug/ed.exe` é x86-64,
exporta 56 e recusa o próprio arquivo; ele **aceita** o de 52 do port. Medido
na [CORR-WTE-132](/docs/tasks/CORR-WTE-132.md).

**Aceitar não é ler direito**, e a diferença só apareceu quando os dois lados
importaram o mesmo arquivo com controle positivo: o `ed.exe` passa na
conferência de tamanho e então decodifica com o vptr de 8 bytes do próprio
binário, **4 bytes adiante do lugar certo** — grava `MP` mais bytes de papel
onde o port grava `PARIMP`. [CORR-WTE-135](/docs/tasks/CORR-WTE-135.md).

Ainda não portado, e conhecido: o `ed.exe` mostra o ícone quando minimizado
(`OnPaint`) e tem um item "About" no menu de sistema. Nenhum dos dois existe em
Qt sem trabalho específico e nenhum edita a imagem.

### Fase 5.5 — Nomenclatura da UI em inglês ✅ concluída

Continuação da Fase 3.5, que já tinha limpado o `src/core/`. A Fase 4 manteve
de propósito os símbolos italianos do `.rc` nos `.ui`, para os formulários
ficarem diffáveis contra `ed.rc`/`resource.h` enquanto os handlers eram
portados; a Fase 5 fechou isso, e a justificativa acabou junto.

#### O mapa

`tools/glossary.py` ganhou `UI_CONTROLS`, 285 entradas. Fica **fora** de
`IDENTIFIERS` de propósito: `IDENTIFIERS` é varrido sobre o código *legado*
pelo `port_database.py` e pelo `extract_legacy_data.py`, e nome de controle não
tem o que fazer ali.

Quem aplica é o `tools/rc2ui.py`, na hora de nomear o widget — os `.ui` e o
`controls.json` são **regerados**, não editados. O `ctest -R ui_forms` continua
falhando se alguém editar um `.ui` à mão.

Exemplos do que mudou:

| ed.rc | agora | por quê |
|---|---|---|
| `TXT_GIOC1..23` | `TXT_PLAYER1..23` | giocatore |
| `CMD_CARAT1..23` | `CMD_SKILLS1..23` | caratteristiche |
| `CMD_SOST1..23` | `CMD_SWAP1..23` | sostituzione |
| `TXT_TATX2..11` / `TXT_TATY2..11` | `TXT_SLOT_X2..11` / `TXT_SLOT_Y2..11` | tattica |
| `CMD_VT1..10` | `CMD_SLOT1..10` | visual tattica |
| `CAMPO_` / `TCAMPO_` | `PITCH` | campo |
| `TXT_NSQUAD1..6` | `TXT_TEAM_NAME1..6` | nome squadra |
| `CMB_KIK_PUNL` / `_PUNC` | `CMB_KICK_LONG_FK` / `_SHORT_FK` | punizione lunga/corta |
| `CMB_KIK_ANGSX` / `_ANGDX` | `CMB_KICK_LEFT_CORNER` / `_RIGHT_CORNER` | angolo sinistro/destro |
| `CMB_KIK_RIG` | `CMB_KICK_PENALTY` | rigori |
| `TXT_BAND_COL1..15` | `TXT_FLAG_COL1..15` | bandiera |
| `TXT_1MAG_COL1..14` | `TXT_KIT1_COL1..14` | maglia |
| `CMB_GCORPO` | `CMB_BUILD` | corporatura |
| `CMB_GFRUOLO` | `CMB_OUT_OF_POSITION` | fuori ruolo |
| `TXT_GPZT` / `TXT_GPRET` | `TXT_SHOT_POWER` / `TXT_SHOT_ACCURACY` | potenza/precisione tiro |

O `T` de `TCMB_TAT` e `TCMD_VT` existia só para não colidir com o diálogo
principal num namespace de recursos único. Cada formulário é uma classe agora,
então caiu.

Uma correção de nome saiu daqui: `LAB_KIK_CAP2` não é um segundo rótulo de
capitão — é a legenda **PENALTY**. Virou `LAB_KICK_PENALTY`.

#### O que ficou como estava

Só nomes italianos entraram no mapa. Ficaram intactos:

- `CMB_WRITE`, `CMB_RELOAD`, `CMB_IMPFIFAWEB`, `CMB_EDITALL*`,
  `CMB_SHOWEDITOPT` — prefixo `CMB_` em `PUSHBUTTON` é esquisitice do `.rc`,
  mas é inglês.
- `IDOK`, `IDC_BUTTON1`, `LAB_BAR_1..5`, `CMD_TACT1..16`, `TXT_URL#`,
  `TXT_NUM#`, `TXT_BAR_*`, `CHK_ML`, `CHK_LK_DEF`, `LBL_LK`, `CMD_IMP`,
  `CMD_EXP`, `CMD_READ_URL`, `CHK_EDIT*`.

Renomear esses seria barulho sem leitor para ajudar, e afastaria os `.ui` do
`ed.rc` sem ganho.

O `legacy/mfc/` continua em italiano, como sempre esteve — é referência
histórica.

#### Rastreabilidade

Cada entrada do `controls.json` guarda o símbolo original em `id`. O manifesto
passou a ser chaveado pela classe Qt (`MainDialog`, `PlayerSkillsDialog`, ...)
em vez do símbolo do `.rc` — três dos seis eram italianos — e o símbolo do
diálogo virou o campo `id` do mesmo jeito.

No C++, cada handler renomeado aponta para o nome legado
(`///< was caratteristiche()`), e o `BindWidgets()` lista as famílias que
mudaram.

#### Guardas

Duas novas, ambas no `ctest`:

- **`glossary`** roda `tools/apply_glossary.py --check`, que agora varre
  `src/core/`, `src/app/` **e** os arquivos gerados em `src/app/ui/`. No código
  da aplicação ele checa contra `IDENTIFIERS` e `UI_CONTROLS`; no core, só
  contra `IDENTIFIERS`. Nos `.ui` e no `controls.json` um nome velho significa
  que o `rc2ui.py` não foi reexecutado, e a mensagem diz isso. A linha do
  campo `id` é pulada — é ali que o símbolo original mora de propósito.
- **`Bind<T>()`** (`src/app/Bind.hpp`) substituiu o `findChild` cru. Nome que
  não casa com o formulário aborta na hora dizendo qual, em vez de virar um
  ponteiro nulo que estoura três frames adiante. É a rede para o caso do `.ui`
  na árvore de build estar velho, que o teste estático não cobre.

#### Verificação

Renomeação não pode mudar byte de saída, e não mudou:

- O diff dos `.ui` toca **só** linhas `<widget class=... name=...>`; o do
  `controls.json`, só `object`/`id` e as chaves de diálogo. Geometria, estilo e
  ordem intactos.
- Os cinco testes verdes, incluindo `golden` e `golden_gui` na European Deluxe.
- Os cinco sub-diálogos abertos e exercitados no `:98` — a busca por nome é em
  runtime, então compilar não prova nada aqui.

### Fase 6 — Acabamento Linux ✅ concluída

As três trocas que esta fase previa — `CFileDialog` → `QFileDialog`,
`AfxMessageBox` → `QMessageBox`, `GetModuleFileName` →
`QCoreApplication::applicationDirPath()` — saíram na Fase 5: sem elas não havia
como abrir uma imagem nem avisar de nada, então não dava para adiar.

#### Decisões tomadas nesta fase

**Formato de pacote: nenhum, por ora.** Só as regras de `install()`. AppImage e
Flatpak ficam para quando houver alguém para distribuir. Se/quando vier, o
AppImage é o candidato: o editor abre um `.bin` de ~474 MB em qualquer lugar do
disco e grava um `_url.txt` ao lado, e o sandbox do Flatpak exigiria
`--filesystem=host`, que é abrir mão do sandbox.

**Fonte: fica como está.** MS Sans Serif não está instalada, o Qt substitui, e
alguns rótulos apertados cortam ("Position" vira "Positior"). O `ed.exe` sob
Wine corta exatamente os mesmos, pelo mesmo motivo. Fidelidade é o critério
desde a Fase 4; custo zero, e agora documentado em vez de pendente.

#### Instalar

```sh
cmake --preset release
cmake --build --preset release
cmake --install build-release --prefix ~/.local
```

| Vai para | O quê |
|---|---|
| `bin/newWe2002` | o executável |
| `share/newWe2002/` | `defaultlook.txt`, `SOFIFA attributes.txt`, `WE attributes conversion rules.txt` |
| `share/applications/` | `io.github.aguilasa.newWe2002.desktop` |
| `share/metainfo/` | AppStream |
| `share/icons/hicolor/{16x16,...,256x256}/apps/newWe2002.png` | o ícone, sete tamanhos |
| `share/doc/newWe2002/` | `NOTICE.md` e `README.md` |

`naz.txt` **não** é instalado: apesar de estar em `data/`, não é dado — é um
array em C que o autor colou na árvore, e nada o lê. Fica no repositório como
história.

**O nome do produto é `newWe2002`; `we2002` é o nome do formato.** A árvore
instalada, o `project()` do CMake, o alvo do executável, o ícone e o appid
`io.github.aguilasa.newWe2002` usam `newWe2002`. Ficaram deliberadamente como
`we2002`: o namespace C++, os headers em `src/core/include/we2002/`, os alvos
`we2002_core` / `we2002::core` / `we2002_tests` / `we2002_golden_tool` e todas as
variáveis `WE2002_*` de CMake e de ambiente (`WE2002_DATA_DIR`,
`WE2002_GOLDEN_IMAGE`, `WE2002_APPDATADIR`, ...) — esses nomeiam o jogo e o
layout da imagem, não este editor, e renomear o namespace arrastaria os
geradores, o glossário e todo arquivo gerado sem ganho nenhum.

Consequência para quem tem árvore de build antiga: `WE2002_APPDATADIR` é
variável de **cache**, então um `build/` configurado antes da renomeação
continua instalando em `share/we2002/`. Reconfigurar do zero, ou passar
`-DWE2002_APPDATADIR=share/newWe2002`.

O ícone era, nesta fase, os dois tamanhos de dentro do `legacy/mfc/res/ed.ico`
(32×32 e 16×16, 16 cores, as palavras "W.E. 2002" em marrom), convertidos sem
reescalar — inventar um 256×256 seria desenhar arte nova, e isso não é trabalho
de port.

**Substituído depois, a pedido:** [tools/make_icon.py](../tools/make_icon.py)
desenha uma camisa listrada em sete tamanhos. Arte nova, não derivada do
`ed.ico`; o marrom das listras é o marrom do original e é a única coisa
herdada. Cada tamanho é desenhado naquele tamanho, não escalado de um master:
em 16 e 24 as listras ficariam com um terço de pixel de largura e virariam
borrão, então lá a camisa é lisa. O `ed.ico` continua em `legacy/` como
história. Os candidatos descartados — campo visto de cima, disco, bola — viravam
todos o mesmo círculo de centro escuro em 16 px; camisa tem silhueta, e é o que
o programa edita.

#### Onde o app acha os dados

Isso é o que um pacote quebra e uma árvore de build esconde. A ordem está em
[src/app/DataFiles.cpp](../src/app/DataFiles.cpp):

1. `$WE2002_DATA_DIR` — escape hatch explícito.
2. Ao lado do executável — a única busca que o original fazia, e como fica uma
   cópia portátil descompactada.
3. O prefixo instalado, **relativo ao executável** (`../share/newWe2002`), não por
   caminho absoluto compilado. Mover a árvore instalada não quebra, e é também
   o que um AppImage precisaria de graça.
4. O `data/` do fonte, para rodar direto da árvore de build.

Verificado do jeito difícil: mascarando o `data/` do fonte com um bind mount num
user+mount namespace (a mesma técnica do `tools/run-sanitized.sh`) e rodando o
binário instalado. Sem o aviso de SoFIFA, então achou pelo caminho relativo.

Detalhe que atrapalha a conferência: `strings` **não** encontra
`../share/newWe2002` no binário. Com `-O2` o GCC monta a string em dois
`movabs` imediatos na pilha, e ela nunca existe contígua em `.rodata`. Conferir
pelas flags de compilação (`grep WE2002_DATA_DIR_FROM_BIN
build/src/app/CMakeFiles/newWe2002.dir/flags.make`), não pelo binário.

#### Três defeitos achados e corrigidos aqui

Nenhum dos três muda byte de saída — os golden tests provam.

- **`Return` na janela principal clicava um botão arbitrário.** Dentro de um
  `QDialog` o Qt torna todo `QPushButton` auto-default, então `Return` acionava
  o primeiro da ordem de tabulação. O diálogo principal tem 86 botões e nenhum
  `DEFPUSHBUTTON`, e um dos candidatos aplica formação predefinida sobre o time
  selecionado. O `rc2ui.py` passou a emitir `autoDefault=false` em
  `PUSHBUTTON`, deixando `DEFPUSHBUTTON` como o único jeito de ser default —
  que é o que o `.rc` quer dizer. Dos seis diálogos, só `DLG_GRAF` e
  `DLG_PTATTICHE` declaram um.

  No original o `Return` ia para o `IDOK` implícito do `CDialog` e **fechava** o
  editor (o `CanExit()` é um stub que retorna `TRUE`). No diálogo principal
  agora não faz nada, que é mais seguro que os dois comportamentos. `Escape`
  continua fechando, como nos dois.

  **Um dos dois `DEFPUSHBUTTON` obrigou a exceção.** O do `DLG_PTATTICHE` é
  `NOT WS_VISIBLE` (`ed.rc:627`), e o Qt **pula** um botão default invisível —
  medido: `setDefault(true)` nele não muda nada. Como os dois lados são modais,
  isso deixava o `DefaultTacticsDialog` sem saída e a gravação inalcançável. O
  diálogo passou a tratar `Return` no `keyPressEvent` e chamar `accept()`
  (CORR-WTE-131). Reproduz o comportamento, não o mecanismo — aqui o mecanismo
  do MFC não tem equivalente.

- **`ResolveMlLink` estourava os limites.** `START_LINK[lk[0]]` com `lk[0]`
  sendo um byte — até 255 — numa tabela de 120 entradas, e o resultado indexando
  `players[1911]` sem checagem. Numa imagem válida os valores estão sempre na
  faixa; em qualquer outro arquivo o editor **morria de segfault antes da janela
  aparecer**, sem nada no stderr. Foi assim que apareceu: apontando o app para
  um arquivo de bytes aleatórios.

  Agora há duas checagens, e fora da faixa resolve para o jogador 0 — todos os
  chamadores usam o resultado como índice na hora e nenhum tem caminho de erro.
  Mesma categoria do `auxlk[2]` da Fase 5: reproduzir a intenção, não o acesso
  fora dos limites. Fixado por `TestResolveMlLinkBounds`, que varre as 65.536
  combinações de dois bytes e exige que nenhuma escape da faixa.

- **O build Release morria em toda imagem.** `*** buffer overflow detected ***`
  logo depois do aviso de tamanho, antes de qualquer coisa aparecer. Achado ao
  conferir a árvore instalada, que é Release; o Debug não tem nada.

  Causa: `Load` lê 30 bytes de formação e faz `strcpy` para
  `Team::raw_formation`, declarado com **30** bytes. O terminador caía um byte
  além, em `slot_role[0]`. Com `-O2` a glibc liga o `_FORTIFY_SOURCE`, que
  confere `strcpy` contra o tamanho do destino (`__strcpy_chk(..., destlen=30)`)
  e aborta. É `Team` e `MlTeam`, 96 vezes por carga.

  O original declarava 30 e escrevia 31; o MSVC não conferia e o zero ia para
  `ruolo[0]`. `slot_role`/`slot_x`/`slot_y` são campos mortos no port — o
  `OnWriteCD` nunca os gravou e a tela lê os 30 bytes de `raw_formation`
  direto — então o byte extra nunca chegou ao disco em nenhum dos dois. Por isso
  passar o array para **31** não muda saída: `Save` grava 30 bytes fixos.
  Conferido dos dois lados — `roundtrip` em Debug e em Release dão arquivos
  byte-idênticos, e o `golden_gui` rodado com o binário Release fecha igual ao
  oráculo.

  Duas guardas: um `static_assert(sizeof(raw_formation) >= 31)` (quebra o build
  em qualquer configuração se alguém reduzir de volta) e
  `TestLoadUnterminatedFormation`, que monta uma imagem **esparsa** do tamanho
  cheio com `0xFF` nas regiões de formação — assim os 30 bytes não têm zero
  nenhum — e roda o `Load` inteiro. Sob `_FORTIFY_SOURCE` esse teste é o que
  pega qualquer outro dos 198 `strcpy` que estoure dentro do `Load`, sem precisar
  de imagem de verdade.

  Lição registrada em CLAUDE.md: **Release não é o mesmo teste que Debug.**

#### Infraestrutura

- **[CMakePresets.json](../CMakePresets.json)** — `debug`, `release`, `asan`,
  `ubsan`. A seção 5 previa isso desde o começo e nunca tinha sido escrito.
- **[.github/workflows/ci.yml](../.github/workflows/ci.yml)** — quatro jobs:
  `linux` (compila, testa, valida `.desktop`/AppStream, instala e confere o
  layout), `linux-release` (Release, para o `_FORTIFY_SOURCE` rodar),
  `linux-ubsan`, e `windows`. A seção 5 pede a matriz com `windows-latest`
  desde o primeiro workflow "mesmo que comece vermelho": vermelho ali era o
  sinal, não uma falha, e a Fase 7 tirou o `continue-on-error`.

  **Desde a Fase 7 o CI não roda sozinho.** Os gatilhos `push` e
  `pull_request` estão desligados por decisão, até o fim do projeto: enquanto a
  árvore está em movimento, o build local diz a mesma coisa antes e diz mais —
  contra o `ed.exe` nenhum runner roda. Sobrou o `workflow_dispatch`, então a
  matriz inteira roda à mão pelo Actions. Religar é descomentar as quatro
  linhas no cabeçalho do `ci.yml`.

  ASan **não** entra no CI: esta máquina não consegue rodar (a Citrix substitui
  o `dlsym`, ver CLAUDE.md), então ninguém reproduziria localmente uma falha que
  só o CI vê. UBSan roda em todo lugar.
- **[README.md](../README.md)** reescrito. Dizia "the Qt application does not
  exist yet" e mandava procurar os fontes MFC na raiz.

#### O que continua de fora

- O item "About" que o original punha no menu de sistema. Um `QDialog` não tem
  menu de sistema em Qt, e a caixa não editava nada.
- O `OnPaint` que desenhava o ícone com a janela minimizada. Não existe
  equivalente e não faz falta.
- Pacote de distribuição, por decisão acima.

**Fim do escopo Linux. Total Fases 1–6 (incluindo a 5.5): ~1,5 a 2 semanas.**

### Fase 7 — Windows ✅ concluída (2026-08-04)

> **O registro de execução — hashes, o que quebrou, o que ficou aberto — está
> na seção 11 do [PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md).** O resumo:
>
> **O `.exe` do MSVC grava os mesmos bytes que o binário do GCC**, nas duas
> imagens, no `Load` e no `Save`. Com o Linux já tendo provado
> `port(GCC) == ed.exe`, a paridade com o original de 2002 sai por
> transitividade — e foi confirmada de novo diretamente, contra o
> `Debug\ed.exe` rodando **nativo**, sem Wine: só a faixa `405724..405739`, a
> mesma de sempre. Isso encerra a dúvida sobre o corte da janela no `:98`: o
> corte nunca importou.
>
> A janela Qt, rodando do zip portátil e com a imagem num caminho acentuado,
> gravou byte a byte o mesmo que o core headless.
>
> Três defeitos que este plano não previa apareceram, e o primeiro é o que vale
> lembrar:
>
> - **`Database` tem 1,21 MB e é declarado como local em toda parte.** O Linux
>   reserva 8 MB de pilha e nunca reclamou; o MSVC reserva 1 MB, e *todo*
>   binário morria antes do `main` com `STATUS_STACK_OVERFLOW` e nenhuma saída.
>   Resolvido com `/STACK:8388608` — a mesma pilha contra a qual o código de
>   2002 foi escrito.
> - `curl/curl.h` puxa `windows.h`, que define `min`/`max` como macro e come os
>   `std::max`/`std::min` de `Sofifa.cpp`. `NOMINMAX` no CMake, não `#ifdef` no
>   fonte.
> - O Pillow escrevia um `.ico` de uma única entrada 16×16 sem avisar.
>
> Ficou aberto **um** item do checklist: editar um nome de time *pela janela
> Qt* e comparar com o oráculo. A Citrix desta máquina filtra input sintético e
> a UIA do Qt só publica os itens do combo com o popup aberto, de forma
> intermitente. É o que a §5.3 daquele plano manda não perseguir agora.
>
> **O ASan no MSVC continua sem ser explorado** — o preset `windows-asan`
> existe, mas o `if(WE2002_SANITIZE AND NOT MSVC)` do `CMakeLists.txt` ainda
> desliga tudo no MSVC. Continua sendo o item de maior retorno da lista.

> **O roteiro de execução está em [PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md)** —
> ambiente de desenvolvimento passo a passo, os defeitos já localizados que só
> aparecem no MSVC, as tarefas em ordem e o checklist de aceitação. Este arquivo
> fica com o *o quê*; o outro tem o *como*, para ser seguido sentado na máquina
> Windows.
>
> Duas coisas que aquele documento resolve e que o resumo abaixo ainda não
> sabia:
>
> - **Os golden tests não rodam no Windows** como estão. Os três scripts são
>   bash e dependem de Wine e `xdotool`. Em vez de portá-los, a paridade de
>   bytes se prova por transitividade: se `port(MSVC) == port(GCC)` e o Linux já
>   provou `port(GCC) == ed.exe`, está provado — e isso é comparação de
>   SHA-256 de dois `roundtrip`, sem GUI e sem Wine. O confronto direto com o
>   `Debug/ed.exe` **nativo** continua valendo a pena uma vez, e não precisa de
>   automação: é clicar.
> - **O ASan só roda no Windows.** Nesta máquina Linux a Citrix o inviabiliza
>   (ver CLAUDE.md); o MSVC tem `/fsanitize=address`, hoje desligado pelo
>   `NOT MSVC` da linha 36 do `CMakeLists.txt`. É a primeira chance real de
>   varrer os 198 `strcpy` herdados.

Não começar antes da Fase 6 fechada e dos golden tests verdes no Linux.

- Configurar dependências: Qt 6 e libcurl via vcpkg (ou instalador oficial do
  Qt).
- Build com MSVC. Esperado que já compile — o CMake é o mesmo e o `core` não
  tem código específico de plataforma. O que costuma quebrar aqui: warnings
  virando erro, `std::filesystem` em caminhos com acento, e a codepage dos
  fontes UTF-8 (resolvida pela flag `/utf-8`).
- **Rodar os golden tests no Windows.** É o único jeito de provar que o
  round-trip byte-a-byte sobrevive à troca de compilador — em especial o layout
  dos bitfields de `NUMERI` e a abertura em modo binário.
- Comparar o `.exe` novo contra o `Debug/ed.exe` original **na mesma máquina**,
  sem Wine no meio. É o teste de paridade mais forte que existe neste projeto.
- Empacotar: `windeployqt` para juntar as DLLs do Qt, depois Inno Setup ou um
  zip portátil.
- Habilitar `windows-latest` como obrigatório no CI.

**Total Fases 1–7: ~2 a 2,5 semanas.**

---

## 7. Riscos

- Bugs de memória latentes vão aparecer sob ASan — bom, mas custa tempo não
  estimado.
- Estado global em `edDlg.cpp` pode resistir à extração limpa; talvez precise
  de um passo intermediário de encapsulamento.
- Se um golden test falhar, suspeitar primeiro de fronteira de setor
  MODE2/2352 (ver seção 2).
- Cada rodada de golden test consome ~474 MB de disco por cópia da imagem.

Específicos do Windows (Fase 7):

- **Abrir arquivo sem `std::ios::binary` corrompe a imagem.** No Linux passa
  despercebido porque não há tradução de fim de linha; no Windows, todo `0x0A`
  vira `0x0D 0x0A`. Se um golden test só falhar no Windows, é a primeira
  suspeita.
- Layout de bitfields de `NUMERI` pode divergir entre GCC e MSVC. O
  `static_assert` da Fase 2 pega o tamanho, mas não a ordem dos bits — só o
  golden test rodando no Windows resolve isso.
- Adiar o Windows até a Fase 7 concentra o risco: se algo estrutural estiver
  errado, a descoberta vem tarde. Mitigação barata — deixar `windows-latest` na
  matriz de CI desde o começo, mesmo vermelho, só para ver *quando* quebra.
