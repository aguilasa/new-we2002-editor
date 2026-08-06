{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_error2`, classe `Tficha_error2`.
  Origem: `wte/re/dfm/ficha_error2.dfm`.
  2 componentes, 0 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}
unit ep2002_error2;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, Buttons;

type
  Tficha_error2 = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    etiq1: TLabel;
    BitBtn3: TBitBtn;
  private

  public

  end;

var
  ficha_error2: Tficha_error2;

implementation

{$R ../forms/ep2002_error2.lfm}

end.
