---
handler: FormShow
formulario: MainForm
endereco: 0x004111d8
veredito: divergencia deliberada
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
[WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md).

**Evidência:** observacao de tela

## Notas

A resolução do caminho do `dat.bin` diverge de propósito: o original depende do
diretório corrente, e reproduzir isso seria reproduzir um defeito de
empacotamento. O port procura `$WTE_ASSETS_DIR`, depois ao lado do executável.
A resolução definitiva é da [WTE-TASK-39](../../../docs/tasks/concluidos/39-empacotamento.md).

## O veredito, e por que ele não é `implementado`

**Passou de `aberto` a `divergencia deliberada` em 2026-08-23**, terceira
passagem da [WTE-TASK-31](../../../docs/tasks/concluidos/31-fechamento-fase-4.md).

O que segurava o `aberto` era *"falta a carga da tela — popular `lista_equipos`
e o resto do `MainForm` a partir do banco"*. **Ela não falta mais**, e a régua
mediu isso no dia: `bash wte/tools/compara_tela.sh 2 68` sobe o port pela linha
de comando, que é este handler carregando a imagem, e compara a tela resultante
com a do oráculo — 5 de 5 barras em pixel nos dois times, 0 de 8.960 px e 0 de
9.800 px em bandeira e uniforme, tolerância zero. Os sete setores que ele
injeta seguem verdes no
[`golden-01-arranque`](../../tests/roteiros/golden-01-arranque.txt), controle e
golden.

**`implementado` seria o veredito errado**, e por duas divergências que estão
escritas acima e são de propósito:

1. **falta do `dat.bin`** — o original encerra, o port escreve a falta no
   `texto_dialogo_we` e segue, para a janela não sumir antes de o gate poder
   dirigi-la;
2. **resolução do caminho do `dat.bin`** — o original depende do diretório
   corrente; o port procura `$WTE_ASSETS_DIR` e depois o lado do executável.

As duas são entrada da
[WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md), e é o
vocabulário do [gabarito](GABARITO.md) que manda: handler portado com desvio
consciente é `divergencia deliberada`, não `implementado` com ressalva no meio
da prosa — a ressalva no meio da prosa é o que não se lê de um índice.
