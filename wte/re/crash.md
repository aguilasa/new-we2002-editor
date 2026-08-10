# `re/crash.md` — onde o `wte.exe` morre ao trocar de time

**Gerado por [`wte/tools/analisar_crash.py`](../tools/analisar_crash.py)
— não editar à mão.** Evidência em [`crash-seh.tsv`](crash-seh.tsv),
[`crash-modulos.tsv`](crash-modulos.tsv) e
[`crash-sessoes.tsv`](crash-sessoes.tsv).

Produto da WTE-TASK-19. O [`offsets-novos.md`](offsets-novos.md) mede
**I/O** e chegou até *a última leitura antes do `SIGSEGV`*; daí a causa
não sai — leitura vizinha de uma falha é correlação. Este documento
pergunta ao Wine **qual instrução faltou**, e responde com nome de
função.

## O que separa as duas sessões

| sessão | roteiro | seleciona time? | violações de acesso |
|---|---|:---:|---:|
| `sem-time` | `07-controle-sem-time.txt` | não | 0 |
| `so-troca-de-time` | `08-so-troca-de-time.txt` | sim | 309 |

Os dois roteiros são **iguais linha a linha até a marca `ARRANQUE`**;
o segundo tem duas linhas a mais, que trocam o time pelo teclado. Mesmo
binário, mesma imagem, uma variável de diferença — e ela separa nenhuma
violação de acesso de todas elas. **A atribuição é medida, não inferida
do que aparece na tela** — e a tela, aqui, engana: a janela sobrevive ao
processo porque o `wineserver` a mantém mapeada.

## A exceção

| # | code | addr | info[1] (endereço que faltou) | eax | edx |
|---:|---|---|---|---|---|
| 1 | `c0000005` | `0x005f5ea0` | `0x0000001c` | `0x00000000` | `0x00000008` |
| 2 | `c0000005` | `0x00000000` | `0x00000000` | `0x0031d8c8` | `0x0031e794` |
| 3 | `c0000005` | `0x00000000` | `0x00000000` | `0x0031cbc8` | `0x0031e794` |
| 4 | `c0000005` | `0x00000000` | `0x00000000` | `0x0031bec8` | `0x0031e794` |
| 5 | `c0000005` | `0x00000000` | `0x00000000` | `0x0031b1c8` | `0x0031e794` |

A primeira é a que localiza. As seguintes falham no **endereço zero**
e não localizam nada: o manipulador de exceção do próprio app cai em
seguida e reentra — daí a contagem alta na tabela acima.

## Onde ela cai

| | |
|---|---|
| endereço da falha | `0x005f5ea0` |
| módulo carregado ali | `vcl60.bpl` em `0x005f0000` |
| RVA no módulo | `0x5ea0` |
| exportação que o contém | `@Graphics@TFont@SetSize$qqri` (`0x5e98`, +0x8) |
| endereço que faltou | `0x0000001c` |

O `vcl60.bpl` prefere `0x400a0000` e foi **realocado** para
`0x005f0000`; sem a linha do `+loaddll` o endereço de falha não
cai em módulo nenhum e a pista morre ali. É por isso que a medição
pede `WINEDEBUG=+seh,+loaddll`, e não só `+seh`.

`eax` é zero e o endereço que faltou é o deslocamento de um campo
do objeto: o `this` chegou **nulo**. Não é ponteiro solto nem
índice fora de faixa — é um objeto que deveria existir e não
existe.

## Quem chama

O `.exe` importa `@Graphics@TFont@SetSize$qqri` e a chama
por thunk (`jmp dword ptr [IAT]`), que é a forma do C++Builder —
procurar `call [IAT]` não acha nada. Sítios de chamada no `.text`:

| sítio | é o da falha? |
|---|:---:|
| `0x0040b1ac` | sim |
| `0x0040b2c3` | — |

O sítio é identificado pelo argumento: o C++Builder passa o
primeiro parâmetro em `EDX` (convenção Borland, §8.1 do plano), e
no instante da falha `EDX` valia `0x00000008` — o mesmo
imediato que só um dos sítios carrega.

Os dois sítios estão dentro da mesma rotina privada, que começa em
`0x0040b188` (prólogo `push ebp; mov ebp,esp`). Ela não é
publicada — não é manipulador de evento —, então não tem nome no
[`published_methods.tsv`](published_methods.tsv). Quem a chama, sim:

| chamada em | manipulador que a contém | formulário | deslocamento |
|---|---|---|---:|
| `0x0040d339` | `lista_equiposChange` | `MainForm` | +0x5cd |
| `0x0040f8cb` | `lista_jugadores_1Change` | `MainForm` | +0x13 |
| `0x00410b2f` | `dorsalClick` | `MainForm` | +0xbb |
| `0x00410e7b` | `dorsalMouseDown` | `MainForm` | +0x9f |

Literais que a rotina referencia (`mov eax, imm32` apontando
para texto no arquivo):

- `0x00424c7b` → `'dorsal'`

## O que isto muda

**A falha é de estado de interface, não de leitura da imagem.** A
cadeia medida vai do manipulador de troca de time até uma rotina que
procura um controle pelo nome e mexe na fonte dele; o que falta é o
objeto, não o byte. A região vazia em `14368636`, que o
[`offsets-novos.md`](offsets-novos.md) mede, continua sendo um fato —
mas deixou de ser a explicação, e passou a ser candidata a *causa da
causa*: um índice derivado de dado ausente pode muito bem ser o que
leva a rotina a procurar um controle que não existe.

Isso **não desbloqueia** a WTE-TASK-19: continua sem haver como levar
o oráculo comportamental além da tela de carga com as ROMs deste
repositório. O que muda é o pedido e o próximo passo — a pergunta
deixou de ser *que imagem tem esta região preenchida* e passou a ser
*por que este controle não existe*, e essa segunda é respondível com o
ferramental da fase 4 sobre um manipulador que já tem nome, endereço e
`depends_on` declarado.
