{ estrategia.FormCreate -- 0x004090fc, 1351 bytes.
  Spec: wte/re/spec/estrategia.FormCreate.md

  O MAIOR DOS 18 `FormCreate`, e a maior parte dele NAO tem equivalente aqui --
  de proposito, e essa e a coisa a entender antes de mexer. Ele monta em tempo
  de execucao duas tabelas que neste port sao GERADAS:

  - a tabela de zonas em `0x00433e5c`, 11 registros de 16 bytes escritos como
    imediatos entre `0x00409168` e `0x0040930b` -> `wte_zonas.pas`, gerado pelo
    `tools/dump_zonas.py`;
  - a tabela de formacoes em `0x00433f0c`, 18 registros de 44 bytes ->
    `wte_formacoes.pas`, gerado pelo `tools/dump_formacoes.py`.

  A SEGUNDA ERA A PERGUNTA ABERTA DA SPEC, e ela fechou por disassembly na
  CORR-WTE-093. Os "quatro lacos de 11 iteracoes" de `0x004092fe`..`0x00409344`
  copiam 11 bytes cada para `esi+0`, `esi+0x0b`, `esi+0x16` e `esi+0x21` -- ou
  seja, quatro colunas de 11 intercaladas num registro de 44 --, e o laco de
  fora (`0x00409355`) avanca `esi` de `0x2c` e para em `0x12`:

      add esi,0x2c ; cmp DWORD PTR [ebp-0x5c],0x12 ; jl

  18 registros de 44 bytes. E exatamente a tabela que o `dump_formacoes.py`
  extrai dos quatro blobs de `.data` (`0x00423be4`, `0x00423cb0`, `0x00423d7c`,
  `0x00423e48`), que sao as quatro copias de 51 dwords que a spec ja listava
  sem saber quem as lia. Reproduzir os lacos daria a MESMA tabela que ja esta
  em `wte_formacoes.pas`, so que montada a mao.

  O QUE SOBRA, e o que este corpo faz:

  1. `Color := $00E68F41` (`0x00409361`);
  2. a zebra dos onze trios `etiqestr`/`jugador`/`etiqpos`;
  3. semear os dois ponteiros de foco;
  4. a cor e o item inicial da `lista_formaciones`.

  A ZEBRA E POR SUFIXO IMPAR, e o teste do original e o mesmo do
  `jugador.FormCreate`: `and eax,0x80000001` em `0x00409378` sobre o contador
  que vai de 0 a 10 (`cmp DWORD PTR [ebp-0x5c],0xb` em `0x004095e2`), com o
  sufixo do nome sendo contador + 1. Contador PAR -> `$00D78228` (os tres
  literais em `0x00424b66`/`0x424b6f`/`0x424b77`); IMPAR -> `$00E68F41` (os
  mesmos tres textos repetidos em `0x00424b7f`/`0x424b88`/`0x424b90`, porque
  sao dois ramos de codigo distintos). Sufixo 1 e par-de-contador, entao sufixo
  IMPAR fica com `$00D78228`.

  O SLOT `0xcc` FOI MEDIDO, nao adivinhado. O fim da rotina faz
  `call DWORD PTR [ecx+0xcc]` com `edx=1` sobre a `lista_formaciones`
  (`+0x318` no `campos.tsv`). Lendo o VMT de `TListBox` no `vcl60.bpl`, o slot
  `0xcc` guarda `@Stdctrls@TCustomListBox@SetItemIndex$qqrxi` -- e o
  `ItemIndex := 1`, o mesmo `FORMACAO_DEFAULT` que o `wte_tatica` ja declara.

  NAO GRAVA NADA. So `SetColor`, `FindComponent` e `SetItemIndex`. }
var
  i: Integer;
  cor: TColor;

  procedure Pinta(const prefixo: string; n: Integer);
  var
    c: TComponent;
  begin
    c := FindComponent(prefixo + IntToStr(n));
    if c is TLabel then
      TLabel(c).Color := cor;
  end;

begin
  REMark('estrategia.FormCreate');
  Color := $00E68F41;

  { O contador do original vai de 0 a 10 e o sufixo e contador + 1. }
  for i := 0 to 10 do
  begin
    if Odd(i) then
      cor := $00E68F41
    else
      cor := $00D78228;
    Pinta('etiqestr', i + 1);
    Pinta('jugador', i + 1);
    Pinta('etiqpos', i + 1);
  end;

  { `0x00434340` e `0x00434344`, semeados com a bola e o rotulo zero. }
  BolaEmFoco := bola0;
  EtiquetaEmFoco := etiqjug0;

  lista_formaciones.Color := $00414B41;
  lista_formaciones.ItemIndex := FORMACAO_DEFAULT;
end;
