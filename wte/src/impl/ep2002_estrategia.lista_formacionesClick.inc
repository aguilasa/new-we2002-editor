{ estrategia.lista_formacionesClick -- 0x00409aa0, 259 bytes.
  Spec: wte/re/spec/estrategia.lista_formacionesClick.md

  Aplica uma das formacoes predefinidas sobre as onze bolas do campinho.

  O CORPO NAO TEM NUMERO NENHUM, e a spec da WTE-TASK-25 errava ao chamar isto
  de "quase so encaminhamento": ele aponta QUATRO ponteiros globais
  (`0x00434224`, `0x28`, `0x2c`, `0x30`) para dentro do registro escolhido e so
  entao chama as duas auxiliares. Le `lista_formaciones.ItemIndex` cinco vezes.

  SAO DOIS RAMOS, e o segundo e o que o port nao alcanca:

    ItemIndex <> 1   ->  indexa a tabela de 18 x 44 de `0x00433f0c`
    ItemIndex  = 1   ->  `DEFAULT`: le o buffer da formacao VIVA do time, em
                         `0x00432e88`, e escolhe a zona por um codigo em
                         `0x00432eaf` (16 = nenhuma das 16, cai no `STOCK`)

  O buffer vivo e preenchido por `0x0040a0b4` -- a rotina que enche a tela de
  tatica ao abrir o formulario --, que NAO esta portada e nao e desta correcao:
  ela e chamada pelo `MainForm.mostrar_estrategiaClick`, do grupo de carga.
  Enquanto ela nao existir, o item `DEFAULT` nao tem o que ler, e mandar as
  bolas para a tabela zerada as poria em (-2, -12), fora do campo. O port
  ignora o clique nesse item, e isso esta na spec como divergencia nomeada.

  NAO GRAVA NADA, e agora isso esta medido e nao delegado: as duas auxiliares
  so alcancam VCL (`FindComponent`, `TTimer.SetEnabled`, `TFont.SetColor`,
  `TControl.SetText`) e helpers de `AnsiString`/`Currency`. Nenhuma das tres
  rotinas abre arquivo. A spec dizia "nao medido, pergunte a WTE-TASK-27";
  agora a resposta e nenhum byte.

  A tabela de 18 x 44 mora em `.bss` e e montada pelo `estrategia.FormCreate` a
  partir de quatro blobs de `.data`. Ela esta extraida em
  `wte/src/wte_formacoes.pas` pelo `dump_formacoes.py` -- nao transcrita: sao
  792 numeros interleavados, e trocar X por Y a olho nao faria nada reclamar. }
var
  indice: Integer;
begin
  REMark('estrategia.lista_formacionesClick');
  indice := lista_formaciones.ItemIndex;
  if (indice < 0) or (indice >= FORMACOES_TOTAL) then
    Exit;

  { O ramo `DEFAULT`. Ver o cabecalho: falta o buffer vivo do time. }
  if indice = FORMACAO_DEFAULT then
    Exit;

  FormacaoAplicada := indice;
  PreparaAnimacao(indice);
  PintaPosicoes(indice);
end;
