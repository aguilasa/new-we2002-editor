# O render 2D — cor, aritmética e arredondamento
**GERADO** por [`dump_render2d.py`](../tools/dump_render2d.py) a partir de
`we-team-editor/we-team-editor.exe` e de `we-team-editor/image/`. Não edite à mão.

```sh
python3 wte/tools/dump_render2d.py --check
```

## As três perguntas que a task manda responder antes do código
O enunciado da
[WTE-TASK-29](../../docs/tasks/concluidos/29-camisa-e-bandeira-2d.md) é explícito:
*"descobrir qual antes de escrever código — muda o algoritmo inteiro"*.
As três têm resposta no `.text`, e nenhuma precisou de decompilador.

| pergunta | resposta | onde está a prova |
|---|---|---|
| paleta ou varredura de pixel? | **paleta** | as três rotinas de desenho posicionam o arquivo em `0x36` e reescrevem as primeiras entradas; nenhuma toca um pixel |
| que espaço de cor no escurecer/clarear? | **nenhum** — a conta é na palavra BGR555 empacotada | `dec`/`sub 0x20`/`sub 0x400` no próprio `DWORD`, sem multiplicação e sem conversão |
| onde some a fidelidade do gradiente? | **no truncamento**, e o passo é float de precisão simples | `fstp DWORD` para o passo, e o arredondador põe `0xc01` no control word |

## A paleta é o meio, e o bitmap é só a forma
Os `.bmp` de 8 bpp trazem 54 bytes de cabeçalho e
256 entradas de 4 bytes. O `0x36` que as
três rotinas de desenho usam é exatamente
54 — a **primeira entrada da paleta** —, e cada uma
reescreve um punhado a partir dali. Medido na pasta do usuário:

| família | arquivos |
|---|---:|
| bandeiras | 53 |
| camisas | 99 |
| calções | 6 |
| **de 8 bpp** | **198** |
| fora do padrão | 0 |

Um único bitmap de 24 bpp na pasta quebraria a mecânica — o cabeçalho
teria outro tamanho e `0x36` cairia no meio do pixel. Por isso a
profundidade é **contada**, e não suposta.

### As três rotinas — e elas **não** reescrevem o mesmo tanto

| rotina | papel | arquivos | entradas por arquivo |
|---|---|---:|---:|
| `0x00405270` | bandeira do titular | 1 | 16 |
| `0x00405468` | bandeira do reserva | 1 | 16 |
| `0x004056c8` | camisa e calcao | 2 | 15 |

**A bandeira reescreve 16 entradas e o uniforme reescreve 15.** O laço
do uniforme para em `cmp esi,0xf`, o da bandeira em `cmp esi,0x10`, e o
uniforme roda o bloco inteiro duas vezes — uma para `camiseta<n>.bmp` e
outra para `pantalon<n>.bmp`, cada uma com o seu `push 0x36`.
Vale registrar porque a seção 6 do [`assets.md`](assets.md) generalizou
*"idem, 16 entradas, por arquivo"* para o uniforme, e são 15. A
generalização é o erro fácil aqui: as três rotinas se parecem o
bastante para alguém escrever um laço só, e o resultado seria uma
entrada de paleta a mais escrita em toda camisa.

## A palavra de cor: BGR555, e o campo de cada canal
A fonte das cores da bandeira é `0x00432ef4`, 16 palavras
de 16 bits.
O decodificador `0x00404dd4` consome os cinco bits mais
baixos primeiro e escreve o resultado no byte 0 do buffer de três; o
escritor de paleta despeja esse buffer na ordem **2, 1, 0**, e a entrada
de paleta BMP é `B, G, R, reservado`. Os dois fatos juntos fixam o
mapeamento sem deixar margem:

| bits | canal | passo de um degrau |
|---|---|---|
| 0–4 | R | `1` |
| 5–9 | G | `0x20` |
| 10–14 | B | `0x400` |
| 15 | não usado | — |

**A expansão de 5 para 8 bits é `v << 3`, e não replicação de bit
alto.** Isso não é detalhe: `31 << 3` dá **248**, não 255, e é por isso
que o teto do clarear é `0xF8`. Um port que expandisse com `v * 255 / 31`
teria branco diferente do original em toda camisa clara.

## Escurecer e clarear: um degrau, na palavra empacotada
Nem RGB de 8 bits, nem HSL. Os dois handlers decodificam a palavra só
para **testar o limite**, e depois somam ou subtraem direto no `DWORD`
empacotado:

```text
escurecer (0x004065fc):        clarear (0x00406744):
  se R_expandido > 0:            se R_expandido < 0xF8:
      palavra -= 1                   palavra += 1
  se G_expandido > 0:            se G_expandido < 0xF8:
      palavra -= 0x20               palavra += 0x20
  se B_expandido > 0:            se B_expandido < 0xF8:
      palavra -= 0x400              palavra += 0x400
```

**O limite é testado no byte já expandido**, e o detalhe importa: o
piso é `> 0` sobre o valor de 8 bits, que é o mesmo que `> 0` sobre o
de 5. Mas o teto é `< 0xF8`, que só coincide com `< 31` porque a
expansão é deslocamento. Trocar a expansão quebraria o teto junto.
Os dois percorrem a faixa selecionada — de `0x00433dcc` a
`0x00433dd0` no vetor `0x00433dd4` —, não a paleta inteira.

## O gradiente, que é o risco nomeado da §9 do plano
A §9 dá probabilidade **média** para *"render 2D não bate pixel a pixel"*
e nomeia a causa: arredondamento de gradiente. A causa está
medida, e são **duas**:

1. **o passo é `Single`, não `Double`.** `fstp DWORD PTR [esi]` guarda
   `(fim - início) / n` em precisão simples, e o acumulador também;
2. **a conversão para inteiro trunca para zero.** O arredondador da RTL
   (`0x00419d80`) põe `0xc01` no control word do 387 antes do `fistp`,
   e os bits 10–11 em `11` são *round toward zero*. Não é `Round`, não
   é meio-para-cima.

E a soma final não recompõe a palavra canal a canal — ela **soma os
deslocamentos sobre a palavra de partida**:

```text
passo[c] := Single(fim[c] - inicio[c]) / Single(n)
acumulado[c] := 0
para cada entrada entre as duas pontas:
    acumulado[c] := acumulado[c] + passo[c]
    palavra := palavra_inicial
             + trunca(acumulado[0])
             + trunca(acumulado[1]) shl 5
             + trunca(acumulado[2]) shl 10
```

Escrever isso como *"interpola cada canal e reempacota"* dá o mesmo
resultado quase sempre — e diferente exatamente onde o truncamento
morde. É a forma de errar que o plano previu.

## `grabar_camisetaClick` **não grava na imagem** — ele exporta
`0x0040ee80`. O enunciado da task dizia que este handler
grava na imagem de CD e que por isso seria a segunda gravação a provar
EDC/ECC. **Medido, não é.** Ele abre o destino em `"wb"`, lê da imagem
e escreve no arquivo; a ROM sai intacta, e a mensagem de fim é
`O uni foi salvo!!!.`
O laço de cópia é payload puro: `fread` de 2048, `fwrite` de
2048, `fseek(+304)`. E 2048 + 304 = 2352, que é o setor MODE2/2352
inteiro — ou seja, ele salta o cabeçalho e o EDC/ECC de cada setor em vez
de copiá-los.
**Consequência para o gate:** o golden deste handler é do mesmo
formato do [`golden-07-mcr`](../tests/roteiros/golden-07-mcr.txt) — a
imagem tem de sair **intacta nos dois lados** e o `--artefato` compara o
arquivo que cada lado emitiu. Comparar só as imagens aprovaria um port
inerte. Quem grava textura **na** imagem é o
[`boton_tex2isoClick`](spec/MainForm.boton_tex2isoClick.md), que já tem
veredito `implementado`.

## As afirmações, uma a uma, contra o `.text`
Cada linha é um padrão de instrução que este gerador **procura** e sem
o qual ele se recusa a emitir. Padrão que sumir é afirmação que
caducou.

| rotina | bytes | o que prova |
|---|---|---|
| `0x00404dd4` | `c02203` | `shl BYTE PTR [edx],0x3` — a expansao de 5 para 8 bits e deslocamento, e NAO replicacao de bit alto |
| `0x00404dd4` | `83fe05` | `cmp esi,0x5` — sao cinco bits por canal |
| `0x00404dd4` | `833c2403` | `cmp DWORD PTR [esp],0x3` — sao tres canais |
| `0x00419d80` | `814dfc010c0000` | `or DWORD PTR [ebp-0x4],0xc01` — os bits 10-11 do control word em `11`, que e **truncar para zero** |
| `0x004065fc` | `ff0b` | `dec DWORD PTR [ebx]` — um passo para baixo no canal R (bits 0-4) |
| `0x004065fc` | `832b20` | `sub DWORD PTR [ebx],0x20` — um passo no canal G (bits 5-9) |
| `0x004065fc` | `812b00040000` | `sub DWORD PTR [ebx],0x400` — um passo no canal B (bits 10-14) |
| `0x004065fc` | `807d0000` | `cmp BYTE PTR [ebp+0x0],0x0` — o piso e conferido no byte EXPANDIDO |
| `0x00406744` | `ff03` | `inc DWORD PTR [ebx]` — o espelho exato do escurecer, no canal R |
| `0x00406744` | `830320` | `add DWORD PTR [ebx],0x20` — idem, canal G |
| `0x00406744` | `810300040000` | `add DWORD PTR [ebx],0x400` — idem, canal B |
| `0x00406744` | `807d00f8` | `cmp BYTE PTR [ebp+0x0],0xf8` — o teto e `0xF8`, que e `31 << 3`: a prova de que a expansao satura em **248**, e nao em 255 |
| `0x004063b0` | `d91e` | `fstp DWORD PTR [esi]` — o passo do gradiente e guardado em float de precisao **simples** |
| `0x004063b0` | `c1e005` | `shl eax,0x5` — o canal G volta empacotado por deslocamento |
| `0x004063b0` | `c1e00a` | `shl eax,0xa` — e o B por dez |
| `0x0040ee80` | `6800080000` | `push 0x800` duas vezes — le 2048 e escreve 2048, o payload do setor |
| `0x0040ee80` | `6830010000` | `push 0x130` — e pula 304, que e cabecalho mais EDC/ECC |
| `0x00405270` | `bbf42e4300` | `mov ebx,0x432ef4` — a bandeira le as 16 palavras da GLOBAL do time selecionado, ja carregada |
| `0x004056c8` | `8d1cc5562f4300` | `lea ebx,[eax*8+0x432f56]` **duas vezes, com a mesma base** — camisa e calcao recebem o MESMO jogo de cores, e nao um cada |
| `0x004056c8` | `8d0c95a6324200` | `lea ecx,[edx*4+0x4232a6]` — o indice da camisa sai de tabela do `.exe`, e nao da imagem de CD |
| `0x004056c8` | `8d048da7324200` | `lea eax,[ecx*4+0x4232a7]` — o do calcao e o byte seguinte da mesma tabela |
| `0x004050f0` | `68162f4300` | `push 0x432f16` — o carregador enche o PRIMEIRO jogo do slot 0 com 0x20 bytes lidos do disco |
| `0x004050f0` | `68362f4300` | `push 0x432f36` — e o segundo jogo, logo depois, com outros 0x20 |
| `0x00404f90` | `8d04c5162f4300` | `lea eax,[eax*8+0x432f16]` — o slot tem 64 bytes (`eax` ja vem multiplicado por 8), e e por isso que o slot 1 comeca em `0x432f56` |
| `0x00404f90` | `8d14d5162f4300` | `lea edx,[edx*8+0x432f16]` — a outra ponta da mesma copia: origem e destino sao slots do MESMO vetor |

## O Pascal, e o que o segura no lugar
A aritmética está em [`wte/src/we2002_render.pas`](../src/we2002_render.pas),
**escrita à mão** — não há gerador possível para uma rotina. O que é
gerado é a *conferência*: o `--check` deste script extrai os operandos
das instruções acima e os compara com as constantes da unidade, um a
um.

| constante do Pascal | de onde o `.exe` a entrega |
|---|---|
| `RENDER_EXPANSAO` | o operando do `shl BYTE PTR [edx],<n>` |
| `RENDER_BITS` | o do `cmp esi,<n>` do laço de bits |
| `RENDER_CANAIS` | o do `cmp DWORD PTR [esp],<n>` |
| `RENDER_MAXIMO` | o do `cmp BYTE PTR [ebp+0x0],<n>` do clarear |
| `RENDER_PASSO_G` | o do `add DWORD PTR [ebx],<n>` |
| `RENDER_PASSO_B` | idem, em 32 bits |
| `PALETA_BANDEIRA`, `PALETA_UNIFORME` | o `cmp esi,<n>` de cada desenhista |

**`BMP_CABECALHO` é o único que não se extrai**, e a conferência dele
vai na direção contrária: um `push imm8` sozinho não diz para que
serve, e a rotina tem vários. Então o Pascal afirma 54 e o script exige
que `push 54` esteja dentro das três rotinas de desenho.
E há um guard que não é sobre número: a unidade **não pode** conter
`Round(acumulado` — o original trunca, e trocar isso é o risco da §9
acontecendo em silêncio. As constantes da unidade são escritas como
literal justamente para caber nesta leitura; a derivação
(`RENDER_MAXIMO = 31 shl 3`) mora no comentário e é **executada** pelo
[`test_render.pas`](../tests/test_render.pas).

## O recipiente: o que os 198 arquivos **são**
A conferência do parágrafo acima é contra o `.text`. Esta é contra a
pasta do usuário, e a direção importa: o
[`we2002_bmp.pas`](../src/we2002_bmp.pas) **recusa** um `.bmp` que não
case com a forma abaixo, e uma constante errada ali faria o port
recusar a pasta inteira em silêncio — tela em branco, sem erro, que é o
pior modo de falhar.

| constante | valor | medido em |
|---|---:|---|
| `BMP_BITS` | 8 | os 198 bitmaps de 8 bpp |
| `BMP_DADOS` | 1078 | os 198 bitmaps de 8 bpp |
| `BMP_INFO_BYTES` | 40 | os 198 bitmaps de 8 bpp |
| `BMP_PALETA_ENTRADAS` | 256 | os 198 bitmaps de 8 bpp |
| `BMP_SEM_COMPRESSAO` | 0 | os 198 bitmaps de 8 bpp |

Os 1078 são 54 + 256 × 4, e é o número
que fecha o círculo com o `push 0x36`: a paleta só termina onde os
pixels começam se ela tiver exatamente 256 entradas.
**O `bfOffBits` é conferido, e o original não o consulta.** Ele assume
`0x36`. Um arquivo com outro valor faria a troca de paleta acertar o
lugar errado — nos dois lados —, e é por isso que o port prefere
recusar o arquivo a desenhá-lo torto.

## Que arquivo cada time usa: as duas tabelas de `.data`
A cor vem da imagem de CD. A **forma** vem daqui, e as duas tabelas
respondem perguntas diferentes:

| tabela | tamanho | o que é | usada no desenho? |
|---|---:|---|---|
| `0x004231e8` | 95 bytes | forma de bandeira *padrão* por time, 53 distintas | **não** |
| `0x004232a6` | 95 × 4 bytes | `(camisa, calção)` por time e por jogo | **sim** |

A assimetria é o achado: **a forma da bandeira é lida da imagem de CD,
e a da camisa não.** A tabela de bandeiras só alimenta o combo de forma
do `ficha_color`, que a *indexa* em vez de digitar o número — e é por
isso que os oito índices sem arquivo (44..51) nunca são pedidos. A de
uniformes é a fonte real: nenhum byte do disco diz que padrão de tecido
um time veste.
As duas saem para [`wte_uniformes.pas`](../src/wte_uniformes.pas), e
este gerador **recusa** se qualquer índice que elas nomeiam não tiver
arquivo em disco. Não é conferência de forma, é de alcance: índice sem
arquivo seria tela em branco no port e `LoadFromFile` falho no
original.

### E camisa e calção recebem o **mesmo** jogo de cores
O desenhista do uniforme monta o endereço das cores com
`lea ebx,[eax*8+0x00432f56]`, onde `eax` é o jogo × 4 — ou seja, passo de
32 bytes, que são as 16 palavras de um jogo. **A mesma
instrução, com a mesma base, aparece nos dois laços**: o de
`camiseta<n>.bmp` e o de `pantalon<n>.bmp`.
Não são dois conjuntos de cor, é um só aplicado a dois arquivos. Um
port que guardasse cores de camisa e cores de calção em separado
estaria inventando um grau de liberdade que o formato não tem — e a
tela mostraria calção de cor errada assim que alguém editasse.

### E o uniforme começa na palavra **1**, não na 0
A assimetria contra a bandeira não é só de contagem — é de **início**, e
essa metade não se vê olhando o laço. Os dois leem palavras de 16 bits
em sequência; o que muda é onde a sequência começa dentro do bloco de
16 palavras do time:

| desenhista | primeira palavra | quantas |
|---|---:|---:|
| bandeira | 0 | 16 |
| uniforme | **1** | 15 |

**Foi medido de frente, e o original entregou a resposta de graça:** ele
grava a paleta *dentro* do `.bmp` (seção 6 do [`assets.md`](assets.md)),
então o arquivo que o oráculo deixou em disco **é** o resultado. Três
pares (arquivo, time) independentes — `camiseta3`, `pantalon4`,
`pantalon0` — casaram com `home_kit[1..15]` da camada de dados, e
nenhum com `[0..14]`.
O `.text` explica por quê, e a explicação é de layout:

1. o carregador (`0x004050f0`) lê do disco `0x20` bytes para
   `0x00432f16` e outros `0x20` para `0x00432f36` — os dois jogos do
   **slot 0**;
2. em seguida copia o slot inteiro, 64 bytes (`0x00404f90`, com
   `lea eax,[eax*8+0x00432f16]`), para o **slot 1** — o rascunho que o
   `ficha_color` edita;
3. o desenhista lê de `0x00432f56`, que é exatamente
   `0x00432f16 + 64`: o slot 1.

E o dado fecha a conta: **nos 190 conjuntos de uniforme das duas ROMs a
palavra 0 é zero.** Ela não é cor, é enchimento — o `.exe` simplesmente
começa na primeira cor de verdade. Já `flag_colours[15]` é zero nas 95, e
o desenhista da bandeira **escreve** esse zero: entrada preta.
> **Este é o erro que a task previu, e o único que apareceu.** Um laço
> compartilhado entre os três desenhistas erraria a contagem *e* o
> início, e o resultado não é tela em branco — é uma camisa colorida com
> as cores certas nos lugares errados, que passa por decisão de design
> para quem não tiver o original ao lado.

## O que fica para o resto da task
Duas decisões já tomadas noutro lugar, e que este documento não
reabre:

- **recolorir em memória**, e não reescrevendo o `.bmp` do usuário. A
  recomendação é da seção 6.2 do [`assets.md`](assets.md); o original só
  grava no arquivo porque a VCL de 2002 carregava paleta por
  `LoadFromFile`. É o que a [`wte_render2d.pas`](../src/wte_render2d.pas)
  faz;

- **`TLazIntfImage`**, não `Canvas.Pixels`. É o que a
  [`wte_render2d.pas`](../src/wte_render2d.pas) usa, e o custo de um
  redesenho está medido: o maior bitmap que este render toca tem
  51×42 = 2142 pixels, uma troca de time redesenha três
  arquivos, e a troca de paleta em si são 45 bytes. O arquivo é lido do
  disco uma vez e fica em memória — o original o relê a cada redesenho,
  porque para ele o arquivo *é* o estado.
