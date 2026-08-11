# `re/arranque.md` — o que os 18 `FormCreate`/`FormShow` fazem

Produto da [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md), grupo de
carga. Gerado por [`../tools/dump_arranque.py`](../tools/dump_arranque.py),
a partir de `we-team-editor/we-team-editor.exe`, de [`published_methods.tsv`](published_methods.tsv)
e de [`campos.tsv`](campos.tsv). **Não editar à mão:**

```sh
python3 wte/tools/dump_arranque.py
python3 wte/tools/dump_arranque.py --check   # o que `make -C wte check` roda
```

A tabela está em [`arranque.tsv`](arranque.tsv); este arquivo é a leitura
dela. **Todo número daqui saiu do script.**

## Eles não são todos triviais, e é isso que a medição diz

A leitura barata seria "inicialização de formulário, deve ser trivial".
Medido, os 18 se separam em quatro formas:

| Forma | Quantos | O que o corpo é |
|---|---:|---|
| `vazio` | 1 | um `ret`. O handler está ligado no DFM e não faz nada |
| `cor` | 11 | uma chamada a `TControl::SetColor` sobre a própria instância |
| `campo` | 1 | uma chamada virtual sobre um campo publicado |
| `composto` | 5 | qualquer outra coisa — inventariada abaixo |

A forma sai de casar o corpo contra o padrão de bytes de cada uma. Quando
nenhum casa, o script chama de `composto` e inventaria — padrão que deixe
de valer vira `composto` sozinho, nunca classificação errada em silêncio.

## Os 18

| Endereço | Formulário | Handler | Forma | Bytes | Resumo |
|---|---|---|---|---:|---|
| `0x00402bc0` | `ficha_dorsal` | `FormCreate` | cor | 15 | Color := $00E68F41 |
| `0x00402c44` | `ficha_enlaza` | `FormShow` | campo | 15 | BitBtn2.SetFocus |
| `0x00402c54` | `ficha_enlaza` | `FormCreate` | cor | 15 | Color := $003CDCDC |
| `0x00402cdc` | `ficha_warning` | `FormCreate` | cor | 15 | Color := $003C3CDC |
| `0x00402d60` | `ficha_info3` | `FormCreate` | cor | 15 | Color := $00DCDC3C |
| `0x00402de4` | `ficha_about` | `FormCreate` | vazio | 1 | — |
| `0x00402e84` | `ficha_movertodos` | `FormCreate` | cor | 15 | Color := $003CDCDC |
| `0x00402f08` | `ficha_salida` | `FormCreate` | cor | 15 | Color := $003CDCDC |
| `0x00402f8c` | `ficha_info` | `FormCreate` | cor | 15 | Color := $00DCDC3C |
| `0x0040422c` | `ficha_info4` | `FormCreate` | cor | 15 | Color := $00DCDC3C |
| `0x00405dcc` | `ficha_color` | `FormCreate` | composto | 116 | 4 campo(s), 0 cor(es) |
| `0x00407ce0` | `jugador` | `FormCreate` | composto | 936 | 3 campo(s), 2 cor(es) |
| `0x00408d88` | `ficha_warning_2` | `FormCreate` | cor | 15 | Color := $003C3CDC |
| `0x004090fc` | `estrategia` | `FormCreate` | composto | 1351 | 3 campo(s), 2 cor(es) |
| `0x0040b034` | `ficha_creditos_equipo` | `FormCreate` | cor | 15 | Color := $003CDCDC |
| `0x004107c8` | `MainForm` | `FormCreate` | composto | 683 | 3 campo(s), 0 cor(es) |
| `0x004111d8` | `MainForm` | `FormShow` | composto | 1605 | 7 campo(s), 0 cor(es) |
| `0x00420e84` | `ficha_info2` | `FormCreate` | cor | 15 | Color := $00DCDC3C |

## As cores

`TColor` da VCL é `$00BBGGRR`, **não** `#RRGGBB`: trocar a ordem daria um
formulário laranja onde o original é azul. A coluna RGB abaixo já vem
invertida, e é ela que o Pascal do port usa.

São 4 valores distintos nos 11 handlers
de forma `cor`:

| `TColor` | R | G | B | Formulários |
|---|---:|---:|---:|---|
| `$003C3CDC` | 220 | 60 | 60 | `ficha_warning`, `ficha_warning_2` |
| `$003CDCDC` | 220 | 220 | 60 | `ficha_enlaza`, `ficha_movertodos`, `ficha_salida`, `ficha_creditos_equipo` |
| `$00DCDC3C` | 60 | 220 | 220 | `ficha_info3`, `ficha_info`, `ficha_info4`, `ficha_info2` |
| `$00E68F41` | 65 | 143 | 230 | `ficha_dorsal` |

Nos 18 DFM a propriedade `Color` do formulário é `clBtnFace`, `clSilver` ou
`clNavy` — nenhuma delas é isto. A cor de projeto **nunca aparece na tela**:
o `OnCreate` a substitui antes de o formulário ser exibido. Um port que
respeitasse só o DFM ficaria cinza onde o original é colorido, e a
[WTE-TASK-12](../../docs/tasks/12-comparacao-visual.md) comparou justamente
as janelas nesse estado.

## Os `composto`, um a um

O inventário não é a spec — é o que a spec tem de explicar, e é um piso,
não um teto: campos são os de [`campos.tsv`](campos.tsv) alcançados por
`mov <reg>,[<reg>+disp32]`, e literais são as cadeias ASCII apontadas por
operando imediato ou por `lea <reg>,[edi+disp32]` sobre a base que o
C++Builder carrega em `EDI`.

### `ficha_color.FormCreate` — `0x00405dcc`, 116 bytes

- **Campos tocados:** `color1`, `lista_col1`, `lista_col2`, `recuadro2`
- **Cores:** nenhuma
- **Literais:** nenhum
- **Importados chamados:** `@Controls@TControl@SetColor$qqr15Graphics@TColor`, `@Controls@TControl@BringToFront$qqrv`

### `jugador.FormCreate` — `0x00407ce0`, 936 bytes

- **Campos tocados:** `etiqdorsal`, `etiqnombre`, `etiqprecio`
- **Cores:** `$00E68F41`, `$00D78228`
- **Literais:** `valorhab`, `etiqhab`, `etiqapa`, `valorapa`
- **Importados chamados:** `@Controls@TControl@SetColor$qqr15Graphics@TColor`, `@Classes@TComponent@FindComponent$qqrx17System@AnsiString`

### `estrategia.FormCreate` — `0x004090fc`, 1351 bytes

- **Campos tocados:** `bola0`, `etiqjug0`, `lista_formaciones`
- **Cores:** `$00D78228`, `$00E68F41`
- **Literais:** `etiqestr`, `jugador`, `etiqpos`
- **Importados chamados:** `@Controls@TControl@SetColor$qqr15Graphics@TColor`, `@Classes@TComponent@FindComponent$qqrx17System@AnsiString`

### `MainForm.FormCreate` — `0x004107c8`, 683 bytes

- **Campos tocados:** `bandera`, `home1`, `home2`
- **Cores:** nenhuma
- **Literais:** `\image`, `\barba`, `\pelo`, `\banderas`, `\uniformes2d`, `\data`
- **Importados chamados:** `@Sysutils@GetCurrentDir$qqrv`

### `MainForm.FormShow` — `0x004111d8`, 1605 bytes

- **Campos tocados:** `casilla_xmlibres`, `cuadro_dialogo_we`, `dialogo_we`, `grupo_barras`, `lista_equipos`, `lista_equipos_2`, `texto_dialogo_we`
- **Cores:** nenhuma
- **Literais:** `OBOCARULEZ`, `\dat.bin`, `The file "dat.bin" must be in the "data" directory`, `$00ffb676`
- **Importados chamados:** `@Dialogs@TOpenDialog@GetFileName$qqrv`, `@Controls@TControl@SetText$qqrx17System@AnsiString`, `@Graphics@StringToColor$qqrx17System@AnsiString`, `@Controls@TControl@SetColor$qqr15Graphics@TColor`, `@Controls@TControl@BringToFront$qqrv`
