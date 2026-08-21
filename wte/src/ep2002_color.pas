{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_color`, classe `Tficha_color`.
  Origem: `wte/re/dfm/ficha_color.dfm`.
  65 componentes, 17 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Cada handler sai de uma de duas formas. Sem corpo escrito, sai como stub que
  registra o proprio nome (secao 4.3 do plano); `REStub` vem de
  `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar `restub`,
  porque o nome colidiria com o da rotina. Com corpo escrito, sai como a
  assinatura mais um $I para `impl/<unidade>.<handler>.inc`: o corpo e da fase 4,
  vem da spec de `wte/re/spec/`, e por isso mora fora deste arquivo gerado.

  Rotina interna compartilhada -- a que o original chama de mais de um handler
  -- nao e handler e nao cabe nesse formato. Ela mora em
  `impl/<unidade>.aux.inc`, um por unidade, e o $I dela sai UMA vez, antes de
  todos os handlers, para que eles possam chama-la.
  Ver `wte/src/impl/README.md`.
}
unit ep2002_color;

{$mode objfpc}{$H+}

interface

uses
  Classes, Forms, Controls, StdCtrls, ExtCtrls, Buttons, ComCtrls, retrace,
  Graphics, SysUtils, we2002_render, wte_cor, wte_render2d, wte_uniformes;

type
  Tficha_color = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    seleccion: TLabel;
    flecha_izquierda: TImage;
    flecha_derecha: TImage;
    color1: TLabel;
    color2: TLabel;
    color3: TLabel;
    color4: TLabel;
    color5: TLabel;
    color6: TLabel;
    color7: TLabel;
    color8: TLabel;
    color9: TLabel;
    color10: TLabel;
    color11: TLabel;
    color12: TLabel;
    color13: TLabel;
    color14: TLabel;
    color15: TLabel;
    color16: TLabel;
    recuadro2: TBevel;
    colcop0: TLabel;
    colcop1: TLabel;
    colcop2: TLabel;
    colcop3: TLabel;
    colcop4: TLabel;
    colcop5: TLabel;
    colcop6: TLabel;
    colcop7: TLabel;
    colcop8: TLabel;
    colcop9: TLabel;
    colcop10: TLabel;
    colcop11: TLabel;
    colcop12: TLabel;
    colcop13: TLabel;
    colcop14: TLabel;
    colcop15: TLabel;
    colcop16: TLabel;
    SpeedButton1: TSpeedButton;
    GroupBox1: TGroupBox;
    GroupBox2: TGroupBox;
    barra_rojo: TScrollBar;
    barra_verde: TScrollBar;
    barra_azul: TScrollBar;
    StaticText1: TStaticText;
    StaticText2: TStaticText;
    StaticText3: TStaticText;
    barra2: TTrackBar;
    barra1: TTrackBar;
    gradiente: TBitBtn;
    oscurecer: TBitBtn;
    aclarar: TBitBtn;
    GroupBox5: TGroupBox;
    Image2: TImage;
    Image3: TImage;
    boton2: TRadioButton;
    boton1: TRadioButton;
    boton0: TRadioButton;
    boton3: TRadioButton;
    lista_col2: TComboBox;
    lista_col3: TComboBox;
    lista_col1: TComboBox;
    lista_col0: TComboBox;
    BitBtn2: TBitBtn;
    BitBtn3: TBitBtn;
    BitBtn1: TBitBtn;
    procedure FormCreate(Sender: TObject);
    procedure barraChange(Sender: TObject);
    procedure botonClick(Sender: TObject);
    procedure barra1Change(Sender: TObject);
    procedure barra2Change(Sender: TObject);
    procedure gradienteClick(Sender: TObject);
    procedure oscurecerClick(Sender: TObject);
    procedure aclararClick(Sender: TObject);
    procedure lista_col0Change(Sender: TObject);
    procedure lista_col1change(Sender: TObject);
    procedure lista_col2Change(Sender: TObject);
    procedure lista_col3Change(Sender: TObject);
    procedure BitBtn1Click(Sender: TObject);
    procedure BitBtn2Click(Sender: TObject);
    procedure BitBtn3Click(Sender: TObject);
    procedure colorMouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure SpeedButton1Click(Sender: TObject);
  private

  public

  end;

var
  ficha_color: Tficha_color;

implementation

{$R ../forms/ep2002_color.lfm}

{ Rotinas internas que o original chama de mais de um handler -- nao sao
  metodo publicado, e por isso nao estao na classe. Ver wte/src/impl/README.md. }
{$I impl/ep2002_color.aux.inc}

procedure Tficha_color.FormCreate(Sender: TObject);
{$I impl/ep2002_color.FormCreate.inc}

procedure Tficha_color.barraChange(Sender: TObject);
{$I impl/ep2002_color.barraChange.inc}

procedure Tficha_color.botonClick(Sender: TObject);
{$I impl/ep2002_color.botonClick.inc}

procedure Tficha_color.barra1Change(Sender: TObject);
{$I impl/ep2002_color.barra1Change.inc}

procedure Tficha_color.barra2Change(Sender: TObject);
{$I impl/ep2002_color.barra2Change.inc}

procedure Tficha_color.gradienteClick(Sender: TObject);
{$I impl/ep2002_color.gradienteClick.inc}

procedure Tficha_color.oscurecerClick(Sender: TObject);
{$I impl/ep2002_color.oscurecerClick.inc}

procedure Tficha_color.aclararClick(Sender: TObject);
{$I impl/ep2002_color.aclararClick.inc}

procedure Tficha_color.lista_col0Change(Sender: TObject);
{$I impl/ep2002_color.lista_col0Change.inc}

procedure Tficha_color.lista_col1change(Sender: TObject);
{$I impl/ep2002_color.lista_col1change.inc}

procedure Tficha_color.lista_col2Change(Sender: TObject);
{$I impl/ep2002_color.lista_col2Change.inc}

procedure Tficha_color.lista_col3Change(Sender: TObject);
{$I impl/ep2002_color.lista_col3Change.inc}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Tficha_color.BitBtn1Click(Sender: TObject);
begin
  REStub('ficha_color.BitBtn1Click');
end;
{$POP}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Tficha_color.BitBtn2Click(Sender: TObject);
begin
  REStub('ficha_color.BitBtn2Click');
end;
{$POP}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Tficha_color.BitBtn3Click(Sender: TObject);
begin
  REStub('ficha_color.BitBtn3Click');
end;
{$POP}

procedure Tficha_color.colorMouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
{$I impl/ep2002_color.colorMouseDown.inc}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Tficha_color.SpeedButton1Click(Sender: TObject);
begin
  REStub('ficha_color.SpeedButton1Click');
end;
{$POP}

end.
