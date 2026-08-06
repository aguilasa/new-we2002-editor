{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_dorsal`, classe `Tficha_dorsal`.
  Origem: `wte/re/dfm/ficha_dorsal.dfm`.
  4 componentes, 3 handlers publicados.

  **NAO EDITAR A MAO.** Correcao entra no gerador e o arquivo e regerado;
  `python3 wte/tools/dfm2lfm.py --check` compara com o commitado e e o que
  `make -C wte check` roda.

  Os corpos dos handlers sao stub que registra o proprio nome (secao 4.3 do
  plano): a fase 2 monta a casca inteira e a fase 4 e que preenche. `REStub`
  vem de `retrace.pas`, da WTE-TASK-11 -- a unidade nao pode se chamar
  `restub`, porque o nome colidiria com o da rotina.
}
unit ep2002_dorsal;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, ExtCtrls, Buttons, retrace;

type
  Tficha_dorsal = class(TForm)
    {
      Descartado: OldCreateOrder = False
      Motivo: propriedade de compatibilidade do Delphi 4; a LCL nao a tem e
      sempre usa a ordem nova de criacao.

      Descartado: TextHeight = 13
      Motivo: medida de tempo de projeto do Delphi, gravada para reescalar o
      formulario; a LCL nao a tem.
    }
    etiq_dorsal: TLabel;
    Bevel1: TBevel;
    BitBtn1: TBitBtn;
    scroll_dorsal: TScrollBar;
    procedure BitBtn1Click(Sender: TObject);
    procedure scroll_dorsalChange(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private

  public

  end;

var
  ficha_dorsal: Tficha_dorsal;

implementation

{$R ../forms/ep2002_dorsal.lfm}

{$PUSH}{$WARN 5024 OFF}  // stub ignora os parametros

procedure Tficha_dorsal.BitBtn1Click(Sender: TObject);
begin
  REStub('ficha_dorsal.BitBtn1Click');
end;

procedure Tficha_dorsal.scroll_dorsalChange(Sender: TObject);
begin
  REStub('ficha_dorsal.scroll_dorsalChange');
end;

procedure Tficha_dorsal.FormCreate(Sender: TObject);
begin
  REStub('ficha_dorsal.FormCreate');
end;

{$POP}

end.
