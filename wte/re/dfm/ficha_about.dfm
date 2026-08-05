object ficha_about: Tficha_about
  Left = 232
  Top = 169
  BorderIcons = []
  BorderStyle = bsNone
  Caption = 'Sobre...'
  ClientHeight = 274
  ClientWidth = 319
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  Icon.Data = {blob ficha_about.Icon.Data.bin 318 sha256:d0b57a6a7fb22398a1b61d15ec4d69b5c08bd77f3c3c835050b31dd98cb7cf86}
  OldCreateOrder = False
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object Image1: TImage
    Left = 0
    Top = 0
    Width = 319
    Height = 274
    Align = alClient
    Center = True
    Picture.Data = {blob Image1.Picture.Data.bin 88770 sha256:e8bc0373d6908764538b66dcdad53533b1cd7656974ff63ecc489997c1a29c3e}
  end
  object SpeedButton1: TSpeedButton
    Left = 168
    Top = 232
    Width = 33
    Height = 25
    Cursor = crHandPoint
    Hint = 'website'
    Action = lanza_url
    Caption = ' '
    Glyph.Data = {blob SpeedButton1.Glyph.Data.bin 730 sha256:9bb1742e2c3a7e3e467b038e527306fc0a2a673ef8ea8990c8fd2e699a7d92dc}
    Layout = blGlyphBottom
    Margin = 5
    ParentShowHint = False
    ShowHint = True
    Transparent = False
    Visible = False
  end
  object imagen_url: TImage
    Left = 24
    Top = 129
    Width = 157
    Height = 85
    Cursor = crHandPoint
    Hint = 'Visite a W11 Online:-)'
    ParentShowHint = False
    Picture.Data = {blob imagen_url.Picture.Data.bin 40186 sha256:58b1f46ca241e8018540e6f768a15a918fa3debed4212acbfcbf25cdf266ca5a}
    ShowHint = True
    OnClick = imagen_urlClick
  end
  object BitBtn3: TBitBtn
    Left = 25
    Top = 232
    Width = 136
    Height = 24
    Caption = ' Ok'
    Default = True
    ModalResult = 1
    TabOrder = 0
    Glyph.Data = {blob BitBtn3.Glyph.Data.bin 778 sha256:2e1dc71591a56997e3590a39defddbe983c7e84eaa105b5c410a8ff9a57b524c}
  end
  object ActionList1: TActionList
    Left = 528
    Top = 216
    object lanza_url: TBrowseURL
      Category = 'Internet'
      Caption = '&Browse URL'
      Hint = 'Browse URL'
      URL = 'http://www.w11.com.br         '
    end
  end
end
