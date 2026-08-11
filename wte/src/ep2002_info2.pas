{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_info2`, classe `Tficha_info2`.
  Origem: `wte/re/dfm/ficha_info2.dfm`.
  6 componentes, 1 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Cada handler sai de uma de duas formas. Sem corpo escrito, sai como stub que
  registra o proprio nome (secao 4.3 do plano); `REStub` vem de
  `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar `restub`,
  porque o nome colidiria com o da rotina. Com corpo escrito, sai como a
  assinatura mais um $I para `impl/<unidade>.<handler>.inc`: o corpo e da fase 4,
  vem da spec de `wte/re/spec/`, e por isso mora fora deste arquivo gerado.
  Ver `wte/src/impl/README.md`.
}
unit ep2002_info2;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, Buttons, retrace;

type
  Tficha_info2 = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    Label4: TLabel;
    Label5: TLabel;
    BitBtn3: TBitBtn;
    procedure FormCreate(Sender: TObject);
  private

  public

  end;

var
  ficha_info2: Tficha_info2;

implementation

{$R ../forms/ep2002_info2.lfm}

procedure Tficha_info2.FormCreate(Sender: TObject);
{$I impl/ep2002_info2.FormCreate.inc}

end.
