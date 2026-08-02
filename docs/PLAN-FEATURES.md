# Plano de features novas — assets do disco

> **Objetivo: sair do editor de tabelas e passar a editar os *arquivos* do
> disco — gráficos, nomes de apresentação e áudio.**
>
> Origem: análise das ferramentas de **Maximiliano Ducoli (CARP)** em
> <https://github.com/maxiducoli>, feita em **2026-08-02**.
>
> Pré-requisito: o escopo Linux (Fases 0–6 do [PLAN-LINUX.md](PLAN-LINUX.md))
> está fechado. Este plano começa na **Fase 8** para não colidir com a Fase 7
> (Windows), que continua não autorizada e é independente desta.
>
> Regra que atravessa o plano inteiro: **`golden` e `golden_gui` continuam
> verdes**. Nenhuma feature aqui toca os 69 offsets legados nem o caminho de
> `Database::Load`/`Save`. O que este plano adiciona vive ao lado, não no
> lugar.

---

## 1. O que foi analisado

21 repositórios públicos. 11 são de *Winning Eleven*; o resto é RAG, Unity e
trabalho de faculdade, fora de escopo.

| Repositório | O que é | Linguagem | Veredito |
|---|---|---|---|
| [WECompressor](https://github.com/maxiducoli/WECompressor) | Compressor/descompressor LZSS do formato `.BIN` | **C++** (MFC só na GUI) | **Entra** — núcleo de tudo |
| [SinSala-BIN-2k24](https://github.com/maxiducoli/SinSala-BIN-2k24---by-CARP) | Cria/edita `.BIN` com gráficos + paletas | C# | **Entra** (formato do contêiner) |
| [GraphicsTools](https://github.com/maxiducoli/GraphicsTools) | BMP ↔ TIM, paletas, TIM ↔ BIN, pintura 4/8 bpp | C# | **Entra** (conversão e paleta) |
| [Winning-Eleven-Image-Manager](https://github.com/maxiducoli/Winning-Eleven-Image-Manager---by-BAT-2005-) | Visualizador de `.BIN`: grade de imagens × grade de paletas | Pascal (BAT_WE, 2005) | **Entra como referência de UX** |
| [T_NAME-Maker](https://github.com/maxiducoli/T_NAME-Maker) | Gera `T_NAME.BIN` (nomes de time e estádio da tela de apresentação) | C# | **Entra** (depende dos anteriores) |
| [WEVagExtractor](https://github.com/maxiducoli/WEVagExtractor) | Extrai `.VAG` de contêiner `.RA` | C# | **Entra** (fase de áudio) |
| [Winning-Eleven-VAG-editor](https://github.com/maxiducoli/Winning-Eleven-VAG-editor) | Troca VAG dentro do `.RA` **ou da ISO**, WAV ↔ VAG | Pascal | **Entra** (fase de áudio) |
| [RA-Maker](https://github.com/maxiducoli/Winning-Eleven-2002---RA-Maker) | Monta `.RA` do zero | C# | **Parcial** — o autor marca "obsoleta"; só o layout do `.RA` interessa |
| [ISO-protect / File Extractor](https://github.com/maxiducoli/Winning-Eleven-ISO-protect---File-Extractor) | Extrai/insere arquivos na ISO | Pascal | **Entra a ideia**, não o código |
| [Nombres largos](https://github.com/maxiducoli/Winning-Eleven---Nombres-largos) | Nomes de time de até 11 chars no menu | C# | **Adiado** — ver §6 |
| [WE_TMD_Tools](https://github.com/maxiducoli/WE_TMD_Tools) | Extrai e remonta estádios (TMD, malha 3D) | C# | **Projeto à parte** — [PLAN-STADIUMS.md](PLAN-STADIUMS.md) |
| [WE2002-MultiTool](https://github.com/maxiducoli/WE2002-MultiTool) | Launcher das ferramentas acima | C# | **Fora** — somos um app só |

Nada disso é biblioteca: são todos WinForms/VCL com a lógica dentro do
formulário ou em classes que dependem de `Application.StartupPath`,
`DataGridView` e `Bitmap` do .NET. O aproveitamento é **de formato e de
algoritmo**, reimplementado em C++ no `src/core/` — não de código copiado,
exceto o `WECompress.cpp`, que já é C++ quase puro.

---

## 2. Por que isso se aplica ao nosso disco (evidência, não suposição)

As ferramentas do CARP dizem "versión PC". A dúvida óbvia é se o WE2002 de PC
usa os mesmos arquivos do disco PSX que editamos. **Usa.** Três verificações
feitas em 2026-08-02:

**(a) O disco tem exatamente os arquivos que as ferramentas atacam.**
Lendo o ISO9660 da imagem golden (setor 16 = PVD, dados em `n*2352+24`):

```
BIN/DAT2D.BIN      81.124      BIN/T_NAME.BIN     54.140
BIN/DATSEL.BIN    223.496      BIN/LOGO.BIN       17.600
BIN/DATSEL2.BIN   124.812      BIN/TITLE.BIN       8.132
BIN/DATSEL3.BIN    65.884      BIN/TEX_00..A4    ~30 KB cada (110 arquivos)
BIN/CG??.BIN      ~30 KB       BIN/GDC_*.BIN     ~150 KB (estádios)
SD/W2002J*.RA     8–22 MB      SD/DA/*.DA        1,4–28 MB (áudio CD-XA)
MOVIE/WE2002.STR  37.486.592   SLPM_870.56      337.920 (executável)
```

**(b) O `DAT2D.BIN` de amostra do repositório do CARP é byte a byte igual ao
do nosso disco japonês.** Ele publica um `DAT2D.BIN` de 81.124 bytes dentro do
Image Manager; extraído do `World Soccer Winning Eleven 2002 (Japan).bin`
(LBA 5300, 81.124 bytes) o arquivo é **idêntico**. Contra o European Deluxe o
tamanho e o cabeçalho batem e 3.798 bytes (4,7%) divergem — é o mesmo arquivo
com gráficos trocados pelo hack.

**(c) O descompressor do `WECompressor` funciona no nosso disco.** Reescrito em
Python a partir do `WECompress.cpp` e apontado para o `DAT2D.BIN` extraído, o
fluxo comprimido começa em **offset 8** e descomprime 7.447 bytes em 16.345 —
saída com nibbles repetidos, o padrão de pixel indexado 4 bpp. Nenhum outro
offset de 0 a 4095 produz fluxo válido, o que também indica um cabeçalho de
contêiner de 8 bytes.

> Detalhe de proveniência: os comentários do `WECompress.cpp` estão **em
> italiano** (`"esci dal ciclo"`, `"numero di bytes da arretrare"`), a mesma
> língua do nosso `edDlg.cpp`. Esse compressor provavelmente vem da mesma cena
> de modding italiana de 2002–2003 que produziu o `ed.exe`, e o CARP o
> manteve. Anotar isso no `NOTICE.md` quando o código entrar.

O que **não** foi verificado e precisa ser antes da Fase 10: se o layout
interno dos contêineres (`DATSEL*.BIN`, `CG*.BIN`) é o mesmo entre PSX e PC
além do `DAT2D`. A hipótese é que sim; a Fase 8 gera a evidência.

---

## 3. Onde isso encaixa no que já temos

O editor de hoje é **cego ao sistema de arquivos**: `Offsets.hpp` são 69
posições absolutas na imagem, e `CdImage` é um `seek`/`read`/`write` cru. Os
dados que ele edita moram dentro de `GAME.BIN`, `SELECT*.BIN` e afins, mas
isso nunca foi explicitado — os saltos de fronteira de setor
(`OFS_TEAM_NAME_1_A` etc.) são a única pista.

As features novas exigem o oposto: achar um arquivo pelo nome, ler o conteúdo
lógico dele sem os cabeçalhos de setor, e gravar de volta. Isso é uma camada
nova no core, e é o gargalo de tudo o mais.

Diferença de escopo que vale deixar explícita:

| Hoje | Depois |
|---|---|
| Bandeira = **índice** de forma + índice de cor | Bandeira = **bitmap**, editável pixel a pixel |
| Uniforme = índice de preview | Textura do uniforme (`TEX_*.BIN`) |
| Nome do time = string em tabela | Nome também na tela de apresentação (`T_NAME.BIN`) |
| Sem áudio | Narração (`SD/*.RA`) |

---

## 4. Arquitetura — **biblioteca nova, não `we2002_core` inchado**

A tentação era jogar tudo em `src/core/`. Não. `we2002_core` é exatamente
aquilo que o golden test julga; deixá-lo crescer transforma "a feature nova não
toca o `Database`" numa promessa de documento. Em alvo separado, isso vira
**erro de link**.

```
src/core/      we2002_core      INALTERADO — Database, CdImage, TextCodec, Sofifa
src/assets/    we2002_assets    NOVO — Iso9660, FileHandle, Lzss, BinArchive, Tim, Ecc
                                       (+ VagCodec, RaArchive na fase de áudio)
src/app/       newWe2002        AssetBrowser: árvore do disco + grade imagem × paleta
```

| Alvo | Depende de | Não pode depender de |
|---|---|---|
| `we2002_core` | libstdc++, libcurl | **`we2002_assets`** |
| `we2002_assets` | `we2002::core` (só por `CdImage`) | Qt, `windows.h`, POSIX |
| `newWe2002` | ambas + Qt6 | — |

A seta aponta num sentido só. `we2002_core` não linka `we2002_assets`, então
código de asset **não consegue** vazar para o caminho do `Database::Load`/`Save`
nem por acidente nem por conveniência de alguém com pressa.

A regra dura de "zero Qt, zero `windows.h`, zero POSIX" passa a valer também
para `we2002_assets` — é o que mantém os testes novos headless como os 61
atuais. Ela deixa de ser regra de *diretório* (`src/core/`) e passa a ser regra
de *alvo*; o `CLAUDE.md` precisa ser corrigido nesse ponto quando a Fase 8
entrar.

Alvos de teste também separados: `we2002_tests` (core, 61 checks) fica como
está e não cresce; entra `we2002_assets_tests`, com nome próprio no ctest.

Opção de build `WE2002_ASSETS` (padrão `ON`). Desligada, o app compila sem a
aba nova — útil para bisect e para a Fase 7 (Windows) não herdar superfície
extra antes da hora.

`CdImage` ganha um irmão, não um substituto. `Database::Load`/`Save` continuam
falando com offsets absolutos exatamente como hoje — é o que mantém o golden
test honesto.

---

## 5. As três decisões estruturais — **decididas em 2026-08-02**

Cada uma foi medida antes de ser decidida. As medições estão junto.

### (a) Gravação com tamanho diferente → **fit-or-fail, e rebuild de ISO está proibido**

A pergunta era se dava para deixar um arquivo crescer. A resposta veio de três
medições:

**1. O disco tem 26 MiB de folga entre arquivos.** As LBAs foram masterizadas
em números redondos e sobra espaço depois de quase todo arquivo:

| Arquivo | bytes | setores usados | folga depois | folga em bytes |
|---|---:|---:|---:|---:|
| `BIN/DAT2D.BIN` | 81.124 | 40 | 660 | 1.351.680 |
| `BIN/T_NAME.BIN` | 54.140 | 27 | 23 | 47.104 |
| `BIN/LOGO.BIN` | 17.600 | 9 | 91 | 186.368 |
| `BIN/TEX_00.BIN` | 32.496 | 16 | 4 | 8.192 |

**2. Mas o jogo não acha arquivo por nome.** Varredura dos primeiros 40 MiB da
imagem atrás das strings `DAT2D`, `T_NAME`, `DATSEL`, `W2002J00`: **um único
hit cada**, no setor 2925 — que é o próprio diretório `BIN/` do ISO9660. O
executável `SLPM_870.56` não contém nenhuma dessas strings, nem `.BIN`, nem
`BIN/`. Ou seja: **não há `CdSearchFile`**; as LBAs estão codificadas no código
do jogo, como é praxe em jogo de PSX da Konami.

Consequência dura: **corrigir o registro de diretório do ISO9660 é cosmético.**
O jogo lê pelo LBA que ele já tem, com uma contagem de setores que ele também
já tem, para dentro de um buffer de tamanho fixo. Crescer um arquivo exigiria
achar e corrigir essa tabela no código — e mesmo achando, o buffer de destino
continuaria do tamanho antigo.

E rebuild de ISO deixa de ser "caro" e passa a ser **errado**: além de quebrar
o jogo, realocar qualquer coisa invalida os 69 offsets absolutos de
`Offsets.hpp` e mata o editor legado junto.

**3. Na prática o problema quase não aparece.** Recomprimindo com o algoritmo
do CARP seis contêineres reais, o resultado é sempre **menor** que o original
(§5c). Estourar o extent exige que o usuário importe um gráfico bem mais
ruidoso que o que estava lá.

> **Decidido:** orçamento = tamanho original arredondado para cima até o fim do
> último setor (a cauda não usada do último setor conta como espaço livre). Se
> não couber, **recusa e diz quantos bytes faltaram**. Rebuild de ISO e
> realocação de extent ficam **fora do projeto**, não "para depois". A folga de
> 26 MiB fica documentada aqui só para não ser redescoberta e proposta de novo.

Escape hatch quando um item não couber: recomprimir o contêiner inteiro
(§5c) recupera ~1% do arquivo, o que costuma bastar. É explícito e avisado, não
automático.

### (b) EDC/ECC → **implementar, aplicar só no caminho novo, mais um comando avulso**

Medido: as duas imagens de teste têm **EDC válido** em todos os setores Modo 2
Forma 1 conferidos (PVD, executável, região do `OFS_TEAM_NAME_1`, diretório,
`DAT2D`, `T_NAME`). O CRC bate byte a byte com o cálculo padrão — polinômio
refletido `0xD8018001` sobre `[0x10, 0x818)`, valor guardado em `0x818`. Os
setores de `MOVIE/*.STR` e `SD/DA/*.DA` são Forma 2 e não têm ECC, só EDC
opcional.

O editor atual grava dados e **não recalcula nada** — logo, todo setor que ele
toca fica com EDC inválido. E isso nunca importou: o `ed.exe` faz isso desde
2002, os discos editados rodam, e emulador não confere Forma 1. O golden test
inclusive **depende** disso continuar assim: ele compara byte a byte com a
saída do `ed.exe`, então recalcular no caminho legado quebraria o teste.

Só que o caminho novo é diferente em natureza: gravar um contêiner inteiro toca
dezenas de setores de uma vez, e deixar todos com EDC velho transforma o
arquivo em lixo para qualquer ferramenta que valide o disco.

> **Decidido:** `Ecc.cpp` implementa EDC (CRC-32, ~15 linhas, já validado em
> protótipo) e ECC P/Q (Reed-Solomon em GF(2⁸), ~120 linhas, algoritmo
> público). Aplicado **exclusivamente** nos setores que o caminho de assets
> escrever. O `Database::Save` continua sem tocar em ECC — divergência
> intencional registrada, na mesma família das quatro da Fase 5 do PLAN-LINUX.
> Além disso entra um comando avulso `we2002_iso fixecc`, **opt-in**, que
> revalida a imagem inteira; nunca ligado ao `Save`.

### (c) Recompressão → **entrada não editada nunca recomprime**

Medido: recomprimi o bloco de seis contêineres reais do European Deluxe com o
algoritmo do CARP e comparei com os bytes da Konami.

| Arquivo | início do fluxo | comprimido | descomprimido | recomprimido | delta | igual à Konami? | round-trip |
|---|---:|---:|---:|---:|---:|:--:|:--:|
| `DAT2D` | 8 | 7.447 | 16.345 | 7.339 | −1,5% | não | ok |
| `LOGO` | 8 | 3.186 | 8.192 | 3.181 | −0,2% | não | ok |
| `TITLE` | 8 | 3.015 | 8.192 | 2.968 | −1,6% | não | ok |
| `T_NAME` | 4 | 1.890 | 8.192 | 1.852 | −2,0% | não | ok |
| `DATSEL3` | 8 | 2.973 | 8.192 | 2.939 | −1,1% | não | ok |
| `TEX_00` | 28 | 6.453 | 16.400 | 6.396 | −0,9% | não | ok |

Três leituras:

- **Nunca é byte-idêntico**, e há motivo estrutural: o CARP deixou
  **comentado** o ramo que emite o opcode de cópia literal em bloco
  (`0xC0..0xFE`), que o compressor da Konami usa. O descompressor entende esse
  opcode; o compressor não o gera. Não é bug — é uma escolha dele.
- **É sempre um pouco menor** (−0,2% a −2,0%). Recompressão não é risco de
  tamanho; é risco de *ruído no diff*.
- **`decompress(compress(x)) == x` em 100% dos casos.** Perda de dados não é a
  preocupação.

O offset de início do fluxo varia (4, 8, 28) — cada contêiner tem cabeçalho
próprio, o que a Fase 10 vai ter que mapear.

> **Decidido:** o `BinArchive` guarda os bytes comprimidos originais de cada
> entrada e **só regenera as que o usuário editou**. Isso dá a invariante que
> vale como teste de regressão do caminho novo: *abrir e salvar sem editar
> devolve a imagem byte a byte idêntica*. Toda entrada comprimida é
> **descomprimida de volta e comparada antes de ir para o disco** — sem
> exceção, sem flag para desligar. A recompressão do contêiner inteiro existe
> só como fallback explícito de (a), com aviso de que o arquivo inteiro muda.

---

## 6. O que fica de fora, e por quê

- **TMD / estádios.** Malha 3D, UV, texturas — precisaria de um visualizador
  3D dentro de um app que hoje não desenha nada. É um projeto próprio, não uma
  feature: **está em [PLAN-STADIUMS.md](PLAN-STADIUMS.md)**, com fases próprias
  (`S1..S7`) e pré-requisito de este plano estar concluído até a Fase 12.
- **Nomes longos (11 caracteres).** O que a ferramenta faz é reescrever uma
  tabela de ponteiros de glifos e o texto codificado (`ABCDario*.csv` mapeia
  caractere → código). Os offsets do CARP são do executável **PC**; no PSX o
  equivalente está no `SLPM_870.56` ou nos `SELECT*.BIN`, e não foi localizado.
  **Adiado** até alguém querer: o custo é de engenharia reversa, não de código.
- **MultiTool.** Launcher de vários `.exe`. Não se aplica.
- **RA Maker.** O próprio autor marca como obsoleta e alpha. Aproveita-se a
  descrição do layout do `.RA`, não a ferramenta.

---

## 7. Fases

Cada fase termina com o `ctest` inteiro verde, incluindo `golden` e
`golden_gui`.

### Fase 8 — Camada ISO9660 (leitura)

Ler PVD, percorrer diretórios, expor `FileHandle` com leitura lógica
(descontando os 24+280 bytes por setor). Ferramenta de linha de comando
`we2002_iso ls|extract` em `tools/`, no mesmo espírito do `golden_tool`.

*Aceite:* listar as três imagens de teste; extrair `BIN/DAT2D.BIN` do dump
japonês e comparar com a amostra do CARP — deve dar **idêntico**, o teste vira
fixture. Extrair todos os arquivos das três imagens sem estourar extent.

*Risco:* baixo. Formato documentado, imagem sob a mão.

### Fase 9 — Codec LZSS

Portar `WECompress.cpp` (373 linhas) para `src/core/Lzss.cpp`. Trocar
`BYTE`/`DWORD`/`BOOL`/`ULONG` por `std::uint8_t`/`std::uint32_t`/`bool`/
`std::size_t`, tirar `stdafx.h`, trocar os buffers crus por `std::vector`.
Nada de MFC entra — o `FORBIDDEN` do `port_database.py` é o precedente do
critério.

*Aceite:* `decompress(bytes)` reproduz o resultado do protótipo Python em todos
os contêineres `BIN/*.BIN` das três imagens; `decompress(compress(x)) == x`
para cada bloco descomprimido dessas imagens. **Não** se exige
`compress(decompress(y)) == y`.

*Risco:* médio-baixo. Dois pontos de atenção no code review, os dois com caso
de teste próprio:

- `while(k3-- >= 0)` usa `k3` **assinado**; trocar por `unsigned` muda o teto do
  laço e o bug só aparece em blocos específicos.
- o ramo do opcode `0xC0..0xFE` (cópia literal em bloco) está **comentado** no
  compressor do CARP e **implementado** no descompressor. Manter assim: o
  descompressor precisa dele para ler os dados da Konami, o compressor não
  precisa gerá-lo. Não "completar" por simetria sem medir.

### Fase 10 — Contêiner `.BIN` e TIM

Parsear o cabeçalho de contêiner (8 bytes, a confirmar), a lista de entradas e
o `DATA_HEADER` de 32 bytes (`ID`, `VramX`, `VramY`, `width`, `height`,
`offset`, …). Decodificar 4 bpp e 8 bpp com CLUT. Exportar PNG.

*Aceite:* extrair todas as entradas de `DAT2D.BIN`, `DATSEL*.BIN`, `LOGO.BIN`,
`TITLE.BIN` e `CG*.BIN` das três imagens sem entrada órfã e sem estourar
buffer; largura × altura × bpp bate com o tamanho descomprimido em 100% das
entradas. Um punhado de PNGs conferidos a olho contra o Image Manager rodando
sob Wine.

*Risco:* **o mais alto do plano.** É o único ponto onde o formato ainda é
hipótese. Se o cabeçalho divergir entre arquivos, esta fase incha.

### Fase 11 — Gravação

Importar PNG/BMP indexado, validar dimensão e profundidade, recomprimir só as
entradas tocadas, remontar o contêiner, escrever no extent com ECC recalculado.
Política fit-or-fail da §5(a).

*Aceite:* abrir e salvar sem editar nada devolve a imagem **byte a byte
idêntica** (nenhuma entrada foi tocada, logo nada recomprime); trocar uma cor
de paleta e salvar altera exatamente os setores daquele arquivo; ECC dos
setores escritos valida contra um verificador independente. Boot manual no
RetroArch (instalado) com core PSX, olhando a tela alterada.

*Risco:* alto. É a primeira vez que o programa escreve fora dos offsets
conhecidos.

### Fase 12 — UI: navegador de assets

Aba nova (ou janela) com árvore do disco à esquerda, grade de imagens e grade
de paletas à direita, render ao cruzar as duas — o modelo do Image Manager do
BAT_WE, que resolve o problema real de "qual paleta vai com qual gráfico".
Exportar/importar pelo menu de contexto.

*Aceite:* `ctest -R ui_forms` continua valendo para os 6 formulários legados; o
formulário novo é escrito à mão (não vem do `ed.rc`) e fica fora do gerador —
documentar isso no `CLAUDE.md`, porque hoje "todo `.ui` é gerado" é regra.

*Risco:* baixo, fora a decisão de UI.

### Fase 13 — `T_NAME.BIN`

Renderizar nomes de time e estádio em bitmap indexado com a fonte do jogo,
montar as entradas e recomprimir. Reaproveita 8–11 inteiras.

*Aceite:* gerar um `T_NAME.BIN` do mesmo tamanho da original, inserir, e ver o
nome novo na tela de apresentação no emulador.

*Risco:* médio. A fonte precisa sair do próprio disco.

### Fase 14 — Áudio (`.RA` / VAG)

Índice do `.RA`, extração de VAG, decodificação ADPCM Sony → PCM, codificação
de volta, substituição in-place. Os `.RA` do disco têm 8–22 MB, com folga de
padding — substituição sem realocar é viável.

*Aceite:* extrair todos os clipes dos 15 `.RA`, converter VAG → WAV → VAG e
verificar que o VAG regerado é aceito; trocar um clipe e ouvir no emulador.

*Risco:* médio. ADPCM da Sony é bem documentado; o índice do `.RA` não.

---

## 8. Estratégia de teste sem oráculo

O `ed.exe` não tem nada disso, então o golden test não julga. O que substitui:

1. **Propriedades de round-trip** — `decompress(compress(x)) == x`,
   `png(entry)` → `import` → mesma entrada comprimida.
2. **Invariantes de formato** — soma dos extents cabe na imagem; nenhuma
   entrada cruza o fim do contêiner; `w*h*bpp/8` == tamanho descomprimido.
3. **Fixture cruzada** — o `DAT2D.BIN` do CARP, byte a byte igual ao do disco
   japonês, entra em `docs/samples/` como fixture de terceiro independente.
4. **Não-regressão** — `golden` e `golden_gui` verdes em toda fase. Se uma
   feature nova precisar tocar `Database`, a feature está errada.
5. **Boot manual** — RetroArch com core PSX, uma vez por fase que escreve.

---

## 9. Licença e crédito

O repositório **não tem `LICENSE`** e isso não muda. O código herdado do
Moriero/thyddralisk é todos-os-direitos-reservados; o do CARP é declarado
"uso no comercial, citar a Maximiliano Ducoli (CARP) como autor original".

Ao entrar código ou formato derivado das ferramentas dele, o
[NOTICE.md](../NOTICE.md) ganha uma seção com:

- Maximiliano Ducoli (CARP) — formatos `.BIN`/`.RA`, ferramentas de origem, URL
  e a condição não comercial;
- BAT_WE — Image Manager (2005), origem do modelo de UI imagem × paleta;
- autoria indefinida do `WECompress.cpp` (comentários em italiano, provável
  cena de 2002–2003), com a ressalva registrada.

Isso é **bloqueante para a Fase 9**: o `NOTICE.md` sai atualizado no mesmo
commit em que o primeiro arquivo derivado entra, não depois.

---

## 10. Ordem sugerida

8 → 9 → 10 são obrigatórias e sequenciais; nada existe sem elas. Da 11 em
diante dá para parar a qualquer momento com valor entregue:

- parar na **10** já dá um extrator/visualizador de assets, útil e sem risco de
  corromper disco;
- parar na **12** dá o editor gráfico completo, que é o maior salto de valor;
- **13** e **14** são independentes entre si e podem ser trocadas de ordem.

A Fase 7 (Windows) não conflita: só a Fase 12 mexe em Qt, e as camadas de 8 a
11 são portáveis por construção.
