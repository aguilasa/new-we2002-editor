{ ficha_color.botonClick -- 0x00406078, 572 bytes.
  Um corpo para os quatro radios `boton0`..`boton3`.
  Spec: wte/re/spec/ficha_color.botonClick.md

  ELE NAO OLHA O `Sender` COMO OBJETO: recorta o SEXTO caractere do `Name` --
  `SubString(6, 1)`, e "boton" tem cinco letras -- e converte para inteiro. O
  digito e a familia de paleta, e e por isso que os quatro radios se chamam
  assim. Ligar um quinto radio a este handler mudaria a familia para 4, que nao
  existe; o original desenharia lixo, e o port nao pinta (ver `PreencheAmostras`
  no `wte_render2d`).

  CINCO MOVIMENTOS, e a quinta passagem desta task so tinha portado dois. Os
  tres que faltavam sao o comeco e o fim:

    1. **grava o vetor de volta na fonte ANTERIOR**, antes de qualquer outra
       coisa. Sem isto, editar a bandeira e clicar em "Unifo. 2D" perde a
       edicao -- e o erro nao aparece na hora, so quando o usuario volta;
    2. a familia, pelo digito do nome;
    3. para as familias 1 e 2 -- as que tem conjunto --, o `conjunto` sai do
       `ItemIndex` do combo `lista_col<familia>`. As familias 0 e 3 nao tem
       combo e nao mexem nele;
    4. so o combo da familia escolhida fica visivel; os outros tres somem;
    5. as 16 amostras sao recarregadas da fonte nova.

  O passo 3 explica por que o `lista_col1change` e o `lista_col2Change` escrevem
  o MESMO global: os dois sao "qual conjunto dentro da familia". }
var
  digito: Integer;

  procedure Combo(indice: Integer; visivel: Boolean);
  var
    c: TComponent;
  begin
    c := FindComponent('lista_col' + IntToStr(indice));
    if c is TControl then
      TControl(c).Visible := visivel;
  end;

var
  c: TComponent;
  b: Integer;
begin
  REMark('ficha_color.botonClick');
  if not (Sender is TComponent) then
    Exit;
  SalvaPaleta(TimeEmCor);

  if Length(TComponent(Sender).Name) < 6 then
    Exit;
  digito := StrToIntDef(Copy(TComponent(Sender).Name, 6, 1), -1);
  if digito < 0 then
    Exit;
  CorEmEdicao.familia := digito;

  if (digito = 1) or (digito = 2) then
  begin
    c := FindComponent('lista_col' + IntToStr(digito));
    if c is TComboBox then
      CorEmEdicao.conjunto := TComboBox(c).ItemIndex;
  end;

  Combo(digito, True);
  for b := 0 to 3 do
    if b <> digito then
      Combo(b, False);

  PreencheAmostras(Self, TimeEmCor);
end;
