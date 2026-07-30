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
> Progresso: Fase 0 validada, **Fase 1 concluída**. Fase 2 em diante ainda
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
| Controles no `.rc` | 393 |
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

| Offset | European Deluxe | Japan (Track 1) | PES2 Europe (Track 1) |
|---|---|---|---|
| `1012640` `NOMI_SQ1` | `AEK KIEV GALATASARAY` ✅ | `PATAGONIA MARMARA` ✅ | idem Japan ✅ |
| `387792` `NOMI_G` | `Toldo` ✅ | Shift-JIS ✅ | `Dyer` ✅ |
| `2002316` `NOMI_SQK` | Shift-JIS ✅ | Shift-JIS ✅ | tabela de ponteiros ❌ |
| `5651448` `NOMI_SQ6` | `AEK KIEV` ✅ | katakana ✅ | texto de erro francês ❌ |

**Veredito:**

- `/home/ingmar/ROMs/psx/Winning Eleven 2002 - European Deluxe 2002-03/` →
  **imagem golden.** Todos os offsets batem, nomes latinos, fácil de
  inspecionar visualmente.
- `/home/ingmar/ROMs/psx/World Soccer Winning Eleven 2002 (Japan)/` →
  compatível estruturalmente, conteúdo Shift-JIS. Segundo caso de teste;
  valida `kanjitoascii`/`asciitokanji` (`edDlg.cpp:732-773`).
- `/home/ingmar/ROMs/psx/Pro Evolution Soccer 2 (Europe) (EnFrDe)/` →
  **NÃO USAR.** Layout diverge depois de ~2 MB; o editor grava por cima de
  outros dados e corrompe a imagem.

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
│     └─ resources/app.qrc     # icone etc, embutidos no binario
│
├─ tests/                      # golden tests da Fase 3
│  ├─ CMakeLists.txt
│  └─ fixtures/                # dados pequenos; NUNCA imagens de CD
│
├─ tools/                      # scripts de apoio, nao entram no binario
│  ├─ rc2ui.py                 # conversor .rc -> .ui (Fase 4)
│  └─ golden_run.sh            # dirige o ed.exe sob Wine (Fase 3)
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

### Fase 2 — Core portável `libwe2002` (~1–2 dias)

**Passo 2.0 — reorganizar a árvore** conforme a seção 5, e só então escrever
código.

Biblioteca sem MFC:

- `CFile` → `std::fstream` (wrapper fino com `Seek`/`Read`/`Write` para
  minimizar o diff).
- `_itoa` → `std::to_string`.
- `CString` → `std::string`.
- `AfxMessageBox` → callback / `std::function` injetado.
- Deletar todo o OLE de `ed.cpp`.
- Mover de `edDlg.cpp`: os 69 `OFS_*`, `carica_dabin`, `OnWriteCD`,
  `kanjitoascii`/`asciitokanji`, `CalcolaCostoGiocatore`, import SoFIFA.
- Manter `giocatore.cpp`, `squadra.cpp`, `squadra_ml.cpp`, `tattica.cpp`,
  `myiotxt.cpp` quase intactos.
- `static_assert(sizeof(NUMERI) == 16)` + teste de layout de bits.
- CMake + g++, `-fsigned-char`, build de dev com ASan/UBSan.

### Fase 3 — Golden tests (~1 dia)

- Sequência fixa de edições no `ed.exe` sob Bottles → salvar.
- Mesma sequência headless via `libwe2002`.
- `cmp` byte-a-byte.
- Rodar contra European Deluxe **e** Japan.
- **Trabalhar sobre cópia** — os testes mutam a imagem (474 MB por cópia).

Sem essa fase o port é chute. É aqui que a suspeita de bitfield/endianness
morre ou se confirma.

### Fase 4 — `.rc` → Qt `.ui` (~2–3 dias)

Script Python converte os 6 blocos `DIALOG`/`DIALOGEX` de `ed.rc` em `.ui`.
Trata `LTEXT`/`CTEXT`/`EDITTEXT`/`PUSHBUTTON`/`COMBOBOX`/`LISTBOX`/
`GROUPBOX`/`CONTROL(BS_AUTOCHECKBOX)`. Conversão DLU→px (MS Sans Serif 8:
baseX=6, baseY=13; `x*baseX/4`, `y*baseY/8`). Layout absoluto preserva o
visual original.

Qt6 precisa ser instalado (só `qmake` do Qt5 presente no host).

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
