# Ordem de disparo de evento: LCL × VCL — WTE-TASK-13

Insumo da fase 4. A ordem em que os eventos disparam **não sai de análise
estática**, e ela decide o resultado: se o original recalcula o preço no
`OnChange` antes de o `OnKillFocus` gravar, a ordem invertida grava valor
velho.

Roteiros em [`../tests/roteiros/`](../tests/roteiros). O trace do port sai em
`wte/re/trace.log` (não versionado — é saída de execução) ou onde
`$WTE_TRACE_FILE` apontar.

---

## Método escolhido: inferência por efeito, e por que não o depurador

O `wte.exe` não loga nada. As duas rotas da task eram *Ghidra + breakpoint nos
96 endereços, com o Wine sob depurador* e *inferência por efeito*.

**Escolhida: inferência por efeito**, com duas fontes que a task não previa e
que se revelaram mais decisivas que a observação de tela:

1. **O fonte da LCL instalada**, lido no disco (`/usr/lib/lazarus/3.0/lcl`).
   Para a pergunta que mais importa — *atribuir valor por código dispara o
   evento?* — a resposta está escrita no widgetset, com comentário do autor, e
   é mais forte que qualquer observação.
2. **Os próprios DFM**, para saber que eventos existem. Metade das perguntas
   de ordem some quando se descobre que um dos dois eventos **não existe** no
   binário.

O depurador foi descartado por custo, e a WTE-TASK-12 deu a razão de fundo: o
gargalo do lado original **não é instrumentação, é navegação** — não se sabe o
que abre cada janela, então um breakpoint nos 96 endereços mediria o mesmo
punhado de handlers que o clique já alcança.

---

## Achado 1 — não existe `OnExit` neste binário

Censo dos 96 handlers por evento, do
[`published_methods.tsv`](published_methods.tsv):

| Evento | Handlers |
|---|---|
| `OnClick` | 45 |
| `OnCreate` | 16 |
| `OnChange` | 12 |
| `OnMouseDown` | 5 |
| `OnKeyPress` | 6 |
| `OnScroll` | 2 |
| `OnShow` | 2 |
| `OnMouseMove` | 2 |
| `OnDrawItem`, `OnDragOver`, `OnDragDrop`, `OnEndDrag`, `OnTimer` | 1 cada |
| **`OnExit` / `OnKillFocus`** | **0** |

*(as contagens somam handlers, não controles: um handler serve vários controles
— `ficha_color.barraChange` atende três barras, e há famílias de `OnClick` com
23 membros. Somam 95; o 96º é `MainForm.Button2Click`, publicado e **não
ligado a evento nenhum** em DFM algum. Órfão do original, e uma pergunta a
menos para a fase 4 responder por engano.)*

**Consequência direta.** A interação nº 3 do enunciado da task — *"editar nome
e sair do campo: `OnKeyPress` × `OnExit`"* — não tem os dois lados. Só há
`OnKeyPress`, nos seis campos:

```
jugador.casilla_nombreKeyPress    jugador.casilla_dorsalKeyPress
jugador.casilla_precioKeyPress    MainForm.edit_nombre1KeyPress
MainForm.edit_nombre2KeyPress     MainForm.edit_nombre3KeyPress
```

**O editor do Obocaman confirma texto numa tecla, não ao sair do campo.** É o
oposto do `ed.exe`, que gravava em `EN_KILLFOCUS` — e o `newWe2002` herdou
isso, ligando os commits em `editingFinished`. Aqui não há o que ligar: o
handler é por tecla, e qual tecla ele aceita (`#13`, provavelmente) é pergunta
para a spec do handler na fase 4.

Para o harness da WTE-TASK-22 isso vale ouro: **sair do campo não grava**.
Um roteiro que digita e clica fora, como o do `newWe2002`, mede nada aqui.

---

## Achado 2 — atribuir por código **não** dispara `OnChange` na LCL/GTK2

Esta é a pergunta que a task manda decidir ("se a carga de time precisa de
bloqueio de sinal"), e o enunciado dela partia da premissa oposta.

Medido no fonte da LCL 3.0 instalada:

| Ação por código | VCL/Win32 (2002) | LCL/GTK2 3.0 | Diverge? |
|---|---|---|---|
| `ComboBox.ItemIndex := k` | não dispara | **não dispara** | não |
| `ListBox.ItemIndex := k` | não dispara | **não dispara** | não |
| `TrackBar.Position := v` | não dispara | **não dispara** | não |
| `ScrollBar.Position := v` | não dispara | **não dispara** | não |
| `Edit.Text := s` | **dispara** | **dispara** | não |
| `ComboBox.Text := s` (`csDropDown`) | **dispara** | **não dispara** | **sim** |

Onde cada linha foi lida:

- `interfaces/gtk2/gtk2wsstdctrls.pp`, `TGtk2WSCustomComboBox.SetItemIndex`:
  incrementa `WidgetInfo^.ChangeLock` em volta do
  `gtk_combo_box_set_active`, com o comentário do autor —
  *"to be delphi compatible OnChange only fires in response to user actions not
  program actions"*. O callback `GtkChangedCB` sai cedo com
  `if WidgetInfo^.ChangeLock > 0 then Exit`.
- `TGtk2WSCustomListBox.SetItemIndex` e `TGtk2WSTrackBar.SetPosition`
  (`gtk2wscomctrls.pp`): mesmo `ChangeLock`, o segundo com o comentário
  *"lock Range, so that no OnChange event is not fired"*.
- `TScrollBar` não precisa de trava: `TGtk2WSScrollBar.SetCallbacks` conecta
  **`change-value`**, que o GTK só emite em interação do usuário — o caminho
  programático (`gtk_adjustment_configure`) emite `value-changed`, e ninguém o
  escuta.
- `include/customedit.inc`, `TCustomEdit.TextChanged`: chama `Change`
  incondicionalmente; o `FTextChangedByRealSetText` só governa `Modified`.
  O Win32 faz o mesmo por `WM_SETTEXT` → `EN_CHANGE`, que é a armadilha que o
  `newWe2002` já documentou.
- `TGtk2WSCustomComboBox.SetText`: **tranca** — *"we use user ChangeLock to not
  signal onchange"*. É a única divergência da tabela.

### Decisão: a carga de time **não** precisa de bloqueio de sinal

`lista_equipos.ItemIndex := k` não dispara `lista_equiposChange`, exatamente
como no original. Não introduzir contador de "estou carregando" nem desligar
handler: seria código sem causa, e código sem causa esconde o dia em que a
causa aparecer.

**O precedente do `newWe2002` não transfere, e é o ponto a guardar.** Lá o Qt
*dispara* em `setCurrentIndex`, e a carga de time precisou de `QSignalBlocker`.
Copiar aquela conclusão para cá teria produzido a trava errada pelo motivo
errado. Framework diferente, resposta diferente — medir, não lembrar.

### A divergência que sobra, e onde ela morde

`ComboBox.Text := s` dispara `OnChange` na VCL e não dispara na LCL. Atinge
**9 dos 11** combos (os `csDropDown`; os outros dois são `csOwnerDrawFixed`),
entre eles o `lista_equipos`.

Ela só morde se algum handler do original escrever `Text` num combo **contando
com** o reentrar do `OnChange`. Não há como saber antes de ler os handlers:
fica registrado aqui e volta como pergunta na spec de cada um dos 12 handlers
de `OnChange` (WTE-TASK-25 em diante).

---

## Achado 3 — ordem de arranque: bate exatamente

Roteiro [`01-arranque.txt`](../tests/roteiros/01-arranque.txt). Trace do port,
sem interação nenhuma:

```
  0.000  MainForm.FormCreate          0.030  ficha_about.FormCreate
  0.018  estrategia.FormCreate        0.031  ficha_salida.FormCreate
  0.022  jugador.FormCreate           0.031  ficha_info4.FormCreate
  0.023  ficha_dorsal.FormCreate      0.031  ficha_info3.FormCreate
  0.023  ficha_enlaza.FormCreate      0.032  ficha_movertodos.FormCreate
  0.025  ficha_color.FormCreate       0.032  ficha_creditos_equipo.FormCreate
  0.026  ficha_info.FormCreate        0.032  ficha_warning_2.FormCreate
  0.026  ficha_warning.FormCreate     0.046  MainForm.FormShow
  0.027  ficha_info2.FormCreate
```

**16, na ordem exata dos 18 sítios de `Application->CreateForm` que a
WTE-TASK-11 mediu** em `0x401a22..0x401bc6`, com `ficha_error` e `ficha_error2`
ausentes por não terem `OnCreate` — o que casa com a contagem estática de 16
`FormCreate` da WTE-TASK-04. Primeira confirmação dinâmica da ordem, e ela
fecha: **nada a corrigir na casca**.

### O que o original faz a mais, e é comportamento, não framework

Observado na sessão da WTE-TASK-12, com o Wine no `:99`:

```
(nenhuma janela)  ->  "Abre" (diálogo de arquivo)
                  ->  ficha_warning  ("O tamanho do .bin nao corresponde...")
                  ->  ficha_about    (o splash)
                  ->  MainForm visível
```

As três aparecem **antes** de o `MainForm` ser mapeado. Logo o caminho de carga
inteiro pendura em `MainForm.FormCreate` (`0x004107c8`) — não em ação do
usuário, não no `FormShow`. É o mesmo desenho do `ed.exe`, que abre um
`CFileDialog` já no `OnInitDialog`.

Isso não é divergência de LCL: é o corpo de um handler, e vira a primeira
pergunta da spec de `MainForm.FormCreate` na
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md).

---

## Achado 4 — abrir formulário é invisível para o trace em 16 dos 18

Só `ficha_enlaza` e `MainForm` têm `OnShow`. Os 18 são criados no arranque, de
uma vez; abrir qualquer um dos outros 16 depois **não gera linha nenhuma**.

Quem marca a fronteira de um trecho de sessão é o `REMark` (`== ` no log),
escrito por quem dirige. Não tentar deduzir "abriu o formulário X" da ausência
de linhas.

---

## Limite medido: teclado não chega no app LCL no `:99`

Nenhuma tecla é entregue ao app Lazarus no `:99`: sem window manager o GTK2
nunca considera a janela ativa. Falharam as duas rotas —
`xdotool windowfocus` seguido de `xdotool key`/`type`, e `xdotool key --window`
(que usa `XSendEvent`, descartado pelo GTK2). Medida: **zero** linha de trace e
**zero** pixel de diferença no campo, com o clique no campo confirmado por
captura. Mouse funciona: o roteiro 02 registra os dois `OnClick`.

O `wte.exe` **não** sofre disso — o Wine implementa o próprio foco, e o
`golden_run.sh` do `newWe2002` já digita caminho de arquivo no `:99` há tempos.
A assimetria é entre GTK2 e Wine, não entre os dois apps.

**Consequência para a [WTE-TASK-22](/docs/tasks/22-harness-golden.md):** ou o
harness dirige o port **só por mouse**, ou o `:99` ganha um window manager.
Nenhum WM está instalado nesta máquina — `twm`, `openbox`, `metacity`,
`mutter`, `xfwm4`, `i3`, `fluxbox`, `icewm`, `jwm`, `matchbox`, `marco`,
`herbstluftwm`, `dwm` e `awesome`, todos ausentes. Instalar pacote é decisão do
usuário.

E com o achado 1 a conta piora: o original grava nome **por tecla**. Sem
teclado do lado port, a operação "editar nome" não tem como ser comparada byte
a byte. **É a pendência mais dura que esta task deixa.**

---

## As cinco interações do enunciado: estado de cada uma

| Interação | Estado |
|---|---|
| trocar de time no combo | **parcial.** O original faz a cascata (barras, camisa, contador de ML). O port não: a casca não lê imagem, o combo está vazio. Volta na WTE-TASK-18 |
| clicar num jogador | **bloqueada.** Não se sabe o que abre o `jugador` (WTE-TASK-12 tentou os candidatos óbvios). WTE-TASK-25 |
| editar nome e sair do campo | **respondida por outro caminho, e a pergunta muda:** não há `OnExit`; o commit é por tecla. Exercitar, do lado port, depende do teclado |
| mexer num `TScrollBar` de atributo | **respondida na semântica:** `Position :=` não dispara `OnChange` dos dois lados; o disparo contínuo × final por arraste do usuário fica para quando houver dado na tela |
| abrir e fechar `ficha_color` | **bloqueada** no gatilho, e invisível no trace (achado 4) |

Três das cinco esperam a fase 3 ou a 4. **Não é falha do método:** o que elas
pedem é o corpo dos handlers, que é o que a fase 4 escreve — e o que esta task
entrega é justamente o que precisava estar decidido *antes* dela.

---

## O que a fase 4 leva daqui

1. Nada de bloqueio de sinal na carga — a LCL/GTK2 já se comporta como a VCL
   (achado 2).
2. Ao escrever `Text` num combo, lembrar que o `OnChange` **não** reentra na
   LCL e reentrava na VCL. Perguntar isso na spec dos 12 handlers de `OnChange`.
3. Campo de texto confirma **por tecla**; não existe caminho de "saiu do
   campo". Seis handlers.
4. `MainForm.FormCreate` carrega o mundo inteiro: diálogo de arquivo, validação
   de tamanho e splash, tudo antes de a janela aparecer.
5. Abrir formulário não deixa rastro em 16 dos 18 — instrumentar com `REMark`.
