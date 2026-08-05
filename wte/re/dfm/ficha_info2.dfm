object ficha_info2: Tficha_info2
  Left = 188
  Top = 314
  AlphaBlend = True
  AlphaBlendValue = 245
  BorderStyle = bsSingle
  Caption = 'W11TE PT!  '
  ClientHeight = 157
  ClientWidth = 408
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_info2.Icon.Data.bin 318 sha256:d0b57a6a7fb22398a1b61d15ec4d69b5c08bd77f3c3c835050b31dd98cb7cf86}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object Label1: TLabel
    Left = 8
    Top = 16
    Width = 377
    Height = 16
    Caption = 'The actual number of free memory blocks available in the game'
    Color = clSilver
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = False
    ParentFont = False
    Transparent = True
  end
  object Label2: TLabel
    Left = 8
    Top = 32
    Width = 314
    Height = 16
    Caption = 'is shown in the white bottom-right box in the main form.'
    Color = clSilver
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = False
    ParentFont = False
    Transparent = True
  end
  object Label3: TLabel
    Left = 8
    Top = 56
    Width = 387
    Height = 16
    Caption = 'You can make free blocks by moving players from national teams'
    Color = clSilver
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = False
    ParentFont = False
    Transparent = True
  end
  object Label4: TLabel
    Left = 8
    Top = 72
    Width = 383
    Height = 16
    Caption = 'to Master League ones. This will "link" (L) the players, freeing one'
    Color = clSilver
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = False
    ParentFont = False
    Transparent = True
  end
  object Label5: TLabel
    Left = 8
    Top = 88
    Width = 395
    Height = 16
    Caption = 'block each time ONLY if the replaced players weren''t already links.'
    Color = clSilver
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlack
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = False
    ParentFont = False
    Transparent = True
  end
  object BitBtn3: TBitBtn
    Left = 161
    Top = 119
    Width = 73
    Height = 25
    Caption = ' Ok'
    Default = True
    ModalResult = 1
    TabOrder = 0
    Glyph.Data = {blob BitBtn3.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
end
