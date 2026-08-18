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
que também estava errado, e por um motivo que só a tela produz: com
`AB-C.D E` o campo corta em **seis**, e o sexto caractere é um
**espaço**. Régua que não distingue `ABC.D ` de `ABC.D` não mede
truncamento; mede tinta.

Emulada a travessia do original sobre as duas imagens, a largura
medida bate com a tabela do `we2002_core` em **95/95** times para os
dois lotes na imagem japonesa. Na European Deluxe o lote kanji bate em
46/95 — nomes latinos foram escritos em slot de kanji e deixaram lixo
depois do terminador, então a distância ao próximo registro encurta.
É comportamento do original com aquela imagem, não defeito do port.

## Onde as duas fontes se sobrepõem

- **`MainForm.edit_nombre1`** — **medido na tela** (compara_tela.sh --nomes, 2026-08-18): 5. O lote esta provado -- OFS_TEAM_NAME_KANJI, `0x004231a0`[0][0] -- e a travessia emulada da 6, **um a mais**. A conta nao fecha e a tela vence; ver a CORR-WTE-064.
- **`MainForm.edit_nombre2`** — **por time** -- a largura e remedida a cada troca de time, do lote OFS_TEAM_NAME_3 (`0x004231a0`[1][0]); 7..19 nos 95, e 7 no time 2, que e o do `compara_tela.sh --nomes`.
- **`MainForm.edit_nombre3`** — o `.dfm` declara 3 e o código reafirma o mesmo em tempo de execução.

Concordam, e é por isso que aparece um só. Se um dia discordarem, o
que vale é o código: `SetMaxLength` roda depois de o formulário ser
construído e sobrescreve o que o `.dfm` pediu.

## O campo cujo `MaxLength` não governa nada

- **`jugador.casilla_dorsal`** — número de camisa, no máximo três dígitos. Quem recusa tecla é o `casilla_dorsalKeyPress`; o `MaxLength` de 10 nunca chega a valer.
- **`jugador.casilla_precio`** — campo numérico de preço. O `MaxLength` de 3 limita dígito, não texto — ver a WTE-TASK-30.

Registrado porque o número é **verdadeiro e irrelevante**: portar "o
campo corta em 10" copiaria uma medição correta para o lugar errado.
