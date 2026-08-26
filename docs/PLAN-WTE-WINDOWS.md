# `wte/` no Windows — o **WE2002 - Lazarus Editor** fora do Linux

> Documento de **execução**, para ser seguido sentado na máquina Windows.
> O plano do projeto e todo o histórico das sete fases estão em
> [/docs/PLAN-WTE-LAZARUS.md](/docs/PLAN-WTE-LAZARUS.md); a árvore, as decisões
> e o vocabulário em [../wte/README.md](../wte/README.md). Este arquivo não
> repete nada dos dois.
>
> **Não confundir com [/docs/PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md)**, que é a
> fase 7 do `newWe2002` — outro produto, outro compilador (MSVC + Qt), outro
> ciclo de verificação. Os dois moram no mesmo repositório e não se tocam.
>
> Escrito em 2026-08-26, com o `wte/` fechado no commit `53de6f2`.
>
> | | |
> |---|---|
> | Pré-condição | as sete fases concluídas no Linux |
> | Estado | **o app compila, abre, carrega a ROM e navega**; a camada de dados está verificada contra o `we2002_core` nas duas ROMs; a bateria golden não roda |
> | Régua | `wte\make.ps1 check` — 884 testes, 43 dos 45 geradores |

---

## 1. O que precisa estar no disco

Duas pastas, nenhuma versionada, nenhuma baixável — ambas são do usuário, como
o [../CLAUDE.md](../CLAUDE.md) já diz para o `newWe2002`:

| O que | Onde | Sem isso |
|---|---|---|
| `we-team-editor/` — **a pasta inteira** | raiz do repositório | o app abre e avisa; 20 dos 45 geradores recusam |
| `roms/*.bin` | `roms/` na raiz | não há o que abrir |

> ### Não basta o `wte.exe`
>
> A **versão Lazarus** lê os 198 bitmaps e o `data/dat.bin` da pasta do
> Obocaman em tempo de execução — camisa 2D, bandeira, cabelo, barba e a
> tabela de arranque saem de lá. O `.exe` do Obocaman é outra coisa: é o
> **oráculo**, e serve às 20 ferramentas que medem o binário original.
>
> Com o `.exe` sozinho o app continua avisando que faltam os assets; com os
> bitmaps sozinhos os geradores continuam recusando.

### O link para `wte\assets`

A ordem de busca é a do [../wte/src/wte_datafiles.pas](../wte/src/wte_datafiles.pas)
e **não muda com o sistema**: `$WTE_ASSETS_DIR`, depois `<exe>\..\assets`,
depois `<exe>\..\share\we2002Lazarus`.

No Linux o `make -C wte assets` cria um symlink. Aqui não há alvo equivalente:
`make.ps1 assets` **confere e imprime o comando pronto**.

```powershell
cd wte
.\make.ps1 assets
cmd /c mklink /J "...\wte\assets" "...\we-team-editor"
```

A junção (`/J`) é o equivalente do `ln -s` que não pede privilégio no Windows.
`wte\assets` já está no `.gitignore`. O alvo termina contando o que alcançou:

```
>> achado em ...\wte\assets -- 198 bitmap(s), data\dat.bin ok
```

---

## 2. Ambiente

Medido em 2026-08-26, Windows 11 Pro 26200.

| Ferramenta | Versão aqui | Como veio | Sem ela |
|---|---|---|---|
| Lazarus + FPC | 4.8 / 3.2.2 x86_64-win64 | `winget install --id Lazarus.Lazarus --exact` | não compila |
| mingw-w64 (g++, objdump) | GCC 16.1.0, binutils 2.47 | `winget install --id BrechtSanders.WinLibs.POSIX.UCRT --exact` | o confronto bilíngue e 2 testes de `objdump` pulam |
| Python | 3.13 | já estava | os geradores e os testes |
| Pillow | 12.3.0 | `python -m pip install pillow` | 3 ferramentas de imagem pulam |
| Git for Windows | bash 4.4, grep 3.0 | já estava | os testes que exercitam bloco de shell |

Nenhuma das duas primeiras entra no PATH sozinha do jeito que as ferramentas
esperam — o instalador do Lazarus **não põe o `fpc`** no PATH. O
[../wte/make.ps1](../wte/make.ps1) resolve os dois e imprime o que achou:

```
Ambiente encontrado:
  lazbuild        C:\lazarus\lazbuild.exe
  arvore Lazarus  C:\lazarus
  fpc             C:\lazarus\fpc\3.2.2\bin\x86_64-win64\fpc.exe
  g++             ...\mingw64\bin\g++.exe
  bash            C:\Program Files\Git\bin\bash.exe
  python          ...\python.exe
```

`WTE_LAZBUILD`, `WTE_FPC`, `WTE_BASH` e `WTE_LAZARUS_DIR` ganham da busca.

### Widgetset: **win32**, não GTK2

O `.lpi` não fixa widgetset, então o Lazarus escolhe o do sistema. No Linux é
`LCLgtk2`, aqui é `LCLwin32` — o log do `lazbuild` mostra `-dLCLwin32`.

Isso importa ao ler `wte/re/`: as notas sobre `Ctl3D`, sobre `TOpenDialog` que
não se dirige por coordenada e sobre fonte substituída **descrevem o GTK2**.
Continuam válidas como registro do que foi medido; não descrevem o que se vê
aqui.

### DPI: a janela é esticada, e a geometria continua a do `.lfm`

Num monitor a 150% a janela ocupa **792×756 px reais**, que é 528×504 × 1,5. O
app não redesenha nada em escala: ele pinta os 528×504 que o `.lfm` manda e o
Windows estica o resultado, porque `Application.Scaled` está desligado — a
decisão e o motivo estão no [../wte/wte.lpr](../wte/wte.lpr).

Isso é o comportamento certo para este projeto e **não** precisa de conserto.
Só há uma consequência prática: **régua de pixel em captura de tela mede 1,5×**
num display escalado. Quem for comparar screenshot com o Linux tira a captura
num display a 100%, ou divide.

---

## 3. O que o Windows quebrou, e o conserto de cada um

Onze coisas. Nenhuma era bug latente do Linux: são todas casos em que o Windows
tem uma regra diferente e o código dependia da do Linux sem dizer.

Nenhum conserto altera comportamento no Linux. Onde há `{$IFDEF WINDOWS}` ou
`os.environ.get(...)`, o ramo de sempre é o padrão; onde há
`key=lambda p: p.as_posix()`, a ordem do Linux é idêntica à de antes porque lá
`str(Path)` **é** o `as_posix()`.

### 3.1 `--help` e `--list` morriam num diálogo da LCL

O `.lpi` pede `GraphicApplication`, e `.exe` do subsistema GUI nasce **sem
handle de saída padrão**. A RTL do FPC não abre `Output` nesse caso, e o
primeiro `WriteLn` levanta `EInOutError`, que a LCL transforma em

```
File not open.
Press OK to ignore and risk data corruption.
```

**antes de qualquer janela**. Redirecionar no shell não resolve — quem não
abriu o arquivo foi a RTL, não o sistema.

Conserto no [../wte/src/wtemain.pas](../wte/src/wtemain.pas): a impressão passou
a ser `Linha()`, que resolve a saída na primeira chamada com
`AttachConsole(ATTACH_PARENT_PROCESS)` — entra no console de quem lançou, se
houver, e vira silêncio se não houver (duplo clique no ícone). A resolução é
preguiçosa de propósito: fazê-la no arranque anexaria um console a toda
abertura normal do editor.

O `WriteLn(StdErr, ...)` do `MainForm.FormShow` **não** foi tocado, e não
precisa: o `StdErr` do FPC é aberto mesmo em app GUI. Medido.

### 3.2 `sorted()` sobre `Path` é case-insensitive no Windows

O caso que revelou: `wte/re/dfm/MainForm.dfm`. No Linux `M` (0x4D) vem antes de
`e` (0x65), então ele encabeça a lista; no Windows a comparação é pelo
`_str_normcase`, que é **minúsculo**, e ele cai depois de `estrategia.dfm`.
Todo relatório ordenado por caminho saía noutra ordem, e três `--check`
acusavam divergência que não existia (`dfm2lfm.py`, `check_retorno.py`,
`check_fase3.py`).

Conserto: `key=lambda p: p.as_posix()` em **45 sítios de 23 ferramentas**. A
chave é `as_posix()` e não `p.name` porque no Linux `str(Path)` **já é** o
`as_posix()` — a ordem de lá não muda nem para `glob` de um diretório só nem
para `rglob` atravessando subdiretório.

### 3.3 `bash` resolve para o WSL, e o PATH não adianta

`C:\Windows\System32\bash.exe` é o atalho do WSL. O `CreateProcess` procura em
System32 **antes** do PATH, então pôr o Git for Windows na frente do PATH não
muda nada: `subprocess.run(["bash", ...])` continua caindo no WSL, que aqui não
tem distribuição e sai 1 dizendo isso.

Conserto: `WTE_BASH` nas quatro ferramentas que chamam bash
(`test_roteiro.py`, `test_check_golden.py`, `test_check_nativo.py`,
`sonda_dorsal.py`). Sem a variável nada muda.

### 3.4 `grep -P` recusa sem locale

O bash do Git for Windows nasce sem locale quando o pai é o PowerShell, e aí o
`grep` do MSYS recusa:

```
grep: -P supports only unibyte and UTF-8 locales
```

saindo 2. O bloco `TSV-DECISAO` do `golden_suite.sh` usa `grep -qP` para
decidir se a linha de um trio (roteiro, rom, modo) já está no `golden.tsv`; com
a recusa a condição dá sempre falsa, a linha velha nunca sai, e a decisão
**acrescenta** onde deveria **substituir**. O sintoma é o TSV com a mesma
corrida duas vezes — que parece bug da decisão e não é.

Conserto: `LC_ALL=C.UTF-8`, no `make.ps1`. Não se conserta no script: quem está
errado é o ambiente.

### 3.5 Caminho do Windows dentro de script bash

`f"SAIDA={alvo}"` com `alvo` sendo um `Path` do Windows produz
`SAIDA=C:\Users\...`, e o bash lê `\U`, `\r` e companhia como escape. O bloco
gravava noutro lugar e o teste via o TSV intacto, como se a decisão não tivesse
rodado.

Conserto: `as_posix()` em toda interpolação de caminho para dentro de bash. O
bash do Git for Windows entende `C:/Users/...`.

### 3.6 `Path.write_text()` escreve CRLF no Windows

**O grave:** `test_dump_mcr.py` e `test_dump_render2d.py` plantam um erro no
fonte de verdade da árvore e o restauram no `finally`. A restauração sem
`newline` explícito devolvia o arquivo com CRLF — `git status` acusava
`wte/src/we2002_mcr.pas` modificado depois de uma corrida de teste que passou.

**O brando:** todo gerador que escreve em `wte/re/` faz o mesmo. Aí o
[../.gitattributes](../.gitattributes) já resolve, e por decisão registrada
(task T1 da fase 7 do `newWe2002`): `* text=auto eol=lf` normaliza no commit.

Conserto: `newline="\n"` só onde a gravação **não** passa pelo git.

### 3.7 `make_icon.py --check` redesenha os ícones

Ele **não tem** `--check` — decisão herdada do `newWe2002`, porque a saída do
PIL não é byte-determinística entre versões do Pillow. Passar o argumento não é
conferir: ele ignora e redesenha os sete PNG. Medido aqui: quatro ícones
commitados voltaram modificados de um alvo chamado `check`.

Conserto: o `make.ps1 check` o exclui da varredura. Quem quiser redesenhar
chama `make.ps1 icon` — e **olha** o resultado.

### 3.8 `check_lcl_props.py` só sabia procurar `/usr/lib/lazarus`

Conserto: `WTE_LAZARUS_DIR` aponta a **árvore** (a que contém `lcl\` e
`components\lazutils\lazversion.pas`), pulando o nível de versão que só a
distribuição tem. A conferência de versão continua valendo — quem decide é o
`lazversion.pas`, não o nome do diretório.

**A variável é lida no import, num nome de módulo**, e não dentro da função.
Sem isso ela passa por cima da LCL sintética que o `test_check_lcl_props.py`
planta num temporário, e os 17 casos dele medem a árvore instalada em vez da
fixture.

### 3.9 "Não medido" não é "falhou"

A LCL do `winget` é 4.8; o `LCL_VERSAO` do `dfm2lfm.py` está pinado em `3.0`.
O `check_lcl_props.py` recusava com exit 2, e o `check` ficava vermelho **para
sempre** nesta máquina — alvo sempre vermelho ninguém lê.

Conserto, seguindo a forma que o `check_lcl_combo.py` já usava: separar as duas
saídas. *Não há LCL utilizável* (ausente, ou de outra versão) é `PULADO` e sai
**0**, dizendo o que deixou de medir; *a tabela não bate com a LCL* continua
saindo **2**. Nada no `make.ps1` sabe o nome de ferramenta nenhuma — quem sabe
se mediu é a ferramenta, o script só conta.

O mesmo no `test_check_lcl_props.py`: a classe que roda contra a LCL de verdade
pula dizendo qual é a versão do disco.

### 3.10 O `fpc` não entra no PATH, e treze testes pulavam

O instalador do Lazarus no Windows não põe o `fpc` no PATH, e treze testes de
`tools/` compilam Pascal de verdade (`test_camada_dados.pas`,
`test_render.pas`, `test_bmp.pas`, `test_mcr.pas`, `test_ml.pas`,
`test_preco.pas`, os offsets). Todos procuram com `shutil.which("fpc")`, e
todos pulavam — pulo honesto, mas era a camada de dados inteira deixando de ser
medida.

Conserto: `Get-FpcDir` no `make.ps1` acha o `fpc` sob a árvore do Lazarus e o
põe no PATH. **Os pulos caíram de 25 para 11.**

### 3.11 `WTE_WORK`

A medição do `compare_dumps.py` copia ~1,9 GB para `work/` na raiz. Este
repositório mora dentro do OneDrive, e 1,9 GB ali vira 1,9 GB de sincronização
antes de alguém apagar. `WTE_WORK` aponta para fora sem mudar nada do que se
mede.

---

## 4. Compilar e rodar

Não há `make` nem bash no Windows, então o `wte/Makefile` não serve. O
[../wte/make.ps1](../wte/make.ps1) cobre os alvos que fazem sentido e **recusa
os que não fazem, dizendo por quê** — a mesma regra do `check` do Makefile:
alvo verde sem medição é pior do que alvo ausente.

```powershell
cd wte
.\make.ps1                              # lista os alvos e o ambiente achado
.\make.ps1 build                        # lazbuild wte.lpi -> build\wte.exe
.\make.ps1 run -Imagem C:\caminho\copia.bin
.\make.ps1 test                         # unittest de tools\test_*.py
.\make.ps1 check                        # test + --check dos geradores
.\make.ps1 icon
.\make.ps1 clean
```

**Sempre sobre cópia** — o editor grava in-place, como os outros três.

### Os três alvos que o Makefile tem e este script não

| Alvo | Por que não existe aqui |
|---|---|
| `assets` | é `ln -sfn`. Aqui o alvo **diz onde pôr** — ver a §1 |
| `run-98` | é Xvfb. Não há `:98` no Windows; a janela abre no desktop |
| `install` | é o layout do freedesktop. Não há equivalente, e empacotar ficou de fora por decisão (WTE-TASK-39) |

---

## 5. O que está medido

Tudo abaixo em 2026-08-26, com a pasta do Obocaman e as duas ROMs no disco.

### 5.1 A camada de dados, contra o `we2002_core` — **zero divergência**

É o aceite da fase 3 refeito no Windows, e é a medida mais forte que se pode
fazer aqui. `compare_dumps.py --medir` compila os dois dumpers com
**compiladores diferentes** — `fpc` lendo o Pascal gerado, `g++` lendo o C++
original — e confronta as duas metades:

| ROM | linhas do dump | divergências | round-trip Pascal × C++ |
|---|---:|---:|---:|
| european-deluxe | 66.498 | **0** | **0 byte** |
| japanese | 66.498 | **0** | **0 byte** |

Todas as colunas do `wte/re/fase-3.tsv` batem com a medição do Linux, **menos
uma** — ver a §6.

```powershell
$env:WTE_WORK = 'D:\tmp\wte-work'      # fora do OneDrive
python wte\tools\compare_dumps.py --medir
```

> **Não commite o `wte/re/fase-3.tsv` que essa corrida escreve.** O arquivo
> versionado é a evidência do Linux; sobrescrevê-lo troca uma medição por
> outra, feita noutra máquina e noutro compilador.

### 5.2 A régua de sempre — `make.ps1 check` sai **0**

| | |
|---|---|
| Testes de ferramenta | **884 de 884**, 11 pulados |
| Geradores | **43 conferidos de 45**, 2 pulados, nenhum divergiu |
| Árvore depois | limpa — nenhum gerador ou teste deixou arquivo modificado |

Os 11 pulos, cada um com motivo escrito pela própria ferramenta:

| Quantos | Motivo | Fecha quando |
|---:|---|---|
| 5 | `sem bwrap` — a guarda do Wine não foi exercitada | nunca no Windows; `bwrap` é namespace de Linux |
| 2 | `sem fixture de cartão` — o `.mcr` sai de um roteiro golden | precisa de Xvfb; não roda aqui |
| 2 | LCL do disco é 4.8, o pino é 3.0 | instalando Lazarus 3.0, ou remedindo a tabela |
| 1 | remedição completa (`WTE_ROUNDTRIP=1`) | é a §5.1, rodada à mão |
| 1 | `sem work\ml-jp.bin` | `copy roms\japanese-shift-jis.bin work\ml-jp.bin` |

### 5.3 O app, sobre a ROM japonesa

- Compila limpo: Lazarus 4.8 / FPC 3.2.2, alvo `x86_64-win64`, widgetset
  `win32`. **Zero erro, zero warning**, 1.888.608 bytes de código. Nenhuma
  linha de Pascal precisou de `{$IFDEF}` além da saída de texto da §3.1 — não
  havia `uses Unix`, nem caminho absoluto, nem I/O em modo texto sobre a
  imagem.
- A janela abre **sem** o aviso de assets, com `copia-jp.bin` no rótulo.
- Os três combos de time trazem **96 itens** cada e nascem habilitados.
- Escolhendo `1 Escocia`: **bandeira e camisa 2D desenhadas**, as cinco barras
  preenchidas, `SCOTLAND` e `SCO` nos campos de nome, os números 1–23 na régua
  de baixo, e o contador de blocos livres de Master League em 1.
- Os 18 formulários são criados na ordem medida — `wte.exe --list`.

**Não verificado:** os campos de nome em kanji da ROM japonesa aparecem como
`?????`. Isso pode ser idêntico ao Linux (o app não mapeia fonte japonesa) ou
ser efeito da página de código do Windows. **Não foi medido dos dois lados**, e
até que seja, não se afirma nada sobre ele.

### 5.4 O que **nunca** vai rodar aqui, e não é falta de conserto

A **bateria golden inteira** — os 24 roteiros, os dois lados, o
`golden_check.sh`, o `compara_tela.sh`, o `nativo_check.sh`. Ela depende de
Xvfb no `:98`, `xdotool` e Wine, e o Wine é o que roda o oráculo PE32 do
Obocaman. Nada disso existe no Windows; o oráculo aqui rodaria **nativo**, que
é outra medida.

Com todas as letras:

> **A paridade byte a byte contra o `wte.exe` continua sendo afirmada pela
> máquina Linux.** O que esta porta prova é que o mesmo fonte compila e roda no
> Windows, e que a **camada de dados** lê e grava ali exatamente o que o
> `we2002_core` lê e grava, nas duas ROMs.

---

## 6. Um achado que **não é** do `wte/`: o sidecar `_url.txt` sai com CRLF

A única coluna do `fase-3.tsv` que não bateu com o Linux:

| Coluna | Linux | Windows |
|---|---:|---:|
| `sidecar_bytes` | 1911 | **3822** |
| `sidecar_igual` | sim | **não** |

3822 é exatamente 2 × 1911 — o arquivo tem 1911 linhas vazias, e cada `\n`
virou `\r\n`.

**Os dois lados não fazem a mesma coisa, e quem diverge é o C++:**

- o Pascal ([../wte/src/we2002_database.pas](../wte/src/we2002_database.pas),
  `WriteUrlSidecar`) grava por `TFileStream` binário e escreve o byte `10` à
  mão. O comentário diz o porquê, e é deliberado: *"sem #13 e sem BOM"*. Dá
  1911 nas duas plataformas;
- o C++ ([../src/core/Database.cpp](../src/core/Database.cpp)) abre com
  `url_file.open(UrlSidecarPath(image), std::ios::trunc)` — **sem
  `std::ios::binary`**. Em modo texto o runtime do Windows traduz `\n` para
  `\r\n`.

Isso é um defeito do **`newWe2002`**, não do `wte/`, e é exatamente o risco 2
que a §1 do [/docs/PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md) nomeia — *"se algum
`open` perder o `std::ios::binary`, o runtime da Microsoft traduz `0x0A` ↔
`0x0D 0x0A`"*. Aquela seção auditou o `CdImage.cpp` e **não** o `ofstream` do
sidecar.

Por que os golden tests nunca pegaram: eles comparam a **imagem de CD**, e o
sidecar é um arquivo ao lado.

**Não foi consertado aqui, por três razões:**

1. é outro produto, e este trabalho é do `wte/`;
2. o `Database.cpp` é **gerado** — o conserto é uma regra do
   [../tools/port_database.py](../tools/port_database.py), linhas 73–75, e a
   saída teria de ser regerada e reconferida;
3. **há uma decisão a tomar antes**, e ela não é minha: o `ed.exe` de 2002 era
   MFC em modo texto no Windows, então CRLF pode ser o comportamento
   *original* — e o critério do `newWe2002` é clonar o original inclusive nos
   defeitos. Hoje o port não está nem num nem noutro: escreve LF no Linux e
   CRLF no Windows, ou seja, é inconsistente **consigo mesmo**. Qualquer das
   duas saídas é melhor do que isso, mas a escolha é do dono do produto.

---

## 7. Arquivos que esta porta tocou

| Arquivo | O quê |
|---|---|
| [../wte/make.ps1](../wte/make.ps1) | **novo** — o irmão do `Makefile` |
| [../wte/src/wtemain.pas](../wte/src/wtemain.pas) | a saída de texto segura da §3.1 |
| `wte/tools/*.py` — 25 arquivos | as §§3.2 a 3.11 |
| [/docs/PLAN-WTE-LAZARUS.md](/docs/PLAN-WTE-LAZARUS.md) §4.4 | a fração caiu de 51,3% para 51,2% — o `wtemain.pas` cresceu 56 linhas |
| [../wte/re/fase-2.md](../wte/re/fase-2.md) | regerado pelo `check_fase2.py`, pela mesma razão |
