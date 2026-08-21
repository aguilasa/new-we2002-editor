{ MainForm.FormCreate -- 0x004107c8. Spec: wte/re/spec/MainForm.FormCreate.md

  Forma `composto` do `wte/re/arranque.md`, 683 bytes, e o que ele faz e uma
  coisa so: montar as SEIS pastas de asset. `GetCurrentDir()`, depois
  `<cwd>\image`, e dali `\barba`, `\pelo`, `\banderas`, `\uniformes2d`; `\data`
  pendura na raiz, nao em `image`. Os seis literais estao em
  0x00425046..0x00425071 e sao consumidos nessa ordem -- medido na WTE-TASK-08
  (`wte/re/assets.md` secao 2) e reconfirmado pelo `arranque.md`.

  A raiz diverge de proposito: ver `ResolveDiretorios` em `we2002_estado.pas`.

  E AS TRES ULTIMAS INSTRUCOES PASSARAM A TER EFEITO. Elas guardam os ponteiros
  de `bandera`, `home1` e `home2` em globais (0x00432ebc..0x00432ec4) -- cache
  de tres `TImage` para o desenho 2D --, e ate a quinta passagem da
  WTE-TASK-29 a spec as classificava como detalhe de implementacao em C++ sem
  efeito observavel, porque em Pascal os tres se alcancam pelo campo do
  formulario. **Isso valia enquanto so o proprio `MainForm` desenhava.** Os
  handlers do `ficha_color` tambem redesenham, e dali os campos nao se
  alcancam: `ep2002_mainform` ja usa `ep2002_color`, entao a volta fecharia
  ciclo de `uses` de interface. As globais do original sao exatamente a
  indirecao que resolve isso, e agora o port as tem -- em
  `wte_render2d.RegistraImagensDoEditor`. }
begin
  REMark('MainForm.FormCreate');
  ResolveDiretorios;
  RegistraImagensDoEditor(bandera, home1, home2);
end;
