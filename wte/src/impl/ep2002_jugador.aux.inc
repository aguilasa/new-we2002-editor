{ Rotinas internas do formulario `jugador` -- WTE-TASK-26, decima sexta
  passagem. Ver `wte/src/impl/README.md`. }

{ AtualizaHabilidade -- o corpo comum de `barrhabScroll` (0x00407a88) e
  `barrhab_bisScroll` (0x00407bb4), 300 bytes cada.

  OS DOIS HANDLERS SAO O MESMO CODIGO COM UM NUMERO DIFERENTE, e o numero e o
  comprimento do `Copy`: o primeiro faz `Copy(Sender.Name, 8, 1)` e o segundo
  `Copy(Sender.Name, 8, 2)`. `barrhab` tem sete caracteres, entao a posicao 8 e
  o primeiro digito -- um handler serve `barrhab1..9` e o outro `barrhab10..16`.

  Nao e uma familia de controles diferente; e a LARGURA DO NUMERO. O autor
  duplicou o corpo em vez de contar digitos, e o `_bis` do nome e so isso.

  O efeito e o mesmo do `Habilidade` do preenchimento da ficha, e nao podia
  deixar de ser: rotulo, largura da barrinha e cor. Aqui o valor vem do
  `ScrollPos` que a LCL entrega; la vem da camada de dados.

  NAO GRAVA NADA. Conferido pelo inventario de chamadas antes de escrever: os
  300 bytes de cada um alcancam `FindComponent`, `IntToStr`, `Copy`,
  `TControl::SetText`, `TControl::SetWidth` e a rotina de cor `0x00406fb4` --
  nenhuma escritora de imagem. E o unico lote desta task que fecha sem
  depender da WTE-TASK-27. }
procedure AtualizaHabilidade(const digitos: string; pos: Integer);
var
  c: TComponent;
begin
  if digitos = '' then
    Exit;
  c := jugador.FindComponent('imghab' + digitos);
  if c is TControl then
    TControl(c).Width := 7 * pos + 8;
  c := jugador.FindComponent('valorhab' + digitos);
  if not (c is TLabel) then
    Exit;
  TLabel(c).Caption := IntToStr(pos + 12);
  { O `0x00406fb4`: amarelo a partir de 5, branco abaixo. }
  if pos >= 5 then
    TLabel(c).Font.Color := $0000FFFF
  else
    TLabel(c).Font.Color := $00FFFFFF;
end;
