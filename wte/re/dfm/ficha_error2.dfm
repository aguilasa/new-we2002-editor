object ficha_error2: Tficha_error2
  Left = 203
  Top = 214
  AlphaBlend = True
  AlphaBlendValue = 245
  BorderStyle = bsSingle
  Caption = 'Error'
  ClientHeight = 90
  ClientWidth = 376
  Color = clNavy
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_error2.Icon.Data.bin 318 sha256:69d12fc04cf6ef24fe32e8c46eafed94b786828fd50525ef5df772f25b08321e}
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object etiq1: TLabel
    Left = 11
    Top = 16
    Width = 350
    Height = 16
    Alignment = taCenter
    AutoSize = False
    Caption = 'That isn''t a memory card file'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object BitBtn3: TBitBtn
    Left = 150
    Top = 50
    Width = 73
    Height = 25
    Caption = ' Ok'
    Default = True
    ModalResult = 1
    TabOrder = 0
    Glyph.Data = {blob BitBtn3.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
end
