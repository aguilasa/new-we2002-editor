---
handler: grabar_memoryClick
formulario: MainForm
endereco: 0x0040f69c
veredito: implementado
---

# MainForm.grabar_memoryClick

Emite um **memory card PSX** com o time selecionado dentro: um arquivo `.mcr`
de 131.072 bytes. 540 bytes de corpo, mais os 1.356 da rotina que ele chama.

**É o único dos seis handlers de gravação da WTE-TASK-27 que não escreve na
imagem de CD.** A imagem só é lida. Isso muda a régua e não só o código — ver
"O gate" no fim.

O trabalho está partido em dois, e a divisão é do original:

| endereço | bytes | papel |
|---|---|---|
| `0x0040f69c` | 540 | escolhe o arquivo, recusa um nome, e avisa no fim |
| `0x0040f150` | 1.356 | copia o molde e escreve o time por cima |

**Evidência:** disassembly lido

## Entrada

- `dialogo_grabar_memory` (`[this+0x3c4]`), o `TSaveDialog` do formulário —
  `DefaultExt = 'mcr'`, `Title = 'Extrair MCR do jogo'`, com
  `ofOverwritePrompt`;
- `dialogo_mcr` (`[this+0x300]`), o `TOpenDialog` da **importação** de `.mcr` —
  entra só como termo da recusa, ver abaixo;
- `lista_equipos.ItemIndex`, que decide o time;
- a imagem aberta, em três regiões;
- as 23 legendas `dorsalN`, que são **tela** e não modelo;
- a primeira metade do `data/dat.bin`, o molde do cartão.

**Evidência:** disassembly lido

## Saída

```text
repete:
    se nao dialogo_grabar_memory.Execute:  sai sem gravar e sem avisar
    destino := dialogo_grabar_memory.FileName
    se destino = dialogo_mcr.FileName:
        ficha_error2.etiq1 := 'That file name is already being used by Team Editor'
        ficha_error2.ShowModal
        volta a repetir            <- reabre o dialogo, nao desiste
    senao: sai do laco

fopen(destino, "wb")
grava o cartao (0x0040f150)
fclose(destino)

ficha_info3.etiq1 := 'A MCR foi salva!!!.    '
ficha_info3.ShowModal
```

O laço tem **duas** portas de saída e só uma leva ao aviso de sucesso: cancelar
o diálogo pula tudo (`bl` fica zero e o salto em `0x0040f7b7` atravessa o corpo
inteiro), enquanto nome bom sai por `0x0040f7ab` com `bl = 1`.

As duas cadeias são do binário — `0x00424f07` e `0x00424f3f` —, e o modo do
`fopen` é o `"wb"` de `0x00424f3b`. `FileName` vazio vira a cadeia vazia de
`0x00424f3e` em vez de ponteiro nulo.

**Evidência:** disassembly lido

## O corpo: `0x0040f150`

### O molde vem inteiro, e primeiro

```text
fseek(dat.bin, 0, SEEK_SET);  fread (buf, 0x20000, 1, dat.bin)
fseek(saida,   0, SEEK_SET);  fwrite(buf, 0x20000, 1, saida)
```

`0x20000` = 131.072 = o tamanho exato de um memory card PSX, e é a primeira
metade do `dat.bin` — um cartão já formatado, com o slot do WE2002 pronto. A
segunda metade (14.336 B) é outra coisa: os sete setores que o arranque injeta
na imagem, já descritos na seção 8 de [`../assets.md`](../assets.md).

O molde tem de ir **antes**; ele cobriria qualquer campo escrito primeiro.

**Evidência:** disassembly lido, `wte/re/assets.md` seção 8.1

### As três regiões de origem

Todas são endereço **lógico** no fluxo de dados a partir do setor 850 — a mesma
base das barras, `850 × 2352 + 24 = 0x1E8178`. Duas casam com um `OFS_*` do
`we2002_core` e uma não:

| lógico | passo | time 0 | `we2002_core` |
|---|---|---|---|
| `0x40C2C` | 30 | 2303700 | `OFS_FORMATIONS` |
| `0x408A8` | 5 | 2302800 | **sem nome** |
| `0x46228` | 6 | 2329056 | `OFS_KICKER` |

Duas delas ainda somam `2 × (índice div 95)`. Esse par de bytes não é enfeite:
é exatamente o `image_file.Read(buf,2)` que o `Load` do `we2002_core` faz entre
os 32 clubes de Master League e o time-modelo. Só o item 95 do combo o sente.

A região de tática (`0x408A8`) não tem nome no `we2002_core` porque o `ed.exe`
não a lê. Quem a nomeia é o próprio `wte.exe`: o mesmo endereço aparece em
`MainForm.mostrar_estrategiaClick` (`0x0041040c`), em
`estrategia.BitBtn3Click` (`0x0040ad42`) e em `MainForm.boton_mcr2isoClick`
(`0x0040c85f`), e nos três ele enche o mesmo rascunho global de 4 bytes,
`0x00432eaf`.

**Evidência:** disassembly lido

### O que vai para onde

| destino no `.mcr` | tamanho | origem |
|---|---|---|
| `0x63D5` | 10 B | formação, bytes 0..9 |
| `0x62A8` | 20 B | formação, bytes 10..29 |
| `0x64E2` | 1 B | tática byte 0, cru |
| `0x6102` | 1 B | tática byte 0 **mais 50** |
| `0x6488` | 1 B | tática byte 1, nibble baixo |
| `0x6479` | 1 B | tática byte 1, nibble alto |
| `0x6497` | 1 B | tática byte 2, nibble baixo |
| `0x64A6` | 1 B | tática byte 2, nibble alto |
| `0x614F` `0x6140` `0x6122` `0x6113` `0x6131` | 1 B cada | cobradores, bytes 0..4 |
| `0x6500` | 1 B | cobradores, byte 5 (o capitão) |
| `0x5904` + 32·j | 22 B | jogador j: 12 B de atributo, depois 10 B de nome |
| `0x5404` | 16 B | os 23 números de camisa, 5 bits cada |

A formação sai **partida**: contígua na imagem, em dois trechos no cartão. O
corte é depois do décimo byte, num teste dentro do próprio laço de 30
(`cmp ebx,0xa` em `0x0040f203`).

Os cinco destinos de cobrador saem de uma tabela de cinco `DWORD` em
`0x00423F84` e **não são crescentes** — por isso são tabela e não aritmética.

Os 22 bytes de jogador saem na ordem **atributo, depois nome**, embora no
buffer o nome venha primeiro. Os 10 bytes que sobram no passo de 32 ficam com o
que o molde tinha.

**Evidência:** diff medido

### Os quatro nibbles são só isso

O extrator é `0x00403278`, que recebe o par (byte baixo, byte alto), um
deslocamento e um comprimento, e devolve `comprimento` bits a partir do bit
`deslocamento` do valor de 16 bits. Nas quatro chamadas o deslocamento é 0 ou 4
e o comprimento é 4, então `deslocamento + comprimento ≤ 8` sempre: **o byte
alto nunca entra na conta**. O quarto byte lido da região de tática é passado e
nunca usado.

**Evidência:** diff medido

### Os números de camisa vêm da TELA

O único campo que não sai nem da imagem nem do molde. Para cada j de 0 a 22:

```text
alvo := MainForm.FindComponent('dorsal' + IntToStr(j + 1))
valor := StrToInt(alvo.Caption) - 1
se valor > 31: valor := 31
posicao := 32 * (j div 6) + 5 * (j mod 6)
poe 5 bits de `valor` em `posicao` no buffer de 16 bytes
```

`'dorsal'` é a cadeia de `0x00424F00`; o limite é o `cmp ..,0x1f` / `jbe` de
`0x0040f60e`, e a comparação é **sem sinal** — um rótulo que não seja número dá
`0 - 1 = 255`, que o limite corta em 31.

São 30 bits usados por grupo de seis e 2 perdidos, quatro grupos, 16 bytes — a
mesma forma do `SquadNumbers` do `we2002_core`.

**Ir à tela é o ponto, não um atalho:** é assim que um número editado pela
WTE-TASK-26 chega ao cartão sem passar pela imagem. É o par que o enunciado da
task nomeia (`dorsalClick`, `scroll_dorsalChange`).

**Evidência:** diff medido

### O buffer 23, e o efeito colateral que ele tem

Os 23 jogadores são carregados um a um pela `0x004046e8`, com **`ecx = 0x17`**
— o índice do buffer, não uma contagem. O array de buffers do original tem
registros de 44 bytes em `0x004335ec`, e o 23 cai **dentro da lista de
descarte** (`BUF_DESCARTE_BASE + 20` na numeração do port). Emitir um cartão
embaralha a linha 20 do descarte, no original e aqui.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem de CD.** Medido: o `cmp` da sonda `27-mcr.txt` contra a
cópia limpa acusa só as duas faixas do arranque, as mesmas de todo roteiro
deste gate.

No `.mcr` produzido, contra o molde do `dat.bin`: **489 bytes em 51 faixas**,
com o time 2 da ROM japonesa. As 51 faixas são as da tabela acima, com uma
ausência que vale registrar — **`0x6479` não aparece**, porque para esse time
o valor gravado (o nibble alto de `0x0E`, que é zero) é igual ao que o molde já
tinha. É a mesma cegueira que o [`gravacao_controle.py`](../../tools/gravacao_controle.py)
descreve entre `escreveu` e `mudou`: gravação de valor igual nenhum `cmp` vê.

Conferência das três regiões contra a imagem, time 2:

```text
formacao img: 02 03 06 07 08 0a 0e 10 11 13 | 0b 0b 0b 0f 0f 14 1f 1f 2c 29 20 34 48 11 57 32 1e 3e 2a 3e
formacao mcr: 02 03 06 07 08 0a 0e 10 11 13 | 0b 0b 0b 0f 0f 14 1f 1f 2c 29 20 34 48 11 57 32 1e 3e 2a 3e
tatica   img: 01 0e 94 38   ->  0x64e2=01 0x6102=33 0x6488=0e 0x6479=00 0x6497=04 0x64a6=09
cobrador img: 07 07 08 07 07 08
              0x614f=07 0x6140=07 0x6122=08 0x6113=07 0x6131=07   0x6500=08
```

**Evidência:** diff medido

## Pré-condições

- imagem aberta e time escolhido — **e o segundo não é só bom senso**: o botão
  nasce `Enabled = False` no DFM e quem o liga é o `lista_equiposChange`, em
  `0x0040d31a`. O `grabar_camiseta` é ligado na linha seguinte
  (`0x0040d327`);
- `dat.bin` presente, que já é pré-condição de arranque do app inteiro.

**Evidência:** disassembly lido

## Comportamento de erro

Uma recusa só, e ela não é validação de conteúdo: **o nome escolhido não pode
ser o mesmo do `.mcr` aberto para importação.** Gravar por cima apagaria a
fonte que o próprio editor está usando. A recusa não desiste — reabre o
diálogo.

Fora isso não há tratamento: `fopen` que falhe segue para a RTL sem checagem no
corpo do handler.

**Evidência:** disassembly lido

## Notas

### O gate precisou de régua nova

`golden_check.sh` compara duas **imagens**. Aqui a imagem sai intacta dos dois
lados, então a comparação passaria com um port que não fizesse nada. Entrou a
opção `--artefato`: o script apaga `work/<nome>` antes de cada lado, guarda o
que aquele lado produziu, e compara os dois no fim — e continua comparando as
imagens, que é como se prova que a gravação **não vazou** para dentro da ROM.
Lado que não produziu o arquivo reprova.

Não-vacuidade sai de graça nesse desenho: o arquivo é **criado** pelo handler,
então port inerte não produz nada e o gate para antes de comparar.

### `WTE_MCR` é afordância de harness

O lado port não consegue digitar num `TSaveDialog` do gtk2 — sem gerenciador de
janela o `:99` não entrega tecla a ele. A variável semeia o destino no
`FormShow` e o handler pula o `Execute`, exatamente como `WTE_TEXTURA` semeia a
textura e o argumento posicional semeia a imagem. Não muda byte nenhum: muda
por onde o caminho entra, e os dois lados terminam com o mesmo arquivo.

### Divergência deliberada: de onde vêm os bytes de jogador

O original chama a `0x004046e8`, que **relê nome e atributos da imagem** para o
buffer 23. O port chama a `CarregaJogador`, que lê a camada de dados — já
byte-idêntica ao `ed.exe`. É a mesma divergência já registrada no
[`boton_barras2isoClick`](MainForm.boton_barras2isoClick.md):
mesmo byte, mesma posição, outra fonte. O buffer continua sendo o 23, com o
efeito colateral acima.

### O que fica de fora, com dono

`boton_mcr2isoClick` (`0x0040c46c`) é o caminho inverso — lê um `.mcr` e grava
**na imagem**. Ele é da mesma task, mas o parser é da
[WTE-TASK-28](../../../docs/tasks/concluidos/28-import-de-mcr.md).
