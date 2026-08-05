object ficha_warning: Tficha_warning
  Left = 225
  Top = 242
  AlphaBlend = True
  AlphaBlendValue = 245
  BorderStyle = bsSingle
  Caption = 'Cuidado'
  ClientHeight = 137
  ClientWidth = 333
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_warning.Icon.Data.bin 318 sha256:9f8c22f63f9402c0da76e0c2dcb0b5970235deeafb4b547d99ea319e5b5042f8}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object etiq1: TLabel
    Left = 8
    Top = 16
    Width = 316
    Height = 16
    Caption = ' O tamanho do .bin nao corresponde. O tamanho exato e de'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object etiq2: TLabel
    Left = 8
    Top = 32
    Width = 298
    Height = 16
    Caption = '474.431.328 bytes.O editor funcionara mal!!!!!!!!.'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object etiq4: TLabel
    Left = 8
    Top = 64
    Width = 169
    Height = 16
    Caption = 'Continuar mesmo assim???      '
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object BitBtn1: TBitBtn
    Left = 176
    Top = 104
    Width = 73
    Height = 25
    Caption = ' Sim'
    Default = True
    ModalResult = 6
    TabOrder = 1
    Glyph.Data = {blob BitBtn1.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
  object BitBtn2: TBitBtn
    Left = 80
    Top = 104
    Width = 73
    Height = 25
    Cancel = True
    Caption = 'Nao'
    ModalResult = 7
    TabOrder = 0
    Glyph.Data = {blob BitBtn2.Glyph.Data.bin 778 sha256:153f22e237fa119d66ddcbe21ff4c57230dd121a1cb9588959920b373f79cb12}
  end
end
