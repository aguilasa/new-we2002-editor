---
id: WTE-TASK-12
title: "Comparação visual dos 18 formulários contra o original"
type: verificação
category: ui
phase: 2
depends_on: ["WTE-TASK-11"]
status: pendente
---

# WTE-TASK-12: Comparação visual

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §6 e Fase 2 item 3.
- **Não automatizar com tolerância de pixel.** `MS Sans Serif` não está
  instalada no host, o Qt e o GTK2 substituem por fontes diferentes, e o próprio
  `wte.exe` sob Wine já renderiza com fonte substituta. Diferença de pixel é
  garantida e não informa nada. É inspeção humana, uma vez por formulário.

O `newWe2002` já passou por isto: rótulo apertado corta ("Position" vira
"Positior") tanto no port quanto no `ed.exe` sob Wine, pelo mesmo motivo.

---

## Objetivo

Capturar os 18 formulários dos dois lados e conferir, um a um, que a diferença é
só de fonte — não de posição, tamanho, cor, ordem ou controle faltando.

### Método

1. `make wte` no `:99`, navegar até cada formulário, `import -window <id>`.
2. O app Lazarus no `:99`. **Ele não navega** — na fase 2 os handlers são stub
   ([WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md), problema 3). O
   andaime é `--show`: `./wte/build/wte --show all` abre os 18 de uma vez,
   `--show <nome>` abre um só, `--list` dá os nomes. Mesma captura.
3. Lado a lado em `wte/re/visual/<formulario>/`.

**`import -window` falha com janela obscurecida por modal** — o aviso de
tamanho aparece na carga dos dois lados. Dispensar o modal antes, ou capturar
`-window root`.

### O que procurar, em ordem de gravidade

| Achado | Gravidade |
|---|---|
| controle faltando ou sobrando | bug do gerador — volta para a WTE-TASK-10 |
| posição ou tamanho errado | bug do gerador |
| cor de fundo diferente | provável `TStaticText` (§8.9) — 37 candidatos |
| bitmap não aparece | **não é perda na conversão** — a preservação dos 118 blobs está medida (WTE-TASK-10). É defeito de exibição: LCL/GTK2 ou pai do componente |
| rótulo cortado | **esperado**, registrar e seguir |

### As 37 instâncias de `TStaticText`

A §8.9 manda conferir agora, não na Fase 6. Corrigir 37 controles no fim é
retrabalho.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual/lazarus/*.png` | criar (18 capturas) |
| `wte/re/visual/original/*.png` | criar (3 capturas — ver a ressalva abaixo) |
| `wte/re/visual.md` | criar — um veredito por formulário |
| `wte/tools/capture_forms.sh` | criar — reproduz o lado port |

O `capture_forms.sh` não estava previsto e entrou porque a captura tem duas
armadilhas que ninguém acerta de memória (janela preta por obscurecimento,
janela do Wine que não pinta quando mapeada por fora). Ele **não** é gerador e
fica fora de `tools/*.py` de propósito: PNG não é byte-estável entre versões de
GTK e de ImageMagick, e um `--check` ali quebraria por atualização de
biblioteca. Mesmo raciocínio que deixou o `make_icon.py` do `newWe2002` fora da
bateria.

---

## Ressalva medida: o original só alcança 3 dos 18 na fase 2

Quem abre formulário são os handlers. No port eles são stub, e o `--show` da
WTE-TASK-11 contorna isso; **no original não há contorno** — descobrir o que
dispara cada janela é a WTE-TASK-25 em diante. Com a ROM carregada e um time
selecionado, nenhum clique nos candidatos óbvios abre janela, e tecla de
função não chega (o `xdotool key` depende de foco, e o `:99` não tem window
manager). Tentado duas vezes, a segunda com sessão limpa do Wine.

Os 3 alcançáveis são os do caminho de arranque: `ficha_warning`,
`ficha_about`, `MainForm`. As 15 capturas restantes do original passam para a
[WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md), que é a task com a lógica
ligada dos dois lados. Geometria, presença e ordem de controle não ficam sem
resposta: são conferidas contra o DFM, com o `dfm2lfm.py --check` provando que
nenhum `.lfm` foi tocado à mão.

---

## Critério de conclusão

- [ ] Os 18 capturados dos dois lados — **18 do port, 3 do original**; ver a
      ressalva acima
- [x] Um veredito escrito por formulário
- [x] Os 118 blobs aparecem na janela — critério herdado da
      [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md), que provou a
      preservação byte a byte e não podia provar a exibição. Os 100 desenháveis
      (`Glyph` + `Picture`) aparecem; os 18 `Icon.Data` não são julgáveis sem
      window manager, nos dois lados
- [x] O sufixo ` [Lazarus]` no `Caption` **não** foi contado como achado — é
      divergência deliberada da WTE-TASK-11, registrada na
      [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md). No `:99` não há
      window manager e a captura nem chega a mostrá-lo
- [x] Nenhum controle faltando ou fora de lugar
- [x] Comportamento das 37 `TStaticText` decidido
- [x] Rótulos cortados listados, com a nota de que é esperado
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  Os 18 formulários do port capturados e inspecionados um a um; o veredito de
  cada um, os três achados e as duas armadilhas de captura estão em
  [`../../wte/re/visual.md`](../../wte/re/visual.md). **A task ficou parcial**:
  o lado original entregou 3 capturas de 18, pelo motivo medido na ressalva
  acima.

  O que se aprendeu, em ordem de valor:

  1. **Cinco formulários recebem a cor de fundo em tempo de execução.** O
     original pinta o `MainForm` de azul e o `ficha_warning` de vermelho; os
     dois DFM dizem `Color = clBtnFace`, e o `clBtnFace` do Wine é o cinza do
     diálogo *Abre* do próprio app. Some com o rótulo branco sobre cinza que a
     casca mostra em `estrategia`, `ficha_color`, `ficha_warning`,
     `ficha_warning_2` e `MainForm`. Não é defeito do gerador, e a aparência
     desses cinco **não é julgável na fase 2**. Os cinco endereços de
     `FormCreate` estão no `visual.md`, para a WTE-TASK-25.

  2. **A §8.9 fecha sem custo: nenhum dos 37 `TStaticText` usa
     `Transparent`.** O risco que ela descreve é sobre transparência no GTK2, e
     não tem instância aqui — 27 declaram cor própria com
     `ParentColor = False` (a LCL aplica; dá para ver nas faixas opacas do
     `MainForm`) e 10 herdam a do pai. Decisão: nenhuma ação, e nenhum item
     para a fase 6. De quebra, 25 dos 37 têm `OnClick`: no original o
     `TStaticText` é widget clicável, não rótulo.

  3. **Os 100 blobs desenháveis aparecem** — o desenho do Obocaman, o retrato
     do `jugador`, o campo tático, o logo e os 24 glifos do `MainForm`. Os 18
     `Icon.Data` não são julgáveis sem window manager, dos dois lados.

  4. `jugador` é o formulário sem ressalva nenhuma: `clNavy` vem do DFM, a LCL
     aplica, e os 59 rótulos brancos ficam legíveis. É a contraprova de que o
     caminho de cor funciona e de que o problema do achado 1 é de execução.

- **Problemas encontrados:**

  1. **`import -window <id>` devolve PNG preto sem erro nenhum.** Sem window
     manager no `:99` não há empilhamento garantido, e quase todo formulário
     nasce dentro da área do `MainForm`; o X entrega o conteúdo indefinido da
     região obscurecida. As 18 primeiras capturas saíram pretas e pareciam bug
     de renderização da LCL. A saída é `windowraise` + recorte de
     `-window root`, e está no `capture_forms.sh`.
  2. **Mapear as janelas do original por fora não funciona.** As 18 janelas X
     existem desde o arranque (a VCL cria o handle em `CreateForm`), todas
     `IsUnMapped`. `xdotool windowmap` deixa a janela `IsViewable` e a captura
     passa — e sai preta, porque a VCL não considera o formulário exibido e
     nunca pinta. Não é atalho.
  3. **O `:99` desta máquina subiu sem `-auth`.** O `CLAUDE.md` descreve o
     Xvfb de `xvfb-run`, com cookie próprio; o processo atual é
     `Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp`, sem cookie. O
     `make -C wte run-99` erra falso nesse estado ("nao ha Xvfb :99 rodando"),
     porque conclui pela ausência do `-auth`. O `capture_forms.sh` trata os
     dois casos: só exporta `XAUTHORITY` quando o `-auth` existe.
  4. A navegação do original não cedeu (ver a ressalva). Descartada corrupção
     de estado: repetido com `wineserver -k` e sessão nova, mesmo resultado.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/capture_forms.sh` | criar |
  | `wte/re/visual.md` | criar |
  | `wte/re/visual/lazarus/*.png` | criar (18) |
  | `wte/re/visual/original/*.png` | criar (3) |
  | `docs/tasks/12-comparacao-visual.md` | modificar — ressalva e Log |
