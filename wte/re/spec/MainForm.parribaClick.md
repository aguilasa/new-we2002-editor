---
handler: parribaClick
formulario: MainForm
endereco: 0x0040e998
veredito: aberto
---

# MainForm.parribaClick

A seta para cima: põe o jogador selecionado no lado esquerdo na linha
selecionada da **lista de descarte**. **807 bytes**, e a maior parte deles é
montagem de cadeia.

**É o único handler deste lote que não grava na imagem**, e por isso o único
que fecha sem depender da WTE-TASK-27.

## Entrada

- `lista_descarte.ItemIndex` (campo `+0x3a8`, um `TListBox`) — a linha de
  destino, e também **o índice do buffer**: `ItemIndex + 3`.
- `lista_equipos_1.ItemIndex` e `lista_jugadores_1.ItemIndex` — o jogador.
- `lista_jugadores_1.Items[ItemIndex]` — de onde o nome é recortado.
- O arquivo aberto (`0x00432e58`), que a rotina de carga usa.

**Evidência:** disassembly lido

## Saída

```text
linha := lista_descarte.ItemIndex
0x004046e8(lista_equipos_1.ItemIndex, lista_jugadores_1.ItemIndex,
           buffer := linha + 3, arquivo)

origem := 4; se lista_jugadores_1.ItemIndex < 9: origem := 5
nome := Copy(lista_jugadores_1.Items[lista_jugadores_1.ItemIndex], origem, 10)

se linha < 9: legenda := '  ' + (linha+1) + ' ' + nome
senao:        legenda :=        (linha+1) + ' ' + nome

lista_descarte.Items[linha] := legenda      ' TStrings VMT +0x20 = Put
lista_descarte.Update                       ' VMT +0x88
lista_descarte.ItemIndex := linha           ' VMT +0xcc
BYTE[0x00434640 + linha] := 1
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum gravado.** Ele lê a imagem através da `0x004046e8` e não chama a
`0x00404820`.

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se há linha selecionada na lista de descarte, não
confere se há jogador selecionado. Com `ItemIndex = -1` o buffer seria o `2` — o
lado direito — e a legenda iria para `Items[-1]`.

O port acrescenta a faixa (`0..22` na lista de descarte, `>= 0` nos dois
combos). Divergência de robustez, registrada nas Notas.

**Evidência:** disassembly lido

## Comportamento de erro

**Não trata**, e não tem o que tratar: não grava e não valida.

**Evidência:** disassembly lido

## Notas

### O `* 10000` não é preço — é a escala do `Currency`

O corpo multiplica `linha + 1` por **10.000** com o `__llmul` da RTL
(`0x0041978c`, cujo miolo é quatro `mul` de 32 bits — multiplicação, não
divisão) e converte o resultado com `SysUtils::CurrToStr` (`0x00422402`,
resolvido pelo nome importado no thunk).

**10.000 é exatamente a escala do tipo `Currency` da Borland**, que é um inteiro
de 64 bits dividido por 10.000 na apresentação. A conta não produz `10000`:
produz `'1'`. Lida como aritmética inteira, ela pareceria um preço de
transferência — e num editor que tem preço de jogador como funcionalidade
([WTE-TASK-30](../../../docs/tasks/30-preco-do-jogador.md)) essa leitura errada
teria sobrevivido a uma revisão.

O que confirma a leitura certa é o próprio `.dfm`: `lista_descarte` nasce com as
23 linhas `'  1 ...'` a `'23 ...'`, que é exatamente o que as duas larguras de
legenda produzem.

### O índice de buffer sai daqui, e ele explica o ramo `> 2` do `0x00404374`

`linha + 3` dá 23 buffers além dos três já conhecidos — um por linha da lista de
descarte. A oitava passagem da
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md) tinha visto o ramo
`indice > 2` daquela rotina (`+0x16 := 0xff`, `+0x19 := 3`) sem saber de quem
era: é deste handler. O `0xff` não é índice de time válido, então um jogador
vindo do descarte **nunca** bate identidade com o destino — a recusa `-2` não
alcança esse caminho.

### O recorte do nome é o mesmo do `dorsalClick`

`Copy(item, 4 ou 5, 10)`, com a origem dependendo de o índice ter um ou dois
dígitos. O original repete essa conta nos dois handlers; o port a fatorou na
`NomeDoItemSelecionado` do
[`.aux.inc`](../../src/impl/ep2002_mainform.aux.inc) e deixou o `dorsalClick`
como estava — a spec daquele já está fechada e reabri-la não mediria nada.

### Veredito `aberto`, e a razão é outra que a dos irmãos

Os demais handlers de mover estão `aberto` porque falta a gravação, que é da
WTE-TASK-27. **Este não grava**, então a metade que falta nele é só a régua:
o `compara_tela.sh --edicao` não foi estendido à lista de descarte. Exercitá-la
exige selecionar time nos dois lados, jogador na esquerda e linha na lista —
quatro cliques cuja coordenada precisa da varredura que cada grupo novo custa
(risco 3 do plano de fechamento da
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md)).

Marcar `implementado` sem ela seria dizer que a régua da task passou quando ela
não rodou — e o veredito passaria a medir quanta leitura foi feita, não o estado
do handler. O comportamento está medido e escrito, o Pascal está em
[`../../src/impl/ep2002_mainform.parribaClick.inc`](../../src/impl/ep2002_mainform.parribaClick.inc),
e o gate de tela fica para quando o `--edicao` alcançar este grupo — junto com o
`pabajoClick`, que é a outra metade da lista de descarte.

**Divergência deliberada do port**
([WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md)): índice fora
da faixa sai sem fazer nada, em vez de escrever em `Items[-1]` e carregar o
buffer errado.
