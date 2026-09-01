---
handler: boton_dialogo_weClick
formulario: MainForm
endereco: 0x0040bd60
veredito: divergencia deliberada
---

# MainForm.boton_dialogo_weClick

Abre a imagem de CD. É o primeiro handler do projeto a sair de stub, e é a
porta de entrada de todo o resto: sem imagem carregada, nenhum handler de
edição tem estado para editar.

## Entrada

O `dialogo_we`, um `TOpenDialog` do próprio `MainForm`, com `Filter = 'ISO do
W11(.bin)|*.BIN'` e `Title = 'Abre'` vindos do DFM. O caminho escolhido pelo
usuário é a entrada; o resto vem do disco.

Também lê `data/dat.bin` — o arquivo de 145.408 B que acompanha o editor. Só a
segunda metade interessa aqui (`0x20000` em diante, 14.336 B = 7 × 2048).

**Evidência:** disassembly lido

## Saída

Três coisas, nesta ordem:

1. injeta sete setores na imagem (ver *Bytes tocados*);
2. carrega o banco inteiro para a memória;
3. escreve o nome do arquivo no `texto_dialogo_we`.

**Evidência:** diff medido

## Bytes tocados

**Grava na imagem**, e este é o achado que contraria o enunciado da
[WTE-TASK-25](../../../docs/tasks/concluidos/25-handlers-de-carga.md) — ele previa provar
que o grupo de carga não escreve nada.

```
0x2e08 +2048 x7  os sete setores de dat.bin[0x20000..], com salto de 0x130
                 entre um e o seguinte
```

O passo `0x130` = 304 = 2352 − 2048 é o salto sobre EDC/ECC e o cabeçalho do
setor seguinte. `0x2e08` = 11784 = 5 × 2352 + 24, o primeiro byte de dados do
setor 5.

Medido sobre `roms/japanese-shift-jis.bin`: **11.952 bytes em 7 faixas**,
`11796..13831`, `14136..16183`, `16488..18535`, `18840..20887`,
`21192..23239`, `23544..25591`, `25896..26527`. As faixas começam em 11796 e
não em 11784 porque os doze primeiros bytes já batiam.

**As duas faixas do arranque que ficaram sem explicação desde a WTE-TASK-25
fecharam em 2026-08-20**, e as duas eram remendos literais:

| endereço | quem grava | o quê |
|---|---|---|
| `2012984..2012985` | `0x0040c19e` **e** `0x00411616` | se o par de vínculo lá for `(102, >22)`, troca por `(0, 27)` |
| `1921862..1921862` | só `0x00411616`, no `FormShow` | grava zero, sem condição |

**Elas estavam escondidas à plena vista.** O endereço é *imediato* no `.text`
(`push 0x1eb738`, `push 0x1d5346`), e a busca que as procurou olhava referência
a `OFS_LINK_ML` — a única que existe é o `push 0x1eb608` de `0x004042fc`, e
essa só lê. Procurar pelo nome do offset nunca acharia um literal.

**Os dois ficam FORA da guarda da sentinela.** O `je` de `0x0041158e`, que pula
a injeção de sete setores quando a imagem já foi injetada, salta para
`0x00411616` — que é onde os remendos começam. Rodam em toda abertura.

**O do vínculo é conserto de dado, e dá para ver o quê.** O par `(102, 23)` do
slot 13 do clube de ML 5 aponta para um bloco do time 102, e o time 102 não tem
jogador *non-contract* nenhum — é referência pendurada. Mandá-la para `(0, 27)`
a aponta para o bloco 4, e o contador de blocos livres cai de 2 para 1. A
condição o torna idempotente: depois de gravado, `b0` vale 0.

**O do byte solto continua sem significado**, e portá-lo assim é legítimo: a
especificação está completa (endereço fixo, sem condição, valor zero). O que
não se pode é dar-lhe um nome inventado. Fica no setor 817, dentro do payload,
sem offset nomeado por perto — o mais próximo é o `OFS_FLAG_SHAPE_COPY_1`, 7142
bytes adiante.

Portados no `we2002_estado` (`PatchDeVinculoDeArranque`,
`PatchDeByteSoltoDeArranque`). Com isso **nenhum roteiro do gate declara faixa
`conhecida:`** — ver [`../../tests/roteiros/README.md`](../../tests/roteiros/README.md).

**Evidência:** diff medido

## Pré-condições

`data/dat.bin` tem de existir e ser legível. O original o resolve a partir do
diretório corrente e, se não achar, mostra `O arquivo dat.bin esta fora do seu
diretorio` (literal em `0x00424cb1`).

A injeção é **idempotente por sentinela**: o byte em `0x2e14` valendo `0xFC`
significa "já injetado", e o bloco inteiro é pulado. Sem isso, reabrir a mesma
imagem regravaria os mesmos bytes.

**Evidência:** disassembly lido

## Comportamento de erro

O original não trata falha de leitura da imagem além da checagem de tamanho, e
a checagem de tamanho é **só aviso** — ele carrega assim mesmo. O port devolve
`False` de `AbreImagem` quando o arquivo não existe e escreve isso no rótulo.

**Evidência:** observação de tela

## Notas

**Este caminho não é exercitado pelo gate**, e não pode ser: sem window
manager no `:99` o GTK2 nunca considera a janela ativa, então o lado port não
recebe teclado e não digita caminho em diálogo nenhum (WTE-TASK-13). Quem
carrega no gate é o `MainForm.FormShow`, pela linha de comando — e passa pelo
mesmo `AbreImagem`, que é onde a injeção mora. O `.exe` tem os dois trechos de
injeção duplicados, um aqui e outro no `FormShow`; o port tem um só.

**Veredito `divergencia deliberada` desde 2026-08-24**, e as duas razões que o
mantinham `aberto` caíram antes disso. A frase antiga dizia *"porque as duas
faixas de cima não têm explicação medida, e porque a carga da tela (nome,
barras, elenco) é o resto da WTE-TASK-25"*. As faixas fecharam em 2026-08-20, e
a seção acima já as explica byte a byte; a carga da tela foi medida em
2026-08-23 pelo `compara_tela.sh 2 68`, que bate em pixel nas barras, na
bandeira e no uniforme dos dois times.

**O que sobra não é pergunta em aberto, é uma diferença de estrutura que o port
tem por decisão** — e é isso que muda o veredito em vez de o manter.

**1. O port tem uma rota de injeção onde o original tem duas.** O `.exe`
duplica o trecho de injeção de sete setores, um aqui e outro no `FormShow`; o
port tem um só, o `AbreImagem`, chamado pelos dois. É desvio consciente, com
ganho declarado: um lugar para corrigir em vez de dois cópia-e-cola.

**2. E é justamente por isso que este ponto de entrada não tem régua própria, e
não pode ter.** Sem window manager o gtk2 não dá foco de teclado à janela, então
o lado port não digita caminho em `TOpenDialog` nenhum
([WTE-TASK-13](../../../docs/tasks/concluidos/13-trace-de-eventos.md)); quem carrega no
gate é o `MainForm.FormShow`, pela linha de comando. O
[`golden-01-arranque`](../../tests/roteiros/golden-01-arranque.txt) verifica o
corpo compartilhado, que é onde a injeção e os dois remendos moram — o que não
verifica é o `Execute` do diálogo, que é o único trecho não comum aos dois.

Chamar isso de `implementado` daria por medido o trecho que nenhum gate alcança;
chamar de `aberto` afirmaria pergunta onde há decisão. As duas divergências vão
para a [WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md), junto
com as do `FormShow`, que é o irmão pelo qual este é coberto.

E a
[cobertura medida](../fase-4-cobertura.tsv) confirma o que se afirma aqui: este
handler dá **zero** linha nos 16 roteiros. A régua não o alcança, e o registro
diz isso em vez de o insinuar.
