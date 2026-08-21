{ ficha_color.botonClick -- 0x00406078.
  Um corpo para os quatro radios `boton0`..`boton3`.

  ELE NAO OLHA O `Sender` COMO OBJETO: recorta o SEXTO caractere do `Name` --
  `SubString(6, 1)`, e "boton" tem cinco letras -- e converte para inteiro. O
  digito e a familia de paleta, e e por isso que os quatro radios se chamam
  assim. Ligar um quinto radio a este handler mudaria a familia para 4, que nao
  existe; o original desenharia lixo, e o port nao pinta (ver `PreencheAmostras`
  no `.aux.inc`). }
var
  nome: string;
  digito: Integer;
begin
  REMark('ficha_color.botonClick');
  if not (Sender is TComponent) then
    Exit;
  nome := TComponent(Sender).Name;
  if Length(nome) < 6 then
    Exit;
  digito := StrToIntDef(Copy(nome, 6, 1), -1);
  if digito < 0 then
    Exit;
  CorEmEdicao.familia := digito;
  PreencheAmostras(Self, TimeEmCor);
end;
