{ jugador.FormCreate -- 0x00407ce0. Spec: wte/re/spec/jugador.FormCreate.md

  Forma `composto` do `wte/re/arranque.md`, 936 bytes, e o que ela faz e uma
  zebra: as 16 linhas de atributo alternam duas cores, e a coluna de aparencia
  alterna ao contrario da coluna de habilidade.

  O original acha cada rotulo por `FindComponent("valorhab" + N)` -- e o mesmo
  padrao que a CORR-WTE-044 mediu no `MainForm` com "dorsal" + N. Aqui ele fica
  como esta: sao 56 rotulos, e listar os 56 no `.lfm` para pegar cada um por
  campo trocaria uma linha de laco por 56 de repeticao.

  O `if i <= 12` nao e arbitrario: `valorhab`/`etiqhab` vao de 1 a 16 e
  `etiqapa`/`valorapa` so de 1 a 12, medido no proprio DFM. No original isso e
  um `cmp ebx,0xc` dentro do laco. }
var
  i: Integer;
  hab, apa: TColor;

  procedure Pinta(const nome: string; cor: TColor);
  var
    c: TComponent;
  begin
    c := FindComponent(nome);
    if c is TLabel then
      TLabel(c).Color := cor;
  end;

begin
  REMark('jugador.FormCreate');
  Color := $00E68F41;
  for i := 1 to 16 do
  begin
    if Odd(i) then
    begin
      hab := $00E68F41;
      apa := $00D78228;
    end
    else
    begin
      hab := $00D78228;
      apa := $00E68F41;
    end;
    Pinta('valorhab' + IntToStr(i), hab);
    Pinta('etiqhab' + IntToStr(i), hab);
    if i <= 12 then
    begin
      Pinta('etiqapa' + IntToStr(i), apa);
      Pinta('valorapa' + IntToStr(i), apa);
    end;
  end;
  etiqdorsal.Color := $00D78228;
  etiqnombre.Color := $00D78228;
  etiqprecio.Color := $00D78228;
end;
