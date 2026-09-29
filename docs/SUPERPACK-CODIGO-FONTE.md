# Projetos com código-fonte no Superpack v6

Levantamento de 2026-09-29 sobre `C:\games\we2002\Superpackv6\We2002`: todo
projeto cujo fonte acompanha o pacote, em pasta aberta ou dentro de `.rar`/`.zip`
(os 122 arquivos compactados foram listados com o 7-Zip; compactado dentro de
compactado não foi aberto). Caminhos relativos à raiz do Superpack.

Ficaram de fora, por não serem projeto: páginas HTML salvas (`*_files/`, com
`.js` de site), `.bat` de instalação, o manual HTML do Psx Multi Converter e os
pacotes de runtime (DLL/OCX do VB6, DAO).

## Específicos do WE2002

| Projeto | Onde | Linguagem | O que é |
| --- | --- | --- | --- |
| **We2002 mania editor** — Francesco Moriero | `MCR\We2002 mania editor - Francesco Moriero\Codigo fuente\ed-eng.rar` | C++ / MFC (VC6 `.dsp` + VS `.sln`), 28 fontes | Versão anterior do editor que este repositório porta: `edDlg.cpp` datado de 2002-07-10, com 7.033 linhas contra as 8.456 do `legacy/mfc/` (que traz o import do SoFIFA acrescentado pelo thyddralisk). Edita times, jogadores, táticas, uniformes e bandeiras direto na imagem de CD. Ao lado, `Codigo fuente We mania editor.txt` é o bloco de `#define OFS_*` extraído do `edDlg.cpp`. |
| **We2002 edit** (`we2000edit`) — Haplo e polipoli | `MCR\We2002 edit - Haplo y polipoli\…\Codigo fuente\en_we2000edit\` | C++ / MFC (VC6), 29 fontes | Editor de jogadores e times sobre uma base Access (`we2000.mdb`, via DAO) com grade `MSFlexGrid`; aplica e exporta patch gravando nos `SELECT*.BIN` de dados e de nomes. Acompanha `SELECT.BIN`, `SELECT4.BIN` e `SLPM_866.00` de exemplo. Herdado de um editor do WE2000. |
| **TEX Editor v2.0** — ramonpsx | `TEX\TEX Editor v.2.0 - ramonpsx\rsc\` (e `rsc.rar`) | Visual Basic 6, 11 forms + 3 módulos | Editor dos uniformes `TEX_*.BIN`: monta camisa, luvas, braçadeira de capitão a partir das peças BMP em `data\`. |
| **T-Name Editor v1** — ramonpsx | `LOGO - TITLE - T_NAME - DATSEL - DAT2D - LC_XX\T_NAME\T-Name Editor v1 - ramonpsx\rsc\` (e `rsc.rar`, projeto `Tool T-name 2014.vbp`) | Visual Basic 6, 6 forms + 1 módulo | Desenha o gráfico de nome de time do `T_NAME` (fonte, negrito, cor, paleta `.pal`) e copia para a área de transferência; não grava no disco. O `.vbp` só existe dentro do `.rar`. |
| **WE2002 HEX Team Editor (beta)** — ramonpsx | `Opciones\WE2002 HEX Team Editor - ramonpsx\rsc\` (projeto `WE2002 Team Delete.vbp`) | Visual Basic 6, 1 form | Grava direto na ISO o número hexadecimal de 14 times (Irlanda a Dinamarca): `FF`, `99`, voltar ao padrão ou trocar por outro time — usado para apagar/substituir times. |
| **Editor de estrutura de estádio** — Fabio FJA | `Estadios\Estructuras estadios - Fabio FJA\PROGRAMA EDITOR DE ESTRUTURA DE ESTADIO.rar` | Visual Basic 6, 1 form | Insere coordenadas X/Y/Z nos `GRDM_*.BIN` para deformar a estrutura do estádio. |
| **Editor de altura de arquibancada** — Fabio FJA | `Estadios\Estructuras estadios - Fabio FJA\PROGRAMA EDITOR DE ALTURA DE ARQUIBANCADA.rar` | Visual Basic 6, 1 form | Grade de valores (69–78…) para a altura das arquibancadas no mesmo `GRDM_*.BIN`. |

## Ferramentas de PSX em geral (ROM hacking, imagem, patch)

| Projeto | Onde | Linguagem | O que é |
| --- | --- | --- | --- |
| **PSXAddress v1.01** — Klarth | `Hack\PSXAddress v1.01 - Klarth\src\` | C++ Win32 (VS `.sln`) | Converte endereço entre RAM do PSX, arquivo PS-EXE e save state do ePSXe (gzip). |
| **Pcsx debugger** — Agemo | `Hack\Emuladores debuggers\Pcsx debugger\src\` | C (fonte do PCSX), ~100 arquivos com as árvores Win32/Linux/MacOSX/Dreamcast/sh4 | PCSX modificado com depurador: breakpoint, dump de memória e CPU interpretada. `src\Agemo\` é a parte própria dele. |
| **Pcsx Trace 1.5b** | `Hack\Emuladores debuggers\Pcsx Trace 1.5b\src\` | C (fonte do PCSX) | Outro fork do PCSX, voltado a registrar traço de execução do R3000. |
| **ECM tools** — Neill Corlett | `ISO\Ecm tools - Neill Corlett\docs\` (`ecm.c`, `unecm.c`) | C, GPL | Remove e reconstrói EDC/ECC dos setores para comprimir a imagem `.bin`. |
| **Popstation** (do Psx2psp 1.4.2) | `ISO\Psx2psp_v.1.4.2\Files\Popstation src\` | C++ (DLL, VS `.sln`) | Converte ISO de PSX em `EBOOT.PBP` para PSP (`popstation.cpp`, `popstrip.cpp`). |
| **PPF-O-MATIC 3** (ApplyPPF/MakePPF) — Icarus/Paradox | `Parches\PPF-O-MATIC - Icarus-Paradox\Codigo fuente\ppfdev\` | C, versões Linux e VC | Aplica e cria patches `.ppf` 3.0; `PPF3.txt` documenta o formato. A GUI vem só em binário. |
| **Thingy32** — necrosaro / ZackMan | `Traduccion\Traduccion textos\Editores hexadecimales y tablas TBL\Thingy\` (`ThingyWin32.vbp`) | Visual Basic 5/6 | Editor hexadecimal com tabela `.tbl` para tradução; vem com `WE.tbl` e `cp932-ascii.tbl`. |
| **readtim.c** do E3D — Jum Hig | `Boot\3D Model Editor - Jum\readtim.c` | C (arquivo avulso) | Leitor de textura `.TIM` do editor de modelos 3D `e3d.exe` (TMD/3DO). O editor em si vem só em binário. |

## Emuladores e SDKs (fonte de terceiro, incidental)

| Projeto | Onde | Linguagem | O que é |
| --- | --- | --- | --- |
| **BleemRunXP** | `Emulacion\Emuladores\Bleem v1.4\BleemRunXP_src.zip` | C++ (VC6), 71 fontes | Carregador que faz o Bleem! 1.4 rodar no Windows NT/XP (CD-ROM, depuração, IA-32). |
| **Plugin SPU do ePSXe** (ADSR/Envelope/Volume) | `Hack\Tutorial como mover gráficos no we2002 - Fabio FJA\ePSXe_1.9.25Completo\plugins\src\`; `Opciones\Creditos infinitos ML - Fabio FJA\…\plugins\src\`; e dentro de `LOGO - …\Balon del menu\MBS - Fabio FJA\ePSXe_1.9.25 Bios+Plugins.rar` | C++, 6 arquivos | Trecho de fonte de plugin de som que veio junto em três cópias do ePSXe; não é projeto completo. |
| **HelloWorld_BizHawkTool** | `Emulacion\Emuladores\BizHawk v2.2.2\ExternalTools\HelloWorld_BizHawkTool.zip` | C# (`.sln`) | Exemplo oficial de ferramenta externa do BizHawk. |
| **Scripts Lua do BizHawk** | `Emulacion\Emuladores\BizHawk v2.2.2\Lua\` | Lua / Python | Scripts de exemplo (`ButtonCount`, `MovieClock`, `tasjudy`). |
| **Interface de plugin do MemcardRex** — Shendo | `Emulacion\Memory card\MemcardRex - Shendo\MemcardRex 1.7 - Shendo\Plugins\Plugin interface.cs` | C# (arquivo avulso) | Contrato para escrever plugin de edição de save; os plugins vêm só em DLL. |
| **Amostras do Loquendo TTS** | `Sonido\Tutorial para crear callnames con Loquendo - polipoli\Loquendo\…\LTTS\Samples\` e `AudioDevices\` | C / C++ / VB | Exemplos do SDK de síntese de voz (HelloTTS, SAPI4/5, gerador de arquivo), usado para gerar callnames. |
| **Headers ASPI** | `Emulacion\Emuladores\{Emurayden,Fpse v0.09,Vgs}\Drivers CDROM aspi\include\` | C (só `.h`/`.inc`) | Cabeçalhos do SDK ASPI da Adaptec; três cópias idênticas. |

## Os que mais importam para este repositório

- **We2002 mania editor** é uma versão mais antiga do fonte do `ed.exe`,
  sem o SoFIFA — dá para comparar com `legacy/mfc/` e ver o que mudou antes
  do upstream.
- **We2002 edit** (Haplo/polipoli) e os três de **ramonpsx** são os únicos
  outros editores de WE2002 com fonte; o **TEX Editor** conhece o formato dos
  `TEX_*.BIN` que o `tools/looks/` lê.
- Os dois programas de **estádio** do Fabio FJA documentam, em código, onde
  moram coordenadas nos `GRDM_*.BIN`.
