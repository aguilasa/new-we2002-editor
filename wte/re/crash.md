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
objeto, não o byte.

**A causa foi medida depois, e está em [`crash-causa.md`](crash-causa.md)** (CORR-WTE-044). O resumo, porque ele aposenta duas
frases que este documento carregou até 2026-08-10:

- **o controle existe.** Os 23 `dorsalN` estão vivos no `MainForm`,
  todos `TStaticText`, todos com `Font` não nula. Quem não presta é o
  ponteiro guardado em `0x004335e4`, que a carga do time sobrescreve
  com dado de uma tabela vizinha (`0x00010001`) — valor que passa no
  `if (obj != nil)` da rotina e cujo `+0x68` lê zero;
- **a região vazia em `14368636` não é a causa, nem a causa da
  causa.** As duas imagens leem essa mesma faixa ao trocar de time, e
  só uma delas trava. O [`offsets-novos.md`](offsets-novos.md)
  continua medindo um fato; ele só não explica este.

E **desbloqueia** a WTE-TASK-19, com ressalva: o oráculo é dirigível
com `roms/japanese-shift-jis.bin` — mesmo roteiro, zero violações de
acesso —, e não com a `golden-european-deluxe.bin`. As três ressalvas
que acompanham o contorno estão no `crash-causa.md`.
