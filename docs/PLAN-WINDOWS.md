# Fase 7 — Windows

> Documento de **execução**, para ser seguido sentado na máquina Windows.
> O plano geral e todo o histórico das Fases 0–6 estão em
> [PLAN-LINUX.md](/docs/PLAN-LINUX.md); a arquitetura e as armadilhas do código em
> [../CLAUDE.md](../CLAUDE.md). Este arquivo não repete nada dos dois — ele
> assume que você leu a seção *Suporte a plataformas* do plano.
>
> Escrito em 2026-07-31, com o Linux fechado no commit `bf1aee2`.
>
> | | |
> |---|---|
> | Pré-condição | Fases 0–6 concluídas, `ctest` verde no Linux |
> | Estimativa | 2–3 dias, sendo ~meio dia só de instalação |
> | Critério de pronto | seção [9](#9-checklist-de-aceitação) |

---

## 1. O que esta fase tem de provar

Uma só coisa, e não é "compila no Windows":

> **O `.exe` compilado com MSVC grava os mesmos bytes que o binário compilado
> com GCC — e portanto os mesmos bytes que o `ed.exe` de 2002.**

Todo o resto (empacotar, ícone, CI) é acabamento. A troca de compilador é o
que pode mudar bytes, por três motivos concretos:

1. **Ordem de bits em bitfield.** `SquadNumbers` ([Types.hpp](../src/core/include/we2002/Types.hpp))
   empacota os números de camisa em campos de 5 bits. O `static_assert` da
   Fase 2 garante o **tamanho** (16 bytes); a ordem de alocação dos bits dentro
   da palavra é definida pela implementação e o MSVC não é obrigado a
   concordar com o GCC.
2. **Modo binário.** Se algum `open` perder o `std::ios::binary`, o runtime da
   Microsoft traduz `0x0A` ↔ `0x0D 0x0A` e **corrompe a imagem de CD**. Hoje o
   [CdImage.cpp](../src/core/CdImage.cpp) está correto nos dois `open`; a
   questão é continuar correto.
3. **Padding de struct.** Nenhuma struct é gravada em bloco (`Save` escreve
   campo a campo), então o risco é baixo — mas é o golden test que diz isso, não
   eu.

A seção [5](#5-como-provar-a-paridade-de-bytes) mostra como provar isso **sem
Wine e sem automatizar GUI**, que é a parte que o plano original subestimou.

---

## 2. Ambiente de desenvolvimento

### 2.1 Máquina

| | Mínimo |
|---|---|
| SO | Windows 10 22H2 ou 11, x64 |
| Disco livre | **~12 GB**: Qt ~3,5 GB, Visual Studio ~8 GB, vcpkg ~1 GB, repo 276 MB, mais uma imagem de CD de 474 MB por cópia de teste |
| RAM | 8 GB compila; 16 GB compila sem sofrer |

O golden test faz duas cópias de ~474 MB por rodada. Reserve ~2 GB de temporário.

### 2.2 Visual Studio 2022

Community serve. No instalador, marque a carga de trabalho **"Desenvolvimento
para desktop com C++"**, que já traz o que importa:

- MSVC v143 (x64/x86)
- Windows 11 SDK
- CMake integrado e Ninja
- Console do desenvolvedor (`x64 Native Tools Command Prompt`)

**Não** precisa de MFC. O `ed.exe` original não vai ser recompilado — ele já
está no repo, em `Debug/ed.exe`, e é o oráculo. Se algum dia precisar
recompilá-lo, aí sim vem o componente "Suporte a MFC", mas isso não é Fase 7.

Todos os comandos deste documento presumem que você está no **x64 Native Tools
Command Prompt for VS 2022**, não no `cmd` comum.

### 2.3 Git

```bat
winget install Git.Git
```

Uma configuração **importa** antes de clonar:

```bat
git config --global core.autocrlf false
```

Motivo: o `.gitattributes` herdado tem `* text=auto`, e com o `autocrlf=true`
padrão do Git for Windows a árvore de trabalho vira CRLF. Nada no repo está em
CRLF hoje (conferido: `ed.rc`, `defaultlook.txt`, os `.ui`, o `controls.json` e
os fontes gerados são todos LF). Os geradores em Python leem em modo texto, que
normaliza `\r\n` na leitura, então o `ctest -R ui_forms` até passaria — mas eles
**escrevem** com `\n` traduzido para `\r\n`, e aí todo arquivo gerado aparece
modificado sem nenhuma mudança real. Com `autocrlf=false` isso não acontece.

Efeito colateral do mesmo `text=auto`: se você algum dia rodar os `.sh` do
`tools/` por WSL ou Git Bash e eles vierem com CRLF, quebram com
`$'\r': command not found`. Ver a tarefa T1 na seção 6.

```bat
git clone git@github.com:aguilasa/new-we2002-editor.git
cd new-we2002-editor
```

Confirme que o oráculo veio:

```bat
dir Debug\ed.exe
```

### 2.4 Python e Pillow

Os geradores (`tools/*.py`) rodam no Windows sem mudança. O `make_icon.py`
precisa do Pillow.

```bat
winget install Python.Python.3.12
python -m pip install --upgrade pip
python -m pip install pillow
```

Cuidado com o nome do executável: no Linux o CMake acha `python3`, no Windows é
`python`. O `find_package(Python3 COMPONENTS Interpreter)` do
[tests/CMakeLists.txt](../tests/CMakeLists.txt) resolve os dois, mas os comandos
que você digitar à mão são `python tools/...`.

### 2.5 Qt 6

Use o **instalador oficial** (<https://www.qt.io/download-qt-installer>), não o
vcpkg: compilar o Qt do fonte leva horas e não traz nada.

Precisa de conta Qt (gratuita). No instalador, escolha *Custom installation* e
marque:

- **Qt 6.5.3** (LTS) → **MSVC 2019 64-bit**
- Qt 6.5.3 → *Qt Debug Information Files* — opcional, só se quiser depurar
  dentro do Qt

O `README.md` pede Qt 6.3+; o CI usa 6.5.3, então use 6.5.3 para bater com o
que já está verde. Instala em `C:\Qt\6.5.3\msvc2019_64`.

Não marque Qt Creator, Android, WebAssembly, nem os módulos extra. Este projeto
usa **só `Qt6::Widgets`**.

### 2.6 libcurl, por vcpkg

```bat
cd C:\
git clone https://github.com/microsoft/vcpkg
C:\vcpkg\bootstrap-vcpkg.bat
C:\vcpkg\vcpkg install curl:x64-windows
```

O `core` liga em `CURL::libcurl` ([src/core/CMakeLists.txt](../src/core/CMakeLists.txt)).

Lembrete que não é burocracia: o [NOTICE.md](../NOTICE.md) diz que o texto da
licença do curl **tem de acompanhar** qualquer redistribuição do binário. Se
você gerar um zip ou um instalador, o arquivo de licença do curl vai dentro.

### 2.7 Configurar e compilar

```bat
cmake -B build -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake ^
  -DCMAKE_PREFIX_PATH=C:/Qt/6.5.3/msvc2019_64
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

**Não use os presets do [CMakePresets.json](../CMakePresets.json) como estão.**
Eles setam `CMAKE_BUILD_TYPE`, que o gerador do Visual Studio — multi-config —
**ignora**. Você pediria Release e levaria Debug. Ou passe `--config` em todo
comando, como acima, ou gere com Ninja:

```bat
cmake -B build-ninja -G Ninja -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake ^
  -DCMAKE_PREFIX_PATH=C:/Qt/6.5.3/msvc2019_64
```

Presets próprios para Windows são a tarefa T2.

### 2.8 Uma imagem de CD

Copie **uma cópia** da imagem European Deluxe 2002-03 (474.784.128 bytes) para
a máquina. É a imagem de referência dos golden tests. Na árvore Linux ela fica
em `roms/golden-european-deluxe.bin`, na raiz do repositório — pasta fora do
versionamento, então ela **não** vem junto no `git clone`; copie à mão.

O editor grava **in-place**. Nunca aponte para a única cópia que você tem.

```bat
set WE2002_TEST_IMAGE=C:\we2002\copia.bin
ctest --test-dir build -C Release -R core --output-on-failure
```

---

## 3. O que já está pronto — não refazer

Levantado antes de escrever este documento, para você não gastar tempo:

| Item | Onde | Situação |
|---|---|---|
| `/utf-8` para o MSVC | [CMakeLists.txt](../CMakeLists.txt) linhas 19–23 | pronto. Os fontes são UTF-8 desde a Fase 1 |
| `char` signed | mesmo bloco | pronto, e **corretamente sem `/J`** — a flag inverteria e quebraria tudo |
| `-fsigned-char`, `-Wall -Wextra` | idem, e os dois `src/*/CMakeLists.txt` | já guardados por `if(NOT MSVC)` |
| Nada de `windows.h`, `MAX_PATH`, `_itoa` no port | `src/` | conferido: zero ocorrências |
| `std::ios::binary` nos dois `open` | [CdImage.cpp](../src/core/CdImage.cpp) linhas 9 e 20 | pronto |
| `std::filesystem::path` em vez de `char[]` | core inteiro | pronto desde a Fase 2 |
| Dados achados ao lado do executável | [DataFiles.cpp](../src/app/DataFiles.cpp) | pronto, e é justo o que um zip portátil precisa |
| Ícone da janela em 7 tamanhos | `src/app/resources/` + `AUTORCC` | pronto (`bf1aee2`) |
| `static_assert(sizeof(raw_formation) >= 31)` | [tests/test_main.cpp](../tests/test_main.cpp) | pronto — e é **a única** proteção contra o estouro da Fase 6 no Windows, porque o MSVC não tem `_FORTIFY_SOURCE` |

Esse último merece leitura. No Linux, o `-O2` liga o `_FORTIFY_SOURCE` da glibc,
que aborta em `strcpy` estourando o destino — foi assim que o defeito do
`raw_formation` apareceu. **O MSVC não faz essa checagem.** O mais próximo é
`/RTC1` (só Debug, e não cobre `strcpy` de biblioteca) e `/GS` (só o canário de
retorno). Ou seja: no Windows, aquele bug teria continuado silencioso para
sempre. O `static_assert` é o que protege, e é de compilação — vale nos dois.

---

## 4. O que vai quebrar

Em ordem de certeza. Os três primeiros são defeitos reais já localizados, não
suspeitas.

### 4.1 `std::string` em UTF-8 virando `path` — quebra caminho com acento

**Certo que acontece.** `QString::toStdString()` devolve **UTF-8**. Construir
`std::filesystem::path` a partir de um `std::string` no MSVC interpreta os bytes
na **codepage ANSI do sistema**, não em UTF-8. Resultado: qualquer caminho com
caractere fora do ASCII vira outro caminho, e o arquivo "não existe".

Três sítios:

| Arquivo | Linha | O que acontece |
|---|---|---|
| [MainWindow.cpp](../src/app/MainWindow.cpp) | 330 | `image_ = chosen.toStdString();` — a imagem escolhida no `QFileDialog`. `C:\ROMs\Seleção\x.bin` não abre |
| [DataFiles.cpp](../src/app/DataFiles.cpp) | 13 | `applicationDirPath().toStdString()` — instalado em `C:\Users\João\...`, não acha `.txt` nenhum |
| [DataFiles.cpp](../src/app/DataFiles.cpp) | 24 | idem para `$WE2002_DATA_DIR` |

Correção portátil, sem `#ifdef`: construir o `path` a partir de UTF-16.

```cpp
// QString e UTF-16; path aceita char16_t e converte para o encoding nativo.
std::filesystem::path FromQString(const QString& s) {
    return std::filesystem::path(s.toStdU16String());
}
```

No Linux isso continua correto (converte UTF-16 → UTF-8). Nada de
`toStdString()` para caminho, em lugar nenhum.

### 4.2 `path::string()` pode lançar no MSVC

[Database.cpp](../src/core/Database.cpp) linha 38, dentro de `UrlSidecarPath()`:

```cpp
std::string s = image.string();
```

No MSVC, `path::string()` converte de UTF-16 para a ANSI do sistema e **lança
`std::system_error`** no que não for representável. Com uma imagem em caminho
acentuado, abrir o editor joga exceção antes da janela.

É código **gerado**? Não — `UrlSidecarPath` é escrita à mão em `Database.cpp`,
mas `Database.cpp` **é gerado** por [tools/port_database.py](../tools/port_database.py).
Confira de onde vem essa função antes de editar; se estiver no template do
gerador, a correção vai lá, e depois `python tools/port_database.py`.

Correção: fazer a substituição de `.bin` → `_url.txt` sobre
`image.u8string()` ou, mais simples, sobre `image.native()` (que é `wstring` no
Windows e `string` no Linux) com um `if constexpr`. Preserve o comportamento
descrito no comentário: o original substitui **toda** ocorrência de `.bin`, não
só a extensão, e isso é de propósito.

### 4.3 Os testes `golden` e `golden_gui` não rodam no Windows

[tests/CMakeLists.txt](../tests/CMakeLists.txt) registra os dois com um `.sh`
como `COMMAND`. No Windows o ctest não sabe executar isso e os dois **falham** —
não são pulados, falham. É exatamente o que o job `windows` do CI vai mostrar
hoje.

Os scripts dependem de bash, Wine e `xdotool`; nada disso existe (nem faz
sentido) no Windows. Guarde com `if(UNIX)` e ponha no lugar o procedimento da
seção 5.

### 4.4 Avisos `C4996` em massa

O código herdado tem **198** `strcpy`/`strcat`. O MSVC marca todos como
deprecados (`C4996`) e a saída fica ilegível. Defina, só para o MSVC:

```cmake
target_compile_definitions(we2002_core PRIVATE _CRT_SECURE_NO_WARNINGS)
```

**Não** troque por `strcpy_s`. A regra do CLAUDE.md continua valendo: o
truncamento pode ser load-bearing no formato, e trocar sem golden test é como se
achou o bug do `raw_formation`. Silenciar o aviso é a resposta certa aqui.

### 4.5 Janela de console aparecendo

O `qt_add_executable` deve marcar `WIN32_EXECUTABLE`, mas confirme: se abrir um
`cmd` preto atrás da janela, force

```cmake
set_property(TARGET newWe2002 PROPERTY WIN32_EXECUTABLE TRUE)
```

Note que isso **cega o stderr**, e o aviso de tamanho de imagem e as mensagens
do `Load` vão por caixa de diálogo, não por console — o que é o comportamento do
original.

### 4.6 Ícone no Explorer

O ícone da Fase 6.5 é o **da janela** (via `.qrc`). O que o Explorer, a barra de
tarefas e o atalho mostram vem de um recurso `ICON` embutido no `.exe`, que não
existe. Tarefa T7.

---

## 5. Como provar a paridade de bytes

O plano dizia "rodar os golden tests no Windows". Como está, isso significaria
portar três scripts bash e automatizar a GUI com AutoIt ou pywinauto — dias de
trabalho para responder a uma pergunta que dá para responder em minutos.

### 5.1 O teste principal: transitividade (sem Wine, sem GUI)

O `golden` do Linux já provou **port(GCC) == ed.exe**. Se você provar
**port(MSVC) == port(GCC)**, a paridade com o `ed.exe` sai por transitividade.

E `port(MSVC) == port(GCC)` é uma comparação de arquivo, nada mais:

**No Linux**, a partir de uma cópia da imagem de referência:

```sh
cp /caminho/referencia.bin /tmp/linux.bin
./build/tests/we2002_golden_tool roundtrip /tmp/linux.bin
sha256sum /tmp/linux.bin
```

**No Windows**, a partir de uma cópia **da mesma** imagem:

```bat
copy C:\we2002\referencia.bin C:\we2002\win.bin
build\tests\Release\we2002_golden_tool.exe roundtrip C:\we2002\win.bin
certutil -hashfile C:\we2002\win.bin SHA256
```

Os dois hashes têm de ser iguais. Isso cobre, de uma vez:

- ordem dos bits de `SquadNumbers` — qualquer reordenação muda os bytes gravados
- modo binário — sem `ios::binary`, todo `0x0A` do arquivo sai diferente
- padding e ordem de campo em tudo que o `Save` escreve
- endianness (mesma, mas o teste não precisa saber)

Faça o mesmo com `digest` em vez de `roundtrip`: ele imprime checksums do
**estado carregado**, então um `digest` divergente aponta o `Load` e um
`roundtrip` divergente aponta o `Save`. Localiza o problema sem depurador.

Repita com a imagem japonesa (SLPM-87056) — é ela que exercita
`kanjitoascii`/`asciitokanji`, e `char` signed vs unsigned aparece justo ali.

### 5.2 O teste forte: `ed.exe` nativo, na mesma máquina

Vale a pena uma vez, porque tira o Wine da equação de vez — e é o teste de
paridade mais forte que este projeto tem. Não precisa de automação: você está
na máquina, então **clique**.

1. Duas cópias da mesma imagem, `oracle.bin` e `port.bin`.
2. Rode `Debug\ed.exe`, abra `oracle.bin`, dispense o aviso de tamanho, clique
   **Write into CD image**, feche.
3. `we2002_golden_tool.exe roundtrip port.bin`.
4. Compare com o script que já existe, que é Python puro e roda no Windows:

```bat
python tools\golden_compare.py C:\we2002\oracle.bin C:\we2002\port.bin
```

Ele recebe os dois arquivos posicionalmente (`left right`, mais `--json`
opcional) e lê os nomes de região do `Offsets.hpp` — Python puro, nada de
plataforma. O resultado esperado é **só** a faixa conhecida `405724..405739`, a
mesma divergência aceita e documentada na Fase 3 — o slot 64 de um array de 63.
Qualquer outra faixa é bug.

Isso também mata uma dúvida antiga: no Wine o diálogo principal fica cortado
(1077 px de largura contra os 960 do `:99`). No Windows, não. Se a saída for a
mesma faixa e só ela, o corte nunca importou.

### 5.3 Automatizar a GUI: não agora

Se algum dia a Fase 7 virar CI de verdade em `windows-latest`, aí precisa de
automação. Pesquise nesta ordem: **pywinauto** (Python, já é dependência de
build), depois AutoIt. Não escreva isso agora — a transitividade da 5.1 cobre o
que importa e roda em CI sem GUI nenhuma.

---

## 6. Tarefas, em ordem

Faça na ordem: cada uma depende da anterior estar verde.

| # | Tarefa | Onde |
|---|---|---|
| **T0** | Ambiente da seção 2 instalado; `cmake --build` passando | — |
| **T1** | Trocar o `.gitattributes` herdado por um que force LF no que os geradores leem e escrevem (`*.ui`, `*.json`, `*.cpp`, `*.hpp`, `*.sh`, `*.py`, `ed.rc`) | [.gitattributes](../.gitattributes) |
| **T2** | Presets de Windows: ou `generator: Ninja` com `CMAKE_BUILD_TYPE`, ou presets multi-config com `configuration` | [CMakePresets.json](../CMakePresets.json) |
| **T3** | `_CRT_SECURE_NO_WARNINGS` para o MSVC; compilar limpo | `src/core/CMakeLists.txt`, `src/app/CMakeLists.txt` |
| **T4** | Guardar `golden`/`golden_gui` com `if(UNIX)` | [tests/CMakeLists.txt](../tests/CMakeLists.txt) |
| **T5** | `ctest -C Release` verde, inclusive com `WE2002_TEST_IMAGE` apontando para uma imagem real | — |
| **T6** | Corrigir os três `toStdString()` e o `path::string()` (§4.1, §4.2). Testar com o repo e a imagem em caminho **acentuado**, de propósito | `MainWindow.cpp`, `DataFiles.cpp`, gerador do `Database.cpp` |
| **T7** | `.ico` embutido: `make_icon.py` passa a emitir `newWe2002.ico` (PIL salva multi-tamanho), mais um `.rc` de uma linha compilado só em `WIN32` | [tools/make_icon.py](../tools/make_icon.py), `src/app/` |
| **T8** | Paridade de bytes da §5.1, nas duas imagens (europeia e japonesa) | — |
| **T9** | Paridade contra `Debug\ed.exe` nativo, §5.2 | — |
| **T10** | Empacotar (seção 7) | — |
| **T11** | CI (seção 8) | [.github/workflows/ci.yml](../.github/workflows/ci.yml) |
| **T12** | Registrar o resultado na seção Fase 7 do [PLAN-LINUX.md](/docs/PLAN-LINUX.md) e neste arquivo | — |

Depois de qualquer mexida em gerador, **rode o gerador e o `--check`**:

```bat
python tools\rc2ui.py --check
python tools\apply_glossary.py --check
```

E antes de comitar, rode o `ctest` no **Linux** também. Toda correção desta fase
tem de valer nas duas plataformas; nenhuma delas justifica `#ifdef` no `core`.

### Bônus que só o Windows consegue

**ASan roda aqui.** Nesta máquina Linux não roda — a Citrix substitui o `dlsym`
via `/etc/ld.so.preload` e o runtime do ASan morre antes do `main` (ver
CLAUDE.md). O MSVC tem `/fsanitize=address`, e hoje o
`if(WE2002_SANITIZE AND NOT MSVC)` do [CMakeLists.txt](../CMakeLists.txt) linha
36 desliga tudo no MSVC.

Ligar isso e rodar `we2002_tests` e um `roundtrip` sob ASan é a primeira
oportunidade real de varrer 198 `strcpy` e 8.456 linhas de código de 2002 em
busca de estouro. Não é obrigatório para fechar a fase, mas é o item de maior
retorno da lista — e é *aqui* ou em lugar nenhum.

---

## 7. Empacotamento

Duas saídas, na ordem de esforço:

**Zip portátil** — e ele funciona sem configuração nenhuma, porque o
`DataFiles.cpp` procura os dados **ao lado do executável antes** de qualquer
outro lugar:

```bat
cmake --install build --config Release --prefix dist\newWe2002
C:\Qt\6.5.3\msvc2019_64\bin\windeployqt.exe dist\newWe2002\bin\newWe2002.exe
copy data\*.txt dist\newWe2002\bin\
```

Note que o `install` põe o `.exe` em `bin\` (é o `CMAKE_INSTALL_BINDIR`), o que
é convenção Unix. Para um zip de Windows, ou mova para a raiz do `dist\`, ou
aceite o `bin\` — o caminho relativo `..\share\newWe2002` continua resolvendo
nos dois casos. Copiar os `.txt` para junto do `.exe` faz o primeiro candidato
da busca acertar e torna a árvore imune a rearranjo.

Vai no zip também: as DLLs que o `windeployqt` trouxe, a DLL do libcurl, a
licença do curl, o `NOTICE.md` e o `README.md`.

**Instalador** — Inno Setup, depois que o zip estiver certo. Não invente:
empacote exatamente o conteúdo do zip que você já testou.

---

## 8. CI

> **O CI não roda sozinho, por decisão — e isso vale até o fim do projeto.**
> Os gatilhos `push` e `pull_request` do
> [ci.yml](../.github/workflows/ci.yml) estão desligados; sobrou o
> `workflow_dispatch`, então a matriz inteira roda à mão pelo Actions quando
> valer a pena. Enquanto a árvore está em movimento, runner queimando minuto a
> cada commit não diz nada que o build local não diga antes — e não diz o que
> importa: contra o `ed.exe` nenhum runner roda.
>
> Ligar de volta é descomentar as quatro linhas que ficaram no cabeçalho do
> `ci.yml`. Fazer isso **no fim do projeto**, quando verde-a-cada-commit passar
> a ser o objetivo.

O job `windows` foi ajustado do jeito que a Fase 7 pedia, mesmo sem rodar
automaticamente:

1. `continue-on-error: true` fora — quando ele rodar, vermelho é falha.
2. Ninja no lugar do gerador do Visual Studio, para o `CMAKE_BUILD_TYPE` valer
   alguma coisa (o gerador do VS é multi-config e o ignora). Some a necessidade
   de `--config` em cada comando.
3. Depois da T4, o `ctest` do Windows roda `core`, `ui_forms` e `glossary`. Os
   `golden`/`golden_gui` **não são nem registrados** fora do UNIX — não é que
   passem por acidente, é que não existem lá.
4. Os `--check` dos geradores acrescentados, como no job `linux` — é onde um
   CRLF vazado aparece.

Fica por fazer, para quando o CI voltar a rodar:

5. Rodar a §5.1 em CI: dois jobs produzindo o mesmo `roundtrip` e um terceiro
   comparando os hashes. Barra a divergência de compilador para sempre, sem
   imagem de CD no runner — só precisa de uma imagem sintética esparsa, que o
   `TestLoadUnterminatedFormation` já mostra como montar.

Nada de macOS. Não é "talvez depois".

---

## 9. Checklist de aceitação

A fase fecha quando **todas** derem certo:

- [x] `cmake --build` Release sem aviso
- [x] `cmake --build` Debug sem aviso
- [x] `ctest` verde, com `golden`/`golden_gui` fora da lista (T4 os registra só no UNIX)
- [x] `ctest` verde com `WE2002_TEST_IMAGE` numa imagem real — 73 checks
- [x] §5.1: `roundtrip` no MSVC dá o **mesmo SHA-256** que no GCC, na imagem europeia
- [x] §5.1 repetido na imagem japonesa
- [x] §5.2: contra o `Debug\ed.exe` nativo, só a faixa `405724..405739`
- [ ] Editor abre, carrega, **edita nome de time pela tela**, grava, e o resultado
      bate com o oráculo — *o lado `ed.exe` foi feito; o lado Qt não. Ver §11.*
- [x] Imagem em caminho com acento: abre e grava (§4.1) — e o sidecar `_url.txt`
      sai no mesmo diretório acentuado (§4.2)
- [x] Ícone certo no Explorer, na barra de tarefas e na janela
- [x] Zip portátil roda **sem Qt instalado** e sem variável de ambiente
- [x] Job `windows` do CI sem `continue-on-error` — mas o CI **não roda
      sozinho**: os gatilhos ficaram desligados até o fim do projeto (§8)
- [x] `python tools\rc2ui.py --check` e `apply_glossary.py --check` verdes no Windows
- [x] `ctest` continua verde no **Linux** depois de tudo
- [x] Resultado escrito na Fase 7 do [PLAN-LINUX.md](/docs/PLAN-LINUX.md)

## 10. O que não fazer

- **Não recompilar o `ed.exe`.** Precisa de MFC estático e não tem propósito: o
  binário de 2002 é o oráculo justamente por ser o de 2002.
- **Não "consertar" os 198 `strcpy`.** Silencie o C4996 e siga. Cada um é
  candidato a mudar bytes.
- **Não espalhar `#ifdef _WIN32` pelo `core`.** Se aparecer mais de um, o
  desenho está errado — leia a seção 5 do plano de novo.
- **Não trocar `std::filesystem` por API do Windows.** O problema da §4.1 é
  *encoding na fronteira*, não a biblioteca.
- **Não mexer nas divergências deliberadas** das Fases 5 e 6. Estão listadas no
  plano com o motivo de cada uma.
- **Não editar arquivo gerado à mão.** `Database.cpp`, `Tables.*`,
  `Offsets.hpp`, `src/app/ui/*` e os PNGs saem de gerador; o `ctest` pega.
- **Não empacotar macOS.** Não está na matriz e não vai estar.

---

## 11. Registro de execução

Executado em **2026-08-04**, Windows 11 Pro 26200, MSVC 19.44 (VS 2022 Build
Tools v143), Qt 6.5.3 msvc2019_64 (instalado por `aqtinstall`, não pelo
instalador oficial — ele exige conta), libcurl 8.x por vcpkg, Python 3.12.

O lado GCC da §5.1 rodou no **WSL Ubuntu 26.04** desta mesma máquina, fora da
árvore (`/root/build-gcc-release`), para não encostar no `build/` que veio da
máquina Linux.

### A resposta da seção 1

Sim: **o `.exe` do MSVC grava exatamente os mesmos bytes que o binário do GCC**,
nas duas imagens. Os três riscos apontados na seção 1 não se materializaram —
a ordem dos bits de `SquadNumbers`, o modo binário e o padding batem.

§5.1, `we2002_golden_tool roundtrip`, SHA-256 do arquivo depois da gravação:

| Imagem | MSVC | GCC |
|---|---|---|
| European Deluxe | `02432b4d22e479b3c4574f9c4c4b76d445ad4aa65dfe490835b6c1788e535356` | idêntico |
| Japonesa (SLPM-87056) | `a9299cc98bb9a0665da5ae40f7ab5cdd03de60c0b0498cf73633dd437655145e` | idêntico |

O `digest` também bate nos dois lados (`players`, `teams`, `ml`), antes e depois
do roundtrip — então não é só o `Save` que concorda, o `Load` também.

§5.2, `Debug\ed.exe` **nativo** contra o port, imagem europeia:

```
1 run(s), 15 byte(s) differ
     start        end    span    diff  sector      kind  region
    405724     405739      16      15     172      data  OFS_SQUAD_NUMBERS_NATIONAL+1008
```

Só a faixa conhecida, e mais nada. Isso responde a dúvida antiga do corte de
janela no Wine: **o corte nunca importou** — sem Wine, sem `:99` e com o
diálogo inteiro visível, o resultado é o mesmo.

E a janela Qt, rodando **do zip portátil**, com a imagem num caminho acentuado,
produziu byte a byte o mesmo `02432b4d…` do roundtrip headless. Ou seja: a
camada de widgets no Windows não muda nada, pelo menos na gravação limpa.

### O que quebrou, em ordem de surpresa

| # | Sintoma | Causa | Correção |
|---|---|---|---|
| 1 | **Todo binário morria antes do `main`**, sem imprimir nada, exit `0xC00000FD` | `we2002::Database` tem **1,21 MB** (só `players[1911]` são 1,17 MB) e é declarado como local em toda parte. Linux reserva 8 MB de pilha; MSVC reserva **1 MB** | `/STACK:8388608` no `CMakeLists.txt` da raiz — a mesma pilha contra a qual o código foi escrito, sem mover objeto nenhum para o heap |
| 2 | `error C2589: '(' : token inválido no lado direito de '::'` em `Sofifa.cpp` | `curl/curl.h` puxa `winsock2.h` e daí `windows.h`, que define `min`/`max` como macro e come os `std::max`/`std::min` | `NOMINMAX` em `target_compile_definitions`, não `#ifdef` no fonte |
| 3 | Ícone do `.ico` saía com **uma** entrada de 16×16 | O Pillow descarta de `sizes` tudo que for maior que a imagem em que o `.save()` foi chamado, e a chamada era na de 16 | Chamar no maior desenho e passar os outros em `append_images` |
| 4 | 5 arquivos "modificados" logo no `git status`, sem um byte de diferença | `core.filemode=true` num checkout Windows: só troca de 755 para 644 | `git config core.filemode false` (e `core.autocrlf false`, como a seção 2.3 manda) |

Nenhum deles estava previsto. Os três defeitos que a seção 4 previa
(`toStdString()`, `path::string()`, os `.sh` no ctest) eram reais e foram
corrigidos como planejado; o `C4996` e a janela de console também.

### Diferença de plataforma que ficou, de propósito

O sidecar `<imagem>_url.txt` sai com **CRLF** no Windows e LF no Linux — 3822
bytes contra 1911. O `ofstream` dele é aberto em modo texto, e é a única coisa
que o editor escreve que **não** é a imagem de CD. Não afeta paridade nenhuma:
os dois lados leem em modo texto, então o arquivo atravessa as plataformas sem
problema. Trocar para `ios::binary` mudaria o que o Bloco de Notas mostra sem
ganhar nada.

### O item que ficou aberto

"Editar nome de time pela tela e comparar com o oráculo" **não foi feito no lado
Qt**. O lado `ed.exe` foi: `tools/../scratchpad/drive_ed.py` seleciona o time,
troca `INTER` por `GOLDEN` e grava. O lado Qt trava em duas coisas desta
máquina:

- **A Citrix filtra input sintético.** `click_input()` move o ponteiro e nada
  acontece. Para o `ed.exe` isso não importa (o backend win32 do pywinauto
  posta `BM_CLICK`), e para os botões do Qt o padrão *Invoke* da UIA resolve —
  mas nada disso ajuda com teclado.
- **O Qt só publica os itens de um `QComboBox` para a UIA com o popup aberto**,
  e a enumeração do popup é intermitente: às vezes vem com 97 itens, às vezes
  vazia. Sem selecionar um time, os campos de nome ficam vazios e não há o que
  editar.

Isso é exatamente o que a §5.3 manda **não** perseguir agora. A gravação limpa
pela janela Qt já está provada byte a byte, e a camada de widgets é o mesmo
fonte que o `golden_gui` cobre no Linux. Fica para quando a Fase 7 virar CI de
verdade — e aí `pywinauto` continua sendo a primeira aposta, com a ressalva de
que a UIA do Qt precisa de retry.

### Detalhes que valem para quem repetir

- **Não use `python -c` com aspas por dentro no PowerShell.** As aspas somem no
  caminho e o Python recebe um script quebrado. Arquivo `.py` de verdade.
- **Python DPI-unaware não consegue clicar numa janela Qt.** Nesta tela a 150%,
  o Qt é per-monitor DPI aware e o Python não: as coordenadas que ele lê estão
  em outro espaço e o clique erra por um terço da tela, sem erro nenhum.
  `SetProcessDpiAwareness(2)` antes de qualquer coordenada.
- O `windeployqt` não traz o runtime da MSVC mesmo com `--compiler-runtime`
  quando o `VCINSTALLDIR` não está no ambiente; foi mais direto copiar
  `msvcp140*.dll` e `vcruntime140*.dll` do diretório `VC\Redist` à mão.
- O `.exe` também precisa de `z.dll` ao lado do `libcurl.dll` — o vcpkg linka
  o zlib como DLL.

| Data | Tarefa | Resultado |
|---|---|---|
| 2026-08-04 | T0 ambiente | VS Build Tools + Qt 6.5.3 (aqtinstall) + vcpkg + WSL para o lado GCC |
| 2026-08-04 | T1 `.gitattributes` | `* text=auto eol=lf`, binários marcados, os dois dumps do autor preservados em CRLF |
| 2026-08-04 | T2 presets | `windows-debug`/`windows-release`/`windows-asan` com Ninja; os presets Linux passaram a recusar `${hostSystemName}` = Windows |
| 2026-08-04 | T3 `C4996` | `_CRT_SECURE_NO_WARNINGS` no core e nos dois alvos de teste; build limpo nos dois modos |
| 2026-08-04 | T4 golden | `if(UNIX)` em volta de `golden`/`golden_gui` |
| 2026-08-04 | T5 `ctest` | 3 testes verdes; 73 checks com `WE2002_TEST_IMAGE` |
| 2026-08-04 | T6 encoding | `src/app/QtPath.hpp`, `qEnvironmentVariable`, e `UrlSidecarPath` sobre `path::string_type` no gerador |
| 2026-08-04 | T7 ícone | `make_icon.py` emite `newWe2002.ico`; `resources/newWe2002.rc` compilado só em `WIN32`; confirmado que o `.exe` mostra o ícone certo |
| 2026-08-04 | T8 §5.1 | SHA-256 idêntico ao do GCC nas duas imagens |
| 2026-08-04 | T9 §5.2 | só `405724..405739` |
| 2026-08-04 | T10 zip | 44,9 MB, roda com PATH limpo e sem Qt |
| 2026-08-04 | T11 CI | `continue-on-error` fora, Ninja no lugar do gerador do VS, `--check` dos geradores acrescentado. Depois disso, **os gatilhos automáticos foram desligados** — o CI só roda por `workflow_dispatch` até o fim do projeto (§8) |
| 2026-08-04 | T12 | este registro |
