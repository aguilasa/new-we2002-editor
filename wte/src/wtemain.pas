{ wtemain -- auto-create, navegacao e o modo de captura (WTE-TASK-11).

  Esta unidade NAO tem formulario. Ela e o arranque: cria as 18 instancias
  globais na ordem do original e resolve a linha de comando. O formulario
  principal de verdade e `MainForm: TMainForm`, de `ep2002_mainform`, gerado
  pelo dfm2lfm.py -- o `TWteMainForm` provisorio da WTE-TASK-02 saiu aqui,
  como aquela task previa.

  A ordem de criacao NAO foi escolhida: foi medida no proprio binario. O
  `WinMain` do original chama `Application->CreateForm` 18 vezes entre
  0x401a2e e 0x401bc6, e cada sitio carrega a referencia de classe num
  endereco de `.data`; resolvendo cada uma pelo `vmtClassName` (o mesmo -44
  que o dump_published.py usa) sai a lista de CRIACAO na ordem abaixo.

  Isso importa porque `OnCreate` dispara na criacao: a ordem dos 18
  primeiros `FormCreate` do `trace.log` E esta lista, e e contra ela que a
  WTE-TASK-13 compara o original.

  Reproduzir a medida:

    objdump -d -M intel we-team-editor/we-team-editor.exe \
      | sed -n '/401a2e:/,/401bc6:/p' | grep -E 'mov +(ecx|edx),DWORD PTR ds:'

  O `edx` de cada sitio e o endereco que guarda o ponteiro de metaclasse; o
  `ecx` e a variavel global da instancia. }

unit wtemain;

{$mode objfpc}{$H+}

interface

// Sufixo posto no Caption dos 18. Ver MarcaOsTitulos.
const
  MARCA_DE_TITULO = ' [Lazarus]';

// Cria os 18 formularios na ordem medida do original.
procedure CriaFormularios;

// Trata a linha de comando. Devolve True se o programa deve seguir para o
// `Application.Run`, False se ja fez o que tinha de fazer (`--help`).
function TrataLinhaDeComando: Boolean;

implementation

uses
  SysUtils, Forms,
  retrace,
  ep2002_mainform, ep2002_estrategia, ep2002_jugador, ep2002_dorsal,
  ep2002_enlaza, ep2002_color, ep2002_info, ep2002_warning, ep2002_error,
  ep2002_info2, ep2002_about, ep2002_error2, ep2002_salida, ep2002_info4,
  ep2002_info3, ep2002_movertodos, ep2002_creditos_equipo, ep2002_warning_2;

procedure MarcaOsTitulos;
var
  i: Integer;
begin
  // DIVERGENCIA DELIBERADA, e obrigatoria -- criterio da WTE-TASK-11.
  //
  // `Application.Title` nao resolve: o Caption dos 18 vem do DFM, e o do
  // MainForm e literalmente " W11 Team Editor PT by chagas_michel!", o mesmo
  // do original. A partir da WTE-TASK-22 os dois rodam no MESMO :99, e o
  // harness acha janela por titulo e por tamanho -- com caption igual ele
  // dirigiria o lado errado, e o diff de bytes pareceria bug do port. E a
  // armadilha 6 do progresso.md, que ja custou tempo no newWe2002.
  //
  // O sufixo e posto EM TEMPO DE EXECUCAO, nao no .lfm: o .lfm e gerado, e
  // editar saida de gerador esta proibido. No :99 nao ha window manager,
  // entao nenhuma barra de titulo e desenhada e a captura da WTE-TASK-12 nao
  // enxerga isto; num desktop de verdade, enxerga -- e deve, porque o port
  // nao se faz passar pelo original.
  //
  // Registrar na WTE-TASK-35 (divergencias deliberadas).
  for i := 0 to Screen.FormCount - 1 do
    Screen.Forms[i].Caption := Screen.Forms[i].Caption + MARCA_DE_TITULO;
end;

procedure CriaFormularios;
begin
  // Ordem medida -- ver o cabecalho. NAO reordenar por gosto: reordenar
  // muda a ordem dos FormCreate e a WTE-TASK-13 acusaria divergencia que
  // nao existe no original.
  Application.CreateForm(TMainForm, MainForm);                          //  1
  Application.CreateForm(Testrategia, estrategia);                      //  2
  Application.CreateForm(Tjugador, jugador);                            //  3
  Application.CreateForm(Tficha_dorsal, ficha_dorsal);                  //  4
  Application.CreateForm(Tficha_enlaza, ficha_enlaza);                  //  5
  Application.CreateForm(Tficha_color, ficha_color);                    //  6
  Application.CreateForm(Tficha_info, ficha_info);                      //  7
  Application.CreateForm(Tficha_warning, ficha_warning);                //  8
  Application.CreateForm(Tficha_error, ficha_error);                    //  9
  Application.CreateForm(Tficha_info2, ficha_info2);                    // 10
  Application.CreateForm(Tficha_about, ficha_about);                    // 11
  Application.CreateForm(Tficha_error2, ficha_error2);                  // 12
  Application.CreateForm(Tficha_salida, ficha_salida);                  // 13
  Application.CreateForm(Tficha_info4, ficha_info4);                    // 14
  Application.CreateForm(Tficha_info3, ficha_info3);                    // 15
  Application.CreateForm(Tficha_movertodos, ficha_movertodos);          // 16
  Application.CreateForm(Tficha_creditos_equipo, ficha_creditos_equipo);// 17
  Application.CreateForm(Tficha_warning_2, ficha_warning_2);            // 18
  MarcaOsTitulos;
end;

// A casca ainda nao tem navegacao de verdade: quem abre formulario sao os
// handlers, e na fase 2 eles sao stub que so registra o nome. Ligar
// botao->formulario exige saber o que cada handler faz, que e a WTE-TASK-25
// em diante.
//
// O que existe aqui e o suficiente para a WTE-TASK-12 capturar os 18 sem
// navegar: `--show`. E andaime, nao comportamento do original, e some
// quando a navegacao de verdade chegar.
function AchaFormulario(const Nome: string): TForm;
var
  i: Integer;
begin
  Result := nil;
  for i := 0 to Screen.FormCount - 1 do
    if SameText(Screen.Forms[i].Name, Nome) then
      Exit(Screen.Forms[i]);
end;

procedure Ajuda;
var
  i: Integer;
begin
  WriteLn('wte -- a casca da fase 2 (WTE-TASK-11). Nenhum acesso a imagem de CD.');
  WriteLn;
  WriteLn('  wte                   abre o MainForm');
  WriteLn('  wte --show <nome>     abre so o formulario <nome>');
  WriteLn('  wte --show all        abre os 18 de uma vez (captura da WTE-TASK-12)');
  WriteLn('  wte --list            lista os nomes e sai');
  WriteLn('  wte --help            isto');
  WriteLn;
  WriteLn('O trace vai para wte/re/trace.log, ou para $WTE_TRACE_FILE.');
  WriteLn;
  WriteLn('Formularios, na ordem de criacao medida no original:');
  for i := 0 to Screen.FormCount - 1 do
    WriteLn('  ', Screen.Forms[i].Name, ' : ', Screen.Forms[i].ClassName);
end;

function TrataLinhaDeComando: Boolean;
var
  i, k: Integer;
  Alvo: string;
  F: TForm;
begin
  Result := True;
  i := 1;
  while i <= ParamCount do
  begin
    if (ParamStr(i) = '--help') or (ParamStr(i) = '-h') then
    begin
      Ajuda;
      Exit(False);
    end
    else if ParamStr(i) = '--list' then
    begin
      for k := 0 to Screen.FormCount - 1 do
        WriteLn(Screen.Forms[k].Name);
      Exit(False);
    end
    else if ParamStr(i) = '--show' then
    begin
      Inc(i);
      Alvo := ParamStr(i);
      if Alvo = '' then
        raise Exception.Create('--show exige o nome de um formulario (veja --list)');
      REMark('--show ' + Alvo);
      if SameText(Alvo, 'all') then
      begin
        for k := 0 to Screen.FormCount - 1 do
          Screen.Forms[k].Show;
      end
      else
      begin
        F := AchaFormulario(Alvo);
        if F = nil then
          raise Exception.CreateFmt(
            'formulario "%s" nao existe; rode --list', [Alvo]);
        // O MainForm continua sendo o principal para a LCL; mostrar outro
        // por cima e o que a captura precisa.
        F.Show;
      end;
    end
    else
      raise Exception.CreateFmt('argumento desconhecido: %s (veja --help)',
        [ParamStr(i)]);
    Inc(i);
  end;
end;

end.
