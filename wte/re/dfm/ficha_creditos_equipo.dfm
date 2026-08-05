object ficha_creditos_equipo: Tficha_creditos_equipo
  Left = 55
  Top = 307
  Width = 285
  Height = 124
  AlphaBlend = True
  AlphaBlendValue = 245
  Caption = 'Calcular precos  '
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_creditos_equipo.Icon.Data.bin 318 sha256:bdcd57af2aedffc5591198d89b55b6adf4f295bbc3dcfbc71afca377edf6d471}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object etiq1: TLabel
    Left = 8
    Top = 16
    Width = 259
    Height = 16
    Alignment = taCenter
    Caption = 'Desejar calcular o preco dos jogadores???      '
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -13
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentFont = False
  end
  object BitBtn1: TBitBtn
    Left = 144
    Top = 48
    Width = 73
    Height = 25
    Caption = ' Sim'
    Default = True
    ModalResult = 6
    TabOrder = 0
    Glyph.Data = {blob BitBtn1.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
  object BitBtn2: TBitBtn
    Left = 56
    Top = 48
    Width = 73
    Height = 25
    Cancel = True
    Caption = 'Nao'
    ModalResult = 7
    TabOrder = 1
    Glyph.Data = {blob BitBtn2.Glyph.Data.bin 778 sha256:153f22e237fa119d66ddcbe21ff4c57230dd121a1cb9588959920b373f79cb12}
  end
end
