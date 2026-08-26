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
> | Estado | **o app compila, abre e navega no Windows**; a bateria golden não |
> | O que falta para o usuário | a seção [1](#1-o-que-trazer-do-linux) |

---

## 1. O que trazer do Linux

Esta é a única parte que exige alguém. O resto já está no repositório.

**Duas pastas, nenhuma versionada, nenhuma baixável.** Ambas são do usuário,
como o `../CLAUDE.md` já diz para o `newWe2002`:

| O que | Para onde | Tamanho | Sem isso |
|---|---|---|---|
| `we-team-editor/` — **a pasta inteira** | raiz do repositório | ~1 MB de `.exe` + 198 `.bmp` + `data/dat.bin` | o app abre e avisa; 20 dos 45 geradores recusam |
| `roms/*.bin` | `roms/` na raiz | ~474 MB por imagem | não há o que abrir |

> ### Não basta o `wte.exe`
>
> A **versão Lazarus** lê os 198 bitmaps e o `data/dat.bin` da pasta do
> Obocaman em tempo de execução — camisa 2D, bandeira, cabelo, barba e a
> tabela de arranque saem de lá. O `.exe` do Obocaman é outra coisa: ele é o
> **oráculo**, e serve às 20 ferramentas que medem o binário original.
>
> Traga a pasta toda. Com o `.exe` sozinho o app continua avisando que faltam
> os assets, e com os bitmaps sozinhos os geradores continuam recusando.

Das ROMs, a que interessa é a **japonesa** (`japanese-shift-jis.bin`): é a
única contra a qual a bateria golden foi medida, pelo motivo registrado em
[../wte/re/crash-causa.md](../wte/re/crash-causa.md) — o oráculo morre com
`c0000005` ao trocar de time na European Deluxe.

### Onde a pasta do Obocaman entra

A ordem de busca é a do [`../wte/src/wte_datafiles.pas`](../wte/src/wte_datafiles.pas)
e **não muda com o sistema**:

1. o diretório que `WTE_ASSETS_DIR` apontar;
2. `<exe>\..\assets` — ou seja, `wte\assets`;
3. `<exe>\..\share\we2002Lazarus`.

No Linux o `make -C wte assets` cria um symlink. Aqui não há alvo equivalente:
`make.ps1 assets` **diz onde pôr** e imprime a linha de junção pronta. Copie a
pasta para a raiz e rode:

```powershell
cd wte
.\make.ps1 assets                      # confere e imprime o comando
cmd /c mklink /J wte\assets ..\we-team-editor
```

A junção (`/J`) é o equivalente do `ln -s` que não pede privilégio no Windows.
`wte\assets` já está no `.gitignore`.

---

## 2. Ambiente

Medido em 2026-08-26, Windows 11 Pro 26200.

| Ferramenta | Versão aqui | Como veio | Obrigatória para |
|---|---|---|---|
| Lazarus + FPC | 4.8 / 3.2.2 x86_64-win64 | `winget install --id Lazarus.Lazarus --exact` | compilar |
| Python | 3.13 | já estava | os geradores e os testes |
| Pillow | 12.3.0 | `python -m pip install pillow` | `check_carregado.py`, `compara_tela.py`, `make_icon.py` |
| Git for Windows | 2.x (bash 4.4, grep 3.0) | já estava | os testes que exercitam bloco de shell |

O `lazbuild` **não entra no PATH** — o instalador não o põe. O
[`../wte/make.ps1`](../wte/make.ps1) o acha sozinho em `C:\lazarus`, no
`%LOCALAPPDATA%\Lazarus` e no `C:\fpcupdeluxe\lazarus`; `WTE_LAZBUILD` ganha de
todos.

### Widgetset: **win32**, não GTK2

O `.lpi` não fixa widgetset, então o Lazarus escolhe o do sistema. No Linux é
`LCLgtk2`, aqui é `LCLwin32` — o próprio log do `lazbuild` mostra `-dLCLwin32`.

Isso importa ao ler `wte/re/`: as notas sobre `Ctl3D`, sobre `TOpenDialog` que
não se dirige por coordenada e sobre fonte substituída **descrevem o GTK2**.
Continuam válidas como registro do que foi medido; não descrevem o que se vê
aqui.

### Variáveis que o `make.ps1` põe, e por quê

Ele exporta três coisas antes de chamar qualquer ferramenta. Quem rodar à mão
precisa delas:

```powershell
$env:WTE_BASH        = 'C:\Program Files\Git\bin\bash.exe'
$env:LC_ALL          = 'C.UTF-8'
$env:WTE_LAZARUS_DIR = 'C:\lazarus'
```

As razões estão na seção [3](#3-o-que-o-windows-quebrou-e-o-conserto-de-cada-um).

---

## 3. O que o Windows quebrou, e o conserto de cada um

Oito coisas. Nenhuma era bug latente do Linux: são todas casos em que o Windows
tem uma regra diferente e o código dependia da do Linux sem dizer.

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

Conserto no [`../wte/src/wtemain.pas`](../wte/src/wtemain.pas): a impressão
passou a ser `Linha()`, que resolve a saída na primeira chamada com
`AttachConsole(ATTACH_PARENT_PROCESS)` — entra no console de quem lançou, se
houver, e vira silêncio se não houver (duplo clique no ícone). A resolução é
preguiçosa de propósito: fazê-la no arranque anexaria um console a toda
abertura normal do editor.

O `WriteLn(StdErr, ...)` do `MainForm.FormShow` **não** foi tocado, e não
precisa: o `StdErr` do FPC é aberto mesmo em app GUI, e o aviso de assets
ausentes sai lá como sempre saiu. Medido.

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
`sonda_dorsal.py`). Sem a variável nada muda — no Linux `bash` é o que sempre
foi.

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

Conserto: `as_posix()` em toda interpolação de caminho para dentro de bash
(`test_check_golden.py`, `test_roteiro.py`). O bash do Git for Windows entende
`C:/Users/...`.

### 3.6 `Path.write_text()` escreve CRLF no Windows

Duas consequências, de gravidade diferente.

**A grave:** `test_dump_mcr.py` e `test_dump_render2d.py` plantam um erro no
fonte de verdade da árvore e o restauram no `finally`. A restauração sem
`newline` explícito devolvia o arquivo com CRLF — `git status` acusava
`wte/src/we2002_mcr.pas` modificado depois de uma corrida de teste que passou.

**A branda:** todo gerador que escreve em `wte/re/` faz o mesmo. Aí o
[`../.gitattributes`](../.gitattributes) já resolve, e por decisão registrada
(task T1 da fase 7 do `newWe2002`): `* text=auto eol=lf` normaliza no commit,
então o conteúdo não se perde.

Conserto: `newline="\n"` só onde a gravação **não** passa pelo git — os dois
arquivos de teste acima e os dois fixtures que alimentam bash.

### 3.7 `make_icon.py --check` redesenha os ícones

Ele **não tem** `--check` — é decisão herdada do `newWe2002`, porque a saída do
PIL não é byte-determinística entre versões do Pillow. Passar o argumento não é
conferir: ele ignora e redesenha os sete PNG. Medido aqui: quatro ícones
commitados voltaram modificados de um alvo chamado `check`.

Conserto: o `make.ps1 check` o exclui da varredura, com o motivo escrito. Quem
quiser redesenhar chama `make.ps1 icon` — e **olha** o resultado, que é a regra
que o `../CLAUDE.md` já dá para o ícone do irmão.

### 3.8 `check_lcl_props.py` só sabia procurar `/usr/lib/lazarus`

Conserto: `WTE_LAZARUS_DIR` aponta a **árvore** (a que contém `lcl\` e
`components\lazutils\lazversion.pas`), pulando o nível de versão que só a
distribuição tem. A conferência de versão continua valendo — quem decide é o
`lazversion.pas`, não o nome do diretório.

E é por isso que essa ferramenta continua vermelha aqui: ver a seção
[5](#5-o-que-fica-vermelho-e-por-que).

---

## 4. Compilar e rodar

Não há `make` nem bash no Windows, então o `wte/Makefile` não serve. O
[`../wte/make.ps1`](../wte/make.ps1) cobre os alvos que fazem sentido e **recusa
os que não fazem, dizendo por quê** — que é a mesma regra do `check` do
Makefile: alvo verde sem medição é pior do que alvo ausente.

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

Direto, sem o script:

```powershell
C:\lazarus\lazbuild.exe wte\wte.lpi
wte\build\wte.exe C:\caminho\copia.bin
```

**Sempre sobre cópia** — o editor grava in-place, como os outros três.

### Os três alvos que o Makefile tem e este script não

| Alvo | Por que não existe aqui |
|---|---|
| `assets` | é `ln -sfn`. Aqui o alvo **diz onde pôr** — ver a seção [1](#1-o-que-trazer-do-linux) |
| `run-98` | é Xvfb. Não há `:98` no Windows; a janela abre no desktop |
| `install` | é o layout do freedesktop. Não há equivalente, e empacotar ficou de fora por decisão (WTE-TASK-39) |

---

## 5. O que está medido, e o que fica vermelho

Tudo abaixo foi medido em 2026-08-26, **sem** a pasta do Obocaman e **sem**
ROM — que é o estado desta máquina até a seção [1](#1-o-que-trazer-do-linux)
ser cumprida.

### Verde

- **O `.exe` compila limpo.** Lazarus 4.8 / FPC 3.2.2, alvo `x86_64-win64`,
  widgetset `win32`. Zero erro, zero warning, 1.888.608 bytes de código.
  Nenhuma linha de código Pascal precisou de `{$IFDEF}` além da saída de texto
  da §3.1 — não havia `uses Unix`, nem caminho absoluto, nem I/O em modo texto
  sobre a imagem.
- **A janela abre e a geometria é a do `.lfm`.** 528×504 na tela contra os
  522×475 de cliente que o DFM declara — a diferença são a borda e a barra de
  título do Windows. `Application.Scaled` continua desligado, e o
  [`../wte/wte.lpr`](../wte/wte.lpr) explica por quê; a janela **não** escala
  com o DPI, que é o que a fidelidade de pixel exige.
- **Os 18 formulários são criados na ordem medida.** `wte.exe --list` os
  imprime.
- **874 dos 875 testes de ferramenta passam** (139 pulados por falta do `.exe`
  do Obocaman ou de captura de tela). O único que falha é o
  `test_check_edicao`, e ele falha por falta do `.exe`.
- **24 dos 45 geradores passam no `--check`.**

### Vermelho, e cada um com a razão

| Quantos | O quê | Por quê | Fecha quando |
|---|---|---|---|
| 20 geradores + 1 teste | `dump_*.py`, `check_fase1.py`, `check_barras.py`, `conta_ml.py`, `analisar_crash.py`, `check_edicao.py`, `dfm_extract.py` | leem `we-team-editor/we-team-editor.exe`, que não está no disco | a pasta chegar (seção [1](#1-o-que-trazer-do-linux)) |
| 1 gerador | `check_lcl_props.py` | `LCL_VERSAO` do `dfm2lfm.py` está pinada em `3.0`; aqui a LCL é `4.8` | nunca, nesta máquina — ver abaixo |

Sobre o `check_lcl_props.py`: **a recusa está certa e é o ponto dele.** Ele
confere a tabela `PROPRIEDADES` do `dfm2lfm.py` contra as seções `published` da
LCL instalada, e a tabela foi medida na 3.0. Rodar contra a 4.8 e aceitar o que
sair seria trocar a régua pelo objeto medido. Remedir é trabalho de verdade, e
não é trabalho desta porta — o `winget` traz 4.8 e o Zorin traz 3.0.

### O que **nunca** vai rodar aqui, e não é falta de conserto

A **bateria golden inteira** — os 24 roteiros, os dois lados, o
`golden_check.sh`, o `compara_tela.sh`, o `nativo_check.sh`. Ela depende de
Xvfb no `:98`, `xdotool` e Wine, e o Wine é o que roda o oráculo PE32 do
Obocaman. Nada disso existe no Windows; o oráculo aqui rodaria **nativo**, que
é outra medida.

Isso quer dizer, com todas as letras:

> **A paridade byte a byte do `wte/` continua sendo afirmada pela máquina
> Linux.** O que esta porta prova é que o mesmo fonte compila e roda no
> Windows, e que o ferramental Python que não depende do `:98` mede o mesmo
> dos dois lados.

Um dia comparar o `.exe` do FPC/Windows contra o do FPC/Linux byte a byte é
possível — seria o equivalente do que a seção 5 do
[/docs/PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md) fez para o `newWe2002`, com o
`dump_estado.pas` no lugar do `golden_tool`. **Não foi feito**, porque exige a
ROM, e a ROM é o item 2 da seção [1](#1-o-que-trazer-do-linux).

---

## 6. Checklist, quando a pasta chegar

Na ordem, do Windows:

1. `git pull` — traz este documento, o `make.ps1` e os oito consertos da §3.
2. Copiar `we-team-editor/` para a raiz do repositório.
3. Copiar ao menos `roms/japanese-shift-jis.bin`.
4. `cd wte; .\make.ps1 assets` — ele conta os bitmaps que alcançou e o
   `dat.bin`; se disser `AUSENTE`, a pasta veio incompleta.
5. `.\make.ps1 check` — o esperado é **44 dos 45 verdes**, sobrando só o
   `check_lcl_props.py` da §5.
6. `.\make.ps1 build`
7. Copiar a ROM para um caminho de trabalho e
   `.\make.ps1 run -Imagem <cópia>` — a janela tem de abrir **sem** o aviso de
   assets, com o nome do arquivo no rótulo e os combos de time habilitados.
8. Trocar de time, abrir a ficha de um jogador, olhar a camisa 2D. É a prova de
   que os 198 bitmaps estão sendo achados.

Se o passo 5 der mais de um vermelho, comparar com a lista da §5 antes de
tratar como regressão: a maioria dos geradores lê o `.exe` do Obocaman, e a
mensagem deles diz isso.

---

## 7. Arquivos que esta porta tocou

Nenhuma mudança altera comportamento no Linux. Onde há `{$IFDEF WINDOWS}` ou
`os.environ.get(...)`, o ramo de sempre é o padrão; onde há
`key=lambda p: p.as_posix()`, a ordem do Linux é idêntica à de antes porque lá
`str(Path)` **é** o `as_posix()`.

| Arquivo | O quê |
|---|---|
| [../wte/make.ps1](../wte/make.ps1) | **novo** — o irmão do `Makefile` |
| [../wte/src/wtemain.pas](../wte/src/wtemain.pas) | a saída de texto segura da §3.1 |
| `wte/tools/*.py` — 23 arquivos | as §§3.2 a 3.6 e 3.8 |
| [/docs/PLAN-WTE-LAZARUS.md](/docs/PLAN-WTE-LAZARUS.md) §4.4 | a fração caiu de 51,3% para 51,2% — o `wtemain.pas` cresceu 56 linhas |
| [../wte/re/fase-2.md](../wte/re/fase-2.md) | regerado pelo `check_fase2.py`, pela mesma razão |
