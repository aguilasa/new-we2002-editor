{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_warning_2`, classe `Tficha_warning_2`.
  Origem: `wte/re/dfm/ficha_warning_2.dfm`.
  5 componentes, 1 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}
unit ep2002_warning_2;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, Buttons, retrace;

type
  Tficha_warning_2 = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    etiq1: TLabel;
    etiq2: TLabel;
    etiq4: TLabel;
    BitBtn1: TBitBtn;
    BitBtn2: TBitBtn;
    procedure FormCreate(Sender: TObject);
  private

  public

  end;

var
  ficha_warning_2: Tficha_warning_2;

implementation

{$R ../forms/ep2002_warning_2.lfm}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros

procedure Tficha_warning_2.FormCreate(Sender: TObject);
begin
  REStub('ficha_warning_2.FormCreate');
end;

{$POP}

end.
