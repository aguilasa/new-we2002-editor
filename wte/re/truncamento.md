# `re/truncamento.md` — onde cada campo editável corta o texto

Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md), o
critério *comportamento de truncamento documentado por campo*. Gerado
por [`../tools/dump_truncamento.py`](../tools/dump_truncamento.py).
**Não editar à mão.** A tabela está em [`truncamento.tsv`](truncamento.tsv).

## O limite não está num lugar só

São **6 campos** com limite declarado: 3 o trazem
do `.dfm` e 3 o recebem em tempo de execução, por
`TCustomEdit::SetMaxLength`. Ler só uma das fontes acha parte e **não
anuncia** que há outra.

Dos que vêm do código, **nenhum é literal puro**: dois são expressão
sobre uma largura **medida em tempo de execução**, e a expressão tem
motivo.

| Formulário | Campo | `MaxLength` | Fonte | Expressão | Destino | Largura |
|---|---|--:|---|---|---|--:|
| `MainForm` | `edit_nombre1` | 5 | código, `0x0040cc43` | `[0x00433a10] div 2` | `TEAM_NAME_KANJI_LEN` | 95 |
| `MainForm` | `edit_nombre2` | 7 | código, `0x0040cc5b` | `[0x00433b48] - 1` | `TEAM_NAME_LEN_3` | 95 |
| `MainForm` | `edit_nombre3` | 3 | código, `0x0040cc71` | `3` | `abbreviations` | 4 |
| `jugador` | `casilla_dorsal` | 10 | dfm | `10` | — | — |
| `jugador` | `casilla_nombre` | 10 | dfm | `10` | `name` | 11 |
| `jugador` | `casilla_precio` | 3 | dfm | `3` | — | — |

## A conferência, e por que ela vale

As duas linhas de código **não medem a mesma coisa** que as do `.dfm`,
e tratá-las como se medissem custou duas divergências seguidas.

`lista_equiposChange` percorre uma tabela de **lotes** em
`0x004231a0` — 3 linhas × 6 colunas de offset, e 11 das 18 entradas
são não-zero. Para cada uma ela **anda pelo arquivo** até o registro do
time selecionado, pulando o rodapé de cada setor MODE2/2352, e grava
três campos em `0x00433a0c`: o offset do registro, a **largura** dele
em bytes, e os próprios bytes. O passo é 312 por linha e 52 por
coluna.

Logo `[0x00433a10]` é a largura da linha 0 coluna 0 e `[0x00433b48]` a
da linha 1 coluna 0. **Não são constantes** — são remedidas a cada
troca de time, e é por isso que nenhum número fixo estava certo:

```text
0x004231a0[0][0] = 2002316 = OFS_TEAM_NAME_KANJI -> TEAM_NAME_KANJI_LEN
0x004231a0[1][0] = 2003996 = OFS_TEAM_NAME_3     -> TEAM_NAME_LEN_3
```

**O gerador prova esse mapeamento, e é isso que faltava.** Ele
decodifica o endereço do operando até a entrada de `0x004231a0`, lê o
offset que está lá, e aborta se ele não for o `OFS_*` que a tabela
`DESTINOS` declara. Também confere a forma: `div 2` só vale para lote
de dois bytes por caractere, que é o kanji — o `Load` do
`we2002_core` lê `TEAM_NAME_KANJI_LEN[t]*2` bytes ali, e
`TEAM_NAME_LEN_3[t]` no outro.

**A conferência antiga batia a aritmética contra uma largura escrita à
mão, e por isso passou com o campo errado — duas vezes.** A primeira
versão declarou `raw_kanji_name` (40 bytes, `div 2` = 20) e a conta
fechou. O `compara_tela.sh --nomes` então mostrou o oráculo cortando
em cinco caracteres, e a segunda versão trocou 20 por um literal 5 —
que também estava errado, porque o limite é **por time**.

## O `dec` que faltava, e ele explica as duas versões erradas

`0x00403c0c` termina com um caso especial que vale **só** para a linha
0 coluna 0 — o lote kanji:

```text
0x00403d59  test edi,edi        ' linha == 0 ?
0x00403d6e  cmp [ebp-4],0       ' coluna == 0 ?
0x00403d95  dec  [0x00433a10 + linha*312 + coluna*52]
0x00403d98  mov  [0x00433a14 + ...], 1
```

**O lote kanji guarda a largura menos um**, e o campo `+8` recebe `1`
em vez do `2` que todos os outros recebem — esse `+8` é o modo do
decodificador de texto (`0x00403598` compara com `0x82`, o byte-líder
Shift-JIS): 1 = dois bytes por caractere, 2 = um byte.

Sem esse `dec`, `div 2` dá **um a mais**, e foi ele que sustentou as
duas versões erradas: a conta não fechava com nenhum campo do formato
porque a largura guardada não era a largura medida.

Medido em 2026-08-18 dirigindo o oráculo em **três** times de larguras
diferentes, digitando `ABCDEFGHIJKLMNOP` no `edit_nombre1`:

| time | `TEAM_NAME_KANJI_LEN` | o oráculo mostra | |
|--:|--:|---|--:|
| 2 | 6 | `ABCDE` | 5 |
| 0 | 8 | `ABCDEFG` | 7 |
| 56 | 14 | `ABCDEFGHIJKLM` | 13 |

A diferença é **constante em 1**, não proporcional — o que descarta
erro de escala e aponta um decremento. `(largura − 1) div 2` fecha nos
três, e sobre a imagem japonesa isso é `TEAM_NAME_KANJI_LEN − 1` em
**95/95** times.

Emulada a travessia do original sobre as **três** imagens, a largura
medida bate com a tabela do `we2002_core` em 95/95 times para os dois
lotes na japonesa. Fora dela o lote kanji não bate: **66/95** na
`ptbr-remaster` e **46/95** na European Deluxe — nomes latinos foram
escritos em slot de kanji e deixaram lixo depois do terminador, então
a distância ao próximo registro encurta.

**Isso era tratado como comportamento do original com aquela imagem, e
não era.** A [CORR-WTE-121](../../docs/tasks/CORR-WTE-121.md) mediu o
efeito na gravação: com a tabela, o campo cortava o nome digitado antes
de gravá-lo, e o `golden-05-nomes` reprovava em duas faixas na
`ptbr-remaster`. Os dois `LimiteDoNome*` passaram a medir a largura na
imagem, como o `0x00403c0c` mede; a tabela ficou de reserva para quando
não há imagem aberta. O lote do `edit_nombre2` bate 285/285 nas três.

## Onde as duas fontes se sobrepõem

- **`MainForm.edit_nombre1`** — **por time** -- a largura e remedida a cada troca de time, do lote OFS_TEAM_NAME_KANJI (`0x004231a0`[0][0]); 5..13 nos 95, e 5 no time 2, que e o do `compara_tela.sh --nomes`. A largura desse lote e guardada **menos um** (`dec` em `0x00403d95`, so para `0x004231a0`[0][0]), logo o limite e `TEAM_NAME_KANJI_LEN - 1`..
- **`MainForm.edit_nombre2`** — **por time** -- a largura e remedida a cada troca de time, do lote OFS_TEAM_NAME_3 (`0x004231a0`[1][0]); 7..19 nos 95, e 7 no time 2, que e o do `compara_tela.sh --nomes`..
- **`MainForm.edit_nombre3`** — o `.dfm` declara 3 e o código reafirma o mesmo em tempo de execução.

Concordam, e é por isso que aparece um só. Se um dia discordarem, o
que vale é o código: `SetMaxLength` roda depois de o formulário ser
construído e sobrescreve o que o `.dfm` pediu.

## O campo cujo `MaxLength` não governa nada

- **`jugador.casilla_dorsal`** — número de camisa, no máximo três dígitos. Quem recusa tecla é o `casilla_dorsalKeyPress`; o `MaxLength` de 10 nunca chega a valer.
- **`jugador.casilla_precio`** — campo numérico de preço. O `MaxLength` de 3 limita dígito, não texto — ver a WTE-TASK-32.

Registrado porque o número é **verdadeiro e irrelevante**: portar "o
campo corta em 10" copiaria uma medição correta para o lugar errado.
