---
handler: mostrar_jugadorClick
formulario: MainForm
endereco: 0x0040f8d4
veredito: aberto
---

# MainForm.mostrar_jugadorClick

Abre a ficha do jogador selecionado. **2.378 bytes** — o maior handler do
grupo de carga, e o segundo maior do `MainForm` depois do
[`lista_equiposChange`](MainForm.lista_equiposChange.md).

Ligado a **dois** botões, `mostrar_jugador_1` e `mostrar_jugador_2`: o do time
titular e o do reserva.

## Entrada

- **`Sender.Name`**, e essa é a parte que a leitura apressada erraria. O
  original **não** compara o ponteiro do `Sender` com o do botão: ele lê o
  campo `Name` do componente (deslocamento `0x08` do `TComponent`, o mesmo que
  o [`sonda_dorsal.py`](../../tools/sonda_dorsal.py) confere) e o compara com a
  cadeia `'mostrar_jugador_1'` em `0x00424f57`. Igual → lado titular; diferente
  → reserva.
- do lado titular, `lista_equipos_1.ItemIndex` e `lista_jugadores_1.ItemIndex`;
  do reserva, `lista_equipos_2` e `lista_jugadores_2`.

**Evidência:** disassembly lido

## Saída

```text
titular := Sender.Name = 'mostrar_jugador_1'
guarda o time e o jogador escolhidos em globais (0x004335dc e vizinhas)
0x00403f00(...)   ' 328 B -- o numero de camisa
0x004046e8(...)   ' 164 B -- nao lida
0x00404820(...)   ' 1.459 B -- enche a ficha
0x0040756c(...)   ' 1.275 B -- enche a ficha
jugador.ShowModal
```

O `ficha_enlaza` também é alcançado — é o diálogo de confirmação de vínculo,
que aparece quando o jogador escolhido é de clube de Master League.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum gravado.** Lê a imagem através de `0x00403f00` e das duas rotinas de
preenchimento. Que faixas exatamente, não foi medido — e não precisa ser aqui:
ver as Notas.

**Evidência:** nao medido

## Pré-condições

Não confere seleção. Com `ItemIndex = -1` nas listas o índice calculado sai
negativo e segue.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**O escopo aqui é navegação, e o resto tem dono.** Das 2.378 instruções, o que
a WTE-TASK-25 deve é *abrir a ficha* — escolher o par de listas certo pelo
`Sender.Name`, guardar a seleção e mostrar o formulário. **Encher a ficha**
(`0x00404820` e `0x0040756c`, 2.734 bytes) é editar jogador, e isso é a
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md), dona do formulário
`jugador`.

A divisão foi decidida em 2026-08-11 e está no enunciado da
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md). Sem ela, o critério
"remover o andaime `--show` com a navegação real no lugar" arrastaria 2,7 KB de
disassembly de outra fase.

**Veredito `aberto` porque metade tem dono fora.** O Pascal da navegação está
escrito em
[`../../src/impl/ep2002_mainform.mostrar_jugadorClick.inc`](../../src/impl/ep2002_mainform.mostrar_jugadorClick.inc);
a ficha abre com o estado que a 26 vai preencher.
