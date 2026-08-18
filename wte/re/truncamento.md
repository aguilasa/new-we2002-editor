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
sobre a largura do campo de destino, e a expressão tem motivo.

| Formulário | Campo | `MaxLength` | Fonte | Expressão | Destino | Largura |
|---|---|--:|---|---|---|--:|
| `MainForm` | `edit_nombre1` | 5 | código, `0x0040cc43` | `[0x00433a10] div 2` | — | — |
| `MainForm` | `edit_nombre2` | 19 | código, `0x0040cc5b` | `[0x00433b48] - 1` | `mixed_case_name` | 20 |
| `MainForm` | `edit_nombre3` | 3 | código, `0x0040cc71` | `3` | `abbreviations` | 4 |
| `jugador` | `casilla_dorsal` | 10 | dfm | `10` | — | — |
| `jugador` | `casilla_nombre` | 10 | dfm | `10` | `name` | 11 |
| `jugador` | `casilla_precio` | 3 | dfm | `3` | — | — |

## A conferência, e por que ela vale

A coluna **Largura** não sai do `.exe`: sai de
[`../src/we2002_team.pas`](../src/we2002_team.pas) e
[`../src/we2002_player.pas`](../src/we2002_player.pas) — a camada de
dados, que é byte-idêntica ao `ed.exe`. É o **outro lado da conta**, e
o gerador aborta se os dois não casarem:

```text
mixed_case_name   20 bytes  -> menos 1 -> 19   o byte do terminador
abbreviations[0]   4 bytes  -> literal  3      idem
```

**Ela confere a aritmética, não o mapeamento — e a diferença custou uma
divergência.** A primeira versão desta ferramenta declarava
`raw_kanji_name` (40 bytes) como destino do `edit_nombre1`, o que dava
`40 div 2 = 20`, e a conferência **passou**: a conta fecha. O
`compara_tela.sh --nomes` então mediu na tela do oráculo — digitando
`AB-C.D E`, o campo mostra `ABC.D`, **cinco** caracteres. Logo
`[0x00433a10]` vale 10 e o destino é outro campo, que **não foi
medido**.

A tabela `DESTINOS` do gerador é escrita à mão, e é por isso que ela
aceita `None`: emitir `nao medido` é o único jeito de a conferência não
passar pelo motivo errado outra vez.

## Onde as duas fontes se sobrepõem

- **`MainForm.edit_nombre1`** — valor medido na tela (compara_tela.sh --nomes, 2026-08-18); o destino no formato continua **nao medido**.
- **`MainForm.edit_nombre3`** — o `.dfm` declara 3 e o código reafirma o mesmo em tempo de execução.

Concordam, e é por isso que aparece um só. Se um dia discordarem, o
que vale é o código: `SetMaxLength` roda depois de o formulário ser
construído e sobrescreve o que o `.dfm` pediu.

## O campo cujo `MaxLength` não governa nada

- **`jugador.casilla_dorsal`** — número de camisa, no máximo três dígitos. Quem recusa tecla é o `casilla_dorsalKeyPress`; o `MaxLength` de 10 nunca chega a valer.
- **`jugador.casilla_precio`** — campo numérico de preço. O `MaxLength` de 3 limita dígito, não texto — ver a WTE-TASK-30.

Registrado porque o número é **verdadeiro e irrelevante**: portar "o
campo corta em 10" copiaria uma medição correta para o lugar errado.
