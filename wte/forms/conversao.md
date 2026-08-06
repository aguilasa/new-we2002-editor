# `forms/conversao.md` -- o que a conversao DFM -> LFM mexeu

Gerado por [`../tools/dfm2lfm.py`](../tools/dfm2lfm.py) a partir de
[`../re/dfm/`](../re/dfm/). **Nao editar a mao** -- correcao entra no
script e o arquivo e regerado:

```sh
python3 wte/tools/dfm2lfm.py
python3 wte/tools/dfm2lfm.py --check   # o que `make -C wte check` roda
```

Este arquivo e o insumo da **WTE-TASK-12**: tudo que a LCL nao reproduz
literalmente esta aqui, com o valor original, para a conferencia visual saber
onde olhar.

## Os 18 formularios

O `.lfm` e o `.pas` levam o nome da **unidade**, nao o do formulario. Os 13
nomes de unidade marcados com * saem dos exports de finalizacao do `.exe`
(secao 1.3 do plano); os outros 5 seguem a mesma regra, sem medida direta.

| DFM | Unidade | Classe | Componentes | Blobs | Descartes | `TStaticText` |
|---|---|---|---:|---:|---:|---:|
| `MainForm.dfm` | `ep2002_mainform` | `TMainForm` | 116 | 36 | 9 | 34 |
| `estrategia.dfm` | `ep2002_estrategia` | `Testrategia` | 89 | 8 | 4 | 0 |
| `ficha_about.dfm` | `ep2002_about`* | `Tficha_about` | 6 | 5 | 5 | 0 |
| `ficha_color.dfm` | `ep2002_color` | `Tficha_color` | 65 | 12 | 2 | 3 |
| `ficha_creditos_equipo.dfm` | `ep2002_creditos_equipo`* | `Tficha_creditos_equipo` | 3 | 3 | 2 | 0 |
| `ficha_dorsal.dfm` | `ep2002_dorsal`* | `Tficha_dorsal` | 4 | 2 | 2 | 0 |
| `ficha_enlaza.dfm` | `ep2002_enlaza`* | `Tficha_enlaza` | 6 | 3 | 2 | 0 |
| `ficha_error.dfm` | `ep2002_error` | `Tficha_error` | 3 | 3 | 2 | 0 |
| `ficha_error2.dfm` | `ep2002_error2`* | `Tficha_error2` | 2 | 2 | 2 | 0 |
| `ficha_info.dfm` | `ep2002_info`* | `Tficha_info` | 6 | 2 | 2 | 0 |
| `ficha_info2.dfm` | `ep2002_info2`* | `Tficha_info2` | 6 | 2 | 2 | 0 |
| `ficha_info3.dfm` | `ep2002_info3`* | `Tficha_info3` | 2 | 2 | 2 | 0 |
| `ficha_info4.dfm` | `ep2002_info4`* | `Tficha_info4` | 4 | 2 | 2 | 0 |
| `ficha_movertodos.dfm` | `ep2002_movertodos`* | `Tficha_movertodos` | 3 | 3 | 2 | 0 |
| `ficha_salida.dfm` | `ep2002_salida`* | `Tficha_salida` | 3 | 3 | 2 | 0 |
| `ficha_warning.dfm` | `ep2002_warning`* | `Tficha_warning` | 5 | 3 | 2 | 0 |
| `ficha_warning_2.dfm` | `ep2002_warning_2`* | `Tficha_warning_2` | 5 | 3 | 2 | 0 |
| `jugador.dfm` | `ep2002_jugador` | `Tjugador` | 113 | 24 | 34 | 0 |
| **total** | | | **441** | **118** | **80** | **37** |

## Substituicao de classe: `TBrowseURL` -> `TLabel`

Duas instancias, as duas chamadas `lanza_url`, as duas dentro de um
`TActionList`. A WTE-TASK-07 mediu que **nao e componente de terceiro**: e a
acao padrao da VCL (unidade `Extactns`). A LCL nao tem par, entao vira
`TLabel` -- e um `TLabel` dentro de um `TActionList` fica sem pai
(`TControl.SetParentComponent` so aceita `TWinControl`) e nao aparece na
tela, que e exatamente o que a acao fazia: nao aparecia.

O comportamento -- abrir a URL no navegador -- e da **WTE-TASK-11**, com
`OpenURL()` de `LCLIntf` no handler que dispara. O `TODO` esta na unidade, ao
lado do campo, e a URL virou constante para nao se perder.

| Formulario | Objeto | Unidade | Constante | URL |
|---|---|---|---|---|
| `MainForm` | `lanza_url` | `ep2002_mainform` | `LANZA_URL_URL` | `'http://www.w11.com.br         '` |
| `ficha_about` | `lanza_url` | `ep2002_about` | `LANZA_URL_URL` | `'http://www.w11.com.br         '` |

## Propriedades descartadas

A tarefa pedia comentario dentro do `.lfm`. **Nao da**: o `TParser` da FCL --
que e quem le LFM, tanto no `LFMtoLRSstream` quanto em tempo de execucao -- so
pula espaco, tabulacao, CR e LF; nao ha sintaxe de comentario em LFM, e `{`
abre bloco binario. Um comentario compilaria (o `{$R}` so embute bytes) e
explodiria ao abrir a janela.

O valor original fica aqui e num comentario **na unidade Pascal**, ao lado do
campo do componente.

Sao 80 descartes.

| Formulario | Componente | Classe | Propriedade | Valor |
|---|---|---|---|---|
| `MainForm` | `MainForm` | `TMainForm` | `OldCreateOrder` | `True` |
| `MainForm` | `MainForm` | `TMainForm` | `TextHeight` | `13` |
| `MainForm` | `SpeedButton3` | `TSpeedButton` | `Action` | `lanza_url` |
| `MainForm` | `sel_barra0` | `TRadioButton` | `Ctl3D` | `True` |
| `MainForm` | `sel_barra0` | `TRadioButton` | `ParentCtl3D` | `False` |
| `MainForm` | `lista_descarte` | `TListBox` | `Ctl3D` | `True` |
| `MainForm` | `lista_descarte` | `TListBox` | `ParentCtl3D` | `False` |
| `MainForm` | `lanza_url` | `TLabel` | `Category` | `'Internet'` |
| `MainForm` | `lanza_url` | `TLabel` | `URL` | `'http://www.w11.com.br         '` |
| `estrategia` | `estrategia` | `Testrategia` | `OldCreateOrder` | `True` |
| `estrategia` | `estrategia` | `Testrategia` | `TextHeight` | `13` |
| `estrategia` | `ComboBox1` | `TComboBox` | `Ctl3D` | `True` |
| `estrategia` | `ComboBox1` | `TComboBox` | `ParentCtl3D` | `False` |
| `ficha_about` | `ficha_about` | `Tficha_about` | `OldCreateOrder` | `False` |
| `ficha_about` | `ficha_about` | `Tficha_about` | `TextHeight` | `13` |
| `ficha_about` | `SpeedButton1` | `TSpeedButton` | `Action` | `lanza_url` |
| `ficha_about` | `lanza_url` | `TLabel` | `Category` | `'Internet'` |
| `ficha_about` | `lanza_url` | `TLabel` | `URL` | `'http://www.w11.com.br         '` |
| `ficha_color` | `ficha_color` | `Tficha_color` | `OldCreateOrder` | `False` |
| `ficha_color` | `ficha_color` | `Tficha_color` | `TextHeight` | `13` |
| `ficha_creditos_equipo` | `ficha_creditos_equipo` | `Tficha_creditos_equipo` | `OldCreateOrder` | `False` |
| `ficha_creditos_equipo` | `ficha_creditos_equipo` | `Tficha_creditos_equipo` | `TextHeight` | `13` |
| `ficha_dorsal` | `ficha_dorsal` | `Tficha_dorsal` | `OldCreateOrder` | `False` |
| `ficha_dorsal` | `ficha_dorsal` | `Tficha_dorsal` | `TextHeight` | `13` |
| `ficha_enlaza` | `ficha_enlaza` | `Tficha_enlaza` | `OldCreateOrder` | `False` |
| `ficha_enlaza` | `ficha_enlaza` | `Tficha_enlaza` | `TextHeight` | `13` |
| `ficha_error` | `ficha_error` | `Tficha_error` | `OldCreateOrder` | `False` |
| `ficha_error` | `ficha_error` | `Tficha_error` | `TextHeight` | `13` |
| `ficha_error2` | `ficha_error2` | `Tficha_error2` | `OldCreateOrder` | `False` |
| `ficha_error2` | `ficha_error2` | `Tficha_error2` | `TextHeight` | `13` |
| `ficha_info` | `ficha_info` | `Tficha_info` | `OldCreateOrder` | `False` |
| `ficha_info` | `ficha_info` | `Tficha_info` | `TextHeight` | `13` |
| `ficha_info2` | `ficha_info2` | `Tficha_info2` | `OldCreateOrder` | `False` |
| `ficha_info2` | `ficha_info2` | `Tficha_info2` | `TextHeight` | `13` |
| `ficha_info3` | `ficha_info3` | `Tficha_info3` | `OldCreateOrder` | `False` |
| `ficha_info3` | `ficha_info3` | `Tficha_info3` | `TextHeight` | `13` |
| `ficha_info4` | `ficha_info4` | `Tficha_info4` | `OldCreateOrder` | `False` |
| `ficha_info4` | `ficha_info4` | `Tficha_info4` | `TextHeight` | `13` |
| `ficha_movertodos` | `ficha_movertodos` | `Tficha_movertodos` | `OldCreateOrder` | `False` |
| `ficha_movertodos` | `ficha_movertodos` | `Tficha_movertodos` | `TextHeight` | `13` |
| `ficha_salida` | `ficha_salida` | `Tficha_salida` | `OldCreateOrder` | `False` |
| `ficha_salida` | `ficha_salida` | `Tficha_salida` | `TextHeight` | `13` |
| `ficha_warning` | `ficha_warning` | `Tficha_warning` | `OldCreateOrder` | `False` |
| `ficha_warning` | `ficha_warning` | `Tficha_warning` | `TextHeight` | `13` |
| `ficha_warning_2` | `ficha_warning_2` | `Tficha_warning_2` | `OldCreateOrder` | `False` |
| `ficha_warning_2` | `ficha_warning_2` | `Tficha_warning_2` | `TextHeight` | `13` |
| `jugador` | `jugador` | `Tjugador` | `OldCreateOrder` | `True` |
| `jugador` | `jugador` | `Tjugador` | `TextHeight` | `13` |
| `jugador` | `barrhab1` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab1` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab2` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab2` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab3` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab3` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab4` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab4` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab5` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab5` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab6` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab6` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab7` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab7` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab8` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab8` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab9` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab9` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab10` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab10` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab11` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab11` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab12` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab12` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab13` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab13` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab14` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab14` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab15` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab15` | `TScrollBar` | `ParentCtl3D` | `False` |
| `jugador` | `barrhab16` | `TScrollBar` | `Ctl3D` | `False` |
| `jugador` | `barrhab16` | `TScrollBar` | `ParentCtl3D` | `False` |

### Por que cada uma cai

| Propriedade | Qtd | Motivo |
|---|---:|---|
| `Action` | 2 | a propriedade existe na LCL, mas o valor aponta para 'lanza_url', que era TBrowseURL e virou TLabel; TLabel nao e TBasicAction e o leitor de LFM recusaria a atribuicao |
| `Category` | 2 | categoria de TAction; some com a acao, porque TLabel nao e acao |
| `Ctl3D` | 19 | a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2 desenha a borda propria |
| `OldCreateOrder` | 18 | propriedade de compatibilidade do Delphi 4; a LCL nao a tem e sempre usa a ordem nova de criacao |
| `ParentCtl3D` | 19 | a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2 desenha a borda propria |
| `TextHeight` | 18 | medida de tempo de projeto do Delphi, gravada para reescalar o formulario; a LCL nao a tem |
| `URL` | 2 | propriedade do TBrowseURL; o valor fica na constante <NOME>_URL da unidade e o comportamento vira OpenURL() no handler |

## Os 118 blobs binarios

118 propriedades `vaBinary` (816880 bytes) saem do `.dfm` como
referencia `{blob <arquivo> <tamanho> sha256:<hash>}` e entram no `.lfm` como
hex inline, no formato canonico do `ObjectBinaryToText`: 32 bytes por linha,
em maiusculas.

Os bytes vivem em `wte/re/dfm/blobs/`, que e **gitignored** (secao 2 do plano):
sem eles o modo de escrita **aborta**. O `--check` nao precisa deles -- ele
confere o hex do `.lfm` versionado contra o SHA-256 que esta no `.dfm`.

| Formulario | Blobs | Bytes |
|---|---:|---:|
| `MainForm` | 36 | 124232 |
| `estrategia` | 8 | 425148 |
| `ficha_about` | 5 | 130782 |
| `ficha_color` | 12 | 9692 |
| `ficha_creditos_equipo` | 3 | 1874 |
| `ficha_dorsal` | 2 | 1096 |
| `ficha_enlaza` | 3 | 1874 |
| `ficha_error` | 3 | 1754 |
| `ficha_error2` | 2 | 1096 |
| `ficha_info` | 2 | 1096 |
| `ficha_info2` | 2 | 1096 |
| `ficha_info3` | 2 | 1096 |
| `ficha_info4` | 2 | 1096 |
| `ficha_movertodos` | 3 | 1874 |
| `ficha_salida` | 3 | 1874 |
| `ficha_warning` | 3 | 1874 |
| `ficha_warning_2` | 3 | 1874 |
| `jugador` | 24 | 107452 |
| **total** | **118** | **816880** |

## As instancias de `TStaticText`

A secao 8.9 do plano manda conferir estas **na fase 2, nao na 6**: 
`TStaticText` existe na LCL, mas transparencia e cor de fundo se comportam
diferente no GTK2 do que no Win32. O gerador nao resolve isso -- so marca.

Sao 37 instancias. A coluna **Fundo** traz as propriedades que
decidem o desenho do fundo
(`Color`, `ParentColor`, `Transparent`, `BorderStyle`);
linha vazia ali e o caso que mais tende a divergir, porque tudo fica no
padrao de cada widgetset.

| Formulario | Componente | Fundo |
|---|---|---|
| `MainForm` | `etiqueta_mcr` | _(nada)_ |
| `MainForm` | `texto_mcr` | `BorderStyle = sbsSingle`, `Color = clCream`, `ParentColor = False` |
| `MainForm` | `etiqueta_camiseta` | _(nada)_ |
| `MainForm` | `texto_dialogo_tex` | `BorderStyle = sbsSingle`, `Color = clCream`, `ParentColor = False` |
| `MainForm` | `(sem nome, TStaticText)` | _(nada)_ |
| `MainForm` | `etiqueta_juego` | _(nada)_ |
| `MainForm` | `texto_dialogo_we` | `BorderStyle = sbsSingle`, `Color = clCream`, `ParentColor = False` |
| `MainForm` | `StaticText1` | _(nada)_ |
| `MainForm` | `help_team` | _(nada)_ |
| `MainForm` | `base_team` | _(nada)_ |
| `MainForm` | `dorsal1` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal2` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal3` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal4` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal5` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal6` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal7` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal8` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal9` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal10` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal11` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal12` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal13` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal14` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal15` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal16` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal17` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal18` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal19` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal20` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal21` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal22` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `dorsal23` | `BorderStyle = sbsSunken`, `Color = clGray`, `ParentColor = False` |
| `MainForm` | `casilla_xmlibres` | `BorderStyle = sbsSunken`, `Color = clCream`, `ParentColor = False` |
| `ficha_color` | `StaticText1` | _(nada)_ |
| `ficha_color` | `StaticText2` | _(nada)_ |
| `ficha_color` | `StaticText3` | _(nada)_ |
