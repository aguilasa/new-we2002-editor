---
handler: FormShow
formulario: MainForm
endereco: 0x004111d8
veredito: aberto
---

# MainForm.FormShow

## Entrada

`data/dat.bin`, montado como `<diretório corrente>` + `\dat.bin` — o
diretório vem de um global em `0x00432e80`, que o `GetCurrentDir()` do
arranque preenche.

No port, a entrada extra é o argumento posicional da linha de comando (o
caminho da imagem), que existe no `wtemain.pas` desde a WTE-TASK-11.

**Evidência:** disassembly lido

## Saída

Abre o `dat.bin` e guarda o `FILE*` num global (`0x00432e68`), aberto pela
sessão inteira. Passa pelo mesmo trecho de injeção de setores do
`boton_dialogo_weClick` — o `.exe` tem os dois trechos duplicados.

Escreve três vezes a cor `$00ffb676` — RGB(118, 182, 255). É a "cor de fundo
posta em tempo de execução" que a fase 2 deixou pendente, e **os três alvos
estão medidos**: o próprio `MainForm` (`ds:0x434360`, em `0x00411738`), o campo
`0x2f4` = `cuadro_dialogo_we` (`0x00411771`) e o campo `0x30c` = `grupo_barras`
(`0x004117ab`), pelo [`../campos.tsv`](../campos.tsv).

O original chega ao valor por texto: monta a cadeia `$00ffb676`, passa pelo
`Graphics::StringToColor` e só então chama `SetColor`. Era a forma de o
C++Builder escrever literal de cor, não comportamento — o port atribui o valor
direto.

Conta os **blocos livres de Master League** e mostra o número no
`casilla_xmlibres`: `call 0x004042d4` em `0x004116df`, e na instrução seguinte
`IntToStr(WORD[0x004335c0])` para o campo `+0x434`. A conta está medida em
[`../ml-slots.md`](../ml-slots.md); no port é a `AtualizaBlocosLivresDeMl`.

**Evidência:** disassembly lido

## Bytes tocados

Na imagem: os mesmos sete setores do
[`boton_dialogo_weClick`](MainForm.boton_dialogo_weClick.md), quando há imagem
aberta. No arranque sem imagem, **nenhum**.

**Evidência:** diff medido

## Pré-condições

`data/dat.bin` tem de existir. Se não existir, o original mostra `The file
"dat.bin" must be in the "data" directory` (`0x004250bd`) e **encerra** — é
pré-condição de arranque, não aviso.

**Evidência:** disassembly lido

## Comportamento de erro

O original encerra. O port **não encerra**: escreve a falta no
`texto_dialogo_we` e segue. Encerrar dentro do `OnShow` levaria a janela embora
antes de o harness do gate poder dirigi-la, e o diagnóstico seria "a janela não
apareceu" — que manda procurar no lugar errado.

É divergência deliberada, e vai para a
[WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md).

**Evidência:** observacao de tela

## Notas

A resolução do caminho do `dat.bin` diverge de propósito: o original depende do
diretório corrente, e reproduzir isso seria reproduzir um defeito de
empacotamento. O port procura `$WTE_ASSETS_DIR`, depois ao lado do executável.
A resolução definitiva é da [WTE-TASK-39](../../../docs/tasks/39-empacotamento.md).

**Veredito ainda `aberto`**: os três alvos de `$00ffb676` já estão medidos e
implementados, mas falta a carga da tela — popular `lista_equipos` e o resto do
`MainForm` a partir do banco, que é o que sobra da
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md).
