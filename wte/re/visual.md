# Comparação visual dos 18 formulários — WTE-TASK-12

Inspeção humana, um veredito por formulário, como manda a §6 do
[`PLAN-WTE-LAZARUS.md`](../../docs/PLAN-WTE-LAZARUS.md): **sem tolerância de pixel**.
`MS Sans Serif` não está instalada no host, o GTK2 e o Wine substituem por
fontes diferentes, e diferença de pixel é garantida sem informar nada.

Capturas em [`visual/lazarus/`](visual/lazarus) (18) e
[`visual/original/`](visual/original) (4). **As 22 estão commitadas e continuam
válidas; o que não existe mais é a maneira de refazer as 18 de uma vez.** Elas
saíram do `wte/tools/capture_forms.sh`, que dependia do andaime `--show` do
`wtemain.pas`, e a
[WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md) removeu os dois ao pôr
navegação de verdade no lugar do andaime — o `--show` tinha dono e prazo desde
que nasceu.

Quem dirige o app hoje é o
[`compara_tela.sh`](../tools/compara_tela.sh), que leva os dois lados ao
mesmo time e captura a janela inteira; ele alcança o `MainForm`, não os 18. Os
outros formulários voltam a ser capturáveis quando a navegação chegar a eles,
que é a [WTE-TASK-37](../../docs/tasks/concluidos/37-reconferencia-de-ui.md) — a
reconferência da UI com a lógica ligada.

---

## Estado: 18 do port, 4 do original — e o que impede os outros 14

| Lado | Capturado |
|---|---|
| App Lazarus | **18 de 18**, capturadas por `--show`, o andaime da WTE-TASK-11 — que a WTE-TASK-25 removeu depois; as capturas ficaram, o andaime não |
| `we-team-editor.exe` | **4 de 18**: `MainForm`, `ficha_warning`, `ficha_about`, `ficha_salida` |

Os 14 restantes **não são inalcançáveis por falta de saber o gatilho** — o
gatilho de cada um está no DFM, e o mapa de coordenadas foi levantado dali. Eles
são inalcançáveis porque **o original quebra antes**, e isso é o achado 1.

---

## Achado 1 — o original não sobrevive a selecionar um time neste Wine

Medido, determinístico, com cópia **byte-idêntica ao ROM de `roms/`**:

```
0024:trace:seh:dispatch_exception code=c0000005 addr=005F5EA0 ip=005f5ea0
0024:trace:seh:dispatch_exception  info[0]=00000000  info[1]=0000001c
0024:warn:seh:dispatch_exception EXCEPTION_ACCESS_VIOLATION (code=c0000005)
   … 310 vezes, as seguintes com addr=00000000 ip=00000000 …
0024:err:virtual:virtual_setup_exception stack overflow 448 bytes
```

A primeira é uma **leitura em ponteiro nulo + 0x1c** (`eax=00000000`,
`info[1]=0000001c`); as seguintes são chamada para o endereço 0 — o próprio
tratador refalha e recursa até estourar a pilha. **310 exceções, sempre 310.**
O processo fica `<defunct>`; as janelas X sobrevivem órfãs sob o `wineserver`,
o que faz o app **parecer vivo** numa captura.

Reproduzir:

```sh
cd we-team-editor && WINEPREFIX=…/work/wineprefix-wte WINEARCH=win32 \
  WINEDEBUG=+seh wine we-team-editor.exe
# abrir a ROM, "Sim" no aviso, "Ok" no splash, escolher um time no combo
```

**O que foi descartado como causa:**

| Suspeita | Como caiu |
|---|---|
| cópia de trabalho corrompida | repetido com cópia recém-tirada de `roms/`: mesmas 310 |
| meus cliques em `TSpeedButton` | sem selecionar time, `Sobre...` abre o `ficha_about` e o `Sair` abre o `ficha_salida` normalmente |
| estado sujo do Wine | repetido com `wineserver -k` e prefix novo |

**Confundidor a registrar:** o único runner disponível é
`wine-experimental.bleeding.edge.9.0.93696.20240429 (TkG Plain)`, que o próprio
log anuncia como versão de teste — não há Wine de sistema nem outro runner
instalado. **Se o crash é do app ou do Wine, esta máquina não tem como
distinguir.** Instalar outro runner é decisão do usuário.

**Consequência, e era grave:** quase toda operação do editor começa por
escolher um time. Enquanto isto não se resolveu, o oráculo A não executou nem
os 14 formulários desta task nem a maior parte da bateria golden. Entregue à
[WTE-TASK-22](../../docs/tasks/concluidos/22-harness-golden.md).

**Resolvido em 2026-08-10 pela CORR-WTE-044, e o que resolveu foi a imagem:**
com `roms/japanese-shift-jis.bin` o mesmo roteiro de troca de time dá **zero**
violação de acesso, contra 49.749 com a europeia. A causa medida — ponteiro
global sobrescrito pela carga do time, não controle faltando — está em
[`crash-causa.md`](crash-causa.md). O confundidor do runner acima **não** foi
eliminado, e deixou de importar para esta decisão: o mesmo Wine roda os dois
casos.

### O que o original alcança sem time, e foi o que rendeu as 4 capturas

`ficha_warning` e `ficha_about` saem no caminho de carga; `MainForm` fica na
tela; e `Sair` abre o `ficha_salida`, que se fecha em "Nao". Os `dorsal1..23`,
únicos com `Enabled = True` no DFM fora dos dois `TSpeedButton` do topo, não
abrem nada sem time — o `Enabled` do DFM é o estado de projeto, e o app decide
o resto em runtime.

---

## Achado 2 — aceitar o aviso de tamanho **grava na imagem**

Descoberto por acidente e medido de propósito. Uma cópia byte-idêntica a
`roms/golden-european-deluxe.bin`, aberta no original, com "Sim" no aviso de
tamanho e **nenhuma edição**:

| Passo | Imagem |
|---|---|
| escolher o arquivo no diálogo | idêntica |
| **"Sim" no aviso de tamanho** | **11.952 bytes divergem** |
| fechar o splash | sem mudança nova |
| selecionar um time | sem mudança nova |

Faixa `11796..26527` (offsets 0-based, inclusivos; o `cmp -l` imprime
`11797..26528`, porque numera bytes a partir de 1), **setores 5 a 11** — região
de metadado ISO9660, não de dado do jogo. Determinístico: a contagem e a faixa
se repetem exatamente entre sessões.

A base importa porque é como a faixa vai ser consumida: a exceção declarada do
`newWe2002` (`tools/golden_check.sh`, `KNOWN_START`/`KNOWN_END`) é offset
0-based. Para medir na base certa, não use os extremos do `cmp -l` — use:

```sh
python3 - roms/golden-european-deluxe.bin work/wte-golden-european-deluxe.bin <<'PY'
import sys
a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
d = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
print('n:', len(d), 'offsets 0-based:', d[0], '..', d[-1],
      'setores:', d[0] // 2352, 'a', d[-1] // 2352)
PY
# n: 11952 offsets 0-based: 11796 .. 26527 setores: 5 a 11
```

O aviso dispara **sempre** com as imagens deste repositório: o editor espera
474.431.328 bytes e nenhuma das duas tem esse tamanho — a europeia medida aqui
tem 474.784.128 e a japonesa, 307.187.664. Ou seja, o caminho que grava é o
caminho normal.

**Tudo acima é a europeia.** Na japonesa — a que a
[WTE-TASK-22](../../docs/tasks/concluidos/22-harness-golden.md) fixa no gate — os mesmos
11.952 bytes aparecem, recortados pelos limites de setor em sete faixas, mais
3 bytes que a europeia não tem. A conta por faixa está na seção 2 daquela task.

**Isto muda o desenho do golden test**, e vai para a
[WTE-TASK-22](../../docs/tasks/concluidos/22-harness-golden.md): *original contra original*
continua dando zero (os dois lados gravam os mesmos 11.952 bytes), mas
*original contra imagem intocada* **não** dá — e o port terá de reproduzir
esses bytes ou o harness terá de declarar a faixa, como o `newWe2002` faz com
os 16 bytes do slot 64.

Por que grava não é pergunta desta task. É da spec de `MainForm.FormCreate`
(`0x004107c8`), na WTE-TASK-25.

---

## Achado 3 — vários formulários recebem a cor de fundo em tempo de execução

O original mostra o `MainForm` **azul**, o `ficha_warning` **vermelho** e o
`ficha_salida` **amarelo**. Os três DFM declaram `Color = clBtnFace`, e o
`clBtnFace` do Wine é o cinza claro que aparece no diálogo *Abre* do próprio
app. A cor não vem do formulário: é atribuída depois de a instância existir.

O `ficha_salida` corrige o palpite da primeira medição. A heurística inicial —
"declara `clBtnFace` **e** tem rótulo `Font.Color = clWhite`" — dava cinco
candidatos; o `ficha_salida` não tem nenhum rótulo branco (o texto é preto) e
mesmo assim é recolorido. **A heurística é piso, não teto: o recolorir em
runtime é largo, e só a captura do original diz de quais formulários.**

Os candidatos que a heurística achava, todos com `FormCreate` conhecido desde a
WTE-TASK-04:

| Formulário | Rótulos brancos | `FormCreate` |
|---|---|---|
| `estrategia` | 35 | `0x004090fc` |
| `ficha_color` | 6 | `0x00405dcc` |
| `ficha_warning` | 3 | `0x00402cdc` |
| `ficha_warning_2` | 3 | `0x00408d88` |
| `MainForm` | 3 | `0x004107c8` |
| `ficha_salida` (fora da heurística) | 0 | `0x00402f08` |

**Evidência:** observação de tela nos quatro que o original alcança, cruzada com
a tabela estática. Que seja o `FormCreate` a escrever `Color` é a hipótese mais
econômica — é o único handler que roda antes de a janela aparecer —, **não** um
fato medido. O disassembly desses endereços é da
[WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md).

> **Resolvido em 2026-08-11 pela WTE-TASK-25, e a hipótese estava certa nos dois
> sentidos — inclusive no de ser piso.** O
> [`dump_arranque.py`](../tools/dump_arranque.py) leu os 18 `FormCreate` /
> `FormShow`: **11** deles têm por corpo inteiro uma chamada a
> `TControl::SetColor` sobre a própria instância, e mais 3 pintam junto com
> outras coisas. São 13 formulários recolorados, não os 6 da heurística — a
> tabela por formulário está em [`arranque.md`](arranque.md), com o valor de
> cada cor. A do `MainForm` não vem do `FormCreate`, e sim do `FormShow`, que
> pinta a si, ao `cuadro_dialogo_we` e ao `grupo_barras` de `$00ffb676`.
>
> O único dos 18 que **não** pinta nada é o `ficha_about`, cujo `FormCreate` é
> um `ret` — e é por isso que ele é o único formulário que fica com o
> `clBtnFace` do projeto na tela, nos dois lados.

Os quatro que declaram cor no próprio DFM — `jugador`, `ficha_error` e
`ficha_error2` em `clNavy`, `ficha_info` em `clSilver` — renderizam certo na
LCL, o que é a contraprova de que o caminho de cor funciona.

---

## Achado 4 — os 37 `TStaticText`: nada a fazer, e a §8.9 fecha sem custo

A §8.9 manda conferir os 37 na fase 2, porque `TStaticText` no GTK2 trata
transparência e cor de fundo diferente do Win32. Medido nos 18 DFM:

| Medida | Valor |
|---|---|
| Instâncias | **37** (36 nomeadas + 1 sem nome, no `MainForm`) |
| Com `Transparent` | **0** |
| Com `Color` próprio e `ParentColor = False` | 27 |
| Herdando a cor do pai | 10 |
| Com `OnClick` | 25 |
| Com `OnMouseDown` | 23 |

**O risco da §8.9 não tem nenhuma instância.** Ele é sobre transparência, e
nenhum dos 37 pede transparência: 27 declaram a própria cor e a LCL a aplica —
visível no `MainForm`, onde a faixa "WE2002 Team Editor" e a do endereço do
site saem como retângulos coloridos opacos —, e os 10 restantes herdam a do
pai, que é o que o Win32 também faz.

**Decisão: nenhuma ação.** Não trocar `TStaticText` por `TLabel`, não mexer no
`dfm2lfm.py`, não abrir item para a fase 6. Os 27 opacos só ficarão *com a cor
certa* quando o pai tiver a cor de execução do achado 3 — mas isso é do pai,
não do `TStaticText`.

O que a medida entrega para a fase 4 é outra coisa: **25 dos 37 têm `OnClick`**.
No original o `TStaticText` é usado como widget clicável, não como rótulo.

---

## Achado 5 — os 118 blobs aparecem

Critério herdado da [WTE-TASK-10](../../docs/tasks/concluidos/10-conversor-dfm-para-lfm.md),
que provou a preservação byte a byte e não podia provar a exibição.

Os 118 se dividem em 18 `Icon.Data`, 59 `Glyph.Data` e 41 `Picture.Data`, e os
18 `.lfm` carregam a mesma contagem por formulário que os 18 `.dfm`.

- Os **100 desenháveis** (`Glyph` + `Picture`) aparecem: em todo formulário que
  tem blob, o blob está na tela. Os casos mais exigentes são os que mais
  provam — o desenho do Obocaman no `ficha_about`, o retrato do `jugador`, o
  campo tático da `estrategia`, o logo *Winning Eleven* e os 24 glifos de botão
  do `MainForm`.
- Os **18 `Icon.Data`** não são julgáveis no `:99`: ícone de janela é desenhado
  pela barra de título, e sem window manager não há barra de título. Isso vale
  igualmente para o original.

Contar blob a blob por screenshot não é possível onde há sobreposição (as 20
camadas de `Picture` do `jugador`); a contagem fina fica para a WTE-TASK-37.

---

## Veredito por formulário

Coluna **Original**: `sim` = capturado; `DFM` = referência estática, porque o
original não chega lá (achado 1).

| Formulário | Original | Veredito |
|---|---|---|
| `MainForm` | sim | **Fundo divergente por handler não implementado** (achado 3). Layout, blobs e controles conferem: o banner, o logo *Winning Eleven*, os 24 glifos e os 11 `Picture` aparecem. Sem controle faltando |
| `estrategia` | DFM | Campo tático, 11 marcadores, lista de formações e os 3 glifos renderizam. Os rótulos brancos do canto inferior esquerdo ficam ilegíveis — mesmo motivo do `MainForm` |
| `jugador` | DFM | **Sem ressalva.** `Color = clNavy` vem do DFM e a LCL aplica; os 59 rótulos brancos ficam legíveis, o retrato e as 20 camadas de `Picture` aparecem, as 20 barras e os spins estão no lugar |
| `ficha_color` | DFM | Renderiza inteiro: 4 grupos de rádio, 4 combos, as setas, os 7 glifos. Os 3 `TStaticText` (R/V/A) aparecem com a cor de fonte do DFM |
| `ficha_dorsal` | DFM | Sem ressalva. Barra, número e o glifo do `Ok` |
| `ficha_enlaza` | DFM | Sem ressalva. Texto quebra em duas linhas como no DFM |
| `ficha_info` | DFM | `Color = clSilver` do DFM aplicado. Duas das quatro linhas de atalho **cortam à direita** |
| `ficha_info2` | DFM | Duas linhas **cortam à direita** |
| `ficha_info3` | DFM | Sem ressalva |
| `ficha_info4` | DFM | Duas linhas **cortam**, uma em cada extremidade |
| `ficha_error` | DFM | `clNavy` do DFM aplicado, texto branco legível. A linha única **corta nas duas pontas** — `Alignment` centralizado com `AutoSize = False` |
| `ficha_error2` | DFM | `clNavy` aplicado. Sem corte |
| `ficha_salida` | **sim** | Texto, os dois `TBitBtn` e os glifos batem. **Fundo divergente**: o original é amarelo, o port cinza (achado 3) |
| `ficha_movertodos` | DFM | Sem ressalva |
| `ficha_creditos_equipo` | DFM | Sem ressalva |
| `ficha_warning` | sim | **Fundo divergente**: o original pinta vermelho, e os 3 rótulos `clWhite` ficam ilegíveis em cinza. Texto também **corta à direita** |
| `ficha_warning_2` | DFM | Mesmo caso do `ficha_warning`, com 3 rótulos brancos. Uma linha **corta** |
| `ficha_about` | sim | **Praticamente idêntico ao original.** Fundo ciano, o desenho do Obocaman, o texto e o glifo do `Ok` no lugar. A única diferença é a faixa de moldura não pintada em volta |

**Nenhum controle faltando, nenhum sobrando, nenhum fora de posição nos 18.**
Onde a captura do original não existe, quem sustenta isso é o DFM, e a garantia
é mais forte que screenshot: os 18 `.lfm` carregam `Left`/`Top`/`Width`/
`Height`/`ClientWidth`/`ClientHeight` **iguais aos do DFM** (conferido nos 18
cabeçalhos), e `dfm2lfm.py --check` prova que nenhum foi editado à mão.

---

## Duas armadilhas de captura, medidas aqui

**1. `import -window <id>` devolve preto, sem erro.** Sem window manager no
`:99` não há empilhamento garantido, e quase todo formulário nasce dentro da
área do `MainForm` (544×495 a partir de 132,72). O X entrega o conteúdo
indefinido da região obscurecida e o PNG sai todo preto — sem mensagem nenhuma.
É o mesmo sintoma que o [`CLAUDE.md`](../../CLAUDE.md) registra para o modal do
`ed.exe`, com outra causa. A saída, e o que o `capture_forms.sh` fazia:
`xdotool windowraise` e recorte de `-window root`. **A ferramenta saiu na
WTE-TASK-25; a armadilha ficou** — o [`compara_tela.sh`](../tools/compara_tela.sh)
captura `-window root` e recorta pela geometria da janela pela mesma razão.

**2. Mapear janela do Wine por fora não faz a VCL pintar — nem com expose
forçado.** As 18 janelas X do original existem desde o arranque (a VCL cria o
handle em `CreateForm`), todas `IsUnMapped`. `xdotool windowmap` deixa a janela
`IsViewable` e a captura passa a funcionar, **e sai preta**. Tentado de novo com
`xrefresh`, que força `Expose` na tela inteira: o que aparece no recorte é o
**`MainForm` por trás**, repintado — a janela mapeada continua sem pintar,
porque a VCL não a considera exibida. Atalho que não existe; medido duas vezes,
não insistir.

---

## Rótulos cortados — esperado, e listado

Sete formulários cortam texto: `ficha_warning`, `ficha_warning_2`,
`ficha_error`, `ficha_info`, `ficha_info2`, `ficha_info4` e, em uma linha, o
`MainForm`.

**É esperado e não é achado.** `MS Sans Serif` não está instalada; a substituta
é mais larga, e o rótulo tem `AutoSize = False` com largura fixa do DFM. O
`newWe2002` tem o mesmo sintoma no `ed.exe` sob Wine, com "Position" virando
"Positior". O `ficha_error` corta nas **duas** pontas porque o `Alignment` é
centralizado.

Não corrigir: alargar rótulo mudaria a geometria, que é o critério de
fidelidade da §5.

---

## Moldura: a janela do port é maior que a do original

A janela X do app Lazarus mede mais que a área de cliente declarada — o
`MainForm` sai 544×495 para `ClientWidth`/`ClientHeight` de 522×475. A LCL
reserva a moldura que o GTK informa, e sem window manager ninguém a desenha:
sobra uma faixa não pintada em volta, visível em toda captura do port.

Não é divergência de layout — os controles estão nas coordenadas do DFM, e a
área de cliente é a mesma. A faixa some com window manager. Registrado para não
voltar como "achado" na fase 6.

---

## Resumo

| Pergunta da task | Resposta |
|---|---|
| Controle faltando ou sobrando? | Não, nos 18 |
| Posição ou tamanho errado? | Não — `.lfm` carrega o DFM verbatim, com `--check` |
| Cor de fundo diferente? | Sim, e explicada: vem do runtime (achado 3) |
| Blobs aparecem? | Os 100 desenháveis, sim (achado 5) |
| `TStaticText` decidido? | Sim: nenhuma ação (achado 4) |
| Rótulo cortado? | Em 7, esperado, listado |
| Sufixo ` [Lazarus]` contado como achado? | Não — divergência deliberada da WTE-TASK-11, e sem window manager a captura nem o mostra |
| Os 18 dos dois lados? | **Não, e não por falta de método:** 18 do port, 4 do original, porque o oráculo quebra ao carregar um time (achado 1) |

## O que sai daqui para outras tasks

| Achado | Para quem |
|---|---|
| 1 — o oráculo quebra ao selecionar time | [WTE-TASK-22](../../docs/tasks/concluidos/22-harness-golden.md), **bloqueante** |
| 2 — aceitar o aviso grava 11.952 bytes | [WTE-TASK-22](../../docs/tasks/concluidos/22-harness-golden.md) e [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md) |
| 3 — cor de fundo em runtime | [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md) |
| 4 — 25 dos 37 `TStaticText` são clicáveis | fase 4 |
| 5 — contagem fina de blob sobrepostos | [WTE-TASK-37](../../docs/tasks/concluidos/37-reconferencia-de-ui.md) |
| as 14 capturas do original | [WTE-TASK-37](../../docs/tasks/concluidos/37-reconferencia-de-ui.md), **se** o achado 1 se resolver |


---

# Segunda passada — WTE-TASK-37: os 18 com a lógica ligada

A primeira passada (acima) conferiu os formulários **vazios**, com o andaime
`--show`. Esta confere com a **imagem carregada e um time selecionado**, que é
quando o problema aparece — e o que ela achou não estava escondido: estava
esperando dado na tela.

**As capturas novas estão em [`visual/carregado/`](visual/carregado)** — 19 do
oráculo e 18 do port, tiradas pelo verbo `! foto` do
[`../tools/roteiro.sh`](../tools/roteiro.sh), que os dois lados compartilham, e
dirigidas pelo [`../tools/captura_ui.sh`](../tools/captura_ui.sh) sobre a ROM
japonesa. Refazer:

```sh
bash wte/tools/captura_ui.sh ui-01-telas ui-02-transferencia ui-03-avisos
python3 wte/tools/check_carregado.py
python3 wte/tools/check_retorno.py
```

As duas medições geradas são [`carregado.md`](carregado.md) (alcance, tamanho,
cor de fundo, rótulos) e [`retorno.md`](retorno.md) (`Default`, `Cancel` e
ordem de tabulação). **Todo número desta seção saiu de uma das duas.**

## Cobertura: 15 pares, e por que os três que faltam faltam

| | Quantos |
|---|---:|
| Formulários | 18 |
| Fotografados dos **dois** lados, no mesmo estado | **15** |
| Só do oráculo | 1 (`ficha_warning`) |
| De nenhum dos dois | 2 (`ficha_enlaza`, `ficha_info4`) |

A primeira passada conseguiu 4 do oráculo, e não por falta de método: o
`wte.exe` morria ao trocar de time na ROM europeia. Com a japonesa —
CORR-WTE-044 — o mesmo roteiro não produz violação de acesso nenhuma, e os 15
pares saíram de três roteiros.

Os três roteiros levam os dois lados ao **mesmo estado** e fecham cada modal
pela **tecla** (`Escape` = `Cancel`, `Return` = `Default`), o que dispensa a
coordenada do botão — e é onde a moldura do Wine faria os dois lados
divergirem:

| Roteiro | O que ele alcança |
|---|---|
| `ui-01-telas` | o time 2 (seleção), `estrategia`, `jugador`, `ficha_dorsal`, `ficha_color`, `ficha_info`, `ficha_about`, `ficha_creditos_equipo`, `ficha_salida` |
| `ui-02-transferencia` | o time 95 (clube), `ficha_movertodos`, `ficha_error2`, `ficha_error`, `ficha_info2` |
| `ui-03-avisos` | `ficha_warning_2` (par de cores de radar) e `ficha_info3` (fim do cálculo de preços) |

## Achado 6 — os 151 `TLabel` com `Color` não pintam no port

**É o achado da task, e é a §8.9 do plano generalizada.** Ela manda conferir os
37 `TStaticText` porque o GTK2 trata cor de fundo diferente do Win32; a primeira
passada mediu os 37, achou que nenhum pedia transparência, e fechou (achado 4).
O que ninguém tinha contado é que **151 `TLabel` declaram `Color` pelo mesmo
DFM** — quatro vezes mais controles, na mesma classe de problema.

Medido nos 15 pares: **68 dos 178 rótulos com `Color` mostram cor de fundo
diferente entre os dois lados**, e sempre no mesmo sentido — no port o rótulo
some no fundo do formulário.

| Formulário | rótulos com `Color` | divergentes | o que se perde na tela |
|---|---:|---:|---|
| `jugador` | 59 | **31** | as faixas alternadas (`#2882D7`) atrás das 16 habilidades |
| `estrategia` | 43 | **18** | as faixas alternadas da tabela de estratégia |
| `ficha_color` | 34 | **18** | a faixa `seleccion` (`#000080`) e os `colcopN` pretos |
| `ficha_dorsal` | 1 | **1** | o retângulo branco atrás do número |
| `MainForm` | 27 (`TStaticText`) | 0 | — |

**A causa é um *default* de widgetset sobre uma propriedade que o DFM não
declara.** Nenhum dos 178 declara `Transparent`. No VCL o `TLabel` nasce
`Transparent = False` e pinta o `Color`; na LCL ele nasce `Transparent = True`
e não pinta. O `TStaticText` não tem o problema — por isso os 27 do `MainForm`
batem, e por isso a medida da primeira passada, restrita a eles, fechou verde.

**Decisão: corrigir no gerador.** O
[`../tools/dfm2lfm.py`](../tools/dfm2lfm.py) deve emitir `Transparent = False`
para `TLabel` que declare `Color` e não declare `Transparent` — propriedade
sintetizada, com a razão escrita, que é o que um conversor existe para fazer.
Volta para a [WTE-TASK-10](../../docs/tasks/concluidos/10-conversor-dfm-para-lfm.md), e o
critério de aceite já é mecânico: `rotulos_divergentes` zerado em
[`carregado.tsv`](carregado.tsv) depois de refazer as capturas.

## Achado 7 — os dois combos de radar do `estrategia` saem VAZIOS

A [`spec/estrategia.ComboBoxDrawItem.md`](spec/estrategia.ComboBoxDrawItem.md)
ficou `nao portado` com a justificativa de que a **decisão** — o port desenhar,
ou deixar a LCL desenhar — pertencia a esta task. Ela está tomada, e o que a
mediu foi a captura:

| | `ComboBox1` (Casa) |
|---|---|
| oráculo | fundo `#808080`, retângulo de amostra da cor (16×11 px) e o texto branco por cima |
| port | **nada** — 1.896 px de `#DCDAD5`, o cinza do tema |

A leitura de 2026-08-24 — *"a LCL desenha o item pelo padrão dela"* — está
errada, e a diferença importa: `Style = csOwnerDrawFixed` **sem** `OnDrawItem`
não desenha item nenhum. O controle não fica com aparência diferente; ele fica
**em branco**.

**Decisão: implementar.** O que o combo mostra é a cor de radar do time, e ela é
dado que o ` Accept` grava na imagem (2 + 2 bytes, `estrategia.BitBtn3Click`) —
um controle que esconde o valor que está prestes a gravar não é diferença
cosmética. **O corpo não entra aqui**: ele é fase 4, e escrevê-lo a partir desta
captura seria transcrever um palpite (quais `TColor`, qual retângulo, onde o
texto) num arquivo que o projeto trata como medido. A medida acima é o critério
de aceite; o corpo sai do disassembly de `0x0040adec`.

## Achado 8 — dois formulários não têm chamador nenhum no port

`Show`/`ShowModal` varrido em `wte/src/`:

| Formulário | quem o abre no port | no original |
|---|---|---|
| `ficha_warning` | **ninguém** | o `MainForm.FormShow` o levanta na carga — é o aviso de tamanho |
| `ficha_enlaza` | **ninguém** | alcançado pelo `MainForm.mostrar_jugadorClick`, cuja spec segue `aberto` nessa rota |

O do `ficha_warning` é consequência de uma decisão já tomada e não registrada: o
port aplica os dois remendos de arranque **sem perguntar**, e é por isso que a
gravação bate byte a byte. O do `ficha_enlaza` é o que a
[WTE-TASK-30](../../docs/tasks/concluidos/30-handlers-auxiliares.md) deixou escrito por
medir — *"qual condição faz o `mostrar_jugadorClick` abrir o modal"*.

Os dois vão para a [WTE-TASK-35](../../docs/tasks/concluidos/35-divergencias-deliberadas.md):
o primeiro como divergência deliberada a registrar, o segundo como rota ainda
não portada.

## Achado 9 — o time-modelo de Master League mostra três campos vazios

Índice 95 (`95 Master L.`), o mesmo estado dos dois lados:

| Campo | oráculo | port |
|---|---|---|
| Nome1 | `?????` | *(vazio)* |
| Nome2 | `PATAGONIA` | *(vazio)* |
| Nome3 | `PTA` | *(vazio)* |

A causa está na camada de dados, não na tela: `NomeDoTime` cai em
`Jogo.ml_default` para índice ≥ 95, e o `dump_estado` mostra
`ml_default.names[0] = 20:` — **vazio**. O oráculo lê alguma coisa ali e o port
não. Volta para a [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md), com
a [WTE-TASK-19](../../docs/tasks/concluidos/19-os-50-offsets-restantes.md) do lado: o que
falta é o offset do nome do modelo de ML, não o caminho de tela.

## Achado 10 — as listas de jogador do painel perdem o número na frente

`lista_jugadores_1`, mesmo time e mesmo slot dos dois lados:

| | texto do item selecionado |
|---|---|
| oráculo | `1 P??w????Y` |
| port | `P??W????Y` |

Duas diferenças numa linha só: o **prefixo de número** e a **caixa da letra**.
O `PreencheJogadores` do port monta o item com `NomeFiltrado` e nada mais. Volta
para a [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md) — é a rotina
`0x0040b2d8`, a mesma cuja tabela de filtro a CORR-WTE-081 já ajustou.

## Achado 11 — `TStaticText` desabilitado pinta fundo próprio no GTK2

A releitura do achado 4 com o fundo de execução por baixo, medida pelo
`check_carregado.py`: dos 37 `TStaticText`, **um** tem cor de fundo diferente
entre os dois lados — `help_team` (`Time Res.`, `Enabled = False` no DFM), que
sai `#76B6FF` (a cor do formulário) no oráculo e `#DCDAD5` (o cinza do tema) no
port.

Não é o mesmo caso do achado 6, e a prova está ao lado: `base_team`, também
`Enabled = False` no DFM, **bate** — porque o app o reabilita em tempo de
execução. O que diverge é a pintura do estado **desabilitado**, que nenhuma
propriedade do DFM controla. É a mesma família da divergência 2 já registrada
(os cinco glifos que não acinzentam), e vai para o mesmo lugar.

**A decisão do achado 4 continua de pé para os outros 36.**

## Achado 12 — o que o `Return` alcança, medido nos 18 e em bytes

| Medida | Valor |
|---|---:|
| Formulários com botão `Default = True` | **13** de 18 |
| Com `Cancel = True` | 7 |
| Cujo `Default` dispara handler que grava **na imagem** | **1** (`ficha_color`) |
| Controles com `TabOrder` | 142 |
| Formulários com ordem de tabulação diferente entre DFM e LFM | **0** |

**A mordida que o `newWe2002` levou não se repete aqui, e o motivo é o
formato.** Lá, `PUSHBUTTON` do `.rc` não carrega "sou o default", o Qt tornava
todo botão `autoDefault` e o `Return` clicava um botão arbitrário — num diálogo
onde um dos candidatos aplicava formação predefinida. No DFM, `Default` e
`Cancel` são propriedades explícitas, e o `dfm2lfm.py` as copia verbatim; o
`check_retorno.py` confere as duas nos 18 e aborta se divergirem.

**O risco que o enunciado nomeava não existe:** `estrategia` — o formulário do
`lista_formacionesClick` destrutivo — **não tem botão `Default`**, e nenhuma
lista dispara `OnClick` por `Return`.

**O que existe é outro, e é do original:** o `OK` do `ficha_color` é
`Default = True` desde o DFM de 2002, e o handler dele grava **383 bytes por
time**. Chega-se lá por `Return` nos dois lados — então a pergunta que sobra
não é se dá para chegar, é se os dois gravam o mesmo. Medido em bytes pelo
roteiro `golden-25-retorno`, que é o `golden-16-cor` fechando o editor por
tecla em vez de clique.

## Achado 13 — a moldura do Wine, medida, e o que ela explica

Sete formulários saem 6 px mais largos e 32 px mais altos no oráculo — o Wine
desenha a moldura **por dentro** da janela X, e a LCL sem window manager não
desenha nenhuma:

`ficha_dorsal`, `ficha_error`, `ficha_error2`, `ficha_info`, `ficha_info2`,
`ficha_info3`, `ficha_salida`.

Os cinco que declaram `Width`/`Height` em vez de `ClientWidth` no DFM
(`ficha_creditos_equipo`, `ficha_enlaza`, `ficha_info4`, `ficha_movertodos`,
`ficha_warning_2`) medem o mesmo dos dois lados, porque o número do DFM já
inclui a moldura — e é por isso que a área de cliente deles é **menor** no
oráculo. Daí vem a única coisa que parecia controle faltando na comparação: o
`ficha_creditos_equipo` mostra uma barra de rolagem horizontal no oráculo e não
no port. Não há barra nenhuma no DFM: é o `AutoScroll` do formulário reagindo a
92 px de cliente contra 124.

O `check_carregado.py` transforma isso em regra e **aborta** se uma captura não
for nem o cliente nem o cliente mais a moldura — sem isso, todo retângulo de
controle mediria 3 px à esquerda e 29 acima do lugar, e o resultado sairia
plausível e errado.

## O que **não** mudou, e é resultado

- **Cor de fundo de execução: 15 de 15 pares batem.** O achado 3 da primeira
  passada — 13 dos 18 formulários recebem `Color` em `FormCreate`/`FormShow` —
  está inteiramente portado, e agora medido com a janela na tela em vez de
  inferido do disassembly.
- **Ordem de tabulação: 18 de 18 iguais.**
- **Nenhum controle faltando, sobrando ou fora de posição** nos 15 pares. O que
  diverge é cor, não geometria.
- **Os blobs sobrepostos do `jugador` aparecem** — o retrato e as camadas de
  `Picture` desenham nos dois lados. Eles **não** desenham a mesma cara, e isso
  é a divergência 3 já registrada (cabelo, barba e `careto` não redesenham); a
  "contagem fina" que a primeira passada mandou para cá não se faz por
  screenshot e não precisa: o que interessa é que a região é desenhada, e é.
- **Os rótulos cortados continuam cortados nos dois lados**, pela mesma fonte
  substituta. Nada a fazer, como já estava escrito.

## O que sai daqui

| Achado | Para quem |
|---|---|
| 6 — 151 `TLabel` com `Color` não pintam (68 divergentes) | [WTE-TASK-10](../../docs/tasks/concluidos/10-conversor-dfm-para-lfm.md) — `Transparent = False` no gerador |
| 7 — combos de radar vazios; decisão **implementar** | corpo de `estrategia.ComboBoxDrawItem`, do disassembly |
| 8 — `ficha_warning` e `ficha_enlaza` sem chamador | [WTE-TASK-35](../../docs/tasks/concluidos/35-divergencias-deliberadas.md) |
| 9 — nomes vazios no modelo de ML | [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md) e [WTE-TASK-19](../../docs/tasks/concluidos/19-os-50-offsets-restantes.md) |
| 10 — prefixo de número nas listas de jogador | [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md) |
| 11 — `TStaticText` desabilitado (1 de 37) | [WTE-TASK-35](../../docs/tasks/concluidos/35-divergencias-deliberadas.md) |
| 12 e 13 | nada — são resultado |
