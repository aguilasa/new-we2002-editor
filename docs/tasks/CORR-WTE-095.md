---
id: CORR-WTE-095
title: "Investigar: o editor do Obocaman nunca preça o slot 22, e o `ed.exe` diz que ele tem preço"
type: correção
category: engenharia-reversa
status: concluído
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

- [x] a causa escrita, com o endereço que a produz — `0x0040342a`, a 23ª
      chamada do `fputc`: ela **tem sucesso**, devolve o caractere `20`, e o
      byte não vira `write`
- [x] `golden-22-precos` verde depois, com o controle fechando antes —
      `controle: PASSOU: byte-identico`, depois `golden: PASSOU: byte-identico`
- [x] `check_preco.py --check` verde — 132 jogadores em 6 times, 100%
- [x] a conclusão é "defeito do original", e a linha entrou na
      [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md)

## Log de Execução

**CONCLUÍDA.** A causa está medida, e não é a que esta correção supunha nem a
que quatro documentos afirmavam.

**Executado em:** 2026-08-24

### O caminho, e por que ele deu voltas

A correção previa quatro perguntas, e ranqueou a leitura da `0x00404374` como a
mais barata. Ela foi respondida primeiro e **excluiu** o desfecho grande — a
rotina não tem ramo por slot —, mas deixou uma contradição: o laço parecia
observar zero num campo que a rotina anterior sempre preenche. Duas medições
desfizeram a contradição, e nenhuma delas estava na lista da correção.

### 1. `strace`, e o `je` cai

O instrumento não era depurador, e já existia: o
[`diff_dirigido.sh`](../../wte/tools/diff_dirigido.sh) da WTE-TASK-19 roda o
oráculo sob `strace`, e o cabeçalho dele diz exatamente por quê — *"`cmp` não vê
LEITURA nenhuma, e leitura é metade da resposta"*.

```bash
bash wte/tools/diff_dirigido.sh wte/tests/roteiros/golden-22-precos.txt \
     --imagem roms/japanese-shift-jis.bin --saida <dir>
```

Seeks `SEEK_SET` por offset, nos 23 bytes condicionais do time 2: **três para
cada slot, 3067472 inclusive**. E a `0x004046e8` só lê o byte condicional na
rota de coluna não nula — o `cmp` de `0x00404748` desvia para `0x0040477e` no
caso zero, e ali não há I/O. Leitura em 3067472 prova coluna **não nula**.

**Logo o `je` de `0x004110ad` não é o que pula o slot 22**, e era o que a
Evidência desta correção, o `preco.md`, a spec e o `.inc` afirmavam.

### 2. O depurador, e a causa

`winedbg` anexado ao PID Wine — o `winedbg <num>` quer o PID do **Wine**, em
hexa (`info process` numa sessão sem alvo dá a lista), não o do Unix. O app foi
dirigido até o time selecionado, o depurador ligado, e só então o clique.

| Endereço | O que é | Paradas |
|---|---|---|
| `0x00411170` | o `call 0x403400` do laço | **23** |
| `0x0040342a` | o `fputc` dentro da `0x403400` | **23** |

E o retorno de cada `fputc`, lido em `0x0040342f`, bate um a um com a coluna
`previsto` do [`preco.tsv`](../../wte/re/preco.tsv) para o time 2 — inclusive o
da 23ª volta, que devolve **20**, o preço do slot 22. Nenhum devolve `EOF`.

O arquivo recebe **22** `write` de 1 byte, o último com `"\25"` (21, o slot 21).

**O preço do 23º jogador é calculado certo, aceito pelo runtime C e jogado
fora.** A perda é na saída bufferizada da Borland, abaixo do `fputc`.

### 3. Não é pendência descarregável

Testado: o roteiro completo faz descarga depois do clique — troca de time, com
I/O de sobra sobre o mesmo arquivo — e o byte continua não chegando. E a
`0x00403388`, chamada depois de cada byte, não tem parte nisso: é o caminhador
de setor MODE2/2352 (`ftell % 2352 == 2072` → `fseek(+304)`), não um flush.

### 4. Corroboração que já estava versionada

O [`io-medido.tsv`](../../wte/re/io-medido.tsv), sessão `27-mcr2iso`, traz
`W 3067473 3067495 23`: o import de `.mcr` escreve os **23** bytes condicionais
do time 3. O slot é endereçável, e o próprio editor o grava por outro caminho —
o que confirma que a lacuna é deste handler, não do formato.

### O desfecho

É o primeiro ramo da própria correção: **defeito do editor do Obocaman**, e o
port continua reproduzindo, com a razão escrita. A linha entrou na
[WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) com as três réguas.
O `ULTIMO_SLOT_PRECADO = 21` **não muda**.

**Problemas encontrados:**

1. **A causa documentada estava errada, e em quatro lugares vivos.** O `je` da
   terceira coluna foi escrito como explicação na WTE-TASK-32 e copiado para o
   `preco.md`, a spec, o `.inc` e esta própria correção. Ninguém tinha medido
   **leitura** — só escrita —, e a leitura é o que derruba a explicação. Os
   quatro foram reescritos.
2. **`pkill -f winedbg` mata o próprio shell**, porque o padrão casa a linha de
   comando que o contém. Custou duas corridas com saída vazia e código 144 antes
   de o motivo aparecer.
3. **O driver de roteiro não guarda janela entre invocações.** Ao partir o
   roteiro em duas partes para ligar o depurador no meio, a parte B precisa
   começar com um `>` que reancore a janela principal; sem isso o clique vai
   para coordenada sem janela resolvida e o diálogo nunca aparece.
4. **Fica fora de alcance, por decisão:** *por que* o runtime da Borland larga
   exatamente o último byte. É interno ao CRT, não ao aplicativo, e este projeto
   faz engenharia reversa do aplicativo. O comportamento observável está medido,
   reproduzido e gateado.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/re/preco.md` | modificado — a causa medida, no lugar da aberta |
| `wte/re/spec/MainForm.base_teamClick.md` | modificado — idem, resumido |
| `wte/src/impl/ep2002_mainform.base_teamClick.inc` | modificado — idem, no cabeçalho que sustenta a constante |
| `wte/tools/check_preco.py` | modificado — a regra do slot 22 agora tem explicação |
| `docs/tasks/35-divergencias-deliberadas.md` | modificado — a entrada nova, com as três réguas |
| `docs/PLAN-WTE-LAZARUS.md` | modificado — a fração da §4.4, que o `.inc` maior moveu |
| `wte/re/fase-2.md` | regerado |
