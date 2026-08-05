object ficha_error: Tficha_error
  Left = 226
  Top = 293
  AlphaBlend = True
  AlphaBlendValue = 245
  BorderStyle = bsSingle
  Caption = 'Error'
  ClientHeight = 89
  ClientWidth = 329
  Color = clNavy
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_error.Icon.Data.bin 318 sha256:69d12fc04cf6ef24fe32e8c46eafed94b786828fd50525ef5df772f25b08321e}
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object SpeedButton1: TSpeedButton
    Left = 104
    Top = 50
    Width = 25
    Height = 25
    Flat = True
    Glyph.Data = {blob SpeedButton1.Glyph.Data.bin 658 sha256:e66257be72bdca81c670c6ddc318eea20f399f254d2231f62c27075464237c9b}
    OnClick = SpeedButton1Click
  end
  object etiq1: TLabel
    Left = 11
    Top = 16
    Width = 302
    Height = 16
    Alignment = taCenter
    AutoSize = False
    Caption = 'You need at least 1 memory block free to do that'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object BitBtn3: TBitBtn
    Left = 134
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
