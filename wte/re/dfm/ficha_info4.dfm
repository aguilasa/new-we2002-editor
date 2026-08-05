object ficha_info4: Tficha_info4
  Left = 252
  Top = 258
  Width = 284
  Height = 158
  AlphaBlend = True
  AlphaBlendValue = 245
  Caption = 'W11 TE PT! '
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_info4.Icon.Data.bin 318 sha256:d0b57a6a7fb22398a1b61d15ec4d69b5c08bd77f3c3c835050b31dd98cb7cf86}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object etiq1: TLabel
    Left = 8
    Top = 16
    Width = 257
    Height = 16
    Alignment = taCenter
    AutoSize = False
    Caption = 'This operation didn''t free any space'
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
  object etiq2: TLabel
    Left = 8
    Top = 40
    Width = 257
    Height = 16
    Alignment = taCenter
    AutoSize = False
    Caption = 'The player substituted is still being used'
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
  object etiq3: TLabel
    Left = 8
    Top = 56
    Width = 257
    Height = 16
    Alignment = taCenter
    AutoSize = False
    Caption = 'in another  different place(s) of the game'
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
  object BitBtn6: TBitBtn
    Left = 104
    Top = 84
    Width = 73
    Height = 25
    Caption = ' Ok'
    ModalResult = 1
    TabOrder = 0
    Glyph.Data = {blob BitBtn6.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
end
