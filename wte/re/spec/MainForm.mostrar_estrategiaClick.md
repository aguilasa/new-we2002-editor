---
handler: mostrar_estrategiaClick
formulario: MainForm
endereco: 0x00410220
veredito: aberto
---

# MainForm.mostrar_estrategiaClick

Abre a tela de tática do time selecionado. 1.446 bytes, e o mesmo par de
botões do irmão: `mostrar_estrategia_1` e `mostrar_estrategia_2`.

## Entrada

- **`Sender.Name`**, comparado com a cadeia `'mostrar_estrategia_1'` em
  `0x00425001` — o mesmo mecanismo do
  [`mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md), e pela mesma
  razão: um corpo servindo dois botões;
- a lista de times do lado escolhido.

**Evidência:** disassembly lido

## Saída

```text
titular := Sender.Name = 'mostrar_estrategia_1'
guarda o time escolhido em global (0x004335cc)
0x0040a0b4(...)   ' 1.443 B -- enche a tela de tatica; nao lida
estrategia.ShowModal
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum gravado.** A leitura acontece dentro de `0x0040a0b4`, não medida.

**Evidência:** nao medido

## Pré-condições

Não confere seleção.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**Mesma divisão do irmão:** navegação é da WTE-TASK-25, encher a tela
(`0x0040a0b4`) é da
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md), dona do formulário
`estrategia`.

**`ShowModal` é chamada virtual, e é por isso que ela não aparece numa busca
por chamada direta.** O símbolo `TCustomForm::ShowModal` é importado do
`vcl60.bpl` e tem thunk em `0x004226de`, e a `.text` inteira tem **zero**
`call rel32` para ele — o `.exe` chama pelo VMT, `mov edx,[eax]` seguido de
`call [edx+<slot>]`, como faz com quase todo método virtual. Vale registrar
porque é a mesma forma da dúvida aberta sobre `SetEnabled` na spec do
[`lista_equiposChange`](MainForm.lista_equiposChange.md) — **com a diferença
de que `ShowModal` é virtual e `SetEnabled` não é**, então a explicação que
serve aqui não serve lá.

**Veredito `aberto` porque metade tem dono fora.** O Pascal da navegação está
em
[`../../src/impl/ep2002_mainform.mostrar_estrategiaClick.inc`](../../src/impl/ep2002_mainform.mostrar_estrategiaClick.inc).
