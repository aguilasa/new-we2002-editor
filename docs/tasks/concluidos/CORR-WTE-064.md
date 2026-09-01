---
id: CORR-WTE-064
title: "Correção: o lote do `edit_nombre1` está provado e a conta dá um a mais que o oráculo"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-064: um a mais, e não é o campo errado desta vez

## Problema identificado

A [CORR-WTE-061](/docs/tasks/concluidos/CORR-WTE-061.md) fechou o que se propunha: o
`0x00433a10` deixou de ser global anônima e passou a ter lote nomeado. Ela
também mediu, na mesma passagem, que **a derivação dá 6 e o oráculo corta em
5** para o time 2.

Não é mais "o destino não foi medido". O destino está provado por três lados
independentes, e é a *aritmética* que sobra um.

## Evidência

O lote, decodificado do binário e não declarado à mão:

```
$ python3 wte/tools/dump_truncamento.py --check
truncamento: ... (o gerador aborta se [0x00433a10] deixar de ser
             0x004231a0[0][0], que vale 2002316 = OFS_TEAM_NAME_KANJI)
```

A travessia do original (`0x00403c0c`), emulada byte a byte com o pulo de setor
do `0x00403388`, sobre `roms/japanese-shift-jis.bin`:

```
time 2, lote kanji : inicio 2003952  bytes 83 45 83 46 81 5B 83 8B 83 59 00 00
                     largura = 12    ->  sar 1  ->  6
time 2, lote name3 : inicio 2004968  bytes 57 41 4C 45 53 00 00 00
                     largura = 8     ->  dec    ->  7
```

E a tela, com `A B-C.DEFG` — texto escolhido para que o sexto caractere seja um
`D` **visível**:

| campo | oráculo | derivação |
|---|---|---|
| `edit_nombre1` | `A BC.` — **5** | 6 |
| `edit_nombre2` | `A BC.DE` — **7** | 7 ✔ |
| `edit_nombre3` | `ABC` — 3 | 3 ✔ |

**O mesmo modelo acerta o segundo campo e erra o primeiro por um.** É isso que
faz este resto valer uma correção própria em vez de uma nota: se o modelo
estivesse errado, o `edit_nombre2` não fecharia — e ele fecha, inclusive
corrigindo os 19 que o port usava.

## Causa raiz

**Não medida.** O que já foi descartado, para a próxima passagem não repetir:

- **não é o índice do time.** Nenhum dos 96 índices de salto produz
  `(kanji div 2, name3 - 1) == (5, 7)`; a varredura está no Log da
  CORR-WTE-061;
- **não é a imagem.** As duas ROMs dão largura 12 para o time 2, e a cópia de
  trabalho do oráculo é byte-idêntica à ROM na região do lote;
- **não é o pulo de setor.** O `fixup` do `0x00403388` cai exatamente em
  2003624 → 2003928, que é o `OFS_TEAM_NAME_KANJI_A` que o `we2002_core` já
  usava como salto manual. Os dois concordam;
- **não é a atribuição de campo.** O `campos.tsv` põe `edit_nombre1` em
  `MainForm+0x35c`, que é o alvo do `SetMaxLength` de `0x0040cc43`, o que
  recebe `[0x00433a10] div 2`;
- **não é outro escritor.** `0x0040cbc8` é chamado só de `0x0040d1c3`, dentro
  do `lista_equiposChange`, e a leitura acontece na mesma função logo depois.

Sobra o corpo de `0x00403c0c`: `esi` nasce 1, os dois laços contam, e o campo
`+4` recebe `lea eax,[esi+1]`. Para o time 2 isso dá 12, e para dar 5 depois do
`sar` teria de dar 10 ou 11. **Todas as larguras do lote kanji são múltiplas
de 4**, então `div 2` nunca é ímpar — o que sozinho mostra que o modelo do
contador está errado em algum ponto, e não que falte um caso especial.

## Correção

1. reler `0x00403c0c` **instrução a instrução**, sem paráfrase, com atenção a
   onde `esi` é incrementado em relação ao `getc` — a hipótese mais barata é o
   laço de salto deixar o cursor uma posição diferente da que a emulação
   assume, e o erro só aparecer no lote de dois bytes por caractere;
2. se a releitura não fechar, instrumentar: rodar o oráculo sob o Wine com um
   `WINEDEBUG` de chamadas de arquivo, ou medir a tela em **três times de
   larguras diferentes** e ver se a diferença é constante em 1 ou proporcional;
3. com a conta fechada, tirar o literal do
   [`LimiteDoNome1`](../../../wte/src/impl/ep2002_mainform.aux.inc) e a entrada de
   `CONTRADIZ_A_TELA` do
   [`dump_truncamento.py`](../../../wte/tools/dump_truncamento.py).

Se a releitura mostrar que a largura do lote kanji **não** é derivável, o
literal fica — mas aí com a razão medida, e não com "a conta dá outro número".

### Arquivos

- [`wte/tools/dump_truncamento.py`](../../../wte/tools/dump_truncamento.py) — a
  tabela `CONTRADIZ_A_TELA`
- [`wte/src/impl/ep2002_mainform.aux.inc`](../../../wte/src/impl/ep2002_mainform.aux.inc)
  — o `LimiteDoNome1`
- [`wte/re/spec/MainForm.lista_equiposChange.md`](../../../wte/re/spec/MainForm.lista_equiposChange.md)

---

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-18

**Resumo do que foi feito:**

**A conta fechou, e o que faltava era um `dec`.** O passo 1 da correção — reler
`0x00403c0c` instrução a instrução — foi o que achou: a rotina termina com um
caso especial testado em `0x00403d59`, e ele vale **só** para a linha 0 coluna
0, que é exatamente o lote kanji:

```text
0x00403d59  test edi,edi        ' linha == 0 ?
0x00403d6e  cmp  [ebp-4],0      ' coluna == 0 ?
0x00403d95  dec  [0x00433a10 + linha*312 + coluna*52]
0x00403d98  mov  [0x00433a14 + ...], 1
```

**O lote kanji guarda a largura menos um**, e o campo `+8` recebe `1` em vez do
`2` que todos os outros recebem — esse `+8` é o modo do decodificador de texto
(`0x00403598` compara com `0x82`, o byte-líder Shift-JIS): 1 = dois bytes por
caractere, 2 = um byte. Como a largura é `TEAM_NAME_KANJI_LEN × 2`, o `div 2`
do valor decrementado dá exatamente `TEAM_NAME_KANJI_LEN − 1`.

**A releitura sozinha não teria bastado, e o passo 2 é que apontou para onde
olhar.** Antes de achar o `dec` eu medi o oráculo em **três** times de larguras
diferentes, digitando `ABCDEFGHIJKLMNOP` no `edit_nombre1`:

| time | `TEAM_NAME_KANJI_LEN` | derivação ingênua | o oráculo mostra | |
|--:|--:|--:|---|--:|
| 2 | 6 | 6 | `ABCDE` | 5 |
| 0 | 8 | 8 | `ABCDEFG` | 7 |
| 56 | 14 | 14 | `ABCDEFGHIJKLM` | 13 |

**A diferença é constante em 1, não proporcional.** Isso descartou erro de
escala e de contador — um contador errado daria erro proporcional ao número de
laços — e mandou procurar um decremento único. Foi assim que o bloco em
`0x00403d59` apareceu, num trecho que as passagens anteriores tinham lido como
"a cópia dos bytes e o retorno".

**Uma das cinco hipóteses que a correção listava como descartadas era
enganosa.** Ela dizia "todas as larguras do lote kanji são múltiplas de 4, então
`div 2` nunca é ímpar — o que mostra que o modelo do contador está errado". A
observação estava certa e a conclusão não: o contador está correto, e quem
torna o valor ímpar é o `dec` aplicado **depois** de guardá-lo.

**O port agora bate com o oráculo nos três times**, medido na mesma sessão e
pelo mesmo método:

| time | oráculo | port (antes: literal 5) | port (agora) |
|--:|--:|--:|--:|
| 2 | 5 | 5 | 5 |
| 0 | 7 | ~~5~~ | 7 |
| 56 | 13 | ~~5~~ | 13 |

O literal 5 acertava só os **59** times de `LEN` 6, de 95. E o
`compara_tela.sh --nomes`, que roda no time 2, continua **PASSOU** — ele nunca
teria pego isto, porque o time que ele dirige é um dos 59.

**Problemas encontrados:**

A correção revelou uma divergência que não existia como afirmação: sobre a
**European Deluxe**, a travessia do original e a tabela do `we2002_core`
concordam em **46/95** times no lote kanji. Nomes latinos foram escritos em slot
de kanji e deixaram lixo depois do terminador, então a medição em tempo de
execução encurta. O port não reabre a imagem — decisão medida e registrada no
cabeçalho do `lista_equiposChange.inc` —, então nessa imagem os dois divergem em
49 times. Registrado na
[WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md) com a razão e o
número; o lote `OFS_TEAM_NAME_3` bate **95/95 nas duas** imagens, o que mostra
que o problema é do slot de kanji e não do método.

**Arquivos criados/modificados:**

- `wte/tools/dump_truncamento.py` — `CONTRADIZ_A_TELA` **sai** e entra
  `LOTE_COM_DECREMENTO`, com guarda de que o `dec` só vale no caminho do
  `div 2`; a prosa gerada ganhou o bloco do `dec` e a tabela das três medições
- `wte/tools/test_dump_truncamento.py` — os dois testes da exceção viraram
  testes do decremento (21 no total)
- `wte/re/truncamento.md`, `wte/re/truncamento.tsv` — regerados; o
  `edit_nombre1` deixa de ser "medido na tela" e passa a ser derivado
- `wte/src/impl/ep2002_mainform.aux.inc` — `LimiteDoNome1` devolve
  `TEAM_NAME_KANJI_LEN[t] − 1`; o literal saiu
- `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — o comentário que
  dizia "o do `edit_nombre1` continua literal"
- `wte/re/spec/MainForm.lista_equiposChange.md` — seção nova com os três
  `SetMaxLength`, que são deste handler e não do `FormShow`
- `wte/re/spec/MainForm.iguala_nombresClick.md` — o bloco que dizia "a conta dá
  um a mais"
- `docs/tasks/concluidos/35-divergencias-deliberadas.md` — a divergência da European Deluxe
- `docs/tasks/concluidos/26-handlers-de-edicao.md` — a pendência encaminhada, fechada
- `docs/PLAN-WTE-LAZARUS.md` §4.4 — a fração remedida (74,1% → 74,0%)
- `wte/re/fase-2.md` — regerado
