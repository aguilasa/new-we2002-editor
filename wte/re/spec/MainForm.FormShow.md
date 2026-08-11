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

Escreve três vezes a cor `$00ffb676` (literais em `0x004250f6`, `0x00425100`,
`0x0042510a`). É a "cor de fundo posta em tempo de execução" que a fase 2
deixou pendente; **quais controles a recebem ainda não foi medido.**

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

**Veredito ainda `aberto`**: falta medir quais controles recebem `$00ffb676`, e
falta a carga da tela.
