---
handler: grabar_camisetaClick
formulario: MainForm
endereco: 0x0040ee80
veredito: implementado
---

# MainForm.grabar_camisetaClick

**Extrai** o uniforme 3D do time selecionado para um arquivo. 656 bytes, sem
rotina auxiliar: o diálogo, a recusa e a cópia estão todos no corpo.

**Ele é o inverso exato do
[`boton_tex2isoClick`](MainForm.boton_tex2isoClick.md).** Aquele escreve vinte
setores na imagem a partir de um arquivo; este lê da mesma região e emite um
arquivo. Os dois calculam o endereço com a **mesma expressão**, literal a
literal — o que muda é a direção e o tamanho.

**Evidência:** disassembly lido

> **O enunciado da [WTE-TASK-29](../../../docs/tasks/concluidos/29-camisa-e-bandeira-2d.md)
> dizia que ele grava na imagem, e não grava.** A ROM sai intacta: o único
> `fopen` de escrita é o do destino, em `"wb"`. Medido em 2026-08-20; a
> consequência é o formato do gate, ver o fim.

## Entrada

- `dialogo_grabar_camiseta` (`[this+0x3c0]`), o `TSaveDialog` do formulário;
- `dialogo_tex` (`[this+0x37c]`), o `TOpenDialog` da **importação** de textura —
  entra só como termo da recusa;
- `lista_equipos.ItemIndex` (`[this+0x2f0]`), que decide o time;
- a imagem aberta (`0x00432e58`), só para leitura.

**Evidência:** disassembly lido

## Saída

```text
repete:
    se nao dialogo_grabar_camiseta.Execute:  sai sem gravar e sem avisar
    destino := dialogo_grabar_camiseta.FileName
    se destino = dialogo_tex.FileName:
        ficha_error2.etiq1 := 'That file name is already being used by Team Editor'
        ficha_error2.ShowModal
        volta a repetir            <- reabre o dialogo, nao desiste
    senao: sai do laco

fopen(destino, "wb")
fseek(destino, 0, SEEK_SET)

offset = 19756824 + 47040 * (indice + 9 * (indice div 95))
fseek(imagem, offset, SEEK_SET)
inicio = ftell(imagem)

fseek(imagem, 44, SEEK_CUR)
tamanho = fgetc() + fgetc() * 256 + 32
fseek(imagem, inicio, SEEK_SET)

para i de 0 ate (tamanho shr 11) - 1:
    fread(buffer, 2048, 1, imagem)
    fwrite(buffer, 2048, 1, destino)
    fseek(imagem, 304, SEEK_CUR)

para i de 0 ate (tamanho and 0x7ff) - 1:
    fputc(fgetc(imagem), destino)

fclose(destino)
ficha_info3.etiq1 := 'O uni foi salvo!!!.     '
ficha_info3.ShowModal
```

**Evidência:** disassembly lido

## Bytes tocados

**Na imagem de CD: nenhum.** Ela é aberta para leitura e o ponteiro passeia por
ela; nenhum `fwrite` tem a imagem como destino. É por isso que o critério de
EDC/ECC da task não se aplica aqui, e é a segunda vez seguida que um critério
de EDC/ECC fecha por refutação — a primeira foi na
[WTE-TASK-28](../../../docs/tasks/concluidos/28-import-de-mcr.md).

No **arquivo de destino**, `tamanho` bytes, com

```text
tamanho = word_le(offset + 44) + 32
offset  = 19756824 + 47040 * (indice + 9 * (indice div 95))
```

Lidos da imagem em `tamanho div 2048` blocos de payload inteiro mais
`tamanho mod 2048` bytes soltos.

**Evidência:** disassembly lido

## Pré-condições

- imagem aberta — sem ela o `FILE*` global é nulo e não há de onde ler;
- `lista_equipos.ItemIndex >= 0`;
- o botão `grabar_camiseta` só é habilitado pelo `lista_equiposChange`
  (`0x0040d327`), então as duas de cima já valem quando ele é clicável.

**Evidência:** disassembly lido

## Comportamento de erro

- **Cancelar o diálogo:** sai sem gravar e **sem avisar**. É a porta silenciosa
  do laço;
- **Nome igual ao do `dialogo_tex`:** mostra `ficha_error2` e **reabre** o
  diálogo. Não desiste, não grava;
- **`fopen` do destino falhando:** o original não confere. O port sai calado,
  que é o mais próximo de não fazer nada.

**Evidência:** disassembly lido

## Notas

### O tamanho vem de DENTRO do bloco, e é a única parte que não é aritmética

Todo o resto do endereçamento é constante. O **tamanho** não: são dois bytes
lidos em `offset + 44`, em little-endian, mais 32.

```text
40f01c:  push 0x1 / push 0x2c / call fseek     ; +44, relativo
40f02e:  call fgetc                            ; byte baixo
40f03d:  call fgetc / shl eax,0x8              ; byte alto
40f058:  add edi,0x20                          ; +32
```

O `+ 32` diz que o campo conta o **corpo** e não o cabeçalho de 32 bytes que o
precede. Um port que somasse 0 emitiria um arquivo 32 bytes curto, e um que
lesse o campo como 32 bits leria lixo do byte 46 em diante — os dois erros
produzem arquivo plausível, com o tamanho errado.

### Os dois laços, e por que são dois

O primeiro copia **payload inteiro**: `fread` de 2048, `fwrite` de 2048,
`fseek(+304)`. O `2048 + 304 = 2352` é o setor MODE2/2352 completo, ou seja o
laço **salta** cabeçalho e EDC/ECC em vez de copiá-los — e é por isso que o
critério de EDC/ECC desta task não se aplica a este handler.

O segundo copia o **resto**, `tamanho mod 2048`, byte a byte com
`fputc(fgetc(...))`. Ele não tem `fseek` nenhum, e não precisa: o primeiro laço
deixou o ponteiro no começo do payload do setor seguinte, e o resto sempre cabe
lá — `tamanho mod 2048 < 2048`.

### A recusa é contra o `dialogo_tex`, não contra o de gravação

Mesma forma do
[`grabar_memoryClick`](MainForm.grabar_memoryClick.md), com o outro par de
diálogos: lá é o `.mcr` de importação, aqui é a **textura** de importação.
Gravar por cima do arquivo que o editor tem aberto para importar apagaria a
fonte. O laço tem duas portas de saída e só uma leva ao aviso de sucesso —
cancelar sai calado.

### O `9 * (indice div 95)`

Mesmo termo do `boton_tex2isoClick`, e com o mesmo efeito: zero para os 95 times
de verdade, 9 para o item 95, o time-modelo da Master League. O
`lista_equiposChange` habilita este botão **sem** olhar `nacional`
(`0x0040d31a`), então o item 95 é alcançável e a expressão tem de valer lá
também.

## O gate

`--artefato`, como o
[`golden-07-mcr`](../../tests/roteiros/golden-07-mcr.txt): a imagem tem de sair
**intacta nos dois lados** e o `--artefato` compara o arquivo que cada lado
emitiu. Comparar só as imagens aprovaria um port inerte — um handler vazio
passaria, porque nenhum dos dois grava byte nenhum na ROM.

Roteiro: [`golden-14-uniforme`](../../tests/roteiros/golden-14-uniforme.txt).

O lado port recebe o destino por `WTE_UNI`, pela mesma razão do `WTE_MCR`: o
`TSaveDialog` do gtk2 quer um nome **digitado**, e o `:98` não entrega tecla ao
GTK2 sem gerenciador de janela. A afordância não muda byte nenhum — muda por
onde o caminho entra.
