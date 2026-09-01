---
handler: barrhabScroll
formulario: jugador
endereco: 0x00407a88
veredito: implementado
---

# jugador.barrhabScroll

Arrastar uma das barras de habilidade da ficha do jogador. **300 bytes** — e o
[`barrhab_bisScroll`](jugador.barrhab_bisScroll.md) ao lado tem os mesmos 300 e
o mesmo conjunto de chamadas.

## Entrada

- **`Sender.Name`**, e é só dele que sai o índice: `Copy(Name, 8, 1)`. O
  original lê o campo `FName` do `TComponent` (deslocamento `0x08`, o mesmo que
  o [`sonda_dorsal.py`](../../tools/sonda_dorsal.py) confere) — não o `Tag`,
  não o ponteiro.
- `ScrollPos`, o terceiro argumento do `OnScroll`, por referência.

**Evidência:** disassembly lido

## Saída

```text
digitos := Copy(Sender.Name, 8, 1)
imghab<digitos>.Width := 7 * ScrollPos + 8         ' TControl::SetWidth
valorhab<digitos>.Caption := IntToStr(ScrollPos + 12)
0x00406fb4(ScrollPos)     ' fonte amarela se >= 5, branca abaixo
```

Os dois controles são achados por `FindComponent` sobre o nome montado, como no
resto da ficha. O rótulo alvo fica guardado na global `0x00433e48`, que é a
mesma que a rotina de cor consome.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum**, e isto foi conferido pelo inventário de chamadas **antes** de o
Pascal ser escrito: os 300 bytes alcançam `FindComponent`, `IntToStr`, `Copy`,
`TControl::SetText`, `TControl::SetWidth` e a rotina de cor `0x00406fb4` — e
nenhuma escritora de imagem (`0x00403400`, `0x00404048`, `0x00404820`).

É o único lote desta task que fecha sem depender da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se o nome tem dígito, não confere faixa. O port
acrescenta o teste de `Sender is TComponent` e sai com nome vazio — divergência
de robustez, como nos demais.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. `FindComponent` devolvendo `nil` seria desreferenciado pelo original;
o port apenas não atualiza.

**Evidência:** disassembly lido

## Notas

### Os dois handlers são o mesmo código com um número diferente

`barrhabScroll` faz `Copy(Sender.Name, 8, 1)` e `barrhab_bisScroll` faz
`Copy(Sender.Name, 8, 2)`. `barrhab` tem sete caracteres, então a posição 8 é o
primeiro dígito: um serve `barrhab1..9` e o outro `barrhab10..16`.

**Não é outra família de controles — é a largura do número.** O `.lfm` tem
exatamente 16 `barrhab`, numerados de 1 a 16, e nenhum `barrhab_bis`. O autor
duplicou o corpo em vez de contar dígitos, e o `_bis` do nome é só isso. Ler o
par como "as barras normais e as outras" mandaria procurar um segundo grupo de
controles que não existe.

### `TScrollBar.Position :=` dispara `OnChange` na LCL, e isso importa aqui

Medido pelo [`check_lcl_combo.py`](../../tools/check_lcl_combo.py), que passou a
cobrir os dois controles da ficha: **`TScrollBar` dispara** (e só quando o valor
muda de verdade), **`TUpDown` não**. É a mesma resposta que o `TTrackBar` deu na
segunda passagem da [WTE-TASK-26](../../../docs/tasks/concluidos/26-handlers-de-edicao.md),
e a oposta à do `TComboBox`.

Consequência: o `PreencheFicha` reentra neste handler dezesseis vezes ao encher
a ficha, e cada reentrada reescreve rótulo, largura e cor **com o mesmo valor**.
A tela não muda; uma contagem de disparos no trace, sim — e é isso que qualquer
gate de trace sobre a ficha tem de esperar.

### Veredito `implementado`

Régua do grupo de edição: tela depois de editar. O efeito inteiro deste handler
**é** tela, ele não grava, e a parte que uma régua de pixel julgaria — a largura
de `7*v + 8` — foi medida na décima quinta passagem na única linha em que o
`TScrollBar` do gtk2 não a cobre: **8 px para valor cru 0**, exatamente a
fórmula.

O que sustenta a ordem dos dezesseis não é pixel e sim o
[`check_bitfields.py`](../../tools/check_bitfields.py), que exige que a posição
`n` use o campo que o descritor `n-1` descreve. Aqui o índice vem do nome do
componente, que é o mesmo nome que aquele check ancora.

Pascal em
[`../../src/impl/ep2002_jugador.barrhabScroll.inc`](../../src/impl/ep2002_jugador.barrhabScroll.inc)
e o corpo compartilhado no
[`.aux.inc`](../../src/impl/ep2002_jugador.aux.inc).
