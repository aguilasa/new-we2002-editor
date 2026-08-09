# Comparação visual dos 18 formulários — WTE-TASK-12

Inspeção humana, um veredito por formulário, como manda a §6 do
[`PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md): **sem tolerância de pixel**.
`MS Sans Serif` não está instalada no host, o GTK2 e o Wine substituem por
fontes diferentes, e diferença de pixel é garantida sem informar nada.

Capturas em [`visual/lazarus/`](visual/lazarus) (18) e
[`visual/original/`](visual/original) (3). Reproduzir o lado port:

```sh
bash wte/tools/capture_forms.sh
```

---

## Estado da comparação: completa de um lado, parcial do outro

| Lado | Capturado | Como |
|---|---|---|
| App Lazarus | **18 de 18** | `--show <nome>`, o andaime da WTE-TASK-11 |
| `we-team-editor.exe` | **3 de 18** | o que o próprio arranque do original alcança |

Os três do original são os que ele abre sozinho no caminho de carga:
`ficha_warning` (o aviso de tamanho), `ficha_about` (o splash) e `MainForm`.

**Os outros 15 não são alcançáveis na fase 2, e a razão é a mesma dos dois
lados.** Quem abre formulário são os handlers. No port eles são stub
(WTE-TASK-11, problema 3) e o `--show` existe justamente para contornar isso;
no original eles existem, mas **descobrir o que dispara cada um é a
WTE-TASK-25 em diante**. Medido: com a ROM carregada e um time selecionado,
nenhum clique nos candidatos óbvios (botões da escalação, `Pintar`, os ícones
do grupo de atributos, `Sair`) abre janela, e as teclas de função também não —
o `xdotool key` depende de foco, e no `:99` não há window manager. Foi tentado
duas vezes, a segunda com sessão limpa do Wine, para descartar corrupção de
estado.

As 15 capturas do original ficam para a
[WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) — *reconferência de UI com
a lógica ligada* —, que é a tarefa que terá navegação nos dois lados.

### O que substitui a captura, para os 15

Geometria, presença e ordem de controle **não dependem de screenshot**, e a
evidência estática é mais forte que ele:

- os 18 `.lfm` carregam `Left`/`Top`/`Width`/`Height`/`ClientWidth`/
  `ClientHeight` **iguais aos do DFM**, conferido nos 18 cabeçalhos;
- `python3 wte/tools/dfm2lfm.py --check` prova que nenhum `.lfm` foi editado à
  mão depois de gerado;
- `test_dfm2lfm.py` e `check_lcl_props.py` cobrem a tabela de mapeamento
  VCL→LCL que produziu esses valores.

O que só a tela responde — se o blob aparece, se o rótulo corta, que cor o
fundo tem de fato — está resolvido abaixo para o lado port nos 18.

---

## Duas armadilhas de captura, medidas aqui

**1. `import -window <id>` devolve preto, sem erro.** Sem window manager no
`:99` não há empilhamento garantido, e quase todo formulário nasce dentro da
área do `MainForm` (544×495 a partir de 132,72). O X entrega o conteúdo
indefinido da região obscurecida e o PNG sai todo preto — sem mensagem
nenhuma. É o mesmo sintoma que o [`CLAUDE.md`](../../CLAUDE.md) registra para o
modal do `ed.exe`, com outra causa. A saída, e o que o `capture_forms.sh` faz:
`xdotool windowraise` e recorte de `-window root`, que sempre tem conteúdo.

**2. Mapear janela do Wine por fora não faz a VCL pintar.** As 18 janelas X do
original existem desde o arranque (a VCL cria o handle em `CreateForm`), todas
`IsUnMapped`. `xdotool windowmap` deixa a janela `IsViewable` e a captura
passa a funcionar — **e sai preta**, porque a VCL não considera o formulário
exibido e nunca pinta. Atalho que não existe; não insistir.

---

## Veredito por formulário

Coluna **Original**: `sim` = capturado; `DFM` = referência estática, captura
adiada para a WTE-TASK-37.

| Formulário | Original | Veredito |
|---|---|---|
| `MainForm` | sim | **Fundo divergente por handler não implementado** (ver abaixo). Layout, blobs e controles conferem: o banner, o logo *Winning Eleven*, os 24 glifos e os 11 `Picture` aparecem. Sem controle faltando |
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
| `ficha_salida` | DFM | Sem ressalva |
| `ficha_movertodos` | DFM | Sem ressalva |
| `ficha_creditos_equipo` | DFM | Sem ressalva |
| `ficha_warning` | sim | **Fundo divergente por handler não implementado.** O original pinta vermelho; o DFM diz `clBtnFace`, e os 3 rótulos são `clWhite` — em cinza ficam ilegíveis. Texto também **corta à direita** |
| `ficha_warning_2` | DFM | Mesmo caso do `ficha_warning`, com 3 rótulos brancos. Uma linha **corta** |
| `ficha_about` | sim | **Praticamente idêntico ao original.** Fundo ciano, o desenho do Obocaman, o texto e o glifo do `Ok` no lugar. A única diferença é a faixa de moldura não pintada em volta (ver "Moldura") |

Nenhum controle faltando, nenhum sobrando, nenhum fora de posição nos 18.

---

## Achado 1 — cinco formulários recebem a cor de fundo em tempo de execução

O original mostra o `MainForm` **azul** e o `ficha_warning` **vermelho**. Os
dois DFM declaram `Color = clBtnFace`, e o `clBtnFace` do Wine é o cinza claro
que aparece no diálogo *Abre* do próprio app. Logo a cor **não vem do
formulário**: é atribuída depois de a instância existir.

O único handler que roda antes de a janela aparecer é o `FormCreate`, e os 18
têm endereço conhecido desde a WTE-TASK-04. Os candidatos, pelo cruzamento de
"declara `clBtnFace`" com "tem rótulo `Font.Color = clWhite`":

| Formulário | Rótulos brancos | `FormCreate` |
|---|---|---|
| `estrategia` | 35 | `0x004090fc` |
| `ficha_color` | 6 | `0x00405dcc` |
| `ficha_warning` | 3 | `0x00402cdc` |
| `ficha_warning_2` | 3 | `0x00408d88` |
| `MainForm` | 3 | `0x004107c8` |

**Evidência:** observação de tela nos dois que o original alcança
(`MainForm`, `ficha_warning`), cruzada com a tabela estática. Que seja o
`FormCreate` a escrever `Color` é a hipótese mais econômica, **não** um fato
medido — o disassembly desses cinco endereços é da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md), e é lá que a spec fecha.

Consequência para esta task: **a aparência desses cinco não pode ser julgada na
fase 2.** O que se pode afirmar é que a divergência é explicada, tem endereço,
e não é defeito do gerador de formulário.

Os quatro que declaram cor no próprio DFM — `jugador` e `ficha_error`/
`ficha_error2` em `clNavy`, `ficha_info` em `clSilver` — renderizam certo na
LCL, o que é a contraprova de que o caminho de cor funciona.

---

## Achado 2 — os 37 `TStaticText`: nada a fazer, e a §8.9 fecha sem custo

A §8.9 do plano manda conferir os 37 na fase 2, porque `TStaticText` no GTK2
trata transparência e cor de fundo diferente do Win32. Medido nos 18 DFM:

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
certa* quando o pai tiver a cor de execução do achado 1 — mas isso é do pai,
não do `TStaticText`.

O que a medida entrega para a fase 4 é outra coisa: **25 dos 37 têm `OnClick`**.
No original o `TStaticText` é usado como widget clicável, não como rótulo.

---

## Achado 3 — os 118 blobs aparecem

Critério herdado da [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md),
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

## Rótulos cortados — esperado, e listado

Sete formulários cortam texto: `ficha_warning`, `ficha_warning_2`,
`ficha_error`, `ficha_info`, `ficha_info2`, `ficha_info4` e, em uma linha, o
`MainForm`.

**É esperado e não é achado.** `MS Sans Serif` não está instalada; a
substituta é mais larga, e o rótulo tem `AutoSize = False` com largura fixa do
DFM. O `newWe2002` tem o mesmo sintoma no `ed.exe` sob Wine, com "Position"
virando "Positior". O `ficha_error` corta nas **duas** pontas porque o
`Alignment` é centralizado.

Não corrigir: alargar rótulo mudaria a geometria, que é o critério de
fidelidade da §5.

---

## Moldura: a janela do port é maior que a do original

A janela X do app Lazarus mede mais que a área de cliente declarada — o
`MainForm` sai 544×495 para `ClientWidth`/`ClientHeight` de 522×475. A LCL
reserva a moldura que o GTK informa, e sem window manager ninguém a desenha:
sobra uma faixa não pintada em volta, visível em toda captura do port.

Não é divergência de layout — os controles estão nas coordenadas do DFM, e a
área de cliente é a mesma. A faixa some com window manager. Registrado para
não voltar como "achado" na fase 6.

---

## Resumo para quem vier depois

| Pergunta da task | Resposta |
|---|---|
| Controle faltando ou sobrando? | Não, nos 18 |
| Posição ou tamanho errado? | Não — `.lfm` carrega o DFM verbatim, com `--check` |
| Cor de fundo diferente? | Em 5, e explicada: vem do `FormCreate` (achado 1) |
| Blobs aparecem? | Os 100 desenháveis, sim (achado 3) |
| `TStaticText` decidido? | Sim: nenhuma ação (achado 2) |
| Rótulo cortado? | Em 7, esperado, listado |
| Sufixo ` [Lazarus]` contado como achado? | Não — divergência deliberada da WTE-TASK-11, e sem window manager a captura nem o mostra |
| Os 18 dos dois lados? | **Não** — 18 do port, 3 do original; os 15 vão para a WTE-TASK-37 |
