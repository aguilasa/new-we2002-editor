---
handler: boton_tex2isoClick
formulario: MainForm
endereco: 0x0040de18
veredito: implementado
---

# MainForm.boton_tex2isoClick

Copia o arquivo de textura escolhido para dentro da imagem — o uniforme do
time, em bytes crus. 460 bytes, do `0x0040de18` ao `0x0040dfe4`.

## Entrada

- `lista_equipos.ItemIndex` (`[this+0x2f0]`), que decide o time;
- o **arquivo de textura já aberto**, `0x00432e60`, e o tamanho dele,
  `0x00434598`. Os dois são postos pelo
  [`boton_dialogo_texClick`](MainForm.boton_dialogo_texClick.md), que também é
  quem habilita este botão — ele nasce `Enabled = False` no DFM.

Não lê a imagem.

**Evidência:** disassembly lido

## Saída

**Vinte setores**, sempre os vinte, com os 2048 bytes de dados de cada um. O
que sobra quando a fonte acaba antes vai a **zero** — o conteúdo velho não
fica.

Depois, `ficha_info3` recebe em `etiq1` a cadeia `Textura inserida no jogo!!!`
(`0x00424e3f`) e é exibido modal.

**Evidência:** diff medido

## Bytes tocados

```
offset = 19756824 + 47040 * (indice + 9 * (indice div 95))
```

`19756824` = `8400 * 2352 + 24`, o primeiro byte de dados do setor 8400;
`47040` = `20 * 2352`. O termo `9 * (indice div 95)` só tem efeito no item 95
do combo, o time-modelo da Master League.

Medido com o time 2 e uma fonte de 5000 bytes: os setores **8440..8459**, 2048
bytes de dados em cada, a partir de 19850904 — que é exatamente
`19756824 + 47040 * 2`.

**Evidência:** diff medido

## Pré-condições

**Nenhuma dentro do handler.** Ele não checa se há imagem aberta nem se há
textura escolhida.

Quem impede o caso ruim é o botão: `Enabled = False` no DFM, e quem o liga é o
`boton_dialogo_texClick`, em `0x0040e17d` — `SetEnabled(True)` pela VMT[0x64]
sobre o campo `0x0474`, que o [`../campos.tsv`](../campos.tsv) resolve neste
botão. Sem fonte escolhida não há o que gravar, e sem clique não há gravação.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Fonte ilegível ou `FILE*` nulo seguiria para a RTL sem checagem.

**Evidência:** disassembly lido

## Notas

### O laço é de vinte blocos, e são dois laços

O original copia enquanto a fonte durar; quando ela acaba **no meio** de um
bloco, ele enche o resto daquele bloco com zero e sai do laço de cópia. Os
blocos que sobraram passam por um segundo laço, que os escreve inteiros de
zero. O contador é o mesmo nos dois, então o total é sempre vinte.

Isso importa: uma textura menor que a anterior **não** deixa rabo. Um port que
gravasse só `lidos` bytes passaria no golden com uma fonte de 40960 bytes e
falharia com qualquer outra — por isso a sonda usa **5000**, que não é múltiplo
de 2048.

### O salto de setor aqui é explícito no original

Diferente dos nomes, que passam pelo `0x00403388` byte a byte, aqui o original
faz um `fseek(+0x130)` no fim de cada bloco. O efeito é o mesmo; o port usa o
`Seek(SETOR_BYTES - SETOR_DADOS, soCurrent)`, que é a forma direta.

### A textura entra no port por variável de ambiente, e isso é do harness

O lado port do gate não consegue escolher arquivo: o `TOpenDialog` do gtk2 não
se dirige por coordenada fixa sem gerenciador de janela. `WTE_TEXTURA` semeia
`TexturaEscolhida` no `FormShow` e liga o botão, exatamente como o argumento
posicional semeia a imagem desde a WTE-TASK-25. **Não muda byte nenhum** —
muda por onde o caminho entra, e os dois lados terminam com o mesmo arquivo.

Enquanto isso, o `boton_dialogo_texClick` continua `aberto`: portá-lo pela
metade daria um veredito que afirma mais do que se fez, e o formato `.tex` é da
[WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md). Na janela do
port o botão de diálogo segue inerte.

### A régua

`golden_check.sh` sobre `golden-06-textura` / `.port`: **passou**, só as duas
faixas do arranque divergem, com o **controle** fechando byte-idêntico antes.
Rodado o lado port sozinho contra a ROM limpa, ele grava os **vinte** setores,
a partir do mesmo 19850904 que a sonda `27-textura` mediu no oráculo.

O Pascal está em
[`../../src/impl/ep2002_mainform.boton_tex2isoClick.inc`](../../src/impl/ep2002_mainform.boton_tex2isoClick.inc).
