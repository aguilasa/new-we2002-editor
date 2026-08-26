# `wte/` — **WE2002 - Lazarus Editor**

Reimplementação do **WE2002 Team Editor v0.99** do Obocaman (C++Builder 6,
Win32) como aplicação **Lazarus/LCL nativa no Linux**, com paridade verificada
byte a byte contra o binário original.

> **O produto se chama `WE2002 - Lazarus Editor`; o original continua sendo
> `WE2002 Team Editor`.** Os dois nomes aparecem nesta página o tempo todo e
> não são intercambiáveis — um é o que se escreve, o outro é o que se mede.
> A decisão e a razão estão na WTE-TASK-38, resumidas
> [abaixo](#3-o-produto-se-chama-we2002---lazarus-editor).

- **Plano:** [`../docs/PLAN-WTE-LAZARUS.md`](../docs/PLAN-WTE-LAZARUS.md) — a
  fonte de verdade
- **Andamento:** [`../docs/tasks/progresso.md`](../docs/tasks/progresso.md)
- **Achados da engenharia reversa:** [`re/`](re/)
- **Ambiente medido:** [`re/ambiente.md`](re/ambiente.md)

> ## Projeto **separado** do `newWe2002`
>
> Apesar de morar no mesmo repositório, este diretório **não faz parte do build
> do `newWe2002`**: não é `add_subdirectory`, não aparece no `CMakeLists.txt` da
> raiz, não tem alvo no `Makefile` da raiz. São dois produtos, com dois ciclos
> de verificação.
>
> O que os dois compartilham é **conhecimento de formato**: `Offsets.hpp`,
> `Tables.cpp` e o `we2002_core` inteiro, que é a *entrada* do transpilador da
> fase 3 — nunca o alvo dele.

## Compilar e rodar

```sh
make -C wte build     # lazbuild wte.lpi -> wte/build/wte
make -C wte assets    # symlink para a pasta do Obocaman (uma vez)
make -C wte run-98    # roda no Xvfb :98
make -C wte check     # --check de todos os geradores de tools/
make -C wte icon      # redesenha os 7 PNG do ícone (sem --check -- olhe)
make -C wte install PREFIX=~/.local    # instala; aceita DESTDIR
make -C wte           # lista os alvos
```

Sem `make`, direto:

```sh
lazbuild wte/wte.lpi
./wte/build/wte
```

> **Cuidado com os dois `wte`.** `make wte` **na raiz** abre o binário do
> Obocaman sob Wine — o oráculo A, que continua existindo e não mudou. Este
> projeto é `make -C wte <alvo>`. Nomes parecidos, coisas opostas: um é o
> original que estamos medindo, o outro é o que estamos escrevendo.

**Toda execução com GUI acontece no `DISPLAY=:98`** — o `:1` é a sessão real do
usuário. O `run-98` resolve o `XAUTHORITY` do Xvfb sozinho; à mão é preciso
fazer o que o [`../CLAUDE.md`](../CLAUDE.md) descreve, ou o GTK morre com
`Invalid MIT-MAGIC-COOKIE-1 key`.

### No Windows

O `Makefile` é GNU make + bash, e nenhum dos dois vem com o Windows. Lá o
equivalente é o [`make.ps1`](make.ps1), com os mesmos alvos menos os três que
não fazem sentido (`assets`, `run-98`, `install`):

```powershell
cd wte
.\make.ps1              # lista os alvos e o ambiente achado
.\make.ps1 build
.\make.ps1 run -Imagem C:\caminho\copia.bin
```

**Leia [`../docs/PLAN-WTE-WINDOWS.md`](../docs/PLAN-WTE-WINDOWS.md) antes**: ele
traz o que instalar, o que precisa estar no disco (a pasta do Obocaman
**inteira**, não só o `.exe`), os onze consertos que a porta exigiu e o que
está medido lá.

O resumo do que o Windows pode e não pode afirmar:

- **pode** — a camada de dados. `compare_dumps.py --medir` roda ali, e deu
  **zero divergência** nas duas ROMs, nas duas metades (66.498 linhas de dump
  idênticas, round-trip Pascal × C++ byte a byte). Mais 884 testes de
  ferramenta e 43 dos 45 geradores;
- **não pode** — a bateria golden, que depende de Xvfb no `:98`, `xdotool` e
  Wine. **A paridade byte a byte contra o `wte.exe` continua sendo afirmada
  pela máquina Linux.**

## Layout

```text
wte/
  wte.lpi, wte.lpr    projeto e programa
  src/                unidades Pascal (.pas)
  forms/              os formulários (.lfm)
  assets/             symlink para ../we-team-editor/ -- NAO versionado
  re/                 produto da engenharia reversa -- VERSIONADO
    dfm/  spec/  ambiente.md
  tools/              geradores e scripts de golden test
  tests/              testes do lado Pascal
  packaging/          .desktop, AppStream e os 7 PNG do ícone -- VERSIONADO
  build/              saída do lazbuild -- ignorada
```

---

## As três decisões da WTE-TASK-02

### 1. `assets/` é symlink de conveniência; quem manda é a resolução em runtime

A pasta `we-team-editor/` **é gitignored** — binário sem fonte e sem licença,
198 bitmaps, `dat.bin`. Um symlink versionado apontando para ela daria um link
quebrado em qualquer clone, então `wte/assets` também é ignorado e nasce de
`make -C wte assets`.

Isso resolve o **desenvolvimento**. Para o binário instalado a decisão é herdar
a ideia do `newWe2002` ([`../src/app/DataFiles.cpp`](../src/app/DataFiles.cpp)):
**resolver em runtime, relativo ao executável**, nunca por caminho absoluto
compilado. Ordem de busca acordada, na mesma forma do irmão:

1. `$WTE_ASSETS_DIR`
2. ao lado do executável
3. o prefixo instalado (`../share/<nome>/`)
4. a árvore de fonte (este `wte/assets`)

A implementação Pascal disso é da **WTE-TASK-39** (`datafiles.pas`), junto com o
empacotamento — antes disso não há prefixo instalado para procurar. O que a
fase 0 fixa é a **ordem**, para que nenhuma fase intermediária compile um
caminho absoluto e crie trabalho de desfazer.

O alvo `assets` **conta o que alcançou** em vez de dizer "ok": 198 bitmaps e o
`data/dat.bin`. Se a pasta faltar, ele falha dizendo o que colocar onde.

> **São 198.** A §1 do plano já registra 198 — a WTE-TASK-08 mediu o inventário
> e a WTE-TASK-09 reconciliou. O "197" que circulava era **erro de soma na
> prosa** da §1.8, que lista `53 + 105 + 32 + 7 + 1` e escrevia 197; o
> `image/careto_base.bmp`, solto na raiz de `image/` em vez de num dos quatro
> subdiretórios (`banderas`, `barba`, `pelo`, `uniformes2d`), sempre esteve
> contado. Ver [`re/assets.md`](re/assets.md) e [`re/fase-1.md`](re/fase-1.md).

### 2. O `--check` mora num `Makefile` próprio, em `wte/`

Três rotas estavam abertas: `ctest` (não existe aqui — não há CMake), um alvo
novo no `Makefile` da raiz, ou coisa própria em `wte/`.

**Escolhido: `wte/Makefile` autônomo.** A razão é a mesma que separa os dois
projetos: um alvo na raiz faria o ciclo de verificação do `newWe2002` e o deste
compartilharem entrada, e o critério da WTE-TASK-02 é explícito em que nada de
`wte/` seja referenciado pelo build do `newWe2002`. O `Makefile` da raiz não foi
tocado.

`make -C wte check` roda `--check` em cada `tools/*.py`, enumerado por
`wildcard` — gerador novo entra na bateria sem editar o Makefile. Enquanto não
houver gerador nenhum, o alvo **diz que nada foi medido** em vez de sair verde:
alvo verde sem medição é pior do que alvo ausente.

A exceção é `tools/test_*.py`: teste de ferramenta não é gerador e não aceita
`--check`, então o `wildcard` o filtra. Esses rodam pelo alvo `test`, do qual
`check` depende — o comando a decorar continua sendo um só.

### 3. O produto se chama **WE2002 - Lazarus Editor**

*(Esta seção nasceu como "o binário se chama `wte` — provisoriamente". A
WTE-TASK-38 decidiu, em 2026-08-25.)*

O nome veio do usuário, e a alusão é deliberada: **Lázaro** ressuscita, e é o
que este projeto faz com um editor de 2002 que só rodava sob Win32.

**A separação produto/formato é herdada do `newWe2002`**, onde `newWe2002` é o
produto e `we2002` é o formato. Aqui vale a mesma regra, e ela decide sozinha
onde cada nome entra:

| Papel | Nome | Onde aparece |
|---|---|---|
| **Produto** — o que o humano lê | `WE2002 - Lazarus Editor` | `Application.Title`, `Name=` do `.desktop`, `<name>` do AppStream, título desta página |
| **Slug** — o que o sistema de arquivos lê | `we2002Lazarus` | binário, `share/<slug>/`, ícone, `StartupWMClass`, `share/doc/<slug>/` |
| **AppID** | `io.github.aguilasa.we2002Lazarus` | AppStream e o nome dos dois arquivos de `packaging/` |
| **Formato** — o que o código lê | `we2002` | as unidades `we2002_*.pas`, os identificadores, as variáveis `WTE_*` |

O slug é camelCase porque o irmão é: `newWe2002` já ocupa `bin/`, `share/` e o
appid neste repositório com essa forma, e um segundo produto com outra
convenção obrigaria quem empacota a lembrar de qual é qual. AppID não leva
hífen — a forma reversa de DNS não os aceita —, e é por isso que o slug não é
`we2002-lazarus`.

**O `Caption` dos 18 formulários NÃO recebe o nome do produto.** Ali o critério
é fidelidade de tela: o `Caption` vem do DFM e ganha o sufixo ` [Lazarus]`, que
é o que separa os dois lados no mesmo `:98` — e é
[divergência registrada](re/divergencias.md). Trocar isso quebraria os **27
roteiros** do lado port de uma vez, e não compraria nada: quem mostra o nome do
programa é a barra de tarefas, que lê o `Application.Title`.

**O que já mudou:** `Application.Title` e o `<Title>` do `wte.lpi`, que diziam
`WE2002 Team Editor (Lazarus)` — tirando o parêntese, o nome do Obocaman letra
por letra, que é exatamente o que a §2 do plano proíbe.

**O que a [WTE-TASK-39](../docs/tasks/39-empacotamento.md) fez, e o que ela
decidiu não fazer.** O `packaging/` existe — `.desktop`, AppStream e os sete
PNG do ícone —, e o `install` põe 13 arquivos num prefixo. A renomeação de
`wte.lpi`/`wte.lpr`/`build/wte` para o slug **não aconteceu**, por decisão: a
razão está na seção *"O binário se chama `wte` na árvore e `we2002Lazarus`
instalado"*, mais abaixo. Este parágrafo dizia que ela faltava até 2026-08-26
([CORR-WTE-118](../docs/tasks/CORR-WTE-118.md)), contradizendo aquela seção
neste mesmo arquivo.

---

## Instalação (WTE-TASK-39)

`make -C wte install PREFIX=<prefixo>` põe a árvore no lugar, no mesmo formato
que o `newWe2002` instala pelo CMake:

| Item | Destino |
|---|---|
| binário | `bin/we2002Lazarus` |
| onde os assets são procurados | `share/we2002Lazarus/` (com um `README.txt` dizendo o que pôr ali) |
| `.desktop` | `share/applications/io.github.aguilasa.we2002Lazarus.desktop` |
| ícone, 7 tamanhos | `share/icons/hicolor/<n>x<n>/apps/we2002Lazarus.png` |
| AppStream | `share/metainfo/io.github.aguilasa.we2002Lazarus.metainfo.xml` |
| documentação | `share/doc/we2002Lazarus/{NOTICE.md,README.md}` |

**Nenhum caminho é compilado no binário.** A ordem de busca vive no
[`src/wte_datafiles.pas`](src/wte_datafiles.pas) e é a mesma para assets e para
o log de trace: variável de ambiente, ao lado do executável, o prefixo
instalado, a árvore de fonte. Medido em 2026-08-26: a árvore instalada foi
**movida de diretório** e o app abriu, achou os assets no novo lugar e carregou
um time da imagem — as mensagens que ele imprime trazem o caminho novo.

### O binário se chama `wte` na árvore e `we2002Lazarus` instalado

O repasse da WTE-TASK-38 previa renomear `wte.lpi`, `wte.lpr` e `build/wte`
para o slug. **Não foi feito, e a razão é de custo:** o nome `wte` aparece em 3
ferramentas, no `LPI`/`BIN` do `Makefile` e em prosa de `docs/`, e **nenhum
desses leitores é o usuário**. Quem vê o nome do produto é a barra de tarefas
(`Application.Title`), o `.desktop` e o `bin/` instalado. A renomeação
acontece no `install`, que é onde ela tem consumidor; o harness golden não muda
de forma por causa de nome.

### O que **não** é instalado, e não é esquecimento

Os 198 `.bmp` e o `data/dat.bin` do editor do Obocaman. Eles não são
redistribuídos (WTE-TASK-38), e é por isso que `share/we2002Lazarus/` nasce com
um `README.txt` em vez de vazio. Sem eles o app **abre e avisa** — a mensagem
diz o que falta e em quais três diretórios ele procura, com os caminhos já
resolvidos. Ela sai em três lugares porque tem três leitores: o rótulo da
janela, a saída de erro e um diálogo.

## Armadilha já paga: o `.lfm` em `forms/`

`{$R *.lfm}` **não respeita o include path.** O FPC expande o curinga para o
nome da unidade e procura o arquivo **no diretório do `.pas`**, e só ali. Com
`src/` para código e `forms/` para formulário — que é o layout que o plano pede
— isso falha com:

```
WteMain.pas(33) Error: (9031) Can't open resource file ".../wte/src/WteMain.lfm"
```

mesmo com `forms/` em `IncludeFiles`. A saída é o caminho explícito:

```pascal
{$R ../forms/WteMain.lfm}
```

**O `dfm2lfm.py` da WTE-TASK-10 tem de emitir essa linha nos 18 esqueletos.**

## O que este projeto pode afirmar

*(Produto da [WTE-TASK-40](../docs/tasks/40-verificacao-final.md), 2026-08-26.
As três condições da definição de pronto estão medidas na §11 do
[plano](../docs/PLAN-WTE-LAZARUS.md).)*

A frase, para reusar:

> **Verificado byte a byte contra o `wte.exe` nas operações que a bateria
> cobre, na ROM japonesa; e toda divergência conhecida está escrita.**

"Verificado" não é "correto", e o vocabulário abaixo é o mesmo que o
`newWe2002` usa. As três palavras não se substituem.

### Verificado

- **Os 96 handlers publicados têm veredito escrito** — 69 `implementado`, 19
  `trivial`, 6 `divergencia deliberada`, 2 `nao portado` (os dois com
  justificativa), **0 `aberto`**. Régua: `spec_index.py --check`.
- **As 24 operações da bateria golden gravam byte a byte o mesmo que o
  original, na ROM japonesa** — 96 corridas em 2026-08-26, `controle` antes de
  cada `golden`, **0 `REPROVOU`**. Régua: [`re/golden.md`](re/golden.md).
- **Os 17 handlers que gravam na imagem têm gate nomeado**, um a um. Régua:
  [`re/fase-4.md`](re/fase-4.md), seção *"Quem grava na imagem"*.
- **A camada de dados lê e grava o que o `we2002_core` lê e grava** — dumps
  Pascal × C++ com **0** bytes de diferença, nas **duas** ROMs. Régua:
  [`re/fase-3.md`](re/fase-3.md).
- **O app roda nativo, sem Wine e sem 32 bits** — sete medidas, sobre a árvore
  *instalada*, num namespace onde o Wine desta máquina está coberto. Régua:
  [`re/nativo.md`](re/nativo.md).

### Não verificado

- **A ROM European Deluxe, fora do arranque.** O oráculo morre com `c0000005`
  ao trocar de time ([`re/crash-causa.md`](re/crash-causa.md)), então 23 dos 24
  roteiros saem `SEM_ORACULO` ali. Não é falha do port: é ausência de régua. O
  port roda nessa ROM; o que falta é com o que comparar.
- **Qualquer ROM que não seja essas duas.** Nada foi medido fora de `roms/`.
- **Operação fora dos 24 roteiros**, e **combinação de edições** que nenhum
  roteiro faz. A bateria cobre o que ela cobre; o eixo é operação × ROM, não
  todas as sequências possíveis.
- **Ramo de handler que o gate não exercita.** O
  [`cobertura_gate.py`](tools/cobertura_gate.py) guarda a *contagem* de
  disparos justamente por isso — o `mostrar_jugadorClick` entra pelo botão do
  titular, e o ramo do reserva segue sem régua.
- **Outra distribuição, outra versão de GTK2, ou Wayland.** A condição 3 foi
  medida nesta máquina, com X.

### Divergente por decisão

São **12**, cada uma com natureza, decisão, razão e evidência em
[`re/divergencias.md`](re/divergencias.md) — da mais visível (o sufixo
` [Lazarus]` no `Caption`, sem o qual o harness dirigiria o lado errado) à mais
sutil (o preço do 23º jogador, que o original nunca grava). O
[`check_divergencias.py`](tools/check_divergencias.py), que o
`make -C wte check` roda, casa **exceção nomeada em ferramenta** com **entrada
no registro**, nos dois sentidos: exceção sem entrada aborta, e entrada cuja
exceção sumiu também.

Neste projeto **"100%" quer dizer toda divergência conhecida e escrita**, não
zero divergência — e a política difere da do `newWe2002` de propósito: lá o
objetivo era clonar o `ed.exe` inclusive nos defeitos.

### O que ficou aberto, e por quê

Cinco itens, nenhum deles escondido:

1. **O `ficha_enlaza` não tem chamador no port.** A rota que o alcança é o
   `MainForm.mostrar_jugadorClick` para jogador de clube de Master League, e
   *qual condição faz o modal abrir* ficou por medir na
   [WTE-TASK-30](../docs/tasks/30-handlers-auxiliares.md). **Não** é
   divergência deliberada — é trabalho não feito, e o dono é aquela spec.
2. **A European Deluxe sem oráculo.** Fechar isso exigiria consertar um bug do
   `wte.exe` — escrita além do fim de tabela — dentro do binário do Obocaman,
   que é leitura pura neste projeto.
3. **Sem formato de pacote** (AppImage/Flatpak). Decisão da
   [WTE-TASK-39](../docs/tasks/39-empacotamento.md), confirmada pelo usuário:
   o uso é pessoal, e as regras de `install` bastam.
4. **`wte.lpi`/`wte.lpr`/`build/wte` continuam com o nome `wte` na árvore.** O
   slug entra no `install`, que é onde ele tem consumidor — a seção acima
   explica o custo.
5. **Os assets do Obocaman não são redistribuídos**, então a árvore instalada
   não roda sozinha: quem recebe o app precisa da pasta do editor original. O
   app abre e avisa, com os três caminhos resolvidos.

## Estado

**Concluído.** As sete fases estão fechadas — 40 tasks e 117 correções, entre
2026-08-05 e 2026-08-26 —, e as três condições da definição de pronto estão
medidas em [§11 do plano](../docs/PLAN-WTE-LAZARUS.md).

O andamento por task, com data de commit, está em
[`../docs/tasks/progresso.md`](../docs/tasks/progresso.md) — este parágrafo é
resumo, e o índice é a fonte.

*(Ele dizia "Fase 0 ... um formulário vazio" até 2026-08-25, e o
`src/WteMain.pas` que ele mandava não investir já não existe: virou os 18
`ep2002_*.pas` na fase 2.)*
