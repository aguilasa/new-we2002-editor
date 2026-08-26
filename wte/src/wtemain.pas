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
      | sed -n '/401a22:/,/401bc6:/p' | grep -E 'mov +(ecx|edx),DWORD PTR ds:'

  A faixa comeca em 0x401a22, nao em 0x401a2e: as 18 CHAMADAS de CreateForm
  vao de 0x401a2e a 0x401bc6, mas os dois `mov` que carregam os operandos de
  cada sitio vem ANTES da chamada dele. Comecando na chamada, o primeiro par
  fica de fora e a saida traz 17 classes, sem TMainForm.

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

// Caminho da imagem passado na linha de comando, ou '' se nao veio nenhum.
//
// O app AINDA NAO LE a imagem -- os 96 handlers sao stubs ate a WTE-TASK-25, e
// o fechamento da fase 3 mediu isso: zero unidade da casca da `uses
// we2002_database`. O caminho e guardado e registrado no trace, e nada mais.
//
// Existe por causa do gate golden (WTE-TASK-22): os dois lados recebem a MESMA
// entrada, cada um sobre a sua copia. Sem isto o `golden_run_laz.sh` teria de
// omitir o argumento hoje e ganha-lo depois -- e harness que muda de forma
// entre uma fase e a seguinte deixa de comparar a mesma coisa.
function ImagemDaLinhaDeComando: string;

implementation

uses
  SysUtils, Forms,
  {$IFDEF WINDOWS}Windows,{$ENDIF}
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

// O `--show` FOI REMOVIDO na WTE-TASK-25, e ele tinha dono e prazo desde que
// nasceu: existia porque na fase 2 nada navegava -- os handlers eram stub, e
// sem ele a WTE-TASK-12 nao teria como abrir formulario para capturar. Com a
// navegacao de verdade no lugar (`mostrar_jugadorClick` e
// `mostrar_estrategiaClick` abrem `jugador` e `estrategia`), o andaime perdeu
// a razao de existir, e andaime sem dono nomeado fica para sempre. Saiu com
// ele o `AchaFormulario`, que so o servia.
//
// O `--list` ficou: e barato, nao simula comportamento nenhum e continua util
// para conferir que os 18 formularios foram criados.

var
  ImagemPedida: string = '';

function ImagemDaLinhaDeComando: string;
begin
  Result := ImagemPedida;
end;

{ SAIDA DE TEXTO, E POR QUE ELA NAO E UM `WriteLn` DIRETO.

  No Linux o binario tem `stdout` sempre, e `WriteLn` bastava -- foi o que
  esteve aqui ate 2026-08-26. No Windows nao: o `.lpi` pede
  `GraphicApplication`, e um `.exe` do subsistema GUI nasce SEM handle de
  saida padrao. A RTL do FPC nao abre `Output` nesse caso, e o primeiro
  `WriteLn` levanta `EInOutError`, que a LCL transforma no dialogo generico

    File not open. / Press OK to ignore and risk data corruption.

  antes de qualquer janela. Medido em 2026-08-26: `wte.exe --list` e
  `wte.exe --help` travavam ali, e nem a lista nem a ajuda saiam. Redirecionar
  a saida no shell NAO resolve -- quem nao abriu o arquivo foi a RTL, nao o
  sistema.

  A saida e `AttachConsole(ATTACH_PARENT_PROCESS)`: se quem lancou tem
  console, o processo entra nele e `SysInitStdIO` religa `Output`; se nao tem
  (duplo clique no icone), nao ha para onde escrever e a impressao vira
  silencio, que e o certo -- e o que o Linux faria com `stdout` fechado.

  A resolucao e PREGUICOSA de proposito. Fazer isso no arranque anexaria um
  console a toda abertura normal do editor, sem ninguem para ler. }
var
  SaidaResolvida: Boolean = False;
  SaidaLigada: Boolean = False;

procedure Linha(const s: string = '');
begin
  if not SaidaResolvida then
  begin
    SaidaResolvida := True;
    {$IFDEF WINDOWS}
    SaidaLigada := AttachConsole(ATTACH_PARENT_PROCESS);
    if SaidaLigada then
    begin
      IsConsole := True;
      SysInitStdIO;
    end;
    {$ELSE}
    SaidaLigada := True;
    {$ENDIF}
  end;
  if not SaidaLigada then
    Exit;
  // A checagem de I/O desligada fecha o ultimo buraco: console anexado que
  // morre no meio da impressao (terminal fechado) devolveria o mesmo dialogo.
  // Aqui vira codigo de erro, a saida se desliga, e o programa segue.
  {$I-}
  WriteLn(s);
  Flush(Output);
  {$I+}
  if IOResult <> 0 then
    SaidaLigada := False;
end;

procedure Ajuda;
var
  i: Integer;
begin
  Linha('wte -- a casca da fase 2 (WTE-TASK-11). Nenhum acesso a imagem de CD.');
  Linha;
  Linha('  wte                   abre o MainForm');
  Linha('  wte --list            lista os nomes e sai');
  Linha('  wte --help            isto');
  Linha('  wte <imagem.bin>      guarda o caminho e registra no trace;');
  Linha('                        NAO le a imagem -- ver a WTE-TASK-25');
  Linha;
  Linha('O trace vai para wte/re/trace.log, ou para $WTE_TRACE_FILE.');
  Linha;
  Linha('Formularios, na ordem de criacao medida no original:');
  for i := 0 to Screen.FormCount - 1 do
    Linha('  ' + Screen.Forms[i].Name + ' : ' + Screen.Forms[i].ClassName);
end;

function TrataLinhaDeComando: Boolean;
var
  i, k: Integer;
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
        Linha(Screen.Forms[k].Name);
      Exit(False);
    end
    else if Copy(ParamStr(i), 1, 1) = '-' then
      raise Exception.CreateFmt('argumento desconhecido: %s (veja --help)',
        [ParamStr(i)])
    else
    begin
      // Argumento POSICIONAL: o caminho da imagem. So se guarda e se registra
      // -- ler e trabalho de handler, e handler tem gate proprio. Opcao
      // desconhecida (comecando por `-`) continua sendo erro: engolir `--sho`
      // em silencio faria a captura da WTE-TASK-12 sair do formulario errado.
      if ImagemPedida <> '' then
        raise Exception.Create('so uma imagem por vez');
      ImagemPedida := ParamStr(i);
      REMark('imagem: ' + ImagemPedida);
    end;
    Inc(i);
  end;
end;

end.
