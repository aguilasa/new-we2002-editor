{ MainForm.FormShow -- 0x004111d8. Spec: wte/re/spec/MainForm.FormShow.md

  Duas coisas medidas, e nesta ordem:

  1. `dat.bin` e PRE-CONDICAO DE ARRANQUE. O original monta o caminho a partir
     do diretorio corrente, tenta abrir, e se falhar mostra `The file
     "dat.bin" must be in the "data" directory` (string 0x004250bd) e encerra.
  2. abrir a imagem passa pelo mesmo caminho do `boton_dialogo_weClick` --
     `wte/re/assets.md` secao 8.2 mediu o trecho de injecao duas vezes no
     `.exe`, uma em cada.

  A imagem vem da linha de comando e nao do dialogo porque o lado port do gate
  nao recebe teclado no `:99` (WTE-TASK-13): sem window manager o GTK2 nunca
  considera a janela ativa, entao nao ha como digitar caminho em dialogo
  nenhum. O argumento posicional existe no `wtemain.pas` desde a WTE-TASK-11
  exatamente para isto. }
var
  imagem: string;
begin
  REMark('MainForm.FormShow');
  { As tres cores de tempo de execucao. O original monta a cadeia `$00ffb676`,
    passa pelo `Graphics::StringToColor` e chama `SetColor` tres vezes -- em
    0x00411738 sobre a propria instancia (`ds:0x434360`), em 0x00411771 sobre o
    campo 0x2f4 e em 0x004117ab sobre o campo 0x30c, que o `wte/re/campos.tsv`
    resolve em `cuadro_dialogo_we` e `grupo_barras`. Era o "quais controles
    recebem $00ffb676" que a primeira passagem da WTE-TASK-25 deixou em aberto.

    Aqui a cadeia nao existe: passar por texto era a forma de o C++Builder
    escrever literal de cor, nao comportamento. O valor e o mesmo. }
  Color := $00FFB676;
  cuadro_dialogo_we.Color := $00FFB676;
  grupo_barras.Color := $00FFB676;
  if CaminhoDatBin = '' then
  begin
    { O original encerra. Aqui so se avisa: encerrar no `OnShow` levaria a
      janela embora antes de o harness do gate poder dirigi-la, e o
      diagnostico seria "a janela nao apareceu" -- que manda procurar no
      lugar errado. Divergencia deliberada, para a WTE-TASK-35. }
    texto_dialogo_we.Caption := 'data/dat.bin nao encontrado';
    Exit;
  end;
  imagem := ImagemDaLinhaDeComando;
  if imagem = '' then
    Exit;
  if AbreImagem(imagem) then
    texto_dialogo_we.Caption := ExtractFileName(imagem)
  else
    texto_dialogo_we.Caption := 'nao foi possivel abrir ' + ExtractFileName(imagem);
end;
