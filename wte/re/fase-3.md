# `re/fase-3.md` — o aceite da camada de dados

**Gerado por [`wte/tools/compare_dumps.py`](../tools/compare_dumps.py)
— não editar à mão.** Evidência em [`fase-3.tsv`](fase-3.tsv).

Produto da [WTE-TASK-20](../../docs/tasks/concluidos/20-round-trip-headless.md). É
o primeiro momento em que o projeto afirma algo **verificado** sobre
dados, e não sobre forma.

O irmão é [`fase-3-fechamento.md`](fase-3-fechamento.md), da
WTE-TASK-21: aqui se mede se **os valores batem**; lá, **quem escreveu**
**o código que os produz** e **quem o consome**. Dois arquivos porque
são dois geradores — o mesmo arquivo escrito por dois seria duplicação
sem guarda.

## O oráculo aqui é o de formato

Não é o `wte.exe` — ele é o oráculo de **comportamento**, e a pergunta
desta task é de **formato**. Ele é dirigível desde a
[CORR-WTE-044](../../docs/tasks/concluidos/CORR-WTE-044.md), com
`roms/japanese-shift-jis.bin`, e mesmo assim não sabe dizer o que os
bytes significam: mostra o que o editor **faz**, não o que o campo **é**
([`crash-causa.md`](crash-causa.md) explica por que a ROM é essa).

O oráculo daqui é o **`we2002_core`** deste repositório, cujo
`Load`/`Save` já é byte-idêntico ao `ed.exe` nas duas ROMs. A pergunta
que ele responde é *o que significam estes bytes*, e é exatamente a
desta task.

**O par é bilíngue de propósito:** o `fpc` lê o Pascal gerado, o `g++`
lê o C++ original. Dois dumpers na mesma linguagem esconderiam erro de
leitura de literal — ele apareceria idêntico dos dois lados. É a mesma
razão dos dois `test_offsets.*` da WTE-TASK-16.

## Leitura: `diff` dos dois dumps

| ROM | o que valida | linhas | divergências |
|---|---|---:|---:|
| `golden-european-deluxe.bin` | offsets, nomes latinos e os ramos de mapeamento do codec | 66498 | **0** |
| `japanese-shift-jis.bin` | o ramo padrao do codec: katakana vira espaco | 66498 | **0** |
| `ptbr-remaster.bin` | os mesmos ramos do codec que a europeia, com oráculo vivo no wte/ | 66498 | **0** |

**Zero divergência nas duas ROMs.** O critério aqui não admite
faixa conhecida, diferente do golden test de imagem do `newWe2002`:
isto é leitura pura, não há comportamento indefinido para
preservar, e qualquer byte diferente seria defeito do transpilador.

O formato do dump é `chave = valor`, uma por linha, com vetor de bytes
em `<n>:<hex>` cortado no último byte não-zero — forma sem perda, já
que o resto é zero por definição, e que não gasta 500 caracteres por
URL vazia.

### As duas medidas de cobertura

Dump igual dos dois lados não prova nada se o dado for todo zero. Por
isso o TSV conta, por ROM, quanto do dado exercitado é não-trivial:

| ROM | `raw_kanji_name` com byte ≥ `0x80` | `kanji_name` decodificado não-vazio | `squad_numbers` não zerados |
|---|---:|---:|---:|
| `european-deluxe` | 95 | 95 | 64 |
| `japanese` | 95 | 0 | 64 |
| `ptbr-remaster` | 95 | 95 | 64 |

A primeira coluna conta o campo **cru** com pelo menos um byte alto,
que é o que caracteriza Shift-JIS de dois bytes; a segunda conta a
saída do `KanjiToAscii` que não é vazia nem só espaço. As duas, e não
uma: contar simplesmente "campo não vazio" dava 97 nas duas ROMs por
coincidência — os 97 registros existem em ambas — e não separava
release nenhuma.

O **bitfield de `SquadNumbers`** é o caso que mais precisa disso. O
Pascal não tem o bitfield do C++: tem um layout escrito à mão
([`tipos.md`](tipos.md), decisão 2), quatro palavras de 32 bits com
campos de 5 bits alocados do bit menos significativo para cima. O dump
emite as **duas** formas — os 23 números desempacotados e as quatro
palavras cruas —, então um erro de deslocamento não tem por onde
passar despercebido.

### O codec: a premissa da task estava trocada

O enunciado da WTE-TASK-20 diz que a ROM japonesa é *o único teste
real do codec de texto*. **Medido, é o contrário.**

As duas ROMs têm 95 campos crus com byte alto, e
o que sai do `KanjiToAscii` é oposto: **95 de 95**
decodificam para texto na European Deluxe, contra **0 de 95**
na japonesa.

A razão está no próprio codec, portado verbatim de
`edDlg.cpp:732-809`: ele só conhece o byte de chefe **130**
(`0x82` — latino de largura dupla e dígitos) e **129** (`0x81`, o
ponto). Tudo o mais cai no ramo padrão e vira espaço.

- a European Deluxe guarda `82 68 82 8e ...` → `Inter`, `Juventu`;
- a japonesa guarda `83 41 83 43 ...`, que é **katakana** — e vira
  espaço.

Ou seja: quem exercita os ramos de mapeamento é a **europeia**; a
japonesa exercita o **ramo padrão**. As duas são necessárias, por
motivos trocados em relação ao que a task supunha, e nenhuma das
duas sozinha cobre o codec. Isso não é defeito do port: os dois
lados concordam byte a byte, e o `ed.exe` mostra os mesmos espaços.

## Gravação: round-trip byte a byte

| ROM | Pascal × C++ | Load+Save × original |
|---|---:|---|
| `european-deluxe` | **0** bytes | 270 bytes em 4 faixa(s) |
| `japanese` | **0** bytes | 1249 bytes em 15 faixa(s) |
| `ptbr-remaster` | **0** bytes | 41 bytes em 9 faixa(s) |

**As duas gravações são byte a byte idênticas.**

A segunda coluna **não é defeito, e é a ressalva que a task manda
registrar**: `Load`+`Save` sem editar nada não devolve a imagem
intacta, e não deveria. O `Save` reconstrói as squads all-star a partir
dos links (`OFS_PLAYER_ATTR_8`), e o original troca os dois primeiros
cobradores de cada clube de ML — o `Load` lê o par trocado e o `Save`
grava na ordem declarada. O `ed.exe` faz o mesmo; gravar duas vezes
volta ao início. O que esta linha mede é que os **dois lados fazem
isso igual**.

| ROM | sidecar `_url.txt` | igual dos dois lados |
|---|---:|:---:|
| `european-deluxe` | 1911 B | sim |
| `japanese` | 1911 B | sim |
| `ptbr-remaster` | 1911 B | sim |

O sidecar entra porque o `Save` o escreve — herdado do `OnWriteCD`
original — e porque ele é a decisão 5 do [`tipos.md`](tipos.md): 1.911
linhas terminadas em `#10`, sem `#13` e sem BOM. Um `\r\n` de um dos
lados apareceria aqui.

## O que isto não mede

- **As faixas que nenhum `OFS_*` explica.** Não são os `OFS_*` da
  [WTE-TASK-19](../../docs/tasks/concluidos/19-os-50-offsets-restantes.md) — esses
  moram todos no `Offsets.hpp`, têm lado C++ e estão dentro deste diff.
  São as regiões que o `wte.exe` endereça e que este repositório nunca
  nomeou, a maior delas a do uniforme. Sem lado C++, nenhum diff
  Pascal × C++ as alcança; nomeá-las é fase 4 e 5.
- **Comportamento.** Isto é a camada de dados, não os 96 handlers. O
  gate deles é a WTE-TASK-22, e o oráculo em que ele se apoia é
  dirigível desde a CORR-WTE-044, com a ROM japonesa.
- **O `Load` do sidecar.** Nenhum dos dois lados lê `_url.txt` no
  `Load` — isso é do app —, então `players[].url` sai zerado dos dois e
  o dump concorda por vacuidade nesse campo.

## Refazer

```sh
python3 wte/tools/compare_dumps.py --medir   # ~1,9 GB de cópia
python3 wte/tools/compare_dumps.py --check   # confere este arquivo
```

A medição **não** roda no `make -C wte check`: são quatro cópias de
~474 MB e uns dois minutos. O `--check` confere o texto contra o TSV,
que é o que o resto da bateria faz. Para reexecutar de dentro da
bateria: `WTE_ROUNDTRIP=1 make -C wte test`.
