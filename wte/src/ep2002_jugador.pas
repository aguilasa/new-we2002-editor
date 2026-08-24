{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `jugador`, classe `Tjugador`.
  Origem: `wte/re/dfm/jugador.dfm`.
  113 componentes, 11 handlers publicados.

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
unit ep2002_jugador;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, ExtCtrls, Buttons, ComCtrls, SysUtils, Classes, Controls,
  wte_legendas, Graphics, retrace, we2002_estado, we2002_player, wte_ficha,
  ep2002_error2, we2002_preco;

type
  Tjugador = class(TForm)
    {
      Descartado: OldCreateOrder = True
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    imagen_base: TImage;
    etiqhab1: TLabel;
    etiqhab2: TLabel;
    valorhab1: TLabel;
    valorhab2: TLabel;
    etiqhab3: TLabel;
    etiqhab4: TLabel;
    valorhab3: TLabel;
    valorhab4: TLabel;
    etiqhab5: TLabel;
    etiqhab6: TLabel;
    valorhab5: TLabel;
    valorhab6: TLabel;
    etiqhab7: TLabel;
    etiqhab8: TLabel;
    valorhab7: TLabel;
    valorhab8: TLabel;
    etiqhab9: TLabel;
    etiqhab10: TLabel;
    valorhab9: TLabel;
    valorhab10: TLabel;
    etiqhab11: TLabel;
    etiqhab12: TLabel;
    valorhab11: TLabel;
    valorhab12: TLabel;
    etiqhab13: TLabel;
    etiqhab14: TLabel;
    valorhab13: TLabel;
    valorhab14: TLabel;
    etiqhab15: TLabel;
    etiqhab16: TLabel;
    valorhab15: TLabel;
    valorhab16: TLabel;
    etiqprecio: TLabel;
    etiqapa1: TLabel;
    valorapa1: TLabel;
    etiqapa2: TLabel;
    etiqapa3: TLabel;
    valorapa2: TLabel;
    valorapa3: TLabel;
    etiqapa4: TLabel;
    etiqapa5: TLabel;
    valorapa4: TLabel;
    valorapa5: TLabel;
    etiqapa6: TLabel;
    etiqapa7: TLabel;
    valorapa6: TLabel;
    valorapa7: TLabel;
    etiqapa8: TLabel;
    etiqapa9: TLabel;
    valorapa8: TLabel;
    valorapa9: TLabel;
    etiqapa10: TLabel;
    etiqapa11: TLabel;
    valorapa10: TLabel;
    valorapa11: TLabel;
    etiqapa12: TLabel;
    valorapa12: TLabel;
    etiqnombre: TLabel;
    imagen_barba_0: TImage;
    imagen_pelo: TImage;
    imagen_barba: TImage;
    etiqdorsal: TLabel;
    imghab1: TImage;
    imghab2: TImage;
    imghab3: TImage;
    imghab4: TImage;
    imghab5: TImage;
    imghab6: TImage;
    imghab7: TImage;
    imghab8: TImage;
    imghab9: TImage;
    imghab10: TImage;
    imghab11: TImage;
    imghab12: TImage;
    imghab13: TImage;
    imghab14: TImage;
    imghab15: TImage;
    imghab16: TImage;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab1: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab2: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab3: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab4: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab5: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab6: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab7: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab8: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab9: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab10: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab11: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab12: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab13: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab14: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab15: TScrollBar;
    {
      Descartado: Ctl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.

      Descartado: ParentCtl3D = False
      Motivo: a LCL nao tem Ctl3D: a borda 3D e do tema do Win32, e o GTK2
      desenha a borda propria.
    }
    barrhab16: TScrollBar;
    BitBtn3: TBitBtn;
    casilla_precio: TEdit;
    flechasapa1: TUpDown;
    flechasapa2: TUpDown;
    flechasapa3: TUpDown;
    flechasapa4: TUpDown;
    flechasapa5: TUpDown;
    flechasapa6: TUpDown;
    flechasapa7: TUpDown;
    flechasapa8: TUpDown;
    flechasapa9: TUpDown;
    flechasapa10: TUpDown;
    flechasapa11: TUpDown;
    flechasapa12: TUpDown;
    casilla_nombre: TEdit;
    BitBtn1: TBitBtn;
    BitBtn2: TBitBtn;
    casilla_dorsal: TEdit;
    procedure BitBtn2Click(Sender: TObject);
    procedure BitBtn1Click(Sender: TObject);
    procedure barrhabScroll(Sender: TObject; ScrollCode: TScrollCode;
      var ScrollPos: Integer);
    procedure barrhab_bisScroll(Sender: TObject; ScrollCode: TScrollCode;
      var ScrollPos: Integer);
    procedure FormCreate(Sender: TObject);
    procedure flechasapaClick(Sender: TObject; Button: TUDBtnType);
    procedure BitBtn3Click(Sender: TObject);
    procedure casilla_nombreKeyPress(Sender: TObject; var Key: char);
    procedure casilla_dorsalKeyPress(Sender: TObject; var Key: char);
    procedure casilla_precioKeyPress(Sender: TObject; var Key: char);
    procedure etiqprecioClick(Sender: TObject);
  private

  public

  end;

var
  jugador: Tjugador;

implementation

{$R ../forms/ep2002_jugador.lfm}

{ Rotinas internas que o original chama de mais de um handler -- nao sao
  metodo publicado, e por isso nao estao na classe. Ver wte/src/impl/README.md. }
{$I impl/ep2002_jugador.aux.inc}

procedure Tjugador.BitBtn2Click(Sender: TObject);
{$I impl/ep2002_jugador.BitBtn2Click.inc}

procedure Tjugador.BitBtn1Click(Sender: TObject);
{$I impl/ep2002_jugador.BitBtn1Click.inc}

procedure Tjugador.barrhabScroll(Sender: TObject; ScrollCode: TScrollCode;
  var ScrollPos: Integer);
{$I impl/ep2002_jugador.barrhabScroll.inc}

procedure Tjugador.barrhab_bisScroll(Sender: TObject; ScrollCode: TScrollCode;
  var ScrollPos: Integer);
{$I impl/ep2002_jugador.barrhab_bisScroll.inc}

procedure Tjugador.FormCreate(Sender: TObject);
{$I impl/ep2002_jugador.FormCreate.inc}

procedure Tjugador.flechasapaClick(Sender: TObject; Button: TUDBtnType);
{$I impl/ep2002_jugador.flechasapaClick.inc}

procedure Tjugador.BitBtn3Click(Sender: TObject);
{$I impl/ep2002_jugador.BitBtn3Click.inc}

procedure Tjugador.casilla_nombreKeyPress(Sender: TObject; var Key: char);
{$I impl/ep2002_jugador.casilla_nombreKeyPress.inc}

procedure Tjugador.casilla_dorsalKeyPress(Sender: TObject; var Key: char);
{$I impl/ep2002_jugador.casilla_dorsalKeyPress.inc}

procedure Tjugador.casilla_precioKeyPress(Sender: TObject; var Key: char);
{$I impl/ep2002_jugador.casilla_precioKeyPress.inc}

procedure Tjugador.etiqprecioClick(Sender: TObject);
{$I impl/ep2002_jugador.etiqprecioClick.inc}

end.
