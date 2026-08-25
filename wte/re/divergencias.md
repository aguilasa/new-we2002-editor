# `re/divergencias.md` — o que diverge do original, e por quê

**Escrito à mão.** Produto da
[WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md). O que é
*medido* aqui vem de ferramenta e está citado entrada a entrada; o que é
*decidido* é prosa, e prosa não se gera.

A conferência mecânica deste arquivo é o
[`check_divergencias.py`](../tools/check_divergencias.py), que o
`make -C wte check` roda. Ele não julga a prosa — ele casa **exceção nomeada em
ferramenta** com **entrada aqui**, nos dois sentidos.

## O que "100%" quer dizer neste projeto

> **Todo handler com veredito escrito e toda gravação byte-idêntica.** Não
> significa que nenhuma divergência é aceita — significa que nenhuma é
> *desconhecida*.

A política difere da do `newWe2002`, e a diferença é deliberada: lá o objetivo
era clonar o `ed.exe` inclusive nos defeitos; aqui a §0 do plano permite **não**
reproduzir bug do original, e exige registro.

## O que NÃO entra aqui

Divergência **não deliberada**. Se algo diverge e ninguém sabe por quê, isso é
bug aberto, não entrada neste documento — confundir os dois é como lista de
problemas conhecidos vira desculpa.

E o simétrico, que esta task teve de aplicar antes de escrever a primeira
entrada: **exceção sem divergência também não entra.** Uma isenção que
sobreviveu à própria causa é o mesmo defeito pelo avesso — ver a §9.

**E rota não portada também não é divergência deliberada.** O vocabulário
importa: divergência deliberada é comportamento que se **escolheu** não
reproduzir; rota não portada é trabalho que ainda não foi feito, e o lugar dela
é o veredito da spec, não este registro. Escrever uma como a outra faz o
documento parecer completo quando falta código.

O caso corrente é o **`ficha_enlaza`**, que não tem chamador nenhum no port
(achado 8 da reconferência de UI, 2026-08-25). Não é escolha de tela: a rota
que o alcança é o `MainForm.mostrar_jugadorClick` para jogador de clube de
Master League, e a
[WTE-TASK-30](../../docs/tasks/30-handlers-auxiliares.md) deixou escrito por
medir *qual condição faz o modal abrir*. O dono é aquela spec; quando a
condição for medida e a rota portada, não haverá nada a registrar aqui — e se
a decisão for **não** portá-la, aí sim vira entrada, com a razão.

---

## 1. Sufixo ` [Lazarus]` no `Caption` dos 18 formulários

| Campo | |
|---|---|
| **O que diverge** | o título de janela dos 18 formulários, em toda execução |
| **Natureza** | escolha |
| **Decisão** | manter |

**Razão.** O `Caption` vem do DFM, e o do `MainForm` é literalmente
`' W11 Team Editor PT by chagas_michel!'`. A partir da
[WTE-TASK-22](../../docs/tasks/22-harness-golden.md) os dois editores rodam no
**mesmo** display, e o harness acha janela por título e por tamanho — título
igual faria ele dirigir o lado errado, que é a armadilha 5 do prompt de
execução e a causa de um diff que pareceria bug do port.

**Evidência.** Posto em tempo de execução por `MarcaOsTitulos`, em
[`wte/src/wtemain.pas`](../src/wtemain.pas) — **não** no `.lfm`, que é gerado.

**Onde o teste sabe.** Os roteiros do lado port casam
`W11 Team Editor PT by chagas_michel! \[Lazarus\]`, e os do lado oráculo o nome
sem sufixo; é o que separa os dois lados no mesmo display. No `:98` não há
window manager, nenhuma barra de título é desenhada, e a captura da
[WTE-TASK-12](../../docs/tasks/12-comparacao-visual.md) não enxerga o sufixo —
num desktop de verdade enxerga, e deve.

---

## 2. Cinco glifos não acinzentam ao desabilitar

| Campo | |
|---|---|
| **O que diverge** | o desenho de 5 botões quando ficam desabilitados |
| **Natureza** | limitação de plataforma (widgetset) |
| **Decisão** | não reproduzir |

**Razão.** A LCL desabilita glifo aplicando `gdeDisabled`, que é **conversão
para tons de cinza**; pixel com `R = G = B` é ponto fixo dela. Glifo desenhado
só com preto e branco puros sobre a cor transparente é portanto **invariante**,
e o botão apaga logicamente sem mudar um pixel. O `comctl32` do Win32 não faz
grayscale — monta o glifo desabilitado de uma máscara monocromática, em que
preto vira sombra (`#A6A6A6`) e branco vira transparente. Igualar exigiria
desenhar à mão um segundo glifo (`NumGlyphs = 2`) que **não existe no recurso do
original**, ou reescrever o `TButtonGlyph` da LCL.

**Evidência.** Medida pela
[CORR-WTE-060](../../docs/tasks/CORR-WTE-060.md) em 2026-08-18 e remedida em
2026-08-25: `iguala_nombres` muda **518 px** no oráculo sob Wine e **0** no port
(`compara_tela.sh --habilitacao`, recorte `(344,184,73,25)`). Duas hipóteses
anteriores foram **refutadas** num harness LCL isolado — `ParentFont := True`
continua dando 0 px, e recolorir o glifo do vizinho para a cor de fundo dá 513
px, não 0. O número fecha dos dois lados: `boton_nombres2iso` tem **280 pixels
não-cinza** no glifo e muda **280 px** no app rodando.

**Onde o teste sabe.** Em dois lugares, e os dois são exceção nomeada:

- [`check_glifos_disabled.py`](../tools/check_glifos_disabled.py) varre os
  **59** botões com glifo dos 18 formulários e declara os **5** invariantes —
  `iguala_nombres`, `parriba`, `pabajo` (`MainForm`), `oscurecer` e `aclarar`
  (`color`). Glifo que entre ou saia do conjunto derruba o `make -C wte check`;
- o grupo `glifo_cinza` do [`compara_tela.py`](../tools/compara_tela.py), que
  mede e relata sem reprovar. Hoje só o `iguala_nombres` cai na faixa medida.

---

## 3. Cara, cabelo e barba da ficha não redesenham

| Campo | |
|---|---|
| **O que diverge** | 5 das 12 setas de aparência do formulário `jugador` mudam o rótulo e não mudam o desenho |
| **Natureza** | escolha de escopo |
| **Decisão** | não implementar |

**Razão.** As três carregadoras de bitmap do original — `0x00406fe0`
(`careto_base.bmp`), `0x00407110` (`pelo_<n>.bmp`) e `0x00407338`
(`barba_<n>.bmp`) — abrem o `.bmp` em `"r+b"`, dão `fseek` para a entrada 10 da
paleta e **regravam a paleta dentro do próprio arquivo de asset** antes de
recarregá-lo. Como `pelo_<n>.bmp` e `barba_<n>.bmp` são compartilhados por todos
os jogadores e o `make -C wte assets` liga a pasta de assets em
`we-team-editor/`, do usuário, mexer numa seta de cabelo reescreveria o arquivo
que todos usam, na pasta do Obocaman.

As saídas seriam duas — reproduzir a gravação in-place, tornando o porte
read-write sobre dado do usuário, ou escrever um segundo caminho de recolorir em
memória — e **nenhuma tinha dono**: a
[WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md) é dona de handler e
excluiu as três; a [WTE-TASK-29](../../docs/tasks/29-camisa-e-bandeira-2d.md) é
dona de asset, mas dos dois do `MainForm`. Caíam entre as duas definições, e é a
própria 26 que escreve a regra: *"Exclusão sem dono nomeado é buraco."* Esta
entrada é o dono.

**Evidência.** O efeito visível está na spec
([`jugador.flechasapaClick`](spec/jugador.flechasapaClick.md)); as medições vêm
das §5, §5.1 e §6 do [`assets.md`](assets.md). Que a gravação acontece de
verdade não precisou de teste destrutivo: a §6.1 lê o `mtime` dos 198 `.bmp` —
176 de 2002, 19 de 2006 — e acha **três** reescritos no mesmo segundo de
2026-08-05, a primeira sessão de `make wte` nesta máquina, com o tamanho
intacto.

**O que esta exclusão não cobre.** A saturação em `7` do `beard_style`: o disco
guarda 3 bits (0..7), o `Max` do controle é 6 e só existem `barba_0..6`. Isso é
comportamento de **gravação**, é da
[WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md), e não deixa de valer
por o desenho não sair.

**Onde o teste sabe.** **Nenhuma régua alcança o formulário `jugador`**, e por
isso esta entrada não pede exceção nomeada em lugar nenhum. A bateria de bytes
não passa por aqui — o handler não grava na imagem; a de pixel mede a janela do
`MainForm`. Se alguma passagem futura criar régua para o `jugador`, ela nasce
com as três imagens divergindo, e é esta entrada que explica por quê.

---

## 4. O `MaxLength` do `edit_nombre1` na European Deluxe

| Campo | |
|---|---|
| **O que diverge** | o limite do primeiro campo de nome, em **49 dos 95** times, e **só** na European Deluxe |
| **Natureza** | consequência de uma decisão já registrada |
| **Decisão** | manter |

**Razão.** O original **anda pelo arquivo** a cada troca de time, medindo a
largura do registro como "bytes não-zero até o próximo não-zero". O port não
reabre a imagem — decisão medida, escrita no cabeçalho do
[`lista_equiposChange.inc`](../src/impl/ep2002_mainform.lista_equiposChange.inc)
— e tira o número de `TEAM_NAME_KANJI_LEN`, do `we2002_core`. Os dois caminhos
dão o mesmo resultado quando o slot de kanji contém kanji. Na European Deluxe
nomes latinos foram escritos em slot de kanji e deixaram lixo depois do
terminador, então a distância ao próximo registro encurta. Reproduzir exigiria o
port reabrir a imagem a cada troca de time, que é a decisão contrária.

**Evidência.** [CORR-WTE-064](../../docs/tasks/CORR-WTE-064.md), 2026-08-18:
emulada a travessia do original sobre as duas imagens,
`(largura − 1) div 2 == TEAM_NAME_KANJI_LEN − 1` em **95/95** times na japonesa
e **46/95** na European Deluxe. O lote `OFS_TEAM_NAME_3`, que o `edit_nombre2`
usa, bate **95/95 nas duas** — o problema é do slot de kanji, não do método.

**Onde o teste sabe.** Não há exceção a nomear, e sim uma imagem escolhida de
propósito: o `compara_tela.sh --nomes` roda sobre a japonesa, onde não há
divergência. Rodar o mesmo modo apontando para a European Deluxe acusaria — e
**acusaria corretamente**.

---

## 5. O preço do 23º jogador nunca é gravado

| Campo | |
|---|---|
| **O que diverge** | nada: o port **reproduz**. A divergência é do original contra si mesmo |
| **Natureza** | **bug do original** |
| **Decisão** | reproduzir |

**O que acontece.** O `MainForm.base_teamClick` percorre os 23 slots de um time
e grava **22** bytes de preço, de `OFS_COST_NATIONAL + 23·t` até `+ 21`. O do
slot 22 fica com o valor de fábrica. Não é limitação do formato: o slot é
endereçável e o próprio editor o grava por outro caminho — o
[`io-medido.tsv`](io-medido.tsv), sessão `27-mcr2iso`, traz `W 3067473 3067495
23`, o import de `.mcr` escrevendo os 23 bytes condicionais do time 3.

**Razão da decisão.** O gate da feature é byte a byte contra o oráculo, e a §0
permite não reproduzir bug do original mas exige registro — aqui reproduzir é o
que mantém o gate honesto. Gravar o 23º byte faria o port divergir do oráculo
num byte por time em toda a operação, e a "correção" seria uma escolha nossa
sobre dado do usuário sem nada que a valide.

**Evidência.** [CORR-WTE-095](../../docs/tasks/CORR-WTE-095.md), 2026-08-24,
três réguas independentes:

1. **Plantio** — `0xFF` nos slots 20, 21 e 22 do time 2; depois da corrida os
   dois primeiros voltam **26** e **21**, o `previsto` do
   [`preco.tsv`](preco.tsv), e o terceiro continua **255**. Separa "não grava"
   de "grava o valor que já estava lá";
2. **`strace`** — o oráculo **lê** o byte condicional do slot 22, com o mesmo
   número de seeks dos outros 22. Logo não é o `je` de `0x004110ad` que pula o
   slot, que era a explicação corrente até esta correção. Contadas as syscalls:
   **22** `write` de 1 byte para **23** voltas;
3. **Depurador** — o `fputc` do laço para **23** vezes e os 23 retornam
   sucesso; o da 23ª volta devolve **20**, exatamente o preço que a fórmula
   prevê. O byte é calculado certo, aceito pelo runtime C, e **não vira
   `write`** — perde-se na saída bufferizada da Borland, abaixo do `fputc`.

**Onde o teste sabe.** Em dois lugares, e nenhum precisa de exceção nomeada,
porque o port reproduz: o
[`golden-22-precos`](../tests/roteiros/golden-22-precos.txt) compara imagem
inteira e fecha byte-idêntico com 22 bytes dos dois lados; e o
[`check_preco.py`](../tools/check_preco.py) **recusa** qualquer linha de slot 22
marcada como medida no `preco.tsv` — se a regra cair, o `ULTIMO_SLOT_PRECADO` do
handler está errado e o `make -C wte check` diz isso.

---

## 6. O vaivém dos cobradores não existe no `wte.exe` — resultado negativo

| Campo | |
|---|---|
| **O que diverge** | nada. O que precisava de decisão era o **enunciado da fase 6** |
| **Natureza** | nenhuma — não há divergência |
| **Decisão** | corrigir o enunciado, e **não** inventar o vaivém no port |

**O que se afirmava.** Que `Load`+`Save` troca os dois primeiros cobradores de
cada clube de ML (`OFS_KICKER`) e que gravar duas vezes volta ao início. Isso é
do **`ed.exe`**, medido pelo `newWe2002`; o `wte.exe` do Obocaman é outro
binário e outro caminho de código, e nunca tinha sido medido.

**Evidência.** [CORR-WTE-104](../../docs/tasks/CORR-WTE-104.md), 2026-08-25 — o
terceiro ponto, medido num time em que a troca **seria** visível: uma gravação
de tática contra duas, pelo
[`golden-24-gravacao-dupla`](../tests/roteiros/golden-24-gravacao-dupla.txt). As
duas imagens são **iguais** (0 bytes), e os seis cobradores do time 5 saem
intactos dos três estados: `[9, 5, 5, 5, 7, 5]` na ROM virgem, depois de uma
gravação e depois de duas. E as duas gravações **aconteceram** — 11.962 bytes
diferem da ROM virgem —, o que impede o zero de ser dois lados parados.

**Por que o time importa.** Até a CORR-WTE-104 o roteiro gravava no time 2, cujos
dois primeiros cobradores são iguais (`[7, 7, …]`). Ali a troca é a identidade e
a medição **não podia** responder em nenhum dos dois sentidos — a pendência que
a [WTE-TASK-34](../../docs/tasks/34-bateria-golden-completa.md) encaminhou era,
sem que ela soubesse, indecidível como estava escrita.

**Onde o teste sabe.** O `test_check_golden.py` lê o time do próprio roteiro e
**reprova** se os dois primeiros cobradores dele forem iguais. Se alguém mover o
`golden-24` de volta para um time cego, o `make -C wte check` diz isso antes de
o número virar doc.

---

## 7. As quatro candidatas que o enunciado deixou em aberto

O enunciado da task listava quatro hipóteses *"se a igualdade exata não sair"*.
Nenhuma virou entrada, e a razão de cada uma é medida — **hipótese que não se
confirma não vira divergência deliberada**, vira linha aqui dizendo que foi
conferida.

| Candidata | Veredito | Onde foi medido |
|---|---|---|
| tolerância de cor do render 2D | **a tolerância é ZERO**, e não há causa a nomear: 0 de 8.960 px no bitmap e 0 de 5.168 nas 16 amostras, inclusive **depois de calcular** (`--grade`) | [WTE-TASK-29](../../docs/tasks/29-camisa-e-bandeira-2d.md), com quatro recusas vistas |
| `TStaticText` no GTK2 (§8.9) | **fecha sem custo: nenhum dos 37 usa `Transparent`**. Nenhuma ação, nenhum item para a fase 6 | [WTE-TASK-12](../../docs/tasks/12-comparacao-visual.md) |
| rótulos cortados por fonte substituta | **não é divergência entre os dois lados** — acontece nos dois, pela mesma causa: `MS Sans Serif` não está instalada e a substituta é mais larga, com `AutoSize = False` no DFM. Sete formulários cortam; o `newWe2002` tem o mesmo sintoma no `ed.exe` sob Wine | [`visual.md`](visual.md), seção "Rótulos cortados" |
| truncamento de campo | **conferido em 2026-08-25, não é divergência.** Os quatro campos de texto têm limite que cabe no vetor, e os dois numéricos são guardados por validação de faixa no handler — não pelo `MaxLength`. O `- 1` do limite de tela é o **mesmo** `- 1` do decodificador, então o campo nunca recebe mais do que a leitura devolve | [WTE-TASK-36](../../docs/tasks/36-buffers-e-truncamento.md), em [`buffers.md`](buffers.md) |

**As quatro fecharam.** A última era a única ainda aberta quando esta seção foi
escrita, e a [WTE-TASK-36](../../docs/tasks/36-buffers-e-truncamento.md) a
fechou no dia seguinte, no sentido negativo: inventariados os seis campos de
digitação, nenhum trunca de forma que o original e o port discordem. O
[`dump_buffers.py`](../tools/dump_buffers.py) **aborta** se um limite passar a
não caber, se a validação de faixa sair de um handler, ou se um campo novo
aparecer sem entrada — então a afirmação continua conferida a cada
`make -C wte check`, em vez de valer só no dia em que foi medida.

---

## 8. A bateria de bytes não tem exceção nenhuma

Medido em 2026-08-25, e vale escrever porque é o resultado que ninguém procura:
**nenhum dos 23 roteiros declara `conhecida:`**. As 92 corridas da
[WTE-TASK-34](../../docs/tasks/34-bateria-golden-completa.md) fecharam com
**zero `REPROVOU`** e zero faixa de divergência declarada.

Isso não é sorte, e nem sempre foi assim: até 2026-08-20 dois roteiros
declaravam as faixas `1921862..1921862` e `2012984..2012985` — os dois remendos
de arranque que o oráculo gravava e o port não. A oitava passagem da
[WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md) achou os autores
(`0x00411616` no `FormShow` e `0x0040c19e` no `boton_dialogo_weClick`) e portou
os dois. **Declarar faixa que não diverge mais REPROVA** no
[`golden_veredito.py`](../tools/golden_veredito.py), então a ausência delas hoje
é afirmação medida, não omissão.

Consequência para esta task: o campo *"onde o teste sabe"* de toda entrada de
gravação diz "não precisa de exceção nomeada", e isso é verificável — o
`check_divergencias.py` recusa uma entrada que **declare** faixa sem que o
roteiro correspondente a tenha.

---

## 9. Uma exceção foi **removida**, não registrada

O grupo `pendente_32` do [`compara_tela.py`](../tools/compara_tela.py) isentava
`bandera`, `home1` e `home2` de reprovar, com a justificativa *"quem DESENHA é a
WTE-TASK-29"*. As duas tasks que o nome e o comentário citam **fecharam**, e a
isenção ficou.

Medido em 2026-08-25, `compara_tela.sh --habilitacao`:

| Controle | Grupo | Oráculo | Port | Veredito |
|---|---|---:|---:|---|
| `bandera` | `pendente_32` | 3840 | 3840 | **bate** |
| `home1` | `pendente_32` | 2328 | 2328 | **bate** |
| `home2` | `pendente_32` | 1012 | 1012 | **bate** |
| `iguala_nombres` | `glifo_cinza` | 518 | 0 | divergência deliberada |

Os três **batem**, com números idênticos dos dois lados. A isenção não protegia
mais nada: ela sobreviveu à própria causa.

**Por isso eles não viraram entrada — viraram remoção.** Escrever entrada de
divergência deliberada para algo que não diverge seria o defeito desta task pelo
avesso: o documento existe para que nenhuma divergência seja desconhecida, e
uma entrada falsa faz alguém procurar um problema que não existe. É a mesma
família que a terceira passagem da
[WTE-TASK-31](../../docs/tasks/31-fechamento-fase-4.md) batizou — **prosa
vencida**, documento que envelhece sozinho enquanto outro o lê como estado
corrente.

Os três controles passaram para `segue_nacional`, que é o que a spec deles diz,
e agora **reprovam** se voltarem a divergir.

---

## 10. O `ficha_warning` não é levantado — o port aplica os remendos sem perguntar

| Campo | |
|---|---|
| **O que diverge** | o aviso de tamanho de imagem, que o original mostra na carga e o port não |
| **Natureza** | escolha de comportamento em produção |
| **Decisão** | não reproduzir |

**Razão.** O `MainForm.FormShow` do original levanta o `ficha_warning` quando a
imagem não tem o tamanho esperado, e **pergunta antes** de aplicar os dois
remendos de arranque. O port os aplica direto. Reproduzir o modal exigiria uma
resposta de quem está do outro lado, e o harness golden não tem quem responda:
todo roteiro que abre imagem passaria a depender de um clique a mais, e o que
o gate mede — a gravação — não mudaria com ele. **É por isso que a gravação
bate byte a byte:** os dois lados aplicam os mesmos remendos, e a diferença
está só em o original ter perguntado.

**Evidência.** Achado 8 da segunda passada da reconferência de UI
([`visual.md`](visual.md)), medido em 2026-08-25: `Show`/`ShowModal` varrido em
`wte/src/` não encontra **nenhum** chamador do `ficha_warning`, contra o
`MainForm.FormShow` do original, que o levanta na carga. O formulário existe no
port — é um dos 18 gerados —, e é o **único** que aparece só do lado do
oráculo na tabela de capturas.

**Onde o teste sabe.** No `golden-01-arranque`, e ele sabe **pelo silêncio**: o
roteiro do lado oráculo dispensa o aviso com um clique em `(222,148)` e o do
lado port não tem esse passo, porque não há o que dispensar. Os dois chegam à
mesma imagem — controle e golden verdes na japonesa —, e é essa igualdade que
prova que o modal não muda byte nenhum. Um port que passasse a perguntar
quebraria o roteiro do lado port, que é o alarme.

---

## 11. `TStaticText` desabilitado pinta fundo próprio no GTK2

| Campo | |
|---|---|
| **O que diverge** | a cor de fundo de **1** dos 37 `TStaticText` quando ele está desabilitado |
| **Natureza** | limitação de plataforma (widgetset) |
| **Decisão** | não reproduzir |

**Razão.** É a mesma família da **§2** — o widgetset decide sozinho como pintar
o estado desabilitado, e nenhuma propriedade do DFM controla isso. No Win32 o
`TStaticText` desabilitado herda o fundo do formulário; no GTK2 ele pinta o
cinza do tema. Igualar exigiria pintar o fundo à mão no `OnPaint` de um
controle que o original nunca customizou.

**E a prova de que é o estado, não o controle**, está ao lado: o `base_team`
também tem `Enabled = False` no DFM e **bate** nos dois lados — porque o app o
reabilita em tempo de execução. O que diverge é a pintura do desabilitado, e só
ela.

**Evidência.** Achado 11 da reconferência de UI, medido pelo
[`check_carregado.py`](../tools/check_carregado.py) em 2026-08-25, com a lógica
ligada e o fundo de execução por baixo: dos 37 `TStaticText` dos 18
formulários, **um** diverge — o `help_team` (`Time Res.`), que sai `#76B6FF`
(a cor do formulário) no oráculo e `#DCDAD5` (o cinza do tema) no port.

**Onde o teste sabe.** No próprio `check_carregado.py`, que compara a cor de
fundo dos `TStaticText` dos dois lados sobre a captura com a lógica ligada. Ele
mede e relata; o número que importa é o **1 de 37** — se um segundo controle
entrar na divergência, a diferença aparece na comparação, e a causa não será
mais "o estado desabilitado do widgetset", porque os outros 36 continuam
batendo.
