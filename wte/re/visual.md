# Comparação visual dos 18 formulários — WTE-TASK-12

Inspeção humana, um veredito por formulário, como manda a §6 do
[`PLAN-WTE-LAZARUS.md`](../../docs/PLAN-WTE-LAZARUS.md): **sem tolerância de pixel**.
`MS Sans Serif` não está instalada no host, o GTK2 e o Wine substituem por
fontes diferentes, e diferença de pixel é garantida sem informar nada.

Capturas em [`visual/lazarus/`](visual/lazarus) (18) e
[`visual/original/`](visual/original) (4). Reproduzir o lado port:

```sh
bash wte/tools/capture_forms.sh
```

---

## Estado: 18 do port, 4 do original — e o que impede os outros 14

| Lado | Capturado |
|---|---|
| App Lazarus | **18 de 18**, por `--show`, o andaime da WTE-TASK-11 |
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

**Consequência, e é grave:** quase toda operação do editor começa por escolher
um time. Enquanto isto não se resolver, o oráculo A não executa nem os 14
formulários desta task nem a maior parte da bateria golden. Entregue à
[WTE-TASK-22](../../docs/tasks/22-harness-golden.md).

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

O aviso dispara **sempre** com as imagens deste repositório: elas têm
474.784.128 bytes e o editor espera 474.431.328. Ou seja, o caminho que grava é
o caminho normal.

**Isto muda o desenho do golden test**, e vai para a
[WTE-TASK-22](../../docs/tasks/22-harness-golden.md): *original contra original*
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
[WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md).

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

Critério herdado da [WTE-TASK-10](../../docs/tasks/10-conversor-dfm-para-lfm.md),
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
`ed.exe`, com outra causa. A saída, e o que o `capture_forms.sh` faz:
`xdotool windowraise` e recorte de `-window root`.

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
| 1 — o oráculo quebra ao selecionar time | [WTE-TASK-22](../../docs/tasks/22-harness-golden.md), **bloqueante** |
| 2 — aceitar o aviso grava 11.952 bytes | [WTE-TASK-22](../../docs/tasks/22-harness-golden.md) e [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md) |
| 3 — cor de fundo em runtime | [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md) |
| 4 — 25 dos 37 `TStaticText` são clicáveis | fase 4 |
| 5 — contagem fina de blob sobrepostos | [WTE-TASK-37](../../docs/tasks/37-reconferencia-de-ui.md) |
| as 14 capturas do original | [WTE-TASK-37](../../docs/tasks/37-reconferencia-de-ui.md), **se** o achado 1 se resolver |
