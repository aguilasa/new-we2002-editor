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
o original usava `CBN_KILLFOCUS` justamente para navegar a lista com as setas sem
gravar. Ver §8.3 para o teste que fecha isso.

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
`y[10]`, 2 de padding — 44 bytes. O port grava zeros no vptr e ignora na leitura.
Arquivos antigos continuam legíveis.

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
| `Return` fecha o editor | `IDOK` implícito do `CDialog`, com `CanExit()` sempre `TRUE` | no Qt, `Return` acionaria um dos 86 botões (um deles aplica formação!). O `rc2ui.py` emite `autoDefault=false`; hoje `Return` **não faz nada**, que é mais seguro que os dois comportamentos. `Escape` fecha, como nos dois |
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

**Dois de três conferidos em 2026-08-28** pela
[PAR-TASK-02](/docs/tasks/PAR-TASK-02.md), na `ptbr-remaster.bin`. O terceiro
reprovou e virou [CORR-WTE-122](/docs/tasks/CORR-WTE-122.md).

- [x] Digitar 33 numa seleção → tem que virar 32 na tela e no disco — **a tela
      mostra 32** e o `dump_estado` dá **31**, porque o campo guarda
      `número − 1`; 31 é o teto, então o clamp aconteceu nos dois
- [x] Digitar num clube de ML (sem clamp) e conferir — o mesmo 33 grava **32**
      lá, contra 31 na seleção. A assimetria é do original e está reproduzida
- [ ] `CMD_DEFAULT_NUMBERS` e conferir que o `number` do jogador seguiu —
      **reprovou**: o port grava 37 faixas contra 20 do `ed.exe`, 18
      divergências fora da faixa conhecida.
      [CORR-WTE-122](/docs/tasks/CORR-WTE-122.md)

> **O botão abre `"Operation done!"`, e dispensar a caixa faz parte do
> roteiro.** Sem isso ela fica na frente do `CMB_WRITE`, o clique de gravar não
> chega, e o `wait_for_window` do `golden_gui.sh` toma **essa** caixa pela
> confirmação de gravação: imprime "gravado" e o arquivo sai intacto. Como os
> dois lados se comportam assim, o golden fica **verde sem ter medido nada**.
>
> E `Return` não serve para dispensá-la: fecha a `QMessageBox` do port e **não**
> fecha a do MFC sob Wine. O que funciona nos dois é clicar no botão — a caixa
> do oráculo mede 148×82 e o `OK` fica no centro horizontal a ~40% da altura.

### 8.3 Cobradores e capitão

**Dois de três conferidos em 2026-08-28** pela
[PAR-TASK-03](/docs/tasks/PAR-TASK-03.md). O primeiro reprovou e virou
[CORR-WTE-123](/docs/tasks/CORR-WTE-123.md).

- [ ] Abrir o combo, **navegar com as setas sem sair do controle**, apertar
      ESC/clicar fora — conferir se grava ou não igual ao original —
      **reprovou**: três `Down` e `Escape` levam `kick_long_fk` de 3 a **6 no
      `ed.exe`** e o deixam em **3 no port**.
      [CORR-WTE-123](/docs/tasks/CORR-WTE-123.md)
- [x] Escolher e sair com Tab; conferir os 6 campos — `kick_long_fk` vai de 3 a
      5 **nos dois**, e os outros cinco ficam intactos
- [x] Lembrar da troca do par de cobradores a cada gravação (é esperada) —
      confirmada em toda corrida desta série: `OFS_KICKER+384` aparece no
      controle positivo mesmo quando nada de cobrador foi tocado

> **A frase da [§3.5](#35-cobradores-e-capitão) está errada, e a
> [CORR-WTE-123](/docs/tasks/CORR-WTE-123.md) a corrige junto com o código.**
> Ela diz que o original usava `CBN_KILLFOCUS` "justamente para navegar a lista
> com as setas sem gravar". Os dois gravam em perda de foco, isso está certo —
> mas o **valor** que chega lá é outro: `Escape` mantém o item navegado no MFC e
> reverte no `QComboBox`.

### 8.4 Atributos do jogador

**Um de cinco conferido em 2026-08-28** pela
[PAR-TASK-04](/docs/tasks/PAR-TASK-04.md); os outros quatro não couberam no
lote e seguem abertos.

- [x] Clampar habilidade abaixo de 12 e acima de 19 — **os dois extremos**: 25
      digitado em `attack` grava **19**, 3 digitado em `defence` grava **12**,
      idêntico ao oráculo
- [ ] Altura 100 e 999; idade 1 e 99; número 0 e 99
- [ ] Custo com mais de 2 dígitos — conferir que o original também trunca
- [ ] Trocar os 10 combos com mouse **e** com teclado
- [ ] Editar nome de jogador (é aqui que se edita, não no diálogo principal)

### 8.5 Troca de jogador
- [ ] Slot de seleção nacional: "complete" e "incomplete"
- [ ] Slot de clube de ML: link para contratado e para agente livre
- [ ] Agente livre com nacionalidade padrão × escolhida no combo
- [ ] Slot de all-star: conferir que os nomes se refazem depois

### 8.6 SoFIFA (sem rede, o possível) — **só depois de reativar (§1.1)**
- [ ] Sem `SOFIFA attributes.txt` → aviso "Impossible to read SOFIFA attributes !"
- [ ] Sem o arquivo de regras → silêncio, editor continua utilizável
- [ ] Cache `<imagem>_SOFIFAdb.txt` escrito à mão + `CMB_IMPFIFATXT` +
      `CMB_EDITALLTXT`, com as 4 combinações relevantes de checkbox
- [ ] URL `dummy` num jogador + `CMD_READ_URL`
- [ ] **Com rede, se ainda funcionar:** um jogador real, ida e volta

### 8.7 Táticas
- [ ] Clampar x em 0/48 e y em 0/112
- [ ] Trocar papel e conferir a legenda do marcador
- [ ] Aplicar os 16 presets num time
- [ ] Editar e renomear um preset no `DefaultTacticsDialog`
- [ ] Exportar `.t2002`, importar de volta, e importar um `.t2002` do original

### 8.8 Bandeira e uniformes
- [ ] Cores no teto (65535) e acima
- [ ] Time sem bandeira própria (57..63, 69, 86 e o 56) → caixas desabilitadas e
      import/export recusado
- [ ] `.b2002` e `.m2002`: exportar do port e importar no `ed.exe`, e vice-versa

### 8.9 Operações em massa
- [ ] `CMD_SORT_RESERVES` numa seleção e num clube (a ordem torta é a certa).
      **O botão é invisível nos dois** — exige build de teste com o controle
      visível dos dois lados; não commitar
- [ ] Clube com 1 goleiro na reserva × com 2
- [ ] `CMD_UPDATE_COSTS`
- [ ] `CMB_EDITALLLOOK`
- [ ] `CMB_EDITALLBARS` — conferir que 57..63 ficaram intactos

### 8.10 Ciclo de vida
- [ ] Cancelar o diálogo de abertura
- [ ] Abrir arquivo com tamanho errado → aviso, e carrega
- [ ] `CMB_RELOAD` depois de editar → descarta as edições
- [ ] `Return` na janela principal não pode disparar nada
- [ ] `Escape` fecha

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
