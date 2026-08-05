object estrategia: Testrategia
  Left = 127
  Top = 50
  BorderIcons = [biSystemMenu]
  BorderStyle = bsSingle
  Caption = 'Estrategia'
  ClientHeight = 498
  ClientWidth = 529
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob estrategia.Icon.Data.bin 318 sha256:172298cd4da01b9c7054f010fe421e5a93b17c77424c200425af4cae1bb0872d}
  OldCreateOrder = True
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object Shape3: TShape
    Left = 432
    Top = 8
    Width = 81
    Height = 49
    Pen.Width = 2
  end
  object campo: TImage
    Left = 16
    Top = 8
    Width = 395
    Height = 246
    AutoSize = True
    Picture.Data = {blob campo.Picture.Data.bin 292314 sha256:38e55b80d40224f5f8898d73d4a9421c001b0a780b70fe72a176577fba7f5195}
    OnMouseMove = campoMouseMove
  end
  object etiqjug2: TLabel
    Left = 80
    Top = 48
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug0: TLabel
    Left = -2
    Top = 137
    Width = 65
    Height = 16
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug1: TLabel
    Left = 64
    Top = 136
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug3: TLabel
    Left = 80
    Top = 224
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug4: TLabel
    Left = 144
    Top = 136
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug5: TLabel
    Left = 184
    Top = 48
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug6: TLabel
    Left = 184
    Top = 224
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug7: TLabel
    Left = 224
    Top = 136
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug8: TLabel
    Left = 320
    Top = 136
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug9: TLabel
    Left = 304
    Top = 48
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object etiqjug10: TLabel
    Left = 304
    Top = 224
    Width = 65
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'Rbto Carlos'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
    Transparent = True
  end
  object rectangulo: TShape
    Left = 24
    Top = 56
    Width = 81
    Height = 73
    Brush.Color = clBlack
    Pen.Color = clMaroon
    Pen.Width = 2
    Visible = False
    OnDragDrop = rectanguloDragDrop
    OnDragOver = rectanguloDragOver
  end
  object bola0: TShape
    Left = 22
    Top = 121
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
  end
  object bola1: TShape
    Left = 88
    Top = 120
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola2: TShape
    Left = 104
    Top = 32
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola4: TShape
    Left = 168
    Top = 120
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola3: TShape
    Left = 104
    Top = 208
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola6: TShape
    Left = 208
    Top = 208
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola7: TShape
    Left = 248
    Top = 120
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola5: TShape
    Left = 208
    Top = 32
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola9: TShape
    Left = 328
    Top = 32
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola8: TShape
    Left = 344
    Top = 120
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object bola10: TShape
    Left = 328
    Top = 208
    Width = 15
    Height = 14
    Brush.Color = clGreen
    DragCursor = crDefault
    Pen.Width = 2
    Shape = stCircle
    OnEndDrag = bolaEndDrag
    OnMouseDown = bolaMouseDown
    OnMouseMove = bolaMouseMove
  end
  object etiqestr1: TLabel
    Left = 16
    Top = 312
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Sem estrate.'
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
  object etiqestr2: TLabel
    Left = 16
    Top = 328
    Width = 129
    Height = 16
    AutoSize = False
    Caption = ' Grupo '
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
  object etiqestr3: TLabel
    Left = 16
    Top = 344
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Meio-Campo    '
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
  object etiqestr4: TLabel
    Left = 16
    Top = 360
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Ala Direira  '
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
  object etiqestr5: TLabel
    Left = 16
    Top = 376
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Ala esquerda'
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
  object etiqestr6: TLabel
    Left = 16
    Top = 392
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Parelelo        '
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
  object etiqestr7: TLabel
    Left = 16
    Top = 408
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Invertida   '
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
  object etiqestr8: TLabel
    Left = 16
    Top = 424
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Zag. Ataque'
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
  object etiqestr9: TLabel
    Left = 16
    Top = 440
    Width = 129
    Height = 16
    AutoSize = False
    Caption = ' Pressao '
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
  object etiqestr10: TLabel
    Left = 16
    Top = 456
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'Contra-Ataque '
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
  object etiqestr11: TLabel
    Left = 16
    Top = 472
    Width = 129
    Height = 16
    AutoSize = False
    Caption = 'L.Impedimento'
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
  object malla1: TImage
    Left = 144
    Top = 312
    Width = 96
    Height = 176
    Cursor = crHandPoint
    Picture.Data = {blob malla1.Picture.Data.bin 50754 sha256:7a24d7163bea4379c694fc10a4fd0692a1417b1da4d2a8e464be424fe9638731}
    OnMouseDown = malla1MouseDown
  end
  object simbolo3: TShape
    Left = 195
    Top = 315
    Width = 18
    Height = 10
    Brush.Color = clBlue
  end
  object simbolo1: TShape
    Left = 147
    Top = 315
    Width = 18
    Height = 10
    Brush.Color = clLime
  end
  object simbolo4: TShape
    Left = 219
    Top = 315
    Width = 18
    Height = 10
    Brush.Color = clRed
  end
  object simbolo2: TShape
    Left = 171
    Top = 315
    Width = 18
    Height = 10
    Brush.Color = clFuchsia
  end
  object malla2: TImage
    Left = 368
    Top = 312
    Width = 144
    Height = 176
    Cursor = crHandPoint
    Picture.Data = {blob malla2.Picture.Data.bin 76802 sha256:cd537c00e5fae527ea4add49c03b61d62e4fa053851fc0a4cdb5f832e84d691f}
    OnMouseDown = malla2MouseDown
  end
  object jugador1: TLabel
    Left = 280
    Top = 312
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador2: TLabel
    Left = 280
    Top = 328
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador3: TLabel
    Left = 280
    Top = 344
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador4: TLabel
    Left = 280
    Top = 360
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador5: TLabel
    Left = 280
    Top = 376
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador6: TLabel
    Left = 280
    Top = 392
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador7: TLabel
    Left = 280
    Top = 408
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador8: TLabel
    Left = 280
    Top = 424
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador9: TLabel
    Left = 280
    Top = 440
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador10: TLabel
    Left = 280
    Top = 456
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object jugador11: TLabel
    Left = 280
    Top = 472
    Width = 89
    Height = 16
    AutoSize = False
    Caption = ' Rbto Carlos'
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
  object tirador1: TShape
    Left = 371
    Top = 315
    Width = 18
    Height = 10
  end
  object tirador2: TShape
    Left = 395
    Top = 315
    Width = 18
    Height = 10
  end
  object tirador3: TShape
    Left = 419
    Top = 315
    Width = 18
    Height = 10
  end
  object tirador4: TShape
    Left = 443
    Top = 315
    Width = 18
    Height = 10
  end
  object tirador5: TShape
    Left = 467
    Top = 315
    Width = 18
    Height = 10
  end
  object tirador6: TShape
    Left = 491
    Top = 315
    Width = 18
    Height = 10
  end
  object etiqpos1: TLabel
    Left = 256
    Top = 312
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'GK'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clSilver
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos2: TLabel
    Left = 256
    Top = 328
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'CB'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clTeal
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos3: TLabel
    Left = 256
    Top = 344
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'CB'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clTeal
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos4: TLabel
    Left = 256
    Top = 360
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'CB'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clTeal
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos5: TLabel
    Left = 256
    Top = 376
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'DH'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clGreen
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos6: TLabel
    Left = 256
    Top = 392
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'LH'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clGreen
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos7: TLabel
    Left = 256
    Top = 408
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'RH'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clGreen
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos8: TLabel
    Left = 256
    Top = 424
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'OH'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clGreen
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos9: TLabel
    Left = 256
    Top = 440
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'CF'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clMaroon
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos10: TLabel
    Left = 256
    Top = 456
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'CF'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clMaroon
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object etiqpos11: TLabel
    Left = 256
    Top = 472
    Width = 25
    Height = 17
    Alignment = taCenter
    AutoSize = False
    Caption = 'CF'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clMaroon
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = False
    Layout = tlCenter
  end
  object Image1: TImage
    Left = 144
    Top = 296
    Width = 97
    Height = 17
    Picture.Data = {blob Image1.Picture.Data.bin 2626 sha256:3f6dd93dab6f88523fca2de7f4d750b5f15b810da6a20f98beb5ba9f50c1dcca}
  end
  object Label1: TLabel
    Left = 368
    Top = 296
    Width = 25
    Height = 17
    Hint = 'Short Foul Kick'
    Alignment = taCenter
    AutoSize = False
    Caption = 'SF'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Transparent = True
    Layout = tlCenter
  end
  object Label2: TLabel
    Left = 392
    Top = 296
    Width = 25
    Height = 17
    Hint = 'Long Foul Kick'
    Alignment = taCenter
    AutoSize = False
    Caption = 'LF'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Transparent = True
    Layout = tlCenter
  end
  object Label3: TLabel
    Left = 416
    Top = 296
    Width = 25
    Height = 17
    Hint = 'Right Corner Kick'
    Alignment = taCenter
    AutoSize = False
    Caption = 'RC'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Transparent = True
    Layout = tlCenter
  end
  object Label4: TLabel
    Left = 440
    Top = 296
    Width = 25
    Height = 17
    Hint = 'Left Corner Kick'
    Alignment = taCenter
    AutoSize = False
    Caption = 'LC'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Transparent = True
    Layout = tlCenter
  end
  object Label5: TLabel
    Left = 464
    Top = 296
    Width = 25
    Height = 17
    Hint = 'Penalty Kick'
    Alignment = taCenter
    AutoSize = False
    Caption = 'PK'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Transparent = True
    Layout = tlCenter
  end
  object Label6: TLabel
    Left = 488
    Top = 296
    Width = 25
    Height = 17
    Hint = 'Captain'
    Alignment = taCenter
    AutoSize = False
    Caption = 'CP'
    Color = clBlack
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    ParentShowHint = False
    ShowHint = True
    Transparent = True
    Layout = tlCenter
  end
  object bandera: TImage
    Left = 433
    Top = 9
    Width = 79
    Height = 47
    Stretch = True
  end
  object Label7: TLabel
    Left = 96
    Top = 264
    Width = 41
    Height = 25
    AutoSize = False
    Caption = 'Casa'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Transparent = True
    Layout = tlCenter
  end
  object Label8: TLabel
    Left = 267
    Top = 264
    Width = 41
    Height = 25
    AutoSize = False
    Caption = 'Vis.'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Transparent = True
    Layout = tlCenter
  end
  object Label9: TLabel
    Left = 16
    Top = 264
    Width = 57
    Height = 25
    AutoSize = False
    Caption = 'RADAR:'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Transparent = True
    Layout = tlCenter
  end
  object Label10: TLabel
    Left = 16
    Top = 264
    Width = 305
    Height = 25
    AutoSize = False
    Caption = '____________________________________________'
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'Arial'
    Font.Style = [fsBold]
    ParentColor = False
    ParentFont = False
    Transparent = True
    Layout = tlCenter
  end
  object lista_formaciones: TListBox
    Left = 432
    Top = 70
    Width = 81
    Height = 115
    Color = clNavy
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ItemHeight = 13
    Items.Strings = (
      'STOCK'
      'DEFAULT'
      '4 - 5 - 1  A'
      '4 - 5 - 1  B'
      '4 - 4 - 2  A'
      '4 - 4 - 2  B'
      '4 - 3 - 3  A'
      '4 - 3 - 3  B'
      '3 - 6 - 1  A'
      '3 - 6 - 1  B'
      '3 - 5 - 2  A'
      '3 - 5 - 2  B'
      '3 - 4 - 3  A'
      '3 - 4 - 3  B'
      '5 - 4 - 1  A'
      '5 - 4 - 1  B'
      '5 - 3 - 2  A'
      '5 - 3 - 2  B')
    ParentFont = False
    TabOrder = 0
    OnClick = lista_formacionesClick
  end
  object BitBtn6: TBitBtn
    Left = 432
    Top = 261
    Width = 81
    Height = 25
    Cursor = crHandPoint
    Caption = ' Accept'
    TabOrder = 1
    OnClick = BitBtn3Click
    Glyph.Data = {blob BitBtn6.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
  object BitBtn1: TBitBtn
    Left = 432
    Top = 197
    Width = 81
    Height = 25
    Caption = ' Default '
    TabOrder = 2
    OnClick = BitBtn1Click
    Glyph.Data = {blob BitBtn1.Glyph.Data.bin 778 sha256:574b01c33617f560b56136716126dbcc553355f2eb9595e884a750a69de980e1}
  end
  object BitBtn2: TBitBtn
    Left = 432
    Top = 229
    Width = 81
    Height = 25
    Caption = 'Cancela'
    ModalResult = 7
    TabOrder = 3
    Glyph.Data = {blob BitBtn2.Glyph.Data.bin 778 sha256:153f22e237fa119d66ddcbe21ff4c57230dd121a1cb9588959920b373f79cb12}
  end
  object ComboBox1: TComboBox
    Left = 144
    Top = 264
    Width = 97
    Height = 22
    Style = csOwnerDrawFixed
    Color = clInactiveCaption
    Ctl3D = True
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ItemHeight = 16
    ParentCtl3D = False
    ParentFont = False
    TabOrder = 4
    OnDrawItem = ComboBoxDrawItem
    Items.Strings = (
      ''
      ''
      ''
      ''
      ''
      ''
      ''
      '')
  end
  object ComboBox2: TComboBox
    Left = 315
    Top = 264
    Width = 97
    Height = 22
    Style = csOwnerDrawFixed
    Color = clInactiveCaption
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -11
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ItemHeight = 16
    ParentFont = False
    TabOrder = 5
    OnDrawItem = ComboBoxDrawItem
    Items.Strings = (
      ''
      ''
      ''
      ''
      ''
      ''
      ''
      '')
  end
  object reloj: TTimer
    Enabled = False
    Interval = 1
    OnTimer = relojTimer
    Left = 392
    Top = 24
  end
end
