{ jugador.etiqprecioClick -- 0x00408bb8, 349 bytes.
  Spec: wte/re/spec/jugador.etiqprecioClick.md

  O rotulo `Preco` da ficha: clicar nele RECALCULA o preco a partir dos
  atributos que estao na tela e o escreve no `casilla_precio`. E a metade "de
  tela" da feature de preco; a de byte e o `MainForm.base_teamClick`.

  A SOMA VEM DA TELA, NAO DO DISCO, e isso e literal: o original faz
  `FindComponent('barrhab' + N)` para N de 1 a 16 e acumula o campo `+0x20c` de
  cada um, que num `TScrollBar` e a `Position`. Quem poe valor la e a
  `PreencheFicha`, como `max(atributo - 12, 0)`.

  A CONSEQUENCIA VALE REGISTRAR: mexer numa barrinha e clicar no rotulo da o
  preco do valor MEXIDO, mesmo sem gravar. O port faz o mesmo lendo as mesmas
  `Position` -- ler o `TPlayer` daria o preco do disco e seria outra coisa.

  O `x 5 div 3` E DO GOLEIRO, e a condicao aqui e `flechasapa1.Position = 0`
  (`0x00408c90`): o `flechasapa1` e a seta de POSICAO, e posicao 0 e goleiro.
  No `base_teamClick` a mesma pergunta e feita a memoria, porque la nao ha tela.

  E O QUE APARECE NO CAMPO E O PRECO VEZES 10.000 (`0x00408cb3`, `imul` de 64
  bits por `0x2710`). O byte gravado na imagem e o preco SEM o fator; quem
  multiplica e so a exibicao.

  NAO GRAVA NADA na imagem. }
var
  soma, i, preco: LongInt;
  c: TComponent;
begin
  REMark('jugador.etiqprecioClick');
  soma := 0;
  for i := 1 to 16 do
  begin
    c := FindComponent('barrhab' + IntToStr(i));
    if c is TScrollBar then
      soma := soma + TScrollBar(c).Position;
  end;
  preco := PrecoDaSoma(soma);
  if flechasapa1.Position = POSICAO_GOLEIRO then
    preco := (preco * 5) div 3;
  casilla_precio.Text := IntToStr(Int64(preco) * FATOR_DE_EXIBICAO);
end;
