{ MainForm.paderecha2Click -- 0x0040e720, 316 bytes.
  Spec: wte/re/spec/MainForm.paderecha2Click.md

  A seta ">>": move os VINTE E TRES jogadores do time da esquerda para o da
  direita, de uma vez. NAO e o `paderechaClick` num laco -- tres diferencas
  medidas, todas na `MoveTodosOsJogadores` do `.aux.inc`:

  1. abre o `ficha_movertodos` como modal e so segue com `mrYes`;
  2. descarta os 23 codigos de retorno e nao mostra mensagem nenhuma;
  3. repovoa a lista de destino incondicionalmente.

  A TELA DE CONFIRMACAO E DESTE BOTAO, e nao do `paderechaeizquierdaClick`
  como o enunciado da WTE-TASK-26 dizia: o global `0x00432e48` que este corpo
  chama e o `_ficha_movertodos` exportado pelo proprio `.exe`, e o
  `paderechaeizquierdaClick` (`0x0040e304`) nao o toca. }
begin
  REMark('MainForm.paderecha2Click');
  MoveTodosOsJogadores(lista_equipos_1, lista_equipos_2, lista_jugadores_2,
                       BUF_ESQUERDA, BUF_DIREITA);
end;
