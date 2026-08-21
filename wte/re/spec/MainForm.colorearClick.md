---
handler: colorearClick
formulario: MainForm
endereco: 0x00410ea8
veredito: divergencia deliberada
---

# MainForm.colorearClick

Abre o editor de cor 2D. 249 bytes: quatro coisas antes do modal e duas depois.

**Evidência:** disassembly lido

## Entrada

- `lista_equipos_1.ItemIndex` (`[this+0x390]`), o time cuja paleta será editada;
- `ficha_color.lista_col1.ItemIndex` (`[0x00433dbc]+0x398`), qual jogo de
  uniforme redesenhar;
- dois bytes por time em `0x004331d6` e `0x004331d7`, que escolhem o item do
  `lista_col3` — ver as Notas;
- `lista_equipos_2.ItemIndex` e `lista_equipos.ItemIndex`, no fim, para decidir
  se a segunda bandeirinha também é copiada.

**Evidência:** disassembly lido

## Saída

```text
se [0x4331d6] <> 0:              ficha_color.lista_col3.ItemIndex := 1
senao se [0x4331d7] = 0x65:      ficha_color.lista_col3.ItemIndex := 0
senao:                           ficha_color.lista_col3.ItemIndex := 2

0x004335cc := lista_equipos_1.ItemIndex
0x00405d6c()                     ' enche as 16 amostras
0x004056c8([0x4335cc], ficha_color.lista_col1.ItemIndex)   ' redesenha o uniforme
ficha_color.ShowModal

banderita1.Picture := bandera.Picture
se lista_equipos_2.ItemIndex = lista_equipos.ItemIndex:
    banderita2.Picture := bandera.Picture
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não há I/O de arquivo no corpo — nem na imagem, nem em `.bmp`. O
que ele mexe é tela e os globais do editor.

**Evidência:** disassembly lido

## Pré-condições

`lista_equipos_1.ItemIndex >= 0`. O botão `colorear` só é habilitado pelo
`lista_equiposChange` quando o time é nacional (`.Enabled := nacional`), então
a condição já vale quando ele é clicável.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Sem time escolhido o botão está desabilitado.

**Evidência:** disassembly lido

## Notas

### O `xor edx,edx` do irmão **não** está aqui

O `lista_equiposChange` chama a mesma `0x004056c8` com o jogo zerado — ao trocar
de time o original desenha sempre o **Primeiro** uniforme. Este handler passa o
`ItemIndex` do combo do editor. Abrir o editor com o `Segundo` escolhido mantém
o Segundo na tela, e é a única diferença entre as duas chamadas.

### O índice do time é **copiado**, não relido

`0x004335cc` recebe o `ItemIndex` uma vez, ao abrir, e o resto do formulário lê
a cópia. Reler o combo daria o mesmo hoje; a cópia é o que o original escolheu, e
o port a reproduz em `TimeEmCor` (`wte/src/wte_cor.pas`).

### A divergência deliberada: o `lista_col3` fica no default

**Medido, e não portado.** O item do combo de padrão de camisa —
`NORMAL` / `ROMBOIDAL` / `EXTRA` — sai de dois bytes que o carregador de estado
lê da imagem para `0x004331d6` e `0x004331d7` (`0x0040517a`, dois bytes a partir
do offset em `0x00433220`). **Esses dois bytes não estão na camada de dados:**
nem `TTeam` nem `TMlTeam` do `we2002_core` têm campo de padrão de camisa, e o
`we2002_core` é o oráculo de formato deste projeto.

Inventar de onde eles saem seria pior do que deixar o combo no default do
formulário, então o port não escreve o `ItemIndex`. É divergência de **tela**,
não de dado: nenhum byte de imagem depende dela, e o `lista_col3` não alimenta
nenhuma das duas famílias de paleta que a
[WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md) porta.

Entrada para a
[WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md).

### O gate

`compara_tela.sh --cor`, que abre o editor dos dois lados e compara as **16
amostras** pixel a pixel. Times 2, 9 e 63: zero divergência, com 8 a 11 cores
distintas em cada — a contagem existe para que "todas iguais" não passe por
verde. O `lista_col3` fica fora do recorte medido, pela razão acima.
