object jugador: Tjugador
  Left = 41
  Top = 211
  BorderIcons = [biSystemMenu]
  BorderStyle = bsSingle
  Caption = 'Player characteristics'
  ClientHeight = 273
  ClientWidth = 707
  Color = clNavy
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob jugador.Icon.Data.bin 318 sha256:e683b8ebbc5b1005e5632d08b3d06af2b12700a652353eab1800ee0e5a2d1617}
  OldCreateOrder = True
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object imagen_base: TImage
    Left = 264
    Top = 8
    Width = 185
    Height = 225
    Picture.Data = {blob imagen_base.Picture.Data.bin 42306 sha256:be60ee4a8a3b9f31f71918b904ec5c8a6d5ddf6b250d0a5dc8afffc9ec81d266}
  end
  object etiqhab1: TLabel
    Left = 8
    Top = 8
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Ataque '
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab2: TLabel
    Left = 8
    Top = 24
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Defesa  '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab1: TLabel
    Left = 232
    Top = 8
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab2: TLabel
    Left = 232
    Top = 24
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab3: TLabel
    Left = 8
    Top = 40
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Forca Fisica'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab4: TLabel
    Left = 8
    Top = 56
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Resist.'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab3: TLabel
    Left = 232
    Top = 40
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab4: TLabel
    Left = 232
    Top = 56
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab5: TLabel
    Left = 8
    Top = 72
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Velo.'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab6: TLabel
    Left = 8
    Top = 88
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Aceleracao  '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab5: TLabel
    Left = 232
    Top = 72
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab6: TLabel
    Left = 232
    Top = 88
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab7: TLabel
    Left = 8
    Top = 104
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Pas.'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab8: TLabel
    Left = 8
    Top = 120
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Chute      '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab7: TLabel
    Left = 232
    Top = 104
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab8: TLabel
    Left = 232
    Top = 120
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab9: TLabel
    Left = 8
    Top = 136
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Pontaria  '
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab10: TLabel
    Left = 8
    Top = 152
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Pulo'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab9: TLabel
    Left = 232
    Top = 136
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab10: TLabel
    Left = 232
    Top = 152
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab11: TLabel
    Left = 8
    Top = 168
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Cab.'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab12: TLabel
    Left = 8
    Top = 184
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Tecnica  '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab11: TLabel
    Left = 232
    Top = 168
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab12: TLabel
    Left = 232
    Top = 184
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab13: TLabel
    Left = 8
    Top = 200
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Dominio'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab14: TLabel
    Left = 8
    Top = 216
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Curva'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab13: TLabel
    Left = 232
    Top = 200
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab14: TLabel
    Left = 232
    Top = 216
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab15: TLabel
    Left = 8
    Top = 232
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Discipli.'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqhab16: TLabel
    Left = 8
    Top = 248
    Width = 241
    Height = 16
    AutoSize = False
    Caption = 'Reflexo '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab15: TLabel
    Left = 232
    Top = 232
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorhab16: TLabel
    Left = 232
    Top = 248
    Width = 17
    Height = 16
    AutoSize = False
    Caption = '12'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqprecio: TLabel
    Left = 608
    Top = 211
    Width = 89
    Height = 21
    Cursor = crHandPoint
    Hint = '  Calcular Preco  '
    AutoSize = False
    Caption = 'Preco  '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold, fsUnderline]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Layout = tlCenter
    OnClick = etiqprecioClick
  end
  object etiqapa1: TLabel
    Left = 464
    Top = 8
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Posicao '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa1: TLabel
    Left = 672
    Top = 8
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Gl'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa2: TLabel
    Left = 464
    Top = 24
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Pele      '
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa3: TLabel
    Left = 464
    Top = 40
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Cab.'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa2: TLabel
    Left = 672
    Top = 24
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa3: TLabel
    Left = 672
    Top = 40
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A1'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa4: TLabel
    Left = 464
    Top = 56
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Cor Cabelo'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa5: TLabel
    Left = 464
    Top = 72
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Barba      '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa4: TLabel
    Left = 672
    Top = 56
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa5: TLabel
    Left = 672
    Top = 72
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa6: TLabel
    Left = 464
    Top = 88
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Cor da Barba     '
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa7: TLabel
    Left = 464
    Top = 104
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Altura'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa6: TLabel
    Left = 672
    Top = 88
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa7: TLabel
    Left = 672
    Top = 104
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = '148'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa8: TLabel
    Left = 464
    Top = 120
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Peso'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa9: TLabel
    Left = 464
    Top = 136
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Ano'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa8: TLabel
    Left = 672
    Top = 120
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa9: TLabel
    Left = 672
    Top = 136
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = '15'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa10: TLabel
    Left = 464
    Top = 152
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Chut.'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa11: TLabel
    Left = 464
    Top = 168
    Width = 233
    Height = 16
    AutoSize = False
    Caption = 'Pe  '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa10: TLabel
    Left = 672
    Top = 152
    Width = 25
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'A'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa11: TLabel
    Left = 648
    Top = 168
    Width = 49
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Dire.'
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqapa12: TLabel
    Left = 464
    Top = 184
    Width = 233
    Height = 16
    AutoSize = False
    Caption = '3D(Trivela)   '
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object valorapa12: TLabel
    Left = 664
    Top = 184
    Width = 33
    Height = 16
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'NO'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object etiqnombre: TLabel
    Left = 264
    Top = 243
    Width = 185
    Height = 21
    AutoSize = False
    Caption = 'Nome       '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object imagen_barba_0: TImage
    Left = 318
    Top = 127
    Width = 59
    Height = 58
    Picture.Data = {blob imagen_barba_0.Picture.Data.bin 8666 sha256:41c44aca6126654dce41291eebcae6db0266ead4940b8cd486ddb23d26f6907d}
    Visible = False
  end
  object imagen_pelo: TImage
    Left = 289
    Top = 37
    Width = 144
    Height = 156
    Picture.Data = {blob imagen_pelo.Picture.Data.bin 22090 sha256:be43a7d7f36e461d54740316c57f1f4bbc1d35efcc2a15504405f59f5e328a2e}
  end
  object imagen_barba: TImage
    Left = 318
    Top = 127
    Width = 59
    Height = 58
    Picture.Data = {blob imagen_barba.Picture.Data.bin 8666 sha256:a1302d4fb707b1626b85d6a789f50ae81f147df2a70e43da877e7b299c5620eb}
  end
  object etiqdorsal: TLabel
    Left = 464
    Top = 211
    Width = 145
    Height = 21
    AutoSize = False
    Caption = 'Numero      '
    Color = clTeal
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object imghab1: TImage
    Left = 144
    Top = 8
    Width = 57
    Height = 8
    Picture.Data = {blob imghab1.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab2: TImage
    Left = 144
    Top = 24
    Width = 57
    Height = 8
    Picture.Data = {blob imghab2.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab3: TImage
    Left = 144
    Top = 40
    Width = 57
    Height = 8
    Picture.Data = {blob imghab3.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab4: TImage
    Left = 144
    Top = 56
    Width = 57
    Height = 8
    Picture.Data = {blob imghab4.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab5: TImage
    Left = 144
    Top = 72
    Width = 57
    Height = 8
    Picture.Data = {blob imghab5.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab6: TImage
    Left = 144
    Top = 88
    Width = 57
    Height = 8
    Picture.Data = {blob imghab6.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab7: TImage
    Left = 144
    Top = 104
    Width = 57
    Height = 8
    Picture.Data = {blob imghab7.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab8: TImage
    Left = 144
    Top = 120
    Width = 57
    Height = 8
    Picture.Data = {blob imghab8.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab9: TImage
    Left = 144
    Top = 136
    Width = 57
    Height = 8
    Picture.Data = {blob imghab9.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab10: TImage
    Left = 144
    Top = 152
    Width = 57
    Height = 8
    Picture.Data = {blob imghab10.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab11: TImage
    Left = 144
    Top = 168
    Width = 57
    Height = 8
    Picture.Data = {blob imghab11.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab12: TImage
    Left = 144
    Top = 184
    Width = 57
    Height = 8
    Picture.Data = {blob imghab12.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab13: TImage
    Left = 144
    Top = 200
    Width = 57
    Height = 8
    Picture.Data = {blob imghab13.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab14: TImage
    Left = 144
    Top = 216
    Width = 57
    Height = 8
    Picture.Data = {blob imghab14.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab15: TImage
    Left = 144
    Top = 232
    Width = 57
    Height = 8
    Picture.Data = {blob imghab15.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object imghab16: TImage
    Left = 144
    Top = 248
    Width = 57
    Height = 8
    Picture.Data = {blob imghab16.Picture.Data.bin 1442 sha256:5d94c131102bb033e2efc9f8be7c4d207118ebae2a14325100cf6f5e8f5b92d7}
  end
  object barrhab1: TScrollBar
    Left = 128
    Top = 12
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 2
    OnScroll = barrhabScroll
  end
  object barrhab2: TScrollBar
    Left = 128
    Top = 28
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 3
    OnScroll = barrhabScroll
  end
  object barrhab3: TScrollBar
    Left = 128
    Top = 44
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 4
    OnScroll = barrhabScroll
  end
  object barrhab4: TScrollBar
    Left = 128
    Top = 60
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 5
    OnScroll = barrhabScroll
  end
  object barrhab5: TScrollBar
    Left = 128
    Top = 76
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 6
    OnScroll = barrhabScroll
  end
  object barrhab6: TScrollBar
    Left = 128
    Top = 92
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 7
    OnScroll = barrhabScroll
  end
  object barrhab7: TScrollBar
    Left = 128
    Top = 108
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 8
    OnScroll = barrhabScroll
  end
  object barrhab8: TScrollBar
    Left = 128
    Top = 124
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 9
    OnScroll = barrhabScroll
  end
  object barrhab9: TScrollBar
    Left = 128
    Top = 140
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 10
    OnScroll = barrhabScroll
  end
  object barrhab10: TScrollBar
    Left = 128
    Top = 156
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 11
    OnScroll = barrhab_bisScroll
  end
  object barrhab11: TScrollBar
    Left = 128
    Top = 172
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 12
    OnScroll = barrhab_bisScroll
  end
  object barrhab12: TScrollBar
    Left = 128
    Top = 188
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 13
    OnScroll = barrhab_bisScroll
  end
  object barrhab13: TScrollBar
    Left = 128
    Top = 204
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 14
    OnScroll = barrhab_bisScroll
  end
  object barrhab14: TScrollBar
    Left = 128
    Top = 220
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 15
    OnScroll = barrhab_bisScroll
  end
  object barrhab15: TScrollBar
    Left = 128
    Top = 236
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 16
    OnScroll = barrhab_bisScroll
  end
  object barrhab16: TScrollBar
    Left = 128
    Top = 252
    Width = 89
    Height = 12
    Ctl3D = False
    LargeChange = 2
    Max = 7
    PageSize = 1
    ParentCtl3D = False
    TabOrder = 17
    OnScroll = barrhab_bisScroll
  end
  object BitBtn3: TBitBtn
    Left = 624
    Top = 240
    Width = 73
    Height = 25
    Cursor = crHandPoint
    Caption = 'Comple.'
    TabOrder = 18
    OnClick = BitBtn3Click
    Glyph.Data = {blob BitBtn3.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
  object casilla_precio: TEdit
    Left = 672
    Top = 211
    Width = 25
    Height = 21
    Color = clCream
    MaxLength = 3
    TabOrder = 19
    OnKeyPress = casilla_precioKeyPress
  end
  object flechasapa1: TUpDown
    Left = 600
    Top = 9
    Width = 33
    Height = 14
    Min = 0
    Max = 7
    Orientation = udHorizontal
    Position = 0
    TabOrder = 20
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa2: TUpDown
    Left = 600
    Top = 25
    Width = 33
    Height = 14
    Min = 0
    Max = 3
    Orientation = udHorizontal
    Position = 0
    TabOrder = 21
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa3: TUpDown
    Left = 600
    Top = 41
    Width = 32
    Height = 14
    Min = 0
    Max = 31
    Orientation = udHorizontal
    Position = 0
    TabOrder = 22
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa4: TUpDown
    Left = 600
    Top = 57
    Width = 32
    Height = 14
    Min = 0
    Max = 7
    Orientation = udHorizontal
    Position = 0
    TabOrder = 23
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa5: TUpDown
    Left = 600
    Top = 73
    Width = 32
    Height = 14
    Min = 0
    Max = 6
    Orientation = udHorizontal
    Position = 0
    TabOrder = 24
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa6: TUpDown
    Left = 600
    Top = 89
    Width = 33
    Height = 14
    Min = 0
    Max = 6
    Orientation = udHorizontal
    Position = 0
    TabOrder = 25
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa7: TUpDown
    Left = 600
    Top = 105
    Width = 33
    Height = 14
    Min = 0
    Max = 63
    Orientation = udHorizontal
    Position = 0
    TabOrder = 26
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa8: TUpDown
    Left = 600
    Top = 121
    Width = 33
    Height = 14
    Min = 0
    Max = 7
    Orientation = udHorizontal
    Position = 0
    TabOrder = 27
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa9: TUpDown
    Left = 600
    Top = 137
    Width = 33
    Height = 14
    Min = 0
    Max = 31
    Orientation = udHorizontal
    Position = 0
    TabOrder = 28
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa10: TUpDown
    Left = 600
    Top = 153
    Width = 33
    Height = 14
    Min = 0
    Max = 7
    Orientation = udHorizontal
    Position = 0
    TabOrder = 29
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa11: TUpDown
    Left = 600
    Top = 169
    Width = 33
    Height = 14
    Min = 0
    Max = 2
    Orientation = udHorizontal
    Position = 0
    TabOrder = 30
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object flechasapa12: TUpDown
    Left = 600
    Top = 185
    Width = 33
    Height = 14
    Min = 0
    Max = 1
    Orientation = udHorizontal
    Position = 0
    TabOrder = 31
    Thousands = False
    Wrap = False
    OnClick = flechasapaClick
  end
  object casilla_nombre: TEdit
    Left = 368
    Top = 243
    Width = 81
    Height = 21
    Color = clCream
    MaxLength = 10
    TabOrder = 1
    OnKeyPress = casilla_nombreKeyPress
  end
  object BitBtn1: TBitBtn
    Left = 464
    Top = 240
    Width = 73
    Height = 25
    Caption = 'Original '
    TabOrder = 32
    OnClick = BitBtn1Click
    Glyph.Data = {blob BitBtn1.Glyph.Data.bin 778 sha256:574b01c33617f560b56136716126dbcc553355f2eb9595e884a750a69de980e1}
  end
  object BitBtn2: TBitBtn
    Left = 544
    Top = 240
    Width = 73
    Height = 25
    Caption = 'Cancela'
    ModalResult = 7
    TabOrder = 0
    OnClick = BitBtn2Click
    Glyph.Data = {blob BitBtn2.Glyph.Data.bin 778 sha256:153f22e237fa119d66ddcbe21ff4c57230dd121a1cb9588959920b373f79cb12}
  end
  object casilla_dorsal: TEdit
    Left = 568
    Top = 211
    Width = 25
    Height = 21
    Color = clCream
    MaxLength = 10
    TabOrder = 33
    OnKeyPress = casilla_dorsalKeyPress
  end
end
