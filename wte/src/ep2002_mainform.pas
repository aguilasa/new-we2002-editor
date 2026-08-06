{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `MainForm`, classe `TMainForm`.
  Origem: `wte/re/dfm/MainForm.dfm`.
  116 componentes, 37 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}
unit ep2002_mainform;

{$mode objfpc}{$H+}

interface

uses
  Classes, Forms, Controls, StdCtrls, ExtCtrls, Buttons, ComCtrls, Dialogs,
  ActnList, retrace;

type
  TMainForm = class(TForm)
    {
      Descartado: OldCreateOrder = True
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    Image1: TImage;
    SpeedButton1: TSpeedButton;
    SpeedButton2: TSpeedButton;
    Image4: TImage;
    GroupBox4: TGroupBox;
    colorear: TSpeedButton;
    home1: TImage;
    home2: TImage;
    Shape8: TShape;
    bandera: TImage;
    punto: TShape;
    grupo_memorycard: TGroupBox;
    Image2: TImage;
    boton_mcr2iso: TSpeedButton;
    boton_tex2iso: TSpeedButton;
    boton_mcr: TSpeedButton;
    boton_dialogo_tex: TSpeedButton;
    grabar_memory: TSpeedButton;
    grabar_camiseta: TSpeedButton;
    {
      Descartado: Action = lanza_url
      Motivo: a propriedade existe na LCL, mas o valor aponta para
      'lanza_url', que era TBrowseURL e virou TLabel; TLabel nao e
      TBasicAction e o leitor de LFM recusaria a atribuicao.
    }
    SpeedButton3: TSpeedButton;
    Image3: TImage;
    etiqueta_mcr: TStaticText;
    texto_mcr: TStaticText;
    etiqueta_camiseta: TStaticText;
    texto_dialogo_tex: TStaticText;
    cuadro_dialogo_we: TGroupBox;
    boton_dialogo_we: TSpeedButton;
    etiqueta_juego: TStaticText;
    texto_dialogo_we: TStaticText;
    grupo_barras: TGroupBox;
    Shape1: TShape;
    Shape2: TShape;
    Shape4: TShape;
    Shape5: TShape;
    Shape6: TShape;
    barra0: TImage;
    barra1: TImage;
    barra2: TImage;
    barra3: TImage;
    barra4: TImage;
    boton_barras2iso: TSpeedButton;
    {
      Descartado: Ctl3D = True
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    sel_barra0: TRadioButton;
    sel_barra1: TRadioButton;
    sel_barra2: TRadioButton;
    sel_barra3: TRadioButton;
    sel_barra4: TRadioButton;
    track_barra: TTrackBar;
    grupo_nombre: TGroupBox;
    etiq_nombre1: TLabel;
    etiq_nombre2: TLabel;
    etiq_nombre3: TLabel;
    boton_nombres2iso: TSpeedButton;
    iguala_nombres: TSpeedButton;
    edit_nombre1: TEdit;
    edit_nombre2: TEdit;
    edit_nombre3: TEdit;
    GroupBox3: TGroupBox;
    StaticText1: TStaticText;
    lista_equipos: TComboBox;
    GroupBox1: TGroupBox;
    parriba: TSpeedButton;
    pabajo: TSpeedButton;
    mostrar_jugador_1: TSpeedButton;
    mostrar_jugador_2: TSpeedButton;
    mostrar_estrategia_2: TSpeedButton;
    mostrar_estrategia_1: TSpeedButton;
    Label1: TLabel;
    Label2: TLabel;
    Shape3: TShape;
    banderita1: TImage;
    Shape7: TShape;
    banderita2: TImage;
    paderecha2: TSpeedButton;
    paderecha: TSpeedButton;
    paderechaeizquierda: TSpeedButton;
    paizquierda: TSpeedButton;
    paizquierda2: TSpeedButton;
    help_team: TStaticText;
    lista_jugadores_1: TComboBox;
    lista_jugadores_2: TComboBox;
    base_team: TStaticText;
    dorsal1: TStaticText;
    dorsal2: TStaticText;
    dorsal3: TStaticText;
    dorsal4: TStaticText;
    dorsal5: TStaticText;
    dorsal6: TStaticText;
    dorsal7: TStaticText;
    dorsal8: TStaticText;
    dorsal9: TStaticText;
    dorsal10: TStaticText;
    dorsal11: TStaticText;
    dorsal12: TStaticText;
    dorsal13: TStaticText;
    dorsal14: TStaticText;
    dorsal15: TStaticText;
    dorsal16: TStaticText;
    dorsal17: TStaticText;
    dorsal18: TStaticText;
    dorsal19: TStaticText;
    dorsal20: TStaticText;
    dorsal21: TStaticText;
    dorsal22: TStaticText;
    dorsal23: TStaticText;
    casilla_xmlibres: TStaticText;
    {
      Descartado: Ctl3D = True
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    lista_descarte: TListBox;
    lista_equipos_2: TComboBox;
    lista_equipos_1: TComboBox;
    dialogo_we: TOpenDialog;
    dialogo_mcr: TOpenDialog;
    dialogo_tex: TOpenDialog;
    dialogo_grabar_camiseta: TSaveDialog;
    dialogo_grabar_memory: TSaveDialog;
    ActionList1: TActionList;
    {
      TODO WTE-TASK-10: 'lanza_url' era TBrowseURL -- a acao padrao da VCL
      (unidade Extactns), medida na WTE-TASK-07. A LCL nao a tem, e virou
      TLabel. O comportamento original abria a URL da constante LANZA_URL_URL
      no navegador: reimplementar com OpenURL() de LCLIntf no handler que
      dispara.

      Descartado: Category = 'Internet'
      Motivo: categoria de TAction; some com a acao, porque TLabel nao e acao.

      Descartado: URL = 'http://www.w11.com.br         '
      Motivo: propriedade do TBrowseURL; o valor fica na constante <NOME>_URL
      da unidade e o comportamento vira OpenURL() no handler.
    }
    lanza_url: TLabel;
    procedure boton_dialogo_weClick(Sender: TObject);
    procedure boton_mcrClick(Sender: TObject);
    procedure boton_mcr2isoClick(Sender: TObject);
    { Metodo publicado sem ligacao em DFM nenhum (WTE-TASK-04). }
    procedure Button2Click(Sender: TObject);
    procedure sel_barraClick(Sender: TObject);
    procedure track_barraChange(Sender: TObject);
    procedure boton_barras2isoClick(Sender: TObject);
    procedure lista_equiposChange(Sender: TObject);
    procedure edit_nombre1KeyPress(Sender: TObject; var Key: char);
    procedure edit_nombre2KeyPress(Sender: TObject; var Key: char);
    procedure edit_nombre3KeyPress(Sender: TObject; var Key: char);
    procedure iguala_nombresClick(Sender: TObject);
    procedure boton_nombres2isoClick(Sender: TObject);
    procedure boton_tex2isoClick(Sender: TObject);
    procedure boton_dialogo_texClick(Sender: TObject);
    procedure lista_equipos_2Change(Sender: TObject);
    procedure paderechaeizquierdaClick(Sender: TObject);
    procedure paizquierdaClick(Sender: TObject);
    procedure paderechaClick(Sender: TObject);
    procedure paderecha2Click(Sender: TObject);
    procedure paizquierda2Click(Sender: TObject);
    procedure parribaClick(Sender: TObject);
    procedure pabajoClick(Sender: TObject);
    procedure grabar_camisetaClick(Sender: TObject);
    procedure grabar_memoryClick(Sender: TObject);
    procedure lista_jugadores_1Change(Sender: TObject);
    procedure mostrar_jugadorClick(Sender: TObject);
    procedure mostrar_estrategiaClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure dorsalClick(Sender: TObject);
    procedure dorsalMouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure colorearClick(Sender: TObject);
    procedure SpeedButton2Click(Sender: TObject);
    procedure SpeedButton1Click(Sender: TObject);
    procedure Image3Click(Sender: TObject);
    procedure base_teamClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
  private

  public

  end;

const
  { URL do TBrowseURL 'lanza_url', descartada do .lfm porque
    TLabel nao tem a propriedade. Guardada aqui para que o
    valor nao se perca -- ver wte/forms/conversao.md. }
  LANZA_URL_URL = 'http://www.w11.com.br         ';

var
  MainForm: TMainForm;

implementation

{$R ../forms/ep2002_mainform.lfm}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros

procedure TMainForm.boton_dialogo_weClick(Sender: TObject);
begin
  REStub('MainForm.boton_dialogo_weClick');
end;

procedure TMainForm.boton_mcrClick(Sender: TObject);
begin
  REStub('MainForm.boton_mcrClick');
end;

procedure TMainForm.boton_mcr2isoClick(Sender: TObject);
begin
  REStub('MainForm.boton_mcr2isoClick');
end;

procedure TMainForm.Button2Click(Sender: TObject);
begin
  REStub('MainForm.Button2Click');
end;

procedure TMainForm.sel_barraClick(Sender: TObject);
begin
  REStub('MainForm.sel_barraClick');
end;

procedure TMainForm.track_barraChange(Sender: TObject);
begin
  REStub('MainForm.track_barraChange');
end;

procedure TMainForm.boton_barras2isoClick(Sender: TObject);
begin
  REStub('MainForm.boton_barras2isoClick');
end;

procedure TMainForm.lista_equiposChange(Sender: TObject);
begin
  REStub('MainForm.lista_equiposChange');
end;

procedure TMainForm.edit_nombre1KeyPress(Sender: TObject; var Key: char);
begin
  REStub('MainForm.edit_nombre1KeyPress');
end;

procedure TMainForm.edit_nombre2KeyPress(Sender: TObject; var Key: char);
begin
  REStub('MainForm.edit_nombre2KeyPress');
end;

procedure TMainForm.edit_nombre3KeyPress(Sender: TObject; var Key: char);
begin
  REStub('MainForm.edit_nombre3KeyPress');
end;

procedure TMainForm.iguala_nombresClick(Sender: TObject);
begin
  REStub('MainForm.iguala_nombresClick');
end;

procedure TMainForm.boton_nombres2isoClick(Sender: TObject);
begin
  REStub('MainForm.boton_nombres2isoClick');
end;

procedure TMainForm.boton_tex2isoClick(Sender: TObject);
begin
  REStub('MainForm.boton_tex2isoClick');
end;

procedure TMainForm.boton_dialogo_texClick(Sender: TObject);
begin
  REStub('MainForm.boton_dialogo_texClick');
end;

procedure TMainForm.lista_equipos_2Change(Sender: TObject);
begin
  REStub('MainForm.lista_equipos_2Change');
end;

procedure TMainForm.paderechaeizquierdaClick(Sender: TObject);
begin
  REStub('MainForm.paderechaeizquierdaClick');
end;

procedure TMainForm.paizquierdaClick(Sender: TObject);
begin
  REStub('MainForm.paizquierdaClick');
end;

procedure TMainForm.paderechaClick(Sender: TObject);
begin
  REStub('MainForm.paderechaClick');
end;

procedure TMainForm.paderecha2Click(Sender: TObject);
begin
  REStub('MainForm.paderecha2Click');
end;

procedure TMainForm.paizquierda2Click(Sender: TObject);
begin
  REStub('MainForm.paizquierda2Click');
end;

procedure TMainForm.parribaClick(Sender: TObject);
begin
  REStub('MainForm.parribaClick');
end;

procedure TMainForm.pabajoClick(Sender: TObject);
begin
  REStub('MainForm.pabajoClick');
end;

procedure TMainForm.grabar_camisetaClick(Sender: TObject);
begin
  REStub('MainForm.grabar_camisetaClick');
end;

procedure TMainForm.grabar_memoryClick(Sender: TObject);
begin
  REStub('MainForm.grabar_memoryClick');
end;

procedure TMainForm.lista_jugadores_1Change(Sender: TObject);
begin
  REStub('MainForm.lista_jugadores_1Change');
end;

procedure TMainForm.mostrar_jugadorClick(Sender: TObject);
begin
  REStub('MainForm.mostrar_jugadorClick');
end;

procedure TMainForm.mostrar_estrategiaClick(Sender: TObject);
begin
  REStub('MainForm.mostrar_estrategiaClick');
end;

procedure TMainForm.FormCreate(Sender: TObject);
begin
  REStub('MainForm.FormCreate');
end;

procedure TMainForm.dorsalClick(Sender: TObject);
begin
  REStub('MainForm.dorsalClick');
end;

procedure TMainForm.dorsalMouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
begin
  REStub('MainForm.dorsalMouseDown');
end;

procedure TMainForm.colorearClick(Sender: TObject);
begin
  REStub('MainForm.colorearClick');
end;

procedure TMainForm.SpeedButton2Click(Sender: TObject);
begin
  REStub('MainForm.SpeedButton2Click');
end;

procedure TMainForm.SpeedButton1Click(Sender: TObject);
begin
  REStub('MainForm.SpeedButton1Click');
end;

procedure TMainForm.Image3Click(Sender: TObject);
begin
  REStub('MainForm.Image3Click');
end;

procedure TMainForm.base_teamClick(Sender: TObject);
begin
  REStub('MainForm.base_teamClick');
end;

procedure TMainForm.FormShow(Sender: TObject);
begin
  REStub('MainForm.FormShow');
end;

{$POP}

end.
