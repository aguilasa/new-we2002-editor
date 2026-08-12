# `re/spec/INDICE.md` — os 96 handlers e o veredito de cada um

**Gerado — não editar à mão.** Correção entra no gerador e o arquivo
é regerado:

```sh
python3 wte/tools/spec_index.py
python3 wte/tools/spec_index.py --check   # o que `make -C wte check` roda
```

Fonte: [`../published_methods.tsv`](../published_methods.tsv)
(WTE-TASK-04) mais os `<formulario>.<handler>.md` desta pasta. O
gabarito e o vocabulário de veredito estão em
[`GABARITO.md`](GABARITO.md); é a
[WTE-TASK-29](../../../docs/tasks/29-fechamento-fase-4.md) que exige nenhum
`aberto`.

## Contagem

| Veredito | Handlers |
|---|---|
| `implementado` | 6 |
| `trivial` | 14 |
| `divergencia deliberada` | 0 |
| `nao portado` | 0 |
| `aberto` | 76 |
| **total** | **96** |

35 de 96 têm arquivo de spec.

## Os 96

Na ordem de endereço, como o `dump_published.py` os emite.

| Endereço | Formulário | Handler | Evento | Grupo | Veredito |
|---|---|---|---|---|---|
| `0x00402b40` | `ficha_dorsal` | BitBtn1Click | OnClick | auxiliar | aberto |
| `0x00402b58` | `ficha_dorsal` | [scroll_dorsalChange](ficha_dorsal.scroll_dorsalChange.md) | OnChange | edicao | implementado |
| `0x00402bc0` | `ficha_dorsal` | [FormCreate](ficha_dorsal.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402c44` | `ficha_enlaza` | [FormShow](ficha_enlaza.FormShow.md) | OnShow | carga | trivial |
| `0x00402c54` | `ficha_enlaza` | [FormCreate](ficha_enlaza.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402cdc` | `ficha_warning` | [FormCreate](ficha_warning.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402d60` | `ficha_info3` | [FormCreate](ficha_info3.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402de4` | `ficha_about` | [FormCreate](ficha_about.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402de8` | `ficha_about` | imagen_urlClick | OnClick | auxiliar | aberto |
| `0x00402e84` | `ficha_movertodos` | [FormCreate](ficha_movertodos.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402f08` | `ficha_salida` | [FormCreate](ficha_salida.FormCreate.md) | OnCreate | carga | trivial |
| `0x00402f8c` | `ficha_info` | [FormCreate](ficha_info.FormCreate.md) | OnCreate | carga | trivial |
| `0x0040422c` | `ficha_info4` | [FormCreate](ficha_info4.FormCreate.md) | OnCreate | carga | trivial |
| `0x00405dcc` | `ficha_color` | [FormCreate](ficha_color.FormCreate.md) | OnCreate | carga | aberto |
| `0x00405e40` | `ficha_color` | barraChange | OnChange x3 | edicao | aberto |
| `0x00406078` | `ficha_color` | botonClick | OnClick x4 | auxiliar | aberto |
| `0x00406358` | `ficha_color` | barra1Change | OnChange | edicao | aberto |
| `0x00406384` | `ficha_color` | barra2Change | OnChange | edicao | aberto |
| `0x004063b0` | `ficha_color` | gradienteClick | OnClick | edicao | aberto |
| `0x004065fc` | `ficha_color` | oscurecerClick | OnClick | edicao | aberto |
| `0x00406744` | `ficha_color` | aclararClick | OnClick | edicao | aberto |
| `0x0040688c` | `ficha_color` | lista_col0Change | OnChange | edicao | aberto |
| `0x004068b0` | `ficha_color` | lista_col1change | OnChange | edicao | aberto |
| `0x004068ec` | `ficha_color` | lista_col2Change | OnChange | edicao | aberto |
| `0x0040690c` | `ficha_color` | lista_col3Change | OnChange | edicao | aberto |
| `0x00406968` | `ficha_color` | BitBtn1Click | OnClick | auxiliar | aberto |
| `0x004069c8` | `ficha_color` | BitBtn2Click | OnClick | auxiliar | aberto |
| `0x004069e8` | `ficha_color` | BitBtn3Click | OnClick | auxiliar | aberto |
| `0x00406a0c` | `ficha_color` | colorMouseDown | OnMouseDown x16 | edicao | aberto |
| `0x00406f34` | `ficha_color` | SpeedButton1Click | OnClick | auxiliar | aberto |
| `0x00407a68` | `jugador` | BitBtn2Click | OnClick | auxiliar | aberto |
| `0x00407a80` | `jugador` | BitBtn1Click | OnClick | auxiliar | aberto |
| `0x00407a88` | `jugador` | barrhabScroll | OnScroll x9 | edicao | aberto |
| `0x00407bb4` | `jugador` | barrhab_bisScroll | OnScroll x7 | edicao | aberto |
| `0x00407ce0` | `jugador` | [FormCreate](jugador.FormCreate.md) | OnCreate | carga | trivial |
| `0x00408088` | `jugador` | flechasapaClick | OnClick x12 | edicao | aberto |
| `0x00408548` | `jugador` | BitBtn3Click | OnClick | auxiliar | aberto |
| `0x00408af8` | `jugador` | [casilla_nombreKeyPress](jugador.casilla_nombreKeyPress.md) | OnKeyPress | edicao | implementado |
| `0x00408b50` | `jugador` | [casilla_dorsalKeyPress](jugador.casilla_dorsalKeyPress.md) | OnKeyPress | edicao | aberto |
| `0x00408b9c` | `jugador` | casilla_precioKeyPress | OnKeyPress | edicao | aberto |
| `0x00408bb8` | `jugador` | etiqprecioClick | OnClick | edicao | aberto |
| `0x00408d88` | `ficha_warning_2` | [FormCreate](ficha_warning_2.FormCreate.md) | OnCreate | carga | trivial |
| `0x00408e0c` | `estrategia` | bolaMouseMove | OnMouseMove x10 | edicao | aberto |
| `0x00408f00` | `estrategia` | bolaMouseDown | OnMouseDown x10 | edicao | aberto |
| `0x004090c8` | `estrategia` | campoMouseMove | OnMouseMove | edicao | aberto |
| `0x004090fc` | `estrategia` | [FormCreate](estrategia.FormCreate.md) | OnCreate | carga | aberto |
| `0x00409644` | `estrategia` | rectanguloDragOver | OnDragOver | edicao | aberto |
| `0x00409780` | `estrategia` | rectanguloDragDrop | OnDragDrop | edicao | aberto |
| `0x004097a4` | `estrategia` | bolaEndDrag | OnEndDrag x10 | edicao | aberto |
| `0x00409aa0` | `estrategia` | [lista_formacionesClick](estrategia.lista_formacionesClick.md) | OnClick | carga | aberto |
| `0x00409ba4` | `estrategia` | relojTimer | OnTimer | edicao | aberto |
| `0x00409f4c` | `estrategia` | malla1MouseDown | OnMouseDown | edicao | aberto |
| `0x0040a000` | `estrategia` | malla2MouseDown | OnMouseDown | edicao | aberto |
| `0x0040a658` | `estrategia` | BitBtn1Click | OnClick | auxiliar | aberto |
| `0x0040a660` | `estrategia` | BitBtn3Click | OnClick | auxiliar | aberto |
| `0x0040adec` | `estrategia` | [ComboBoxDrawItem](estrategia.ComboBoxDrawItem.md) | OnDrawItem x2 | carga | aberto |
| `0x0040b034` | `ficha_creditos_equipo` | [FormCreate](ficha_creditos_equipo.FormCreate.md) | OnCreate | carga | trivial |
| `0x0040bd60` | `MainForm` | [boton_dialogo_weClick](MainForm.boton_dialogo_weClick.md) | OnClick | carga | aberto |
| `0x0040c2c8` | `MainForm` | [boton_mcrClick](MainForm.boton_mcrClick.md) | OnClick | carga | aberto |
| `0x0040c46c` | `MainForm` | boton_mcr2isoClick | OnClick | gravacao | aberto |
| `0x0040c9c4` | `MainForm` | Button2Click | — | auxiliar | aberto |
| `0x0040c9d0` | `MainForm` | [sel_barraClick](MainForm.sel_barraClick.md) | OnClick x5 | edicao | implementado |
| `0x0040ca10` | `MainForm` | [track_barraChange](MainForm.track_barraChange.md) | OnChange | edicao | implementado |
| `0x0040cab8` | `MainForm` | boton_barras2isoClick | OnClick | gravacao | aberto |
| `0x0040cd6c` | `MainForm` | [lista_equiposChange](MainForm.lista_equiposChange.md) | OnChange | carga | aberto |
| `0x0040d36c` | `MainForm` | edit_nombre1KeyPress | OnKeyPress | edicao | aberto |
| `0x0040d3c4` | `MainForm` | edit_nombre2KeyPress | OnKeyPress | edicao | aberto |
| `0x0040d41c` | `MainForm` | edit_nombre3KeyPress | OnKeyPress | edicao | aberto |
| `0x0040d43c` | `MainForm` | iguala_nombresClick | OnClick | edicao | aberto |
| `0x0040d534` | `MainForm` | boton_nombres2isoClick | OnClick | gravacao | aberto |
| `0x0040de18` | `MainForm` | boton_tex2isoClick | OnClick | gravacao | aberto |
| `0x0040dfe8` | `MainForm` | [boton_dialogo_texClick](MainForm.boton_dialogo_texClick.md) | OnClick | carga | aberto |
| `0x0040e1a8` | `MainForm` | [lista_equipos_2Change](MainForm.lista_equipos_2Change.md) | OnChange | carga | aberto |
| `0x0040e304` | `MainForm` | paderechaeizquierdaClick | OnClick | edicao | aberto |
| `0x0040e4b0` | `MainForm` | paizquierdaClick | OnClick | edicao | aberto |
| `0x0040e5e8` | `MainForm` | paderechaClick | OnClick | edicao | aberto |
| `0x0040e720` | `MainForm` | paderecha2Click | OnClick | edicao | aberto |
| `0x0040e85c` | `MainForm` | paizquierda2Click | OnClick | edicao | aberto |
| `0x0040e998` | `MainForm` | parribaClick | OnClick | edicao | aberto |
| `0x0040ecc0` | `MainForm` | pabajoClick | OnClick | edicao | aberto |
| `0x0040ee80` | `MainForm` | grabar_camisetaClick | OnClick | gravacao | aberto |
| `0x0040f69c` | `MainForm` | grabar_memoryClick | OnClick | gravacao | aberto |
| `0x0040f8b8` | `MainForm` | [lista_jugadores_1Change](MainForm.lista_jugadores_1Change.md) | OnChange | carga | aberto |
| `0x0040f8d4` | `MainForm` | [mostrar_jugadorClick](MainForm.mostrar_jugadorClick.md) | OnClick x2 | carga | aberto |
| `0x00410220` | `MainForm` | [mostrar_estrategiaClick](MainForm.mostrar_estrategiaClick.md) | OnClick x2 | carga | aberto |
| `0x004107c8` | `MainForm` | [FormCreate](MainForm.FormCreate.md) | OnCreate | carga | implementado |
| `0x00410a74` | `MainForm` | [dorsalClick](MainForm.dorsalClick.md) | OnClick x23 | edicao | aberto |
| `0x00410ddc` | `MainForm` | [dorsalMouseDown](MainForm.dorsalMouseDown.md) | OnMouseDown x23 | edicao | implementado |
| `0x00410ea8` | `MainForm` | colorearClick | OnClick | edicao | aberto |
| `0x00410fa4` | `MainForm` | SpeedButton2Click | OnClick | auxiliar | aberto |
| `0x00410fc0` | `MainForm` | SpeedButton1Click | OnClick | auxiliar | aberto |
| `0x00410fd0` | `MainForm` | Image3Click | OnClick | auxiliar | aberto |
| `0x00410ff4` | `MainForm` | base_teamClick | OnClick x2 | auxiliar | aberto |
| `0x004111d8` | `MainForm` | [FormShow](MainForm.FormShow.md) | OnShow | carga | aberto |
| `0x00420e84` | `ficha_info2` | [FormCreate](ficha_info2.FormCreate.md) | OnCreate | carga | trivial |
| `0x00420f08` | `ficha_error` | SpeedButton1Click | OnClick | auxiliar | aberto |
