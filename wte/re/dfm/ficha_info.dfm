object ficha_info: Tficha_info
  Left = 371
  Top = 350
  AlphaBlend = True
  AlphaBlendValue = 245
  BorderStyle = bsSingle
  Caption = 'Atalhos    '
  ClientHeight = 164
  ClientWidth = 258
  Color = clSilver
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_info.Icon.Data.bin 318 sha256:d0b57a6a7fb22398a1b61d15ec4d69b5c08bd77f3c3c835050b31dd98cb7cf86}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object etiq1: TLabel
    Left = 8
    Top = 16
    Width = 198
    Height = 16
    Caption = 'Para as cores, use os controles: '
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
  object Label1: TLabel
    Left = 8
    Top = 40
    Width = 215
    Height = 16
    Caption = '-  Ctrl + MouseDir p/ copiar uma cor   '
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
    Top = 56
    Width = 152
    Height = 16
    Caption = '-  Ctrl + MouseEsq p/ cola-la  '
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
    Top = 80
    Width = 251
    Height = 16
    Caption = '-  Ctrl + Shift + MouseDir p/ copiar todas cores'
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
    Top = 96
    Width = 213
    Height = 16
    Caption = '-  Ctrl + Shift + MouseEsq p/ cola-las   '
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
    Left = 89
    Top = 127
    Width = 73
    Height = 25
    Caption = ' Ok'
    Default = True
    ModalResult = 1
    TabOrder = 0
    Glyph.Data = {blob BitBtn3.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
end
