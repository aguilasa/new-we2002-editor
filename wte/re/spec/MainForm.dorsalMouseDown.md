---
handler: dorsalMouseDown
formulario: MainForm
endereco: 0x00410ddc
veredito: implementado
---

# MainForm.dorsalMouseDown

O botão **direito** sobre um número de camisa abre a ficha do jogador. 203
bytes, um corpo para os 23 rótulos — os mesmos que o
[`dorsalClick`](MainForm.dorsalClick.md) atende com o botão esquerdo.

## Entrada

- `lista_equipos.ItemIndex` — se `< 0`, sai.
- **`Button`**, e só `mbRight` passa. No `TMouseButton` da VCL isso é o valor
  **1** (`mbLeft = 0`, `mbRight = 1`, `mbMiddle = 2`); a LCL declara a mesma
  ordem, então comparar por nome vale nos dois.
- `Sender.Name` e `0x004335e4`, exatamente como no `dorsalClick`.

**Evidência:** disassembly lido

## Saída

```text
se lista_equipos.ItemIndex < 0: sai
se Button <> mbRight: sai

se Sender <> camisa_marcada:
    numero := StrToInt(Copy(Sender.Name, 7, 2))
    lista_jugadores_1.ItemIndex := numero - 1
    0x0040b188(numero)                  ' MarcaCamisa

0x0040f8d4(mostrar_jugador_1)           ' mostrar_jugadorClick, LADO TITULAR
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum diretamente.** O que ele chama —
[`mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md) — lê a imagem para
encher a ficha, e não grava.

**Evidência:** disassembly lido

## Pré-condições

`lista_equipos.ItemIndex >= 0` e botão direito. Nada mais.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata, pelas mesmas razões do `dorsalClick`.

**Evidência:** disassembly lido

## Notas

**O bloco de seleção é letra por letra o do `dorsalClick`** — mesmo
`Copy(Name, 7, 2)`, mesmo `ItemIndex := numero - 1`, mesma chamada de realce. O
original repete o código em vez de chamar uma rotina comum, e o port **repete
também**, em vez de fatorar. Fatorar mudaria a ordem de execução no dia em que
um dos dois ganhasse uma linha, e a fidelidade é o critério; é a mesma decisão
que a WTE-TASK-25 tomou nos handlers indexados.

**Ele chama o handler irmão passando um controle como `Sender`**, e o controle
importa: `mostrar_jugador_1`, o botão do time **titular**. É o que faz o
`LadoTitular` do `mostrar_jugadorClick` devolver verdadeiro — aquele handler
decide o lado comparando `Sender.Name` com a cadeia `'mostrar_jugador_1'`, e
não por ponteiro. Passar o botão reserva abriria a ficha do outro time.

**Veredito `implementado`:** o corpo está completo — ao contrário do
`dorsalClick`, este não grava nada, então não sobra metade para a WTE-TASK-27.
O que ele produz na tela é a ficha do jogador aberta, que é a mesma saída já
coberta pela spec do `mostrar_jugadorClick`.

Pascal em
[`../../src/impl/ep2002_mainform.dorsalMouseDown.inc`](../../src/impl/ep2002_mainform.dorsalMouseDown.inc).
