# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Regra obrigatória: validação visual no display `:98`

**Toda execução com GUI — rodar o editor, tirar screenshot, dirigir a janela com
`xdotool` — deve acontecer no `DISPLAY=:98`.** O `:1` é a sessão real do usuário;
abrir janelas nele atrapalha o uso da máquina.

**Era o `:99` até 2026-08-20**, e a troca foi a pedido do usuário. O motivo é
concreto e vale saber: outro projeto desta máquina
(`~/desenvolvimento/github/World-Of-Football`) mantém uma janela de 1024×768
no `:99`, e a guarda de janela grande do `golden_check.sh` — que existe
justamente para não dirigir a janela errada — passou a recusar toda corrida.
A guarda está certa; quem muda de lugar é o nosso servidor. Registro
histórico (`CORR-*`, logs de execução, "medido no `:99` em 2026-08-11")
**continua dizendo `:99`**, porque é o que aconteceu.

O servidor sobe assim, e **sem `-auth`**:

```sh
Xvfb :98 -screen 0 1280x1024x24 -nolisten tcp &
```

Sem `-auth` não há cookie, e **`XAUTHORITY` vazio é o certo** — não herde o do
desktop (`/run/user/1000/gdm/Xauthority`), que o shell traz e só confunde quem
depurar depois. Se algum dia o servidor subir por `xvfb-run`, aí ele **tem**
cookie próprio, e sem apontar o `XAUTHORITY` para ele o Qt morre antes de abrir
janela com `Invalid MIT-MAGIC-COOKIE-1 key` seguido de
`qt.qpa.xcb: could not connect to display :98`. As ferramentas já tratam os dois
casos: procuram o `-auth` no `ps` e limpam a variável quando não acham.

```sh
export DISPLAY=:98
export XAUTHORITY=$(ps -o args= -C Xvfb \
  | sed -n 's/.*Xvfb :98 .*-auth \([^ ]*\).*/\1/p' | head -1)
```

O `make run-98` faz isso sozinho (ver a seção do Makefile), e o
`roteiro.sh` — que todo gate do `wte/` carrega — também.

**O número mora em um lugar por ferramenta**, para a próxima mudança custar uma
linha: `XVFB` nos dois `Makefile`, `WTE_DISPLAY` nos scripts de `wte/tools/`, e
`GOLDEN_DISPLAY` nos de `tools/`. Todos com `:98` de default.

Se por qualquer motivo não for possível usar o `:98` — servidor caído, resolução
insuficiente, app que exige compositor Wayland, ferramenta que não respeita
`DISPLAY` — **pergunte ao usuário antes de cair para o `:1`**. Nunca faça esse
fallback silenciosamente.

O diálogo principal `IDD_ED_DIALOG` tem 718×337 DLU ≈ **1077×548 px** e **cabe
inteiro** nos 1280×1024 atuais. (Isso já foi limitação: o Xvfb era 960×672 e
cortava a borda direita. Se ele voltar a subir numa resolução menor que 1077
de largura, validar a janela inteira exige reiniciá-lo — **pergunte antes**.)

Screenshot de uma janela específica:

```sh
DISPLAY=:98 xdotool search --pid <PID> | while read i; do \
  echo "$i :: $(DISPLAY=:98 xdotool getwindowname $i)"; done
DISPLAY=:98 import -window <WINDOW_ID> out.png
```

`import -window <id>` falha com `unable to read X window image: Resource
temporarily unavailable` quando a janela está obscurecida por um modal — e o
port abre um aviso modal já na carga. Dispense o aviso primeiro, ou capture
`-window root`, que sempre funciona.

Disponível no host: `Xvfb`, `xvfb-run`, `xdotool`, `import` (ImageMagick),
`ffmpeg`. **Não** instalados: `wmctrl`, `scrot`, `x11vnc`.

**Não há window manager no `:98`.** Duas consequências ao dirigir janela:

- `xdotool windowactivate` falha com `XGetInputFocus returned the focused
  window of 1`. Não há foco para transferir. Dirija por coordenada absoluta —
  `xdotool mousemove <x> <y> click 1` —, que independe de foco.
- `xdotool type --window <id>` usa `XSendEvent` e **embaralha string longa**.
  Um caminho de 60 caracteres chegou truncado num `CFileDialog` e produziu
  "Path does not exist" que parecia bug do app. Prefira digitar curto: o
  `make wte` existe em parte por isso, mapeando uma letra de unidade para
  encurtar o caminho.
- **O foco de teclado segue o ponteiro** (`PointerRoot`), e é isto que decide
  para onde vai um `xdotool key`. Uma caixa de aviso que sobe sozinha — depois
  de um export, por exemplo — **não** recebe foco; o `Return` vai para onde o
  último clique deixou o ponteiro, que costuma ser o diálogo por baixo, e
  **fecha o diálogo** em vez da caixa. O gesto certo é `xdotool mousemove
  --window <caixa>` e só então `xdotool key Return`, sem `--window`. Medido em
  2026-08-31, três gestos na mesma corrida (CORR-WTE-137): mousemove+`Return`
  fecha a caixa e preserva o diálogo; `xdotool key --window` (XSendEvent) não é
  entregue; clicar dentro da caixa leva o diálogo junto. Consequência prática:
  **teclar uma vez e esperar o efeito**, nunca em laço — o `Return` a mais,
  disparado enquanto a caixa ainda some, é o que fecha o que não devia.

### A mesma regra no Windows: **fora da tela**

**Nenhum editor abre na sessão visível do usuário no Windows tampouco.** A
razão é a do `:98` e não muda com a plataforma: ele usa a máquina enquanto o
trabalho corre, e janela que aparece atrapalha e rouba foco. O que muda é o
mecanismo — lá existe um Xvfb, aqui não.

Lance e **mova para fora da tela imediatamente**, antes de dirigir:

```
SetWindowPos(h, NULL, -32000, -32000, 0, 0,
             SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)
```

`SendMessage`/`BM_CLICK` e `PrintWindow` **continuam funcionando** com a janela
ali. Medido em 2026-08-27 sobre o `Debug\ed.exe`: a mesma captura, 7.337 pixels
de conteúdo, dentro e fora da tela. O usuário vê no máximo um piscar no
instante da abertura.

Três coisas que **não** servem aqui, todas medidas:

- **Desktop Win32 separado** (`CreateDesktop` + `STARTUPINFO.lpDesktop`) seria
  o equivalente exato do `:98`, e **não funciona nesta máquina**: o
  `CreateProcessW` sai com erro **123** em toda variante testada — com
  `lpApplicationName`, com `lpCommandLine`, e até com `lpDesktop` vazio. A
  suspeita é o Citrix App Protection, cuja `Desktop Viewer` roda aqui e
  engancha API. Não insista nesse caminho.
- **`SendInput`, `SetCursorPos`, `click_input`** — dependem de janela visível e
  de foco, e a Citrix desta máquina filtra input sintético. É o mesmo tropeço
  registrado na §11 do [docs/PLAN-WINDOWS.md](docs/PLAN-WINDOWS.md). Dirija por
  **mensagem de janela**, que não passa por esse filtro.
- **`ShowWindow(SW_HIDE)`** — esconde, mas o `PrintWindow` passa a capturar
  quadro em branco. Fora da tela preserva o desenho; escondido, não.

Duas armadilhas de identificação de janela no Windows, já pagas:

- **Botão de VCL não é `Button`.** O editor do Obocaman usa `TBitBtn`, e um
  filtro por classe `Button` não acha o `Sim` do aviso de tamanho. Filtre por
  `Contains("BitBtn") || Contains("Button")`.
- **`Process.MainWindowTitle` mente durante a carga.** Ele devolve o modal da
  vez (`Cuidado`, `Sobre...`), não o formulário principal. Enumere as janelas
  visíveis do PID e escolha pela largura, como o `wait_for_main` faz no Linux.
- **`GetWindowText` não lê controle de outro processo.** Ele devolve a legenda
  em cache, então botão e título saem certos e **`Edit` sai vazio** — inclusive
  logo depois de um `WM_SETTEXT` que funcionou. Confira com `WM_GETTEXT` de
  verdade (`SendMessageW` com buffer); senão a guarda acusa falha que não
  houve.
- **`ed.exe` esquecido de uma corrida anterior segura a imagem**, e o
  `CFileDialog` recusa com *"This file is in use"*, que parece erro de caminho
  e não é. Mate o que sobrou antes de abrir — no Linux o `golden_check.sh` já
  faz o equivalente com a guarda de janela grande.

Num display escalado (o desta máquina está a 150%), processo que não é
DPI-aware lê coordenada virtualizada e captura recorte errado. Chame
`SetProcessDPIAware()` antes de medir ou capturar.

---

## O que é este repositório

Editor binário do **Winning Eleven 2002 (PSX)** — edita times, jogadores,
táticas, uniformes e bandeiras gravando direto na imagem de CD. Escrito em
2002 por Francesco Moriero (ver `readme.txt`), como app **MFC** do Visual C++ 6
migrado para VS2010. Fork com feature adicional de importar dados do SoFIFA.

O código é Windows-only. Há um plano de port para Linux em
[docs/PLAN-LINUX.md](docs/PLAN-LINUX.md) — **leia antes de mexer em qualquer coisa de
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

## Compilar e testar

O [Makefile](Makefile) da raiz é um wrapper fino sobre os presets — não
substitui o CMake, e é opcional. `make` sem alvo lista tudo. O que ele resolve
que a linha de comando crua não resolve:

| Alvo | O que faz |
|---|---|
| `make run` | compila, **copia** `roms/golden-european-deluxe.bin` para `work/` e abre o editor sobre a cópia |
| `make run-jp` | idem com `roms/japanese-shift-jis.bin` |
| `make run-98` | `run` no `:98`, resolvendo o `XAUTHORITY` do Xvfb sozinho |
| `make oracle` / `oracle-98` | abre o `Debug/ed.exe` original sob o runner Wine do Bottles, em prefix dedicado |
| `make wte` / `wte-98` | abre o editor de terceiro do Obocaman (C++Builder 6, PE32), em prefix `win32` próprio |
| `make fresh` | descarta as cópias de trabalho e refaz do original |
| `make test` / `test-release` | `ctest` sem os golden |
| `make golden` / `golden-gui` | exportam `WE2002_GOLDEN_IMAGE` absoluto |
| `make gen` / `gen-check` | os geradores; o `-check` complementa o `ctest` com `git diff` |
| `make distclean` | remove todos os `build*/` e o `work/` |

`PRESET=debug|release|asan|ubsan` escolhe o preset (e o `binaryDir` certo);
`IMAGE=` troca a imagem. `work/` está no `.gitignore`.

O `oracle` mantém o prefix Wine em `work/wineprefix` (criado uma vez, reusado
depois) e **nunca** toca numa bottle existente — `ed.cpp:75` chama
`COleObjectFactory::UpdateRegistryAll()`, que escreve no registry. A cópia do
oráculo é separada da do port e se chama `we2002.bin`, porque o filtro default
do `CFileDialog` é literalmente esse nome (`edDlg.cpp:1331`); o alvo ainda
cria `Debug/we2002.bin` como symlink para ela, já que o diálogo abre no CWD —
assim o arquivo aparece na primeira tela sem navegar.

O `gen-check` confere `extract_legacy_data.py` e `port_database.py` por
`git diff` porque **esses dois não têm `--check`** — só `rc2ui.py` e
`apply_glossary.py` têm, e são os que o `ctest` registra (`ui_forms`,
`glossary`).

Direto pelo CMake:

```sh
cmake --preset debug        # ou: cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build --preset debug
ctest --preset debug
```

Presets em [CMakePresets.json](CMakePresets.json): `debug`, `release`, `asan`,
`ubsan`. O `asan` só roda por dentro do `tools/run-sanitized.sh` nesta máquina
(ver a seção de sanitizers).

No Windows os presets são outros — `windows-debug`, `windows-release`,
`windows-asan` — e os quatro de cima se **recusam** a configurar ali. Não é
implicância: sem `generator` explícito o CMake escolhe o gerador do Visual
Studio, que é multi-config e **ignora** `CMAKE_BUILD_TYPE`; pedir `release`
entregaria Debug em silêncio. Os presets de Windows usam Ninja e assumem os
caminhos da seção 2 do [docs/PLAN-WINDOWS.md](docs/PLAN-WINDOWS.md)
(`C:/vcpkg`, `C:/Qt/6.5.3/msvc2019_64`); para outros, `-D` na linha de comando
ganha do preset. Rode de dentro do *x64 Native Tools Command Prompt*.

Duas coisas específicas do MSVC que já custaram tempo e estão no CMake:

- **`/STACK:8388608`.** `Database` tem 1,21 MB e é declarado como local em toda
  parte. O MSVC reserva 1 MB de pilha contra os 8 MB do Linux, e sem isso todo
  binário morre antes do `main` com `STATUS_STACK_OVERFLOW` — sem imprimir nada.
- **`NOMINMAX`.** O core não inclui `windows.h`, mas `curl/curl.h` inclui, e as
  macros `min`/`max` de lá comem os `std::max`/`std::min` de `Sofifa.cpp`.

Instalar:

```sh
cmake --install build-release --prefix ~/.local
```

Põe `bin/newWe2002`, os `.txt` em `share/newWe2002/`, o `.desktop`, os sete
tamanhos de ícone e o AppStream. O binário acha os dados **relativo a si mesmo**
(`../share/newWe2002`), não por caminho absoluto compilado, então a árvore
instalada pode ser movida. Ordem de busca em
[src/app/DataFiles.cpp](src/app/DataFiles.cpp): `$WE2002_DATA_DIR`, ao lado do
executável, o prefixo instalado, o `data/` do fonte.

**`newWe2002` é o nome do produto, `we2002` é o nome do formato.** O executável,
`share/newWe2002/`, `share/doc/newWe2002/`, o ícone, o appid
`io.github.aguilasa.newWe2002` e o `project()` do CMake usam `newWe2002`. O
namespace C++, os headers em `include/we2002/`, os alvos `we2002_core` /
`we2002::core` / `we2002_tests` / `we2002_golden_tool` e todas as variáveis
`WE2002_*` (de CMake e de ambiente) continuam `we2002`. Renomear o namespace
arrastaria os geradores e o glossário inteiro sem ganho nenhum.

Os 61 checks unitários rodam sem imagem. Dois testes ficam mais fortes com
uma, e se reportam como *skipped* sem ela:

```sh
# unitários contra uma imagem real (só leitura, mas passe cópia mesmo assim)
WE2002_TEST_IMAGE=/caminho/copia.bin ./build/tests/we2002_tests

# golden tests: ed.exe sob Wine vs o port, byte a byte
WE2002_GOLDEN_IMAGE=/caminho/imagem.bin ctest --test-dir build -R golden
```

São dois: `golden` compara o core headless com o `ed.exe`, `golden_gui` põe a
janela Qt no lugar do core. Os dois usam Wine e o `:98`.

### O golden test

`tools/golden_check.sh` é o teste de regressão que importa. Ele faz duas
cópias da imagem, passa uma pelo `ed.exe` sob Wine (`tools/golden_run.sh`) e a
outra pelo port, e compara com `tools/golden_compare.py`. Falha se aparecer
**qualquer** divergência além de uma faixa conhecida.

`WE2002_GOLDEN_MODE=gui` troca o lado do port: em vez do `tests/golden_tool.cpp`
headless, dirige a janela Qt com `tools/golden_gui.sh`. É o teste `golden_gui`
do ctest, e é o que cobre a camada de widgets da Fase 5.

**Os dois lados aceitam um roteiro de edição, e os nomes das variáveis são
diferentes:** `GOLDEN_EDIT` no `golden_run.sh` (o `ed.exe`) e
**`GOLDEN_GUI_EDIT`** no `golden_gui.sh` (o port). Exportar só um deles num
modo `gui` não dá erro — um lado edita, o outro não, e os dois divergem em toda
faixa tocada, num falso vermelho que parece bug do port. Como os dois recebem
`$MAIN` em escopo e definem `dlu_x`/`dlu_y` com a mesma conversão, o **mesmo**
trecho de shell serve aos dois:

```sh
R="$(cat tools/par/8.1-nomes-6-slots.sh)"
WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$R" GOLDEN_GUI_EDIT="$R" \
  tools/golden_check.sh roms/ptbr-remaster.bin
```

**`tools/par/`** guarda esses roteiros, um por item do inventário de paridade
([docs/PARIDADE-FUNCIONAL.md](docs/PARIDADE-FUNCIONAL.md) §8), nomeados pelo
item. Verde de golden é asserção sobre um estímulo: sem o estímulo versionado a
corrida não é repetível, e o par verde+faixa vira lembrança. Toda corrida da
série leva também um **controle positivo** — a cópia gravada comparada contra a
imagem original —, sem o qual um roteiro que não chegou a editar nada passa
verde sem medir nada.

Essa faixa é `405724..405739` (`OFS_SQUAD_NUMBERS_NATIONAL+1008`): o slot 64
de um array de 63, que o original lê e grava por engano a partir da memória
vizinha (`ml_teams[0]`). O port preserva o que está na imagem em vez de
reproduzir comportamento indefinido. É a única divergência aceita — se
aparecer outra, é bug do port. Detalhe na Fase 3 do
[PLAN-LINUX.md](docs/PLAN-LINUX.md).

O script não toca na imagem de origem, mas usa ~950 MB de temporário. Precisa
do `Debug/ed.exe`, de Wine e do `:98`; por isso não roda em CI.

**Feche qualquer editor aberto no `:98` antes de rodar.** Os dois lados acham o
diálogo principal **pelo tamanho** — ele não tem título —, então uma janela
esquecida de um teste manual é dirigida em vez da que está sob teste, e o
resultado é um diff de bytes que parece bug do port. Duas guardas: o
`golden_check.sh` se recusa a começar se houver janela ≥ 900×450 no `:98`, e o
`golden_gui.sh` restringe os candidatos ao `_NET_WM_PID` do processo que ele
mesmo lançou. O `golden_check.sh` fixa `DISPLAY=:98` por conta própria: o
`ctest` repassa o `DISPLAY` do shell (`:1` aqui), e as janelas normais da sessão
real derrubariam a guarda.

Duas armadilhas conhecidas ao mexer nisso:

- **O editor não é idempotente.** `Load`+`Save` troca os dois primeiros
  cobradores de cada clube de ML (`OFS_KICKER`), porque `Load` lê o par
  trocado e `Save` grava na ordem declarada. Gravar duas vezes volta ao
  início. É bug do original, reproduzido de propósito.
- **`Load`+`Save` sem editar nada não devolve a imagem intacta**, e não
  deveria: o `Save` reconstrói as all-star a partir dos links
  (`OFS_PLAYER_ATTR_8`). O oráculo faz o mesmo.

### Sanitizers e o bloqueio da Citrix

```sh
cmake -B build-asan -DCMAKE_BUILD_TYPE=Debug -DWE2002_SANITIZE=ON
cmake --build build-asan -j
tools/run-sanitized.sh ./build-asan/tests/we2002_tests
```

O wrapper `tools/run-sanitized.sh` é **obrigatório** para ASan nesta máquina.
Motivo: a Citrix põe `/usr/local/lib/AppProtection/libAppProtection.so` em
`/etc/ld.so.preload`, e essa lib exporta o próprio **`dlsym`** (os demais
símbolos são hooks de X11 — `XGetImage`, `XNextEvent`, `XQueryExtension` — que
implementam a proteção anti-screenshot).

O runtime do ASan chama `dlsym(RTLD_NEXT, "malloc")` na própria inicialização,
antes de libc e libstdc++ subirem. Com o `dlsym` da Citrix no caminho, isso
estoura: **qualquer** binário com ASan morre antes do `main`, sem imprimir nada.
`-static-libasan` não resolve — o problema não é ordem de carregamento, é o
`dlsym` substituído.

O script entra num user+mount namespace sem privilégio e monta um arquivo vazio
por cima do `/etc/ld.so.preload`. Só a árvore daquele processo enxerga isso;
nada no sistema muda, não precisa de root, e a App Protection continua ativa no
resto da sessão.

UBSan não é afetado e roda direto:

```sh
cmake -B build-ubsan -DWE2002_SANITIZE=ON -DWE2002_SANITIZERS=undefined
```

Existe uma skill `zorin-citrix-dconf-fix` para outro estrago da mesma
instalação da Citrix (dock e Zorin Appearance). São problemas irmãos, causas
diferentes.

## Rodar o editor original (oráculo)

Para o ciclo abrir → gravar, use `tools/golden_run.sh <copia.bin>`: ele sobe o
Wine num prefix próprio, atravessa os diálogos e encerra sozinho. Aceita
`GOLDEN_EDIT` com um trecho de shell para fazer edições na tela antes de
gravar (`dlu_x`/`dlu_y` convertem coordenadas direto do `ed.rc`).

Para mexer na interface à mão, o binário pré-compilado `Debug/ed.exe` (PE32+
x86-64, MFC estático) roda sob o runner Wine do Bottles:

```sh
export DISPLAY=:98
export WINEPREFIX=<prefix dedicado>
export WINEDEBUG=-all
WINE=/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin
cd Debug && "$WINE/wine64" ed.exe
```

Encerrar: `WINEPREFIX=<prefix> "$WINE/wineserver" -k`

Notas:

- **Não reusar a bottle `DiztinGUIsh`.** `ed.cpp:75` chama
  `COleObjectFactory::UpdateRegistryAll()`, que escreve no registry do prefix.
- O `ed.exe` é x64 e casa com o `wine64`. O runner **também** roda 32-bit —
  tem `lib32/wine/i386-{unix,windows}` e o `bin/wine` é um ELF 32-bit —, o que
  é o que faz o `make wte` funcionar. Isso depende do stack X i386 no host;
  sem ele o `winex11.drv` de 32 bits não carrega e o app morre antes da janela.
- `wineboot` reclama de FreeType e `/etc/ld.so.preload` reclama de
  `libAppProtection.so` (Citrix). Ambos benignos — as fontes renderizam.
- `Debug/ed.exe` é o **oráculo de referência** para os golden tests do port.
  Manter no disco mesmo depois de adicionar `.gitignore`.
- O `ed.exe` abre um `CFileDialog` já no `OnInitDialog` e depois avisa que a
  imagem não tem 474.431.328 bytes. O aviso é só aviso — ele carrega assim
  mesmo. O diálogo principal **não tem título**, então só dá para achá-lo pelo
  tamanho; é o que o `wait_for_main` faz.
- O diálogo principal tem 1077 px de largura e o Xvfb já teve 960: o Wine cortava a
  borda direita. O `CMB_WRITE` fica em x≈315, dentro da parte visível, então o
  golden test funciona mesmo cortado.

Rebuild do `.exe` exige MSVC + MFC estático no Windows. MinGW e Winelib não
servem: nenhum dos dois distribui MFC.

**`Ctrl+A` não seleciona tudo num `CEdit` do Win32.** Ao escrever um teste que
digita a mesma coisa no `ed.exe` e no port, limpar o campo com `End`,
`shift+Home`, `BackSpace` — com `ctrl+a` os dois recebem textos diferentes e o
diff acusa uma divergência que não existe.

## Rodar o editor de terceiro (`make wte`)

O **WE2002 Team Editor v0.99** do Obocaman (2002), em tradução PT-BR, mora em
`we-team-editor/`. É outro editor do mesmo jogo, de outro autor. **Não é
oráculo de nada** — nenhum teste o mede; ele roda só para comparar interface e
garimpar ideia. Tem coisa que o `ed.exe` não tem: camisa e bandeira 2D em tempo
real com colar-cores, preço derivado dos atributos (do jogador ou do time
inteiro), import de jogador de `.mcr`, contador de slots de ML livres na tela.

```sh
make wte      # DISPLAY do shell -- o ponto do alvo é olhar
make wte-98   # no Xvfb
```

O que ele não compartilha com o `make oracle`, e não pode:

- É **Borland C++Builder 6, PE32**. Precisa de prefix `WINEARCH=win32` próprio
  (`work/wineprefix-wte`) e do loader `wine`, não do `wine64`.

  Este `CLAUDE.md` dizia "Delphi 6" até 2026-08-05, e o engano é fácil: os dois
  produtos são do mesmo ano, usam a mesma VCL, os mesmos runtime packages
  (`rtl60.bpl`/`vcl60.bpl`, ambos na pasta) e o mesmo formato de formulário
  `.dfm`. O que separa é o *name mangling* (`$qqr`, do `__fastcall` da Borland,
  que o Delphi não emite), os símbolos `___CPPdebugHook` /
  `__GetExceptDLLinfo`, e a string `c:\bcb\emuvcl\utilcls.h` — `emuvcl` é a
  camada que emula em C++ os recursos de linguagem do Delphi.
- Cópia própria da imagem, porque os três editores gravam in-place.
- O `winex11.drv` de 32 bits exige o stack X **i386** no host. Sem ele o app
  morre antes de desenhar janela, sem nada na tela e só
  `Initialization of L"winex11.drv" failed` no log do Wine. O alvo confere e
  imprime a linha do `apt`.

O diálogo de abrir não engole caminho longo digitado (ver a nota do `:98`
acima), então o alvo mapeia `E:` para `work/` e imprime o caminho curto para
colar. O aviso de tamanho é o mesmo do `ed.exe` e é igualmente inofensivo.

`we-team-editor/` está no `.gitignore`: binário sem fonte e sem licença não
entra no repositório. O usuário mantém a pasta, como faz com `roms/`.

**Nada disto vale no Windows, e a diferença é grande.** Lá o
`we-team-editor.exe` é só um PE32 num x64: o WOW64 o roda **nativo**, sem
Wine, sem prefix `win32`, sem loader de 32 bits e sem o stack X i386 — as três
guardas do alvo `wte` deixam de ter objeto. Quem abre os editores no Windows é
o [`make.ps1`](make.ps1) da raiz (`run-obocaman`, `run-lazarus`); quem compila
e verifica o app Lazarus é o [`wte/make.ps1`](wte/make.ps1). Os dois `Makefile`
não rodam lá — são GNU make + bash. Ver
[docs/PLAN-WTE-WINDOWS.md](docs/PLAN-WTE-WINDOWS.md), que também registra os
onze consertos de portabilidade que a porta exigiu e o que **não** roda no
Windows (a bateria golden inteira, que depende de Xvfb, `xdotool` e Wine).

Existe um plano de engenharia reversa desse binário, com alvo em Lazarus/FPC
nativo no Linux, em [docs/PLAN-WTE-LAZARUS.md](docs/PLAN-WTE-LAZARUS.md). É
**projeto separado** do `newWe2002` — não compartilha build nem código, só o
conhecimento de formato (`Offsets.hpp`, `we2002_core`). Nenhuma fase foi
executada. O plano traz o diagnóstico do binário já medido: 18 formulários
`.dfm` extraíveis, 96 handlers com nome e endereço recuperados do VMT, e 19 dos
nossos 69 `OFS_*` batendo numa tabela em `.data` do próprio `.exe`.

## Rodar o port

```sh
make run-98                 # cuida da cópia e do XAUTHORITY
# ou, à mão (exige DISPLAY e XAUTHORITY já exportados — ver a regra do :98):
./build/src/app/newWe2002 /caminho/copia.bin
```

O argumento é opcional; sem ele abre o `QFileDialog`, como o original. Ele
existe para o `golden_gui.sh` conseguir dirigir a janela. O aviso de
"não tem 474.431.328 bytes" aparece igual ao do `ed.exe` e é só aviso.

## Imagens de CD para teste

As duas imagens que os testes usam ficam em **`roms/`, na raiz deste
repositório**:

| Arquivo em `roms/` | Release | Uso |
|---|---|---|
| `golden-european-deluxe.bin` | Winning Eleven 2002 – European Deluxe 2002-03 | **Imagem golden.** Todos os offsets batem, nomes latinos. Vem com `golden-european-deluxe.cue` ao lado. |
| `japanese-shift-jis.bin` | World Soccer Winning Eleven 2002 (Japan), SLPM-87056, dump de arquivo único | **Melhor imagem japonesa para testes.** Valida `kanjitoascii`/`asciitokanji`. ECC íntegro — use esta para testar que o port reproduz o mesmo ECC inválido que o `ed.exe` ao gravar. Só track de dados, sem `.cue`: não serve para jogar. |

Os nomes são deste repositório, não dos dumps: minúsculas, sem espaço, e dizem
para que a imagem serve. O `.cue` foi ajustado para apontar para o `.bin`
renomeado.

`roms/` está no `.gitignore` — são ~780 MB e não entram no versionamento. O
usuário garante que os arquivos estão lá; **não copie de outro lugar nem baixe
nada**. Se a pasta estiver vazia, avise em vez de improvisar.

Duas releases que não vale usar:

- `World Soccer Winning Eleven 2002 (Japan)` em dump multi-track (9 tracks +
  `.cue` válido) — é a de jogar, mas para testes é redundante com a de arquivo
  único e tem ECC degradado (211/300 setores zerados). Os dois dumps japoneses
  divergem em 3 bytes de dados (patch anti-pirataria em código MIPS), fora de
  qualquer região do editor; comparação na seção 3 do
  [PLAN-LINUX.md](docs/PLAN-LINUX.md).
- `Pro Evolution Soccer 2 (Europe) (EnFrDe)` — **NÃO USAR com o
  `newWe2002`.** Layout diverge após ~2 MB; o editor corrompe a imagem.
  A proibição é sobre este editor, e só. **PES2 é outro jogo, com projeto
  próprio** ([docs/PLAN-PES2-PSX.md](docs/PLAN-PES2-PSX.md)), e ali as duas
  releases europeias — `(EsIt)` e `(EnFrDe)` — são justamente as duas
  amostras de trabalho. Ver a seção de PES2 mais abaixo.

**Sempre trabalhar sobre cópia** — o editor grava in-place e cada imagem tem
~474 MB. As de `roms/` são as originais: copie para o scratchpad antes de
apontar o editor ou o golden test para elas.

## PES2 (PSX) — projeto separado, em `tools/pes2/`

*Pro Evolution Soccer 2* (PlayStation, Konami, 2002, `SLES-03957`) é um
**quarto projeto** deste repositório, ao lado do `newWe2002`, do `wte/` e
dos planos de Windows. O objetivo é mapear o banco de times e jogadores da
imagem de CD e tornar viável um editor escrito do zero — **não existe
editor conhecido para ele**, e portanto não existe oráculo. O plano é
[docs/PLAN-PES2-PSX.md](docs/PLAN-PES2-PSX.md); o apêndice de nomes
fictícios é [docs/PES2-NOMES.md](docs/PES2-NOMES.md).

Ele **não compartilha código** com o `newWe2002`: nada em `src/` sabe o que
é PES2, e `tools/pes2/` é Python 3 e shell puros. O que se empresta é
conhecimento de formato — as duas engines são a mesma, e o `KanjiToAscii`
do WE2002 decodifica o título de save do PES2 sem uma linha de adaptação.

Duas imagens, as duas em `roms/`, as duas fora do versionamento:
`Pro Evolution Soccer 2 (Europe) (EsIt)/` e `…(EnFrDe)/`. São **dumps
multi-track** — 1 trilha de dados e 7 de áudio —, e todo offset só vale
dentro do `(Track 1).bin`. O banco é o mesmo nas duas; o que muda é onde
cada tabela cai dentro do overlay, e é por isso que o mapa ancora por
**marcador**, nunca por offset constante.

As ferramentas, e o que cada uma responde:

| Comando | O que faz |
|---|---|
| `python3 tools/pes2/iso.py ls\|extract\|inject <track1.bin>` | lê e reinjeta arquivo preservando setor e cauda EDC/ECC |
| `python3 tools/pes2/iso.py roundtrip <track1.bin>` | a guarda: reescreve os 244 arquivos e exige imagem idêntica |
| `python3 tools/pes2/iso.py negative <track1.bin> --tmpdir <dir>` | a prova de que a guarda sabe ficar vermelha |
| `python3 tools/pes2/tables.py <track1.bin> --check` | conta e digere as catorze tabelas de texto |
| `python3 tools/pes2/diff_releases.py <a> <b> --check` | o confronto entre as duas releases |
| `python3 tools/pes2/memcard.py <card.mcd> <track1.bin> --check` | alinha o memory card e fecha as fronteiras de elenco |
| `python3 tools/pes2/team_map.py <track1.bin> --team N` | onde o time N mora em cada uma das oito listas |
| `python3 tools/pes2/poke.py <copia.bin> --team N --name X` | grava o nome em todas as cópias e varre o disco atrás do que sobrou |
| `python3 tools/pes2/player_map.py <track1.bin> --check` | relaciona as duas tabelas de nome de jogador |
| `python3 tools/pes2/strings_inventory.py <track1.bin>` | varre o disco por texto, agrupado em blocos densos |
| `python3 tools/pes2/ofs_map.py <we2002.bin> --pes2 <track1.bin>` | os 69 `OFS_*` como `(arquivo, offset relativo)` |
| `python3 tools/pes2/lzss.py <track1.bin> --check` | o codec LZSS dos `BIN/*.BIN`; aceita vários discos e soma |
| `python3 tools/pes2/bin_archive.py ls\|export\|check <track1.bin>` | o índice do contêiner: imagens, CLUTs e PNG |
| `python3 tools/pes2/lang_map.py <track1.bin> --check` | os conjuntos de cópia de asset, agrupados por conteúdo |
| `python3 tools/pes2/tname.py bands\|fontscan\|swap <track1.bin>` | os nomes rasterizados do `T_NAME`, e a busca que mostrou não haver fonte no disco |
| `python3 tools/pes2/asset_write.py save\|import\|palette\|negative\|check <copia.bin>` | grava asset editado, fit-or-fail; recusa `roms/` |
| `tools/pes2/asset_screen.sh` | quadros do boot no `:98`, para ver um asset editado na tela |
| `python3 tools/pes2/faq_check.py --image <track1.bin>` | confere `docs/PES2-NOMES.md` contra o disco |
| `tools/pes2/run_duckstation.sh` | sobe o jogo no `:98` sob a configuração do próprio DuckStation da máquina; `--kill` encerra |
| `python3 tools/pes2/drive.py <copia.cue> --screen title\|main-menu\|team-select\|edit` | dirige o emulador por rota nomeada e captura; espera pela assinatura do quadro, não pelo relógio. `--save-state` deixa um estado na tela alcançada, e as rotas o reusam — 2,5 min por tentativa viram ~40 s |
| `tools/pes2/boot_check.sh` | mede que ele botou — janela, quadro vivo, dois quadros diferentes |

No `ctest` são três alvos: **`pes2_selftest`**, que monta um disco
sintético de 24 setores e roda em qualquer lugar; **`pes2_image`**, que
precisa de `WE2002_PES2_IMAGE`; e **`pes2_boot`**, que precisa do
DuckStation e do `:98` e leva ~90 s. Os dois últimos se reportam *skipped*
sem o que precisam — mesma convenção do `WE2002_TEST_IMAGE` e dos golden,
e como eles não rodam em CI.

```sh
WE2002_PES2_IMAGE="roms/Pro Evolution Soccer 2 (Europe) (EsIt)/…(Track 1).bin" \
WE2002_PES2_IMAGE_B="roms/Pro Evolution Soccer 2 (Europe) (EnFrDe)/…(Track 1).bin" \
WE2002_PES2_CARD="$HOME/.local/share/duckstation/memcards/…(Es,It)_1.mcd" \
WE2002_PES2_TMPDIR=<~450 MiB livres> \
  ctest --test-dir build -R pes2
```

Quatro coisas que custam tempo se descobertas tarde:

- **O emulador é DuckStation, e não está no `PATH`** — é um AppImage em
  `~/Applications/`. O `run_duckstation.sh` **não configura nada**, por
  decisão de 2026-09-02: esta máquina roda DuckStation para este projeto,
  então a configuração dele é a que vale, e o `drive.py` **lê** os bindings
  de `[Pad1]` do arquivo em vigor em vez de declarar os seus. Remapear um
  botão na interface do emulador basta. Save state e cartão caem em
  `~/.local/share/duckstation` como em qualquer sessão dele.

  Isto dizia "usa um `XDG_DATA_HOME` isolado" até aquela data, e era
  **falso**: o AppImage resolve o diretório de dados pelo `$HOME`, então o
  `settings.ini` que o lançador escrevia nunca foi lido — doze subidas
  apertando teclas ligadas a nada. Detalhe nas armadilhas 14 e 20 da §6.11
  do [PLAN-PES2-PSX.md](docs/PLAN-PES2-PSX.md).
- **`roms/` tem os originais; PES2 grava in-place como o WE2002.** Copie a
  release inteira (571 MiB, as oito trilhas) para o scratchpad antes de
  apontar qualquer coisa que escreva.
- **"Cópia" de tabela não quer dizer mesma lista, e o conjunto de cópias não
  se declara.** São **oito** listas de nome de time — 106, 99, 95, 94, 123,
  32, 99 e 99 entradas —, e o índice 34 de uma é outro time no índice 34 da
  outra. Casar por índice grava no time errado, e o resultado parece plausível
  em tela. As três últimas só apareceram porque o `poke.py` varre o disco
  atrás do nome velho depois de gravar; gravar as cinco conhecidas deixava
  três telas com o nome antigo. §6.1 do plano.
- **A ordem de armazenamento é propriedade da tabela.** `SELECTC.BIN`
  guarda elenco de trás para frente; o executável de boot, de frente para
  trás. Quem assume uma inverte 23 jogadores por time na metade das
  tabelas, sem sintoma visível. §3.3 do plano.
- **`SELECTC.BIN` é pool deduplicado, o executável é ordenado por vaga.**
  Os dois guardam os mesmos 1.399 nomes; o executável repete 50 deles,
  porque jogador em dois elencos ocupa duas vagas. Ler o pool como se
  fosse lista de elenco desalinha tudo depois do primeiro nome repetido.
  §1.5 do plano.

**PES2 entrou no pool em 2026-09-01**, e o backlog dele é
[docs/tasks/progresso.md](docs/tasks/progresso.md) — 25 tasks nas seis fases do
plano, cada uma com `fonte_de_verdade` apontando para a seção que a mede. Até
essa data o projeto estava fora do pool *por escolha*, e o backlog era a §7 do
[docs/PES2-AJUSTES.md](docs/PES2-AJUSTES.md); aquela seção agora é registro
histórico. O que sobrou de aberto lá é um item só, e não é código: instalar
`numpy` e um desmontador MIPS, decisão do dono da máquina.

## Arquitetura

### Layout do repositório (pós-Fase 5)

```
src/core/            we2002_core — logica pura. ZERO Qt, ZERO API de plataforma.
  include/we2002/    API publica
src/app/             o executavel Qt: MainWindow + 5 dialogos
src/app/ui/          os 6 .ui gerados do ed.rc + controls.json
src/app/resources/   o icone (gerado por tools/make_icon.py) + app.qrc
tests/               65 checks + 2 golden tests + guardas dos geradores
tools/               geradores e ferramentas de verificacao
legacy/mfc/          o app MFC original — REFERENCIA, nao compila
data/                dados lidos em runtime
packaging/           .desktop + AppStream
docs/                PLAN-LINUX.md
.github/workflows/   CI: linux, linux-release, linux-ubsan, windows.
                     So roda por workflow_dispatch -- ver abaixo.
```

O `CMakeLists.txt` da raiz só adiciona `src/app` se achar o Qt6, então o core e
os testes ainda compilam numa máquina com apenas compilador e libcurl.

**Regra dura: `src/core/` não pode incluir Qt nem `windows.h` nem POSIX.** É o
que permite os golden tests da Fase 3 rodarem headless.

### App

Um arquivo por área do diálogo, todos métodos do mesmo `MainWindow`:
`MainWindow.cpp` (construção e ligação), `TeamView.cpp` (o ex-
`OnSelezioneSquadraV` e os killfocus de nome/barra/cobrador/número),
`TacticsView.cpp`, `Commands.cpp`, `SofifaView.cpp`. Mais os cinco diálogos:
`PlayerSelectDialog`, `PlayerSkillsDialog`, `FlagKitDialog`,
`DefaultTacticsDialog`, `EditOptionsDialog`.

As 376 famílias indexadas do original (`OnCarat1..23`, `OnSost1..23`,
`OnKillfocusNum1..23`, `OnKillfocusTatx2..11`, ...) viraram um método por
família recebendo o índice, ligado num laço sobre arrays de ponteiro
(`txt_player_[23]`, `cmb_role_[10]`, ...) resolvidos por nome de objeto.
**Ao mexer num handler, lembre que ele atende os 22 irmãos.**

A busca por nome passa por `Bind<T>()` ([src/app/Bind.hpp](src/app/Bind.hpp)),
não por `findChild` cru: nome que não casa com o formulário aborta na hora com
a mensagem certa, em vez de virar um ponteiro nulo que estoura três frames
adiante. `ctest -R glossary` pega o mesmo erro estaticamente.

Três diferenças de sinal entre Qt e MFC que valem saber antes de mexer:

- `setText` não dispara `editingFinished`, como `SetWindowText` não dispara
  `EN_KILLFOCUS`. Por isso os commits usam `editingFinished` sem flag de
  "estou carregando".
- `EN_CHANGE` **dispara** em `SetWindowText`, e é o que move os marcadores do
  campinho ao trocar de time. Os `TXT_TATX/TATY` usam `textChanged`, não
  `textEdited`. Não "otimize" isso.
- `QComboBox` não tem `killFocus`. Os combos de papel e de cobrador gravavam em
  `CBN_KILLFOCUS`; um `eventFilter` de `FocusOut` no `MainWindow` reproduz.
  E como `setCurrentIndex` **dispara** `currentIndexChanged` (`SetCurSel` não
  disparava `CBN_SELCHANGE`), as cargas de time usam `QSignalBlocker`.
- **`Escape` num combo aberto não significa o mesmo nos dois.** No MFC as setas
  movem o `CurSel` do próprio combo e o `Escape` só fecha a lista, então o
  killfocus grava o item navegado; no Qt as setas movem a linha corrente da
  *view* e o `Escape` desfaz. Um `eventFilter` do `MainWindow` intercepta o
  `Escape` no popup dos **dezesseis** combos que gravam em perda de foco — os
  seis de cobrador e os dez de papel — e repõe o índice navegado. Medido: três
  `Down` e `Escape` levam `kick_long_fk` de 3 a 6 e `raw_formation[0]` de
  `0x02` a `0x05`, nos dois lados. Os dez de papel enganam: o
  `currentIndexChanged` deles só repinta a legenda do marcador, e quem grava é
  o `FocusOut`, como nos seis.
- **E são vinte e seis combos, não dezesseis.** O `DefaultTacticsDialog` tem
  **outros dez** de papel (`CMB_SLOT_ROLE2..11`), que escrevem os `roles[]` dos
  presets e precisaram do **próprio** filtro. O caminho de gravação de lá é
  outro — `currentIndexChanged` guardado por `hasFocus()`, não `FocusOut` —, e
  isso muda o conserto: repor o índice com o combo já sem foco não grava nada,
  então o filtro chama `setFocus()` depois do `hidePopup()`. Ao mexer no filtro
  de um formulário, confira o outro (CORR-WTE-134).

Cuidado com `slots`: é macro do Qt. Uma variável local com esse nome não
compila, com erro que não menciona macro nenhuma.

**`PUSHBUTTON` do `.rc` sai com `autoDefault=false`.** Dentro de um `QDialog` o
Qt torna todo botão auto-default, e `Return` clicaria o primeiro da ordem de
tabulação — num diálogo com 86 botões e nenhum `DEFPUSHBUTTON`, uma ação
arbitrária, e um dos candidatos aplica formação predefinida sobre o time
selecionado. Quem decide isso é o `rc2ui.py`; só `DEFPUSHBUTTON` vira default,
que é o que o `.rc` quer dizer.

**Efeito colateral virou decisão:** no `ed.exe` o `Return` na janela principal
**encerra o editor** (`CDialog::OnOK`, via um `CanExit()` que devolve `TRUE`
sempre), e no port ele não faz nada. Medido em 2026-08-31 e mantido de
propósito — reproduzir faria uma tecla acidental descartar o não gravado. É
divergência deliberada registrada
([CORR-WTE-141](docs/tasks/concluidos/CORR-WTE-141.md)); não "conserte" isso.

**E `DEFPUSHBUTTON` invisível não vira nada.** O `IDOK` do
`DefaultTacticsDialog` é `NOT WS_VISIBLE` (`ed.rc:627`); no MFC ele continua
sendo o default e `Return` fecha o diálogo, no Qt um default invisível é
**pulado** — medido, `setDefault(true)` nele não muda nada. Como os dois lados
são modais, o diálogo ficava sem saída e a gravação inalcançável. Ele trata
`Return` no `keyPressEvent` e chama `accept()`; `Escape` segue com o `QDialog`.
Ao mexer num diálogo cujo botão de confirmação não aparece na tela, confira se
ele tem como ser confirmado.

### Código gerado — não editar à mão

`src/core/Database.cpp`, `Tables.cpp`, `include/we2002/Offsets.hpp`,
`Tables.hpp`, todo o `src/app/ui/` e os PNGs de `src/app/resources/` são
**gerados**. Para mudá-los, mexa no gerador e reexecute:

```sh
python3 tools/extract_legacy_data.py   # 69 offsets + 16 tabelas
python3 tools/port_database.py          # Load/Save/custo a partir do legacy
python3 tools/rc2ui.py                  # os 6 .ui + controls.json, do ed.rc
python3 tools/make_icon.py              # os 7 PNGs do ícone
```

O `make_icon.py` é a exceção do grupo: **não tem `--check`**. Os outros três
comparam com o commitado e falham no `ctest`; a saída do PIL não é
byte-determinística entre versões, e um guard que quebra o CI quando o Pillow
sobe é pior do que nenhum. Ao mexer no ícone, **olhe** o resultado — é a única
coisa gerada aqui que teste não julga.

`port_database.py` extrai `carica_dabin` e `OnWriteCD` verbatim do legacy e
aplica substituições listadas. Se algo que ele não reconhece sobrar, ele
**falha** em vez de emitir código quebrado. Dois guards:

- `FORBIDDEN` — recusa se sobrar construção MFC. Pegou dois erros na Fase 2.
- `check_seeks()` — conta seeks absolutos e relativos no legado e na saída e
  recusa se não baterem. Existe porque na Fase 3 uma regex com `[^,]`
  atravessou uma quebra de linha e **trocou** um `Seek(begin)` por um
  `SeekCurrent`. Compilava, passava nos testes e passava no ASan; só o
  `ed.exe` mostrou. Ao escrever regra nova em `SUBS`, lembre que `[^x]` casa
  `\n`.

### Core

- `Database` — o ex-estado global (`players[]`, `teams[]`, `ml_teams[]`,
  `preset_formations[]`) mais `Load()` (ex-`carica_dabin`) e `Save()`
  (ex-`OnWriteCD`).
- `CdImage` — substituto do `CFile`. Imita a semântica dele de propósito:
  ponteiro de arquivo único, leitura curta não é erro, e **sempre**
  `std::ios::binary`.
- `Offsets.hpp` — os 69 `OFS_*`.
- `SquadNumbers` (`Types.hpp`) — o ex-`struct NUMERI`. Bitfields agora são
  `std::uint32_t`, **não** `DWORD`: no Linux LP64 `DWORD` seria 64-bit e
  embaralharia todos os números de camisa.
- `Player` / `Team` / `MlTeam` / `Formation` — ex-`giocatore`/`squadra`/
  `squadra_ml`/`tattica`.
- `TextCodec` — `kanjitoascii`/`asciitokanji` portados verbatim, como
  `KanjiToAscii`/`AsciiToKanji`.

### Os formulários `.ui`

`src/app/ui/*.ui` sai do `ed.rc` por `tools/rc2ui.py`. Geometria **absoluta**,
sem layouts Qt: os 434 controles foram posicionados à mão em 2002 e a
fidelidade é o critério. DLU→px com as base units 6×13 do MS Sans Serif 8pt.

`ctest -R ui_forms` regenera em memória e compara com o commitado — editar um
`.ui` à mão falha ali.

`src/app/ui/controls.json` guarda o que o `.ui` não expressa: o símbolo de
recurso de origem (`id`), keyword `.rc`, estilo Win32 cru e geometria em DLU e
px. `ES_NUMBER` e `ES_UPPERCASE` são validadores, não propriedades de widget —
o app lê o JSON, não o `.rc`.

Três coisas a saber antes de mexer:

- **`COMBOBOX` no `.rc` guarda a altura do dropdown**, não a do controle. Os
  39 combos são desenhados com 12 DLU; a altura original fica no manifesto
  como `dropdown_dlu`. Levar o `.rc` ao pé da letra faz um combo de 104 px
  engolir o grupo atrás dele.
- **Nomes de controle passam pelo glossário** (`UI_CONTROLS`) desde a Fase
  5.5: `TXT_NSQUAD1` virou `TXT_TEAM_NAME1`, `CMD_CARAT1` virou `CMD_SKILLS1`.
  O símbolo original de cada controle continua no `controls.json` como `id`,
  então grepar contra `ed.rc`/`resource.h` ainda funciona. Só nomes italianos
  foram trocados — `CMB_WRITE` num botão, `IDOK`, `IDC_BUTTON1`, `LAB_BAR_1..5`
  e `CMD_TACT1..16` ficaram como o `.rc` escreveu.
- **MS Sans Serif não está instalada**, então o Qt substitui e alguns rótulos
  apertados cortam ("Position" vira "Positior"). O `ed.exe` sob Wine corta os
  mesmos, pelo mesmo motivo.

Para conferir visualmente:

```sh
cmake -B build-uipreview -S tools/uipreview
cmake --build build-uipreview -j
DISPLAY=:98 ./build-uipreview/preview_MainDialog /tmp/main.png
```

`QWidget::grab()` pinta fora da tela, então o diálogo de 1077 px sai inteiro
mesmo com o Xvfb em 960 — a captura do `ed.exe` não consegue isso. O
`uipreview` usa Qt6 se existir e cai para Qt5.

### Nomenclatura

Desde as Fases 3.5 (core) e 5.5 (UI) **não existe identificador em italiano
fora de `legacy/`** — membros, offsets, tabelas, locais, comentários e nomes de
objeto dos widgets foram traduzidos.

O mapa está em [tools/glossary.py](tools/glossary.py) e é a única fonte. São
dois dicionários, deliberadamente separados:

| | Conteúdo | Quem aplica |
|---|---|---|
| `IDENTIFIERS` | membros, locais, offsets, tabelas | `port_database.py`, `extract_legacy_data.py`, `apply_glossary.py` |
| `UI_CONTROLS` | nomes de objeto dos widgets | `rc2ui.py` |

`UI_CONTROLS` fica **fora** de `IDENTIFIERS` de propósito: `IDENTIFIERS` é
varrido sobre o código *legado* pelos dois geradores, e nome de controle não
tem o que fazer ali.

Para renomear qualquer coisa, mexa no glossário e rode:

```sh
python3 tools/apply_glossary.py          # fontes à mão
python3 tools/apply_glossary.py --check  # acusa italiano sobrando (= ctest -R glossary)
python3 tools/port_database.py           # Database.cpp
python3 tools/extract_legacy_data.py     # Offsets.hpp, Tables.*
python3 tools/rc2ui.py                   # os .ui e o controls.json
```

`--check` cobre core, `src/app/` e os arquivos gerados em `src/app/ui/`. Nos
`.ui` e no `controls.json` um nome velho significa que o `rc2ui.py` não foi
reexecutado, e a mensagem diz isso.

Rastreabilidade contra o legado: cada offset renomeado carrega o nome antigo
num comentário (`// was OFS_NOMI_SQ1`), cada handler renomeado idem
(`///< was caratteristiche()`), e cada controle guarda o símbolo do `.rc` no
`controls.json`. Grepar um nome nas duas árvores continua funcionando.

Duas correções de semântica saíram dessa fase:

- `nome_m` não é "long name" como a Fase 2 anotou. O `_m` é de *minuscolo*: é
  o nome do time em caixa mista ("Bayern" em vez de "BAYERN"). Virou
  `mixed_case_name`.
- `OFS_NOMI_PML1/2` não são nomes de jogador apesar do prefixo — são o 7º e o
  8º slot de nome de clube de ML. Viraram `OFS_ML_TEAM_NAME_7/8`.

Nomes invertidos herdados, agora corrigidos: o decodificador do original se
chamava `codifica_carat()` e o codificador `decodifica()`. São `Player::Decode()`
e `Player::Encode()`.

### Legacy

`legacy/mfc/` guarda o app MFC inteiro como referência. `edDlg.cpp` (8.456
linhas) tem a UI, os offsets, a codificação e o estado global misturados.
`ed.rc` são 6 diálogos e 434 controles, e continua em **ISO-8859-1** (14 × `°`
em labels) — deliberado: o consumidor dele é o conversor da Fase 4 (que declara
o encoding) e o `rc.exe` do MSVC, que quebraria com UTF-8 sem BOM.

### Formato da imagem: MODE2/2352 sector-aware

Setor PSX = 2352 bytes = 24 header + 2048 dados + 280 EDC/ECC. Os offsets
hardcoded **pulam os cabeçalhos de setor manualmente**:

```
OFS_TEAM_NAME_1     = 1012640  → setor 430, byte 1280 (dados = 24..2071)
OFS_TEAM_NAME_1_END = 1013431  → último byte de dados do setor 430
OFS_TEAM_NAME_1_A   = 1013736  → 1011360 + 2352 + 24 = 1º byte do setor 431
```

Os `if (i == 40) fil_ctrl.Seek(OFS_NOMI_SQ1A, ...)` (`edDlg.cpp:1665-1667`) são
exatamente esses saltos — no legado esses três ainda se chamam `OFS_NOMI_SQ1`,
`_F` e `1A`. Consequências:

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
- **Build Release não é o mesmo teste que Debug.** Com `-O2` a glibc liga
  `_FORTIFY_SOURCE`, que confere `strcpy` contra o tamanho do destino. Um dos
  198 estourava um byte em **toda** imagem aberta (`raw_formation[30]` recebendo
  30 bytes + terminador) e derrubava o editor com `*** buffer overflow
  detected ***` antes de qualquer coisa aparecer — invisível em Debug, e o ASan
  não roda nesta máquina. Ao mexer num desses `strcpy`, confira em Release:
  `ctest --preset release` (o `TestLoadUnterminatedFormation` roda o `Load`
  inteiro contra uma imagem esparsa sintética) e o job `linux-release` do CI.
- Nomes de identificadores em **italiano** (`giocatore` = jogador, `squadra` =
  time, `tattica` = tática, `bandiera` = bandeira, `maglia` = camisa,
  `carat`/`caratteristiche` = atributos, `sost`/`sostituzione` =
  substituição, `nomi` = nomes, `costi` = custos, `numeri` = números). Isso
  vale só para `legacy/`; o mapa completo para o port está em
  [tools/glossary.py](tools/glossary.py).
- Zero desenho GDI. O único `OnPaint` (`edDlg.cpp:1493`) só desenha o ícone
  quando minimizado. O "campo tático" move `CButton`s com `MoveWindow`.

## Convenções da documentação

Regras que valem para os markdowns ficam em `.claude/rules/`. Hoje há duas:

- [.claude/rules/tasks.md](.claude/rules/tasks.md)
  — **os prompts de `docs/prompts/` são agnósticos de projeto.** Eles leem os
  dois arquivos de progresso, abrem a task pelo link da linha dela, e medem
  contra o que o campo `fonte_de_verdade` do frontmatter dela apontar. Nunca
  codifique num prompt o nome de um plano, um prefixo de ID, uma fase ou um
  mapeamento `ID → arquivo` — este repositório tem dois projetos no mesmo
  `progresso.md` e terá outros. `ctest -R tasks` (`tools/check_tasks.py`)
  confere as quatro convenções que fazem isso funcionar.
- [.claude/rules/links.md](.claude/rules/links.md)
  — link de um markdown de `docs/` para outro markdown dentro de `docs/` usa
  `/docs/` + o caminho do arquivo, nunca caminho relativo. Alvo fora de `docs/`
  (`../NOTICE.md`, `../CLAUDE.md`) continua relativo.

**Projeto encerrado é arquivado em `docs/tasks/concluidos/`.** Em 2026-09-01 as
195 tasks, `CORR-*.md` e os dois arquivos de progresso do ciclo `WTE-TASK` +
`PAR-TASK` desceram para lá, e `docs/tasks/` ficou só com
`progresso.template.md` e `correcoes-progresso.template.md` — a base do próximo
ciclo. Três coisas que decorrem disso, e que já custaram conserto na mudança:

- **A pasta é um conjunto fechado.** Task e progresso viajam juntos, porque o
  `check_tasks.py` confere cada task contra o `progresso.md` que mora **ao lado
  dela** — ele varre `docs/tasks/` e cada subpasta que tenha progresso próprio.
- **Os prompts continuam apontando para `docs/tasks/progresso.md`**, o vivo, que
  a próxima leva cria do template. Prompt que aponta para o arquivo executa
  task já feita.
- **Os `CORR-*.md` são cheios de transcrição** — saída de `grep`, de `git show`,
  fonte de gerador — e ali `docs/tasks/…` dentro de **bloco de código ou entre
  crases** é **evidência do que um arquivo dizia**, não link. Reescrever é
  falsificar a evidência. A varredura da mudança pulou as duas formas de
  propósito, e a versão ingênua tropeçou nas duas antes disso: sete
  transcrições em bloco e duas entre crases.

## Estado do repositório

Fases 1 (higiene), 2 (core portável), 3 (golden tests), 3.5 (nomenclatura do
core), 4 (`.rc` → `.ui`), 5 (handlers), 5.5 (nomenclatura da UI), 6
(acabamento) e 7 (Windows) concluídas. Ver
[docs/PLAN-LINUX.md](docs/PLAN-LINUX.md) para o estado por fase e
[docs/PLAN-WINDOWS.md](docs/PLAN-WINDOWS.md) seção 11 para o registro da 7.

O inventário de funcionalidade — cada comportamento do original, onde ele foi
parar no port, que evidência sustenta cada um e o roteiro do que ainda falta
clicar na tela — está em
[docs/PARIDADE-FUNCIONAL.md](docs/PARIDADE-FUNCIONAL.md).

**O import do SoFIFA está desligado** desde 2026-08-05, por decisão: fica em
último plano até a paridade com o `ed.exe` estar conferida tela a tela. O código
continua compilado e linkado; só ficou inalcançável pela janela. O interruptor é
`app::SOFIFA_ENABLED` em [src/app/Features.hpp](src/app/Features.hpp), e ele
apaga (em cinza, não escondido) os três botões de SoFIFA, o botão de edit
options, as 23 caixas de URL, o `CMD_READ_URL` do diálogo de atributos e a
leitura dos dois arquivos de regras no startup. Nada disso toca a imagem.

**O que não pode ser desligado junto: o `<imagem>_url.txt`.** O `OnWriteCD`
original grava esse sidecar (`legacy/mfc/edDlg.cpp:6207`) e o `Database::Save()`
gerado herda isso, montando o arquivo a partir de `players[].url`. Por isso o
`LoadUrls()` roda mesmo com o SoFIFA desligado — sem ele a gravação truncaria o
arquivo do usuário para 1.911 linhas em branco. Detalhe na §1.1 do
`docs/PARIDADE-FUNCIONAL.md`.

**O escopo Linux está fechado.** O port está verificado contra o `ed.exe` nos
dois níveis: o core headless (teste `golden`) e a janela Qt dirigida por
`xdotool` (teste `golden_gui`). Nas imagens European Deluxe e japonesa,
gravação limpa ou com edição pela tela, a saída é byte-idêntica à do original
salvo a faixa de 16 bytes já descrita.

Formato de pacote (AppImage/Flatpak) foi **decidido ficar de fora** por
enquanto: só as regras de `install()`.

**O CI não roda sozinho.** Os gatilhos `push` e `pull_request` do
[.github/workflows/ci.yml](.github/workflows/ci.yml) estão desligados **por
decisão**, não por descuido: enquanto o projeto está sendo construído, runner
queimando minuto a cada commit não diz nada que o build local não diga antes, e
não diz o que importa — contra o `ed.exe` nenhum runner roda. Sobrou o
`workflow_dispatch`, então a matriz inteira roda à mão pela aba Actions.
Religar é descomentar as quatro linhas no cabeçalho do `ci.yml`, e isso é para
o **fim do projeto**. Não religue por conta própria.

**O Windows também está verificado.** O `.exe` do MSVC grava os mesmos bytes
que o do GCC nas duas imagens, e o confronto direto com o `Debug\ed.exe`
rodando nativo (sem Wine) dá a mesma faixa de 16 bytes e nada mais. Um item do
checklist ficou aberto — editar nome de time pela janela Qt e comparar com o
oráculo — porque a Citrix filtra input sintético e a UIA do Qt não expõe os
itens do combo de forma estável. Detalhe na seção 11 do
[docs/PLAN-WINDOWS.md](docs/PLAN-WINDOWS.md).

Quatro divergências deliberadas do original entraram na Fase 5 (preço do
jogador importado, o swap fora do array no ordenar-banco, gravar as URLs de
volta, e o teste único de "tem bandeira própria"). Estão listadas na seção da
Fase 5 do plano; nenhuma aparece nos golden tests.

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

**Há duas cópias do `defaultlook.txt`, e elas precisam bater.** O port lê
`data/defaultlook.txt`, versionado; o `ed.exe` abre `"defaultlook.txt"` com
**caminho relativo** (`edDlg.cpp`, no `OnEditAllPlayersLook`), e como o
`golden_run.sh` o executa de dentro de `Debug/`, quem ele lê é
`Debug/defaultlook.txt` — que é **gitignored** e sai de sincronia sem que nada
reclame.

Em 2026-09-01 as duas divergiam em 4 das 95 linhas, e o golden do
`CMB_EDITALLLOOK` acusava 92 bytes de diferença que **não eram de código**: os
dois lados liam arquivos diferentes e cada um gravava certo o que leu. O
versionado é o fiel — bate com o `defaultlook.txt` do commit raiz. Ao mexer em
qualquer coisa que leia esse arquivo, confira antes:

```sh
cmp Debug/defaultlook.txt data/defaultlook.txt
```

Detalhe na [CORR-WTE-133](docs/tasks/concluidos/CORR-WTE-133.md).

Arquivos `debugio*.txt` / `debugread*.txt` na raiz são dumps de depuração do
autor, não fixtures de teste.
