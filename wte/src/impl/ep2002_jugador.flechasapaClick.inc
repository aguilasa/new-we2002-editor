{ jugador.flechasapaClick -- 0x00408088, 981 bytes (mais a 0x00408460, 143 B).
  Spec: wte/re/spec/jugador.flechasapaClick.md

  O despachante das doze setas de aparencia. SAO DOIS DESPACHANTES EM FILA, e
  a leitura apressada veria um: o primeiro escreve o rotulo, o segundo
  redesenha os bitmaps, e todo caminho do primeiro cai no segundo.

  O indice sai do NOME, `Copy(Sender.Name, 11, 2)` -- `flechasapa` tem dez
  letras, e o corte de dois pega tanto `1`..`9` quanto `10`..`12`. Um so corte
  serve os doze porque o despacho compara CADEIA, nao numero -- diferente dos
  `barrhab*Scroll`, que precisaram de dois corpos.

  NAO GRAVA NA IMAGEM. Conferido pelo inventario de chamadas dos 1.124 bytes
  antes de escrever: nenhuma das duas escritoras (`0x00403400` e `0x00404048`)
  aparece. Escreve DENTRO DOS `.bmp`, o que e outra coisa -- ver abaixo. }
var
  sufixo: string;
  alvo: TComponent;
  posicao: Integer;
begin
  REMark('jugador.flechasapaClick');
  if not (Sender is TUpDown) then
    Exit;
  sufixo := Copy(TComponent(Sender).Name, 11, 2);
  posicao := TUpDown(Sender).Position;

  { Primeiro despachante: o rotulo.

    Os tres primeiros ramos sao os tres controles de faixa maior que as oito
    colunas da tabela de legendas, e e SO por isso que sao especiais: altura e
    idade mostram numero, a forma do cabelo tem tabela propria. O original le
    o campo do formulario aqui em vez do `Sender` -- e o mesmo objeto, e a
    fidelidade nao custa nada. }
  if sufixo = '7' then
    jugador.valorapa7.Caption := IntToStr(jugador.flechasapa7.Position + 148)
  else if sufixo = '9' then
    jugador.valorapa9.Caption := IntToStr(jugador.flechasapa9.Position + 15)
  else if sufixo = '3' then
    jugador.valorapa3.Caption := LegendaDoCabelo(jugador.flechasapa3.Position)
  else
  begin
    { O ramo generico, que atende os outros nove. O original acha o rotulo por
      nome e converte o sufixo em indice de linha pela `0x00408460`, que monta
      dois `Variant` e subtrai um. Aqui `StrToIntDef` faz a mesma conta sem o
      rodeio: o C++Builder usou `Variant` para nao ter de decidir o tipo. }
    alvo := jugador.FindComponent('valorapa' + sufixo);
    if alvo is TLabel then
      TLabel(alvo).Caption := Legenda(StrToIntDef(sufixo, 0), posicao);
  end;

  { Segundo despachante: os bitmaps. NAO PORTADO, e o motivo esta na spec.

    O original redesenha aqui `image/careto_base.bmp`, `image/pelo/pelo_<n>.bmp`
    e `image/barba/barba_<n>.bmp` -- `'2'` chama os tres, `'3'` e `'4'` o
    cabelo, `'5'` e `'6'` a barba. As tres carregadoras (0x00406fe0, 0x00407110,
    0x00407338, 1.414 B somados) NAO TEM DONO: a WTE-TASK-29 cobre uniforme e
    bandeira do MainForm, nao cara/cabelo/barba da ficha.

    E nao e so carregar. Cada uma abre o `.bmp` em "r+b" e REGRAVA A PALETA
    DENTRO DO ARQUIVO antes de recarrega-lo -- mexer numa seta de cabelo altera
    o arquivo que todos os jogadores compartilham. Ver a §6 de wte/re/assets.md.

    Ate la a seta muda o rotulo e nao muda o desenho. }
  if (sufixo = '2') or (sufixo = '3') or (sufixo = '4')
     or (sufixo = '5') or (sufixo = '6') then
    REMark('jugador.flechasapaClick: bitmap ' + sufixo + ' sem dono');
end;
