#!/usr/bin/env python3
"""Converte os 18 DFM de `wte/re/dfm/` em `.lfm` da LCL e no esqueleto das
unidades Pascal (WTE-TASK-10).

    python3 wte/tools/dfm2lfm.py            # gera
    python3 wte/tools/dfm2lfm.py --check    # regera em memoria e compara

Entradas, todas somente-leitura:

    wte/re/dfm/*.dfm              estrutura dos 18 formularios (WTE-TASK-03)
    wte/re/dfm/blobs/**/*.bin     os 118 blobs binarios (gitignored, regeravel)
    wte/re/published_methods.tsv  os 96 handlers com dono (WTE-TASK-04)

Saidas, todas geradas -- **nao editar a mao**:

    wte/forms/ep2002_*.lfm        os 18 formularios em LFM
    wte/src/ep2002_*.pas          o esqueleto das 18 unidades
    wte/forms/conversao.md        o que a conversao descartou ou substituiu


O nome das unidades
-------------------

A secao 1.3 do plano recuperou 13 nomes de unidade dos exports de finalizacao
do `.exe` (`@@Tep2002_about@Initialize`, ...). Todos os 13 seguem a mesma
regra: `ep2002_` + o nome do formulario sem o prefixo `ficha_`. As outras 5
unidades (`MainForm`, `estrategia`, `jugador`, `ficha_color`, `ficha_error`)
nao exportam finalizacao e por isso nao tem nome medido; para elas a mesma
regra e aplicada. `UNIDADES_MEDIDAS` guarda os 13 e o gerador **aborta** se a
regra deixar de reproduzi-los -- a extrapolacao para as outras 5 so vale
enquanto a regra continuar batendo onde ha medida.

O `.lfm` recebe o nome da **unidade**, nao o do formulario: e a convencao do
Lazarus (o `.pas` e o `.lfm` sao irmaos de mesmo radical) e e o que permite
abrir o projeto na IDE grafica sem que ela reescreva nada. O `.dfm` de origem
continua com o nome do formulario, e a tabela em `conversao.md` liga os dois.


As quatro excecoes da tarefa
----------------------------

**1. Blobs binarios.** Os 118 `vaBinary` nao estao no `.dfm`: ele guarda
`{blob <arquivo> <tamanho> sha256:<hash>}` e os bytes vivem em
`wte/re/dfm/blobs/`, que e gitignored (ver a secao 2 do plano e a WTE-TASK-03).
Este gerador resolve a referencia lendo o `.bin` ao lado e emite hex inline no
formato canonico do `ObjectBinaryToText` do FPC -- `{`, linhas de 32 bytes em
hexadecimal maiusculo indentadas em `prop + 2`, `}` na coluna da propriedade.
E o unico formato que a LCL le, conferido contra os `.lfm` do proprio Lazarus.

O que acontece **sem** `blobs/`, que e o estado de um clone limpo:

- **modo de escrita aborta**, dizendo qual blob falta e que comando o
  materializa. Emitir `.lfm` sem a imagem seria emitir formulario parcial;
- **`--check` nao precisa dos `.bin`.** Ele nao regenera o hex: regenera o
  *layout* (que so depende do tamanho, e o tamanho esta no `.dfm`), le os
  digitos que estao no `.lfm` versionado, decodifica e confere tamanho e
  SHA-256 contra a referencia do `.dfm`. A garantia e byte a byte e nao depende
  de nada fora do que o git versiona.

  Isso e deliberado e e a licao da CORR-WTE-004: no `dfm_extract.py` o
  `--check` exigia os `.bin` no disco e ficava vermelho em clone limpo, dando o
  mesmo codigo de saida de um arquivo editado a mao -- que e o que o gate
  existe para pegar. Aqui o modo de conferencia nao le `blobs/` de forma
  alguma, entao o problema nao tem como voltar.

**2. `TBrowseURL` -> `TLabel`.** Duas instancias, `lanza_url`, uma em
`ficha_about` e outra em `MainForm`. A WTE-TASK-07 mediu que nao e componente
de terceiro: e a acao padrao da VCL, unidade `Extactns`. A LCL nao a tem. As
duas viram `TLabel`, ficam onde estavam (dentro do `TActionList`) e o `TODO`
sai **na unidade**, junto do campo, com a URL preservada numa constante. O
`Action = lanza_url` do `SpeedButton1` de `ficha_about` cai junto: a
propriedade existe na LCL, mas o valor agora aponta para um `TLabel`, e o
leitor de LFM recusaria.

**3. Propriedade que a LCL nao tem.** O enunciado da tarefa manda vira-la
comentario dentro do `.lfm`. **Isso nao e possivel** -- e nao e opiniao:

    $ ./lfmcheck t_slashcomment.lfm t_bracecomment.lfm
    FALHA t_slashcomment.lfm
    FALHA t_bracecomment.lfm

O `TParser` da FCL, que e quem le LFM tanto no `LFMtoLRSstream` quanto em
tempo de execucao, so pula espaco, tabulacao, CR e LF (`SkipWhitespace`, em
`rtl/objpas/classes/parser.inc`). Nao ha sintaxe de comentario em LFM, e `{`
abre bloco binario. Um comentario compilaria -- `{$R}` so embute bytes -- e
explodiria ao abrir a janela, que e a pior forma de falhar.

O espirito do requisito ("nunca sumir calado") fica, em tres lugares que um
humano le: um bloco de comentario **na unidade Pascal** ao lado do campo do
componente, a tabela completa em `wte/forms/conversao.md`, e a contagem no
stdout do gerador.

**4. `TStaticText`.** 37 instancias, e a secao 8.9 avisa que transparencia e
cor de fundo diferem no GTK2. O gerador nao resolve: marca as 37 no
`conversao.md`, com formulario, nome e as propriedades de fundo que cada uma
declara, que e a lista de conferencia da WTE-TASK-12.


A tabela de mapeamento
----------------------

`PROPRIEDADES` diz, para cada classe da LCL, quais propriedades sao aceitas e
quais sao descartadas. Ela **nao e palpite**: saiu das fontes da LCL 3.0
instaladas em `/usr/lib/lazarus/3.0/lcl`, varrendo as secoes `published` de
cada classe e de todos os ancestrais dela, cruzado com as propriedades que
ocorrem de fato nos 18 DFM. Propriedade que nao esteja em nenhuma das duas
listas **aborta**: e o caso "nao sei em que balde isto cai", diferente de "a
LCL nao tem", que e o balde `DESCARTA`.

`Left` e `Top` em componente nao visual (`TTimer`, `TActionList`, os dialogos)
nao aparecem em nenhuma secao `published`, e ainda assim sao validos: o
`TComponent.DefineProperties` da FCL os define sobre o `DesignInfo`. Estao em
`ACEITA` por isso, e o `.lfm` do proprio Lazarus os escreve assim.


Geometria absoluta
------------------

Nenhum `Anchors`, `Align` novo, `BorderSpacing` ou `ChildSizing` e
introduzido. Os 441 controles foram posicionados a mao em 2002 e a fidelidade e
o criterio -- secao 5 do plano, e a mesma decisao que o `newWe2002` tomou para
os 434 controles do `ed.rc`. O unico `Align` que aparece na saida e o
`Align = alClient` que ja estava no DFM.


Falha alta
----------

Classe sem mapeamento, propriedade fora das duas listas, valor com
identificador desconhecido, handler referenciado no DFM e ausente do TSV (ou o
contrario), blob referenciado e ausente no modo de escrita -- todos abortam com
formulario, componente e propriedade na mensagem. Nada e escrito no disco antes
de os 18 formularios converterem inteiros.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DFM_DIR = ROOT / "wte" / "re" / "dfm"
BLOBS_DIR = DFM_DIR / "blobs"
METHODS_TSV = ROOT / "wte" / "re" / "published_methods.tsv"
FORMS_OUT = ROOT / "wte" / "forms"
SRC_OUT = ROOT / "wte" / "src"

REL_DFM = "wte/re/dfm"
REL_FORMS = "wte/forms"
REL_SRC = "wte/src"
GENERATOR = "wte/tools/dfm2lfm.py"
EXTRACTOR = "wte/tools/dfm_extract.py"
RELATORIO = "conversao.md"

# Versao da LCL de onde a tabela de propriedades foi medida. Trocar de versao
# pede remedir -- nao e para editar a tabela a mao.
LCL_VERSAO = "3.0"


class Dfm2LfmError(Exception):
    """Erro de conversao, sempre com formulario e caminho do objeto."""


# ------------------------------------------------------- nome das unidades ---

# Recuperados dos exports de finalizacao do `.exe` (secao 1.3 do plano). Sao 13
# dos 18; servem de prova da regra aplicada aos outros 5.
UNIDADES_MEDIDAS = {
    "ficha_about": "ep2002_about",
    "ficha_creditos_equipo": "ep2002_creditos_equipo",
    "ficha_dorsal": "ep2002_dorsal",
    "ficha_enlaza": "ep2002_enlaza",
    "ficha_error2": "ep2002_error2",
    "ficha_info": "ep2002_info",
    "ficha_info2": "ep2002_info2",
    "ficha_info3": "ep2002_info3",
    "ficha_info4": "ep2002_info4",
    "ficha_movertodos": "ep2002_movertodos",
    "ficha_salida": "ep2002_salida",
    "ficha_warning": "ep2002_warning",
    "ficha_warning_2": "ep2002_warning_2",
}


def nome_da_unidade(formulario: str) -> str:
    """`ep2002_` + o nome do formulario sem o prefixo `ficha_`, em minusculas."""
    base = formulario[len("ficha_"):] if formulario.startswith("ficha_") \
        else formulario
    return "ep2002_" + base.lower()


# ------------------------------------------------------ mapeamento de tipo ---

# A unica classe sem par na LCL. Ver a excecao 2 no cabecalho.
SUBSTITUICOES = {"TBrowseURL": "TLabel"}

# Classe da LCL -> unidade que a declara.
UNIDADE_DA_CLASSE = {
    "TLabel": "StdCtrls",
    "TEdit": "StdCtrls",
    "TComboBox": "StdCtrls",
    "TListBox": "StdCtrls",
    "TGroupBox": "StdCtrls",
    "TRadioButton": "StdCtrls",
    "TStaticText": "StdCtrls",
    "TScrollBar": "StdCtrls",
    "TImage": "ExtCtrls",
    "TShape": "ExtCtrls",
    "TBevel": "ExtCtrls",
    "TTimer": "ExtCtrls",
    "TBitBtn": "Buttons",
    "TSpeedButton": "Buttons",
    "TUpDown": "ComCtrls",
    "TTrackBar": "ComCtrls",
    "TOpenDialog": "Dialogs",
    "TSaveDialog": "Dialogs",
    "TActionList": "ActnList",
}

# Unidade que hospeda o `REStub` dos 96 stubs. **Nao pode se chamar `restub`**:
# em Pascal identificador nao distingue maiusculas, entao o nome da unidade e o
# nome da rotina colidiriam e o FPC recusa a chamada crua --
#
#     user1.pas(6,28) Fatal: Syntax error, "." expected but "(" found
#
# porque resolve `REStub` como o nome da unidade e espera `.` depois. A
# WTE-TASK-11 planeja `wte/src/restub.pas`; o arquivo tem de ganhar outro nome,
# e este e o escolhido. A assinatura que o plano fixa
# (`procedure REStub(const Nome: string)`) fica como esta.
UNIDADE_RESTUB = "retrace"

# Ordem convencional do `uses` -- a mesma que a IDE do Lazarus escreve.
ORDEM_USES = ["Classes", "SysUtils", "Types", "Forms", "Controls", "Graphics",
              "StdCtrls", "ExtCtrls", "Buttons", "ComCtrls", "Dialogs",
              "ActnList"]

# Chave usada no lugar da classe do formulario raiz (`TMainForm`,
# `Tficha_about`, ...): todas descendem de `TForm` e compartilham a tabela.
FORM = "@form"

# ACEITA: propriedade que existe na LCL, emitida verbatim.
ACEITA = {
    FORM: {
        "AlphaBlend", "AlphaBlendValue", "BorderIcons", "BorderStyle",
        "Caption", "ClientHeight", "ClientWidth", "Color", "Font.Charset",
        "Font.Color", "Font.Height", "Font.Name", "Font.Style", "Height",
        "Icon.Data", "Left", "OnCreate", "OnShow", "PixelsPerInch", "Top",
        "Width",
    },
    "TActionList": {"Left", "Top"},
    "TBevel": {"Cursor", "Height", "Left", "Top", "Width"},
    "TBitBtn": {
        "Cancel", "Caption", "Cursor", "Default", "Glyph.Data", "Height",
        "Hint", "Layout", "Left", "ModalResult", "OnClick", "ParentShowHint",
        "ShowHint", "Spacing", "TabOrder", "Top", "Width",
    },
    "TComboBox": {
        "Color", "Enabled", "Font.Charset", "Font.Color", "Font.Height",
        "Font.Name", "Font.Pitch", "Font.Style", "Height", "ItemHeight",
        "Items.Strings", "Left", "OnChange", "OnDrawItem", "ParentFont",
        "Style", "TabOrder", "TabStop", "Text", "Top", "Width",
    },
    "TEdit": {
        "CharCase", "Color", "Enabled", "Height", "Left", "MaxLength",
        "OnKeyPress", "TabOrder", "Top", "Width",
    },
    "TGroupBox": {
        "Caption", "Color", "Font.Charset", "Font.Color", "Font.Height",
        "Font.Name", "Font.Style", "Height", "Left", "ParentColor",
        "ParentFont", "TabOrder", "Top", "Width",
    },
    "TImage": {
        "Align", "AutoSize", "Center", "Cursor", "DragCursor", "Height",
        "Hint", "Left", "OnClick", "OnMouseDown", "OnMouseMove",
        "ParentShowHint", "Picture.Data", "ShowHint", "Stretch", "Top",
        "Transparent", "Visible", "Width",
    },
    "TLabel": {
        "Alignment", "AutoSize", "Caption", "Color", "Cursor", "Enabled",
        "Font.Charset", "Font.Color", "Font.Height", "Font.Name", "Font.Style",
        "Height", "Hint", "Layout", "Left", "OnClick", "OnMouseDown",
        "ParentColor", "ParentFont", "ParentShowHint", "ShowHint", "Top",
        "Transparent", "Width",
    },
    "TListBox": {
        "Color", "Enabled", "Font.Charset", "Font.Color", "Font.Height",
        "Font.Name", "Font.Style", "Height", "ItemHeight", "Items.Strings",
        "Left", "OnClick", "ParentFont", "TabOrder", "Top", "Width",
    },
    "TOpenDialog": {"Filter", "Left", "Title", "Top"},
    "TRadioButton": {
        "Caption", "Checked", "Enabled", "Font.Charset", "Font.Color",
        "Font.Height", "Font.Name", "Font.Style", "Height", "Left", "OnClick",
        "ParentFont", "TabOrder", "TabStop", "Top", "Width",
    },
    "TSaveDialog": {"DefaultExt", "Filter", "Left", "Options", "Title", "Top"},
    "TScrollBar": {
        "Height", "Kind", "LargeChange", "Left", "Max", "Min", "OnChange",
        "OnScroll", "PageSize", "Position", "TabOrder", "Top", "Width",
    },
    "TShape": {
        "Brush.Color", "DragCursor", "Height", "Left", "OnDragDrop",
        "OnDragOver", "OnEndDrag", "OnMouseDown", "OnMouseMove", "Pen.Color",
        "Pen.Width", "Shape", "Top", "Visible", "Width",
    },
    "TSpeedButton": {
        "Action", "Caption", "Cursor", "Enabled", "Flat", "Font.Charset",
        "Font.Color", "Font.Height", "Font.Name", "Font.Style", "Glyph.Data",
        "Height", "Hint", "Layout", "Left", "Margin", "OnClick", "ParentFont",
        "ParentShowHint", "ShowHint", "Spacing", "Top", "Transparent",
        "Visible", "Width",
    },
    "TStaticText": {
        "Alignment", "AutoSize", "BorderStyle", "Caption", "Color", "Cursor",
        "Enabled", "Font.Charset", "Font.Color", "Font.Height", "Font.Name",
        "Font.Style", "Height", "Hint", "Left", "OnClick", "OnMouseDown",
        "ParentColor", "ParentFont", "ParentShowHint", "ShowHint", "TabOrder",
        "Top", "Width",
    },
    "TTimer": {"Enabled", "Interval", "Left", "OnTimer", "Top"},
    "TTrackBar": {
        "Enabled", "Frequency", "Height", "Hint", "Left", "Max", "Min",
        "OnChange", "Orientation", "ParentShowHint", "Position", "SelEnd",
        "SelStart", "ShowHint", "TabOrder", "TabStop", "TickMarks",
        "TickStyle", "Top", "Width",
    },
    "TUpDown": {
        "Height", "Left", "Max", "Min", "OnClick", "Orientation", "Position",
        "TabOrder", "Thousands", "Top", "Width", "Wrap",
    },
}

# DESCARTA: propriedade que a LCL nao tem, com o motivo que vai para o
# `conversao.md` e para o comentario na unidade.
_SEM_CTL3D = (
    "a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2 desenha a "
    "borda propria")
DESCARTA = {
    FORM: {
        "OldCreateOrder": (
            "propriedade de compatibilidade do Delphi 4; a LCL nao a tem e "
            "sempre usa a ordem nova de criacao"),
        "TextHeight": (
            "medida de tempo de projeto do Delphi, gravada para reescalar o "
            "formulario; a LCL nao a tem"),
    },
    "TComboBox": {"Ctl3D": _SEM_CTL3D, "ParentCtl3D": _SEM_CTL3D},
    "TListBox": {"Ctl3D": _SEM_CTL3D, "ParentCtl3D": _SEM_CTL3D},
    "TRadioButton": {"Ctl3D": _SEM_CTL3D, "ParentCtl3D": _SEM_CTL3D},
    "TScrollBar": {"Ctl3D": _SEM_CTL3D, "ParentCtl3D": _SEM_CTL3D},
    # Chegam aqui pela substituicao TBrowseURL -> TLabel.
    "TLabel": {
        "Category": (
            "categoria de TAction; some com a acao, porque TLabel nao e acao"),
        "URL": (
            "propriedade do TBrowseURL; o valor fica na constante <NOME>_URL "
            "da unidade e o comportamento vira OpenURL() no handler"),
    },
}

# Descarte que nao vem da tabela e sim do valor: a propriedade existe na LCL,
# mas o valor referencia um objeto que a substituicao mudou de tipo.
MOTIVO_ACAO_SUBSTITUIDA = (
    "a propriedade existe na LCL, mas o valor aponta para '{alvo}', que era "
    "TBrowseURL e virou TLabel; TLabel nao e TBasicAction e o leitor de LFM "
    "recusaria a atribuicao")

# Identificadores validos como valor de propriedade. Conferidos um a um contra
# as fontes da LCL 3.0 (`ColorToIdent`/`CursorToIdent`/`CharsetToIdent` em
# graphics.pp e controls.pp, e as declaracoes de enumerado). Identificador fora
# desta lista aborta -- e o sinal de que a LCL nao conhece o nome.
IDENTIFICADORES = {
    # booleanos
    "True", "False",
    # TColor
    "clActiveBorder", "clBlack", "clBlue", "clBtnFace", "clCream", "clFuchsia",
    "clGray", "clGreen", "clHighlightText", "clInactiveCaption", "clLime",
    "clMaroon", "clNavy", "clRed", "clSilver", "clTeal", "clWhite",
    "clWindowText",
    # TFontCharset
    "ANSI_CHARSET", "DEFAULT_CHARSET", "OEM_CHARSET",
    # TCursor
    "crDefault", "crHandPoint",
    # TAlignment / TTextLayout / TAlign
    "taCenter", "taRightJustify", "tlBottom", "tlCenter", "alClient",
    # TFormBorderStyle / TStaticBorderStyle
    "bsNone", "bsSingle", "sbsSingle", "sbsSunken",
    # TButtonLayout
    "blGlyphBottom", "blGlyphRight", "blGlyphTop",
    # TShapeType / TScrollBarKind / TUDOrientation / TTrackBarOrientation
    "stCircle", "sbVertical", "udHorizontal", "trHorizontal",
    # TTickStyle / TTickMark
    "tsNone", "tmBoth",
    # TComboBoxStyle / TEditCharCase / TFontPitch
    "csOwnerDrawFixed", "ecUpperCase", "fpFixed",
}

# Propriedades cujo valor e o **nome de outro objeto** do formulario, nao um
# identificador de valor. Nao passam pela conferencia de IDENTIFICADORES; sao
# conferidas contra os objetos que o DFM declara.
PROPS_REFERENCIA = {"Action"}

# Elementos validos dentro de `[...]`.
ELEMENTOS_DE_CONJUNTO = {
    "biMinimize", "biSystemMenu",        # TBorderIcon
    "fsBold", "fsUnderline",             # TFontStyle
    "ofHideReadOnly", "ofOverwritePrompt",  # TOpenOption
}

# ------------------------------------------------------------- assinaturas ---

# (classe da LCL, evento) -> forma da assinatura. Par que nao esteja aqui
# aborta: adivinhar assinatura da um `.pas` que nao compila, e o erro do
# compilador nao aponta para o gerador.
EVENTOS = {
    (FORM, "OnCreate"): "notify",
    (FORM, "OnShow"): "notify",
    ("TBitBtn", "OnClick"): "notify",
    ("TComboBox", "OnChange"): "notify",
    ("TComboBox", "OnDrawItem"): "drawitem",
    ("TEdit", "OnKeyPress"): "keypress",
    ("TImage", "OnClick"): "notify",
    ("TImage", "OnMouseDown"): "mouse",
    ("TImage", "OnMouseMove"): "mousemove",
    ("TLabel", "OnClick"): "notify",
    ("TLabel", "OnMouseDown"): "mouse",
    ("TListBox", "OnClick"): "notify",
    ("TRadioButton", "OnClick"): "notify",
    ("TScrollBar", "OnChange"): "notify",
    ("TScrollBar", "OnScroll"): "scroll",
    ("TShape", "OnDragDrop"): "dragdrop",
    ("TShape", "OnDragOver"): "dragover",
    ("TShape", "OnEndDrag"): "enddrag",
    ("TShape", "OnMouseDown"): "mouse",
    ("TShape", "OnMouseMove"): "mousemove",
    ("TSpeedButton", "OnClick"): "notify",
    ("TStaticText", "OnClick"): "notify",
    ("TStaticText", "OnMouseDown"): "mouse",
    ("TTimer", "OnTimer"): "notify",
    ("TTrackBar", "OnChange"): "notify",
    ("TUpDown", "OnClick"): "udclick",
}

# forma -> (lista de parametros, unidades que os tipos exigem no `uses`)
ASSINATURAS = {
    "notify": ("Sender: TObject", ()),
    "udclick": ("Sender: TObject; Button: TUDBtnType", ("ComCtrls",)),
    "keypress": ("Sender: TObject; var Key: char", ()),
    "mouse": ("Sender: TObject; Button: TMouseButton; Shift: TShiftState; "
              "X, Y: Integer", ("Classes", "Controls")),
    "mousemove": ("Sender: TObject; Shift: TShiftState; X, Y: Integer",
                  ("Classes",)),
    "scroll": ("Sender: TObject; ScrollCode: TScrollCode; "
               "var ScrollPos: Integer", ("StdCtrls",)),
    "dragdrop": ("Sender, Source: TObject; X, Y: Integer", ()),
    "dragover": ("Sender, Source: TObject; X, Y: Integer; State: TDragState; "
                 "var Accept: Boolean", ("Controls",)),
    "enddrag": ("Sender, Target: TObject; X, Y: Integer", ()),
    "drawitem": ("Control: TWinControl; Index: Integer; ARect: TRect; "
                 "State: TOwnerDrawState",
                 ("Types", "Controls", "StdCtrls")),
}

# Handler publicado que nenhum DFM referencia: o `Button2Click` do `MainForm`,
# registrado assim na WTE-TASK-04. Sem componente nao ha par (classe, evento),
# entao a assinatura vem daqui, explicitamente, em vez de sair de heuristica
# sobre o sufixo do nome.
SEM_COMPONENTE = {("MainForm", "Button2Click"): "notify"}


# ------------------------------------------------------------------ modelo ---


class Blob:
    """Referencia `{blob <arquivo> <tamanho> sha256:<hash>}` de um `.dfm`."""

    __slots__ = ("arquivo", "tamanho", "sha256")

    def __init__(self, arquivo: str, tamanho: int, sha256: str):
        self.arquivo = arquivo
        self.tamanho = tamanho
        self.sha256 = sha256


class Prop:
    __slots__ = ("nome", "linhas", "blob")

    def __init__(self, nome: str, linhas: list[str], blob: Blob | None):
        self.nome = nome
        self.linhas = linhas      # valor cru, ja sem `nome = `; 1+ linhas
        self.blob = blob

    @property
    def valor(self) -> str:
        return "\n".join(self.linhas)


class Obj:
    __slots__ = ("cls", "nome", "props", "filhos")

    def __init__(self, cls: str, nome: str):
        self.cls = cls
        self.nome = nome
        self.props: list[Prop] = []
        self.filhos: list[Obj] = []


class Descarte:
    __slots__ = ("formulario", "componente", "classe_dfm", "classe_lcl",
                 "propriedade", "valor", "motivo")

    def __init__(self, formulario, componente, classe_dfm, classe_lcl,
                 propriedade, valor, motivo):
        self.formulario = formulario
        self.componente = componente
        self.classe_dfm = classe_dfm
        self.classe_lcl = classe_lcl
        self.propriedade = propriedade
        self.valor = valor
        self.motivo = motivo


# ------------------------------------------------------------------ leitor ---

RE_OBJETO = re.compile(
    r"^(?P<pad> *)(?P<tipo>object|inherited|inline) "
    r"(?:(?P<nome>[A-Za-z_][A-Za-z_0-9]*): )?(?P<cls>[A-Za-z_][A-Za-z_0-9]*)"
    r"(?: \[(?P<pos>\d+)\])?$")
RE_PROP = re.compile(
    r"^(?P<pad> *)(?P<nome>[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)"
    r" = (?P<valor>.*)$")
RE_FIM = re.compile(r"^(?P<pad> *)end$")
RE_BLOB = re.compile(
    r"^\{blob (?P<arq>[^ ]+) (?P<tam>\d+) sha256:(?P<sha>[0-9a-f]{64})\}$")


def _erro(formulario: str, linha_no: int, trilha: list[str], msg: str):
    onde = " > ".join(trilha) or "(raiz)"
    return Dfm2LfmError(
        f"{REL_DFM}/{formulario}.dfm:{linha_no}: {onde}: {msg}")


def ler_dfm(formulario: str, texto: str) -> Obj:
    """Le o DFM textual do `dfm_extract.py`.

    A estrutura e conferida com rigor; o **valor** de cada propriedade e
    guardado como texto cru, porque o `dfm_extract.py` ja o emitiu na forma
    canonica e reescreve-lo daqui so criaria uma segunda chance de divergir.
    """
    linhas = texto.split("\n")
    if linhas and linhas[-1] == "":
        linhas.pop()

    raiz: Obj | None = None
    pilha: list[Obj] = []
    trilha: list[str] = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        numero = i + 1

        m = RE_OBJETO.match(linha)
        if m:
            if m.group("tipo") != "object":
                raise _erro(formulario, numero, trilha,
                            f"'{m.group('tipo')}' nao ocorre nos 18 "
                            f"formularios e a forma LFM dele nao foi decidida")
            if m.group("pos") is not None:
                raise _erro(formulario, numero, trilha,
                            "posicao explicita de filho ('[n]') nao ocorre "
                            "nos 18 formularios")
            obj = Obj(m.group("cls"), m.group("nome") or "")
            if raiz is None:
                if pilha:
                    raise _erro(formulario, numero, trilha, "estado impossivel")
                raiz = obj
            elif not pilha:
                raise _erro(formulario, numero, trilha,
                            "segundo objeto raiz no mesmo arquivo")
            else:
                pilha[-1].filhos.append(obj)
            pilha.append(obj)
            trilha.append(obj.nome or obj.cls)
            i += 1
            continue

        m = RE_FIM.match(linha)
        if m:
            if not pilha:
                raise _erro(formulario, numero, trilha, "'end' sem objeto")
            pilha.pop()
            trilha.pop()
            i += 1
            continue

        m = RE_PROP.match(linha)
        if m:
            if not pilha:
                raise _erro(formulario, numero, trilha,
                            "propriedade fora de objeto")
            nome = m.group("nome")
            valor = m.group("valor")
            corpo = [valor]
            if valor == "(":
                # Lista de strings (`Items.Strings`): consome ate o `)`.
                while True:
                    i += 1
                    if i >= len(linhas):
                        raise _erro(formulario, numero, trilha + [nome],
                                    "lista sem ')' de fechamento")
                    corpo.append(linhas[i])
                    if linhas[i].rstrip().endswith(")"):
                        break
            elif valor.startswith("(") or valor.startswith("<"):
                raise _erro(formulario, numero, trilha + [nome],
                            f"valor {valor[0]!r} em linha unica nao esperado")
            blob = None
            if valor.startswith("{"):
                mb = RE_BLOB.match(valor)
                if not mb:
                    raise _erro(formulario, numero, trilha + [nome],
                                f"'{{' que nao e referencia de blob: {valor!r}")
                blob = Blob(mb.group("arq"), int(mb.group("tam")),
                            mb.group("sha"))
            pilha[-1].props.append(Prop(nome, corpo, blob))
            i += 1
            continue

        raise _erro(formulario, numero, trilha,
                    f"linha que nao e objeto, propriedade nem 'end': {linha!r}")

    if pilha:
        raise _erro(formulario, len(linhas), trilha,
                    f"{len(pilha)} objeto(s) sem 'end'")
    if raiz is None:
        raise Dfm2LfmError(f"{REL_DFM}/{formulario}.dfm: arquivo vazio")
    return raiz


# ------------------------------------------------------------- validacoes ---


def valida_valor(formulario: str, trilha: list[str], prop: Prop,
                 objetos: set[str]) -> None:
    """Recusa identificador ou elemento de conjunto que a LCL nao conhece."""
    if prop.blob is not None:
        return
    if prop.nome.startswith("On"):
        return                      # nome de handler, conferido contra o TSV
    valor = prop.linhas[0]
    if prop.nome in PROPS_REFERENCIA:
        if valor not in objetos:
            raise Dfm2LfmError(
                f"{formulario}: {' > '.join(trilha)}.{prop.nome}: aponta para "
                f"'{valor}', que nao e objeto declarado neste formulario")
        return
    if valor.startswith("["):
        corpo = valor[1:-1].strip()
        if not corpo:
            return
        for elemento in (e.strip() for e in corpo.split(",")):
            if elemento not in ELEMENTOS_DE_CONJUNTO:
                raise Dfm2LfmError(
                    f"{formulario}: {' > '.join(trilha)}.{prop.nome}: "
                    f"elemento de conjunto desconhecido '{elemento}'. "
                    f"Se a LCL o tem, acrescente a ELEMENTOS_DE_CONJUNTO em "
                    f"{GENERATOR}.")
        return
    if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", valor):
        if valor not in IDENTIFICADORES:
            raise Dfm2LfmError(
                f"{formulario}: {' > '.join(trilha)}.{prop.nome}: "
                f"identificador desconhecido '{valor}'. Se a LCL o tem, "
                f"acrescente a IDENTIFICADORES em {GENERATOR}.")


def chave_da_classe(cls: str, e_raiz: bool) -> str:
    return FORM if e_raiz else SUBSTITUICOES.get(cls, cls)


def classe_lfm(cls: str, e_raiz: bool) -> str:
    """A classe que vai para o `.lfm`.

    A do formulario raiz e a propria (`TMainForm`, `Tficha_about`, ...): sao as
    classes do aplicativo, declaradas na unidade gerada. As dos componentes
    passam pela substituicao.
    """
    return cls if e_raiz else SUBSTITUICOES.get(cls, cls)


# ------------------------------------------------------------ escrita LFM ---

BYTES_POR_LINHA = 32

# Marca de "aqui vai um digito hexadecimal" no gabarito que o `--check` monta
# sem os blobs. Tem de ser um caractere **impossivel** na saida: `?` nao serve
# -- ha `Caption = 'Desejar calcular o preco dos jogadores???      '` em
# `ficha_creditos_equipo`, e o gabarito casaria com o texto do usuario.
SENTINELA = "\x00"


def _hex_layout(tamanho: int, pad: str) -> list[tuple[str, int]]:
    """Layout canonico do `ObjectBinaryToText`: (prefixo, digitos) por linha."""
    linhas = []
    resta = tamanho
    while resta > 0:
        n = min(BYTES_POR_LINHA, resta)
        resta -= n
        linhas.append((pad + "  ", n * 2))
    return linhas


def emite_lfm(raiz: Obj, formulario: str, blobs: dict[str, bytes] | None,
              descartes: list[Descarte], substituidos: set[str]) -> str:
    """Monta o texto do `.lfm`.

    `blobs` mapeia `<arquivo>.bin` -> bytes. Com `None`, cada digito
    hexadecimal sai como `SENTINELA`: e o modo que o `--check` usa, em que o
    layout e regenerado (so depende do tamanho, que esta no `.dfm`) e os
    digitos sao lidos do arquivo versionado e conferidos pelo SHA-256.
    """
    saida: list[str] = []
    objetos = {o.nome for o in _todos(raiz) if o.nome}

    def caminha(obj: Obj, nivel: int, e_raiz: bool, trilha: list[str]) -> None:
        pad = "  " * nivel
        cls_saida = classe_lfm(obj.cls, e_raiz)
        cabeca = f"{pad}object "
        if obj.nome:
            cabeca += f"{obj.nome}: "
        saida.append(cabeca + cls_saida + "\n")

        chave = chave_da_classe(obj.cls, e_raiz)
        aceita = ACEITA.get(chave)
        if aceita is None:
            raise Dfm2LfmError(
                f"{formulario}: {' > '.join(trilha)}: classe '{obj.cls}' sem "
                f"mapeamento para a LCL. Acrescente a ACEITA/UNIDADE_DA_CLASSE "
                f"em {GENERATOR}, ou a SUBSTITUICOES se ela nao tiver par.")
        descarta = DESCARTA.get(chave, {})

        pad_prop = "  " * (nivel + 1)
        for prop in obj.props:
            valida_valor(formulario, trilha, prop, objetos)

            motivo = None
            if prop.nome in descarta:
                motivo = descarta[prop.nome]
            elif prop.nome not in aceita:
                raise Dfm2LfmError(
                    f"{formulario}: {' > '.join(trilha)}.{prop.nome}: "
                    f"propriedade desconhecida em '{chave}'. Ela nao esta nem "
                    f"em ACEITA nem em DESCARTA -- decida em qual balde cai e "
                    f"acrescente em {GENERATOR}. Nao ha terceiro caminho: "
                    f"emitir sem saber daria um LFM que so falha ao abrir a "
                    f"janela.")
            elif prop.nome == "Action" and prop.valor in substituidos:
                motivo = MOTIVO_ACAO_SUBSTITUIDA.format(alvo=prop.valor)

            if motivo is not None:
                descartes.append(Descarte(
                    formulario, obj.nome or f"(sem nome): {obj.cls}", obj.cls,
                    cls_saida, prop.nome, prop.valor, motivo))
                continue

            if prop.blob is not None:
                saida.append(f"{pad_prop}{prop.nome} = {{\n")
                dados = None
                if blobs is not None:
                    dados = blobs[prop.blob.arquivo]
                pos = 0
                for prefixo, digitos in _hex_layout(prop.blob.tamanho,
                                                    pad_prop):
                    if dados is None:
                        corpo = SENTINELA * digitos
                    else:
                        corpo = dados[pos:pos + digitos // 2].hex().upper()
                    pos += digitos // 2
                    saida.append(prefixo + corpo + "\n")
                saida.append(f"{pad_prop}}}\n")
                continue

            saida.append(f"{pad_prop}{prop.nome} = {prop.linhas[0]}\n")
            for extra in prop.linhas[1:]:
                saida.append(extra + "\n")

        for filho in obj.filhos:
            caminha(filho, nivel + 1, False,
                    trilha + [filho.nome or filho.cls])
        saida.append(f"{pad}end\n")

    caminha(raiz, 0, True, [raiz.nome or raiz.cls])
    return "".join(saida)


def nomes_substituidos(raiz: Obj) -> set[str]:
    """Objetos cuja classe a substituicao trocou.

    Serve para achar `Action = <nome>` apontando para eles: a propriedade
    existe na LCL, o valor e que deixou de ser aceitavel.
    """
    return {o.nome for o in _todos(raiz)
            if o.nome and o.cls in SUBSTITUICOES}


# ------------------------------------------------------------ handlers TSV ---


def le_handlers() -> dict[str, list[tuple[str, list[str], str]]]:
    """`formulario` -> [(handler, componentes, evento)], na ordem do TSV."""
    if not METHODS_TSV.is_file():
        raise Dfm2LfmError(f"{METHODS_TSV.relative_to(ROOT)} nao existe")
    linhas = METHODS_TSV.read_text(encoding="utf-8").splitlines()
    cabecalho = linhas[0].split("\t")
    esperado = ["endereco", "handler", "formulario", "componente", "evento"]
    if cabecalho[:5] != esperado:
        raise Dfm2LfmError(
            f"{METHODS_TSV.relative_to(ROOT)}: cabecalho inesperado "
            f"{cabecalho[:5]}, esperado {esperado}")

    por_formulario: dict[str, list[tuple[str, list[str], str]]] = {}
    vistos: set[tuple[str, str]] = set()
    for numero, linha in enumerate(linhas[1:], 2):
        if not linha.strip():
            continue
        campos = linha.split("\t")
        handler, formulario = campos[1], campos[2]
        componentes = [c for c in campos[3].split("|") if c]
        eventos = [e for e in campos[4].split("|") if e]
        if len(set(eventos)) > 1:
            raise Dfm2LfmError(
                f"published_methods.tsv:{numero}: o handler '{handler}' "
                f"atende eventos diferentes ({sorted(set(eventos))}); a "
                f"assinatura unica nao serviria para todos")
        if componentes and len(componentes) != len(eventos):
            raise Dfm2LfmError(
                f"published_methods.tsv:{numero}: {len(componentes)} "
                f"componentes para {len(eventos)} eventos")
        chave = (formulario, handler)
        if chave in vistos:
            raise Dfm2LfmError(
                f"published_methods.tsv:{numero}: '{handler}' repetido em "
                f"'{formulario}' -- as duas linhas dariam o mesmo metodo")
        vistos.add(chave)
        por_formulario.setdefault(formulario, []).append(
            (handler, componentes, eventos[0] if eventos else ""))
    return por_formulario


def classes_dos_componentes(raiz: Obj) -> dict[str, str]:
    """Nome do componente -> classe da LCL (raiz inclusa, como FORM)."""
    mapa = {raiz.nome: FORM}

    def caminha(obj: Obj) -> None:
        for filho in obj.filhos:
            if filho.nome:
                mapa[filho.nome] = SUBSTITUICOES.get(filho.cls, filho.cls)
            caminha(filho)

    caminha(raiz)
    return mapa


def handlers_do_dfm(raiz: Obj) -> dict[str, list[tuple[str, str]]]:
    """Nome do handler -> [(componente, evento)] que o DFM liga a ele."""
    achados: dict[str, list[tuple[str, str]]] = {}

    def caminha(obj: Obj, e_raiz: bool) -> None:
        for prop in obj.props:
            if prop.nome.startswith("On"):
                dono = obj.nome or f"(sem nome): {obj.cls}"
                achados.setdefault(prop.linhas[0], []).append(
                    (dono, prop.nome))
        for filho in obj.filhos:
            caminha(filho, False)

    caminha(raiz, True)
    return achados


# --------------------------------------------------------- escrita da unit ---

CABECALHO_UNIT = """\
{{ Esqueleto gerado por `{gerador}` (WTE-TASK-10).

  Formulario `{formulario}`, classe `{classe}`.
  Origem: `{rel_dfm}/{formulario}.dfm`.
  {n_comp} componentes, {n_handlers} handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 {gerador} --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `{restub}.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}}
unit {unidade};

{{$mode objfpc}}{{$H+}}

interface

uses
{uses};

type
"""


def emite_unit(formulario: str, unidade: str, raiz: Obj,
               handlers: list[tuple[str, str, str]],
               descartes: list[Descarte],
               urls: list[tuple[str, str]]) -> str:
    """Monta o texto do `.pas`.

    `handlers` e [(nome, forma, comentario)] ja resolvido; `descartes` sao os
    desta unidade; `urls` sao os `TBrowseURL` substituidos.
    """
    classe = raiz.cls

    # Campos dos componentes, em ordem de DFM. O componente sem nome (ha um,
    # um TStaticText no MainForm) nao vira campo: o DFM nao lhe deu nome, e
    # inventar um seria inventar identificador que o original nao tem.
    campos: list[tuple[str, str]] = []
    classes_usadas: set[str] = set()

    def caminha(obj: Obj) -> None:
        for filho in obj.filhos:
            cls = SUBSTITUICOES.get(filho.cls, filho.cls)
            classes_usadas.add(cls)
            if filho.nome:
                campos.append((filho.nome, cls))
            caminha(filho)

    caminha(raiz)

    # `uses`: so o que os tipos declarados aqui exigem. Unidade a mais vira
    # hint 5023 do FPC, e a WTE-TASK-11 pede compilacao sem ruido novo.
    precisa = {"Forms"}
    for cls in classes_usadas:
        unidade_cls = UNIDADE_DA_CLASSE.get(cls)
        if unidade_cls is None:
            raise Dfm2LfmError(
                f"{formulario}: classe '{cls}' sem unidade LCL conhecida; "
                f"acrescente a UNIDADE_DA_CLASSE em {GENERATOR}")
        precisa.add(unidade_cls)
    for _nome, forma, _c in handlers:
        precisa.update(ASSINATURAS[forma][1])
    lista_uses = [u for u in ORDEM_USES if u in precisa]
    faltando = precisa - set(ORDEM_USES)
    if faltando:
        raise Dfm2LfmError(
            f"{formulario}: unidade(s) {sorted(faltando)} fora de ORDEM_USES "
            f"em {GENERATOR}")
    # `ficha_error2` nao tem handler nenhum, e ali o `uses` do REStub sairia
    # como hint 5023 ("unit not used").
    if handlers:
        lista_uses.append(UNIDADE_RESTUB)

    linhas_uses = []
    atual = " "
    for i, u in enumerate(lista_uses):
        peca = u + ("," if i < len(lista_uses) - 1 else "")
        if len(atual) + 1 + len(peca) > 78:
            linhas_uses.append(atual)
            atual = " "
        atual += " " + peca
    linhas_uses.append(atual)

    out = [CABECALHO_UNIT.format(
        unidade=unidade, gerador=GENERATOR, formulario=formulario,
        classe=classe, rel_dfm=REL_DFM, n_comp=len(campos) + _sem_nome(raiz),
        n_handlers=len(handlers), uses="\n".join(linhas_uses),
        restub=UNIDADE_RESTUB)]

    out.append(f"  {classe} = class(TForm)\n")

    # Comentario de substituicao / descarte, colado no objeto a que pertence.
    # O do proprio formulario vem primeiro, logo abaixo da linha da classe;
    # o resto acompanha o campo do componente.
    por_componente: dict[str, list[Descarte]] = {}
    for d in descartes:
        por_componente.setdefault(d.componente, []).append(d)
    urls_por_nome = dict(urls)

    out.extend(_bloco_comentario("    ", por_componente.get(raiz.nome)))

    for nome, cls in campos:
        todo = ""
        if nome in urls_por_nome:
            todo = (
                f"TODO WTE-TASK-10: '{nome}' era TBrowseURL -- a acao padrao "
                f"da VCL (unidade Extactns), medida na WTE-TASK-07. A LCL nao "
                f"a tem, e virou {cls}. O comportamento original abria a URL "
                f"da constante {nome.upper()}_URL no navegador: reimplementar "
                f"com OpenURL() de LCLIntf no handler que dispara.")
        out.extend(_bloco_comentario("    ", por_componente.get(nome), todo))
        out.append(f"    {nome}: {cls};\n")

    for nome, forma, comentario in handlers:
        if comentario:
            for linha in _quebra(comentario, 78, "    "):
                out.append(linha + "\n")
        params, _dep = ASSINATURAS[forma]
        out.append(_assinatura(f"procedure {nome}", params, "    "))

    out.append("  private\n\n  public\n\n  end;\n\n")

    if urls:
        out.append("const\n")
        for nome, url in urls:
            out.append(
                f"  {{ URL do TBrowseURL '{nome}', descartada do .lfm porque\n"
                f"    TLabel nao tem a propriedade. Guardada aqui para que o\n"
                f"    valor nao se perca -- ver {REL_FORMS}/{RELATORIO}. }}\n")
            out.append(f"  {nome.upper()}_URL = {url};\n")
        out.append("\n")

    out.append("var\n")
    out.append(f"  {raiz.nome}: {classe};\n\n")
    out.append("implementation\n\n")
    # `{$R *.lfm}` procura o arquivo no diretorio do `.pas`, e so ali -- nem o
    # include path resolve. Com `src/` e `forms/` separados, o caminho tem de
    # ser explicito. Armadilha ja paga na WTE-TASK-02; ver wte/README.md.
    out.append(f"{{$R ../forms/{unidade}.lfm}}\n\n")

    if handlers:
        # 5024 e o hint "Parameter <x> not used". Stub que so registra o nome
        # ignora os parametros por definicao, e sem isto os 96 rendem mais de
        # 200 hints que afogam os de verdade. O escopo e so o bloco de stubs
        # gerado -- quando a fase 4 escrever os corpos, o {$PUSH}/{$POP} sai
        # junto com eles.
        out.append("{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros\n\n")
        for nome, forma, _c in handlers:
            params, _dep = ASSINATURAS[forma]
            out.append(_assinatura(f"procedure {classe}.{nome}", params, ""))
            out.append("begin\n")
            out.append(f"  REStub('{raiz.nome}.{nome}');\n")
            out.append("end;\n\n")
        out.append("{$POP}\n\n")

    out.append("end.\n")
    return "".join(out)


def _sem_nome(raiz: Obj) -> int:
    total = 0

    def caminha(obj: Obj) -> None:
        nonlocal total
        for filho in obj.filhos:
            if not filho.nome:
                total += 1
            caminha(filho)

    caminha(raiz)
    return total


def _assinatura(cabeca: str, params: str, indent: str) -> str:
    """`cabeca(params);`, quebrado nos `;` da lista quando passa de 79 colunas.

    `dorsalMouseDown` sozinho tem 103 colunas; sem isto os stubs de mouse e de
    drag ficariam fora do limite que o resto do repositorio respeita.
    """
    inteira = f"{indent}{cabeca}({params});"
    if len(inteira) <= 79:
        return inteira + "\n"
    partes = [p.strip() for p in params.split(";")]
    pecas = [p + "; " for p in partes[:-1]] + [partes[-1] + ");"]
    linhas: list[str] = []
    atual = f"{indent}{cabeca}("
    for peca in pecas:
        if not atual.endswith("(") and len(atual + peca.rstrip()) > 79:
            linhas.append(atual.rstrip())
            atual = indent + "  "
        atual += peca
    linhas.append(atual.rstrip())
    return "\n".join(linhas) + "\n"


def _quebra(texto: str, largura: int, prefixo: str) -> list[str]:
    linhas, atual = [], prefixo
    for palavra in texto.split():
        if len(atual) + 1 + len(palavra) > largura and atual != prefixo:
            linhas.append(atual)
            atual = prefixo
        atual += (" " if atual != prefixo else "") + palavra
    linhas.append(atual)
    return linhas


def _bloco_comentario(indent: str, ds: list[Descarte] | None,
                      todo: str = "") -> list[str]:
    """Comentario Pascal com o `TODO` e os descartes de um objeto.

    O **valor** descartado sai numa linha propria, sem reformatacao: ele e o
    dado a preservar, e quebra-lo em palavras comeria o espaco significativo
    (a URL do `TBrowseURL` termina em nove espacos, por exemplo).
    """
    if not ds and not todo:
        return []
    dentro = indent + "  "
    saida = [indent + "{\n"]
    primeiro = True
    if todo:
        for linha in _quebra(todo, 78, dentro):
            saida.append(linha + "\n")
        primeiro = False
    for d in ds or []:
        if not primeiro:
            saida.append("\n")
        primeiro = False
        saida.append(f"{dentro}Descartado: {d.propriedade} = {d.valor}\n")
        for linha in _quebra("Motivo: " + d.motivo + ".", 78, dentro):
            saida.append(linha + "\n")
    saida.append(indent + "}\n")
    return saida


# ---------------------------------------------------------------- relatorio ---

# Propriedades que decidem fundo e transparencia de um TStaticText, que e o
# que a secao 8.9 manda conferir no GTK2.
PROPS_FUNDO = ("Color", "ParentColor", "Transparent", "BorderStyle")


def emite_relatorio(formularios: list[dict]) -> str:
    total_desc = sum(len(f["descartes"]) for f in formularios)
    total_blobs = sum(f["n_blobs"] for f in formularios)
    total_bytes = sum(f["bytes_blobs"] for f in formularios)
    total_comp = sum(f["n_componentes"] for f in formularios)
    estaticos = [(f["formulario"], nome, marca)
                 for f in formularios for nome, marca in f["staticos"]]

    L: list[str] = []
    L.append("# `forms/conversao.md` -- o que a conversao DFM -> LFM mexeu\n")
    L.append(
        f"Gerado por [`../tools/dfm2lfm.py`](../tools/dfm2lfm.py) a partir de\n"
        f"[`../re/dfm/`](../re/dfm/). **Nao editar a mao** -- correcao entra no\n"
        f"script e o arquivo e regerado:\n")
    L.append("```sh")
    L.append(f"python3 {GENERATOR}")
    L.append(f"python3 {GENERATOR} --check   # o que `make -C wte check` roda")
    L.append("```\n")
    L.append(
        "Este arquivo e o insumo da **WTE-TASK-12**: tudo que a LCL nao "
        "reproduz\nliteralmente esta aqui, com o valor original, para a "
        "conferencia visual saber\nonde olhar.\n")

    L.append("## Os 18 formularios\n")
    L.append(
        "O `.lfm` e o `.pas` levam o nome da **unidade**, nao o do "
        "formulario. Os 13\nnomes de unidade marcados com * saem dos exports "
        "de finalizacao do `.exe`\n(secao 1.3 do plano); os outros 5 seguem a "
        "mesma regra, sem medida direta.\n")
    L.append("| DFM | Unidade | Classe | Componentes | Blobs | Descartes | "
             "`TStaticText` |")
    L.append("|---|---|---|---:|---:|---:|---:|")
    for f in formularios:
        marca = "*" if f["formulario"] in UNIDADES_MEDIDAS else ""
        L.append(
            f"| `{f['formulario']}.dfm` | `{f['unidade']}`{marca} | "
            f"`{f['classe']}` | {f['n_componentes']} | {f['n_blobs']} | "
            f"{len(f['descartes'])} | {len(f['staticos'])} |")
    L.append(f"| **total** | | | **{total_comp}** | **{total_blobs}** | "
             f"**{total_desc}** | **{len(estaticos)}** |")
    L.append("")

    L.append("## Substituicao de classe: `TBrowseURL` -> `TLabel`\n")
    L.append(
        "Duas instancias, as duas chamadas `lanza_url`, as duas dentro de "
        "um\n`TActionList`. A WTE-TASK-07 mediu que **nao e componente de "
        "terceiro**: e a\nacao padrao da VCL (unidade `Extactns`). A LCL nao "
        "tem par, entao vira\n`TLabel` -- e um `TLabel` dentro de um "
        "`TActionList` fica sem pai\n(`TControl.SetParentComponent` so aceita "
        "`TWinControl`) e nao aparece na\ntela, que e exatamente o que a acao "
        "fazia: nao aparecia.\n")
    L.append(
        "O comportamento -- abrir a URL no navegador -- e da **WTE-TASK-11**, "
        "com\n`OpenURL()` de `LCLIntf` no handler que dispara. O `TODO` esta "
        "na unidade, ao\nlado do campo, e a URL virou constante para nao se "
        "perder.\n")
    L.append("| Formulario | Objeto | Unidade | Constante | URL |")
    L.append("|---|---|---|---|---|")
    for f in formularios:
        for nome, url in f["urls"]:
            L.append(f"| `{f['formulario']}` | `{nome}` | `{f['unidade']}` | "
                     f"`{nome.upper()}_URL` | `{url}` |")
    L.append("")

    L.append("## Propriedades descartadas\n")
    L.append(
        "A tarefa pedia comentario dentro do `.lfm`. **Nao da**: o `TParser` "
        "da FCL --\nque e quem le LFM, tanto no `LFMtoLRSstream` quanto em "
        "tempo de execucao -- so\npula espaco, tabulacao, CR e LF; nao ha "
        "sintaxe de comentario em LFM, e `{`\nabre bloco binario. Um "
        "comentario compilaria (o `{$R}` so embute bytes) e\nexplodiria ao "
        "abrir a janela.\n")
    L.append(
        "O valor original fica aqui e num comentario **na unidade Pascal**, "
        "ao lado do\ncampo do componente.\n")
    L.append(f"Sao {total_desc} descartes.\n")
    L.append("| Formulario | Componente | Classe | Propriedade | Valor |")
    L.append("|---|---|---|---|---|")
    for f in formularios:
        for d in f["descartes"]:
            L.append(f"| `{f['formulario']}` | `{d.componente}` | "
                     f"`{d.classe_lcl}` | `{d.propriedade}` | "
                     f"`{d.valor.replace('|', '\\|')}` |")
    L.append("")
    L.append("### Por que cada uma cai\n")
    motivos: dict[str, tuple[str, int]] = {}
    for f in formularios:
        for d in f["descartes"]:
            chave = d.propriedade
            texto, qtd = motivos.get(chave, (d.motivo, 0))
            motivos[chave] = (texto, qtd + 1)
    L.append("| Propriedade | Qtd | Motivo |")
    L.append("|---|---:|---|")
    for prop in sorted(motivos):
        texto, qtd = motivos[prop]
        L.append(f"| `{prop}` | {qtd} | {texto} |")
    L.append("")

    L.append("## Os 118 blobs binarios\n")
    L.append(
        f"{total_blobs} propriedades `vaBinary` ({total_bytes} bytes) saem "
        f"do `.dfm` como\nreferencia `{{blob <arquivo> <tamanho> "
        f"sha256:<hash>}}` e entram no `.lfm` como\nhex inline, no formato "
        f"canonico do `ObjectBinaryToText`: 32 bytes por linha,\nem "
        f"maiusculas.\n")
    L.append(
        "Os bytes vivem em `wte/re/dfm/blobs/`, que e **gitignored** (secao 2 "
        "do plano):\nsem eles o modo de escrita **aborta**. O `--check` nao "
        "precisa deles -- ele\nconfere o hex do `.lfm` versionado contra o "
        "SHA-256 que esta no `.dfm`.\n")
    L.append("| Formulario | Blobs | Bytes |")
    L.append("|---|---:|---:|")
    for f in formularios:
        if f["n_blobs"]:
            L.append(f"| `{f['formulario']}` | {f['n_blobs']} | "
                     f"{f['bytes_blobs']} |")
    L.append(f"| **total** | **{total_blobs}** | **{total_bytes}** |")
    L.append("")

    L.append("## As instancias de `TStaticText`\n")
    L.append(
        "A secao 8.9 do plano manda conferir estas **na fase 2, nao na 6**: "
        "\n`TStaticText` existe na LCL, mas transparencia e cor de fundo se "
        "comportam\ndiferente no GTK2 do que no Win32. O gerador nao resolve "
        "isso -- so marca.\n")
    L.append(
        f"Sao {len(estaticos)} instancias. A coluna **Fundo** traz as "
        f"propriedades que\ndecidem o desenho do fundo\n"
        f"({', '.join('`%s`' % p for p in PROPS_FUNDO)});\nlinha vazia ali e "
        f"o caso que mais tende a divergir, porque tudo fica no\npadrao de "
        f"cada widgetset.\n")
    L.append("| Formulario | Componente | Fundo |")
    L.append("|---|---|---|")
    for formulario, nome, marca in estaticos:
        L.append(f"| `{formulario}` | `{nome}` | {marca or '_(nada)_'} |")
    L.append("")
    return "\n".join(L)


# ----------------------------------------------------------------- driver ---


def converte() -> tuple[dict[str, str], list[dict]]:
    """Le tudo, converte tudo em memoria. Nada e escrito aqui.

    Devolve (arquivos, formularios), em que `arquivos` mapeia caminho relativo
    a raiz do repositorio -> texto. O `.lfm` sai com `SENTINELA` no lugar dos
    digitos hexadecimais: e o gabarito do `--check`. Quem quer o hex de verdade
    chama `com_blobs()`, que e o que o modo de escrita faz.
    """
    dfms = sorted(DFM_DIR.glob("*.dfm"))
    if len(dfms) != 18:
        raise Dfm2LfmError(
            f"{REL_DFM}: esperados 18 arquivos .dfm, achados {len(dfms)}. "
            f"Rode `python3 {EXTRACTOR}`.")

    # A regra de nome so vale enquanto reproduzir os 13 nomes medidos.
    for formulario, esperado in sorted(UNIDADES_MEDIDAS.items()):
        obtido = nome_da_unidade(formulario)
        if obtido != esperado:
            raise Dfm2LfmError(
                f"a regra de nome de unidade deu '{obtido}' para "
                f"'{formulario}', e o `.exe` exporta '{esperado}'. A "
                f"extrapolacao para os 5 formularios sem nome medido nao vale "
                f"mais -- veja UNIDADES_MEDIDAS em {GENERATOR}.")

    handlers_tsv = le_handlers()

    arvores: list[tuple[str, Obj]] = []
    for caminho in dfms:
        formulario = caminho.stem
        raiz = ler_dfm(formulario, caminho.read_text(encoding="ascii"))
        if raiz.nome != formulario:
            raise Dfm2LfmError(
                f"{REL_DFM}/{caminho.name}: o objeto raiz se chama "
                f"'{raiz.nome}' e o arquivo '{formulario}'")
        arvores.append((formulario, raiz))

    arquivos: dict[str, str] = {}
    formularios: list[dict] = []
    unidades: dict[str, str] = {}

    for formulario, raiz in arvores:
        unidade = nome_da_unidade(formulario)
        if unidade in unidades:
            raise Dfm2LfmError(
                f"'{formulario}' e '{unidades[unidade]}' dao a mesma unidade "
                f"'{unidade}'")
        unidades[unidade] = formulario

        descartes: list[Descarte] = []
        texto_lfm = emite_lfm(raiz, formulario, None, descartes,
                              nomes_substituidos(raiz))

        # Blobs deste formulario, na ordem em que aparecem.
        blobs: list[Blob] = []

        def colhe(obj: Obj) -> None:
            for prop in obj.props:
                if prop.blob is not None:
                    blobs.append(prop.blob)
            for filho in obj.filhos:
                colhe(filho)

        colhe(raiz)

        # Handlers: o DFM e o TSV tem de concordar nos dois sentidos.
        do_dfm = handlers_do_dfm(raiz)
        do_tsv = handlers_tsv.get(formulario, [])
        nomes_tsv = {h for h, _c, _e in do_tsv}
        for nome in sorted(do_dfm):
            if nome not in nomes_tsv:
                raise Dfm2LfmError(
                    f"{formulario}: o DFM liga o evento ao handler '{nome}', "
                    f"que nao esta em published_methods.tsv. O TSV e o dono da "
                    f"lista de metodos publicados -- corrija a WTE-TASK-04.")
        classes = classes_dos_componentes(raiz)

        resolvidos: list[tuple[str, str, str]] = []
        urls: list[tuple[str, str]] = []
        for nome, componentes, evento in do_tsv:
            if not componentes:
                forma = SEM_COMPONENTE.get((formulario, nome))
                if forma is None:
                    raise Dfm2LfmError(
                        f"{formulario}: '{nome}' nao tem componente no TSV e "
                        f"nao esta em SEM_COMPONENTE; sem os dois nao ha como "
                        f"saber a assinatura. Acrescente em {GENERATOR}.")
                resolvidos.append((nome, forma, _nota_sem_dfm(nome)))
                continue
            formas = set()
            for componente in componentes:
                cls = classes.get(componente)
                if cls is None:
                    raise Dfm2LfmError(
                        f"{formulario}: o TSV liga '{nome}' ao componente "
                        f"'{componente}', que nao existe no DFM")
                forma = EVENTOS.get((cls, evento))
                if forma is None:
                    raise Dfm2LfmError(
                        f"{formulario}: par sem assinatura conhecida "
                        f"({cls}, {evento}), em '{componente}'. Acrescente a "
                        f"EVENTOS em {GENERATOR} -- adivinhar a assinatura da "
                        f"um .pas que nao compila.")
                formas.add(forma)
            if len(formas) > 1:
                raise Dfm2LfmError(
                    f"{formulario}: '{nome}' atende componentes de "
                    f"assinaturas diferentes ({sorted(formas)})")
            resolvidos.append((nome, formas.pop(), ""))

        for obj in _todos(raiz):
            if obj.cls in SUBSTITUICOES and obj.nome:
                for prop in obj.props:
                    if prop.nome == "URL":
                        urls.append((obj.nome, prop.valor))

        texto_pas = emite_unit(formulario, unidade, raiz, resolvidos,
                               descartes, urls)

        arquivos[f"{REL_FORMS}/{unidade}.lfm"] = texto_lfm
        arquivos[f"{REL_SRC}/{unidade}.pas"] = texto_pas

        staticos = []
        for obj in _todos(raiz):
            if SUBSTITUICOES.get(obj.cls, obj.cls) != "TStaticText":
                continue
            declaradas = [f"`{p.nome} = {p.valor}`" for p in obj.props
                          if p.nome in PROPS_FUNDO]
            staticos.append((obj.nome or f"(sem nome, {obj.cls})",
                             ", ".join(declaradas)))

        formularios.append({
            "formulario": formulario,
            "unidade": unidade,
            "raiz": raiz,
            "classe": raiz.cls,
            "n_componentes": sum(1 for _ in _todos(raiz)) - 1,
            "n_blobs": len(blobs),
            "bytes_blobs": sum(b.tamanho for b in blobs),
            "blobs": blobs,
            "descartes": descartes,
            "urls": urls,
            "staticos": staticos,
            "n_handlers": len(resolvidos),
        })

    arquivos[f"{REL_FORMS}/{RELATORIO}"] = emite_relatorio(formularios)
    return arquivos, formularios


def _nota_sem_dfm(nome: str) -> str:
    del nome                 # o nome ja esta na linha logo abaixo
    return "{ Metodo publicado sem ligacao em DFM nenhum (WTE-TASK-04). }"


def _todos(raiz: Obj):
    yield raiz
    for filho in raiz.filhos:
        yield from _todos(filho)


def carrega_blobs(formularios: list[dict]) -> dict[str, dict[str, bytes]]:
    """Le os `.bin` e confere tamanho e SHA-256 contra a referencia do `.dfm`.

    Usado so no modo de escrita. Blob ausente aborta: emitir um `.lfm` sem a
    imagem seria emitir formulario parcial.
    """
    faltando: list[str] = []
    por_formulario: dict[str, dict[str, bytes]] = {}
    for f in formularios:
        mapa: dict[str, bytes] = {}
        for blob in f["blobs"]:
            caminho = BLOBS_DIR / f["formulario"] / blob.arquivo
            if not caminho.is_file():
                faltando.append(f"{f['formulario']}/{blob.arquivo}")
                continue
            dados = caminho.read_bytes()
            if len(dados) != blob.tamanho:
                raise Dfm2LfmError(
                    f"blobs/{f['formulario']}/{blob.arquivo}: {len(dados)} "
                    f"bytes no disco contra {blob.tamanho} no .dfm")
            sha = hashlib.sha256(dados).hexdigest()
            if sha != blob.sha256:
                raise Dfm2LfmError(
                    f"blobs/{f['formulario']}/{blob.arquivo}: SHA-256 "
                    f"{sha[:16]}... no disco contra {blob.sha256[:16]}... no "
                    f".dfm")
            mapa[blob.arquivo] = dados
        por_formulario[f["formulario"]] = mapa
    if faltando:
        raise Dfm2LfmError(
            f"{len(faltando)} blob(s) referenciados pelos .dfm nao estao em "
            f"{REL_DFM}/blobs/,\n"
            f"       a comecar por {faltando[0]}.\n"
            f"       Essa pasta e gitignored e renasce do .exe: rode\n"
            f"       `python3 {EXTRACTOR}` uma vez antes.")
    return por_formulario


def com_blobs(arquivos: dict[str, str], formularios: list[dict],
              blobs: dict[str, dict[str, bytes]]) -> dict[str, str]:
    """Refaz os `.lfm` com o hex de verdade no lugar dos `SENTINELA`."""
    saida = dict(arquivos)
    for f in formularios:
        raiz = f["raiz"]
        descartes: list[Descarte] = []
        saida[f"{REL_FORMS}/{f['unidade']}.lfm"] = emite_lfm(
            raiz, f["formulario"], blobs[f["formulario"]], descartes,
            nomes_substituidos(raiz))
    return saida


def confere_hex(caminho_rel: str, esperado: str, no_disco: str) -> list[str]:
    """Compara um `.lfm` com o gabarito, deixando os digitos hex em aberto.

    `esperado` traz `SENTINELA` em cada posicao de digito hexadecimal: o
    *layout* do bloco binario so depende do tamanho, e o tamanho esta no `.dfm`
    versionado. Fora dessas posicoes a igualdade e exata; nelas basta ser
    digito hexadecimal maiusculo. Quem confere o **valor** e o SHA-256, tambem
    do `.dfm` -- e por isso que nada aqui le `wte/re/dfm/blobs/`.
    """
    problemas: list[str] = []
    if len(esperado) != len(no_disco):
        problemas.append(
            f"{caminho_rel}: {len(no_disco)} bytes no disco contra "
            f"{len(esperado)} regerados")
        return problemas
    linha = 1
    for e, d in zip(esperado, no_disco):
        if e == SENTINELA:
            if d not in "0123456789ABCDEF":
                problemas.append(
                    f"{caminho_rel}: linha {linha}: {d!r} nao e digito "
                    f"hexadecimal maiusculo dentro de um bloco binario")
                return problemas
        elif e != d:
            problemas.append(f"{caminho_rel}: linha {linha} diverge")
            return problemas
        if e == "\n":
            linha += 1
    return problemas


def extrai_blobs_do_lfm(esperado: str, no_disco: str,
                        blobs: list[Blob]) -> tuple[list[bytes], int]:
    """Os bytes de cada blob, lidos das posicoes de `SENTINELA` do gabarito.

    Devolve tambem quantos digitos sobraram: a ordem dos blobs no gabarito e a
    mesma da lista (as duas sao a mesma travessia em pre-ordem), entao sobra
    diferente de zero significa que os dois lados discordam sobre o numero de
    blocos, e nao que um blob especifico esta errado.
    """
    digitos = [d for e, d in zip(esperado, no_disco) if e == SENTINELA]
    saida: list[bytes] = []
    pos = 0
    for blob in blobs:
        n = blob.tamanho * 2
        saida.append(bytes.fromhex("".join(digitos[pos:pos + n])))
        pos += n
    return saida, len(digitos) - pos


def do_check(arquivos: dict[str, str], formularios: list[dict]) -> int:
    problemas: list[str] = []

    for rel, esperado in sorted(arquivos.items()):
        caminho = ROOT / rel
        if not caminho.is_file():
            problemas.append(f"{rel}: nao existe")
            continue
        no_disco = caminho.read_text(encoding="ascii")
        problemas.extend(confere_hex(rel, esperado, no_disco))

    # Blobs: sem tocar em `blobs/`. O gabarito diz onde estao os digitos, o
    # `.lfm` versionado diz quais sao, e o `.dfm` versionado diz o que deveriam
    # somar. Fecha o circuito sem nada gitignored no caminho.
    for f in formularios:
        rel = f"{REL_FORMS}/{f['unidade']}.lfm"
        caminho = ROOT / rel
        if not caminho.is_file() or any(p.startswith(rel) for p in problemas):
            continue
        achados, sobra = extrai_blobs_do_lfm(
            arquivos[rel], caminho.read_text(encoding="ascii"), f["blobs"])
        if sobra:
            problemas.append(
                f"{rel}: {sobra} digito(s) hexadecimais a mais do que os "
                f"{len(f['blobs'])} blobs do .dfm pedem")
            continue
        for dados, blob in zip(achados, f["blobs"]):
            if len(dados) != blob.tamanho:
                problemas.append(
                    f"{rel}: {blob.arquivo}: {len(dados)} bytes contra "
                    f"{blob.tamanho} no .dfm")
            elif hashlib.sha256(dados).hexdigest() != blob.sha256:
                problemas.append(
                    f"{rel}: {blob.arquivo}: SHA-256 diverge do .dfm")

    esperados = set(arquivos)
    for caminho in sorted(FORMS_OUT.glob("ep2002_*.lfm")):
        rel = f"{REL_FORMS}/{caminho.name}"
        if rel not in esperados:
            problemas.append(f"{rel}: sobra, nenhum .dfm o gera")
    for caminho in sorted(SRC_OUT.glob("ep2002_*.pas")):
        rel = f"{REL_SRC}/{caminho.name}"
        if rel not in esperados:
            problemas.append(f"{rel}: sobra, nenhum .dfm o gera")

    if problemas:
        print(f"{REL_FORMS} e {REL_SRC} nao correspondem a {REL_DFM}:",
              file=sys.stderr)
        for p in problemas:
            print("  " + p, file=sys.stderr)
        print(f"rode: python3 {GENERATOR}", file=sys.stderr)
        return 1

    n_blobs = sum(f["n_blobs"] for f in formularios)
    print(f"{len(arquivos)} arquivos em dia com {REL_DFM}; "
          f"{n_blobs} blobs conferidos pelo SHA-256 do .dfm "
          f"(sem ler {REL_DFM}/blobs/)")
    return 0


def do_write(arquivos: dict[str, str], formularios: list[dict]) -> int:
    blobs = carrega_blobs(formularios)
    arquivos = com_blobs(arquivos, formularios, blobs)

    FORMS_OUT.mkdir(parents=True, exist_ok=True)
    SRC_OUT.mkdir(parents=True, exist_ok=True)
    for rel, texto in sorted(arquivos.items()):
        (ROOT / rel).write_text(texto, encoding="ascii", newline="\n")

    for f in formularios:
        lfm = arquivos[f"{REL_FORMS}/{f['unidade']}.lfm"].count("\n")
        pas = arquivos[f"{REL_SRC}/{f['unidade']}.pas"].count("\n")
        print(f"  {f['unidade']}: {lfm} linhas de .lfm, {pas} de .pas, "
              f"{f['n_componentes']} componentes, {f['n_handlers']} handlers, "
              f"{f['n_blobs']} blobs, {len(f['descartes'])} descartes")
    total_desc = sum(len(f["descartes"]) for f in formularios)
    total_static = sum(len(f["staticos"]) for f in formularios)
    print(f"\n18 .lfm em {REL_FORMS}, 18 .pas em {REL_SRC}, "
          f"{REL_FORMS}/{RELATORIO}")
    print(f"{sum(f['n_componentes'] for f in formularios)} componentes, "
          f"{sum(f['n_handlers'] for f in formularios)} handlers, "
          f"{sum(f['n_blobs'] for f in formularios)} blobs, "
          f"{total_desc} propriedades descartadas, "
          f"{total_static} TStaticText a conferir na WTE-TASK-12")
    return 0


def main(argv: list[str]) -> int:
    check = False
    for arg in argv:
        if arg == "--check":
            check = True
        else:
            print(f"uso: {GENERATOR} [--check]", file=sys.stderr)
            return 2

    try:
        arquivos, formularios = converte()
        return do_check(arquivos, formularios) if check \
            else do_write(arquivos, formularios)
    except Dfm2LfmError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
