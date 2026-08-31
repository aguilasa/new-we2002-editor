# Paridade funcional — `ed.exe` (2002) × `newWe2002` (port Qt)

> **Para que serve este arquivo.** O [PLAN-LINUX.md](/docs/PLAN-LINUX.md) conta *como*
> o port foi feito, fase a fase. Este conta *o que* o original faz, item por
> item, e onde cada item foi parar no port — para que a validação futura seja
> uma conferência de lista, e não uma releitura de 8.456 linhas de MFC.
>
> Levantado em **2026-08-05** contra `legacy/mfc/` (os 375 `ON_*` dos seis
> diálogos) e contra `src/core/` + `src/app/` no estado do commit `2e3cd7e`.
>
> Nada aqui é plano de trabalho novo. É inventário e roteiro de conferência.

---

## 1. Como ler as tabelas

A coluna **Ev.** diz qual é a evidência que sustenta o item hoje. Não é opinião
sobre qualidade — é o tipo de prova que existe:

| Ev. | Significado | Como se refaz |
|---|---|---|
| **A** | Provado byte a byte contra o `ed.exe` | `ctest -R golden` / `golden_gui` |
| **B** | Coberto por teste unitário | `ctest -R core` |
| **C** | Conferido por leitura lado a lado legado × port | releitura |
| **D** | **Só existe no código; ninguém exercitou na tela** | §8 deste arquivo |
| **X** | Não portado, de propósito | — |

**A maior parte da UI está em C ou D.** Isso não é defeito escondido: os golden
tests provam que a *imagem gravada* é idêntica, e provam que a janela Qt
carregando e gravando não muda nada. O que eles não provam é que cada botão
individual da tela faz na tela o que o original fazia — porque eles só dirigem
dois controles (o combo de time e o `CMB_WRITE`). Esta é a lista do que falta
clicar.

Comandos:

```sh
ctest --preset debug                       # core, ui_forms, glossary
WE2002_GOLDEN_IMAGE=roms/golden-european-deluxe.bin ctest --test-dir build -R golden
WE2002_GOLDEN_MODE=gui WE2002_GOLDEN_IMAGE=... ctest --test-dir build -R golden_gui
DISPLAY=:98 ./build/src/app/newWe2002 /tmp/copia.bin
```

Sempre sobre **cópia** da imagem. Sempre no `DISPLAY=:98`.

### 1.1 O SoFIFA está desligado

Desde **2026-08-05**, por decisão: o import do SoFIFA é acréscimo do fork, não
faz parte do editor de 2002, é a área menos verificada do projeto e depende de
um site cujo layout de 2015 o raspador espera. Fica em último plano até a
paridade com o `ed.exe` estar conferida tela a tela.

O código continua inteiro, compilado e linkado — só ficou **inalcançável pela
janela**, com os controles em cinza (não escondidos: o formulário tem geometria
absoluta do `ed.rc` e não há layout Qt para fechar o vão, e a tela precisa
continuar comparável contra uma captura do `ed.exe`).

O interruptor é um só: `app::SOFIFA_ENABLED` em
[src/app/Features.hpp](../src/app/Features.hpp). Voltar para `true` reativa tudo.
O que ele desliga:

| O quê | Onde |
|---|---|
| `CMB_IMPFIFAWEB`, `CMB_IMPFIFATXT`, `CMB_EDITALLTXT` | `MainWindow::ApplySofifaSwitch()` |
| `CMB_SHOWEDITOPT` (as 4 checkboxes só alimentavam o "edit all") | idem |
| As 23 caixas `TXT_URL1..23` | idem, e os ramos de `TeamView.cpp` que as reabilitavam por time |
| `CMD_READ_URL` ("Import from URL") | `PlayerSkillsDialog` |
| Ler `SOFIFA attributes.txt` e `WE attributes conversion rules.txt` no startup | `OpenImage()` — some junto o popup de aviso quando faltam |

Não muda byte nenhum da imagem: nada disso é gravado no `.bin`.

**O que continua ligado de propósito: o `<imagem>_url.txt`.** Ele é lido no
`OpenImage()`/`OnReload()` e gravado dentro do `Database::Save()` — o
`OnWriteCD` do original já fazia as duas coisas (`legacy/mfc/edDlg.cpp:6207`), e
o `Save()` é código gerado a partir dele. Pular a leitura deixaria os 1.911
campos vazios e a gravação seguinte truncaria o arquivo do usuário para 1.911
linhas em branco. Conferido em 2026-08-05: sidecar de teste com 1.911 URLs,
gravação pela janela com o SoFIFA desligado, arquivo sai com o **mesmo md5**.

Conferido na tela em 2026-08-05 (`:98`): os quatro botões, as 23 caixas de URL e
o "Import from URL" aparecem em cinza; o resto do diálogo carrega normalmente.

---

## 2. Núcleo (`src/core/`)

### 2.1 Leitura e gravação da imagem

| Item | Original | Port | Ev. |
|---|---|---|---|
| Abrir `.bin` MODE2/2352 cru, ponteiro único, leitura curta não é erro | `CFile` | `CdImage` | B |
| Sempre modo binário | implícito no Windows | `std::ios::binary` explícito | B |
| Carregar tudo para memória | `carica_dabin()`, 696 linhas | `Database::Load()` | A |
| Gravar tudo de volta, in-place | `OnWriteCD()`, 663 linhas | `Database::Save()` | A |
| **Não** recalcular EDC/ECC | comportamento original | preservado | A |
| Saltos manuais de fronteira de setor (`_A`/`_B`/`_C`) | `if(i==40) Seek(...)` | idem, gerado verbatim | A |
| Aviso de tamanho ≠ 474.431.328 bytes, e carrega assim mesmo | `aprifilebin()` | `MainWindow::OpenImage()` | C |

**As 69 regiões** estão em `src/core/include/we2002/Offsets.hpp`, cada uma com o
nome legado em comentário (`// was OFS_NOMI_SQ1`).

Conferência mecânica já feita: `Load` e `Save` tocam o **mesmo** conjunto de 63
offsets, mais quatro que só o `Save` escreve — `OFS_FLAG_SHAPE_COPY_2..5`. O
disco guarda cinco cópias da tabela de formato de bandeira; o original também lê
só a primeira e grava as cinco (`OFS_BANDIERE_FORMA1` aparece 3× no legado, as
outras 2× cada). **Paridade confirmada.**

### 2.2 Regiões, por assunto

| Assunto | Offsets | Ev. |
|---|---|---|
| Nomes de time (6 slots) | `OFS_TEAM_NAME_1..6` + `_A`/`_B`/`_END` | A |
| Nome em kanji | `OFS_TEAM_NAME_KANJI`, `_A` | A |
| Nome em caixa mista (`nome_m` = *minuscolo*) | `OFS_TEAM_MIXED_CASE_NAME` | A |
| Abreviações (3) | `OFS_TEAM_ABBREV_1..3` | A |
| 7º e 8º nome de clube de ML | `OFS_ML_TEAM_NAME_7/8` | A |
| Barras de força | `OFS_TEAM_BARS`, `_A` | A |
| Cobradores e capitão | `OFS_KICKER` | A |
| Nomes de jogador (8 blocos) | `OFS_PLAYER_NAME..._8` | A |
| Nomes de jogador de ML (3) | `OFS_ML_PLAYER_NAME..._3` | A |
| Atributos de jogador (10 blocos) | `OFS_PLAYER_ATTR..._9` | A |
| Atributos de ML (3) | `OFS_ML_PLAYER_ATTR..._2` | A |
| Formato de bandeira (5 cópias) | `OFS_FLAG_SHAPE_COPY_1..5` | A |
| Cores de bandeira (+ o caso Senegal) | `OFS_FLAG_COLOURS`, `_A`, `_B`, `_SENEGAL` | A |
| Custos | `OFS_COST_NATIONAL`, `OFS_COST_NC` | A |
| Números de camisa | `OFS_SQUAD_NUMBERS_NATIONAL`, `_ML` | A |
| Formações predefinidas | `OFS_FORMATIONS`, `_A` | A |
| Links de ML e all-star | `OFS_LINK_ML`, `_ML1`, `_ML2` | A |
| Preview de uniforme | `OFS_KIT_PREVIEW`, `_A`, `_B`, `_C` | A |

### 2.3 Codificação

| Item | Original | Port | Ev. |
|---|---|---|---|
| Empacotar/desempacotar os 12 bytes de atributos | `codifica_carat()` / `decodifica()` — **nomes invertidos no original** | `Player::Decode()` / `Player::Encode()` | B |
| Números de camisa: 23 × 5 bits em 16 bytes | `struct NUMERI` com bitfields `DWORD` | `SquadNumbers` com `std::uint32_t` + `static_assert` | B |
| Shift-JIS ↔ ASCII | `kanjitoascii` / `asciitokanji` | `TextCodec` | A, B |
| Resolver link de ML (2 bytes → índice de jogador) | `trovaIDml()` | `ResolveMlLink()` | B |
| Custo do jogador (fórmula por posição, 8 ramos) | `CalcolaCostoGiocatore()` | `ComputePlayerCost()` | C |
| Reconstruir nomes das all-star a partir dos links | `nomiallstar()` | `Database::CopyAllStarNames()` | A |

`TestSquadNumbersLayout` fixa a posição de cada um dos 23 campos de bit;
`TestPlayerBitPacking` fecha o round-trip dos atributos; `TestTextCodec` o do
codec; `TestResolveMlLinkBounds` varre as 65.536 combinações de dois bytes.

### 2.4 SoFIFA (`src/core/Sofifa.cpp`) — **desligado, ver §1.1**

| Item | Original | Port | Ev. |
|---|---|---|---|
| Baixar a página do jogador | `myiotxt.cpp` (libcurl) | `FetchUrl()` | D |
| Raspar os atributos da página | `giocatore.cpp` | `FifaPlayer::UpdatePlayerFromURL()` | D |
| Jogador "dummy" (URL = `dummy`) | idem | `SetPlayerToDummy()` | D |
| Ler `SOFIFA attributes.txt` | `carica_SOFIFAFields()` | `SofifaRules::LoadFields()` | D |
| Ler `WE attributes conversion rules.txt` | `carica_SOFIFAConversionRules()` | `SofifaRules::LoadConversions()` | D |
| Converter FIFA → WE e aplicar no jogador | `editFromFIFA()` | `ApplyFifaToPlayer()` | D |
| Mapear posição FIFA → posição WE | idem | `SofifaRules::PositionFromFifa()` | D |
| Gravar números de camisa vindos do FIFA | idem | `SetPlayerNumbers()` | D |

Todos estes continuam compilados, mas hoje só um `app::SOFIFA_ENABLED = true`
chega até eles.

**Nenhum item de SoFIFA aparece nos golden tests** — o oráculo precisaria de
rede e de um site que não existe mais no formato de 2015. Esta é a área menos
verificada do projeto inteiro, e a §8.6 diz o que dá para conferir sem rede.

---

## 3. Diálogo principal (`IDD_ED_DIALOG` → `MainWindow`)

216 dos 375 `ON_*` do original estão aqui.

### 3.1 Abertura

| Comportamento | Original | Port | Ev. |
|---|---|---|---|
| `CFileDialog` já no `OnInitDialog`, antes da janela | `aprifilebin()` | `QFileDialog` em `OpenImage()` | C |
| Cancelar = "Impossible editing without CD image !" e não abre | idem | idem | D |
| Aviso de tamanho, mas carrega | idem | idem | C |
| Ler `<imagem>_url.txt` | `carica_url()` | `LoadUrls()` | C |
| Preencher o combo de times (`---`, 54 Nation, 9 All-star, 32 ML, ML default) | `OnInitDialog` | `FillTeamCombo()` | A |
| Rótulos dos 16 botões de formação | `aggiornaNtatt()` | `RefreshPresetButtons()` | D |
| Quatro checkboxes de "edit options" começam ligados | `OnInitDialog` | `edit_opt_{}` | C |
| Aceitar caminho da imagem por argumento | **não existia** | acréscimo, para o `golden_gui` | A |

### 3.2 Seleção de time — `CMB_TEAM`

`OnSelezioneSquadraV()` (1.030 linhas) → `OnTeamSelected()` + `ShowNationalOrAllStar` / `ShowMlClub` / `ShowMlDefault` / `ClearTeamForm`.

O índice do combo é o `id` do original e todo handler ramifica nele:

| `id` | Significado |
|---|---|
| 0 | nada selecionado — formulário limpo |
| 1..63 | seleção nacional / all-star → `teams[id-1]` |
| 55, 56 | as duas all-star: elenco vem por link, não por aritmética |
| 64..95 | clube de Master League → `ml_teams[id-64]` |
| 96 | o template "Master League (default)" |

| Comportamento por ramo | Ev. |
|---|---|
| Nacional: 6 nomes, kanji, caixa mista, 3 abreviações, 5 barras, 10 papéis + 20 coordenadas, 23 nomes de jogador, 23 URLs, 23 números, 6 combos de cobrador com os 11 titulares | A (carga), D (cada campo) |
| All-star (55/56): idem, mas elenco por link e **URLs desabilitadas** | D |
| Clube de ML: mais os dois nomes extras (`TXT_ML_EXTRA_NAME1/2`) e seus rótulos, visíveis só aqui | D |
| ML default (96): nomes "---" e barras "-", tudo desabilitado; só elenco e formação | D |
| Rótulos `(n)` de comprimento máximo por slot, tirados das tabelas por time | D |
| `setMaxLength` por slot, idem | D |
| Nada selecionado: limpa tudo | D |

Diferença de mecânica registrada: o original terminava chamando
`OnSelchangeTat2..11` à mão porque `SetCurSel` não dispara `CBN_SELCHANGE`; no
Qt `setCurrentIndex` dispara, então a carga usa `QSignalBlocker` e repinta as
legendas explicitamente. Efeito líquido igual — é o que o `golden_gui` prova.

### 3.3 Nomes do time

| Controle | Gatilho | Efeito | Port | Ev. |
|---|---|---|---|---|
| `TXT_TEAM_NAME1..6` | killfocus | grava `names[0..5]` | `OnTeamNameEdited(slot)` | A (slot 1), D |
| `TXT_TEAM_NAME_KANJI` | killfocus | grava `kanji_name` | `OnKanjiNameEdited()` | D |
| `TXT_TEAM_NAME_MIXED` | killfocus | grava `mixed_case_name` | `OnMixedCaseNameEdited()` | D |
| `TXT_TEAM_ABBREV1..3` | killfocus | grava `abbreviations[0..2]` | `OnAbbreviationEdited(slot)` | D |
| `TXT_ML_EXTRA_NAME1/2` | killfocus | grava `names[6]`/`names[7]` | `OnMlExtraNameEdited(slot)` | D |
| `CMD_COPY_TEAM_NAMES` | clique | espalha o nome 1 nos outros slots, truncando por tabela; deriva abreviações, caixa mista e kanji | `OnCopyTeamNames()` | D |

Quirk do original preservado no `OnCopyTeamNames`: o comprimento do slot kanji é
lido na linha `id-64` para clubes de ML e `id-1` para o resto — inclusive para os
outros cinco nomes, que usam `id-1` sempre. O rótulo acima da caixa promete um
comprimento e a cópia entrega outro. **Reproduzido de propósito.**

### 3.4 Barras de força

| Controle | Gatilho | Efeito | Port | Ev. |
|---|---|---|---|---|
| `TXT_BAR_OFF/DEF/POW/SPE/TEC` | killfocus | grava `bar_attack/defence/power/speed/technique` | `OnBarEdited(bar)` | D |
| — | — | 1 dígito, só números (`ES_NUMBER`) | `InitLimits()` | D |

### 3.5 Cobradores e capitão

| Controle | Gatilho | Efeito | Port | Ev. |
|---|---|---|---|---|
| `CMB_KICK_LONG_FK` | **killfocus do combo** | `kick_long_fk` | `OnKickerChanged(0)` via `eventFilter` | D |
| `CMB_KICK_SHORT_FK` | idem | `kick_short_fk` | `OnKickerChanged(1)` | D |
| `CMB_KICK_LEFT_CORNER` | idem | `kick_left_corner` | `OnKickerChanged(2)` | D |
| `CMB_KICK_RIGHT_CORNER` | idem | `kick_right_corner` | `OnKickerChanged(3)` | D |
| `CMB_KICK_PENALTY` | idem | `kick_penalty` | `OnKickerChanged(4)` | D |
| `CMB_CAPTAIN` | idem | `captain` | `OnKickerChanged(5)` | D |

A ordem dos seis é load-bearing: é a ordem em que o handler indexa e a ordem dos
campos em `Team`/`MlTeam`. **Commit em `FocusOut`, não em mudança de seleção** —
o original usava `CBN_KILLFOCUS`, e é por isso que navegar a lista com as setas
não grava **na hora**. Grava depois, quando o foco sai: medido na §8.3, três
`Down` e um `Escape` levam `kick_long_fk` de 3 a 6 no `ed.exe`. O que o
`Escape` decide é qual valor chega ao killfocus, e aí os dois frameworks
divergiam — no MFC as setas movem o `CurSel` do próprio combo e o `Escape` só
fecha a lista, no Qt elas movem a linha corrente da *view* e o `Escape`
desfaz. O port intercepta o `Escape` no popup para manter o item navegado
([CORR-WTE-125](/docs/tasks/CORR-WTE-125.md)) — nos **dezesseis** combos do
diálogo principal que gravam assim, porque os dez de papel da §3.7 usam o mesmo
`FocusOut` ([CORR-WTE-127](/docs/tasks/CORR-WTE-127.md)). Os dez combos de
papel do `DefaultTacticsDialog` divergiam igual e têm filtro próprio
([CORR-WTE-134](/docs/tasks/CORR-WTE-134.md)) — **vinte e seis ao todo**.

Lembrete permanente: `Load` lê os dois primeiros cobradores de ML **trocados** e
`Save` grava na ordem declarada, então toda gravação troca o par. Bug do
original, reproduzido; ver Fase 3 do PLAN-LINUX.

### 3.6 Elenco (23 linhas)

| Controle | Gatilho | Efeito | Port | Ev. |
|---|---|---|---|---|
| `TXT_PLAYER1..23` | **nenhum** | só exibe o nome — `ES_READONLY` no `.rc` | `readOnly` no `.ui`, só `setText` | C |
| `TXT_NUM1..23` | killfocus | número de camisa; nacional clampa em 32 e escreve nos 5 bits + no `number` do jogador; ML grava `raw_numbers` | `OnSquadNumberEdited(slot)` | D |
| `TXT_URL1..23` | `EN_CHANGE` | grava `players[].url` | `OnPlayerUrlEdited(slot)` em `textEdited` — **em cinza, §1.1** | X |
| `CMD_SKILLS1..23` | clique | abre o diálogo de atributos | `OnPlayerSkills(slot)` | D |
| `CMD_SWAP1..23` | clique | abre o seletor de jogador | `OnPlayerSwap(slot)` | D |

> **Confirmado nesta análise:** as 23 caixas de nome de jogador são
> `ES_READONLY` nas 23 linhas do `ed.rc`, e é por isso que o original não tem
> `ON_EN_KILLFOCUS` para `TXT_GIOC*`. O `tools/rc2ui.py` traduz o estilo para
> `readOnly` no `.ui`, então o port se comporta igual. Quem edita nome de
> jogador é o diálogo de atributos.

### 3.7 Táticas

Dez slots (o 1 é o goleiro e não tem posição editável — daí a numeração 2..11 do
`.rc` virar índice 0..9 no port).

| Controle | Gatilho | Efeito | Port | Ev. |
|---|---|---|---|---|
| `CMB_SLOT_ROLE2..11` | selchange | repinta a legenda do botão no campinho | `OnRoleShown(slot)` | D |
| `CMB_SLOT_ROLE2..11` | killfocus | grava `raw_formation[0..9]` (papel + 2) | `OnRoleCommitted(slot)` | D |
| `CMB_SLOT_ROLE2..11` | `Escape` no popup | mantém o item navegado, para o killfocus gravá-lo | `eventFilter` na `view()` | D |
| `TXT_SLOT_X2..11` | change | move o marcador no campinho | `OnSlotMoved(slot)` | D |
| `TXT_SLOT_X2..11` | killfocus | clampa 0..48 e grava `raw_formation[10..19]` | `OnSlotXCommitted(slot)` | D |
| `TXT_SLOT_Y2..11` | change | move o marcador | `OnSlotMoved(slot)` | D |
| `TXT_SLOT_Y2..11` | killfocus | clampa 0..112 e grava `raw_formation[20..29]` | `OnSlotYCommitted(slot)` | D |
| `CMD_TACT1..16` | clique | aplica a formação predefinida `k` no time selecionado | `ApplyPresetFormation(k)` | D |
| `CMD_SLOT1..10` | — | são os marcadores; sem handler | posicionados por `PitchPosition()` | D |

Constantes do campinho preservadas do original (`TXMIN/TXMAX/TYMIN/TYMAX/BTW/BTH/TCORRX/TCORRY`) em `MainWindow.hpp`.

Os `TXT_SLOT_*` usam `textChanged`, **não** `textEdited`, porque no original o
`EN_CHANGE` dispara também no `SetWindowText` da carga — é o que reposiciona os
marcadores ao trocar de time. Não "otimizar".

### 3.8 Comandos

| Botão | Original | Efeito | Port | Ev. |
|---|---|---|---|---|
| `CMB_WRITE` | `OnWriteCD()` | grava a imagem inteira **e o `<imagem>_url.txt`** | `OnWriteCd()` → `Database::Save()` | A |
| `CMB_RELOAD` | `OnReload()` | recarrega do disco e redesenha | `OnReload()` | D |
| `CMD_DEFAULT_NUMBERS` | `OnNumeriDefault()` | copia os números do time para o campo `number` de cada jogador, 64 times × 23 | `OnDefaultNumbers()` | D |
| `CMD_UPDATE_COSTS` | `OnCalcolaCostiML()` | recalcula o custo dos 1.911 jogadores | `OnRecomputeCosts()` | D |
| `CMD_SORT_RESERVES` | `OnOrdinaPanchina()` | ordena as 12 reservas por posição, goleiro por último — **botão invisível** (ver abaixo) | `OnSortReserves()` | D |
| `CMD_FLAG_KIT` | `OnButtgraf()` | abre bandeira/uniformes do time selecionado | `OnFlagKitPreview()` | D |
| `CMD_EDIT_PRESETS` | `OnTattPredef()` | abre as 16 formações predefinidas | `OnPresetTactics()` | D |
| `CMB_SHOWEDITOPT` | `OnEditOptForm()` | abre as opções de "edit all" | `OnEditOptions()` — **em cinza, §1.1** | X |
| `CMB_EDITALLLOOK` | `OnEditAllPlayersLook()` | aplica `defaultlook.txt` a todos os elencos | `OnEditAllPlayersLook()` | D |
| `CMB_EDITALLBARS` | `OnEditAllBars()` | recalcula as 5 barras de 56 seleções + 32 clubes a partir do onze inicial | `OnEditAllBars()` | D |
| `IDC_BUTTON1` / `IDC_BUTTON2` | `OnImporta` / `OnEsporta` | importar/exportar time `.2002` | **não portado** | X |
| `CMD_IMP_TOT` / `CMD_ESP_TOT` | `OnImportaTot` / `OnEsportaTot` | importar/exportar tudo `.tt2002` | **não portado** | X |

> **Confirmado nesta análise: o botão "sort reserve" é invisível nos dois.**
> `ed.rc` declara `CMD_CALCFORZA2` com `NOT WS_VISIBLE`; o `rc2ui.py` traduziu
> isso para `visible=false` no `.ui`, e é o único controle do diálogo principal
> invisível que não seja um dos cinco campos extras de ML (esses o
> `OnTeamSelected` mostra em runtime). Ou seja: `OnOrdinaPanchina` /
> `OnSortReserves` é código vivo com botão inalcançável nos dois programas.
> Para exercitá-lo (§8.9) é preciso tornar o botão visível numa build de teste
> — **não commitar essa mudança**, ela quebraria a fidelidade e o `ctest -R
> ui_forms`.

Detalhes que a validação deve respeitar:

- `OnSortReserves` reproduz o *bubble sort* torto do original (o índice externo
  também avança a base). A ordem resultante é a que os saves dos usuários já
  têm — não é para consertar.
- Times por link (ML e all-star) reordenam os **bytes de link**, não os registros
  de jogador.
- Se sobrar exatamente um goleiro, as duas últimas posições trocam.
- `OnEditAllBars` deixa as sete seleções clássicas (57..63) de fora, como o
  original.
- `OnEditAllPlayersLook` lê `defaultlook.txt` em **cp1252** (tem um `0x92` em
  "Costa d'Avorio"); campo vazio quer dizer "não mexer".

### 3.9 SoFIFA no diálogo principal — **desligado, ver §1.1**

| Botão | Original | Efeito | Port | Ev. |
|---|---|---|---|---|
| `CMB_IMPFIFAWEB` | `OnImportSoFIFAWeb()` | uma requisição por jogador com URL; grava o cache `<imagem>_SOFIFAdb.txt` | `OnImportSofifaWeb()` (+ `QProgressDialog` com "Stop") | D |
| `CMB_IMPFIFATXT` | `OnImportSoFIFATxt()` | recarrega o cache do `.txt` | `OnImportSofifaTxt()` | D |
| `CMB_EDITALLTXT` | `OnEditAllFromFIFA()` | aplica os dados raspados em todos os jogadores, respeitando as 4 opções | `OnEditAllFromFifa()` | D |

Acréscimo do port: a barra de progresso cancelável. O original bloqueava a
janela por 1.911 requisições sem feedback nenhum.

---

## 4. Sub-diálogos

### 4.1 `carattDlg` → `PlayerSkillsDialog` (32 `ON_*`)

Atributos de **um** jogador.

| Grupo | Controles | Faixa | Ev. |
|---|---|---|---|
| Texto | nome (10 chars) | — | D |
| Numéricos com faixa própria | altura 155..210, idade 15..46, número 1..32 | clampa e reescreve a caixa | D |
| Custo | `TXT_COST` | **sem clamp**, e limitado a 2 caracteres | D |
| 16 habilidades | acceleration, aggression, attack, defence, dribbling, swerve, jump, strength, passing, shot_accuracy, shot_power, stamina, reflexes, technique, heading, speed | clampa 12..19 | D |
| 10 combos | position, skin, hair style/colour, beard style/colour, build, boots, foot, out_of_position | listas fixas | D |
| Botão | `CMD_READ_URL` — importa este jogador do SoFIFA ignorando as opções de "edit all" | **em cinza, §1.1** | X |

> **Confirmado nesta análise:** o limite de 2 caracteres em `TXT_COST` e a
> ausência de limite em `TXT_JUMP` e `TXT_NUMBER` **são do original**
> (`carattDlg.cpp:226-244`: há `SetLimitText` para 19 caixas e o custo é uma
> delas, com 2). O port copia isso exatamente. Parece bug — é fidelidade.

Diferença de mecânica: os 10 combos gravavam em `CBN_KILLFOCUS`; o port grava em
`currentIndexChanged` protegido por `hasFocus()`. Sem caminho de "Cancel" no
diálogo, o efeito é o mesmo — mas é item de conferência manual (§8.4).

### 4.2 `selezDlg` → `PlayerSelectDialog` (8 `ON_*`)

Escolher um jogador para ocupar um slot.

| Controle | Efeito | Ev. |
|---|---|---|
| `LIST_TEAMS` | 54 nacionais + 9 all-star + "- ML (non contacted) " (o pool de 462 livres) | D |
| `LIST_PLAYERS` | nomes; para quem tem URL, o slug do SoFIFA depois de `\|` | D |
| duplo clique / `IDC_BUTTON1` | confirma | D |
| `CHK_ML` | alterna "link" × "skill" — só aparece para times por link | D |
| `CHK_COMPLETE_SWAP` | "complete substitution" (troca) × "incomplete" (duplica) | D |
| `CHK_LK_DEF` / `CHK_LK_NDEF` | mutuamente exclusivos: nacionalidade padrão do agente livre × a escolhida no combo | D |
| `CMB_NATIONALITY` | só os times cujo `START_LINK` alcança o jogador dentro de 255 | D |
| rótulo | `"n° (nazionality t - NOME )"` | D |

Regra de montagem do link: contratado → `(time, posição no elenco)`; livre com
nacionalidade padrão → `(time do run, posição - início + 23)`; livre com
nacionalidade escolhida → `(código escolhido, linha - START_LINK + 23)`.

Depois de trocar num slot all-star, `CopyAllStarNames()` é chamado — o original
fazia o mesmo.

### 4.3 `tattDlg` → `DefaultTacticsDialog` (64 `ON_*`)

As 16 formações predefinidas (as mesmas que os `CMD_TACT1..16` aplicam).

| Controle | Efeito | Ev. |
|---|---|---|
| `CMB_FORMATION` | escolhe qual das 16 editar | D |
| `TXT_FORMATION_NAME` | renomeia (6 chars) e atualiza o combo | D |
| 10 combos de papel + 20 coordenadas | mesma mecânica do diálogo principal | D |
| campinho com 10 marcadores | idem | D |
| `CMD_IMP` / `CMD_EXP` | importa/exporta `.t2002` | D |

Formato `.t2002`: magic, **4 bytes de vptr** (o original gravava a imagem de
memória de uma classe com destrutor virtual), `nome[7]`, `ruoli[11]`, `x[10]`,
`y[10]`, 2 de padding — 44 bytes. O port grava zeros no vptr e ignora na
leitura. Arquivos antigos continuam legíveis.

> **Os 4 bytes estão certos, e o `Debug/ed.exe` é que exporta errado.** O
> formato é de **52 bytes** (`8 + sizeof(tattica)` com vptr de 4), e é o que o
> import do original valida — `tattDlg.cpp:701` compara `GetLength()` com um
> **52** literal. O `ed.exe` deste repositório é **x86-64**, onde o vptr vira 8
> e `sizeof(tattica)` vai a 48: ele exporta 56 bytes e **recusa o próprio
> arquivo**. Defeito de recompilação do oráculo, não do formato. O `ed.exe`
> **aceita** o arquivo de 52 bytes do port — medido em
> [CORR-WTE-132](/docs/tasks/CORR-WTE-132.md).
>
> **Mas aceitar não é ler direito.** Ele passa na conferência de tamanho e
> decodifica com o vptr de 8 bytes, 4 adiante do lugar certo: importando o
> mesmo arquivo, o port grava `PARIMP` no nome do preset e o `ed.exe` grava
> `MP` seguido de bytes de papel. Medido na
> [CORR-WTE-135](/docs/tasks/CORR-WTE-135.md), com controle positivo dos dois
> lados; a §8.7 traz as faixas.

### 4.4 `graf` → `FlagKitDialog` (50 `ON_*`)

Bandeira e os dois uniformes do time selecionado.

| Controle | Efeito | Ev. |
|---|---|---|
| `TXT_FLAG_STYLE` | formato da bandeira (2 dígitos) | D |
| `TXT_FLAG_COL1..15` | 15 cores, teto 65535 | D |
| `TXT_KIT1_COL1..14` / `TXT_KIT2_COL1..14` | 14 cores por uniforme — as palavras 0 e 1 dos 16 não são expostas | D |
| `CMD_IMPORT_FLAG` / `CMD_EXPORT_FLAG` | `.b2002` (magic `f.m.band` + estilo + 16 words) | D |
| `CMD_IMPORT_KIT1/2` / `CMD_EXPORT_KIT1/2` | `.m2002` (magic `f.m.magl` + 16 words) | D |

Teste único de "tem bandeira própria" — ver §6.

O original copiava os valores para o diálogo e de volta depois do `DoModal()`,
inclusive quando fechado com ESC; o port edita por referência. Efeito idêntico:
não existe caminho de cancelamento nos dois.

### 4.5 `editOptForm` → `EditOptionsDialog` (4 `ON_*`)

Quatro checkboxes que o `CMB_EDITALLTXT` consulta: nomes, idade/altura/peso/pé,
características, números de camisa. Todos começam ligados. O port lê os quatro de
volta ao fechar, independentemente de como fechou — o original gravava a cada
clique, mesmo efeito.

---

## 5. Mapa de handlers, por família

375 macros `ON_*` no legado → 34 métodos indexados no port.

| Família do original | Qtd. | Port | Ev. |
|---|---|---|---|
| `OnCarat1..23` | 23 | `OnPlayerSkills(int)` | D |
| `OnSost1..23` | 23 | `OnPlayerSwap(int)` | D |
| `OnKillfocusNum1..23` | 23 | `OnSquadNumberEdited(int)` | D |
| `OnChangeURL1..23` | 23 | `OnPlayerUrlEdited(int)` | D |
| `OnSelchangeTat2..11` | 10 | `OnRoleShown(int)` | D |
| `OnKillfocusTat2..11` | 10 | `OnRoleCommitted(int)` | D |
| `OnChangeTatx/Taty2..11` | 20 | `OnSlotMoved(int)` | D |
| `OnKillfocusTatx2..11` | 10 | `OnSlotXCommitted(int)` | D |
| `OnKillfocusTaty2..11` | 10 | `OnSlotYCommitted(int)` | D |
| `On451a..On532b` | 16 | `ApplyPresetFormation(int)` | D |
| `OnKillfocusNsquad1..6` | 6 | `OnTeamNameEdited(int)` | A/D |
| `OnKillfocusNsquadA1..3` | 3 | `OnAbbreviationEdited(int)` | D |
| `OnKillfocusNomiml1..2` | 2 | `OnMlExtraNameEdited(int)` | D |
| `OnKillfocusBar*` | 5 | `OnBarEdited(int)` | D |
| `OnKillfocusKik*` | 6 | `OnKickerChanged(int)` | D |
| `carattDlg` killfocus de habilidade | 16 | `BindSkill()` | D |
| `carattDlg` killfocus de combo | 10 | `BindChoice()` | D |
| `tattDlg` (papéis + coordenadas) | 60 | métodos indexados do diálogo | D |
| `graf` (15 + 14 + 14 cores) | 43 | lambdas indexadas | D |
| avulsos (1 para 1) | ~89 | ver §3.8, §3.9 e §4 | — |

---

## 6. Divergências deliberadas

Cinco já registradas nas fases, mais uma levantada agora. **Nenhuma altera os
bytes gravados na imagem** — as quatro primeiras porque não tocam regiões de
disco no fluxo dos golden tests, a última porque só afeta o arquivo lateral.

| # | O que o original fazia | O que o port faz | Por quê |
|---|---|---|---|
| 1 | Lê e grava 16 bytes além do fim de `squad_nazall[63]` (slot 64) | dá ao array os 64 slots que o disco tem e preserva o que estava lá | reproduzir seria reproduzir UB dependente de linker; é a faixa `405724..405739`, a **única** tolerada pelo `golden_check.sh` |
| 2 | `editFromFIFA` fechava com `costo = CalcolaCostoGiocatore(i)` com `i` sobrando do laço — sempre 8 | usa o índice do próprio jogador | preço do jogador 8 para todo mundo era claramente erro; `CMD_UPDATE_COSTS` recalcula tudo de qualquer jeito |
| 3 | `OnOrdinaPanchina` escrevia `auxlk[1]`/`auxlk[2]` num `char[2]` | `std::swap` | mesmo efeito sem sair do array |
| 4 | ~~Nunca gravava o `<imagem>_url.txt`~~ — **registro errado, corrigido em 2026-08-05**: `OnWriteCD` grava o sidecar desde sempre (`legacy/mfc/edDlg.cpp:6207-6214`) | o `Database::Save()` gerado grava igual; o `MainWindow::SaveUrls()` que a Fase 5 acrescentou só reescreve o mesmo arquivo com o mesmo conteúdo, e está desligado junto com o resto do SoFIFA | não havia divergência. A Fase 5 do PLAN-LINUX registrou o contrário e foi corrigida |
| 5 | `graf` tinha **dois** testes de "tem bandeira própria" que discordavam na borda (56) | um só: `id>0 && id!=69 && id!=86 && (id<56 \|\| id>63)` | 56 é a World All-Stars, que também não tem bandeira própria |
| 6 | `EN_CHANGE` das 23 caixas de URL dispara também no `SetWindowText` da carga, então **trocar de time regravava a URL** — e para as all-star (55/56) escrevia a URL do jogador ligado por link no jogador do slot aritmético, que é outro | `textEdited`: só grava quando o usuário digita | levantado em 2026-08-05. Invisível no original porque ele nunca salvava o arquivo de URLs; no port, que salva, reproduzir isso corromperia o `_url.txt` ao navegar |

---

## 7. O que não foi portado

| Item | Original | Motivo |
|---|---|---|
| `OnEsporta` / `OnImporta` (time `.2002`) | `IDC_BUTTON2` / `IDC_BUTTON1` | os `PUSHBUTTON` estão **comentados** em `ed.rc:347,348`; o formato é `sizeof(squadra)` cru do MSVC 32-bit, com padding |
| `OnEsportaTot` / `OnImportaTot` (`.tt2002`) | `CMD_ESP_TOT` / `CMD_IMP_TOT` | idem, `ed.rc:368,369` |
| Item "About" no menu de sistema | `OnSysCommand` + `CAboutDlg` | `QDialog` não tem menu de sistema; a caixa não editava nada |
| Ícone desenhado com a janela minimizada | `OnPaint` | sem equivalente, não faz falta |
| `Return` fecha o editor **(diálogo principal)** | `IDOK` implícito do `CDialog`, com `CanExit()` sempre `TRUE` | no Qt, `Return` acionaria um dos 86 botões (um deles aplica formação!). O `rc2ui.py` emite `autoDefault=false`; hoje `Return` **não faz nada** ali, que é mais seguro que os dois comportamentos. `Escape` fecha, como nos dois. **Vale só para o `MainWindow`:** o `DefaultTacticsDialog` trata `Return` e confirma, porque lá o botão de confirmação é `NOT WS_VISIBLE` e sem isso o diálogo não teria saída (§8.7, [CORR-WTE-131](/docs/tasks/CORR-WTE-131.md)) |
| Pacote de distribuição (AppImage/Flatpak) | — | decisão da Fase 6 |

---

## 8. Roteiro de validação manual

O que os golden tests não alcançam. Cada bloco é independente; marque conforme
for fazendo. **Sempre sobre cópia**, sempre no `:98`.

```sh
cp roms/golden-european-deluxe.bin /tmp/claude-*/scratchpad/v.bin
DISPLAY=:98 ./build/src/app/newWe2002 /tmp/.../v.bin
```

Para cada bloco, o critério de aprovação é o mesmo: **fazer a mesma coisa no
`ed.exe` sob Wine e no port, gravar as duas cópias e comparar com
`tools/golden_compare.py`.** Divergência esperada: só `405724..405739`.

### 8.1 Nomes e abreviações

**Conferido em 2026-08-28** pela [PAR-TASK-01](/docs/tasks/PAR-TASK-01.md), na
`ptbr-remaster.bin`, com o `golden_check.sh` em modo `gui`. As seis corridas
saíram `OK: identico ao oraculo, exceto o slot 64 conhecido (405724..405739)`.

**Os seis roteiros estão em `tools/par/`**, um por corrida, e cada item abaixo
nomeia o seu. Cada arquivo é o trecho de shell que os **dois** hooks recebem
sem alteração — `GOLDEN_EDIT` no `golden_run.sh` (o `ed.exe`) e
`GOLDEN_GUI_EDIT` no `golden_gui.sh` (o port) —, porque os dois exportam
`$MAIN` e definem `dlu_x`/`dlu_y` com a mesma conversão do `ed.rc`. As faixas
abaixo são as do **controle positivo** (a cópia gravada contra a imagem
original), remedidas em 2026-08-28 a partir dos arquivos versionados; as cinco
não-idempotências conhecidas (`OFS_PLAYER_NAME_7+471`, três de
`OFS_PLAYER_ATTR_8`, `OFS_KICKER+384`) aparecem em todas e não são contadas.

- [x] Editar os 6 slots de nome de uma seleção; conferir que o `(n)` de cada
      rótulo bate com o truncamento real — **6 faixas, 7 bytes cada**, contra o
      `(7)` que os seis rótulos mostram no `Nation 1 - Ireland`
      (`tools/par/8.1-nomes-6-slots.sh`)
- [x] Editar kanji e caixa mista — `OFS_TEAM_NAME_KANJI_A` sai com **span 13 /
      diff 7** (a codificação ocupa mais que os caracteres digitados) e
      `OFS_TEAM_MIXED_CASE_NAME` com **7 bytes**
      (`tools/par/8.1-kanji-e-mista.sh`)
- [x] Editar as 3 abreviações — **3 bytes cada** em `OFS_TEAM_ABBREV_1/_2/_3`,
      o `setMaxLength(3)` fixo em código, não por tabela
      (`tools/par/8.1-abreviacoes.sh`)
- [x] `CMD_COPY_TEAM_NAMES` numa seleção e num clube de ML — conferir o quirk do
      comprimento kanji (§3.3). **11 regiões** na seleção
      (`tools/par/8.1-copy-selecao.sh`) e **13** no clube
      (`tools/par/8.1-copy-clube-ml.sh`, as duas a mais são
      `OFS_ML_TEAM_NAME_7`/`_8`). **O kanji não acompanha o comprimento dos
      outros, e o quanto ele desanda depende do time:** no clube sai com
      **span 9 / diff 4** enquanto os nomes saem com 7, e na seleção sai com
      **span 13 / diff 7** para a mesma fonte de 6 caracteres. É o quirk
      preservado
- [x] Repetir num clube de ML, incluindo os dois nomes extras — no
      `Master League 32` os limites são `(11)(11)(11)(7)(7)(7)` mais `(8)` e
      `(11)`, e as faixas gravadas batem com cada um: **10, 10, 10, 7, 7, 7**
      nos seis nomes, **7** em `OFS_ML_TEAM_NAME_7` e **10** em
      `OFS_ML_TEAM_NAME_8` (`tools/par/8.1-clube-ml-extras.sh`)

**O truncamento segue o rótulo em todos os limites medidos** — quatro
diferentes na mesma tela do clube de ML.

> **Verde de gravação exige controle positivo.** A primeira corrida deste bloco
> passou sem que **nada** tivesse sido editado: o port abre com o combo de time
> em `---` e os campos vazios, e digitar ali não grava em time nenhum. Os dois
> lados fizeram `Load`+`Save` e saíram iguais — verde que não media nada. O que
> denunciou foi comparar a cópia gravada contra a imagem **original**: só as
> não-idempotências conhecidas (all-star, cobradores) apareciam, e nenhuma
> região de nome. **Selecionar um time é parte do roteiro, não preâmbulo**, e
> toda corrida desta série leva o par golden + controle positivo.

### 8.2 Números de camisa

**Conferido em 2026-08-28** pela
[PAR-TASK-02](/docs/tasks/PAR-TASK-02.md), na `ptbr-remaster.bin`. O terceiro
item reprovou na primeira medição e foi fechado em 2026-08-29 pela
[CORR-WTE-124](/docs/tasks/CORR-WTE-124.md). **Um roteiro por item em
`tools/par/8.2-*.sh`**, os três remedidos a partir dos arquivos versionados.

**Os dois primeiros itens não se medem por byte cru.** `squad_numbers` é
bitfield empacotado, e lê-lo à mão no disco dá `63`, um número que não
significa nada. Quem decodifica é o `dump_estado`, e a invocação que produziu o
`31` e o `32` abaixo é esta:

```sh
g++ -std=c++17 -Isrc/core/include src/core/{CdImage,Database,Player,Tables,Team,TextCodec}.cpp \
    wte/tests/dump_estado.cpp -o dump_cpp
./dump_cpp <copia-gravada.bin> | grep -E '^teams\[0\]\.squad_numbers|^players\[462\]\.number'
./dump_cpp <copia-gravada.bin> | grep -E '^ml_teams\[31\]\.raw_numbers'
```

- [x] Digitar 33 numa seleção → tem que virar 32 na tela e no disco
      (`tools/par/8.2-clamp-selecao.sh`) — **a tela mostra 32** e o
      `dump_estado` dá **31**, porque o campo guarda `número − 1`; 31 é o teto,
      então o clamp aconteceu nos dois. Remedido em 2026-08-29 a partir do
      arquivo versionado: `teams[0].squad_numbers[0]` vai de `0` a **31** e
      `players[462].number` de `1` a **32**, iguais nos dois lados; o controle
      positivo traz `OFS_SQUAD_NUMBERS_NATIONAL+0`, 1 byte
- [x] Digitar num clube de ML (sem clamp) e conferir
      (`tools/par/8.2-clamp-clube-ml.sh`) — o mesmo 33 grava **32** lá, contra
      31 na seleção. A assimetria é do original e está reproduzida. Remedido:
      `ml_teams[31].raw_numbers[0]` vai de `0` a **32** nos dois lados, com
      `OFS_SQUAD_NUMBERS_ML+737` de 1 byte no controle positivo
- [x] `CMD_DEFAULT_NUMBERS` e conferir que o `number` do jogador seguiu
      (`tools/par/8.2-numeros-default.sh`) — reprovou na primeira medição, com
      **37 faixas no port contra 20 do `ed.exe`**, e foi corrigido pela
      [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md): o laço ia aos **64 slots** do
      array em vez dos **63 times**, e a 64ª volta escrevia fora de
      `players[1911]`, em cima de `teams[]`. Remedido depois do conserto: o
      controle do oráculo dá **20 faixas / 118 bytes**, o do port **19 / 103** —
      a diferença é exatamente a faixa conhecida do slot 64 —, e o golden sai
      `OK`. Pelo `dump_estado`, o `number` que **não** batia com o número de
      camisa do time cai de **62 slots na imagem original para 3**, os mesmos 3
      nos dois lados (time 55, slots 7/14/21 — all-star, que o `Save` refaz a
      partir dos links)

> **O botão abre `"Operation done!"`, e dispensar a caixa faz parte do
> roteiro.** Sem isso ela fica na frente do `CMB_WRITE`, o clique de gravar não
> chega, e o `wait_for_window` do `golden_gui.sh` toma **essa** caixa pela
> confirmação de gravação: imprime "gravado" e o arquivo sai intacto. Como os
> dois lados se comportam assim, o golden fica **verde sem ter medido nada**.
>
> E `Return` não serve para dispensá-la: fecha a `QMessageBox` do port e **não**
> fecha a do MFC sob Wine. O que funciona nos dois é clicar no botão, e ele fica
> em lugar **diferente** em cada um: a caixa do oráculo mede 148×82 com o `OK`
> no centro horizontal a ~40% da altura, e a do port mede 188×100 com o `OK` a
> ~77% da largura e ~75% da altura. Como o roteiro é o mesmo nos dois lados, o
> `8.2-numeros-default.sh` tenta os pontos em ordem e reconfere a caixa entre
> eles — o clique que erra o botão não faz nada.

### 8.3 Cobradores e capitão

**Conferido em 2026-08-28** pela
[PAR-TASK-03](/docs/tasks/PAR-TASK-03.md). O primeiro item reprovou na primeira
medição e foi fechado em 2026-08-29 pela
[CORR-WTE-125](/docs/tasks/CORR-WTE-125.md).

- [x] Abrir o combo, **navegar com as setas sem sair do controle**, apertar
      ESC/clicar fora — conferir se grava ou não igual ao original
      (`tools/par/8.3-escape-cobrador.sh`) — reprovou na primeira medição, com
      três `Down` e `Escape` levando `kick_long_fk` de 3 a **6 no `ed.exe`** e o
      deixando em **3 no port**, e foi corrigido pela
      [CORR-WTE-125](/docs/tasks/CORR-WTE-125.md). Remedido depois do conserto:
      **6 nos dois**, golden `OK`. E a contraprova
      (`tools/par/8.3-escape-sem-navegar.sh`): `Escape` **sem** navegar deixa o
      campo em 3 nos dois e não põe `OFS_KICKER+0` no controle positivo
- [x] Escolher e sair com Tab; conferir os 6 campos
      (`tools/par/8.3-escolher-e-tab.sh`) — `kick_long_fk` vai de 3 a 5 **nos
      dois**, e os outros cinco ficam intactos. Remedido depois do conserto do
      `Escape`, que não podia quebrá-lo
- [x] Lembrar da troca do par de cobradores a cada gravação (é esperada) —
      confirmada em toda corrida desta série: `OFS_KICKER+384` aparece no
      controle positivo mesmo quando nada de cobrador foi tocado

> **`Escape` num combo não é "cancelar".** A [§3.5](#35-cobradores-e-capitão)
> chegou a dizer que o original usava `CBN_KILLFOCUS` "justamente para navegar a
> lista com as setas sem gravar"; a metade certa é que ele não grava **na hora**.
> O valor navegado sobrevive ao `Escape` no MFC e era desfeito no `QComboBox`,
> e é essa diferença que a [CORR-WTE-125](/docs/tasks/CORR-WTE-125.md) fechou —
> no código e na frase da §3.5.
>
> **A emenda vale para os dezesseis combos que gravam em perda de foco**, não
> só para estes seis: os dez de papel usam o mesmo `FocusOut`, e divergiam do
> mesmo jeito. A [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md) estendeu o filtro
> e pôs o item na §8.7.
>
> **E não são dezesseis no total, são vinte e seis.** Os dez combos de papel do
> `DefaultTacticsDialog` divergiam pelo mesmo motivo e ficaram de fora daquele
> filtro, porque gravam por outro caminho —
> [CORR-WTE-134](/docs/tasks/CORR-WTE-134.md).

### 8.4 Atributos do jogador

**Os cinco conferidos** pela [PAR-TASK-04](/docs/tasks/PAR-TASK-04.md) — o
primeiro em 2026-08-28, os outros quatro em 2026-08-29. **Um roteiro por item**
em `tools/par/8.4-*.sh`, todos concatenados **depois** do `8.4-prelude.sh`, que
abre o `PlayerSkillsDialog` e não roda sozinho — são seis arquivos para cinco
itens, e o prelúdio é o sexto.

> **Este bloco edita numa janela própria.** O `PlayerSkillsDialog` mede 493×323
> px, e as coordenadas dos seus 21 campos no `controls.json` são relativas **a
> ele**, não ao `MainDialog` — daí o `sk_click` do prelúdio, que usa
> `--window "$SKILLS"`. `CMD_SKILLS1` fica em dlu (382,32) e `Escape` fecha.

- [x] Clampar habilidade abaixo de 12 e acima de 19
      (`tools/par/8.4-habilidade.sh`) — **os dois extremos**: 25 digitado em
      `attack` grava **19**, 3 digitado em `defence` grava **12**, idêntico ao
      oráculo. Remedido em 2026-08-29 a partir do arquivo versionado:
      `players[462]` sai de `attack 13 / defence 17` para `19 / 12` nos dois
      lados, e o controle positivo traz `OFS_PLAYER_ATTR+7`, 2 bytes
- [x] Altura 100 e 999; idade 1 e 99; número 0 e 99 — **os seis extremos, com
      clamp em todos**: altura `155..210`, idade `15..46`, número com teto 32
      (o mesmo da §8.2) e piso 1
- [x] Custo com mais de 2 dígitos — conferir que o original também trunca —
      `12345` grava **12**, e o `ed.exe` trunca igual
- [x] Trocar os 10 combos com mouse **e** com teclado — cinco por caminho,
      **nove avançam exatamente 1**; o décimo (`out_of_position`) fica parado
      nos dois lados por já estar no último item de um combo YES/NO
- [x] Editar nome de jogador (é aqui que se edita, não no diálogo principal) —
      `JOGADORxyz` grava os 10 bytes do `setMaxLength(10)`

### 8.5 Troca de jogador

**Os quatro conferidos em 2026-08-29** pela
[PAR-TASK-05](/docs/tasks/PAR-TASK-05.md), na `ptbr-remaster.bin`. Sete
corridas de `golden_check.sh` em modo `gui`, todas `OK`. **Um roteiro por item**
em `tools/par/8.5-*.sh`, todos concatenados **depois** do `8.5-prelude.sh`, que
abre o `PlayerSelectDialog` e não roda sozinho.

- [x] Slot de seleção nacional: "complete" e "incomplete"
      (`tools/par/8.5-selecao-nacional.sh`, os dois modos na mesma corrida por
      `PAR_COMPLETA=0|1`) — os dois gravam **coisas diferentes**: desmarcado
      (*incomplete*) toca **um** registro de jogador (`OFS_PLAYER_NAME+0` e
      `OFS_PLAYER_ATTR+0`), marcado (*complete*, `PAR_COMPLETA=1`) toca **dois**
      (mais `+1044` e `OFS_PLAYER_ATTR_1+356`)
- [x] Slot de clube de ML: link para contratado e para agente livre
      (`tools/par/8.5-clube-ml.sh`) — os dois gravam em `OFS_LINK_ML2+1122`,
      com **valores diferentes entre si**
- [x] Agente livre com nacionalidade padrão × escolhida no combo
      (`tools/par/8.5-nacionalidade-livre.sh`) — a escolha muda **1 byte** no
      mesmo `OFS_LINK_ML2+1122`
- [x] Slot de all-star: conferir que os nomes se refazem depois
      (`tools/par/8.5-allstar.sh`) — `OFS_PLAYER_NAME_7+124` muda junto com o
      link em `OFS_PLAYER_ATTR_8+36`, e o `ed.exe` refaz igual

> **O `PlayerSelectDialog` é a terceira janela desta série**, de 390×404 px —
> nem o `MainDialog` nem os 493×323 do `PlayerSkillsDialog` da §8.4. Os
> controles de link e nacionalidade (`CHK_ML`, `CHK_LK_DEF`, `CHK_LK_NDEF`,
> `CMB_NATIONALITY`) **não existem na tela** quando o destino é uma seleção
> nacional: só aparecem para time por link e para o pool de agentes livres,
> como a [§4.2](#42-selezdlg--playerselectdialog-8-on_) descreve.
>
> **Item de lista se escolhe por teclado, não por coordenada de linha.** O Qt e
> o MFC não desenham a mesma altura de linha, então calcular `topo + i*altura`
> erra de lado diferente em cada um. Clicar na lista, `Home` para ancorar, e
> `Down` N vezes — a mesma lição do `CMB_TEAM` na §8.1.

### 8.6 SoFIFA (sem rede, o possível) — **só depois de reativar (§1.1)**
- [ ] Sem `SOFIFA attributes.txt` → aviso "Impossible to read SOFIFA attributes !"
- [ ] Sem o arquivo de regras → silêncio, editor continua utilizável
- [ ] Cache `<imagem>_SOFIFAdb.txt` escrito à mão + `CMB_IMPFIFATXT` +
      `CMB_EDITALLTXT`, com as 4 combinações relevantes de checkbox
- [ ] URL `dummy` num jogador + `CMD_READ_URL`
- [ ] **Com rede, se ainda funcionar:** um jogador real, ida e volta

### 8.7 Táticas

**Os seis conferidos**, e a seção fechou em 2026-09-01 pela
[PAR-TASK-06](/docs/tasks/PAR-TASK-06.md).

O glob `tools/par/8.7-*.sh` tem **dez arquivos**: o prelúdio, que não roda
sozinho, mais **nove roteiros**. Sete saem `OK` de golden. Os outros dois são
os do item 6, o do `.t2002`: exportar sai `OK` e **importar diverge de
propósito**, porque quem lê errado é o oráculo — faixas, tabela e prova em
bytes no item. A contagem separa as duas coisas porque a frase anterior dizia
"seis roteiros, os seis saindo `OK`" e mandava, sem querer, re-medir a seção
inteira sem tocar no item mais valioso dela
([CORR-WTE-136](/docs/tasks/CORR-WTE-136.md)).

Rendeu **cinco** CORRs — a [127](/docs/tasks/CORR-WTE-127.md), a
[131](/docs/tasks/CORR-WTE-131.md), a [132](/docs/tasks/CORR-WTE-132.md), a
[134](/docs/tasks/CORR-WTE-134.md) e a [135](/docs/tasks/CORR-WTE-135.md) — e
**nenhuma delas era o que parecia à primeira vista**.

- [x] Clampar x em 0/48 e y em 0/112 — **os dois tetos, medidos no
      `raw_formation`**: 99 digitado em x grava `0x30` = 48, e 999 em y grava
      `0x70` = 112. Com 0 e 0, nada é clampado
- [x] Trocar papel e conferir a legenda do marcador — dois `Down` levam o 1º
      papel de `0x02` a `0x04` nos dois lados, e a legenda do marcador passa de
      `CB SX` a **`SW`** também nos dois, conferida em captura
- [x] **`Escape` depois de navegar um combo de papel** — **são dois conjuntos
      de dez, em formulários diferentes, e cada um custou uma CORR.** Os dez do
      `MainWindow` gravam pelo **mesmo** `FocusOut` dos seis de cobrador, então
      o `Escape` divergia ali exatamente como divergia lá: três `Down` a partir
      do papel `0x02` davam `0x05` no `ed.exe` e deixavam `0x02` no port,
      reprovando o golden em `OFS_FORMATIONS+0`. Fechado pela
      [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md), que estendeu o filtro aos
      dezesseis: agora `raw_formation[0]` vai a `0x05` nos dois, os outros nove
      slots ficam intactos, e a legenda do marcador mostra `LIB` nos dois —
      conferida em captura. Roteiros `tools/par/8.7-escape-papel.sh` e
      `tools/par/8.7-escape-papel-sem-navegar.sh`.

      Os **outros dez** são os `CMB_SLOT_ROLE2..11` do `DefaultTacticsDialog`
      (`TCMB_TAT2..11` no `.rc`), que escrevem os `roles[]` dos **presets**. O
      filtro da CORR-WTE-127 não os alcançava, e eles divergiam pelo mesmo
      motivo: três `Down` no primeiro papel do preset davam `0x05` no `ed.exe`
      e deixavam `0x02` no port, reprovando o golden em
      `before first offset+374189` — 1 faixa / 1 byte. Fechado pela
      [CORR-WTE-134](/docs/tasks/CORR-WTE-134.md); roteiro
      `tools/par/8.7-escape-papel-preset.sh`. Depois do conserto o golden sai
      `OK` e o controle positivo do port contra a imagem original dá **6
      faixas / 42 bytes**, com o byte de papel em `0x05` — o mesmo valor que o
      oráculo grava.

      **O caminho de commit dos dois conjuntos não é o mesmo**, e é o que torna
      o conserto do segundo diferente do primeiro: no `MainWindow` a escrita é
      no `FocusOut`; no diálogo de presets ela mora dentro do
      `currentIndexChanged`, guardada por `hasFocus()`. Repor o índice com o
      combo já sem foco não grava nada — daí o `setFocus()` explícito depois do
      `hidePopup()`
- [x] Aplicar os 16 presets num time — os dezesseis em sequência e o preset 1
      isolado dão `raw_formation` diferentes entre si, os dois idênticos ao
      oráculo
- [x] Editar e renomear um preset no `DefaultTacticsDialog`
      (`tools/par/8.7-preset-renomear.sh`) — reprovou na primeira medição, com
      o `ed.exe` gravando 7 faixas / 61 bytes contra o `IDENTICAL` do port, e
      foi corrigido pela [CORR-WTE-131](/docs/tasks/CORR-WTE-131.md).
      Remedido em 2026-08-30: o port grava **7 faixas / 48 bytes** contra a
      imagem original, com as duas do preset —
      `before first offset+374780` (o nome) e
      `OFS_TEAM_MIXED_CASE_NAME+223676` (a geometria do slot) — nos mesmos
      offsets do oráculo, e o golden sai `OK`
- [x] Exportar `.t2002`, importar de volta, e importar um `.t2002` do original
      (`tools/par/8.7-t2002-exportar.sh`, `8.7-t2002-importar.sh`) —
      **o port está certo, e a assimetria é do oráculo.** As duas pernas foram
      medidas com `golden_compare.py` e controle positivo dos dois lados em
      2026-08-31, pela [CORR-WTE-135](/docs/tasks/CORR-WTE-135.md); até então o
      item se apoiava só em tamanhos de arquivo e na leitura do fonte.

      **Exportar: `OK`.** O port grava **52 bytes** e o `Debug/ed.exe` **56** —
      a diferença é a largura do vptr, 4 contra 8, porque `tattica` tem
      destrutor virtual e o oráculo é um rebuild x86-64. O port zera os quatro
      bytes; o oráculo vaza um endereço de processo (`18e3 5c40 0100 0000`). Os
      **40 bytes de carga são byte-idênticos**: `cmp` de `port[12..51]` contra
      `oráculo[16..55]` não acusa nada. A gravação na imagem sai
      `OK: identico ao oraculo, exceto o slot 64 conhecido`, e o controle
      positivo do port dá 5 faixas / 41 bytes — só as não-idempotências, porque
      exportar não altera a imagem.

      **Importar: diverge, e a divergência é do oráculo.** Os dois lados
      importaram o **mesmo** arquivo de 52 bytes, editado para ser observável
      (nome `4-5-1A` → `PARIMP`, `roles[1]` `0x02` → `0x05`). O golden reprova
      em 3 faixas — `374188..374198`, `374780..374797` e
      `OFS_TEAM_MIXED_CASE_NAME+223676` —, e os controles positivos dizem quem
      errou:

      | | faixas / bytes | o que gravou no nome do preset |
      |---|---|---|
      | port | 7 / 48 | `5041 5249 4d50` = `PARIMP` |
      | `ed.exe` | 9 / 91 | `4d50 0001 0506` = `MP`, e depois bytes de papel |

      **O oráculo lê o registro 4 bytes adiante do lugar certo.** Ele valida o
      tamanho contra o literal 52 (`legacy/mfc/tattDlg.cpp:701`) — por isso
      aceita o arquivo —, mas decodifica com o vptr de 8 bytes do próprio
      binário x64, e tudo depois do magic sai deslocado: o nome vira o fim do
      nome, os papéis viram o começo do `x[]`. O port muda exatamente os dois
      campos que o arquivo mudou: 1 byte em `before first offset+374189`
      (`roles[1]`) e 6 em `OFS_TEAM_MIXED_CASE_NAME+223676` (o nome).

      **Este item não pode ficar verde, e não deve.** Verde exigiria o port
      reproduzir o deslocamento — isto é, ler errado de propósito um formato
      que o próprio fonte do original define como de 52 bytes. É a mesma
      conclusão da [CORR-WTE-132](/docs/tasks/CORR-WTE-132.md), agora com a
      prova em bytes em vez de por leitura de fonte.

> **A ida e volta funciona no sentido port → `ed.exe`, e não no inverso** —
> porque o arquivo que o oráculo x64 produz é que está torto, não o formato. O
> `.b2002` e o `.m2002` da §8.8 não têm esse problema: as classes de bandeira e
> uniforme **não têm destrutor virtual**, então não têm vptr, e o tamanho não
> muda entre 32 e 64 bits.

> **O `IDOK` do `DefaultTacticsDialog` é `NOT WS_VISIBLE` no próprio `ed.rc`**
> (linha 627: `DEFPUSHBUTTON "OK",IDOK,197,17,50,14,NOT WS_VISIBLE`), e o
> `rc2ui.py` traduz isso corretamente para `visible: false`. A tela concorda
> nos dois lados — o botão não aparece em nenhum. **A tradução está certa; o
> que diverge é o efeito.**
>
> **Os dois lados aplicam as edições campo a campo, e os dois são modais.** O
> port escreve direto em `db_.preset_formations`, que o `OnPresetTactics` passa
> por ponteiro; nada ali espera pelo `accept()`. O que divergia era **fechar o
> diálogo**: no MFC o `DEFPUSHBUTTON` invisível continua sendo o default, e
> `Return` roda o `EndDialog` — só então o clique em `CMB_WRITE` alcança o
> diálogo principal. O Qt não ativava nada, o `exec()` seguia bloqueando, e o
> `Database::Save()` nunca rodava.
>
> Medido em 2026-08-30: `ed.exe` grava 8 faixas / 63 bytes contra a imagem
> original, port saía `IDENTICAL`. E o **oráculo sem o `Return` final** sai
> `a gravacao nao confirmou`, também `IDENTICAL` — é o controle que mostra que
> o `Return` fecha o modal, e não que o original grave com ele aberto.
>
> **O conserto foi um `keyPressEvent`**, não um botão default:
> `setDefault(true)` no `IDOK` invisível foi medido e **não muda nada** — o Qt
> pula um default que não está visível. O `DefaultTacticsDialog` passou a
> tratar `Return` e chamar `accept()`; `Escape` continua com o `QDialog`, que
> rejeita, como o `IDCANCEL` fazia. O evento só chega ao diálogo depois de o
> `QLineEdit` focado ignorá-lo, e ele emite `editingFinished` antes — então o
> campo em edição é gravado antes de a janela fechar, na mesma ordem do
> original. [CORR-WTE-131](/docs/tasks/CORR-WTE-131.md)
>
> **Botão focado também fecha o diálogo, e isso custou uma segunda emenda.** No
> Win32 o `Return` de um diálogo vai para o `DEFPUSHBUTTON`, não para o controle
> focado — então, depois de clicar `Import` ou `Export`, o `Return` chega ao
> `IDOK` e o `EndDialog` roda. No Qt um `QAbstractButton` com foco trata
> `Return` como ativação e **consome** o evento, que nunca chegava ao
> `keyPressEvent`: o botão se auto-clicava e reabria o diálogo de arquivo,
> indefinidamente. Com o modal de pé o `CMB_WRITE` fica inalcançável, e o port
> saía `IDENTICAL` contra a imagem original onde o `ed.exe` gravava 6 faixas /
> 56 bytes. O `autoDefault=false` do `rc2ui.py` **não** resolve: ele governa
> qual botão é o default, não a ativação por foco. O `eventFilter` do diálogo
> passou a ver o `Return` antes dos botões
> ([CORR-WTE-139](/docs/tasks/CORR-WTE-139.md)); medido depois do conserto, o
> controle positivo do port dá 5 faixas / 41 bytes em vez de `IDENTICAL`.
>
> Quatro caminhos de fechamento foram descartados por medição, e não vale
> repeti-los: `Return` sem foco, `Return` com `windowfocus`,
> `xdotool key --window` (XSendEvent, que o Qt ignora) e clicar na posição do
> botão invisível.

### 8.8 Bandeira e uniformes

**Os três conferidos em 2026-08-31** pela
[PAR-TASK-07](/docs/tasks/PAR-TASK-07.md), na `ptbr-remaster.bin`. Roteiros em
`tools/par/8.8-*.sh`, sobre o `8.8-prelude.sh`.

- [x] Cores no teto (65535) e acima — `flag_colours[0]` vai de 3523 a **65535**
      tanto com `65535` quanto com `99999` digitado: clampa no teto, igual nos
      dois lados. O uniforme muda em `home_kit[2]`, não `[0]`, confirmando que
      as palavras 0 e 1 das 16 não são expostas
- [x] Time sem bandeira própria (57..63, 69, 86 e o 56) → caixas desabilitadas e
      import/export recusado — **as duas metades medidas em todos os ids da
      lista, e o 56 diverge como previsto**; ver a nota abaixo.

      Os **69 e 86 foram medidos depois, em 2026-08-31**, pela
      [CORR-WTE-138](/docs/tasks/CORR-WTE-138.md): eles estavam nomeados no item
      sem nunca terem ido à tela, e não são mais do mesmo — 56 e 57..63 são
      seleções e all-star, tratadas pelo primeiro ramo do `OnButtgraf`
      (`squad_nazall[id-1]`), enquanto **69 e 86 são clubes de Master League**,
      abertos pelo segundo (`squad_ml[id-64]`; `db_.ml_teams[id-64]` no port,
      [src/app/Commands.cpp:65](../src/app/Commands.cpp)). Medir 57..63 não
      exercitava esse caminho.

      **Os dois lados concordam nos dois ids, nas duas metades.** As caixas de
      cor saem desabilitadas em ambos — capturado nos quatro cruzamentos, com
      `Style` 54 no id 69 e 56 no id 86, iguais dos dois lados —, e o
      `CMD_EXPORT_FLAG` é recusado em ambos: nenhum diálogo de arquivo abre e
      sobe a caixa `Choose a team (that has "indipendent" flag too) !`. Golden
      `OK` nas duas corridas. Roteiro
      `tools/par/8.8-sem-bandeira.sh`, com o id em `PAR_TEAM`
- [x] `.b2002` e `.m2002`: exportar do port e importar no `ed.exe`, e vice-versa
      — **funciona nos dois sentidos**. Os arquivos exportados são
      **byte-idênticos** (41 e 40 bytes), e importar o mesmo `.b2002` alterado
      nos dois lados grava `OFS_FLAG_COLOURS+2` em ambos, com as imagens saindo
      idênticas salvo a faixa conhecida.

      **Remedido em 2026-08-31 pela
      [CORR-WTE-137](/docs/tasks/CORR-WTE-137.md)**, porque o roteiro que
      sustentava este item era um falso verde: em quatro corridas idênticas ele
      dava quatro resultados, nunca produzia o `.m2002`, e em duas delas saía
      `gui: gravado` com a imagem `IDENTICAL` contra a original — não gravava e
      dizia que sim. Com o roteiro consertado, **três corridas seguidas** dão os
      dois arquivos nos dois lados, com os mesmos bytes entre corridas e entre
      lados (`cmp` limpo), o golden sai
      `OK: identico ao oraculo, exceto o slot 64 conhecido` e o controle
      positivo do port dá **5 faixas / 41 bytes** — as não-idempotências, que é
      a assinatura de que o `Save()` rodou. O `.b2002` do port, na íntegra:

      ```text
      00000000: 662e 6d2e 6261 6e64 00c3 0d82 89bd f718  f.m.band........
      00000010: e359 8ef6 8dcb aedc 8ebd f7bd f7bd f7bd  .Y..............
      00000020: f700 8000 8020 cd00 00                   ..... ...
      ```

> **A divergência deliberada da Fase 5 está medida na tela, e é a esperada.** No
> id **56** (World All-Stars) o port **desabilita** as caixas de cor e o
> `ed.exe` as **habilita** — capturado nos dois. É o que a
> [§6 item 5](#6-divergências-deliberadas) descreve: o `graf` original tinha
> **dois** testes de "tem bandeira própria" que discordavam nessa borda, e o
> port usa um só. Nos ids **57..63, 69 e 86** os dois lados concordam (ambos
> desabilitam), e o export é recusado com a **mesma** mensagem em ambos —
> `Choose a team (that has "indipendent" flag too) !`. Os dois de Master League
> entraram nesta conta em 2026-08-31, pela
> [CORR-WTE-138](/docs/tasks/CORR-WTE-138.md); antes dela a concordância só
> estava medida em 57..63.
>
> **Isto não é CORR**: a divergência está na lista de aceitas do
> [/docs/PLAN-LINUX.md](/docs/PLAN-LINUX.md), e este item era justamente onde
> ela finalmente se mediria.
>
> **O contraste com o `.t2002` da §8.7 vale registrar.** Aqui os dois formatos
> saem byte-idênticos e a troca funciona nos dois sentidos; lá o arquivo do
> port tem 52 bytes contra 56 do original e o `ed.exe` recusa até o que ele
> mesmo exportou ([CORR-WTE-132](/docs/tasks/CORR-WTE-132.md)). Mesmo diálogo
> de origem, formatos vizinhos, resultados opostos.

### 8.9 Operações em massa
**Três de cinco medidos em 2026-09-01** pela
[PAR-TASK-08](/docs/tasks/PAR-TASK-08.md); dois não são mensuráveis nesta
máquina. Roteiros em `tools/par/8.9-*.sh`.

- [ ] `CMD_SORT_RESERVES` numa seleção e num clube (a ordem torta é a certa).
      **O botão é invisível nos dois** — exige build de teste com o controle
      visível dos dois lados; não commitar. **Não medido:** o `.rc` confirma o
      `NOT WS_VISIBLE`, e tornar o controle visível no `ed.exe` exige MSVC com
      MFC estático, que não existe nesta máquina
- [ ] Clube com 1 goleiro na reserva × com 2 — **não medido pela mesma razão**:
      é o mesmo `OnSortReserves`, cujo comentário descreve justamente o caso de
      um goleiro só (as duas últimas vagas trocam)
- [x] `CMD_UPDATE_COSTS` — golden `OK`
- [x] `CMB_EDITALLLOOK` — reprovou na primeira medição (92 bytes em quatro
      faixas de `OFS_PLAYER_ATTR`), e a
      [CORR-WTE-133](/docs/tasks/CORR-WTE-133.md) mostrou que **não era
      código**: o legado abre `defaultlook.txt` por caminho relativo e lê a
      cópia de `Debug/`, que é gitignored e tinha 4 das 95 linhas diferentes da
      versionada. Alinhada a fixture, sai `OK`
- [x] `CMB_EDITALLBARS` — conferir que 57..63 ficaram intactos — **ficaram**:
      as barras de 56..63 saem `7 8 9 7 8 9 9 0` antes e depois, enquanto as de
      0..5 vão de `7 4 5 7 8 8` a `7 7 7 7 7 7`, provando que o botão agiu

> **Nem toda operação em massa abre `"Operation done!"`, e os dois lados não
> concordam sobre isso.** O `CMD_UPDATE_COSTS` abre nos dois; o
> `CMB_EDITALLBARS` abre **só no port** (uma caixa de 126×100) e não no
> `ed.exe`. Um `Return` seco resolve os dois casos — fecha a `QMessageBox` e é
> inócuo no diálogo do original, que não tem `DEFPUSHBUTTON`.
>
> **O que não serve é o `dispensa_modal`** do roteiro da §8.2 quando não há
> caixa: sob Wine os controles do MFC são janelas X de verdade, e vários caem
> na faixa de tamanho que ele procura (206×80, 148×82). Ele acha um
> **controle**, clica nele, e a gravação do oráculo não acontece — a cópia sai
> `IDENTICAL` enquanto o port grava, e o golden acusa o port por uma
> divergência que é do roteiro.

### 8.10 Ciclo de vida

**Os cinco conferidos** pela [PAR-TASK-09](/docs/tasks/PAR-TASK-09.md), em
2026-08-31. **Três concordam e dois divergem** — e os dois que divergem são de
ciclo de vida, não de dado: nenhuma das duas divergências grava byte nenhum.
Rendeu duas CORRs, a [140](/docs/tasks/CORR-WTE-140.md) e a
[141](/docs/tasks/CORR-WTE-141.md), as duas esperando **decisão**, não conserto.

Dois roteiros são hooks de golden (`tools/par/8.10-reload-descarta.sh` e
`8.10-return-nao-dispara.sh`) e dois rodam sozinhos
(`8.10-ciclo-oraculo.sh`, `8.10-ciclo-port.sh`) — arranque e encerramento o
harness não expõe, porque ele já entra pelo diálogo de abertura e já sai
gravando.

- [x] Cancelar o diálogo de abertura — **DIVERGE.** Os dois mostram
      `Impossible editing without CD image !`; depois disso o `ed.exe` **fica de
      pé com o diálogo principal inteiro e vazio** (combo sem itens, campos em
      branco, `Write into CD image` clicável) e o port **encerra**. A causa é uma
      armadilha de MFC: `OnInitDialog` faz `return FALSE`
      (`legacy/mfc/edDlg.cpp:1331`), e esse retorno **não fecha diálogo** — só
      diz que o foco já foi tratado. [CORR-WTE-140](/docs/tasks/CORR-WTE-140.md)
- [x] Abrir arquivo com tamanho errado → aviso, e carrega — **concordam.** Os
      dois avisam `Not WE2002 CD image (474.431.328 bytes)!` e carregam assim
      mesmo; no legado a linha que abortaria está comentada
      (`// return FALSE;`), e o port copia isso com o comentário
      "A warning only, exactly as in the original"
- [x] `CMB_RELOAD` depois de editar → descarta as edições — **concordam**,
      golden `OK`. Editar `TXT_TEAM_NAME1` para `RELOAD`, recarregar e gravar dá
      **5 faixas / 41 bytes** contra a imagem original, que são só as
      não-idempotências. O **controle** é a corrida gêmea sem o `CMB_RELOAD`
      (`PAR_SEM_RELOAD=1`): ali saem **6 faixas / 46 bytes**, e a sexta é
      `OFS_TEAM_NAME_1_A+200`, a edição chegando ao disco. Sem esse controle o
      item passaria com um roteiro que nem chegou a digitar
- [x] `Return` na janela principal não pode disparar nada — **cumprido nos dois,
      e o ciclo de vida DIVERGE.** Nenhum dos dois dispara ação de edição, que é
      o que o item existe para garantir: no port a imagem gravada depois do
      `Return` é **byte-idêntica** à de um `Load`+`Save` sem tecla nenhuma. Mas
      no `ed.exe` o `Return` **encerra o editor** — `IDD_ED_DIALOG` não tem
      `DEFPUSHBUTTON` e o Enter cai em `CDialog::OnOK` —, então lá nada é
      gravado porque não há mais janela.
      [CORR-WTE-141](/docs/tasks/CORR-WTE-141.md)
- [x] `Escape` fecha — **concordam**: `IDCANCEL`/`CDialog::OnCancel` de um lado,
      `QDialog::reject` do outro, e o processo termina nos dois

> **Este item é a guarda do `autoDefault=false`, e é por isso que ele importa.**
> Dentro de um `QDialog` o Qt torna todo botão auto-default; num diálogo com 86
> botões e nenhum `DEFPUSHBUTTON`, o `Return` clicaria o primeiro da ordem de
> tabulação — e um dos candidatos aplica formação predefinida sobre o time
> selecionado. O `rc2ui.py` emite `autoDefault=false` por causa disso, e o
> roteiro `8.10-return-nao-dispara.sh` é o que impede a emenda de apodrecer em
> silêncio.
>
> **A decisão do `DefaultTacticsDialog` não contradiz esta.** Lá o `Return`
> **fecha**, e deve ([CORR-WTE-139](/docs/tasks/CORR-WTE-139.md)), porque o
> `ed.rc` declara um `DEFPUSHBUTTON` — invisível, mas declarado (linha 627).
> Aqui não há nenhum. A regra é a mesma nos dois: o `Return` vai para o botão
> default do diálogo, e o comportamento muda porque um diálogo tem esse botão e
> o outro não.

### 8.11 Windows (o item aberto da Fase 7)
- [ ] Editar nome de time pela janela Qt no Windows e comparar com o
      `Debug\ed.exe` nativo. Bloqueado por: a Citrix filtra input sintético e a
      UIA do Qt não expõe os itens do combo de forma estável. Ver §5.3 e §11 do
      [PLAN-WINDOWS.md](/docs/PLAN-WINDOWS.md)

---

## 9. Em aberto

| Item | Situação |
|---|---|
| ASan no MSVC | preset `windows-asan` existe, mas `if(WE2002_SANITIZE AND NOT MSVC)` desliga tudo. É a primeira chance de varrer os 198 `strcpy` herdados |
| Fonte | MS Sans Serif não instalada; rótulos apertados cortam ("Position" → "Positior"). O `ed.exe` sob Wine corta os mesmos. Decidido ficar assim |
| SoFIFA em 2026 | o site mudou desde 2015; o raspador pode não achar mais nada. Nada disso é regressão do port — conferir antes de acusar |
| CI | `push`/`pull_request` desligados por decisão até o fim do projeto; só `workflow_dispatch`. **Não religar por conta própria** |
