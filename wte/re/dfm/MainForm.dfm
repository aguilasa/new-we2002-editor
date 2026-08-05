object MainForm: TMainForm
  Left = 132
  Top = 72
  BorderIcons = [biSystemMenu, biMinimize]
  BorderStyle = bsSingle
  Caption = ' W11 Team Editor PT by chagas_michel!'
  ClientHeight = 475
  ClientWidth = 522
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob MainForm.Icon.Data.bin 318 sha256:3d608e33b23ff77f8bdf8560961d08233c6abdb774f114b2c61695ccc8cafae3}
  OldCreateOrder = True
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object Image1: TImage
    Left = 544
    Top = 136
    Width = 113
    Height = 65
    Center = True
    Picture.Data = {blob Image1.Picture.Data.bin 20086 sha256:497673690c85a83af43626b8d46c0c1d13170c3466de0035065c5d3b7c1ee3cf}
  end
  object SpeedButton1: TSpeedButton
    Left = 136
    Top = 14
    Width = 73
    Height = 25
    Caption = '  Sobre...'
    Flat = True
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clCream
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    Glyph.Data = {blob SpeedButton1.Glyph.Data.bin 658 sha256:e66257be72bdca81c670c6ddc318eea20f399f254d2231f62c27075464237c9b}
    ParentFont = False
    Spacing = 0
    OnClick = SpeedButton1Click
  end
  object SpeedButton2: TSpeedButton
    Left = 136
    Top = 40
    Width = 73
    Height = 24
    Caption = ' Sair    '
    Flat = True
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clCream
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    Glyph.Data = {blob SpeedButton2.Glyph.Data.bin 658 sha256:4f7377cf8e04cf79249d03cb42a57792f7bf24db4f73313084387caede8003af}
    ParentFont = False
    Spacing = 0
    OnClick = SpeedButton2Click
  end
  object Image4: TImage
    Left = 330
    Top = 8
    Width = 193
    Height = 41
    Center = True
    Picture.Data = {blob Image4.Picture.Data.bin 7670 sha256:81da0cea805d19db00e884f5b8667792806612162d0b2c0a024d66a2adbdb11e}
  end
  object GroupBox4: TGroupBox
    Left = 216
    Top = 8
    Width = 113
    Height = 209
    TabOrder = 10
    object colorear: TSpeedButton
      Left = 8
      Top = 176
      Width = 97
      Height = 25
      Hint = 'Colorir    '
      Caption = 'Pintar'
      Enabled = False
      Flat = True
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      Glyph.Data = {blob colorear.Glyph.Data.bin 734 sha256:442f16f9dddd52287b71a5b231e4d20e43964aca34141b09e69223201ef95f31}
      Layout = blGlyphRight
      ParentFont = False
      ParentShowHint = False
      ShowHint = True
      OnClick = colorearClick
    end
    object home1: TImage
      Left = 16
      Top = 96
      Width = 80
      Height = 42
      Center = True
      Picture.Data = {blob home1.Picture.Data.bin 2770 sha256:15d91c4864ed2347960685fbe7102ef1d8987605a326d05a7d3af42ed02ab06a}
      Stretch = True
      Visible = False
    end
    object home2: TImage
      Left = 16
      Top = 138
      Width = 80
      Height = 22
      Picture.Data = {blob home2.Picture.Data.bin 1970 sha256:b14d6913f07034d59aa46663e4606f1c36d2a5c07d97e67611274325c80fe299}
      Stretch = True
      Visible = False
    end
    object Shape8: TShape
      Left = 14
      Top = 26
      Width = 84
      Height = 52
      Brush.Color = clCream
      Pen.Width = 2
    end
    object bandera: TImage
      Left = 16
      Top = 28
      Width = 80
      Height = 48
      Stretch = True
      Visible = False
    end
    object punto: TShape
      Left = 96
      Top = 117
      Width = 2
      Height = 2
      Visible = False
    end
  end
  object grupo_memorycard: TGroupBox
    Left = 8
    Top = 224
    Width = 505
    Height = 89
    TabOrder = 1
    object Image2: TImage
      Left = 176
      Top = 7
      Width = 153
      Height = 58
      Center = True
      Picture.Data = {blob Image2.Picture.Data.bin 17286 sha256:6aba5d653c8c8c234d0c3f0a59faf5c1c1a30ac18304402be6ef80f6d98db71d}
    end
    object boton_mcr2iso: TSpeedButton
      Left = 8
      Top = 56
      Width = 73
      Height = 25
      Cursor = crHandPoint
      Hint = '      Inserir MCR no jogo     '
      Enabled = False
      Flat = True
      Glyph.Data = {blob boton_mcr2iso.Glyph.Data.bin 2878 sha256:a8b6802c4bb97db019d963e84970899ef02fc562552901f0532f00624df0c450}
      ParentShowHint = False
      ShowHint = True
      OnClick = boton_mcr2isoClick
    end
    object boton_tex2iso: TSpeedButton
      Left = 424
      Top = 56
      Width = 73
      Height = 25
      Cursor = crHandPoint
      Hint = '   Inserir UNI no jogo  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob boton_tex2iso.Glyph.Data.bin 2878 sha256:3151e825f79fbcbde9a856c7c05709da4e1e85fb51be3b941537aa393f2a44cd}
      ParentShowHint = False
      ShowHint = True
      OnClick = boton_tex2isoClick
    end
    object boton_mcr: TSpeedButton
      Left = 8
      Top = 24
      Width = 25
      Height = 25
      Hint = '  Carregar MCR  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob boton_mcr.Glyph.Data.bin 1258 sha256:21b6226c6b6e19cfaf3dbffe33d947b9ff97b11424e4884090fc7815e6b3e8e2}
      ParentShowHint = False
      ShowHint = True
      OnClick = boton_mcrClick
    end
    object boton_dialogo_tex: TSpeedButton
      Left = 472
      Top = 24
      Width = 25
      Height = 25
      Hint = ' Car. Uni '
      Enabled = False
      Flat = True
      Glyph.Data = {blob boton_dialogo_tex.Glyph.Data.bin 1258 sha256:21b6226c6b6e19cfaf3dbffe33d947b9ff97b11424e4884090fc7815e6b3e8e2}
      ParentShowHint = False
      ShowHint = True
      OnClick = boton_dialogo_texClick
    end
    object grabar_memory: TSpeedButton
      Left = 88
      Top = 56
      Width = 25
      Height = 25
      Hint = 'Salvar MCR      '
      Enabled = False
      Flat = True
      Glyph.Data = {blob grabar_memory.Glyph.Data.bin 942 sha256:9337cdcbbf67a7d50ab29f957676c37ea58415ff4a74551e49473596659d0dda}
      ParentShowHint = False
      ShowHint = True
      OnClick = grabar_memoryClick
    end
    object grabar_camiseta: TSpeedButton
      Left = 392
      Top = 56
      Width = 25
      Height = 25
      Hint = 'Salvar Uni'
      Enabled = False
      Flat = True
      Glyph.Data = {blob grabar_camiseta.Glyph.Data.bin 942 sha256:9337cdcbbf67a7d50ab29f957676c37ea58415ff4a74551e49473596659d0dda}
      ParentShowHint = False
      ShowHint = True
      OnClick = grabar_camisetaClick
    end
    object SpeedButton3: TSpeedButton
      Left = 352
      Top = 60
      Width = 25
      Height = 25
      Cursor = crHandPoint
      Hint = 'Take a look at my site...'
      Action = lanza_url
      Caption = ' '
      Flat = True
      ParentShowHint = False
      ShowHint = True
      Spacing = -3
      Visible = False
    end
    object Image3: TImage
      Left = 136
      Top = 60
      Width = 233
      Height = 25
      Cursor = crHandPoint
      Hint = 'Visite a W11 Online:-)'
      Center = True
      ParentShowHint = False
      Picture.Data = {blob Image3.Picture.Data.bin 13266 sha256:3d7cdce117e4fe49d660ab6d68f462694c2582c803f6034f98683f34584a6f86}
      ShowHint = True
      OnClick = Image3Click
    end
    object etiqueta_mcr: TStaticText
      Left = 40
      Top = 16
      Width = 66
      Height = 17
      Caption = 'Equipe(mcr)'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 1
    end
    object texto_mcr: TStaticText
      Left = 40
      Top = 32
      Width = 129
      Height = 17
      AutoSize = False
      BorderStyle = sbsSingle
      Color = clCream
      ParentColor = False
      TabOrder = 0
    end
    object etiqueta_camiseta: TStaticText
      Left = 440
      Top = 16
      Width = 25
      Height = 17
      Alignment = taRightJustify
      Caption = 'UNI  '
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 3
    end
    object texto_dialogo_tex: TStaticText
      Left = 336
      Top = 32
      Width = 129
      Height = 17
      AutoSize = False
      BorderStyle = sbsSingle
      Color = clCream
      ParentColor = False
      TabOrder = 2
    end
  end
  object cuadro_dialogo_we: TGroupBox
    Left = 536
    Top = 376
    Width = 153
    Height = 57
    TabOrder = 0
    object boton_dialogo_we: TSpeedButton
      Left = 8
      Top = 24
      Width = 25
      Height = 25
      Flat = True
      Glyph.Data = {blob boton_dialogo_we.Glyph.Data.bin 1258 sha256:21b6226c6b6e19cfaf3dbffe33d947b9ff97b11424e4884090fc7815e6b3e8e2}
      OnClick = boton_dialogo_weClick
    end
    object TStaticText
      Left = 16
      Top = 16
      Width = 4
      Height = 4
      TabOrder = 0
    end
    object etiqueta_juego: TStaticText
      Left = 40
      Top = 16
      Width = 32
      Height = 17
      Caption = 'Game'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 1
    end
    object texto_dialogo_we: TStaticText
      Left = 40
      Top = 32
      Width = 105
      Height = 17
      AutoSize = False
      BorderStyle = sbsSingle
      Color = clCream
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clBlack
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 2
    end
  end
  object grupo_barras: TGroupBox
    Left = 8
    Top = 72
    Width = 201
    Height = 145
    Color = clBtnFace
    ParentColor = False
    TabOrder = 3
    object Shape1: TShape
      Left = 83
      Top = 17
      Width = 110
      Height = 15
      Brush.Color = clNavy
    end
    object Shape2: TShape
      Left = 83
      Top = 33
      Width = 110
      Height = 15
      Brush.Color = clNavy
    end
    object Shape4: TShape
      Left = 83
      Top = 49
      Width = 110
      Height = 15
      Brush.Color = clNavy
    end
    object Shape5: TShape
      Left = 83
      Top = 65
      Width = 110
      Height = 15
      Brush.Color = clNavy
    end
    object Shape6: TShape
      Left = 83
      Top = 81
      Width = 110
      Height = 15
      Brush.Color = clNavy
    end
    object barra0: TImage
      Left = 84
      Top = 18
      Width = 9
      Height = 13
      Picture.Data = {blob barra0.Picture.Data.bin 6050 sha256:c51b6c2e60bd7033c8be7525678ded685e0530d4a853ed2ed245e0c99191ec98}
    end
    object barra1: TImage
      Left = 84
      Top = 34
      Width = 9
      Height = 13
      Picture.Data = {blob barra1.Picture.Data.bin 6050 sha256:c51b6c2e60bd7033c8be7525678ded685e0530d4a853ed2ed245e0c99191ec98}
    end
    object barra2: TImage
      Left = 84
      Top = 50
      Width = 9
      Height = 13
      Picture.Data = {blob barra2.Picture.Data.bin 6050 sha256:c51b6c2e60bd7033c8be7525678ded685e0530d4a853ed2ed245e0c99191ec98}
    end
    object barra3: TImage
      Left = 84
      Top = 66
      Width = 9
      Height = 13
      Picture.Data = {blob barra3.Picture.Data.bin 6050 sha256:c51b6c2e60bd7033c8be7525678ded685e0530d4a853ed2ed245e0c99191ec98}
    end
    object barra4: TImage
      Left = 84
      Top = 82
      Width = 9
      Height = 13
      Picture.Data = {blob barra4.Picture.Data.bin 6050 sha256:c51b6c2e60bd7033c8be7525678ded685e0530d4a853ed2ed245e0c99191ec98}
    end
    object boton_barras2iso: TSpeedButton
      Left = 8
      Top = 112
      Width = 73
      Height = 25
      Cursor = crHandPoint
      Hint = 'Inserir barras no jogo '
      Enabled = False
      Flat = True
      Glyph.Data = {blob boton_barras2iso.Glyph.Data.bin 2878 sha256:367c0ab1ef82e0f839b9906d8c76b2bcf0ee9ca87695c1acaa8ae8c0f332fce3}
      ParentShowHint = False
      ShowHint = True
      OnClick = boton_barras2isoClick
    end
    object sel_barra0: TRadioButton
      Left = 8
      Top = 16
      Width = 73
      Height = 16
      Caption = ' Ataque '
      Checked = True
      Ctl3D = True
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentCtl3D = False
      ParentFont = False
      TabOrder = 0
      TabStop = True
      OnClick = sel_barraClick
    end
    object sel_barra1: TRadioButton
      Left = 8
      Top = 32
      Width = 73
      Height = 16
      Caption = 'Defesa  '
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 1
      OnClick = sel_barraClick
    end
    object sel_barra2: TRadioButton
      Left = 8
      Top = 48
      Width = 73
      Height = 16
      Caption = 'Equipe  '
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 2
      OnClick = sel_barraClick
    end
    object sel_barra3: TRadioButton
      Left = 8
      Top = 64
      Width = 73
      Height = 16
      Caption = 'Velocidade'
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 3
      OnClick = sel_barraClick
    end
    object sel_barra4: TRadioButton
      Left = 8
      Top = 80
      Width = 73
      Height = 16
      Caption = 'Tecnica '
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 4
      OnClick = sel_barraClick
    end
    object track_barra: TTrackBar
      Left = 88
      Top = 112
      Width = 105
      Height = 25
      Enabled = False
      Max = 9
      Orientation = trHorizontal
      Frequency = 1
      Position = 0
      SelEnd = 0
      SelStart = 0
      TabOrder = 5
      TabStop = False
      TickMarks = tmBoth
      TickStyle = tsNone
      OnChange = track_barraChange
    end
  end
  object grupo_nombre: TGroupBox
    Left = 336
    Top = 48
    Width = 177
    Height = 169
    TabOrder = 4
    object etiq_nombre1: TLabel
      Left = 8
      Top = 16
      Width = 41
      Height = 17
      Alignment = taRightJustify
      AutoSize = False
      Caption = 'Nome1'
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      Layout = tlBottom
    end
    object etiq_nombre2: TLabel
      Left = 8
      Top = 56
      Width = 41
      Height = 17
      Alignment = taRightJustify
      AutoSize = False
      Caption = 'Nome2'
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      Layout = tlBottom
    end
    object etiq_nombre3: TLabel
      Left = 8
      Top = 96
      Width = 41
      Height = 17
      Alignment = taRightJustify
      AutoSize = False
      Caption = 'Nome3'
      Enabled = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      Layout = tlBottom
    end
    object boton_nombres2iso: TSpeedButton
      Left = 96
      Top = 136
      Width = 73
      Height = 25
      Cursor = crHandPoint
      Hint = 'Inserir nomes no jogo   '
      Enabled = False
      Flat = True
      Glyph.Data = {blob boton_nombres2iso.Glyph.Data.bin 2878 sha256:6678bfbcdd6169adbab295582bd9347d466f08317483f2f7d7435f6c85ed929c}
      ParentShowHint = False
      ShowHint = True
      OnClick = boton_nombres2isoClick
    end
    object iguala_nombres: TSpeedButton
      Left = 8
      Top = 136
      Width = 73
      Height = 25
      Hint = 'Usar Nome1 nos 3 tipos de nomes'
      Enabled = False
      Flat = True
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      Glyph.Data = {blob iguala_nombres.Glyph.Data.bin 2998 sha256:708455136c20717dbec0393fbaf4a319693d66cb14098935588d8bfc3e0fa48b}
      ParentFont = False
      ParentShowHint = False
      ShowHint = True
      OnClick = iguala_nombresClick
    end
    object edit_nombre1: TEdit
      Left = 56
      Top = 16
      Width = 113
      Height = 21
      Color = clCream
      Enabled = False
      TabOrder = 0
      OnKeyPress = edit_nombre1KeyPress
    end
    object edit_nombre2: TEdit
      Left = 56
      Top = 56
      Width = 113
      Height = 21
      CharCase = ecUpperCase
      Color = clCream
      Enabled = False
      TabOrder = 1
      OnKeyPress = edit_nombre2KeyPress
    end
    object edit_nombre3: TEdit
      Left = 56
      Top = 96
      Width = 33
      Height = 21
      CharCase = ecUpperCase
      Color = clCream
      Enabled = False
      MaxLength = 3
      TabOrder = 2
      OnKeyPress = edit_nombre3KeyPress
    end
  end
  object GroupBox3: TGroupBox
    Left = 8
    Top = 8
    Width = 121
    Height = 57
    TabOrder = 5
    object StaticText1: TStaticText
      Left = 8
      Top = 12
      Width = 31
      Height = 17
      Caption = 'Time'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 0
    end
  end
  object lista_equipos: TComboBox
    Left = 16
    Top = 36
    Width = 105
    Height = 21
    Color = clCream
    Enabled = False
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ItemHeight = 13
    ParentFont = False
    TabOrder = 2
    TabStop = False
    OnChange = lista_equiposChange
    Items.Strings = (
      '  0 Irlanda'
      '  1 Escocia '
      '  2 Gales'
      '  3 Inglate'
      '  4 Portugal'
      '  5 Espan'
      '  6 Franca'
      '  7 Belgica'
      '  8 Holanda    '
      '  9 Suica      '
      '10 Itali'
      '11 Rep. Checa.'
      '12 Alemanh'
      '13 Dinamar'
      '14 Norueg'
      '15 Suecia'
      '16 Finland'
      '17 Poloni'
      '18 Eslovaqu'
      '19 Austria'
      '20 Hungria'
      '21 Esloveni'
      '22 Croacia'
      '23 Iugoslavia'
      '24 Romenia'
      '25 Bulgaria'
      '26 Grecia'
      '27 Turqui'
      '28 Ucrania'
      '29 Russia'
      '30 Marroco'
      '31 Tunisia'
      '32 Egito'
      '33 Nigeria'
      '34 Camaroes'
      '35 Afr. do Sul '
      '36 Senegal'
      '37 USA'
      '38 Mexico'
      '39 Costa Rica'
      '40 Colombia'
      '41 Brasil'
      '42 Peru'
      '43 Chile'
      '44 Paraguai'
      '45 Uruguai'
      '46 Argentina'
      '47 Equador'
      '48 Japao'
      '49 Corei'
      '50 China'
      '51 Iran'
      '52 Arabia   '
      '53 Australia'
      '54 Sel. Euro'
      '55 Sel. Mundo'
      '56 Inglaterra C'
      '57 Franca Clas'
      '58 Holanda Clas.'
      '59 Italia Cla'
      '60 Alemanha Cla'
      '61 Brasil Clas'
      '62 Argentina Clas'
      '63 Manchester'
      '64 Arsenal'
      '65 Chelsea'
      '66 Liverpool'
      '67 Leeds'
      '68 Newcastle'
      '69 Aston Villa'
      '70 Barcelona'
      '71 Real Madrid'
      '72 Valencia'
      '73 Deportivo'
      '74 Monaco'
      '75 Marseille'
      '76 PSG'
      '77 Burdeos'
      '78 Ajax'
      '79 Feyenoord'
      '80 PSV'
      '81 Inter'
      '82 Juventus'
      '83 Milan'
      '84 Lazio'
      '85 Parma'
      '86 Fiorentina'
      '87 Roma'
      '88 Borussia'
      '89 B. Munich'
      '90 B. Leverk.'
      '91 Olympiakos'
      '92 Galatasaray'
      '93 Dinamo Kiev'
      '94 Boca Juniors'
      '95 Master L. ')
  end
  object GroupBox1: TGroupBox
    Left = 8
    Top = 320
    Width = 505
    Height = 145
    TabOrder = 6
    object parriba: TSpeedButton
      Left = 152
      Top = 16
      Width = 33
      Height = 49
      Hint = 'Copiar jg.'
      Enabled = False
      Flat = True
      Glyph.Data = {blob parriba.Glyph.Data.bin 1210 sha256:7175f243999a37c4c72081e35e448c213e862b946101d876cf9bc4fa5119703c}
      Layout = blGlyphRight
      ParentShowHint = False
      ShowHint = True
      OnClick = parribaClick
    end
    object pabajo: TSpeedButton
      Left = 320
      Top = 16
      Width = 33
      Height = 49
      Hint = 'Inserir jug. '
      Enabled = False
      Flat = True
      Glyph.Data = {blob pabajo.Glyph.Data.bin 1210 sha256:c4514f0bd01b96b2f12ea39ffcb424deb8f045f29e426ed37272bc4d02a529d8}
      ParentShowHint = False
      ShowHint = True
      OnClick = pabajoClick
    end
    object mostrar_jugador_1: TSpeedButton
      Left = 8
      Top = 72
      Width = 25
      Height = 21
      Hint = '  Jogador  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob mostrar_jugador_1.Glyph.Data.bin 786 sha256:740f59d6c975d2b881a8417238f083b8778c21e4d2f74ff7a78d87445e90e3c9}
      ParentShowHint = False
      ShowHint = True
      OnClick = mostrar_jugadorClick
    end
    object mostrar_jugador_2: TSpeedButton
      Left = 472
      Top = 72
      Width = 25
      Height = 21
      Hint = '  Jogador  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob mostrar_jugador_2.Glyph.Data.bin 786 sha256:1ebb067b8849b5d7cc1f7468557ec2ba5c74155404f791ea7df2c2df8b417ef9}
      Margin = 1
      ParentShowHint = False
      ShowHint = True
      OnClick = mostrar_jugadorClick
    end
    object mostrar_estrategia_2: TSpeedButton
      Left = 472
      Top = 40
      Width = 25
      Height = 21
      Hint = ' Equipe  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob mostrar_estrategia_2.Glyph.Data.bin 786 sha256:e8f08f984e11fc8dddef50962e117bc45f030bdd23745ceff8dcaf36277c37ff}
      Margin = 1
      ParentShowHint = False
      ShowHint = True
      OnClick = mostrar_estrategiaClick
    end
    object mostrar_estrategia_1: TSpeedButton
      Left = 8
      Top = 40
      Width = 25
      Height = 21
      Hint = ' Equipe  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob mostrar_estrategia_1.Glyph.Data.bin 786 sha256:28422433d8af183d8ca1b00571774448e90e9369cd160c9c05e7c160910cb8dd}
      ParentShowHint = False
      ShowHint = True
      OnClick = mostrar_estrategiaClick
    end
    object Label1: TLabel
      Left = 464
      Top = 128
      Width = 33
      Height = 13
      Alignment = taCenter
      AutoSize = False
      Caption = 'Livre'
      Font.Charset = OEM_CHARSET
      Font.Color = clWhite
      Font.Height = -11
      Font.Name = 'Terminal'
      Font.Style = []
      ParentFont = False
      Layout = tlBottom
    end
    object Label2: TLabel
      Left = 464
      Top = 100
      Width = 31
      Height = 13
      Alignment = taCenter
      AutoSize = False
      Caption = 'SPC '
      Font.Charset = OEM_CHARSET
      Font.Color = clWhite
      Font.Height = -11
      Font.Name = 'Terminal'
      Font.Style = []
      ParentFont = False
      Layout = tlCenter
    end
    object Shape3: TShape
      Left = 113
      Top = 18
      Width = 32
      Height = 14
      Brush.Color = clCream
    end
    object banderita1: TImage
      Left = 114
      Top = 19
      Width = 30
      Height = 12
      Stretch = True
    end
    object Shape7: TShape
      Left = 360
      Top = 18
      Width = 32
      Height = 14
      Brush.Color = clCream
    end
    object banderita2: TImage
      Left = 361
      Top = 19
      Width = 30
      Height = 12
      Stretch = True
    end
    object paderecha2: TSpeedButton
      Left = 176
      Top = 72
      Width = 25
      Height = 21
      Hint = '  Mover todos pro time 2  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob paderecha2.Glyph.Data.bin 682 sha256:33047031730e6bd6720623e76e50fd6e0b1f1bab83beb7bc6adcfc2665467fdc}
      ParentShowHint = False
      ShowHint = True
      OnClick = paderecha2Click
    end
    object paderecha: TSpeedButton
      Left = 208
      Top = 72
      Width = 25
      Height = 21
      Hint = '  Mover pro time 2   '
      Enabled = False
      Flat = True
      Glyph.Data = {blob paderecha.Glyph.Data.bin 394 sha256:7a886420cf2255ee81a22558bc05e2a369cee6cb604cb5e161cf3540c942e9c2}
      ParentShowHint = False
      ShowHint = True
      OnClick = paderechaClick
    end
    object paderechaeizquierda: TSpeedButton
      Left = 240
      Top = 72
      Width = 25
      Height = 21
      Hint = 'Trocar jogadores'
      Enabled = False
      Flat = True
      Glyph.Data = {blob paderechaeizquierda.Glyph.Data.bin 682 sha256:bf43203242c300d09a2161bea2a207f38409d7450f6d6706f926b4e5a0588333}
      ParentShowHint = False
      ShowHint = True
      OnClick = paderechaeizquierdaClick
    end
    object paizquierda: TSpeedButton
      Left = 272
      Top = 72
      Width = 25
      Height = 21
      Hint = '  Mover pro time 1   '
      Enabled = False
      Flat = True
      Glyph.Data = {blob paizquierda.Glyph.Data.bin 394 sha256:73806f55afd7b4c9f465194899575b80a42c93ce7830d02512212fc7a9a6e421}
      ParentShowHint = False
      ShowHint = True
      OnClick = paizquierdaClick
    end
    object paizquierda2: TSpeedButton
      Left = 304
      Top = 72
      Width = 25
      Height = 21
      Hint = '  Mover todos pro time 2  '
      Enabled = False
      Flat = True
      Glyph.Data = {blob paizquierda2.Glyph.Data.bin 682 sha256:d83950c314d3dd1235f11f238ac5cc6ffcf20d918966d091add5bff36c408c2e}
      ParentShowHint = False
      ShowHint = True
      OnClick = paizquierda2Click
    end
    object help_team: TStaticText
      Left = 400
      Top = 16
      Width = 97
      Height = 23
      Cursor = crHandPoint
      Hint = 'Calcular precos           '
      Alignment = taRightJustify
      AutoSize = False
      Caption = 'Time Res.'
      Enabled = False
      Font.Charset = ANSI_CHARSET
      Font.Color = clActiveBorder
      Font.Height = -16
      Font.Name = 'Arial'
      Font.Style = [fsBold, fsUnderline]
      ParentFont = False
      ParentShowHint = False
      ShowHint = True
      TabOrder = 3
      OnClick = base_teamClick
    end
    object lista_jugadores_1: TComboBox
      Left = 40
      Top = 72
      Width = 129
      Height = 21
      Color = clCream
      Enabled = False
      Font.Charset = ANSI_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Pitch = fpFixed
      Font.Style = []
      ItemHeight = 13
      ParentFont = False
      TabOrder = 0
      OnChange = lista_jugadores_1Change
    end
    object lista_jugadores_2: TComboBox
      Left = 336
      Top = 72
      Width = 129
      Height = 21
      Color = clActiveBorder
      Enabled = False
      ItemHeight = 13
      TabOrder = 1
    end
    object base_team: TStaticText
      Left = 8
      Top = 16
      Width = 98
      Height = 23
      Cursor = crHandPoint
      Hint = 'Calcular precos           '
      Caption = 'Time Tit.'
      Enabled = False
      Font.Charset = ANSI_CHARSET
      Font.Color = clCream
      Font.Height = -16
      Font.Name = 'Arial'
      Font.Style = [fsBold, fsUnderline]
      ParentFont = False
      ParentShowHint = False
      ShowHint = True
      TabOrder = 2
      OnClick = base_teamClick
    end
    object dorsal1: TStaticText
      Left = 8
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 4
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal2: TStaticText
      Left = 27
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 5
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal3: TStaticText
      Left = 46
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 6
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal4: TStaticText
      Left = 65
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 7
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal5: TStaticText
      Left = 84
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 8
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal6: TStaticText
      Left = 103
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 9
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal7: TStaticText
      Left = 122
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 10
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal8: TStaticText
      Left = 141
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 11
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal9: TStaticText
      Left = 160
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 12
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal10: TStaticText
      Left = 179
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 13
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal11: TStaticText
      Left = 198
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 14
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal12: TStaticText
      Left = 217
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 15
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal13: TStaticText
      Left = 236
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 16
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal14: TStaticText
      Left = 255
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 17
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal15: TStaticText
      Left = 274
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 18
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal16: TStaticText
      Left = 293
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 19
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal17: TStaticText
      Left = 312
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 20
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal18: TStaticText
      Left = 331
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 21
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal19: TStaticText
      Left = 350
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 22
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal20: TStaticText
      Left = 369
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 23
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal21: TStaticText
      Left = 388
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 24
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal22: TStaticText
      Left = 407
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 25
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object dorsal23: TStaticText
      Left = 426
      Top = 112
      Width = 17
      Height = 17
      Cursor = crHandPoint
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '--'
      Color = clGray
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clSilver
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      TabOrder = 26
      OnClick = dorsalClick
      OnMouseDown = dorsalMouseDown
    end
    object casilla_xmlibres: TStaticText
      Left = 464
      Top = 112
      Width = 33
      Height = 17
      Hint = 'Free blocks for new Master League players'
      Alignment = taCenter
      AutoSize = False
      BorderStyle = sbsSunken
      Caption = '0'
      Color = clCream
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clNavy
      Font.Height = -13
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentColor = False
      ParentFont = False
      ParentShowHint = False
      ShowHint = True
      TabOrder = 27
    end
  end
  object lista_descarte: TListBox
    Left = 200
    Top = 336
    Width = 121
    Height = 49
    Color = clNavy
    Ctl3D = True
    Enabled = False
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ItemHeight = 13
    Items.Strings = (
      '  1 ...'
      '  2 ...'
      '  3 ...'
      '  4 ...'
      '  5 ...'
      '  6 ...'
      '  7 ...'
      '  8 ...'
      '  9 ...'
      '10 ...'
      '11 ...'
      '12 ...'
      '13 ...'
      '14 ...'
      '15 ...'
      '16 ...'
      '17 ...'
      '18 ...'
      '19 ...'
      '20 ...')
    ParentCtl3D = False
    ParentFont = False
    TabOrder = 9
  end
  object lista_equipos_2: TComboBox
    Left = 368
    Top = 360
    Width = 105
    Height = 21
    Color = clActiveBorder
    Enabled = False
    ItemHeight = 13
    TabOrder = 7
    TabStop = False
    OnChange = lista_equipos_2Change
    Items.Strings = (
      '  0 Irlanda'
      '  1 Escocia '
      '  2 Gales'
      '  3 Inglate'
      '  4 Portugal'
      '  5 Espan'
      '  6 Franca'
      '  7 Belgica'
      '  8 Holanda    '
      '  9 Suica      '
      '10 Itali'
      '11 Rep. Checa.'
      '12 Alemanh'
      '13 Dinamar'
      '14 Norueg'
      '15 Suecia'
      '16 Finland'
      '17 Poloni'
      '18 Eslovaqu'
      '19 Austria'
      '20 Hungria'
      '21 Esloveni'
      '22 Croacia'
      '23 Iugoslavia'
      '24 Romenia'
      '25 Bulgaria'
      '26 Grecia'
      '27 Turqui'
      '28 Ucrania'
      '29 Russia'
      '30 Marroco'
      '31 Tunisia'
      '32 Egito'
      '33 Nigeria'
      '34 Camaroes'
      '35 Afr. do Sul '
      '36 Senegal'
      '37 USA'
      '38 Mexico'
      '39 Costa Rica'
      '40 Colombia'
      '41 Brasil'
      '42 Peru'
      '43 Chile'
      '44 Paraguai'
      '45 Uruguai'
      '46 Argentina'
      '47 Equador'
      '48 Japao'
      '49 Corei'
      '50 China'
      '51 Iran'
      '52 Arabia   '
      '53 Australia'
      '54 Sel. Euro'
      '55 Sel. Mundo'
      '56 Inglaterra C'
      '57 Franca Clas'
      '58 Holanda Clas.'
      '59 Italia Cla'
      '60 Alemanha Cla'
      '61 Brasil Clas'
      '62 Argentina Clas'
      '63 Manchester'
      '64 Arsenal'
      '65 Chelsea'
      '66 Liverpool'
      '67 Leeds'
      '68 Newcastle'
      '69 Aston Villa'
      '70 Barcelona'
      '71 Real Madrid'
      '72 Valencia'
      '73 Deportivo'
      '74 Monaco'
      '75 Marseille'
      '76 PSG'
      '77 Burdeos'
      '78 Ajax'
      '79 Feyenoord'
      '80 PSV'
      '81 Inter'
      '82 Juventus'
      '83 Milan'
      '84 Lazio'
      '85 Parma'
      '86 Fiorentina'
      '87 Roma'
      '88 Borussia'
      '89 B. Munich'
      '90 B. Leverk.'
      '91 Olympiakos'
      '92 Galatasaray'
      '93 Dinamo Kiev'
      '94 Boca Juniors'
      '95 Default ML')
  end
  object lista_equipos_1: TComboBox
    Left = 48
    Top = 360
    Width = 105
    Height = 21
    Color = clCream
    Enabled = False
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ItemHeight = 13
    ParentFont = False
    TabOrder = 8
    TabStop = False
    Items.Strings = (
      '  0 Irlanda'
      '  1 Escocia '
      '  2 Gales'
      '  3 Inglate'
      '  4 Portugal'
      '  5 Espan'
      '  6 Franca'
      '  7 Belgica'
      '  8 Holanda    '
      '  9 Suica      '
      '10 Itali'
      '11 Rep. Checa.'
      '12 Alemanh'
      '13 Dinamar'
      '14 Norueg'
      '15 Suecia'
      '16 Finland'
      '17 Poloni'
      '18 Eslovaqu'
      '19 Austria'
      '20 Hungria'
      '21 Esloveni'
      '22 Croacia'
      '23 Iugoslavia'
      '24 Romenia'
      '25 Bulgaria'
      '26 Grecia'
      '27 Turqui'
      '28 Ucrania'
      '29 Russia'
      '30 Marroco'
      '31 Tunisia'
      '32 Egito'
      '33 Nigeria'
      '34 Camaroes'
      '35 Afr. do Sul '
      '36 Senegal'
      '37 USA'
      '38 Mexico'
      '39 Costa Rica'
      '40 Colombia'
      '41 Brasil'
      '42 Peru'
      '43 Chile'
      '44 Paraguai'
      '45 Uruguai'
      '46 Argentina'
      '47 Equador'
      '48 Japao'
      '49 Corei'
      '50 China'
      '51 Iran'
      '52 Arabia   '
      '53 Australia'
      '54 Sel. Euro'
      '55 Sel. Mundo'
      '56 Inglaterra C'
      '57 Franca Clas'
      '58 Holanda Clas.'
      '59 Italia Cla'
      '60 Alemanha Cla'
      '61 Brasil Clas'
      '62 Argentina Clas'
      '63 Manchester'
      '64 Arsenal'
      '65 Chelsea'
      '66 Liverpool'
      '67 Leeds'
      '68 Newcastle'
      '69 Aston Villa'
      '70 Barcelona'
      '71 Real Madrid'
      '72 Valencia'
      '73 Deportivo'
      '74 Monaco'
      '75 Marseille'
      '76 PSG'
      '77 Burdeos'
      '78 Ajax'
      '79 Feyenoord'
      '80 PSV'
      '81 Inter'
      '82 Juventus'
      '83 Milan'
      '84 Lazio'
      '85 Parma'
      '86 Fiorentina'
      '87 Roma'
      '88 Borussia'
      '89 B. Munich'
      '90 B. Leverk.'
      '91 Olympiakos'
      '92 Galatasaray'
      '93 Dinamo Kiev'
      '94 Boca Juniors'
      '95 Master L. ')
  end
  object dialogo_we: TOpenDialog
    Filter = 'ISO do W11(.bin)|*.BIN'
    Title = 'Abre'
    Left = 545
    Top = 390
  end
  object dialogo_mcr: TOpenDialog
    Filter = 'MCR do W11 (.mcr)        |*.MCR'
    Title = 'Abre'
    Left = 9
    Top = 238
  end
  object dialogo_tex: TOpenDialog
    Filter = 'Uni do W11(.bin)    |*.BIN'
    Title = 'Abre'
    Left = 489
    Top = 238
  end
  object dialogo_grabar_camiseta: TSaveDialog
    DefaultExt = 'bin'
    Filter = 'Uni do W11 (.bin)|*.bin'
    Options = [ofOverwritePrompt, ofHideReadOnly]
    Title = 'Extrair Uni do jogo        '
    Left = 392
    Top = 272
  end
  object dialogo_grabar_memory: TSaveDialog
    DefaultExt = 'mcr'
    Filter = 'MCR do W11 (.mcr)      |*.mcr'
    Options = [ofOverwritePrompt, ofHideReadOnly]
    Title = 'Extrair MCR do jogo              '
    Left = 104
    Top = 272
  end
  object ActionList1: TActionList
    Left = 368
    Top = 272
    object lanza_url: TBrowseURL
      Category = 'Internet'
      Caption = '&Browse URL'
      Hint = 'Browse URL'
      URL = 'http://www.w11.com.br         '
    end
  end
end
