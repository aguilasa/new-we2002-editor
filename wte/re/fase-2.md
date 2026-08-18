# `re/fase-2.md` — fechamento da fase 2

Produto da [WTE-TASK-14](../../docs/tasks/14-fechamento-fase-2.md). **Gerado** por
[`../tools/check_fase2.py`](../tools/check_fase2.py) — não editar à mão; correção
entra no script e o arquivo é regerado:

```sh
python3 wte/tools/check_fase2.py
python3 wte/tools/check_fase2.py --check   # o que `make -C wte check` roda
```

Ele não remede o binário: mede a **coerência entre os produtos** das WTE-TASK-10 a 13
e a fração de código gerado, que é o número com que a §4.4 do plano se compromete.

---

## Veredito da fase

| Conferência | Resultado |
|---|---|
| Formulários com `.lfm` e `.dfm` pareados | **18** |
| Handlers do `published_methods.tsv` com stub próprio | **96** |
| Stub na unidade que declara a classe | **todos** |
| Formulários com veredito visual escrito | **18** |
| …confrontados com captura do original / só com o DFM | **4** / **14** |
| Achados registrados em `eventos.md` | **4** |

Qualquer uma dessas falhando **aborta** este script — não há tabela de resíduo.
Resíduo é falha, como no `FORBIDDEN` do `port_database.py`.

A conferência que **não** está aqui é "nenhum arquivo gerado foi editado à mão":
quem prova isso é o `dfm2lfm.py --check`, na mesma bateria. Refazê-la aqui seria
uma segunda cópia da mesma medida.

---

## Fração de código gerado — a tese da §4.4

A §4.4 diz que só um bloco vem de teclado: os corpos dos 96 handlers. Medido
hoje, com a fase 2 fechada e as fases 3 e 4 ainda por vir:

| Origem | Arquivos | Linhas |
|---|---|---|
| Unidades Pascal geradas (`dfm2lfm.py`) | 21 | 2559 |
| Formulários `.lfm`, estrutura | 18 | 6768 |
| **Gerado, subtotal** | | **9327** |
| Escrito à mão | 57 | 3269 |
| **Total** | | **12596** |

**74.0% do Pascal da casca é saída de gerador.**

Fora desta conta, por não serem casca: `src/we2002_cdimage.pas`, `src/we2002_database.pas`, `src/we2002_estado.pas`, `src/we2002_offsets.pas`, `src/we2002_player.pas`, `src/we2002_tables.pas`, `src/we2002_team.pas`, `src/we2002_textcodec.pas`, `src/we2002_types.pas`.
São a camada de dados da fase 3, e cada uma tem gerador e `--check` próprios.
Contá-las aqui faria o número da §4.4 flutuar a cada unidade nova, e — pior —
as jogaria na coluna "escrito à mão", porque a marca no cabeçalho delas é a do
gerador **delas**, não a do `dfm2lfm.py`.

Escrito à mão, linha por linha:

| Arquivo | Linhas | O que é |
|---|---|---|
| `src/impl/ep2002_about.FormCreate.inc` | 13 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_creditos_equipo.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_dorsal.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_dorsal.scroll_dorsalChange.inc` | 22 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_enlaza.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_enlaza.FormShow.inc` | 14 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.aux.inc` | 317 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.bolaEndDrag.inc` | 13 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.bolaMouseDown.inc` | 47 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.bolaMouseMove.inc` | 33 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.campoMouseMove.inc` | 17 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.lista_formacionesClick.inc` | 50 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.rectanguloDragDrop.inc` | 16 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.rectanguloDragOver.inc` | 25 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_estrategia.relojTimer.inc` | 75 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_info.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_info2.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_info3.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_info4.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.FormCreate.inc` | 54 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.aux.inc` | 42 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.barrhabScroll.inc` | 15 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.barrhab_bisScroll.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.casilla_dorsalKeyPress.inc` | 30 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.casilla_nombreKeyPress.inc` | 22 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_jugador.flechasapaClick.inc` | 67 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.FormCreate.inc` | 20 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.FormShow.inc` | 85 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.aux.inc` | 967 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.boton_dialogo_weClick.inc` | 21 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.dorsalClick.inc` | 91 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.dorsalMouseDown.inc` | 40 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.edit_nombre1KeyPress.inc` | 19 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.edit_nombre2KeyPress.inc` | 19 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.edit_nombre3KeyPress.inc` | 20 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.iguala_nombresClick.inc` | 33 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.lista_equiposChange.inc` | 160 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.lista_equipos_2Change.inc` | 56 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.lista_jugadores_1Change.inc` | 22 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.mostrar_estrategiaClick.inc` | 17 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.mostrar_jugadorClick.inc` | 37 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.pabajoClick.inc` | 50 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.paderecha2Click.inc` | 20 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.paderechaClick.inc` | 16 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.paderechaeizquierdaClick.inc` | 72 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.paizquierda2Click.inc` | 11 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.paizquierdaClick.inc` | 15 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.parribaClick.inc` | 42 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.sel_barraClick.inc` | 28 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_mainform.track_barraChange.inc` | 29 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_movertodos.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_salida.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_warning.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/impl/ep2002_warning_2.FormCreate.inc` | 12 | corpo de handler, da spec (fase 4) |
| `src/retrace.pas` | 125 | o registrador de disparo (WTE-TASK-11) |
| `src/wtemain.pas` | 196 | auto-create, linha de comando e a marca de título (WTE-TASK-11) |
| `wte.lpr` | 42 | programa principal (WTE-TASK-02) |

### O hex dos blobs fica fora da conta, e por quê

Os 118 blobs viraram **25712 linhas** de hexadecimal inline nos 18 `.lfm`
(decisão de 2026-08-06, registrada no `re/dfm/README.md`). Contados junto, a
fração sobe para 91.5% — e passa a medir bitmap, não geração de código.
O número que responde à §4.4 é o de cima.

### O que este número **não** decide ainda

A §4.3 afirma que a camada de UI é **60% do volume** do projeto. Isso não é
verificável hoje: a UI é a única camada que existe. Só dá para fechar depois
da fase 3 (camada de dados, gerada) e da fase 4 (os 96 corpos, à mão) — e é
nessa hora que a fração cai, porque os corpos são o único bloco manual grande.

O que **está** verificado é o lado forte da tese: a casca inteira saiu de
gerador, e o que sobrou de teclado é andaime de projeto, não lógica do editor.

---

## Stubs por unidade

| Unidade | Stubs |
|---|---|
| `src/ep2002_color.pas` | 17 |
| `src/ep2002_mainform.pas` | 14 |
| `src/ep2002_estrategia.pas` | 6 |
| `src/ep2002_jugador.pas` | 5 |
| `src/ep2002_about.pas` | 1 |
| `src/ep2002_dorsal.pas` | 1 |
| `src/ep2002_error.pas` | 1 |
| _com corpo escrito_ | 51 |
| **total** | **96** |

Os que já têm corpo saíram do stub para `src/impl/` — é a fase 4 chegando.
A conta continua fechando por soma: cada handler aparece uma vez, de uma
das duas formas.

- `MainForm.FormCreate`
- `MainForm.FormShow`
- `MainForm.boton_dialogo_weClick`
- `MainForm.dorsalClick`
- `MainForm.dorsalMouseDown`
- `MainForm.edit_nombre1KeyPress`
- `MainForm.edit_nombre2KeyPress`
- `MainForm.edit_nombre3KeyPress`
- `MainForm.iguala_nombresClick`
- `MainForm.lista_equiposChange`
- `MainForm.lista_equipos_2Change`
- `MainForm.lista_jugadores_1Change`
- `MainForm.mostrar_estrategiaClick`
- `MainForm.mostrar_jugadorClick`
- `MainForm.pabajoClick`
- `MainForm.paderecha2Click`
- `MainForm.paderechaClick`
- `MainForm.paderechaeizquierdaClick`
- `MainForm.paizquierda2Click`
- `MainForm.paizquierdaClick`
- `MainForm.parribaClick`
- `MainForm.sel_barraClick`
- `MainForm.track_barraChange`
- `estrategia.bolaEndDrag`
- `estrategia.bolaMouseDown`
- `estrategia.bolaMouseMove`
- `estrategia.campoMouseMove`
- `estrategia.lista_formacionesClick`
- `estrategia.rectanguloDragDrop`
- `estrategia.rectanguloDragOver`
- `estrategia.relojTimer`
- `ficha_about.FormCreate`
- `ficha_creditos_equipo.FormCreate`
- `ficha_dorsal.FormCreate`
- `ficha_dorsal.scroll_dorsalChange`
- `ficha_enlaza.FormCreate`
- `ficha_enlaza.FormShow`
- `ficha_info.FormCreate`
- `ficha_info2.FormCreate`
- `ficha_info3.FormCreate`
- `ficha_info4.FormCreate`
- `ficha_movertodos.FormCreate`
- `ficha_salida.FormCreate`
- `ficha_warning.FormCreate`
- `ficha_warning_2.FormCreate`
- `jugador.FormCreate`
- `jugador.barrhabScroll`
- `jugador.barrhab_bisScroll`
- `jugador.casilla_dorsalKeyPress`
- `jugador.casilla_nombreKeyPress`
- `jugador.flechasapaClick`

---

## O que a fase 2 **não** prova

Escrito de propósito, para o vocabulário não inflar.

1. **A casca não toca a imagem de CD.** Nada aqui diz que o app *funciona* —
   só que ele *parece* e *reage*. Toda gravação é da fase 3 em diante.
2. **Os 18 formulários não eram navegáveis no fechamento da fase 2, e não
   podiam ser.** O critério de pronto da fase 2 no plano pede navegação; quem
   abre formulário são os handlers, e naquela fase eles eram stub. O que houve
   até a WTE-TASK-25 foi o `--show`, andaime explícito para a captura da
   WTE-TASK-12; ele **saiu** quando `mostrar_jugadorClick` e
   `mostrar_estrategiaClick` passaram a abrir `jugador` e `estrategia`.
3. **A comparação visual cobriu os 18 do port e 4 do original.** Os
   outros 14 não foram capturados porque o oráculo quebra ao selecionar um
   time — ver `re/visual.md`, achado 1. Geometria e presença de controle estão
   provadas contra o DFM, que é evidência mais forte que screenshot; **cor e
   render** dos 14 continuam sem confronto. *(Os dois números saem da coluna
   `Original` da tabela do `re/visual.md`, contada por este script — não de
   soma à mão.)*
4. **Nenhum evento foi comparado com o original em execução.** O que a
   WTE-TASK-13 mediu do lado da LCL saiu do fonte da LCL e do trace do port;
   do lado do original saiu do DFM e da observação do arranque.

---

## Pendências que a fase 2 entrega para as seguintes

| Pendência | Para quem |
|---|---|
| O oráculo quebra ao selecionar um time (310 `EXCEPTION_ACCESS_VIOLATION`) | [WTE-TASK-22](../../docs/tasks/22-harness-golden.md), **bloqueante** |
| Aceitar o aviso de tamanho grava 11.952 bytes na imagem | [WTE-TASK-22](../../docs/tasks/22-harness-golden.md) |
| Teclado não chega ao app LCL no `:99` | [WTE-TASK-22](../../docs/tasks/22-harness-golden.md) |
| Cor de fundo posta em tempo de execução | [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md) |
| As 14 capturas do original | [WTE-TASK-37](../../docs/tasks/37-reconferencia-de-ui.md) |

