{ ficha_color.oscurecerClick -- 0x004065fc, 328 bytes.
  Spec: wte/re/spec/ficha_color.oscurecerClick.md

  Um degrau para baixo em cada canal, em TODA a faixa selecionada -- as duas
  pontas incluidas. A aritmetica e a `Escurece` da `we2002_render`, que soma
  na palavra BGR555 empacotada e nao muda de espaco de cor.

  O LACO VAI DE `faixa_ini` A `faixa_fim` INCLUSIVE, e isso o separa do
  gradiente, que preenche so o miolo. No original o indice de base zero comeca
  em `faixa_ini - 1` e o teste e `< faixa_fim`, o que da o mesmo intervalo
  fechado em base um. }
var
  i: Integer;
begin
  REMark('ficha_color.oscurecerClick');
  for i := CorEmEdicao.faixa_ini to CorEmEdicao.faixa_fim do
  begin
    if (i < 1) or (i > COR_AMOSTRAS) then
      Continue;
    PintaUmaAmostra(Self, i, Escurece(CorEmEdicao.cores[i - 1]));
  end;
  MostraCorSelecionada(Self);
  AplicaAosDesenhos(Self);
end;
