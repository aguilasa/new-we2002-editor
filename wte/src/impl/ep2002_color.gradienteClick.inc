{ ficha_color.gradienteClick -- 0x004063b0, 588 bytes.
  Spec: wte/re/spec/ficha_color.gradienteClick.md

  Interpola entre as duas pontas da faixa e preenche o MIOLO. As pontas ficam
  como estao -- o laco do original vai de `faixa_ini + 1` a `faixa_fim - 1`,
  e escrever `faixa_fim - faixa_ini` entradas apagaria a cor que o usuario
  escolheu na ponta de cima.

  A ARITMETICA E A DA `Rampa`, e ela e o risco nomeado da secao 9 do plano:
  passo em `Single`, acumulador em `Single`, e conversao para inteiro por
  TRUNCAMENTO -- nao `Round`. As duas causas estao medidas em
  `wte/re/render2d.md` e o `dump_render2d.py --check` recusa emitir se alguma
  deixar de bater com o `.exe`.

  A `Rampa` NAO desenha nem grava: devolve o miolo, e quem o poe na tela e o
  laco abaixo, uma amostra por vez, como o original faz. }
var
  miolo: array[0 .. COR_AMOSTRAS - 1] of TCorBgr555;
  distancia, i: Integer;
begin
  REMark('ficha_color.gradienteClick');
  distancia := CorEmEdicao.faixa_fim - CorEmEdicao.faixa_ini;
  if (CorEmEdicao.faixa_ini >= 1) and (CorEmEdicao.faixa_fim <= COR_AMOSTRAS)
     and Rampa(CorEmEdicao.cores[CorEmEdicao.faixa_ini - 1],
               CorEmEdicao.cores[CorEmEdicao.faixa_fim - 1],
               distancia, miolo) then
  begin
    { `miolo[0]` e a amostra `faixa_ini + 1`, em base um. }
    for i := 0 to distancia - 2 do
      PintaUmaAmostra(Self, CorEmEdicao.faixa_ini + 1 + i, miolo[i]);
  end;
  MostraCorSelecionada(Self);
  AplicaAosDesenhos(Self);
end;
