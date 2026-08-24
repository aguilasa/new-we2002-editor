---
id: CORR-WTE-095
title: "Investigar: o editor do Obocaman nunca preça o slot 22, e o `ed.exe` diz que ele tem preço"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-095: os dois editores discordam sobre o 23º slot

## Problema identificado

O `MainForm.base_teamClick` do editor do Obocaman percorre os 23 slots de um
time e grava o preço de **22**. O slot 22 nunca é escrito.

Isso foi medido pela [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) e o port
o reproduz — o gate é byte a byte contra o oráculo, então reproduzir é
obrigatório. **O que não se sabe é por quê**, e é isso que esta correção
investiga.

## Evidência

O laço vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em `0x00411178`), e cada
volta começa com:

```text
call 0x4046e8                        ' carrega_jogador(time, slot, buffer 2)
cmp  DWORD PTR ds:0x43366c,0x0       ' a terceira coluna do buffer 2
je   0x411175                        ' pula o slot
```

A CORR abriu afirmando que *"para o slot 22 a coluna sai zero, e o slot é
pulado"*. **Medido em 2026-08-24: não sai** — ver o Log. O `je` acima existe e é
real; o que ele não é é a causa deste salto.

**Medido em seis times da ROM japonesa** (0, 2, 9, 17, 30, 48): os bytes
gravados vão de `CONDICIONAL_BASE + 23·t` até `+ 21`, e o do slot 22 fica com o
valor de fábrica em todos os seis.

**O conteúdo do jogador não explica.** No time 9 o slot 21 e o slot 22 têm a
**mesma** soma de habilidades (36) e a **mesma** posição (0, goleiro), e só o 21
é gravado.

**E o outro editor discorda.** A conta de offset que este port herdou —
`CONDICIONAL_BASE + 23·indice + 2·(indice div 56) + slot`, em
`wte/src/wte_ficha.pas` — dá coluna **não nula** para o slot 22. Ela veio do
`we2002_core`, que é byte-idêntico ao `ed.exe`, e o `ed.exe` lê e grava custo
para os 1.449 jogadores de seleção sem pular nenhum
(`src/core/Database.cpp:756-764`, que só salta os 46 dos times 54 e 55).

## Causa raiz

**Desconhecida.** É o que esta correção tem de estabelecer.

## Correção

Determinar de onde vem o zero, e então decidir o que fazer com ele.

### As perguntas, na ordem em que se respondem barato

1. **A ficha concorda com a gravação?** Se o `casilla_precio` nascer
   desabilitado para o slot 22 no oráculo, então a `0x00404374` inteira acha
   que aquele slot não tem campo condicional — e o efeito é bem maior que
   preço: alcança o `casilla_dorsalKeyPress`, que só encadeia o foco quando a
   coluna não é zero. Custa uma corrida de tela.
2. **É todo time, ou só time de seleção?** Clube de Master League resolve o
   slot por vínculo, e o slot 22 de um clube pode apontar para outro lugar.
3. **É o slot 22 ou é "o último"?** Um clube de ML com menos jogadores diria.
4. **Onde a `0x00404374` calcula a terceira coluna**, e se há um `cmp` contra
   22 ou um limite de tabela ali.

### O que fazer depois de saber

Se for defeito do editor do Obocaman, ele entra na
[WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) como divergência
**do original contra o formato**, e o port continua reproduzindo-o — com a
razão escrita em vez de "medido, não explicado".

Se for propriedade do formato que o `we2002_core` lê errado, a conta de offset
do port está errada para o slot 22 **em toda operação**, não só em preço, e aí
é achado grande.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/preco.md` | modificar (a seção do achado ganha a causa) |
| `wte/re/spec/MainForm.base_teamClick.md` | modificar |
| `wte/src/impl/ep2002_mainform.base_teamClick.inc` | modificar, se a causa mudar o `ULTIMO_SLOT_PRECADO` |
| `wte/tools/check_preco.py` | modificar, idem |

## Verificação

- [ ] a causa escrita, com o endereço que a produz — **não atingido**, e o que
      falta está nomeado no Log
- [x] `golden-22-precos` verde depois, com o controle fechando antes
- [x] `check_preco.py --check` verde
- [ ] se a conclusão for "defeito do original", linha na WTE-TASK-35 — sem
      conclusão ainda, então sem linha

## Log de Execução

**PARCIAL.** A correção segue **pendente**, mas o que ela afirmava como causa
**foi refutado**, e por isso quatro documentos vivos mudaram nesta invocação. As
perguntas 2 e 3 (clube de ML, "o slot 22 ou o último") deixaram de importar: a
resposta não está do lado do slot.

**Executado em:** 2026-08-24 *(medição parcial; a correção não fecha)*

### 1. O instrumento que faltava não era depurador — era `strace`

O Log anterior fechou dizendo que só a observação em execução resolveria, e
apontou para depurador sob Wine ou Ghidra. Havia um canal mais barato já
construído no projeto: o
[`diff_dirigido.sh`](../../wte/tools/diff_dirigido.sh) da WTE-TASK-19 roda o
oráculo sob `strace`, e o cabeçalho dele diz exatamente por que isso importa —
*"`cmp` não vê LEITURA nenhuma, e leitura é metade da resposta"*. É a metade que
faltava aqui.

```bash
bash wte/tools/diff_dirigido.sh wte/tests/roteiros/golden-22-precos.txt \
     --imagem roms/japanese-shift-jis.bin --saida <dir>
```

### 2. A coluna do slot 22 **não** é zero

Seeks `SEEK_SET` por offset, na faixa dos 23 bytes condicionais do time 2:

```text
3067450  3     3067458  3     3067466  3
3067451  3     ...            ...
...            3067465  3     3067471  3
                              3067472  3   <- o slot 22, os mesmos 3
```

Vinte e três slots, **três seeks cada, sem exceção**. E a `0x004046e8` só lê o
byte condicional na rota de coluna não nula: o
`cmp DWORD PTR [esi*4+0x433614],0x0` de `0x00404748` desvia para `0x0040477e`
quando ela é zero, e ali não há I/O — o que ele faz é pôr `0x32` no buffer.
Leitura em 3067472 prova coluna não nula.

**Logo o `je` de `0x004110ad` não é o que pula o slot 22**, e essa era a causa
que a CORR, o `preco.md`, a spec e o `.inc` afirmavam.

### 3. O byte se perde na escrita, e o trace diz onde

```text
slot 21                              slot 22
  _llseek 3067471 SET                  _llseek 3067472 SET
  read 512                             read 512
  _llseek 0 CUR -> 3067983             _llseek 0 CUR -> 3067984
  _llseek 3067983 SET                  _llseek 3067984 SET
  _llseek 3067471 SET                  _llseek 3067472 SET
  _llseek 0 CUR -> 3067471             _llseek 0 CUR -> 3067472
  _llseek 3067471 SET                  _llseek 3067472 SET
  write "\25" 1                       (nada)
```

Idênticas até o `fseek` da gravação **inclusive**. O offset **3067473** — a
posição do arquivo depois de uma escrita de 1 byte em 3067472 — não aparece nos
52 MB de trace, e o `0xFF` plantado em 3067472 sobrevive à corrida. A perda é
dentro da `0x00403400`, entre o `fseek` de `0x00403410` e o `fputc` de
`0x0040342a`.

**E não é buffer de saída não descarregado.** A `0x00403388`, chamada depois de
cada byte, não é um flush: é o caminhador de setor MODE2/2352 —
`ftell % 2352 == 2072` → `fseek(+304)`, pulando os 280 de EDC/ECC mais os 24 do
cabeçalho seguinte.

### 4. O slot 22 é endereçável, e o próprio editor o grava por outro caminho

Estava versionado e ninguém tinha cruzado: o
[`io-medido.tsv`](../../wte/re/io-medido.tsv), sessão `27-mcr2iso`, traz

```text
japanese-shift-jis.bin  27-mcr2iso  IMPORTA  W  3067473  3067495  23  1304  465
```

`3067473 = CONDICIONAL_BASE + 23·3` e `3067495 = + 22`: o import de `.mcr`
escreve os **23** bytes condicionais do time 3. Não é propriedade do formato,
não é do time, não é do slot — é deste handler.

### O que fica aberto

**Só o mecanismo**, e ele está localizado numa rotina de 70 bytes: por que a
`0x00403400` posiciona e não escreve na 23ª volta, com `ecx = 1` posto três
instruções antes em `0x00411160`. Isso exige `[ebp-0x4]` observado **em
execução** dentro dela — depurador sob Wine, ou a rotina decompilada no projeto
do Ghidra (§8.10 do plano). As perguntas 1, 2 e 3 da seção *Correção* não são
mais o caminho: elas supunham que a resposta estava no slot ou no tipo de time,
e a coluna do slot 22 é não nula em ambos.

### Por que ainda não fecha

A Verificação pede *"a causa escrita, com o endereço que a produz"*. Há um
endereço — `0x00403400`, entre `0x00403410` e `0x0040342a` — mas não há
mecanismo, e escrever "perde-se ali" como causa seria trocar um "não explicado"
por outro mais bem localizado. O `ULTIMO_SLOT_PRECADO = 21` **não muda**: o
comportamento observável é o mesmo, e é contra ele que o gate mede.

**Gates rodados**

- `make -C wte check`: verde, **764** testes, `OK (skipped=1)`
- `lazbuild -B`: o mesmo **único** warning pré-existente
  (`we2002_preco.pas(138,27)`, de `c566455`), em arquivo que esta correção não
  toca; 143 hints, os mesmos de antes
- `check_preco.py --check`: verde
- `analisar_io.py --check`: verde — as linhas de sessão `dd95` que a corrida
  anexou ao `io-medido.tsv` e ao `cmp-medido.tsv` foram **revertidas**: são
  medida duplicada sob rótulo de rascunho, e o valor da corrida está na prosa
  com o comando que a refaz
- `roms/` intocada; a corrida trabalhou sobre `work/dd-run.bin`

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/re/preco.md` | modificado — a causa refutada e a medição que a refuta |
| `wte/re/spec/MainForm.base_teamClick.md` | modificado — idem, resumido |
| `wte/src/impl/ep2002_mainform.base_teamClick.inc` | modificado — idem, no cabeçalho que sustenta a constante |
| `wte/tools/check_preco.py` | modificado — a justificativa do `ULTIMO_SLOT_PRECADO` não é mais "o limite do laço" |
| `docs/PLAN-WTE-LAZARUS.md` | modificado — a fração da §4.4, que o `.inc` maior moveu |
| `wte/re/fase-2.md` | regerado |
