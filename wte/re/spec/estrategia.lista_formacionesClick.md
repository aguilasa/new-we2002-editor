---
handler: lista_formacionesClick
formulario: estrategia
endereco: 0x00409aa0
veredito: implementado
---

# estrategia.lista_formacionesClick

Aplica uma das formações predefinidas sobre as onze bolas do campinho. 259
bytes.

## Entrada

`lista_formaciones.ItemIndex` — a formação escolhida. É o único campo que o
corpo toca; ele o lê cinco vezes.

**Evidência:** disassembly lido

## Saída

**O corpo não tem número nenhum: ele aponta quatro ponteiros e chama duas
auxiliares.**

```text
[0x00434224] := papel   do registro escolhido
[0x00434228] := x       idem
[0x0043422c] := y       idem
[0x00434230] := zona    idem
0x004097d4()            ' prepara a animacao e liga o `reloj`
0x004099bc([0x00434224])' pinta os onze `etiqposN`
```

Os quatro ponteiros apontam para dentro de uma tabela de **18 registros de 44
bytes** em `0x00433f0c` — quatro colunas de 11 bytes cada. Ela **não existe no
arquivo**: é `.bss`, montada pelo `estrategia.FormCreate` com quatro `rep
movsd` a partir de quatro blobs contíguos de `.data`
(`0x00423be4`, `0x00423cb0`, `0x00423d7c`, `0x00423e48`, 198 bytes cada). O fim
da tabela encosta em `0x00434224`, que é o primeiro ponteiro, e é essa
contiguidade que fecha o tamanho.

Extraída por [`dump_formacoes.py`](../../tools/dump_formacoes.py) para
[`../../src/wte_formacoes.pas`](../../src/wte_formacoes.pas), com a tabela em
[`../formacoes.md`](../formacoes.md).

**Evidência:** disassembly lido

## Os dois ramos

```text
se ItemIndex <> 1:  os quatro ponteiros indexam a tabela de 18 x 44
senao:              `DEFAULT` -- os tres primeiros apontam o buffer da
                    formacao VIVA do time (0x00432e88) e o quarto sai de um
                    codigo em 0x00432eaf: 16 cai no registro 0 (`STOCK`),
                    qualquer outro valor `f` cai no registro `f + 2`
```

O `+ 2` pula os itens `STOCK` e `DEFAULT` da lista.

**O registro 1 da tabela é um buraco, e o dado prova o ramo:** as quatro
colunas dele são zero. O handler nunca o lê, porque `ItemIndex = 1` desvia
para o buffer vivo. Um zero em `x` daria destino `-2`, fora do campo — e o
`dump_formacoes.py` isenta esse registro da conferência de campo com uma
guarda própria, que cai se ele deixar de ser zero.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum**, e agora isso está medido em vez de delegado. O inventário das três
rotinas alcança `FindComponent`, `CurrToStr`, `TTimer::SetEnabled`,
`TFont::SetColor`, `TControl::SetText` e helpers de `AnsiString`/`Currency` —
nenhuma escritora de arquivo. A versão anterior desta spec dizia "não medido" e
mandava perguntar à
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md); a resposta é
nenhum byte, e a pergunta não precisa ser feita.

**Evidência:** disassembly lido

## Pré-condições

Não confere `ItemIndex = -1` no corpo. O port confere, e a divergência está
abaixo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## As duas auxiliares

### `0x004097d4`, 474 B — prepara a animação e liga o `reloj`

Três laços de `1..10` (o goleiro não anda). As seis tabelas que o
[`relojTimer`](estrategia.relojTimer.md) consome saem daqui:

```text
DestinoX[i] := x[i]*8 - 2
DestinoY[i] := ((y[i] - 3) div 2)*5 - 7      ' idiv: trunca para ZERO
AtualX[i]   := bola_i.Left - campo.Left
DeltaX[i]   := (DestinoX[i] - AtualX[i]) * 0.2
```

O `0.2` é um `long double` de 80 bits em `0x004099b0`, dentro da `.text`, logo
após o corpo. **Com os quatro quadros do `relojTimer` isso cobre 80% do
trajeto**, e o ramo de encaixe dá o último quinto de uma vez — não é correção
de arredondamento de um pixel, como a spec do `relojTimer` sugeria.

No fim: zera o contador de quadros e faz `reloj.Enabled := True`. **Quem liga o
timer é esta rotina, não o handler** — e ela é chamada também por `0x0040a0b4`.

Ela semeia `0x00434340` (a bola em foco) a cada iteração, terminando na
`bola10`.

### `0x004099bc`, 227 B — pinta os onze `etiqposN`

Recebe o vetor de papéis. Para cada jogador `1..10` acha
`etiqpos<i+1>` — o deslocamento existe porque `etiqpos1` é o goleiro —, põe a
cor da fonte e o texto de uma tabela de **22 abreviaturas** em `0x00423b8c`,
que o [`legendas.tsv`](../legendas.tsv) já trazia como tabela `resto`.

O critério de cor tem uma excentricidade que **não** é erro de leitura:

```text
papel = 4  ou  papel > 16  ->  vermelho
papel < 9                  ->  ciano
senao (9..16)              ->  verde
```

`papel = 4` é `Zl`, um zagueiro, e ele cai no ramo dos atacantes. O
`cmp al,4 / je` é a **primeira** instrução do teste, antes de qualquer
comparação de faixa.

**Evidência:** disassembly lido

## Notas

**Este é o handler destrutivo que o enunciado da WTE-TASK-25 manda vigiar.** A
vigilância pedida — "conferir que ela não roda durante a carga" — está
satisfeita por construção: o `estrategia` só é criado no arranque e só fica
alcançável pelo `mostrar_estrategiaClick`, e nenhum handler de carga toca
`lista_formaciones`.

### A divergência que havia aqui, e como ela caiu

**O item `DEFAULT` não fazia nada no port**, e a segunda metade da mesma falta
era mais visível ainda: a tela de tática abria com as bolas nas posições de
projeto do `.lfm` e toda bola na zona 0, até que se clicasse num item da lista.
As duas dependiam de `0x0040a0b4` — a rotina que enche a tela ao abrir o
formulário, chamada pelo `MainForm.mostrar_estrategiaClick`, do grupo de
**carga** —, que não estava portada.

**As duas caíram na
[CORR-WTE-082](../../../docs/tasks/concluidos/CORR-WTE-082.md)**, que a portou como
`PreencheTelaDeTatica` na [`wte_tatica`](../../src/wte_tatica.pas). Com ela o
formulário abre já preenchido, e o `DEFAULT` que a lista mostra é o que a
imagem diz.

**O que mudou aqui por causa disso:** a formação em vigor deixou de ser um
ÍNDICE na tabela predefinida e passou a ser o próprio registro
(`FormacaoEmVigor: TFormacao`). É o que o original sempre teve — um ponteiro em
`0x00434230`, que ora aponta para esta tabela, ora para o buffer vivo do time —
e é o que faz as duas auxiliares servirem os dois casos com um corpo só.

Pascal em
[`../../src/impl/estrategia.lista_formacionesClick.inc`](../../src/impl/ep2002_estrategia.lista_formacionesClick.inc);
as duas auxiliares em
[`../../src/impl/ep2002_estrategia.aux.inc`](../../src/impl/ep2002_estrategia.aux.inc)
como `PreparaAnimacao` e `PintaPosicoes`.
