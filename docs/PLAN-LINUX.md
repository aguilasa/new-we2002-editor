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
> Progresso: Fases 0, 1, 2, 3, 3.5 e **4 concluídas**. Fase 5 em diante ainda
> **não autorizada** — não iniciar sem pedido explícito.

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

- `/home/ingmar/ROMs/psx/Winning Eleven 2002 - European Deluxe 2002-03/` →
  **imagem golden.** Todos os offsets batem, nomes latinos, fácil de
  inspecionar visualmente.
- `/home/ingmar/ROMs/psx/World Soccer Winning Eleven 2002/` →
  **melhor imagem japonesa.** Ver comparação abaixo.
- `/home/ingmar/ROMs/psx/World Soccer Winning Eleven 2002 (Japan)/` →
  compatível, mas redundante com a anterior e com ECC degradado.
- `/home/ingmar/ROMs/psx/Pro Evolution Soccer 2 (Europe) (EnFrDe)/` →
  **NÃO USAR.** Layout diverge depois de ~2 MB; o editor grava por cima de
  outros dados e corrompe a imagem.

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
| `we2002` | executável | `we2002_core`, `Qt6::Widgets` |
| `we2002_tests` | executável de teste | `we2002_core` |

Esqueleto do `CMakeLists.txt` da raiz:

```cmake
cmake_minimum_required(VERSION 3.21)
project(we2002 LANGUAGES CXX)

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
  workflow, mesmo que o Windows comece vermelho. Sem macOS.

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
| `tools/golden_run.sh` | metade oráculo — dirige o `ed.exe` com `xdotool` no `:99` |
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
DISPLAY=:99 ./build-uipreview/preview_MainDialog /tmp/main.png
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
  handlers são portados. **Renomear controles é trabalho da Fase 5**, e o
  `controls.json` já é o ponto de mapeamento.
- **Sem layouts Qt.** Geometria absoluta, como no original.
- **A fonte não é a original.** Os `.ui` declaram `MS Sans Serif` 8pt
  fielmente, mas ela não está instalada e o Qt substitui, o que corta o texto
  de alguns rótulos apertados — `Position` vira `Positior`. O `ed.exe` sob
  Wine corta exatamente os mesmos, pelo mesmo motivo. Decidir a política de
  fonte é da Fase 5.

#### Guarda

`ctest -R ui_forms` roda `rc2ui.py --check`: regenera em memória e compara com
o que está commitado. Editar um `.ui` à mão, ou mexer no `ed.rc` sem
regenerar, falha aqui em vez de silenciosamente lá na Fase 5. O `--check`
também revalida o XML, sem precisar de Qt.

Qt6 ainda **não** está instalado — é pré-requisito da Fase 5, não desta.


### Fase 5 — Portar handlers (~3–5 dias)

A maior parte das 8.456 linhas é repetição indexada: `OnCarat1..23`,
`OnSost1..23`, `OnChangeURL1..23`, `OnKillfocusNum1..23`,
`OnKillfocusTatx2..11`, `OnKillfocusTaty2..11`, `OnSelchangeTat2..11`.
Colapsar em loops com lambdas capturando o índice. Estimativa: ~60% de
redução do arquivo.

Arrays `CEdit txt_gioc1..23` viram `QLineEdit* txt_gioc[23]`.

### Fase 6 — Acabamento e empacotamento Linux (~1 dia)

`CFileDialog` → `QFileDialog`; `AfxMessageBox` → `QMessageBox`;
`GetModuleFileName` → `QCoreApplication::applicationDirPath()`.
Empacotar AppImage ou Flatpak.

**Fim do escopo Linux. Total Fases 1–6: ~1,5 a 2 semanas.**

### Fase 7 — Windows (~2–3 dias, só depois do Linux redondo)

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
