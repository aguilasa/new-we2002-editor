{ MainForm.boton_barras2isoClick -- 0x0040cab8, 272 bytes.
  Spec: wte/re/spec/MainForm.boton_barras2isoClick.md

  Grava os cinco bytes do BUFFER DE EDICAO -- nao de `Jogo.teams[].bar_*` --
  no bloco do time selecionado. A distincao e a razao de o buffer existir: sem
  ela a gravacao levaria o valor velho ao disco e o golden acusaria a
  gravacao por um defeito da edicao.

  O endereco sai da mesma aritmetica do original, e nao de um `OFS_*` mais um
  passo: `0x45FF0 + 5*idx` e indice de byte no fluxo de DADOS, contado do setor
  850, e `EnderecoDeDados` faz a conversao MODE2/2352. As duas formas coincidem
  -- o `we2002_core` chega aos mesmos enderecos lendo em sequencia com um salto
  em `i = 3`, e a spec mostra os dois lados da conferencia.

  NAO valida indice: o original tambem nao. Quem impede o caso ruim e o
  formulario, que so habilita o botao com `ItemIndex` em 0..94. }
var
  offset: TOffset;
begin
  REMark('MainForm.boton_barras2isoClick');
  offset := EnderecoDeDados(BARRAS_SETOR_BASE,
                            BARRAS_LOGICO_BASE
                            + BARRAS_POR_TIME * lista_equipos.ItemIndex);
  if GravaNaImagem(offset, BarrasEmEdicao, Length(BarrasEmEdicao)) then
    { O port carrega a imagem UMA vez e desenha a partir de `Jogo`; o original
      rele o disco a cada troca de time. Sem esta linha, voltar ao time
      mostraria o valor velho na tela do proprio port -- e o arquivo estaria
      certo. Nao muda byte nenhum: ver a spec. }
    GuardaBarrasNoModelo(lista_equipos.ItemIndex);

  ficha_info3.etiq1.Caption := 'Barras inseridas no jogo!!!     ';
  ficha_info3.ShowModal;
end;
