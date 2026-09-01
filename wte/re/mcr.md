# O `.mcr` do WE2002 — contêiner e conteúdo
**GERADO** por [`dump_mcr.py`](../tools/dump_mcr.py) a partir de
`we-team-editor/data/dat.bin` e `we-team-editor/we-team-editor.exe`. Não edite a mão.
```sh
python3 wte/tools/dump_mcr.py --check
```

## A divisão, e por que ela poupa a maior parte do trabalho
**Contêiner pela documentação pública, conteúdo por engenharia
reversa.** O memory card do PSX é formato documentado; o que o WE2002
guarda dentro do bloco dele não é. Este documento lê o contêiner do
molde e tira o conteúdo do `.exe` — nenhuma das duas metades é suposta.

## O molde: as duas metades do `dat.bin`
`we-team-editor/data/dat.bin` tem **145408** bytes, e não os 131072 de um
cartão. A primeira metade é um cartão formatado com o save do WE2002
dentro — o molde que o `grabar_memoryClick` copia inteiro antes de
escrever por cima. Os **14336** restantes são os
sete setores que a abertura da imagem injeta, descritos na seção 8 do
[`assets.md`](assets.md). Era a pergunta que o enunciado da
[WTE-TASK-28](../../docs/tasks/concluidos/28-import-de-mcr.md) mandava responder
antes de usar o arquivo como fixture.

## O contêiner
131072 bytes = 16 blocos de 8192. O bloco 0 é
cabeçalho (`MC`) mais 15 quadros de
128 bytes, um por bloco de save.

| bloco | estado | significado | tamanho | link | nome |
|---:|---|---|---:|---|---|
| 1 | `0x51` | em uso, primeiro bloco da cadeia | 16384 | `0x0001` | `BISLPM-86600WEW-OPT` |
| 2 | `0x53` | em uso, ultimo bloco da cadeia | 0 | `0xffff` | `—` |
| 3 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 4 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 5 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 6 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 7 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 8 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 9 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 10 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 11 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 12 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 13 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 14 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |
| 15 | `0xa0` | livre (formatado) | 0 | `0xffff` | `—` |

O save ocupa os blocos **[1, 2]** e se chama
`BISLPM-86600WEW-OPT` — `SLPM-86600` é o *World Soccer Winning Eleven
2002* japonês, o mesmo da ROM que o gate usa.

## O conteúdo do bloco do WE2002
Os dois lados foram medidos: quem escreve é o `0x0040f150` do
`grabar_memoryClick`, quem lê é o `0x0040b9ec` que o `boton_mcrClick`
chama. **Eles não são simétricos**, e a assimetria está na coluna `lê`.

| endereço | bloco | bytes | campo | escreve | lê |
|---|---:|---:|---|---|---|
| `0x5404` | 2 | 16 | numeros de camisa, 23 x 5 bits | `0x0040f5c9` | `0x0040baa9` |
| `0x5904` | 2 | 276 | jogador j: 12 B de atributo (passo 32) | `0x0040f2fe` | `0x0040ba55` |
| `0x5910` | 2 | 230 | jogador j: 10 B de nome (passo 32) | `0x0040f2fe` | `0x0040ba01` |
| `0x6102` | 3 | 1 | tatica byte 0, mais 50 | `0x0040f36d` | `-` **—** |
| `0x6113` | 3 | 1 | cobrador 3 | `0x0040f4a2` | `0x0040bb40` |
| `0x6122` | 3 | 1 | cobrador 2 | `0x0040f4a2` | `0x0040bb40` |
| `0x6131` | 3 | 1 | cobrador 4 | `0x0040f4a2` | `0x0040bb40` |
| `0x6140` | 3 | 1 | cobrador 1 | `0x0040f4a2` | `0x0040bb40` |
| `0x614f` | 3 | 1 | cobrador 0 | `0x0040f4a2` | `0x0040bb40` |
| `0x62a8` | 3 | 20 | formacao, bytes 10..29 | `0x0040f21d` | `0x0040bb07` |
| `0x63d5` | 3 | 10 | formacao, bytes 0..9 | `0x0040f21d` | `0x0040bad9` |
| `0x6479` | 3 | 1 | tatica byte 1, nibble alto | `0x0040f43a` | `-` **—** |
| `0x6488` | 3 | 1 | tatica byte 1, nibble baixo | `0x0040f40a` | `-` **—** |
| `0x6497` | 3 | 1 | tatica byte 2, nibble baixo | `0x0040f3d8` | `-` **—** |
| `0x64a6` | 3 | 1 | tatica byte 2, nibble alto | `0x0040f3a6` | `-` **—** |
| `0x64e2` | 3 | 1 | tatica byte 0, cru | `0x0040f33d` | `-` **—** |
| `0x6500` | 3 | 1 | cobrador 5 (o capitao) | `0x0040f4f8` | `0x0040bb68` |

### A tática vai e não volta
**6 destinos são escritos e nunca lidos de volta** por
`0x0040b9ec`: `0x6102`, `0x6479`, `0x6488`, `0x6497`, `0x64a6`, `0x64e2` — os seis campos de tática. O
leitor traz nomes, atributos, números de camisa, formação e cobradores,
e para aí. Quem lê a tática de um `.mcr` é o `boton_mcr2isoClick`,
direto do arquivo (`0x0040c759` em diante), sem passar pelo buffer que
o `boton_mcrClick` enche.

### As duas tabelas que o `.exe` guarda, e por que são tabelas
Os cinco destinos de cobrador saem de `0x00423f84` e
valem `0x614f`, `0x6140`, `0x6122`, `0x6113`, `0x6131` — **não são
crescentes**, e é por isso que são tabela e não aritmética.
Os deslocamentos de bit do número de camisa saem de
`0x0042360c` e valem [0, 5, 2, 7, 4, 1], que é
`(5 · (j mod 6)) mod 8` — a mesma forma do `SquadNumbers` do
`we2002_core`: 30 bits usados por grupo de seis, 2 perdidos, quatro
grupos, 16 bytes.
O gerador **recusa** se qualquer uma das duas deixar de bater com o
layout escrito aqui.

## O achado: 14 dos 17 destinos caem num bloco que o diretório diz livre
O save declara ocupar os blocos [1, 2]. Os destinos de escrita caem
nos blocos [2, 3], e **[3] não está entre os declarados**.

| bloco | bytes não-zero no molde | declarado |
|---:|---:|---|
| 1 | 5844 | sim |
| 2 | 6243 | sim |
| 3 | 0 | **não** (`0xA0`, livre) |
| 4 | 0 | **não** (`0xA0`, livre) |

Ou seja: jogadores e números de camisa vão para o bloco 2, que é do
save; **formação, tática e cobradores vão para o bloco 3**, que o molde
entrega zerado e o diretório marca livre. E o escritor nunca toca o
diretório — o menor endereço que ele grava é
`0x5404`, muito depois dos
2048 bytes de cabeçalho.
**A coincidência que vale registrar:** o readme do original diz que a
v0.98 consertou *"the problem with the captain and kickers when loading
from .mcr files"*, e capitão e cobradores são exatamente campos do
bloco 3. O veredito — se o cartão emitido é válido para o console, ou se
só serve de transporte entre cópias do editor — é da
[WTE-TASK-28](../../docs/tasks/concluidos/28-import-de-mcr.md); aqui fica a
medição.

## A fixture, e por que ela NAO e versionada
O proprio original emite `.mcr` -- e o `grabar_memoryClick` --,
entao a fixture se gera em vez de se escrever a mao: o roteiro
[`27-mcr.txt`](../tests/roteiros/27-mcr.txt) abre a ROM japonesa,
escolhe um time e salva o cartao.
**O arquivo fica em `work/`, fora do git.** Sao 128 KiB de nomes e
atributos tirados da ROM, e este repositorio nao versiona dado do
jogo -- nem `roms/`, nem `we-team-editor/`. O que entra no git e a
**medicao** abaixo, produzida por
`python3 wte/tools/dump_mcr.py --medir <cartao.mcr>`.

| arquivo | bytes mudados | faixas | diretorio intacto | por bloco |
|---|---:|---:|:-:|---|
| `saida.mcr` | 489 | 51 | sim | 2=448;3=41 |

As duas primeiras colunas fecham com o que a spec do
[`grabar_memoryClick`](spec/MainForm.grabar_memoryClick.md) mediu
quando o handler foi portado, e as duas ultimas sao a prova do
achado acima: **o diretorio sai intacto** e a escrita se reparte
entre o bloco declarado e o bloco livre.

## O que o `boton_mcr2isoClick` faz com isso
`0x0040c46c`. Ele **não** é um leitor a mais: reusa as duas rotinas de
gravação que a [WTE-TASK-27](../../docs/tasks/concluidos/27-handlers-de-gravacao.md)
portou. Para cada um dos 23 slots, enche o buffer 23 a partir do `.mcr`
(`0x0040478c`) e chama a `0x00404820` — a mesma dos handlers de mover —,
depois grava o número de camisa pela `0x00404048`. Formação e tática vão
direto para a imagem.
**A recusa dele é a mesma família da `-1`, e é aritmética antes de
gravar:** para destino de clube de Master League (`ItemIndex > 62`) ele
varre os 23 vínculos do time contando quantos precisariam de bloco novo,
e se o contador de blocos livres for menor recusa com `Voce precisa de
<n> mais blocos livres!!!` sem escrever byte nenhum. Para seleção não
confere nada — não há bloco a alocar.

## Os três casos especiais do readme, e onde cada um mora
O readme da v0.98 do original registra três correções sobre `.mcr`, e
cada uma é um caso que o **formato** tem. O que se reproduz é a
correção, não o bug — e as três estão medidas no binário da v0.99,
que já é o corrigido.

| readme | onde a correção mora | como o port a perde |
|---|---|---|
| *the captain and kickers when loading from .mcr files* | a tabela `0x00423f84`, que **não é crescente**, mais o capitão sozinho em `0x6500` | trocar a tabela por aritmética: os cinco sairiam na ordem do endereço e o capitão viraria o sexto vizinho |
| *the Eire's goalkeeper when loading a .mcr file* | o carimbo `+0x16 := 0xff` da `0x0040478c` | deixar a identidade zerada: `(0, 0)` é a identidade real do slot 0 do time 0, e a `0x00404820` recusa jogador repetido |
| *the spaces in the players names* | o nome é **10 bytes crus**, lidos por `fread`, e o `0x0040b2d8` tem um ramo próprio para `0x20` ao montar a lista | tratar o campo como cadeia C: nome que enche os 10 bytes perderia o fim, e o espaço sumiria da tela |

**O do meio é o que se enxerga menos, e o mais fácil de perder.** Ele só aparece num time e num slot — o 0 e o 0 —, porque só ali a identidade real coincide com o zero que um buffer não carimbado teria. *Ireland* é o item 0 da lista de times, e o slot 0 é o goleiro; daí o nome que o autor deu ao bug. O `--check` deste gerador lê os três carimbos do `.text` e os compara com as constantes do Pascal, e o gate [`golden-13-roundtrip`](../tests/roteiros/golden-13-roundtrip.txt) importa **no time 0** justamente por isso.

## O round-trip: cartão → imagem → cartão
Medido **no lado oráculo** do gate: o mesmo cartão entra pelo
`boton_mcr2iso` e sai pelo `grabar_memory`, sem nada no meio. A
pergunta é do formato, não do port — o que não voltar aqui não
volta para o original tampouco.

| campo | bytes | iguais | diferentes | nota |
|---|---:|---:|---:|---|
| `nomes` | 230 | 230 | 0 | - |
| `atributos` | 276 | 276 | 0 | - |
| `numeros` | 16 | 16 | 0 | - |
| `formacao` | 30 | 30 | 0 | - |
| `cobradores` | 6 | 6 | 0 | - |
| `tatica` | 6 | 6 | 0 | - |
| `arquivo inteiro` | 131072 | 131072 | 0 | entrada.mcr contra volta.mcr |

**Zero divergência, e o arquivo inteiro junto** — a última
linha não é campo, é o `cmp` cru dos 131.072 bytes. Nada do que
o cartão guarda se perde na ida e volta, nem sequer a folga.
A comparação é **campo a campo**, e não byte a byte no arquivo: os
dois cartões herdam a mesma folga do molde, e comparar cru faria a
folga responder pelo dado — precaução que esta medição não precisou
cobrar, mas que a próxima pode.
