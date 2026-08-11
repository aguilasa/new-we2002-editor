{ Esqueleto gerado por `wte/tools/dfm2lfm.py` (WTE-TASK-10).

  Formulario `ficha_warning`, classe `Tficha_warning`.
  Origem: `wte/re/dfm/ficha_warning.dfm`.
  5 componentes, 1 handlers publicados.

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
unit ep2002_warning;

{$mode objfpc}{$H+}

interface

uses
  Forms, StdCtrls, Buttons, retrace;

type
  Tficha_warning = class(TForm)
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
  ficha_warning: Tficha_warning;

implementation

{$R ../forms/ep2002_warning.lfm}

procedure Tficha_warning.FormCreate(Sender: TObject);
{$I impl/ep2002_warning.FormCreate.inc}

end.
