{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_enlaza`, classe `Tficha_enlaza`.
  Origem: `wte/re/dfm/ficha_enlaza.dfm`.
  6 componentes, 2 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}
unit ep2002_enlaza;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, Buttons, retrace;

type
  Tficha_enlaza = class(TForm)
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
    etiq3: TLabel;
    etiq4: TLabel;
    BitBtn1: TBitBtn;
    BitBtn2: TBitBtn;
    procedure FormShow(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private

  public

  end;

var
  ficha_enlaza: Tficha_enlaza;

implementation

{$R ../forms/ep2002_enlaza.lfm}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros

procedure Tficha_enlaza.FormShow(Sender: TObject);
begin
  REStub('ficha_enlaza.FormShow');
end;

procedure Tficha_enlaza.FormCreate(Sender: TObject);
begin
  REStub('ficha_enlaza.FormCreate');
end;

{$POP}

end.
