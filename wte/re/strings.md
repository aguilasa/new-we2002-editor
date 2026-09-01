# `re/strings.md` — as strings de `.data`, e quem as usa

Produto da [WTE-TASK-05](../../docs/tasks/concluidos/05-inventario-de-strings.md). Gerado por
[`../tools/dump_strings.py`](../tools/dump_strings.py), a partir de
`we-team-editor/we-team-editor.exe` e de
[`published_methods.tsv`](published_methods.tsv).
**Não editar à mão** — correção entra no script e o arquivo é regerado:

```sh
python3 wte/tools/dump_strings.py
python3 wte/tools/dump_strings.py --check   # o que `make -C wte check` roda
```

Os dados em forma de tabela estão em [`strings.tsv`](strings.tsv); este arquivo é a
leitura deles. **Todo número daqui saiu do script**, inclusive os do texto corrido — é
por isso que o `--check` compara o markdown inteiro byte a byte, e não só o TSV.

## O que foi medido, e com que régua

O `.exe` tem 1151488 bytes, é PE32 i386, `ImageBase` `0x400000`.
A `.data` vai de `0x00423000` a `0x00432e00` (65024 bytes de conteúdo em arquivo) e a
`.reloc` traz 7347 realocações `HIGHLOW`.

São **765 strings**. O critério tem quatro cortes, e nenhum deles é
"corrida de bytes imprimíveis" sozinho — esse devolve 1964 registros nesta
`.data`, e a maioria não é texto:

| # | Corte | Por quê |
|---|---|---|
| 1 | corrida maximal de `0x20..0x7E` terminada em NUL | é a forma do literal C |
| 2 | nenhum byte dentro de um slot de realocação | tabela de ponteiros tem três bytes imprimíveis com frequência incômoda; a `.reloc` diz quais dwords são endereço |
| 3 | comprimento &ge; 4 | abaixo disso a corrida é indistinguível de um dword: a [tabela de offsets](offsets.md) que a WTE-TASK-06 delimitou é feita de valores que cabem em três bytes, e o quarto é o NUL |
| 4 | **ou** comprimento &ge; 1 e endereço inicial referenciado pelo `.text` | código que carrega o endereço de um byte imprimível seguido de NUL está usando aquilo como `const char*`. Resgata 72 strings de uma a três letras |

O corte 2 é a mesma régua do `dump_offsets.py`, com o sinal invertido: lá a
`.reloc` servia para **rejeitar** o que era endereço, aqui ela rejeita ponteiro em
`.data` e **acha** as referências em `.text`. Ver [`offsets.md`](offsets.md).

### Dois formatos procurados, um encontrado

Delphi e C++Builder guardam `AnsiString` com cabeçalho — refcount em `-8`,
comprimento em `-4`, bytes, NUL. Um inventário que só reconhece literal C perderia
metade do arquivo sem parecer que perdeu, então o cabeçalho foi **procurado**:

| Formato | Como foi testado | Achadas |
|---|---|---:|
| literal C (`char[]` terminado em NUL) | os quatro cortes acima | 760 |
| `AnsiString` com cabeçalho | dword em `VA-4` igual ao comprimento | 0 |
| `AnsiString` com cabeçalho **e** refcount `-1` | o teste acima mais dword em `VA-8` igual a `-1` | 0 |
| UTF-16LE (`<imprimível> 00`, terminada em dois NUL) | varredura própria, com o início referenciado pelo `.text` | 5 |

**Zero `AnsiString` com cabeçalho, e isso é resultado.** O C++Builder monta o
`AnsiString` em tempo de execução a partir do literal C; o que fica em `.data` é
`char[]` cru. A consequência para a fase 2 é direta: não há comprimento gravado em
lugar nenhum, então o tamanho de cada mensagem é o que o NUL disser — e é por isso
que enchimento de espaço passou despercebido por vinte e quatro anos.

As 5 UTF-16 são todas da RTL da Borland — `(null)`, `-INF`, `+INF`, `-NAN`, `+NAN` —, e
nenhuma é texto do app: são o que `printf` imprime para ponteiro nulo e para
infinito. A varredura larga exige que o código referencie o início da corrida, e
isso não é economia: aqui a `+NAN` estreita termina em `N`, NUL e é seguida da
`-INF` larga, de modo que ler a partir daquele `N` produz uma corrida larga
`N-INF` perfeitamente bem formada e deslocada de dois bytes. A referência desfaz a
ambiguidade sem heurística.

### Uma correção à §1.5 do plano: não é cp1252 quebrado, é ASCII

A §1.5 diz que "o arquivo está em cp1252 quebrado". Medido: das 765 strings
reconhecidas, **0 bytes** são maiores que `0x7E`. Não há byte alto nenhum em
lugar nenhum.

O que aconteceu é diferente, e a diferença importa para quem for reescrever as
mensagens: o tradutor **removeu os acentos** em vez de errar a codificação —
`Numero`, `invalido`, `Preco`, `jogo`. Não há nada a consertar de encoding; há texto
a reescrever, que é o que a §1.5 já decidiu.

## Como a referência é medida

A `.text` tem 3599 slots de realocação, apontando para 2067 endereços
distintos. Destes, 1012 caem em `.data`, e **438 caem exatamente no primeiro
byte de uma string** — são as referências deste inventário, 474 no total.

Apenas 1 ponteiro cai no meio de uma string em vez de no início. Esse número
precisa ser pequeno: se fosse grande, o corte de início estaria errado.

### O padrão de instrução que o enunciado sugeriu, medido

A WTE-TASK-05 propõe procurar o imediato — `mov eax, 0x00423xxx`. Isso funciona, e
foi medido contra a `.reloc`:

| Método | Referências achadas | Perde | Inventa |
|---|---:|---:|---:|
| `mov r32, imm32` + `push imm32` | 430 | 44 | 0 |
| alvos `HIGHLOW` da `.reloc` | 474 | 0 | 0 |

O padrão de instrução **não inventa nenhuma** — as 430 que ele acha são
verdadeiras —, mas deixa 44 de fora, que entram por outras codificações de carga
de endereço. A `.reloc` acha todas sem heurística, porque **todo** endereço absoluto
que o carregador teria de ajustar está lá por construção. Não é uma correção ao
enunciado; é uma régua melhor para a mesma medida.

## A coluna `handler` exigiu medir onde cada handler termina

O [`published_methods.tsv`](published_methods.tsv) dá o endereço de **início** dos 96 handlers e nada mais.
Atribuir uma referência ao "handler anterior mais próximo" seria errado de um jeito
que não parece errado: entre dois handlers publicados há código que não é handler
nenhum, e o maior desses vazios tem 64684 bytes.

Então o script mede o **fim** de cada um: decodificador de comprimento de instrução
x86-32 mais varredura linear que encerra no primeiro `ret` ou `jmp` situado além de
todo alvo de desvio já visto — o `jmp` de dentro de um `if` não encerra a função. O
limite duro é o início do handler seguinte: handler é função, e função acaba antes da
próxima começar.

| Medida | Valor |
|---|---:|
| handlers resolvidos | 96 de 96 |
| bytes de `.text` dentro de um corpo de handler | 36983 |
| `.text` inteira | 138240 |
| cobertura | 26.8% |
| menor corpo | 1 byte |
| maior corpo | 2378 bytes |

O menor corpo é `ficha_about.FormCreate` (`0x00402de4`), com 1 byte:
um `ret` e nada mais. Handler publicado e vazio é coisa que a IDE cria com um duplo
clique e o autor nunca preencheu.

### Conferência por desmontagem

O decodificador não é um detalhe de implementação — se ele errar o comprimento de
uma instrução, todas as extensões depois dela ficam erradas em silêncio. Foi
conferido contra o `objdump`, com a `.text` recortada para um arquivo:

```sh
objdump -D -b binary -m i386 -M intel --adjust-vma=0x401000 \
        --start-address=<início> --stop-address=<fim> text.bin
```

As fronteiras de instrução dos 96 corpos coincidem com as do `objdump` nas **10.416
instruções**, sem uma divergência.

Essa conferência **está versionada** em [`../tools/test_dump_strings.py`](../tools/test_dump_strings.py) e roda por
`make -C wte test`, de que o `check` depende. Ela se pula sozinha onde faltar o
`objdump` ou o `.exe`; o resto do arquivo — o mapa de opcodes caso a caso, os
abortos e o `extent()` — roda em qualquer máquina.

Ao refazê-la à mão, a armadilha é uma: o `objdump` emite **linhas de continuação**
para instrução longa, com endereço e mnemônico vazio. Contá-las como instrução dá
48 divergências que não existem. O teste as descarta e afirma que são 48 — se
virarem outro número, o recorte mudou.

## 1. Quantas não são referenciadas por nenhum dos 96

| População | Quantas |
|---|---:|
| strings em `.data` | 765 |
| referenciadas por algum ponteiro de `.text` | 438 |
| **não referenciadas por ponteiro nenhum** | **327** |
| referenciadas, mas de código que não é um dos 96 | 316 |
| referenciadas de dentro de um dos 96 | 122 |

**643 das 765 não são alcançadas por nenhum dos 96 handlers publicados**, e as duas
razões são diferentes:

- **327** não são referenciadas por ponteiro nenhum em `.text`. A maior parte é
  tabela de nome de componente e mensagem de diagnóstico da RTL da Borland, mais as
  cópias mortas do bloco de literais (seção seguinte);
- **316** são referenciadas, mas de código fora dos corpos medidos: os 96 cobrem
  26.8% da `.text`. O resto é método não publicado, código
  de inicialização de unidade e a própria RTL estática.

Nenhum dos dois grupos é "código morto" — é código que esta tarefa não mapeia. Quem
mapeia o primeiro tipo é a fase 4, handler a handler; a RTL não interessa a
ninguém aqui.

## 2. Qual handler tem mais strings

**`MainForm.boton_nombres2isoClick`**, com 10 strings distintas. Os 12 primeiros:

| Handler | Formulário | Strings | Referências |
|---|---|---:|---:|
| `boton_nombres2isoClick` | `MainForm` | 10 | 10 |
| `FormShow` | `MainForm` | 9 | 9 |
| `flechasapaClick` | `jugador` | 9 | 9 |
| `ComboBoxDrawItem` | `estrategia` | 8 | 8 |
| `FormCreate` | `jugador` | 8 | 8 |
| `mostrar_jugadorClick` | `MainForm` | 7 | 7 |
| `boton_dialogo_weClick` | `MainForm` | 6 | 6 |
| `FormCreate` | `estrategia` | 6 | 6 |
| `BitBtn3Click` | `estrategia` | 5 | 5 |
| `lista_equiposChange` | `MainForm` | 4 | 4 |
| `relojTimer` | `estrategia` | 4 | 4 |
| `BitBtn3Click` | `jugador` | 4 | 4 |

O que `MainForm.boton_nombres2isoClick` carrega, que é a razão de a coluna existir:

| VA | String |
|---|---|
| `0x00424db1` | `Insira o nome (1)···` |
| `0x00424dc7` | `Insira o nome (2)···` |
| `0x00424ddc` | `Insira o nome (3) de 3 letras·` |
| `0x00424dfb` | `··` |
| `0x00424dfe` | `·` |
| `0x00424e00` | `·` |
| `0x00424e02` | `lista_equipos_` |
| `0x00424e11` | `edit_nombre` |
| `0x00424e1d` | `?` |
| `0x00424e1f` | `Nomes inseridos no jogo!!!·····` |

Por formulário, somando os handlers de cada um:

| Formulário | Strings distintas | Handlers com string |
|---|---:|---:|
| `MainForm` | 63 | 18 |
| `estrategia` | 26 | 7 |
| `jugador` | 26 | 6 |
| `ficha_color` | 7 | 3 |

Só 4 dos formulários têm handler com string literal. Isso **não** quer dizer que os
outros não validem nada: quer dizer que a mensagem deles, se existe, é montada em
código que não é handler publicado, ou vem do `.dfm`.

## 3. As strings com enchimento se concentram em algum formulário

**Sim: em `MainForm`.** Das 13 strings com enchimento de espaço, 12
são carregadas de dentro de um handler de `MainForm`. A única fora dele é de `jugador`.

| VA | String | Handler |
|---|---|---|
| `0x00424ac0` | `Numero do uniforme invalido ([33 ... 99] somente na Mastere····` | `jugador.BitBtn3Click` |
| `0x00424cb1` | `O arquivo dat.bin esta fora do seu diretorio······` | `MainForm.boton_dialogo_weClick` |
| `0x00424d0d` | `Voce precisa de···` | `MainForm.boton_mcr2isoClick` |
| `0x00424d20` | `·mais blocos livres!!!.·······` | `MainForm.boton_mcr2isoClick` |
| `0x00424d3f` | `MCR inserida no jogo!!!.·················` | `MainForm.boton_mcr2isoClick` |
| `0x00424d6f` | `Barras inseridas no jogo!!!·····` | `MainForm.boton_barras2isoClick` |
| `0x00424db1` | `Insira o nome (1)···` | `MainForm.boton_nombres2isoClick` |
| `0x00424dc7` | `Insira o nome (2)···` | `MainForm.boton_nombres2isoClick` |
| `0x00424e1f` | `Nomes inseridos no jogo!!!·····` | `MainForm.boton_nombres2isoClick` |
| `0x00424e3f` | `Uniforme inserido no jogo!!!.···` | `MainForm.boton_tex2isoClick` |
| `0x00424e61` | `Isto nao e um uniforme!!!.···` | `MainForm.boton_dialogo_texClick` |
| `0x00424ee7` | `O uni foi salvo!!!.·····` | `MainForm.grabar_camisetaClick` |
| `0x00424f3f` | `A MCR foi salva!!!.····` | `MainForm.grabar_memoryClick` |

A concentração não é surpresa e ainda assim é informação: `MainForm` é a tela que
escreve na imagem, e mensagem de confirmação de gravação é justamente o texto que
o tradutor mexeu.

### O que `suspeita_patch` marca, e o que não marca

| Código | Critério | Quantas |
|---|---|---:|
| `enchimento` | tem conteúdo e termina em dois ou mais espaços | 13 |
| `truncada` | parece mensagem e tem `(` ou `[` sem fechar | 1 |
| `buraco` | parece mensagem e tem três ou mais espaços entre palavras | 2 |
| `gemea_difere` | existe cópia com o mesmo trecho de 16 caracteres e texto diferente | 3 |
| **alguma delas** | | **17** |

Fora da marcação, dois grupos medidos e deliberadamente deixados de fora:

- **16 strings terminam em exatamente um espaço**. Um espaço final é o que
  separa a frase do número que vem depois (`'Voce precisa de '` + n), e marcar isso
  como enchimento encheria a coluna de falso positivo. O critério da tarefa é dois
  espaços, e é o que está implementado;
- **21 strings são só espaço**, sem conteúdo nenhum. São separadores e
  campos em branco, não texto decepado.

## O bloco de literais do app aparece mais de uma vez

371 das 765 strings têm ao menos uma cópia byte a byte em outro endereço de
`.data` — a coluna `copia_de` do TSV traz o menor VA de cada grupo. Parte disso é
banal (`xx.cpp` da RTL aparece dezenas de vezes), mas os deslocamentos mais
frequentes contam outra coisa:

| Δ entre cópias | Pares |
|---|---:|
| `0x8598` | 57 |
| `0x9b80` | 37 |
| `0x15e8` | 36 |
| `0x10` | 18 |
| `0x22` | 18 |

| Cópia | Δ | Strings | Origem | Cópia mora em | Referenciadas |
|---:|---|---:|---|---|---:|
| 1 | `0x8598` | 78 | `0x00424767`…`0x00424c6f` | `0x0042ccff`…`0x0042d207` | 0 |
| 2 | `0x9b80` | 47 | `0x00424767`…`0x00424b13` | `0x0042e2e7`…`0x0042e693` | 0 |

O bloco de literais do app — o que vive entre `0x00424767` e `0x00424c6f` e é o
único que o código referencia — aparece **3 vezes** em `.data`. As cópias altas não
são idênticas à viva: o texto difere, e é disso que sai a seção seguinte.

### As cópias mortas preservam conteúdo que a viva perdeu

É o que a §8.8 do plano dava como perdido — "conseguir o binário original em
espanhol resolveria isso". Em parte, não é preciso: o próprio arquivo carrega
outra versão do mesmo texto, e a §8.8 passou a dizer isso ([CORR-WTE-009](../../docs/tasks/concluidos/CORR-WTE-009.md)).

**`0x00424ac0`** — viva, `jugador.BitBtn3Click`:

```
Numero do uniforme invalido ([33 ... 99] somente na Mastere    
```

Cópia morta em `0x0042d058`:

```
Numero da camisa          r ([33 ... 99] somente na Master    )
```

**`0x00424f84`** — viva, `MainForm.mostrar_jugadorClick`:

```
 You need at least 1 memory block free to do that
```

Cópia morta em `0x0042cd25`:

```
You need at least 1 memory block free to do that
```

Cópia morta em `0x0042e30d`:

```
You need at least 1 memory block free to do that
```

Cópia morta em `0x0042ec41`:

```
You need at least 1 memory block free to do that
```

**`0x00431eec`** — viva, sem handler:

```
((unsigned __far *)vftAddr)[-1] == 0
```

Cópia morta em `0x0042f40f`:

```
((unsigned __far *)vtablePtr)[-1] == 0
```

O caso do número de camisa é o que a §1.5 e a §8.8 citam nominalmente. A versão
viva perde o `)` e termina em `Mastere`; a cópia morta fecha o parêntese e escreve
`Master`. **A regra de validação é a mesma nas duas** — `[33 ... 99]`, e só na Master
League —, então a spec do handler pode ser escrita sem o binário espanhol.

Isso não torna a cópia morta uma fonte confiável de tradução: ela também tem
buraco de espaço no meio das palavras, e num ponto ela está em português onde a
viva está em inglês. O que ela dá é **sentido**, que é exatamente o que a §1.5 pede
das mensagens originais.

E o par de `0x00431eec` não é mensagem do app e ainda assim é o achado mais
informativo da seção: é uma asserção da RTL da Borland, e as duas cópias trazem
**nome de variável diferente** dentro dela. Tradutor nenhum renomeia variável em
asserção de biblioteca — isso quer dizer que as cópias vêm de **compilações
diferentes**, e não de duas passadas de tradução sobre o mesmo `.data`. Qual das três
veio primeiro não sai daqui.

## Onde o plano envelheceu

Tudo abaixo é contagem do script contra texto já escrito.

A coluna **Diz** cita o texto como ele estava quando esta página foi medida. A
[CORR-WTE-009](../../docs/tasks/concluidos/CORR-WTE-009.md) já levou a última linha à §8.8 e à
lista de pendências do `progresso.md`, então aquela citação é registro do que foi
corrigido, não do que se lê lá hoje. As duas primeiras seguem de pé — o `70`
contra `13` é da WTE-TASK-09, que tem a reconciliação no critério.

| Onde | Diz | Medido |
|---|---|---|
| §1.5 e §8.8 do plano, e a WTE-TASK-05 | "**70 strings** terminam em espaço de enchimento" | **13** em `.data` pelo critério desta página (conteúdo + dois espaços no fim); 16 com um espaço só |
| §1.5 do plano | "o arquivo está em **cp1252 quebrado**" | **0 bytes** acima de `0x7E` nas 765 strings — é ASCII com os acentos removidos |
| §8.8 do plano | "conseguir o binário original em espanhol resolveria isso" | 3 strings têm uma segunda versão **dentro do próprio arquivo**, entre elas a do número de camisa que a §8.8 cita |

O **13 contra 70** merece cuidado, porque a diferença não é erro de ninguém: são
populações diferentes. A §1.5 não diz onde contou, e o número que ela cita não sai
de `.data` com nenhum critério razoável. Sai quando se conta o **binário inteiro**,
que é o que uma passada de `strings` faria — e a maior parte do que aparece lá é
`.rsrc`, isto é, **caption de formulário**.

Isso é medida, não conjectura: nos 18 formulários já extraídos em [`dfm/`](dfm/), pelo
**mesmo critério** desta página, há **80 literais com dois ou mais espaços no fim** — contra
os 13 de `.data`. O `.rsrc` sozinho já passa dos 70, e é onde a §1.5 quase certamente
contou.

| Formulário | Literais com enchimento |
|---|---:|
| `MainForm` | 32 |
| `ficha_color` | 15 |
| `jugador` | 14 |
| `estrategia` | 4 |
| `ficha_info` | 4 |
| `ficha_enlaza` | 3 |
| `ficha_creditos_equipo` | 2 |
| `ficha_movertodos` | 2 |
| `ficha_about` | 1 |
| `ficha_info2` | 1 |
| `ficha_salida` | 1 |
| `ficha_warning` | 1 |

A concentração é a mesma da pergunta 3, por outro caminho: `MainForm` de novo.
**Consequência prática:** quem for reescrever as mensagens em pt-BR tem de olhar os
`.dfm` também, não só este inventário — e é a WTE-TASK-10 que os transforma em
`.lfm`.

A conclusão da §1.5 continua de pé, e é a que importa: **o patch é in-place com
enchimento de espaço, e pelo menos uma mensagem perdeu conteúdo.** O que muda é
onde procurar as outras — em `.rsrc`, com os `.dfm`, não aqui.

## Ressalvas

- **`suspeita_patch` é heurística, e as quatro regras estão no script.** Nenhuma
  delas é prova de que o tradutor mexeu naquela string; são os sinais que sobram de
  um patch in-place. Um texto escrito com espaço no fim de propósito seria marcado
  igual.
- **Não referenciada não quer dizer morta.** Ponteiro montado em tempo de execução
  (base mais índice) não aparece na `.reloc` como referência à string, e sim à base
  da tabela. As tabelas de nome de componente são o caso óbvio.
- **A coluna `handler` só cobre os corpos dos 96 publicados.** Referência vinda
  de método não publicado fica com a coluna vazia mesmo tendo dono claro; separar
  isso é trabalho de fase 4.
- **O escopo é `.data`.** Caption de formulário mora em `.rsrc` e saiu na
  WTE-TASK-03; nome de DLL e de função importada mora em `.idata`; o `.text` tem
  nome de tipo de RTTI (`Tficha_enlaza *`) entre as funções. Nada disso é mensagem
  do app, e nada disso está aqui.
- **Nenhum byte do `.exe` foi copiado para cá além do necessário para responder as
  perguntas.** As mensagens citadas aparecem porque a evidência **é** o texto; o
  resto são medidas, no espírito da §2 do plano.

