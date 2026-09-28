# Visualizador de aparência — o ambiente, no Windows e no Linux

O ciclo `looks` (`tools/looks/`) foi feito quase todo no Windows. Esta página
serve a duas coisas:

1. listar o que ele usa **fora** do repositório, e onde isso está em cada
   máquina;
2. dizer o que falta fazer para rodá-lo no Linux, em
   `/home/ingmar/desenvolvimento/github/new-we2002-editor`.

Tudo o que se afirma do Linux foi medido em 2026-09-28, a partir do Windows,
com a partição Linux montada só para leitura pelo WSL (`wsl --mount … --options
"ro,noload"`). Nada foi gravado lá. O que **não** foi medido está marcado como
tal.

Os caminhos saem do código (`tools/looks/`, `tools/pes2/fork.py`, `make.ps1`) e
dos docs do ciclo ([PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md), o
[perfil](/docs/prompts/perfil-looks.md) e as tasks de
[docs/tasks/looks/](/docs/tasks/looks/progresso.md)).

## O `C:\` do Windows, visto do Linux

O `C:\` desta máquina aparece no Linux em **`/media/ingmar/win/`**. É a linha do
`/etc/fstab` com `UUID=649806ED9806BE14`, montada por `ntfs-3g` com `uid=1000`.
Para achar pelo Linux qualquer arquivo abaixo, troque o `C:\` por esse prefixo e
as barras invertidas por barras:

| no Windows | no Linux |
|---|---|
| `C:\github\new-we2002-editor\work\looks-states\` | `/media/ingmar/win/github/new-we2002-editor/work/looks-states/` |
| `C:\games\ps1\work\we2002-english.cue` | `/media/ingmar/win/games/ps1/work/we2002-english.cue` |
| `C:\games\we2002\Superpackv6\` | `/media/ingmar/win/games/we2002/Superpackv6/` |

Isso vale para **dados** (discos, save states, medições, Superpack). Não vale
para **programas**: o `.exe` do DuckStation, o Python do Windows, o vcpkg e o
Git Bash não rodam no Linux, e lá cada um tem equivalente próprio (tabela
abaixo).

## Resumo: cada artefato, nas duas máquinas

| artefato | Windows | Linux, medido em 2026-09-28 |
|---|---|---|
| repositório | `C:\github\new-we2002-editor`, em `14e1ecf6`, igual ao `origin/main` | em `08cad58` (2026-09-14): **316 commits atrás**, 124 deles em `tools/looks/`; hoje só tem `layout.py` e `superpack_count.py` |
| disco japonês (`WE2002_LOOKS_IMAGE`) | `roms\japanese-shift-jis.bin` | `roms/japanese-shift-jis.bin`, **presente**, 307.187.664 B |
| disco inglês (`WE2002_LOOKS_DRIVE_IMAGE`) | `C:\games\ps1\work\we2002-english.cue`, cópia de `C:\games\ps1\roms\we2002\we2002-english\` | `roms/we2002-english/we2002-english.{bin,cue}`, **presente**, 306.834.864 B, o mesmo tamanho |
| fork do DuckStation com MCP | `C:\games\ps1\duckstation-mcp\`, portable, build `a2edf2d` | `~/Applications/duckstation-mcp/` (`bin/`, `lib/`, `plugins/`), build **`c55b8ee`**: outro build |
| dados do emulador | a pasta do próprio fork (`portable.txt`) | `~/.local/share/duckstation/`, com `EnableMCPServer = true`, `MCPServerPort = 2346` |
| BIOS | `…\duckstation-mcp\bios\`, 4 imagens | `~/.local/share/duckstation/bios/`, as **mesmas 4** (SHA-1 idênticos) |
| save states (cópia mestra) | `work\looks-states\SLPM-87056_{1,2}.sav` | **ausentes**: não existe `work/looks-states/` |
| medições do ciclo | `work\looks-{walk,camera,scenery,pose,stature}\` | **ausentes** |
| venv com PySide6 | `work\venv-looks\` (PySide6 6.11.2, Python 3.13.14) | **ausente** (só existe o `work/venv-mcr/`) |
| Python com Pillow | `C:\Users\ingcvs\AppData\Local\Programs\Python\Python313\`, Pillow 12.3.0 | mise 3.13.13 (`~/.local/share/mise/installs/python/3.13/`), **Pillow 12.3.0 já instalado** |
| build do `ctest` | um diretório fora do worktree, com vcpkg | `build/`, configurado com o Python do mise; **não lista** os alvos `looks_*` |
| display | janela estacionada em -32000 pelo `app.py` | `Xvfb`, `xdotool` e `import` em `/usr/bin` |
| alvo que abre a tela | `.\make.ps1 looks` | `make looks` / `looks-98` / `looks-venv` (passos 2 e 7) |
| Superpack v6 (`WE2002_LOOKS_CORPUS`) | `C:\games\we2002\Superpackv6\` | não está no `$HOME`; alcançável em `/media/ingmar/win/games/we2002/Superpackv6/` |
| gravação de tela do usuário | `Gravação de Tela 2026-09-17 130706.mp4`, pasta do usuário | não procurada; nenhum comando a lê |

## Rodar no Linux, passo a passo

Os comandos abaixo rodam **no Linux**, a partir da raiz do repositório.

### 1. Atualizar o repositório

```sh
cd ~/desenvolvimento/github/new-we2002-editor
git status --short        # estava limpo em 2026-09-28
git pull --ff-only
```

O `main` do Windows está publicado (`origin/main` = `14e1ecf6`), e o `08cad58`
do Linux é ancestral dele, então o pull é *fast-forward*.

### 2. Criar o venv da janela

```sh
make looks-venv
```

O alvo cria `work/venv-looks` com o `python3` do `PATH`, que no Linux é o
**mise** 3.13, o mesmo que o `build/CMakeCache.txt` fixou, e instala
`PySide6==6.11.2`, a versão que roda no Windows. Confira que a linha `>>
criando` que o alvo imprime mostra o 3.13 do mise, e não o `/usr/bin/python3`
(3.12). Não use `apt`: a armadilha do Python duplo do `CLAUDE.md` vale igual
para este venv. O núcleo e o `confront.py` usam o Python do mise, que já tem Pillow;
o venv serve só à janela.

### 3. Trazer do Windows as medições e os save states

Nada disto está no git. São seis pastas de `work/`, que o código **lê**:

| pasta | quem lê | o que é |
|---|---|---|
| `looks-states/` | `oracle.py` | as duas cópias mestras de save state; slot 1 goleiro, slot 2 jogador de linha |
| `looks-walk/` | `anime.py`, `app.py --frame`, `ui_check.py` | o ciclo da caminhada medido |
| `looks-camera/` | `scene.py`, `ui_check.py` | a câmera de cada linha |
| `looks-scenery/` | `scene.py`, `ui_check.py` | a mobília e os sprites da tela |
| `looks-pose/` | `anime.py`, `oracle.py --pose-lag` | as poses capturadas |
| `looks-stature/` | `oracle.py --stature` | a estatura medida |

```sh
W=/media/ingmar/win/github/new-we2002-editor/work
for d in looks-states looks-walk looks-camera looks-scenery looks-pose looks-stature; do
  cp -a "$W/$d" work/
done
sha1sum work/looks-states/*
# 4facca1aee9ea543bc9b7bc1b58934bb0b4470c8  SLPM-87056_1.sav
# 719bf3f214177e25b1b032baad07ba2e4c664a55  SLPM-87056_2.sav
```

As outras pastas `work/looks-*` do Windows são **saída** (`looks-shots`, 81
MB; `looks-confront`; `looks-corpus`; `looks-task20`) e não precisam ir. Todas
as seis acima podem ser refeitas no Linux pelo `oracle.py`; copiar poupa horas
de emulador.

### 4. Guardar o save state que já está no emulador do Linux

**Faça isto antes da primeira corrida que suba o emulador.** O
`oracle.restore_state` copia a cópia mestra para o slot do DuckStation **sem
backup**. No Linux o slot 1 já tem outro save state:
`~/.local/share/duckstation/savestates/SLPM-87056_1.sav`, com 1.558.617 bytes
e data de 2026-09-10. A cópia mestra tem 1.690.941 bytes, então ele seria
sobrescrito.

```sh
cp -a ~/.local/share/duckstation/savestates/SLPM-87056_1.sav \
      ~/.local/share/duckstation/savestates/SLPM-87056_1.sav.antes-looks
```

No Linux a pasta de dados é **uma só** para o fork e para o AppImage oficial,
porque o fork não roda em modo portable ali. Um save state do ciclo aparece
também no DuckStation de uso normal.

### 5. Apontar os discos

Pela regra do repositório, trabalhe sobre cópia:

```sh
mkdir -p work/looks-disc
cp roms/we2002-english/we2002-english.bin roms/we2002-english/we2002-english.cue work/looks-disc/
```

Com a cópia feita, as variáveis ficam assim:

```sh
export WE2002_LOOKS_IMAGE="$PWD/roms/japanese-shift-jis.bin"
export WE2002_LOOKS_DRIVE_IMAGE="$PWD/work/looks-disc/we2002-english.cue"
```

O `layout.py` confere o digest de todo arquivo que lê. Se o disco inglês do
Linux fosse outro patch, o `oracle.py` recusaria na hora. **Não medido:** o
digest do `roms/we2002-english/we2002-english.bin` do Linux contra a cópia do
Windows. Os tamanhos batem, e a guarda decide na primeira corrida. A outra
opção é apontar direto para `/media/ingmar/win/games/ps1/work/we2002-english.cue`,
a mesma cópia que o Windows usou, lida pelo NTFS.

### 6. O emulador, e a pergunta que ficou aberta

O fork do Linux tem as 17 ferramentas MCP que o `tools/looks/` chama: os nomes
estão no binário (`breakpoint`, `continue`, `dump_vram`, `frame_step`,
`get_gpu_state`, `get_gte_registers`, `get_status`, `load_state`, `pause`,
`press_button`, `read_memory`, `read_registers`, `read_vram_region`,
`take_screenshot`, `vram_watch`, `wait_for_pause`, `write_vram_region`).

**Não medido: se o build `c55b8ee` do Linux carrega os save states gravados
pelo `a2edf2d` do Windows.** Save state do DuckStation carrega a versão do
formato, e os dois são commits diferentes do fork. A primeira corrida responde
isso:

```sh
python3 tools/looks/oracle.py --check-live
```

Se o state for recusado, há dois caminhos:

- **Igualar o build.** `python3 tools/pes2/fork.py recipe` diz como obter o
  fork. O zip que roda no Windows é do CI do mesmo fork.
- **Refazer os states no Linux.** Leve o jogo à tela `LOOKS SET` nos slots 1 e
  2 e rode `oracle.py --adopt-states`. Aí **as seis pastas do passo 3 precisam
  ser remedidas** (`--walk`, `--camera`/`--closeups`, `--scenery --write`,
  `--pose`, `--stature`), porque elas descrevem aqueles states.

### 7. O display

No Linux a regra é o `:98`, e as ferramentas já a seguem: o `ui_check.py` fixa
`DISPLAY=:98`, e o `fork.py launch` usa `PES2_DISPLAY`, que também vale `:98`
por default. O servidor tem de estar de pé, sem `-auth`:

```sh
Xvfb :98 -screen 0 1280x1024x24 -nolisten tcp &
```

Para abrir a tela, o `Makefile` tem os equivalentes do `.\make.ps1 looks` do
Windows, com os parâmetros de lá virando variáveis:

```sh
make looks                              # a tela, na SUA sessão; STATE=2 é o default
make looks STATE=1                      # começando do goleiro
make looks TUPLE=A-I3-A-E-A FIGURE=1    # o visualizador de uma tupla só
make looks TUPLE=A-I3-A-E-A ARGS=--wireframe
make looks-98                           # o mesmo, no Xvfb
```

| `make.ps1` (Windows) | `Makefile` (Linux) |
|---|---|
| `-State 1\|2` | `STATE=1\|2` |
| `-Tuple A-I3-A-E-A` | `TUPLE=A-I3-A-E-A` |
| `-Figure 0\|1` | `FIGURE=0\|1` |
| `-LooksImage <bin>` | `LOOKS_IMAGE=<bin>` (default: `WE2002_LOOKS_IMAGE`, senão `roms/japanese-shift-jis.bin`) |
| o resto da linha | `ARGS=...` |

As recusas também são as mesmas: `FIGURE` sem `TUPLE`, ou uma opção só do
visualizador (`--wireframe`, `--no-shelf`, `--piece`, `--yaw`, `--pitch`,
`--size`) sem `TUPLE`, param com a explicação em vez de abrir outra coisa
calado.

### 8. O Superpack (opcional)

Só o `corpus.py` e o `looks.py --corpus` o usam, e os dois pulam com 77 sem
ele:

```sh
export WE2002_LOOKS_CORPUS="/media/ingmar/win/games/we2002/Superpackv6/We2002/MCR/We DB - polipoli/Faces"
```

### 9. Conferir, do mais barato ao mais caro

```sh
python3 tools/looks/selftest.py                   # sem nada; nunca pula
python3 tools/looks/cli.py check                  # precisa de WE2002_LOOKS_IMAGE
python3 tools/looks/ui_check.py                   # + venv, :98, as pastas do passo 3
python3 tools/looks/oracle.py --check-live        # + fork, states, disco inglês
cmake --preset debug && ctest --preset debug -N -R looks   # tem de listar os 4 alvos
```

O `build/` do Linux foi configurado antes de os alvos `looks_*` existirem, então
precisa do `cmake` de novo. Confira os **nomes** na saída do `ctest -N`, não o
código de saída: um `-R` que não casa nada sai 0.

## Os artefatos, um a um

### Os discos

O ciclo usa **dois discos, e cada um serve para uma coisa**
([PLAN-LOOKS-PY.md §1](/docs/PLAN-LOOKS-PY.md#1)):

- **O japonês** (SLPM-87056) é de onde sai **toda leitura**: geometria,
  textura, paleta, animação.
- **O inglês** é um patch de tradução de terceiro sobre a mesma release. É o
  disco que o emulador roda, e foi por ele que toda medição de RAM, VRAM, GPU e
  GTE foi feita: câmera, pose, caminhada, ritmo, kit, cenário, silhueta,
  `screen.json`. Nos discos japoneses os doze rótulos da `LOOKS SET` saem em
  japonês. **Nunca se lê textura nem paleta dele**: o `DAT2D.BIN` e o
  `SELECT8.BIN` diferem entre os dois discos, e o `layout.py` recusa o inglês
  por digest.

No Windows existem mais duas coisas nessa área:

- `C:\games\ps1\roms\we2002\we-2002-original-japao.bin`, o mesmo dump do
  `roms/japanese-shift-jis.bin` (`layout.IMAGE_DIGEST_JAPANESE`);
- a cópia de conferência `C:\games\ps1\work\we2002-japao.cue`.

Os `we2002-pt-br` / `we2002-ptbr` das duas máquinas **não** são usados pelo
ciclo.

### O emulador

O **fork `sadnescity/duckstation`, branch `mcp`**, é o único DuckStation com
servidor MCP. É ele que deixa o `oracle.py` e o `confront.py` pararem a CPU,
porem breakpoint e lerem RAM, VRAM e GTE. A licença é CC-BY-NC-ND-4.0: o fork
não se versiona nem se publica.

- **No Windows:** `C:\games\ps1\duckstation-mcp\`, o
  `duckstation-windows-x64-release.zip` do CI descompactado, com o
  `duckstation-qt-x64-ReleaseLTCG.exe`. Roda em modo portable: BIOS, cartões,
  `savestates\` e `settings.ini` ficam na própria pasta. O log das subidas vai
  para `C:\games\ps1\work\duckstation-fork.log`.
- **No Linux:** `~/Applications/duckstation-mcp/bin/duckstation-qt`, com as
  bibliotecas em `lib/` e `plugins/`, que o `fork.py` põe no `LD_LIBRARY_PATH`.
  Os dados ficam em `~/.local/share/duckstation/`, que o
  `oracle.emulator_states_dir` usa.

O `load_state` do fork recebe **número de slot, não caminho**. Por isso o
`oracle.py` copia a cópia mestra de `work/looks-states/` para
`SLPM-87056_{1,2}.sav` no diretório do emulador antes de cada corrida (passo 4).

### A BIOS, que aqui é dado

As duas máquinas têm as mesmas quatro imagens: `scph1001`, `scph5500`,
`scph5501` e `scph7502`, com SHA-1 idênticos. A configuração é `SearchDirectory
= bios` e `Region = Auto`.

A BIOS não serve só para ligar o console. A
[LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md) mediu que o texto da
caixa de ajuda **vem da ROM do console**: uma chamada de BIOS por caractere
(vetor `0xB0`, função `0x51`) devolve um bitmap 16×15. Por isso a janela
escreve a ajuda numa fonte de apoio (§10.3 (o) do plano).

**Não medido:** qual das quatro o fork carrega. O disco é NTSC-J, e com `Region
= Auto` a candidata natural é a `scph5500.bin`, mas nenhum log registra isso.

### Material de terceiros

Nada disto entra no git ([PLAN-LOOKS-PY.md §2](/docs/PLAN-LOOKS-PY.md#2) e a
seção *"Lineage of the appearance viewer"* do [NOTICE.md](../NOTICE.md)).

- **Superpack v6**: coletânea da cena de modding, sem licença. A raiz tem
  31.790 arquivos e 4.830.420.054 bytes, medidos pelo
  `tools/looks/superpack_count.py`. O ciclo usou duas coisas dele:
  - **o corpus de 50 JPGs** em `We2002\MCR\We DB - polipoli\Faces\`, cujos
    nomes são tuplas de aparência (`looks.py --corpus`, `corpus.py`);
  - **o fonte MFC `en_we2000edit`** (Haplo e polipoli) em `We2002\MCR\We2002
    edit - Haplo y polipoli\`, terceira testemunha do unpack de 12 bytes (§1.9
    do plano). Serviu só como testemunha; nenhum código foi copiado.
- **`Darkensses/we3d`** (<https://github.com/Darkensses/we3d>, MIT): foi lido
  no GitHub como conferência cruzada do `MODEL.BIN`. Não há clone local.

### A gravação de tela

`Gravação de Tela 2026-09-17 130706.mp4`, na pasta do usuário, é a referência
visual do pedido da v2 (§10.1 do plano). **Nenhum número foi tirado dela.** O
ritmo da caminhada saiu do `oracle.py --rhythm`, porque um gravador tem
cadência própria (`layout.FRAME_TICKS`).

### Ferramentas do Windows sem papel no Linux

- **O Git Bash** exige `MSYS_NO_PATHCONV=1` nas ferramentas de `tools/pes2/`
  que recebem caminho de dentro do ISO. O `sh` do Linux não converte nada.
- **O vcpkg e o build fora do worktree** existiam porque, no Windows, nenhum
  build dentro da árvore listava os alvos `looks_*`. No Linux, o `build/` com o
  preset basta.
- **O estacionamento em -32000** (`oracle.py` e `app.py`, por `ctypes` +
  `user32`) só roda no Windows; no Linux o papel é do `:98`.
