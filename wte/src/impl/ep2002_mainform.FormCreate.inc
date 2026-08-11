{ MainForm.FormCreate -- 0x004107c8. Spec: wte/re/spec/MainForm.FormCreate.md

  Forma `composto` do `wte/re/arranque.md`, 683 bytes, e o que ele faz e uma
  coisa so: montar as SEIS pastas de asset. `GetCurrentDir()`, depois
  `<cwd>\image`, e dali `\barba`, `\pelo`, `\banderas`, `\uniformes2d`; `\data`
  pendura na raiz, nao em `image`. Os seis literais estao em
  0x00425046..0x00425071 e sao consumidos nessa ordem -- medido na WTE-TASK-08
  (`wte/re/assets.md` secao 2) e reconfirmado pelo `arranque.md`.

  A raiz diverge de proposito: ver `ResolveDiretorios` em `we2002_estado.pas`.

  O que NAO se reproduz: as tres ultimas instrucoes do original guardam os
  ponteiros de `bandera`, `home1` e `home2` em globais (0x00432ebc..0x00432ec4)
  -- cache de tres `TImage` para o desenho 2D. E detalhe de implementacao em
  C++ sem efeito observavel: em Pascal os tres se alcancam pelo proprio campo
  do formulario. Registrado na spec. }
begin
  REMark('MainForm.FormCreate');
  ResolveDiretorios;
end;
