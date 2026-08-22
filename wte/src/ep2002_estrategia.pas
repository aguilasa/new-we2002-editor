{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `estrategia`, classe `Testrategia`.
  Origem: `wte/re/dfm/estrategia.dfm`.
  89 componentes, 14 handlers publicados.

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
unit ep2002_estrategia;

{$mode objfpc}{$H+}

interface

uses
  Classes, Types, Forms, Controls, StdCtrls, ExtCtrls, Buttons, retrace,
  SysUtils, Graphics, wte_zonas, wte_formacoes, wte_tatica, ep2002_warning_2,
  ep2002_error2, we2002_estado;

type
  Testrategia = class(TForm)
    {
      Descartado: OldCreateOrder = True
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    Shape3: TShape;
    campo: TImage;
    etiqjug2: TLabel;
    etiqjug0: TLabel;
    etiqjug1: TLabel;
    etiqjug3: TLabel;
    etiqjug4: TLabel;
    etiqjug5: TLabel;
    etiqjug6: TLabel;
    etiqjug7: TLabel;
    etiqjug8: TLabel;
    etiqjug9: TLabel;
    etiqjug10: TLabel;
    rectangulo: TShape;
    bola0: TShape;
    bola1: TShape;
    bola2: TShape;
    bola4: TShape;
    bola3: TShape;
    bola6: TShape;
    bola7: TShape;
    bola5: TShape;
    bola9: TShape;
    bola8: TShape;
    bola10: TShape;
    etiqestr1: TLabel;
    etiqestr2: TLabel;
    etiqestr3: TLabel;
    etiqestr4: TLabel;
    etiqestr5: TLabel;
    etiqestr6: TLabel;
    etiqestr7: TLabel;
    etiqestr8: TLabel;
    etiqestr9: TLabel;
    etiqestr10: TLabel;
    etiqestr11: TLabel;
    malla1: TImage;
    simbolo3: TShape;
    simbolo1: TShape;
    simbolo4: TShape;
    simbolo2: TShape;
    malla2: TImage;
    jugador1: TLabel;
    jugador2: TLabel;
    jugador3: TLabel;
    jugador4: TLabel;
    jugador5: TLabel;
    jugador6: TLabel;
    jugador7: TLabel;
    jugador8: TLabel;
    jugador9: TLabel;
    jugador10: TLabel;
    jugador11: TLabel;
    tirador1: TShape;
    tirador2: TShape;
    tirador3: TShape;
    tirador4: TShape;
    tirador5: TShape;
    tirador6: TShape;
    etiqpos1: TLabel;
    etiqpos2: TLabel;
    etiqpos3: TLabel;
    etiqpos4: TLabel;
    etiqpos5: TLabel;
    etiqpos6: TLabel;
    etiqpos7: TLabel;
    etiqpos8: TLabel;
    etiqpos9: TLabel;
    etiqpos10: TLabel;
    etiqpos11: TLabel;
    Image1: TImage;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    Label4: TLabel;
    Label5: TLabel;
    Label6: TLabel;
    bandera: TImage;
    Label7: TLabel;
    Label8: TLabel;
    Label9: TLabel;
    Label10: TLabel;
    lista_formaciones: TListBox;
    BitBtn6: TBitBtn;
    BitBtn1: TBitBtn;
    BitBtn2: TBitBtn;
    {
      Descartado: Ctl3D = True
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    ComboBox1: TComboBox;
    ComboBox2: TComboBox;
    reloj: TTimer;
    procedure bolaMouseMove(Sender: TObject; Shift: TShiftState;
      X, Y: Integer);
    procedure bolaMouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure campoMouseMove(Sender: TObject; Shift: TShiftState;
      X, Y: Integer);
    procedure FormCreate(Sender: TObject);
    procedure rectanguloDragOver(Sender, Source: TObject; X, Y: Integer;
      State: TDragState; var Accept: Boolean);
    procedure rectanguloDragDrop(Sender, Source: TObject; X, Y: Integer);
    procedure bolaEndDrag(Sender, Target: TObject; X, Y: Integer);
    procedure lista_formacionesClick(Sender: TObject);
    procedure relojTimer(Sender: TObject);
    procedure malla1MouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure malla2MouseDown(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y: Integer);
    procedure BitBtn1Click(Sender: TObject);
    procedure BitBtn3Click(Sender: TObject);
    procedure ComboBoxDrawItem(Control: TWinControl; Index: Integer;
      ARect: TRect; State: TOwnerDrawState);
  private

  public

  end;

var
  estrategia: Testrategia;

implementation

{$R ../forms/ep2002_estrategia.lfm}

{ Rotinas internas que o original chama de mais de um handler -- nao sao
  metodo publicado, e por isso nao estao na classe. Ver wte/src/impl/README.md. }
{$I impl/ep2002_estrategia.aux.inc}

procedure Testrategia.bolaMouseMove(Sender: TObject; Shift: TShiftState;
  X, Y: Integer);
{$I impl/ep2002_estrategia.bolaMouseMove.inc}

procedure Testrategia.bolaMouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
{$I impl/ep2002_estrategia.bolaMouseDown.inc}

procedure Testrategia.campoMouseMove(Sender: TObject; Shift: TShiftState;
  X, Y: Integer);
{$I impl/ep2002_estrategia.campoMouseMove.inc}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Testrategia.FormCreate(Sender: TObject);
begin
  REStub('estrategia.FormCreate');
end;
{$POP}

procedure Testrategia.rectanguloDragOver(Sender, Source: TObject;
  X, Y: Integer; State: TDragState; var Accept: Boolean);
{$I impl/ep2002_estrategia.rectanguloDragOver.inc}

procedure Testrategia.rectanguloDragDrop(Sender, Source: TObject;
  X, Y: Integer);
{$I impl/ep2002_estrategia.rectanguloDragDrop.inc}

procedure Testrategia.bolaEndDrag(Sender, Target: TObject; X, Y: Integer);
{$I impl/ep2002_estrategia.bolaEndDrag.inc}

procedure Testrategia.lista_formacionesClick(Sender: TObject);
{$I impl/ep2002_estrategia.lista_formacionesClick.inc}

procedure Testrategia.relojTimer(Sender: TObject);
{$I impl/ep2002_estrategia.relojTimer.inc}

procedure Testrategia.malla1MouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
{$I impl/ep2002_estrategia.malla1MouseDown.inc}

procedure Testrategia.malla2MouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
{$I impl/ep2002_estrategia.malla2MouseDown.inc}

procedure Testrategia.BitBtn1Click(Sender: TObject);
{$I impl/ep2002_estrategia.BitBtn1Click.inc}

procedure Testrategia.BitBtn3Click(Sender: TObject);
{$I impl/ep2002_estrategia.BitBtn3Click.inc}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros
procedure Testrategia.ComboBoxDrawItem(Control: TWinControl; Index: Integer;
  ARect: TRect; State: TOwnerDrawState);
begin
  REStub('estrategia.ComboBoxDrawItem');
end;
{$POP}

end.
