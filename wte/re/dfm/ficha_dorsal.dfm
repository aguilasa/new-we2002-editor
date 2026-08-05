object ficha_dorsal: Tficha_dorsal
  Left = 176
  Top = 442
  AlphaBlend = True
  AlphaBlendValue = 245
  BorderIcons = [biSystemMenu]
  BorderStyle = bsSingle
  Caption = 'Number'
  ClientHeight = 121
  ClientWidth = 129
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_dorsal.Icon.Data.bin 318 sha256:2576795bbec251035b2ef5e3c5f3cef2dd5bfeb7f2b132e4175ce95d123b2a43}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object etiq_dorsal: TLabel
    Left = 56
    Top = 24
    Width = 49
    Height = 41
    Alignment = taCenter
    AutoSize = False
    Caption = '7'
    Color = clHighlightText
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clRed
    Font.Height = -32
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = False
    ParentFont = False
    Layout = tlCenter
  end
  object Bevel1: TBevel
    Left = 56
    Top = 24
    Width = 49
    Height = 41
  end
  object BitBtn1: TBitBtn
    Left = 48
    Top = 80
    Width = 65
    Height = 25
    Cursor = crHandPoint
    Caption = ' Ok'
    Default = True
    ModalResult = 1
    TabOrder = 0
    OnClick = BitBtn1Click
    Glyph.Data = {blob BitBtn1.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
  object scroll_dorsal: TScrollBar
    Left = 17
    Top = 8
    Width = 16
    Height = 105
    Kind = sbVertical
    LargeChange = 4
    Max = 99
    Min = 1
    PageSize = 0
    Position = 1
    TabOrder = 1
    OnChange = scroll_dorsalChange
  end
end
