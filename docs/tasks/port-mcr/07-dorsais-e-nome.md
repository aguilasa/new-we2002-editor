---
id: MCR-TASK-07
title: "`numbers.py` e `text.py` — os 5 bits e o cp932"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-05"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §1.5"
status: concluído
---

# MCR-TASK-07: Dorsais e nome

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §1.5 e §1.6.
- **O dorsal está gravado duas vezes** e os dois concordam 23/23 na fixture. É
  a melhor tripwire do plano, e custa uma subtração.
- **O nome de 10 bytes é cp932**, medido: o slot 0 é `50 a5 83 57 ae b0 d9 83
  59 00` = `P･ジｮｰﾙズ`, mistura de ASCII, katakana meia-largura e Shift-JIS de 2
  bytes. O `KanjiToAscii` do `we2002_core` devolve **cinco espaços** para ele; o
  upstream assume ASCII e ainda filtra por `[^a-zA-Z.]`.
- O campo **não é cadeia terminada em NUL**: os slots **5** e **20** usam os
  10 bytes — são dois na fixture, e o `text.py --check` marca os dois.

---

- **`[0,5,2,7,4,1]` é a posição DENTRO DO BYTE, não o offset dentro do grupo.**
  Medido na MCR-TASK-06, e custou um vermelho: o offset do valor `j` dentro do
  grupo de 4 bytes é `5·(j mod 6)` — 0, 5, 10, 15, 20, 25 —, que cai nos bytes
  0, 0, 1, 1, 2, 3 com os deslocamentos 0, 5, 2, 7, 4, 1. Usar a tabela
  documentada **como se fosse o offset do grupo** devolve
  `1 5 1 26 9 1 6 11 18 …` na fixture: números que parecem dorsais e não são.
  A leitura certa dá `1 5 4 3 2 7 6 11 10 9 8 16 17 13 19 22 12 18 20 14 15 21 23`,
  que é o que a §1.5 do plano registra. Há uma leitura mínima de referência em
  `attributes.shirt_numbers_from_table()`, escrita só para a tripwire; o
  `numbers.py` é quem a implementa de verdade, com domínio e gravação.
- **O upstream monta os bytes `+0..+3` concatenando dígitos hexadecimais como
  string**, não somando pesos — `cuartobite = idfeedoutside.Text &
  idheigth2.Text`. É onde moram o dorsal (5 bits) e o `out_of_position`, e é
  por isso que os pesos `id*` daqueles quatro bytes **não** são
  `índice << shift` como os dos oito seguintes (`idfeedoutside` vale `[0, 9]`).
  Se algo do dorsal do upstream não fechar, é aqui que ele difere do nosso.

---

## Objetivo

`numbers.py` (leitura e gravação dos 24 valores de 5 bits) e `text.py` (o nome
de 10 bytes ↔ `str`).

---

## Critério de conclusão

- [x] `numbers.py` lê os 4 grupos de 4 B com `int.from_bytes(..., "little")` e
      o offset **`5·(j mod 6)`** dentro do grupo, somando 1; grava subtraindo 1.
      **Simetria obrigatória** — o `+1` sem `−1` do upstream é divergência
      registrada.
      *(Esta linha dizia "os deslocamentos `[0,5,2,7,4,1]`" até 2026-09-07, e
      repetia a confusão que a MCR-TASK-06 mediu: aquela tabela é o
      deslocamento **dentro do byte**, e usá-la como offset do grupo devolve
      números plausíveis e errados. As duas formas são equivalentes só quando
      a do byte vem acompanhada do índice do byte — `5·(j mod 6)` cai nos
      bytes 0,0,1,1,2,3 exatamente naqueles deslocamentos. O
      `numbers.self_check` mantém as duas lado a lado.)*
- [x] Os 23 dorsais da tabela batem com os 23 do bit-field do registro:
      **23/23**.
- [x] `text.py` decodifica os 23 nomes da fixture em cp932 sem exceção, e
      `encode(decode(b)) == b` nos 23 — inclusive os slots 5 e 20, que enchem
      os 10 bytes.
- [x] Nome maior que 10 bytes **recusa**, não trunca em silêncio.
- [x] Um comentário no módulo dizendo por que o `TextCodec` do `we2002_core`
      **não** serve aqui, com o exemplo do slot 0.
- [x] Caso vermelho: remover o `−1` da gravação rompe o par dos dois
      codificadores.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

`tools/mcr/numbers.py` (323 linhas) e `tools/mcr/text.py` (338 linhas), en-US.
Os dorsais leem `+1` e gravam `−1` simetricamente, por read-modify-write; os
nomes vão e voltam em **cp932** com recusa em vez de truncagem. **23/23** na
tripwire e **23/23** no `encode(decode(b)) == b` dos nomes.

Três coisas que a execução mediu: a tabela `[0,5,2,7,4,1]` do próprio critério
estava sendo citada como offset de grupo; o `TextCodec` não perde *alguns*
nomes, perde **os 23**; e um check verde não provava o que dizia provar,
porque a fixture não tem o caso que o distingue.

### Os dorsais

```
$ python3 tools/mcr/numbers.py work/mcr-entrada.mcr --check
numbers.py --check: 23/23 shirt numbers agree between the table and the
player records
```

A leitura da fixture bate com a §1.5 do plano —
`1 5 4 3 2 7 6 11 10 9 8 16 17 13 19 22 12 18 20 14 15 21 23` — e o slot 24,
não usado, guarda 0 e lê 1. Reencodar a tabela da fixture **não muda um byte**.

**O offset dentro do grupo é `5·(j mod 6)`, não `[0,5,2,7,4,1]`.** O
`_group_and_offset` carrega o porquê, e o `self_check` mantém as duas leituras
lado a lado — uma asserção de que a primeira **cai** nos deslocamentos da
segunda, e outra de que os dois números **não são iguais**. O texto do critério
desta task repetia a confusão e foi corrigido.

Três invariantes que o RMW compra e o controle N3 cobra: os **2 bits que
sobram** em cada grupo de 32 (6 × 5 = 30) sobrevivem à gravação, o **slot 24**
fica intacto quando se gravam só os 23, e mudar um slot não mexe nos outros 23.

### Os nomes

```
$ python3 tools/mcr/text.py work/mcr-entrada.mcr --check
text.py --check: 23/23 names re-encode to the same bytes
```

Os 23 decodificam em cp932 sem exceção; os slots 5 (`ジｮｰ･ﾛﾚﾝｿﾝ`) e 20
(`ガﾘｽ･ﾛバｰｽ`) enchem os dez bytes sem terminador — **dois**, não um, e é o
`--check` que os conta. Nome maior que dez bytes **recusa** dizendo de quantos
precisava, porque truncar cortaria um caractere de dois bytes ao meio.

**E o `TextCodec` não serve — agora demonstrado, não afirmado.** O módulo traz
uma transcrição do `KanjiToAscii` de `src/core/TextCodec.cpp`, usada **só** para
ser mostrada falhando: ele lê o campo **de dois em dois bytes** e só reconhece
pares que começam em `0x82` (letras e dígitos) ou o par `0x81 0x42` (o ponto);
todo o resto cai no ramo default, que emite espaço. Este campo mistura katakana
meia-largura de **1 byte** com Shift-JIS de 2, então nenhum par acerta.

**Medido: 23 de 23 nomes voltam como espaços, e nenhum é reproduzido.** O
`TextCodec` continua certo para o que foi escrito — o nome de time da imagem de
CD, que é mesmo par de `0x82`.

### Os controles negativos

Seis defeitos plantados numa cópia em `/tmp`:

| módulo | defeito plantado | resultado |
|---|---|---|
| `numbers` | tirar o `−1` da gravação | 🔴 7 falhas |
| `numbers` | usar `[0,5,2,7,4,1]` como offset do grupo | 🔴 7 falhas |
| `numbers` | montar a tabela do zero em vez de RMW | 🔴 2 falhas (bits sobrando, slot 24) |
| `text` | tratar o nome como ASCII | 🔴 16 falhas |
| `text` | parar no primeiro NUL | 🔴 1 falha |
| `text` | truncar em vez de recusar | 🔴 2 falhas |

**6/6 vermelhos, `rc=1` em todos.**

### Arquivos criados/modificados

- `tools/mcr/numbers.py` — **novo**
- `tools/mcr/text.py` — **novo**
- `docs/tasks/port-mcr/08-formacao-e-dominios.md` — o precedente do RMW
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — o guard externo do harness
- `docs/tasks/port-mcr/progresso.md` — a linha desta task

### Problemas encontrados

**1. Um check verde que não provava nada.** O controle "parar no primeiro NUL"
(`split(b"\0")[0]` no lugar de `rstrip`) passou **verde** na primeira rodada.
Motivo: **nenhum dos 23 nomes da fixture tem NUL no meio**, e os slots 5 e 20
não têm NUL nenhum — para todos eles as duas leituras dão o mesmo resultado. A prosa
dizia "o campo não é cadeia terminada em NUL" e o teste não sabia disso.

Consertado com um caso sintético — `AB\x00CD` seguido de padding — que é o
único formato onde as duas leituras divergem. O controle passou a ficar
vermelho.

**Vale para as tasks seguintes:** *a fixture é uma amostra, não o domínio.* Um
guard escrito só contra ela concorda com o defeito sempre que a amostra não o
alcança, e isso não aparece em lugar nenhum — o check fica verde.

**2. O harness morreu de traceback três vezes nesta task.** `encode_table`
dentro do laço de "muda um slot", `read_all` e `decode_name` na região da
fixture — os três levantam quando há defeito, e um `ok(...)` cuja expressão
levanta mata a corrida. É a quinta ocorrência do mesmo padrão no ciclo
(MCR-TASK-04, MCR-TASK-06 e três aqui).

Passar chamada por chamada pelo `attempt()` conserta **uma de cada vez**, e foi
o que coube aqui. O conserto durável é um **guard externo** em volta do corpo
inteiro do `self_check`; a linha foi escrita **no arquivo da MCR-TASK-10**, que
é quem monta o harness compartilhado.

**3. A primeira medição do `TextCodec` disse 5 de 23, e são 23 de 23.** O
`kanji_to_ascii` emite `"\0"` para o par NUL, e `str.strip()` **não** remove
`\0` — só espaço em branco. Contando com `strip()` sozinho, 18 nomes pareciam
"parcialmente legíveis" quando na verdade eram espaços seguidos de NULs. Com
`strip("\0 ")` o número certo aparece, e o check passou a afirmar os dois
lados: **blanks all 23** e **reproduces none of them**.

**4. A fixture não foi tocada** — tudo sobre `work/mcr-entrada.mcr`; digest
`e53f4895…c47546` inalterado.

