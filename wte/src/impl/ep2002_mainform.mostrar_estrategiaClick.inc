{ MainForm.mostrar_estrategiaClick -- 0x00410220, 1.446 bytes.
  Spec: wte/re/spec/MainForm.mostrar_estrategiaClick.md

  A CARGA CHEGOU NA CORR-WTE-082, e ate ela este corpo era so navegacao -- o
  cabecalho dizia que encher a tela de tatica era "da WTE-TASK-26, dona do
  formulario `estrategia`". Nao era de ninguem: a `0x0040a0b4` caiu na
  fronteira entre as duas tasks e ficou sem dono ate a correcao.

  SAO DUAS METADES, e o original as separa no mesmo lugar que este corpo:

    - ele LE da imagem cinco regioes (formacao, cobrador, tatica e as duas
      cores de radar) para globais -- e isso e deste handler;
    - a `0x0040a0b4` posiciona a tela a partir das globais, SEM tocar em
      arquivo nenhum. Medido: nao ha `0x004033BC`, `0x00403388` nem `fseek` no
      corpo dela.

  As duas moram no `wte_tatica`, que e a unidade neutra: o preenchimento
  precisa do `ep2002_estrategia` e deste formulario ao mesmo tempo, e nenhum
  dos dois pode usar o outro na interface.

  AS CORES DE RADAR SO EXISTEM PARA SELECAO. O original desabilita os dois
  combos quando o indice chega a 95 e nem tenta ler; a `CarregaTaticaDaImagem`
  guarda isso em `tem_radar`. }
var
  titular: Boolean;
begin
  REMark('MainForm.mostrar_estrategiaClick');
  titular := LadoTitular(Sender, 'mostrar_estrategia_1');
  if titular then
    TimeEmEdicao := lista_equipos_1.ItemIndex
  else
    TimeEmEdicao := lista_equipos_2.ItemIndex;

  estrategia.ComboBox1.Enabled := TimeEmEdicao < TATICA_TIMES_COM_TABELA;
  estrategia.ComboBox2.Enabled := estrategia.ComboBox1.Enabled;

  if CarregaTaticaDaImagem(TimeEmEdicao) then
    PreencheTelaDeTatica;

  estrategia.ShowModal;
end;
