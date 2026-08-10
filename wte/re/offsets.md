# `re/offsets.md` — a tabela de offsets do `we-team-editor.exe`

Produto da [WTE-TASK-06](../../docs/tasks/06-mapa-de-offsets.md). Gerado por
[`../tools/dump_offsets.py`](../tools/dump_offsets.py), a partir de
`we-team-editor/we-team-editor.exe` e de
[`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp).
**Não editar à mão** — correção entra no script e o arquivo é regerado:

```sh
python3 wte/tools/dump_offsets.py
python3 wte/tools/dump_offsets.py --check   # o que `make -C wte check` roda
```

Os dados em forma de tabela estão em [`offsets.tsv`](offsets.tsv); este arquivo é a
leitura deles. **Todo número daqui saiu do script**, inclusive os do texto corrido —
é por isso que o `--check` compara o markdown inteiro byte a byte, e não só o
TSV.

## O que foi medido, e com que régua

O `.exe` tem 1151488 bytes, é PE32 i386, `ImageBase` `0x400000`,
`SizeOfImage` `0x126000`, 8 seções. A `.reloc` traz
7347 realocações `HIGHLOW`.

Um dword do binário é tratado como **offset plausível** quando passa em quatro
cortes, todos derivados de medida e nenhum escolhido a olho:

1. **faixa** — entre 387792 e 12552648, que são o menor e o maior
   valor declarados no `Offsets.hpp`;
2. **geometria do setor** — `24 <= v % 2352 < 2072`, isto é, o offset cai
   dentro da região de dados de usuário de um setor MODE2/2352. Os 69
   offsets conhecidos passam, e o script aborta no dia em que um deixar de
   passar;
3. **não é texto** — os quatro bytes não formam ASCII imprimível nem par UTF-16
   de imprimíveis;
4. **não é alvo de realocação base** — um dword que a `.reloc` manda o carregador
   ajustar é um endereço, não uma constante.

O corte 4 é o que faz o trabalho. Sem ele, a varredura de `.text` devolve mais
de mil e quinhentos candidatos, quase todos VAs do próprio módulo.

**O corte 1 sai do nosso próprio `Offsets.hpp`, e isso tem consequência.** A faixa
é literalmente o `[min, max]` dos 69 valores declarados lá, então a guarda
que confere "o filtro aceita 100% do que já se sabe ser offset" é **tautológica na
parte de faixa** — ela morde de verdade nos cortes 2 e 3, que não vêm dali.

A consequência é uma acoplagem entre dois projetos que não compartilham build: o
limite medido da tabela do Obocaman se move quando alguém mexe no `Offsets.hpp`
do `newWe2002`. A **WTE-TASK-19** existe justamente para acrescentar offsets lá; um
valor novo fora da faixa atual alarga a janela, e a corrida pode passar a engolir
o dword seguinte — a armadilha §8.7 entrando pela porta dos fundos. **Quem
acrescentar offset tem de reconferir o limite das duas tabelas.**

Congelar a faixa numa constante foi considerado e recusado: a faixa derivada é o
que faz o filtro acompanhar o que o projeto aprende. O que faltava não era
rigidez, era esta acoplagem escrita.

O corte 3 parou onde parou de propósito. Um terceiro caso tentador — "prefixo
imprimível seguido de NUL", que é a forma do `xyz` + NUL que fecha a tabela de
alfabeto logo abaixo da tabela 1 — foi testado e **descartado**: como todo valor da
faixa cabe em três bytes, esse caso degenera em "os três bytes baixos são
imprimíveis" e derruba cinco offsets conhecidos, `OFS_TEAM_NAME_4` = 2830160 =
`0x002B2F50` entre eles. Quem mantém aquele `xyz` fora da tabela é o recorte pelo
endereço-base referenciado por código, que é critério de posição e não de valor.

### Três critérios da tarefa que não sobreviveram à medição

O markdown da tarefa sugere procurar dword "entre 1.000.000 e 8.000.000,
alinhado, referenciado por código". Conferido contra o próprio `Offsets.hpp`:

| Critério sugerido | Quantos dos 69 conhecidos ele descartaria |
|---|---:|
| valor abaixo de 1.000.000 | 9 |
| valor acima de 8.000.000 | 4 |
| valor não múltiplo de 4 | 4 |

São 15 offsets conhecidos que o critério sugerido jogaria fora — filtro
assim não serve para achar os desconhecidos, e por isso ele foi trocado pelos quatro
cortes acima. **Isto é uma correção ao enunciado da WTE-TASK-06**, não uma
divergência de execução.

O mesmo vale para a tentação de descartar valor dentro da janela `[ImageBase,
ImageBase+SizeOfImage)`: 5 dos 69 offsets conhecidos caem nessa janela por
coincidência numérica (`OFS_FLAG_SHAPE_COPY_4` entre eles). A `.reloc` separa endereço de
constante sem heurística; a janela de VA não separa.

E "alinhado" também não vale para a **posição** do dword: 2 dos
19 offsets confirmados só aparecem em posição desalinhada, porque são imediato de
instrução (`OFS_COST_NC`, `OFS_LINK_ML`). Uma varredura alinhada acha 17 dos 19.

## 1. Onde a tabela começa e onde termina

São **2 tabelas** em `.data`: corrida de dwords 4-alinhados,
todos plausíveis ou zero, começando num endereço que o `.text` referencia e
contendo pelo menos um `OFS_*` conhecido.

### Tabela 1 — `0x004231a0` … `0x004231e8`

| Medida | Valor |
|---|---|
| primeiro byte | `0x004231a0` |
| primeiro byte **fora** | `0x004231e8` |
| tamanho | 72 bytes, 18 slots |
| slots preenchidos | 11 |
| buracos (`= 0`) | 7 — slots 2, 3, 4, 5, 15, 16, 17 |
| já em `Offsets.hpp` | 11 de 11 |
| referências a partir de `.text` | 3 ao endereço-base |
| dword logo abaixo | `0x007a7978` = 8026488 — bytes `xyz.` |
| dword logo acima | `0x04030200` = 67305984 — bytes `....`, não é offset plausível |
| próximo endereço de `.data` referenciado por `.text` | `0x004231e8` |
| os dois critérios de limite | **coincidem** |

Conteúdo, na ordem em que está na memória:

| slot | VA | valor | `Offsets.hpp` |
|---:|---|---:|---|
| 0 | `0x004231a0` | 2002316 | `OFS_TEAM_NAME_KANJI` |
| 1 | `0x004231a4` | 4598596 | `OFS_TEAM_MIXED_CASE_NAME` |
| 2 | `0x004231a8` | 0 | — *(buraco)* |
| 3 | `0x004231ac` | 0 | — *(buraco)* |
| 4 | `0x004231b0` | 0 | — *(buraco)* |
| 5 | `0x004231b4` | 0 | — *(buraco)* |
| 6 | `0x004231b8` | 2003996 | `OFS_TEAM_NAME_3` |
| 7 | `0x004231bc` | 1012640 | `OFS_TEAM_NAME_1` |
| 8 | `0x004231c0` | 2830160 | `OFS_TEAM_NAME_4` |
| 9 | `0x004231c4` | 2028267 | `OFS_ML_TEAM_NAME_7` |
| 10 | `0x004231c8` | 1881968 | `OFS_TEAM_NAME_2` |
| 11 | `0x004231cc` | 5651448 | `OFS_TEAM_NAME_6` |
| 12 | `0x004231d0` | 2004996 | `OFS_TEAM_ABBREV_1` |
| 13 | `0x004231d4` | 4234484 | `OFS_TEAM_ABBREV_3` |
| 14 | `0x004231d8` | 5651068 | `OFS_TEAM_ABBREV_2` |
| 15 | `0x004231dc` | 0 | — *(buraco)* |
| 16 | `0x004231e0` | 0 | — *(buraco)* |
| 17 | `0x004231e4` | 0 | — *(buraco)* |

### Tabela 2 — `0x00423634` … `0x00423648`

| Medida | Valor |
|---|---|
| primeiro byte | `0x00423634` |
| primeiro byte **fora** | `0x00423648` |
| tamanho | 20 bytes, 5 slots |
| slots preenchidos | 5 |
| buracos (`= 0`) | 0 |
| já em `Offsets.hpp` | 5 de 5 |
| referências a partir de `.text` | 1 ao endereço-base |
| dword logo abaixo | `0x7c1f7fe0` = 2082439136 — bytes `...|`, não é offset plausível |
| dword logo acima | `0x00000007` = 7 — bytes `....`, não é offset plausível |
| próximo endereço de `.data` referenciado por `.text` | `0x00423648` |
| os dois critérios de limite | **coincidem** |

Conteúdo, na ordem em que está na memória:

| slot | VA | valor | `Offsets.hpp` |
|---:|---|---:|---|
| 0 | `0x00423634` | 1929004 | `OFS_FLAG_SHAPE_COPY_1` |
| 1 | `0x00423638` | 2005412 | `OFS_FLAG_SHAPE_COPY_2` |
| 2 | `0x0042363c` | 2328060 | `OFS_FLAG_SHAPE_COPY_3` |
| 3 | `0x00423640` | 4904664 | `OFS_FLAG_SHAPE_COPY_4` |
| 4 | `0x00423644` | 5711640 | `OFS_FLAG_SHAPE_COPY_5` |

### O critério, escrito

O limite superior é medido por **dois testes independentes**, que se confrontam:

- **pelo conteúdo** — a corrida acaba no primeiro dword que não é plausível nem
  zero. Zero **não** encerra: é buraco. Tratar zero como terminador cortaria a
  tabela 1 no slot 2 e perderia 9 offsets;
- **por quem aponta para lá** — a tabela vai até o próximo endereço de `.data`
  que o `.text` referencia. Nada dentro do intervalo é referenciado; só a base é.

**A discordância entre os dois não é tratada igual nos dois sentidos**, e o motivo
é que ela não significa a mesma coisa:

- **referência antes do fim medido pelo conteúdo — aborta.** É a armadilha §8.7
  em pessoa: o conteúdo estica a tabela além do que o código sustenta, e publicar
  isso seria dar como offset um slot que ninguém referencia;
- **referência depois do fim — avisa e segue.** O intervalo publicado continua
  sendo o que o conteúdo sustenta, então não há número errado a emitir; o que há é
  um vizinho que talvez pertença à tabela. Sai como `AVISO:` na saída padrão e
  na tabela de limites acima.

O limite **inferior** é o endereço-base referenciado pelo código, e esse critério
não é decorativo: no caso da tabela 1, o dword logo abaixo é numericamente
plausível — é o `xyz` + NUL que fecha a tabela de alfabeto ASCII vizinha — e só o
recorte pela referência o mantém fora. Uma corrida sem referência nenhuma não é
tratada como tabela.

### Uma correção à §8.7 do plano

A §8.7 diz que o bloco em `0x004231a0` "é **seguido** de dados que não são
offsets", e dá como exemplo o valor 1869507948, que é ASCII. Medido: esse dword
está em `0x00423190` — **16 bytes abaixo** da tabela, não acima. Ele é `lmno`, um
pedaço da tabela de alfabeto que termina onde a de offsets começa.

A conclusão da §8.7 continua valendo — o bloco **é** cercado de dado que não é
offset dos dois lados, e o dword logo acima da tabela é 67305984
(`0x04030200`), que não passa no filtro. O que muda é o lado: quem obriga a
medir o limite **inferior** é o ASCII, e é por isso que o critério de início deste
script é posicional (endereço referenciado por código) e não numérico.

### Corroboração por desmontagem

Transcrito de `objdump`, não do script — e é a terceira medida independente do
mesmo limite. Com a `.text` recortada para um arquivo:

```sh
objdump -D -b binary -m i386 -M intel --adjust-vma=0x401000 \
        --start-address=0x40cbc8 --stop-address=0x40cc30 text.bin
```

O laço que percorre a tabela 1 é duplo:

```
40cbdb:  mov  DWORD PTR [ebp-0x34],0x4231a0   ; ponteiro = base
40cbe4:  mov  eax,DWORD PTR [ebp-0x34]        ; inicio da linha
40cbeb:  cmp  DWORD PTR [ebx],0x0
40cbee:  je   0x40cc18                        ; zero e PULADO
  ...    (usa o offset em [ebx])
40cc18:  inc  esi
40cc19:  add  ebx,0x4
40cc1c:  cmp  esi,0x6                         ; 6 colunas
40cc1f:  jl   0x40cbeb
40cc21:  inc  edi
40cc22:  add  DWORD PTR [ebp-0x34],0x18       ; passo de linha = 24
40cc26:  cmp  edi,0x3                         ; 3 linhas
40cc29:  jl   0x40cbe4
```

Três linhas × seis colunas × 4 bytes = 72 bytes, exatamente o tamanho que o
script mede para a tabela 1 (72 bytes, 18 slots). E o `je` sobre o teste de zero é
a prova de que os 7 buracos são buracos, não fim de array.

As duas linhas do bloco correspondem ao agrupamento que os nossos próprios nomes
já sugerem: uma linha de nomes completos de time, uma de abreviações, e uma com
kanji e caixa mista. Isso é leitura, não medida — o que está medido é o retângulo.

### A tabela não é única no arquivo

6 cópias adicionais em `.data`, com a mesma sequência de valores byte a byte:

| cópia de | endereço | bytes |
|---|---|---:|
| `0x004231a0` | `0x0042b750` | 72 |
| `0x004231a0` | `0x0042d244` | 72 |
| `0x004231a0` | `0x0042e6d4` | 72 |
| `0x00423634` | `0x0042bbe4` | 20 |
| `0x00423634` | `0x0042d6d8` | 20 |
| `0x00423634` | `0x0042eb68` | 20 |

Nenhuma das cópias é referenciada pelo `.text`; só o endereço-base da tabela
canônica é. **Consequência para a WTE-TASK-19:** candidato tem de ser contado por
*valor*, não por ocorrência, ou cada offset apareceria várias vezes.

## 2. Quais dos 69 batem, e o que os outros 50 são

**19 dos 69** aparecem literalmente no binário — o mesmo número que a §1.7
do plano registra. A varredura é do arquivo inteiro, em qualquer alinhamento.

| `Offsets.hpp` | valor | onde |
|---|---:|---|
| `OFS_TEAM_NAME_1` | 1012640 | `.data` `0x004231bc`, `.data` `0x0042b76c`, `.data` `0x0042d260`, `.data` `0x0042e6f0` |
| `OFS_TEAM_NAME_2` | 1881968 | `.data` `0x004231c8`, `.data` `0x0042b778`, `.data` `0x0042d26c`, `.data` `0x0042e6fc` |
| `OFS_TEAM_NAME_3` | 2003996 | `.data` `0x004231b8`, `.data` `0x0042b768`, `.data` `0x0042d25c`, `.data` `0x0042e6ec` |
| `OFS_TEAM_NAME_4` | 2830160 | `.data` `0x004231c0`, `.data` `0x0042b770`, `.data` `0x0042d264`, `.data` `0x0042e6f4` |
| `OFS_TEAM_NAME_6` | 5651448 | `.data` `0x004231cc`, `.data` `0x0042b77c`, `.data` `0x0042d270`, `.data` `0x0042e700` |
| `OFS_TEAM_NAME_KANJI` | 2002316 | `.data` `0x004231a0`, `.data` `0x0042b750`, `.data` `0x0042d244`, `.data` `0x0042e6d4` |
| `OFS_TEAM_MIXED_CASE_NAME` | 4598596 | `.data` `0x004231a4`, `.data` `0x0042b754`, `.data` `0x0042d248`, `.data` `0x0042e6d8` |
| `OFS_TEAM_ABBREV_1` | 2004996 | `.data` `0x004231d0`, `.data` `0x0042b780`, `.data` `0x0042d274`, `.data` `0x0042e704` |
| `OFS_TEAM_ABBREV_2` | 5651068 | `.data` `0x004231d8`, `.data` `0x0042b788`, `.data` `0x0042d27c`, `.data` `0x0042e70c` |
| `OFS_TEAM_ABBREV_3` | 4234484 | `.data` `0x004231d4`, `.data` `0x0042b784`, `.data` `0x0042d278`, `.data` `0x0042e708` |
| `OFS_ML_TEAM_NAME_7` | 2028267 | `.data` `0x004231c4`, `.data` `0x0042b774`, `.data` `0x0042d268`, `.data` `0x0042e6f8` |
| `OFS_FLAG_SHAPE_COPY_1` | 1929004 | `.data` `0x00423634`, `.data` `0x0042bbe4`, `.data` `0x0042d6d8`, `.data` `0x0042eb68` |
| `OFS_FLAG_SHAPE_COPY_2` | 2005412 | `.data` `0x00423638`, `.data` `0x0042bbe8`, `.data` `0x0042d6dc`, `.data` `0x0042eb6c` |
| `OFS_FLAG_SHAPE_COPY_3` | 2328060 | `.text` `0x004054b7`, `.data` `0x0042363c`, `.data` `0x0042bbec`, `.data` `0x0042d6e0`, `.data` `0x0042eb70` |
| `OFS_FLAG_SHAPE_COPY_4` | 4904664 | `.data` `0x00423640`, `.data` `0x0042bbf0`, `.data` `0x0042d6e4`, `.data` `0x0042eb74` |
| `OFS_FLAG_SHAPE_COPY_5` | 5711640 | `.data` `0x00423644`, `.data` `0x0042bbf4`, `.data` `0x0042d6e8`, `.data` `0x0042eb78` |
| `OFS_COST_NATIONAL` | 3067404 | `.text` `0x0040448c`, `.text` `0x00404628` |
| `OFS_COST_NC` | 3069512 | `.text` `0x004046b9`, `.text` `0x00404b66` |
| `OFS_LINK_ML` | 2012680 | `.text` `0x004042fd` |

16 moram em `.data`, dentro das tabelas da seção 1; 3 só existem como
imediato de instrução em `.text` (`OFS_COST_NATIONAL`, `OFS_COST_NC`, `OFS_LINK_ML`). As duas formas precisam de
varreduras diferentes, e é por isso que este script faz as duas.

### Os 50 restantes, classificados

A classificação é **hipótese priorizada, não prova**. Quem prova é a execução, e
ela já rodou: a coluna **medido** traz o veredito da WTE-TASK-19, que pôs o
`wte.exe` sob `strace` e olhou que faixa da imagem cada ação endereça. Detalhe em
[`offsets-novos.md`](offsets-novos.md).

**14 dos 50** já saíram de hipótese: o `wte.exe` endereçou o ponto em
execução. Os demais continuam sem evidência dinâmica — e isso **não** quer dizer
que ele não os alcance: quer dizer que a sessão medida não chegou na tela que os
toca. Ela não chegou porque o `wte.exe` **cai** ao carregar um time com as ROMs
deste repositório; a medida e a consequência estão no `offsets-novos.md`.

A regra de classificação é busca em largura a partir das bases que o Obocaman
comprovadamente tem:

- **H1** — deriva de um offset **confirmado**, por deslocamento dentro do mesmo
  setor (`|Δ| < 2352`) ou por um número inteiro de setores (`|k| <= 32`);
- **H2** — deriva de um **candidato** da seção 3, isto é, de uma base que o
  Obocaman tem e que este repositório ainda não nomeou. É a classe mais
  informativa: ela liga um `OFS_*` nosso a um número dele;
- **H3** — nenhuma das duas. Região que o Moriero nomeou e que o Obocaman não
  alcança por esta aritmética.

Bases de profundidade maior que 1 são offsets ausentes já ligados: é o que faz uma
família inteira de passo de setor entrar a partir de uma única âncora.

| Classe | Quantos |
|---|---:|
| H1 — base confirmada | 15 |
| H2 — base é candidato | 26 |
| H3 — sem base derivável | 9 |
| **total** | **50** |

| `Offsets.hpp` | valor | classe | medido | base | relação | Δ | prof. |
|---|---:|---|---|---:|---|---:|---:|
| `OFS_TEAM_NAME_1_END` | 1013431 | H1 | R em `SELECIONA_TIME` | 1012640 (`OFS_TEAM_NAME_1`) | mesmo setor | 791 | 1 |
| `OFS_TEAM_NAME_1_A` | 1013736 | H1 | R em `SELECIONA_TIME` | 1012640 (`OFS_TEAM_NAME_1`) | mesmo setor | 1096 | 1 |
| `OFS_TEAM_NAME_5` | 4822908 | H3 | — | 4904664 (`OFS_FLAG_SHAPE_COPY_4`) | - | -81756 | — |
| `OFS_TEAM_NAME_5_A` | 4823976 | H3 | — | 4904664 (`OFS_FLAG_SHAPE_COPY_4`) | - | -80688 | — |
| `OFS_TEAM_NAME_6_A` | 5651880 | H1 | R em `SELECIONA_TIME` | 5651448 (`OFS_TEAM_NAME_6`) | mesmo setor | 432 | 1 |
| `OFS_TEAM_NAME_6_B` | 5652364 | H1 | R em `SELECIONA_TIME` | 5651448 (`OFS_TEAM_NAME_6`) | mesmo setor | 916 | 1 |
| `OFS_TEAM_NAME_KANJI_A` | 2003928 | H1 | R em `ARRANQUE` | 2003996 (`OFS_TEAM_NAME_3`) | mesmo setor | -68 | 1 |
| `OFS_ML_TEAM_NAME_8` | 2476048 | H2 | — | 2476680 (`OFS_ML_TEAM_NAME_8_A`) | mesmo setor | -632 | 2 |
| `OFS_ML_TEAM_NAME_8_A` | 2476680 | H2 | — | 2469624 *(candidato)* | +3 setores | 7056 | 1 |
| `OFS_TEAM_BARS` | 2328184 | H1 | R em `SELECIONA_TIME` | 2328060 (`OFS_FLAG_SHAPE_COPY_3`) | mesmo setor | 124 | 1 |
| `OFS_TEAM_BARS_A` | 2328504 | H1 | R em `SELECIONA_TIME` | 2328060 (`OFS_FLAG_SHAPE_COPY_3`) | mesmo setor | 444 | 1 |
| `OFS_KICKER` | 2329056 | H1 | — | 2328060 (`OFS_FLAG_SHAPE_COPY_3`) | mesmo setor | 996 | 1 |
| `OFS_PLAYER_NAME` | 387792 | H2 | R em `SELECIONA_TIME` | 389920 *(candidato)* | mesmo setor | -2128 | 1 |
| `OFS_PLAYER_NAME_2` | 390456 | H2 | — | 389920 *(candidato)* | mesmo setor | 536 | 1 |
| `OFS_PLAYER_NAME_3` | 392808 | H2 | — | 390456 (`OFS_PLAYER_NAME_2`) | +1 setor | 2352 | 2 |
| `OFS_PLAYER_NAME_4` | 395160 | H2 | — | 390456 (`OFS_PLAYER_NAME_2`) | +2 setores | 4704 | 2 |
| `OFS_PLAYER_NAME_5` | 397512 | H2 | — | 390456 (`OFS_PLAYER_NAME_2`) | +3 setores | 7056 | 2 |
| `OFS_PLAYER_NAME_6` | 399864 | H2 | — | 390456 (`OFS_PLAYER_NAME_2`) | +4 setores | 9408 | 2 |
| `OFS_PLAYER_NAME_7` | 402216 | H2 | — | 390456 (`OFS_PLAYER_NAME_2`) | +5 setores | 11760 | 2 |
| `OFS_PLAYER_NAME_8` | 404568 | H2 | — | 390456 (`OFS_PLAYER_NAME_2`) | +6 setores | 14112 | 2 |
| `OFS_ML_PLAYER_NAME` | 2006288 | H1 | — | 2005412 (`OFS_FLAG_SHAPE_COPY_2`) | mesmo setor | 876 | 1 |
| `OFS_ML_PLAYER_NAME_2` | 2008632 | H2 | — | 1999224 *(candidato)* | +4 setores | 9408 | 1 |
| `OFS_ML_PLAYER_NAME_3` | 2010984 | H1 | — | 2012680 (`OFS_LINK_ML`) | mesmo setor | -1696 | 1 |
| `OFS_PLAYER_ATTR` | 2179492 | H2 | — | 2180328 (`OFS_PLAYER_ATTR_1`) | mesmo setor | -836 | 3 |
| `OFS_PLAYER_ATTR_1` | 2180328 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -11 setores | -25872 | 2 |
| `OFS_PLAYER_ATTR_2` | 2182680 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -10 setores | -23520 | 2 |
| `OFS_PLAYER_ATTR_3` | 2185032 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -9 setores | -21168 | 2 |
| `OFS_PLAYER_ATTR_4` | 2187384 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -8 setores | -18816 | 2 |
| `OFS_PLAYER_ATTR_5` | 2189736 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -7 setores | -16464 | 2 |
| `OFS_PLAYER_ATTR_6` | 2192088 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -6 setores | -14112 | 2 |
| `OFS_PLAYER_ATTR_7` | 2194440 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -5 setores | -11760 | 2 |
| `OFS_PLAYER_ATTR_8` | 2196792 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -4 setores | -9408 | 2 |
| `OFS_PLAYER_ATTR_9` | 2199144 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | -3 setores | -7056 | 2 |
| `OFS_ML_PLAYER_ATTR` | 2204112 | H2 | — | 2204904 *(candidato)* | mesmo setor | -792 | 1 |
| `OFS_ML_PLAYER_ATTR_1` | 2206200 | H2 | — | 2204904 *(candidato)* | mesmo setor | 1296 | 1 |
| `OFS_ML_PLAYER_ATTR_2` | 2208552 | H2 | — | 2206200 (`OFS_ML_PLAYER_ATTR_1`) | +1 setor | 2352 | 2 |
| `OFS_FLAG_COLOURS` | 12549518 | H3 | R em `SELECIONA_TIME` | 5711640 (`OFS_FLAG_SHAPE_COPY_5`) | - | 6837878 | — |
| `OFS_FLAG_COLOURS_A` | 12550296 | H3 | — | 5711640 (`OFS_FLAG_SHAPE_COPY_5`) | - | 6838656 | — |
| `OFS_FLAG_COLOURS_B` | 12552648 | H3 | — | 5711640 (`OFS_FLAG_SHAPE_COPY_5`) | - | 6841008 | — |
| `OFS_FLAG_COLOURS_SENEGAL` | 12545758 | H2 | — | 12544268 *(candidato)* | mesmo setor | 1490 | 1 |
| `OFS_SQUAD_NUMBERS_ML` | 2014504 | H1 | R em `ARRANQUE` | 2012680 (`OFS_LINK_ML`) | mesmo setor | 1824 | 1 |
| `OFS_SQUAD_NUMBERS_NATIONAL` | 404716 | H2 | R em `SELECIONA_TIME` | 404568 (`OFS_PLAYER_NAME_8`) | mesmo setor | 148 | 3 |
| `OFS_FORMATIONS` | 2303700 | H1 | — | 2304984 (`OFS_FORMATIONS_A`) | mesmo setor | -1284 | 3 |
| `OFS_FORMATIONS_A` | 2304984 | H1 | — | 2328504 (`OFS_TEAM_BARS_A`) | -10 setores | -23520 | 2 |
| `OFS_LINK_ML1` | 2012728 | H1 | R em `ARRANQUE` | 2012680 (`OFS_LINK_ML`) | mesmo setor | 48 | 1 |
| `OFS_LINK_ML2` | 2013336 | H1 | R em `ARRANQUE` | 2012680 (`OFS_LINK_ML`) | mesmo setor | 656 | 1 |
| `OFS_KIT_PREVIEW` | 2667256 | H3 | R em `SELECIONA_TIME` | 2830160 (`OFS_TEAM_NAME_4`) | - | -162904 | — |
| `OFS_KIT_PREVIEW_A` | 2669544 | H3 | — | 2830160 (`OFS_TEAM_NAME_4`) | - | -160616 | — |
| `OFS_KIT_PREVIEW_B` | 2671896 | H3 | — | 2830160 (`OFS_TEAM_NAME_4`) | - | -158264 | — |
| `OFS_KIT_PREVIEW_C` | 2674248 | H3 | — | 2830160 (`OFS_TEAM_NAME_4`) | - | -155912 | — |

### Os alvos que valem primeiro

5 candidatos ancoram uma família H2 inteira. Confirmar um deles resolve todos os
`OFS_*` pendurados nele:

| candidato | ocorrências | resolve |
|---:|---:|---|
| 389920 | 1 | `OFS_PLAYER_NAME`, `OFS_PLAYER_NAME_2` |
| 1999224 | 30 | `OFS_ML_PLAYER_NAME_2` |
| 2204904 | 1 | `OFS_ML_PLAYER_ATTR`, `OFS_ML_PLAYER_ATTR_1` |
| 2469624 | 2 | `OFS_ML_TEAM_NAME_8_A` |
| 12544268 | 1 | `OFS_FLAG_COLOURS_SENEGAL` |

### Os H3, e por que não é o fim da linha

| `Offsets.hpp` | valor | confirmado mais próximo | Δ | candidato mais próximo | Δ |
|---|---:|---:|---:|---:|---:|
| `OFS_TEAM_NAME_5` | 4822908 | 4904664 | -81756 | 5100520 | -277612 |
| `OFS_TEAM_NAME_5_A` | 4823976 | 4904664 | -80688 | 5100520 | -276544 |
| `OFS_FLAG_COLOURS` | 12549518 | 5711640 | 6837878 | 12544268 | 5250 |
| `OFS_FLAG_COLOURS_A` | 12550296 | 5711640 | 6838656 | 12544268 | 6028 |
| `OFS_FLAG_COLOURS_B` | 12552648 | 5711640 | 6841008 | 12544268 | 8380 |
| `OFS_KIT_PREVIEW` | 2667256 | 2830160 | -162904 | 2679272 | -12016 |
| `OFS_KIT_PREVIEW_A` | 2669544 | 2830160 | -160616 | 2679272 | -9728 |
| `OFS_KIT_PREVIEW_B` | 2671896 | 2830160 | -158264 | 2679272 | -7376 |
| `OFS_KIT_PREVIEW_C` | 2674248 | 2830160 | -155912 | 2679272 | -5024 |

H3 quer dizer "não derivável pela regra deste script", não "o Obocaman não
edita isso". A regra aceita deslocamento dentro de um setor ou múltiplo inteiro
de setor; um deslocamento de dois setores e meio não passa. A coluna do candidato
mais próximo mostra que em vários casos há um número do Obocaman na vizinhança —
é por aí que a WTE-TASK-19 começa.

## 3. Offsets que o Obocaman tem e nós não

**90 valores distintos** sobraram, todos ausentes do `Offsets.hpp`. Não são
ofensivos até a WTE-TASK-19 confirmar cada um; são a lista de alvos dela.

| Rota | Critério | Valores distintos |
|---|---|---:|
| `.text` | imediato de 32 bits em codificação de carga de constante, plausível, não relocado | 90 |
| `.data` | dword de uma corrida que contém offset conhecido, plausível, não relocado | 0 |

**A rota `.data` devolveu zero, e isso é resultado.** Todo dword plausível que
mora nas tabelas ao lado de um offset confirmado **já está** no `Offsets.hpp`: as
tabelas do Obocaman estão inteiramente cobertas por este repositório. O que ele
tem a mais está no código, não em tabela — e é por isso que a rota `.text` existe.

### Os 15 candidatos com mais de uma ocorrência

Ordenados por número de ocorrências. Repetição é o melhor sinal barato que
existe aqui: artefato de decodificação raramente aparece duas vezes com o mesmo
valor.

| valor | hex | setor | byte no setor | ocorrências | formas |
|---:|---|---:|---:|---:|---|
| 1999224 | `0x001e8178` | 850 | 24 | 30 | `imm32` |
| 524037 | `0x0007ff05` | 222 | 1893 | 6 | `imm32` |
| 887140 | `0x000d8964` | 377 | 436 | 5 | `mov` |
| 3988700 | `0x003cdcdc` | 1695 | 2060 | 4 | `mov` |
| 1411428 | `0x00158964` | 600 | 228 | 3 | `mov` |
| 12465624 | `0x00be35d8` | 5300 | 24 | 3 | `imm32` |
| 1080707 | `0x00107d83` | 459 | 1139 | 2 | `imm32` |
| 2012984 | `0x001eb738` | 855 | 2024 | 2 | `imm32` |
| 2469624 | `0x0025aef8` | 1050 | 24 | 2 | `imm32` |
| 2736690 | `0x0029c232` | 1163 | 1314 | 2 | `imm32` |
| 2736694 | `0x0029c236` | 1163 | 1318 | 2 | `imm32` |
| 3000000 | `0x002dc6c0` | 1275 | 1200 | 2 | `mov` |
| 3947740 | `0x003c3cdc` | 1678 | 1084 | 2 | `mov` |
| 6880767 | `0x0068fdff` | 2925 | 1167 | 2 | `imm32` |
| 7012351 | `0x006affff` | 2981 | 1039 | 2 | `imm32` |

Os outros 75 aparecem uma vez só e estão no [`offsets.tsv`](offsets.tsv), com a mesma
classificação.

### Quanto disso é ruído

A varredura de `.text` casa padrão de byte; ela **não** é um desmontador, e casa em
posição que um decodificador linear nunca visitaria. Exemplo real, para calibrar a
confiança: o valor 2204904 aparece uma única vez, em `0x0042013f`, e o `objdump`
mostra que aquele endereço cai no meio de `mov DWORD PTR fs:0x0,ecx` — não existe
instrução ali. Candidato de ocorrência única merece desconfiança proporcional.

No outro extremo, o candidato mais frequente tem evidência forte de contexto. Em
`0x004046ac`:

```
40469e:  sar  edx,0xb                   ; indice / 2048
4046a1:  lea  ecx,[edx+edx*8]
4046a4:  lea  ecx,[edx+ecx*2]           ; ecx = 19 * edx
4046a7:  shl  ecx,0x4                   ; ecx = 304 * edx
4046aa:  add  eax,ecx
4046ac:  add  eax,0x1e8178              ; + base
```

`304 = 2352 - 2048` é exatamente o cabeçalho de setor que o formato obriga a
pular, e essa é a aritmética que o `CLAUDE.md` deste repositório descreve na seção
do formato MODE2/2352. Um valor usado como base **depois** dessa correção é offset
de imagem, não coincidência.

## Ressalvas

- **A rota `.text` sub-conta.** Ela cobre as codificações de carga de constante
  listadas no cabeçalho do script; um offset construído em duas etapas (por
  exemplo `mov` de 16 bits seguido de `shl`) não aparece.
- **A rota `.text` super-conta.** Ver a seção de ruído acima.
- **Nada aqui foi conferido contra imagem de CD.** Os cortes são estruturais
  (geometria de setor, realocação, faixa); nenhum candidato foi lido de uma
  imagem real para ver o que tem lá. É a WTE-TASK-19 que faz isso.
- **A classificação da seção 2 é ordenada por prioridade**, e a escolha de base é
  desempatada por (classe, profundidade, |Δ|, base). Um mesmo `OFS_*` pode ter
  mais de uma base compatível; a tabela mostra a de maior confiança, não todas.
- **Nenhum byte do `.exe` foi copiado para cá.** O que este arquivo traz são
  medidas — endereços, contagens e valores numéricos —, no espírito da §2 do
  plano: recuperação de especificação, não transcrição.

