# Ecossistema de ferramentas do Winning Eleven 2002 no GitHub

Levantamento feito em **2026-08-09** pela API de busca do GitHub (MCP), com as
variações `winning eleven 2002`, `WE2002`, `we 2002`, `winning eleven`,
`pro evolution soccer editor`, `ISS Pro Evolution`, `sofifa scraper`, além de
busca por código (`"Winning Eleven 2002"`, `we2002` em markdown) e varredura dos
repositórios de cada autor que apareceu mais de uma vez.

**O que o levantamento mostra.** Não existe um projeto de edição de WE2002 com
tração no GitHub — nenhum passa de **6 estrelas**, e a maioria tem 0 ou 1. O
conhecimento está concentrado em quatro pessoas (`Darkensses`, `Diego-Pino`,
`maxiducoli`/CARP, `zetaprog`), todas ligadas às comunidades hispano-americanas
**MexWE** e **ZonaWe**, e o GitHub delas é mais um depósito de binários e
tutoriais do que um projeto de software. Quase tudo é Windows-only (VB.NET, C#,
Delphi/Pascal, VB6) ou web (JS/React).

**Onde este repositório se encaixa.** Nenhum outro projeto encontrado edita a
**imagem de CD** diretamente com foco em portabilidade. Os que mexem em binário
ou atacam o **memory card** (`.MCR`, que é outro formato) ou atacam a **ISO por
arquivo** (TEX, VAG, RA). Os únicos que tocam no mesmo terreno que o
`newWe2002` são o upstream `thyddralisk/WE2002-editor-2.0` e a DLL do
`zetaprog`.

> Nada aqui foi baixado, clonado ou executado — o levantamento é só de
> metadados e README lidos pela API.

---

## 1. Edição de dados do jogo em binário (o mesmo terreno deste projeto)

| Repositório | Linguagem | ⭐ | Última atividade | Descrição |
|---|---|---|---|---|
| [thyddralisk/WE2002-editor-2.0](https://github.com/thyddralisk/WE2002-editor-2.0) | C++ | 1 | 2015 (código) | **O upstream deste repositório.** Editor MFC do Francesco Moriero (2002) com o import do SoFIFA acrescentado. Grava direto na imagem de CD. Ver [NOTICE.md](../NOTICE.md). |
| [aguilasa/new-we2002-editor](https://github.com/aguilasa/new-we2002-editor) | C++ | 0 | 2026-08 | **Este repositório.** Port Qt multiplataforma do editor acima. |
| [zetaprog/We2002-Data-Base-Manager](https://github.com/zetaprog/We2002-Data-Base-Manager) | VB.NET | 0 | 2026-05 | DLL de edição binária de save/memory card do WE2002 / ISS Pro Evolution 2. Lê e grava blocos de jogador de **12 bytes** com bit-packing, inversão de endian, números de camisa de clube e seleção, atributos (velocidade, aceleração, drible, técnica...), aparência e posição. O README documenta a lista de atributos — **é a fonte de terceiro mais próxima do nosso `Player::Decode()`/`Encode()`**. |
| [zetaprog/WE4-Binary-Editing-DLL](https://github.com/zetaprog/WE4-Binary-Editing-DLL) | VB.NET | 1 | 2026-05 | Mesma ideia, mas para **Winning Eleven 4 / ISS Pro Evolution** (PS1). Útil para comparar como o formato evoluiu entre gerações. |
| [zetaprog/Editor-de-Coordenadas-de-Banderas---WE2002](https://github.com/zetaprog/Editor-de-Coordenadas-de-Banderas---WE2002) | VB.NET | 0 | 2026-05 | Editor visual de **posição das bandeiras** no menu, com drag-and-drop e patch direto no binário. O README publica os offsets: seleções em `0x28D228` (650 bytes), Master League em `0x28D4B2` (320 bytes), estrutura de 10 bytes por bandeira (largura, altura, crop X/Y, pos X `UShort`, pos Y `Short`, extra, ID) e eixo Y invertido. **Offsets que o nosso `Offsets.hpp` não cobre.** |

## 2. Memory card (`.MCR`) — formato irmão, não o mesmo

O `.MCR` é o save do PlayStation, não a imagem de CD. A comunidade edita mais
por ali do que pela ISO, porque não exige regravar o disco.

| Repositório | Linguagem | ⭐ | Última atividade | Descrição |
|---|---|---|---|---|
| [zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1](https://github.com/zetaprog/Easy-Mcr-Winning-Eleven-2002-PS1) | JavaScript | 0 | 2026-05 | **O projeto ativo mais completo do lote.** Cria e edita jogadores, formações, atributos, aparências e treino no `.MCR`, com drag-and-drop, banco local de rostos, export para JSON e integração com Transfermarkt, SoFIFA, FMInside (até FM26) e PESMaster/eFootball. Converte estatísticas de **FC25** e de **PES6** para WE2002. Já vai na V4.2. |
| [Darkensses/mexwe-mcr](https://github.com/Darkensses/mexwe-mcr) | JavaScript | 6 | 2026-05 | **O repo de WE2002 com mais estrelas que existe.** App React/Node que faz scraping do SoFIFA e converte para `.MCR` usando as fórmulas do **PoliPoli**. Do time MexWE, com participação do Diego-Pino. MIT. Interessante como precedente direto do nosso import de SoFIFA (desligado). |
| [Darkensses/mexwe-mcr-api](https://github.com/Darkensses/mexwe-mcr-api) | JavaScript | 0 | 2020 | Servidor auxiliar que entrega o `.MCR` gerado pelo conversor acima. |
| [Darkensses/sofifa-pyscraper](https://github.com/Darkensses/sofifa-pyscraper) | Python | 10 | 2024 | O scraper de SoFIFA que sustenta o `mexwe-mcr`. Genérico, não é específico de WE2002. |
| [Darkensses/sofifa-v-scraper](https://github.com/Darkensses/sofifa-v-scraper) | V | 0 | 2019 | Reescrita experimental do scraper na linguagem V. |
| [Diego-Pino/Winning-Eleven-Memcard-Editor](https://github.com/Diego-Pino/Winning-Eleven-Memcard-Editor) | Python | 1 | 2026-07 | Script único (`Memcard-Editor.py`, 23 KB) de edição de memory card. A descrição diz "Python SOTN Memcard Editor" — provável adaptação do editor de *Symphony of the Night*. |
| [Diego-Pino/Winning-Eleven-2002-MCR-Database](https://github.com/Diego-Pino/Winning-Eleven-2002-MCR-Database) | — | 0 | 2020 | Coleção de `.MCR` prontos: jogadores, formações e stats. Dado, não ferramenta. |

## 3. Gráficos: TEX, TIM, TMD

O WE2002 empacota texturas num container `TEX` (comprimido) que contém `.TIM`
do PSX; os modelos 3D são `.TMD`. Nada disso é tocado pelo `ed.exe` nem pelo
port — é um eixo de edição inteiramente separado.

| Repositório | Linguagem | ⭐ | Última atividade | Descrição |
|---|---|---|---|---|
| [Darkensses/we2002-edition-tools](https://github.com/Darkensses/we2002-edition-tools) | JavaScript | 0 | 2022 | *"Ninguém documentava as ferramentas de edição do we2002, mas aqui você acha o código."* Três módulos: `compressor`, `decompressor` e `texbuilder`. Sem README. |
| [Darkensses/py-getWeTex](https://github.com/Darkensses/py-getWeTex) | Python | 1 | 2021 | Descomprime o `TEX` do WE2002 em arquivos `.TIM`. |
| [Darkensses/wetex-viewer](https://github.com/Darkensses/wetex-viewer) | JavaScript | 0 | 2022 | Visualizador de `TEX` em React. |
| [Darkensses/mexwezip](https://github.com/Darkensses/mexwezip) | JavaScript | 0 | 2022 | Utilitário de empacotamento do time MexWE. Sem README. |
| [Darkensses/we3d](https://github.com/Darkensses/we3d) | JavaScript | 3 | 2026-06 | **Visualizador e editor de vértices de `.TMD` no navegador**, com Three.js. Parser próprio (`TMDParser.v2.js`), arrasta vértice com o mouse e regrava só a seção de vértices no binário original, preservando cabeçalhos. Mesma filosofia de "preservar o que não entendo" que o nosso port aplica ao EDC/ECC. |
| [ramonpsx95/EASY-TEX-GENERATOR](https://github.com/ramonpsx95/EASY-TEX-GENERATOR) | VB6 | 0 | 2023 | Monta um `TEX` do WE2002 a partir de 5 texturas `.bmp` mais a textura `arbitro.bin`. |
| [Diego-Pino/we2002-TEX-2023-Zeta-Pino](https://github.com/Diego-Pino/we2002-TEX-2023-Zeta-Pino) | — | 0 | 2023 | Coleção de `TEX` para jogos de PlayStation. Dado. |
| [Diego-Pino/Winning-Eleven-2002-Texs-Kits](https://github.com/Diego-Pino/Winning-Eleven-2002-Texs-Kits) | — | 0 | 2020 | Uniformes (kits) em `TEX`. Dado. |
| [maxiducoli/GraphicsTools](https://github.com/maxiducoli/GraphicsTools) | C# | 0 | 2026-01 | Utilitários gráficos da suíte CARP. Sem README. |
| [maxiducoli/WE_TMD_Tools](https://github.com/maxiducoli/WE_TMD_Tools) | C# | 0 | 2026-04 | Extrator de `TMD` de **estádios** e criador de estádios a partir das peças extraídas. |
| [maxiducoli/Winning-Eleven-Image-Manager---by-BAT-2005-](https://github.com/maxiducoli/Winning-Eleven-Image-Manager---by-BAT-2005-) | Pascal | 0 | 2026-01 | Gerenciador de imagens escrito por *BAT_WE* em Delphi 7 por volta de 2005, portado para Delphi 12. |
| [maxiducoli/SinSala-BIN-2k24---by-CARP](https://github.com/maxiducoli/SinSala-BIN-2k24---by-CARP) | C# | 0 | 2026-01 | Editor dos `.BIN` que guardam gráficos e paletas (menus, escudos, bandeiras). |
| [saturnu/we2bmp](https://github.com/saturnu/we2bmp) | C | 0 | 2022 | Reinjetor de bitmap para Winning Eleven de **GameCube**. Outra plataforma, mesma família. |
| [saturnu/txsfix](https://github.com/saturnu/txsfix) | C | 0 | 2022 | Corretor de `TXS` do Winning Eleven 6 (GameCube). |

## 4. Áudio e ISO

| Repositório | Linguagem | ⭐ | Última atividade | Descrição |
|---|---|---|---|---|
| [maxiducoli/WE2002-MultiTool](https://github.com/maxiducoli/WE2002-MultiTool) | C# | 1 | 2026-01 | **Launcher da suíte CARP** — reúne num só frontend .NET/WinForms o RA Maker, o SinSala-BIN, WAV2VAG/VAG2WAV, extrator de VAG, criador de estádios e "La Pinta" (editor de pixel com paleta de 16 e 256 cores). O README é o melhor panorama de 20 anos de modding de WE2002 que apareceu na busca. Uso não comercial, atribuição a Maximiliano Ducoli (CARP). |
| [maxiducoli/Winning-Eleven-2002---RA-Maker](https://github.com/maxiducoli/Winning-Eleven-2002---RA-Maker) | C# | 0 | 2026-04 | Cria bancos de áudio `.RA` com narração personalizada a partir de clipes `.VAG`. |
| [maxiducoli/Winning-Eleven-VAG-editor](https://github.com/maxiducoli/Winning-Eleven-VAG-editor) | Pascal | 0 | 2026-01 | Troca `.VAG` direto na ISO ou dentro do container `RA`; converte WAV↔VAG. |
| [maxiducoli/WEVagExtractor](https://github.com/maxiducoli/WEVagExtractor) | C# | 0 | 2026-01 | Extrator de `.VAG` do WE2002 e de outras versões. |
| [maxiducoli/WECompressor](https://github.com/maxiducoli/WECompressor) | C++ | 0 | 2026-04 | Compressor/descompressor dos arquivos internos. Sem README. |
| [maxiducoli/Winning-Eleven-tools-by-CARP-TESTs-TOOLs-](https://github.com/maxiducoli/Winning-Eleven-tools-by-CARP-TESTs-TOOLs-) | C# | 0 | 2026-04 | Bancada de testes da suíte: `DecodeTest`, `TIMTools`, `GraphicsUtils`, `compressUtils`, `WECompress`, `WE Decompress 2k24`. |
| [maxiducoli/Winning-Eleven-ISO-protect---File-Extractor](https://github.com/maxiducoli/Winning-Eleven-ISO-protect---File-Extractor) | Pascal | 0 | 2026-01 | Extrai e reinsere arquivos na ISO do WE2002 e "protege" os modificados. **O ponto que mais interessa aqui**: é o mesmo problema de fronteira de setor MODE2/2352 que o nosso port enfrenta, resolvido por outro caminho. |
| [Diego-Pino/Winning-Eleven-2002-Audio-Remasterizado](https://github.com/Diego-Pino/Winning-Eleven-2002-Audio-Remasterizado) | — | 2 | 2022 | Pacote de áudio remasterizado. Dado. |
| [Diego-Pino/W2002J00](https://github.com/Diego-Pino/W2002J00) | — | 0 | 2025-01 | *"WE2002 sin audio público, repeticiones."* Dado. |

## 5. Nomes, texto e tradução

| Repositório | Linguagem | ⭐ | Última atividade | Descrição |
|---|---|---|---|---|
| [maxiducoli/T_NAME-Maker](https://github.com/maxiducoli/T_NAME-Maker) | C# | 0 | 2026-01 | Cria arquivos `T_NAME` do WE2002. |
| [maxiducoli/Winning-Eleven---Nombres-largos](https://github.com/maxiducoli/Winning-Eleven---Nombres-largos) | C# | 0 | 2026-01 | Permite nomes de time de até **11 caracteres** no menu principal — ou seja, quebra o limite que o editor original impõe. |
| [Diego-Pino/WE2002-Traductor-Jairo](https://github.com/Diego-Pino/WE2002-Traductor-Jairo) | — | 1 | 2025-10 | Macro VBA de Excel para tradução, atribuída a "Jairo". |
| [Diego-Pino/Jon-Kabira-Teams-Names-Konami](https://github.com/Diego-Pino/Jon-Kabira-Teams-Names-Konami) e [Jon-Kabira-CallNames](https://github.com/Diego-Pino/Jon-Kabira-CallNames) | — | 0 | 2025-07 | Nomes de time e de jogador na voz do narrador japonês Jon Kabira. Dado. |
| [DiegoMich/searchenko](https://github.com/DiegoMich/searchenko) | — | 0 | 2026-04 | *"Winning Eleven 2002 players search engine."* Só um README de 55 bytes — repositório vazio, ideia registrada. |

## 6. Bancos de dados e conversão de estatísticas

| Repositório | Linguagem | ⭐ | Última atividade | Descrição |
|---|---|---|---|---|
| [Diego-Pino/WinningEleven-2002-Database-Update-From-FIFA2020](https://github.com/Diego-Pino/WinningEleven-2002-Database-Update-From-FIFA2020) | — | 1 | 2025-10 | Planilha da base do WE2002 convertida do FIFA 2020, criada por **PoliPoli** (ZonaWe), com exemplos em pandas para ler o `mcr-db-to-mcr.xls` — a planilha de fórmulas que o `mexwe-mcr` reimplementou em JavaScript. **É a documentação mais direta da conversão FIFA→WE2002 que existe em aberto.** |
| [Diego-Pino/Archivo-BackUps](https://github.com/Diego-Pino/Archivo-BackUps) | — | 0 | 2025-08 | Manuais, mapas de AFS e documentação diversa da comunidade. |
| [Diego-Pino/Winning-Eleven-Pro-Evolution-Soccer-eFootball-Series](https://github.com/Diego-Pino/Winning-Eleven-Pro-Evolution-Soccer-eFootball-Series) | — | 0 | 2024 | Wiki informal da série inteira. |

## 7. Outras versões da série (contexto, não WE2002)

| Repositório | Linguagem | ⭐ | Descrição |
|---|---|---|---|
| [AlbioreGamera/JWE8-Player-Editor](https://github.com/AlbioreGamera/JWE8-Player-Editor) | C# | 0 | Editor de jogadores do *J.League Winning Eleven 8*. |
| [Nisto/we5ex](https://github.com/Nisto/we5ex) | Python | 1 | Extrai o sistema de arquivos interno e o áudio do *World Soccer: Winning Eleven 5*. |
| [Diego-Pino/PES3-WE7-Club-Team-Flag-Edit-Guide](https://github.com/Diego-Pino/PES3-WE7-Club-Team-Flag-Edit-Guide) | HTML | 0 | Guia de edição de bandeiras no PES3 / WE7. |
| [Diego-Pino/we7_Kits_Club](https://github.com/Diego-Pino/we7_Kits_Club) | HTML | 0 | Kits feitos com o editor do WE7. |
| [Diego-Pino/Winning-Eleven-9-Databases-2024](https://github.com/Diego-Pino/Winning-Eleven-9-Databases-2024) | — | 0 | Bases do WE9, temporada 2024. |
| [MarceloBristot/Winning-Eleven-Tactics-...-Traducao](https://github.com/MarceloBristot/Winning-Eleven-Tactics-European-Club-Soccer-Traducao) | — | 0 | Tradução para PT-BR do *WE Tactics — European Club Soccer* (PS2, 2004). Único projeto brasileiro da lista. |
| [the4chancup/pes-gameplay-editor](https://github.com/the4chancup/pes-gameplay-editor) | Python | 5 | Editor dos binários de `dt18` dos PES modernos. Comunidade separada, muito mais organizada. |
| [FVitor7/PES-EDITOR-PS2](https://github.com/FVitor7/PES-EDITOR-PS2) | Java | 6 | Editor de PES 2014 de PS2. |
| [EdgarOSR/SoFIFA-Scraper---Python](https://github.com/EdgarOSR/SoFIFA-Scraper---Python) | Python | 5 | Converte estatísticas do SoFIFA para **PES6** via site pes6.es. Mesma ideia do nosso import, outro jogo-alvo. |

## 8. Ferramentas genéricas de PSX que servem ao caso

Não mencionam WE2002, mas resolvem os problemas de formato que o projeto
encontra.

| Repositório | Linguagem | ⭐ | Descrição |
|---|---|---|---|
| [acemon33/psx_extractor_inserter](https://github.com/acemon33/psx_extractor_inserter) | C | 2 | Extrai e insere arquivos em imagem PSX **ISO Mode 2 / 2352 / Form 1** — exatamente o layout de setor descrito na seção de arquitetura do [CLAUDE.md](../CLAUDE.md). |
| [rodrigokiller/tim-studio](https://github.com/rodrigokiller/tim-studio) | TypeScript | 0 | Editor de `.TIM` com leitor de ISO/BIN e **reinserção com recálculo de EDC/ECC**. É o oposto da decisão do nosso port, que preserva o ECC inválido do original. |
| [zeroviim/IsoIdentifier](https://github.com/zeroviim/IsoIdentifier) | C# | 1 | Identifica informação por setor de ISO de PSX conforme a spec do no$psx. |
| [niemasd/GameDB-PSX](https://github.com/niemasd/GameDB-PSX) | — | — | Base de dados de títulos de PSX; foi onde a busca por código bateu em `SLPM-87056` e afins. |

## 9. Falsos positivos frequentes

Para não repetir busca: `winning eleven` como nome de repositório é usado por
dezenas de projetos sem nenhuma relação com o jogo — trabalhos de bootcamp
coreano, lojas em React, calculadoras, sites de bootcamp, um simulador de
futebol genérico ([chouqiu/FootBall-Simulator-Engine](https://github.com/chouqiu/FootBall-Simulator-Engine),
7 ⭐) e um sistema de recomendação de jogadores em ML
([Suwadith/Winning-Eleven-Scout...](https://github.com/Suwadith/Winning-Eleven-Scout-Evaluation-and-Analysis-to-Enhance-Football-Player-Recommendations-ML-Flask),
6 ⭐). O usuário `we2002/we2002` é uma conta de perfil, não uma ferramenta.

Também não existe **topic** `winning-eleven` no GitHub — `topic:winning-eleven`
devolve zero. As buscas que funcionam são por nome/descrição e por autor.

## 10. O que sobrou de fora do GitHub

Vale registrar o que a busca **não** encontra, porque explica os buracos acima:

- O **WE2002 Team Editor v0.99 do Obocaman** (o `make wte` deste repositório,
  ver [docs/PLAN-WTE-LAZARUS.md](/docs/PLAN-WTE-LAZARUS.md)) **não está no
  GitHub** sob nenhuma grafia. Binário C++Builder distribuído por fórum, como
  quase tudo de 2002.
- As fórmulas do **PoliPoli** circulam como planilha `.xls`, não como código.
- O grosso da comunidade vive em fórum e Facebook — o `mexwe-mcr` cita
  `zonawe.forosactivos.net`, `winningeleven-games.com` e um grupo de
  "WE2002 Rom Hacking" no Facebook.

---

## Como refazer este levantamento

```
mcp__github__search_repositories  "winning eleven 2002 editor"
mcp__github__search_repositories  "WE2002"
mcp__github__search_repositories  "winning eleven"           (sort: stars)
mcp__github__search_repositories  user:Darkensses | user:Diego-Pino
                                  | user:maxiducoli | user:zetaprog
mcp__github__search_code          "\"Winning Eleven 2002\" NOT is:archived"
```

A busca por código estoura o limite de tokens da ferramenta e é salva em
arquivo; extraia os repositórios com

```sh
grep -oE '"full_name":"[^"]+"' <arquivo> | sed 's/.*:"//;s/"//' | sort -u
```
