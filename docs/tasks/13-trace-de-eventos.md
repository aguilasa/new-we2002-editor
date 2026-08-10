---
id: WTE-TASK-13
title: "Trace de eventos — a ordem de disparo dos dois lados"
type: verificação
category: comportamento
phase: 2
depends_on: ["WTE-TASK-11"]
status: concluído
---

# WTE-TASK-13: Trace de eventos

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.3 item 3 e Fase 2 item 4.
- **Isto é RE dinâmica barata, e alimenta a Fase 4 inteira.** A ordem em que os
  eventos disparam não sai de análise estática, e ela decide o resultado: se o
  original recalcula o preço no `OnChange` antes do `OnKillFocus` gravar, a
  ordem invertida grava valor velho.

O `newWe2002` já pagou por diferença de sinal entre frameworks — `setText` não
dispara `editingFinished`, mas `EN_CHANGE` **dispara** em `SetWindowText`, e é o
que move os marcadores do campinho. Descobrir o equivalente aqui, antes de
implementar handler, é o ponto desta task.

---

## Objetivo

Comparar a sequência de eventos entre o original e a casca, para um conjunto
fixo de interações.

### 1. Instrumentar o lado do original

O `wte.exe` não loga nada. Duas opções, escolher e escrever a razão:

- **Ghidra + breakpoint** nos 96 endereços, com o Wine sob depurador. Preciso,
  caro de montar.
- **Inferência por efeito** — clicar e observar o que muda na tela, cruzando com
  os DFM. Barato, e suficiente para ordem relativa na maioria dos casos.

### 2. O roteiro de interações

Fixo, versionado, reproduzível por `xdotool` — **não** driver que reage à tela.
Roteiro que reage muda o estímulo quando um lado diverge, e aí os dois param de
receber a mesma entrada.

Candidatos de partida, cobrindo os pontos onde a ordem importa:

| Interação | Por que interessa |
|---|---|
| trocar de time no combo | `lista_equiposChange` — carga em cascata |
| clicar num jogador | `mostrar_jugadorClick` |
| editar nome e sair do campo | `OnKeyPress` × `OnExit` |
| mexer num `TScrollBar` de atributo | `OnChange` contínuo × final |
| abrir e fechar `ficha_color` | ordem de `FormShow`/`FormCreate` |

### 3. O que registrar

Diferenças de ordem entre LCL e VCL, com a consequência. Cada uma vira nota na
spec do handler afetado, na Fase 4.

**`setCurrentIndex`/`ItemIndex` dispara `OnChange` na LCL.** Se o original
dependia de não disparar, a carga de time precisa de bloqueio de sinal — o
`newWe2002` resolveu com `QSignalBlocker`; o equivalente aqui é um contador de
"estou carregando" ou desligar o handler temporariamente.

> **Medido, e é o contrário: `ItemIndex :=` NÃO dispara `OnChange` na
> LCL/GTK2.** O widgetset tranca o sinal em volta do `gtk_combo_box_set_active`
> com o comentário *"to be delphi compatible OnChange only fires in response to
> user actions not program actions"*. O precedente do Qt não transfere, e a
> carga de time **não** precisa de bloqueio. A tabela completa das seis ações
> programáticas, com o arquivo e a rotina de cada linha, está em
> [`../../wte/re/eventos.md`](../../wte/re/eventos.md), achado 2. O parágrafo
> acima fica como estava: é a premissa que a task carregava, e vê-la derrubada
> é metade do valor dela.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/roteiros/*.txt` | criar (5) |
| `wte/tests/roteiros/README.md` | criar — o formato das diretivas |
| `wte/re/eventos.md` | criar — diferenças de ordem e consequência |

---

## Critério de conclusão

- [x] Método de instrumentação do original escolhido, com razão
- [x] Roteiro fixo versionado, não driver reativo
- [x] As cinco interações da tabela cobertas — 2 exercitadas, 1 respondida por
      outro caminho (não existe `OnExit`), 2 bloqueadas com a razão escrita e o
      roteiro versionado à espera. A tabela do enunciado são "candidatos de
      partida", e cada um saiu daqui com estado medido
- [x] Cada diferença de ordem com a consequência escrita
- [x] Decidido se a carga de time precisa de bloqueio de sinal — **não precisa**
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  Cinco roteiros fixos versionados e o
  [`../../wte/re/eventos.md`](../../wte/re/eventos.md) com quatro achados. O
  método escolhido foi **inferência por efeito**, e não o Ghidra com
  breakpoint: caro de montar, e a WTE-TASK-12 mostrou que o gargalo do lado
  original não é instrumentação, é navegação — um breakpoint nos 96 endereços
  mediria o mesmo punhado de handlers que o clique já alcança. Duas fontes que
  o enunciado não previa acabaram sendo as decisivas: o **fonte da LCL
  instalada** e os **próprios DFM**.

  1. **A premissa da task estava invertida, e derrubá-la é metade do valor.**
     `ComboBox.ItemIndex := k` **não** dispara `OnChange` na LCL/GTK2: o
     widgetset tranca com `ChangeLock` e o autor escreveu por quê — *"to be
     delphi compatible OnChange only fires in response to user actions not
     program actions"*. Vale igual para `ListBox.ItemIndex`, `TrackBar.Position`
     e, por outro caminho, `TScrollBar.Position` (a LCL só conecta
     `change-value`, que o GTK emite apenas em interação do usuário).
     **A carga de time não precisa de bloqueio de sinal.** O precedente do
     `newWe2002`, onde o Qt dispara em `setCurrentIndex` e exigiu
     `QSignalBlocker`, **não transfere** — copiá-lo teria produzido a trava
     certa pelo motivo errado.

     Sobra uma divergência, **com um lado medido e o outro não**: `ComboBox.Text
     := s` não dispara na LCL — isto é medido, `TGtk2WSCustomComboBox.SetText`
     tranca. Que dispare na VCL vem da semântica documentada do Win32, não de
     leitura do `vcl60.bpl`, que nada no repositório abre. Atinge 9 dos 11
     combos, vira pergunta na spec dos 12 handlers de `OnChange`, e fecha por
     disassembly do handler ou por observação do `wte.exe` (ver "A divergência
     que sobra" no `eventos.md`).

  2. **Não existe `OnExit` nem `OnKillFocus` em nenhum dos 96.** A interação 3
     do enunciado ("`OnKeyPress` × `OnExit`") não tem os dois lados: o editor
     do Obocaman confirma texto **por tecla**, nos seis `OnKeyPress`. É o
     oposto do `ed.exe`, que gravava em `EN_KILLFOCUS`, e do `newWe2002`, que
     herdou isso em `editingFinished`. Para o harness da WTE-TASK-22: **sair do
     campo não grava**.

  3. **A ordem de arranque bate exatamente.** Os 16 `FormCreate` do trace saem
     na ordem dos 18 sítios de `CreateForm` que a WTE-TASK-11 mediu, com
     `ficha_error` e `ficha_error2` ausentes por não terem `OnCreate` — o que
     casa com a contagem estática de 16 da WTE-TASK-04. Primeira confirmação
     dinâmica, e nada a corrigir na casca.

  4. **O original carrega tudo em `MainForm.FormCreate`.** Diálogo de arquivo,
     aviso de tamanho e splash aparecem **antes** de o `MainForm` ser mapeado.
     Mesmo desenho do `ed.exe`, que abre o `CFileDialog` no `OnInitDialog`.
     Primeira pergunta da spec de `MainForm.FormCreate` (`0x004107c8`).

- **Problemas encontrados:**

  1. **Teclado não chega ao app LCL no `:99`, e essa é a pendência mais dura
     que a task deixa.** Sem window manager o GTK2 nunca considera a janela
     ativa: falharam `windowfocus` + `xdotool key`/`type` e também
     `xdotool key --window` (`XSendEvent`, que o GTK2 descarta). Medido em zero
     linha de trace e zero pixel de diferença no campo, com o clique no campo
     confirmado por captura; o mouse funciona (o roteiro 02 registra os dois
     `OnClick`). O `wte.exe` **não** sofre disso — o Wine implementa o próprio
     foco. Nenhum WM está instalado nesta máquina (14 candidatos procurados),
     e instalar pacote é decisão do usuário. Combinado com o achado 2, a
     operação "editar nome" fica sem comparação byte a byte até isso se
     resolver — **item para a WTE-TASK-22**.
  2. Três das cinco interações do enunciado dependem da fase 3 (dado na tela)
     ou da fase 4 (o gatilho de cada janela). Ficaram com roteiro versionado e
     estado escrito, prontas para replay.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/re/eventos.md` | criar |
  | `wte/tests/roteiros/README.md` | criar |
  | `wte/tests/roteiros/01-arranque.txt` … `05-abrir-fechar-cor.txt` | criar (5) |
  | `docs/tasks/13-trace-de-eventos.md` | modificar — premissa corrigida e Log |
