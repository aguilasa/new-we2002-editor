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

## Compilar e testar

```sh
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build --output-on-failure
```

Os 61 checks unitários rodam sem imagem. Dois testes ficam mais fortes com
uma, e se reportam como *skipped* sem ela:

```sh
# unitários contra uma imagem real (só leitura, mas passe cópia mesmo assim)
WE2002_TEST_IMAGE=/caminho/copia.bin ./build/tests/we2002_tests

# golden test: ed.exe sob Wine vs o port, byte a byte
WE2002_GOLDEN_IMAGE=/caminho/imagem.bin ctest --test-dir build -R golden
```

### O golden test

`tools/golden_check.sh` é o teste de regressão que importa. Ele faz duas
cópias da imagem, passa uma pelo `ed.exe` sob Wine (`tools/golden_run.sh`) e a
outra pelo core (`tests/golden_tool.cpp`), e compara com
`tools/golden_compare.py`. Falha se aparecer **qualquer** divergência além de
uma faixa conhecida.

Essa faixa é `405724..405739` (`OFS_SQUAD_NUMBERS_NATIONAL+1008`): o slot 64
de um array de 63, que o original lê e grava por engano a partir da memória
vizinha (`ml_teams[0]`). O port preserva o que está na imagem em vez de
reproduzir comportamento indefinido. É a única divergência aceita — se
aparecer outra, é bug do port. Detalhe na Fase 3 do
[PLAN-LINUX.md](docs/PLAN-LINUX.md).

O script não toca na imagem de origem, mas usa ~950 MB de temporário. Precisa
do `Debug/ed.exe`, de Wine e do `:99`; por isso não roda em CI.

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
- O `ed.exe` abre um `CFileDialog` já no `OnInitDialog` e depois avisa que a
  imagem não tem 474.431.328 bytes. O aviso é só aviso — ele carrega assim
  mesmo. O diálogo principal **não tem título**, então só dá para achá-lo pelo
  tamanho; é o que o `wait_for_main` faz.
- O diálogo principal tem 1077 px de largura e o `:99` tem 960: o Wine corta a
  borda direita. O `CMB_WRITE` fica em x≈315, dentro da parte visível, então o
  golden test funciona mesmo cortado.

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

### Layout do repositório (pós-Fase 2)

```
src/core/            we2002_core — logica pura. ZERO Qt, ZERO API de plataforma.
  include/we2002/    API publica
tests/               61 checks, sem framework externo
tools/               os dois geradores (ver abaixo)
legacy/mfc/          o app MFC original — REFERENCIA, nao compila
data/                dados lidos em runtime
docs/                PLAN-LINUX.md
```

`src/app/` (a UI Qt) ainda não existe — chega nas Fases 4–5. O `CMakeLists.txt`
da raiz só adiciona `src/app` se o Qt6 for encontrado **e** o diretório
existir, então o core e os testes compilam numa máquina com apenas compilador
e libcurl.

**Regra dura: `src/core/` não pode incluir Qt nem `windows.h` nem POSIX.** É o
que permite os golden tests da Fase 3 rodarem headless.

### Código gerado — não editar à mão

`src/core/Database.cpp`, `Tables.cpp`, `include/we2002/Offsets.hpp` e
`Tables.hpp` são **gerados**. Para mudá-los, mexa no gerador e reexecute:

```sh
python3 tools/extract_legacy_data.py   # 69 offsets + 15 tabelas
python3 tools/port_database.py          # Load/Save/custo a partir do legacy
```

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

### Nomenclatura

Desde a Fase 3.5 **não existe identificador em italiano fora de `legacy/`** —
membros, offsets, tabelas, locais e comentários foram traduzidos.

O mapa está em [tools/glossary.py](tools/glossary.py) e é a única fonte:
`port_database.py` e `extract_legacy_data.py` o importam, e
`tools/apply_glossary.py` aplica o mesmo mapa nos fontes escritos à mão.
Para renomear qualquer coisa do core, mexa no glossário e rode:

```sh
python3 tools/apply_glossary.py          # fontes à mão
python3 tools/apply_glossary.py --check  # acusa italiano sobrando
python3 tools/port_database.py           # Database.cpp
python3 tools/extract_legacy_data.py     # Offsets.hpp, Tables.*
```

Rastreabilidade contra o legado: cada offset renomeado carrega o nome antigo
num comentário (`// was OFS_NOMI_SQ1`), então grepar um nome nas duas árvores
continua funcionando.

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
`ed.rc` são 6 diálogos e 393 controles, e continua em **ISO-8859-1** (14 × `°`
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
- Nomes de identificadores em **italiano** (`giocatore` = jogador, `squadra` =
  time, `tattica` = tática, `bandiera` = bandeira, `maglia` = camisa,
  `carat`/`caratteristiche` = atributos, `sost`/`sostituzione` =
  substituição, `nomi` = nomes, `costi` = custos, `numeri` = números). Isso
  vale só para `legacy/`; o mapa completo para o port está em
  [tools/glossary.py](tools/glossary.py).
- Zero desenho GDI. O único `OnPaint` (`edDlg.cpp:1493`) só desenha o ícone
  quando minimizado. O "campo tático" move `CButton`s com `MoveWindow`.

## Estado do repositório

Fases 1 (higiene), 2 (core portável), 3 (golden tests) e 3.5 (nomenclatura)
concluídas. Ver [docs/PLAN-LINUX.md](docs/PLAN-LINUX.md) para o estado por
fase.

O port está verificado contra o `ed.exe`: nas imagens European Deluxe e
japonesa, gravação limpa ou com edição pela GUI, a saída é byte-idêntica à do
original salvo a faixa de 16 bytes já descrita. A próxima fase é a **4**
(`.rc` → `.ui`), e ela ainda não foi autorizada.

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
