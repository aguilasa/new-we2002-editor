# As recusas do transpilador, e a rota escolhida para cada uma — WTE-TASK-18

**Escrito à mão.** O irmão gerado é
[`transpilador.md`](transpilador.md), que traz a tabela de substituição, a
lista do `FORBIDDEN` e o estado corrente das recusas. Aqui fica a **decisão**:
que rota cada recusa tomou e por quê.

As três rotas, como a task as define:

1. **Estender a tabela** — a construção tem tradução mecânica, faltava a regra.
2. **Ajustar a entrada** — o C++ do `we2002_core` pode ser reescrito num estilo
   que o transpilador digere, sem mudar comportamento.
3. **Porte manual daquele trecho** — último recurso, e o trecho fica marcado.

**A rota 2 não foi usada em nenhuma recusa.** Ela mexe em `src/core/`, que é o
`newWe2002` — escopo fechado e verificado —, e exigiria rodar `ctest` e o
golden dele depois. Nenhuma das 498 recusas precisou disso: todas cabiam na
rota 1 (o passe estrutural) ou na rota 3 (o que o
[`tipos.md`](tipos.md) já tinha decidido que **não é** transpilação). Por
tabela, `src/core/` não foi tocado nesta task.

---

## O ponto de partida: 498 recusas em 13 motivos

Números da execução que fechou a [WTE-TASK-17](../../docs/tasks/concluidos/17-transpilador-da-camada-de-dados.md),
lidos do `transpilador.md` daquele commit — não contados à mão. Hoje o
`port_database_pas.py --report` diz **0 recusa(s) em 0 motivo(s)**.

| Ocorrências | Motivo, como o `FORBIDDEN` o escrevia | Rota |
|---|---|---|
| 288 | bloco `{ }` | 1 |
| 160 | cabeçalho de `for` no estilo C | 1 |
| 33 | `std::` sobrou (todas em `CdImage.cpp`) | 3 |
| 4 | assinatura de função | 1 |
| 2 | declaração de `struct` | 1 e 3 |
| 2 + 2 | `[[fallthrough]]` (entrada e saída) | 1 |
| 2 | `static_assert` | 1 |
| 1 + 1 | contêiner da STL (entrada e saída), `Player.hpp:41` | fora |
| 1 | `delete`, `CdImage.hpp:33` | 3 |
| 1 | `sizeof`, `Types.hpp:78` | 1 |
| 1 | `std::function`, `Database.hpp:15` | 3 |

**454 das 498 são o passe estrutural** — bloco, `for` e assinatura. Elas não
eram 454 problemas: eram um só, e a WTE-TASK-17 o pôs no `FORBIDDEN` em vez de
deixar a estrutura passar. Emitir `.pas` com corpo em C++ produziria um
artefato que parece camada de dados, não compila, e convida a "só ajustar à
mão" o que a §4.4 do plano proíbe.

---

## Rota 1 — o passe estrutural

Bloco, laço, `switch`, assinatura, declaração de campo e hoisting de local.
Nenhuma regex alcança isso: C++ e Pascal não têm forma comum para chave,
cabeçalho de laço nem declaração de variável. O passe está em
`wte/tools/port_database_pas.py`, seções 11 e 12, e cada decisão dele que **não
é óbvia** está abaixo.

### `for` → `for..to..do` ou `while`, e a escolha não é de estilo

Em Pascal, duas coisas que em C são legítimas não são:

- **o valor da variável de controle depois do laço é indefinido** pela
  linguagem;
- **atribuir a ela dentro do corpo é proibido**.

As duas acontecem na entrada:

| Onde | O que faz | Consequência |
|---|---|---|
| `TextCodec.cpp:42` e `:74` | lê `i` **depois** do laço, para escrever o terminador | `for..to..do` gravaria o NUL no lugar errado |
| `Database.cpp:762` e `:1417` | `i = 1750;` dentro do corpo, para pular 46 slots de custo | `for..to..do` ignoraria o salto e leria 46 custos que o original pula |

Então o passe decide caso a caso: `for..to..do` quando o passo é 1, o corpo não
atribui à variável e ninguém a lê depois; `while` com o incremento no fim do
corpo em qualquer outro caso. Dos laços do `Load`/`Save`, a maioria vira
`for..to..do`; os quatro acima e os de passo 2 do `TextCodec` viram `while`.

**Um efeito colateral disso entrou no `FORBIDDEN`:** `continue`. No `while` o
incremento está no fim do corpo, e um `continue` o pularia — laço infinito
silencioso. Não há nenhum na entrada; a recusa é para o dia em que houver.

A distinção "lida depois" é por **statement**, e não por posição de caractere.
A condição `i < 63` do `for` seguinte lê `i`, mas o `init` daquele mesmo `for`
já a reinicializou — uma varredura de caractere tomava isso por uso e jogava
metade dos laços do `Load` para a forma `while` sem necessidade.

### `[[fallthrough]]` → o ramo seguinte, duplicado e marcado

São dois, `Database.cpp:450` (no `Load`) e `:1256` (no `Save`), e os dois
decidem **quantos bytes se lê da imagem**:

```cpp
case 1: case 40: case 52:
    image_file.SeekCurrent(32);
[[fallthrough]];
default:
    image_file.Read(&teams[i].flag_colours, 32);
```

O `case` do Pascal **não cai** para o ramo seguinte. Traduzir literalmente
deixaria as três seleções retiradas (Irlanda do Norte, Jamaica, Emirados) sem a
leitura de 32 bytes — e o fluxo inteiro depois delas desalinhado, porque os
offsets seguintes são relativos.

O passe **duplica o corpo do ramo seguinte** dentro do ramo que cai, com um
comentário `// PORTE A MAO (rota 1)` em cima. É a alternativa que o
`transpilador.md` já indicava ("duplique o ramo ou reescreva como if/else"), e é
a que preserva a ordem de execução sem inventar estrutura.

**A duplicação é contada.** O `test_a_contagem_de_io_bate_com_a_entrada` confere
que a saída tem exatamente `Read`/`Write`/`CStrCopy` da entrada **mais** os que
a duplicação introduziu — nem um a mais. Um `Read` a menos é um campo que nunca
se carrega; um a mais desalinha todo o resto.

### `static_assert` e `sizeof` → viraram teste

`Types.hpp:78` e `:81` afirmam `sizeof(SquadNumbers) == 16` e
`alignof(SquadNumbers) == 4`. Não há equivalente em Pascal, e o `SizeOf` do FPC
**pode divergir** do C++ por alinhamento e empacotamento — que é exatamente o
que essas asserções existem para fixar.

Viraram casos de `wte/tests/test_camada_dados.pas`
(`squad_numbers/tamanho`), que roda contra a camada gerada. Afirmação que o
compilador checava passou a ser afirmação que o teste checa; o que não podia
acontecer era ela sumir.

### `struct` → `record`

Duas declarações. `Types.hpp:33` (`SquadNumbers`) e `CdImage.hpp:65`
(`SectorPosition`) — as duas acabaram na rota 3, por motivos que não são o
`struct` em si (bitfield e `std::fstream`). Os `record` que o passe **de fato**
gera vêm de `class`: `Team`, `MlTeam`, `Formation`, `Player`, `Database`.

`packed` só onde a imagem manda, como a decisão 2 do `tipos.md` fixou: os
registros do core não são lidos em bloco — `Load`/`Save` percorrem campo a
campo —, então empacotá-los só perderia alinhamento. A exceção é
`SquadNumbers`, lido e gravado como blob de 16 bytes.

---

## Rota 3 — o que o `tipos.md` já decidira que não é transpilação

Três peças, todas com desenho escrito desde a
[WTE-TASK-15](../../docs/tasks/concluidos/15-mapeamento-de-tipo.md). O Pascal delas mora
**dentro do gerador** (`MANUAIS`, `TRECHOS_MANUAIS`), nunca no arquivo de
saída: a unidade continua sendo gerada por inteiro, e o trecho vai marcado
`PORTE A MAO (rota 3)`.

| Peça | Recusa que a trouxe | Decisão |
|---|---|---|
| `CdImage` inteiro | 33 × `std::` sobrou, 1 × `delete` | `tipos.md` decisão 3 |
| `SquadNumbers` + acessores | `struct` com bitfield | `tipos.md` decisão 2 |
| `Reporter` / `Report` | `std::function` | `tipos.md`, tabela |
| `UrlSidecarPath` + sidecar | — (`std::ofstream`, `operator<<`) | `tipos.md` decisão 5 |

### `CdImage` — `std::fstream` não tem tradução textual

As 33 recusas de `std::` estão todas em `CdImage.cpp`, e são `std::ios::in`,
`std::streamoff`, `stream_.seekg`, `gcount()`. Nenhuma tem equivalente por
regra; e a decisão 3 do `tipos.md` já prescreve um desenho **diferente** do C++,
não uma tradução dele:

- `Read` e **nunca** `ReadBuffer` — o `TFileStream` levanta `EReadError` no fim
  do arquivo, e o `CFile` do MFC devolvia curto. Leitura curta não é erro, e há
  chamadas que dependem disso.
- `fmOpenReadWrite` e **nunca** `fmCreate` — `fmCreate` truncaria uma imagem de
  474 MB.
- `Seek` com sobrecarga de `Int64`, `soBeginning`/`soCurrent`.
- EDC/ECC **não** recalculado.

O `= delete` do construtor de cópia (`CdImage.hpp:33`) desaparece junto: em C++
ele **apaga** uma operação e não há comportamento para traduzir.

`SectorPosition` e `Locate` saem no mesmo pacote — o `Locate` do C++ devolve o
registro por inicialização com chaves, que também não é transpilável.

### `SquadNumbers` — máscara e deslocamento, não `bitpacked`

O FPC tem `bitpacked record`, **mas a ordem de bit é definida pelo compilador e
pelo endianness** e não é obrigada a casar com o que o MSVC fez em 2002. O
layout reproduzido é o que o `TestSquadNumbersLayout` do `newWe2002` fixou, e
está provado em execução por cinco casos de `test_camada_dados.pas`.

### `Reporter` — `std::function` vazio vira `Assigned()`

`std::function<void(const std::string&)>` vira
`procedure(const msg: string) of object`, que pode ser `nil` como o
`std::function` vazio. O `if (report)` do C++ vira `if Assigned(report)`.

**A rotina portada à mão se chama `Reportar`, e não `Report`.** O Pascal não
distingue caixa: o parâmetro `report` esconderia a rotina `Report`, e a chamada
deixaria de compilar com um erro que não menciona caixa nenhuma. Há uma regra de
`SUBS` que renomeia a chamada.

### O sidecar `_url.txt` — byte a byte

O bloco de `std::ofstream` do `Save` (`Database.cpp:1453-1459`) é substituído
por uma chamada a `TDatabase.WriteUrlSidecar`, portada à mão conforme a decisão
5 do `tipos.md`: `TFileStream` com `#10` escrito explicitamente, e **não**
`TStringList` — o `SaveToFile` dele usa o `LineEnding` da plataforma e tem
`WriteBOM`, e este é arquivo **do usuário**.

O trecho é casado **exatamente** na entrada. Se ele deixar de existir lá, o
gerador recusa: porte à mão que apodrece calado é pior que porte à mão nenhum.

Provado em execução por `sidecar/uma_linha_por_jogador` (1.911 ocorrências de
`#10`), `sidecar/sem_cr`, `sidecar/sem_bom` e `sidecar/termina_em_lf` — em
**byte**, não em linha. Contar linha não serve: `TStringList` com `LineEnding`
de Windows daria 1.911 linhas com CRLF e passaria.

---

## Fora da camada de dados

| Item | Onde | Razão |
|---|---|---|
| `FifaPlayer` | `Player.hpp:12-42` | a classe do import do SoFIFA. Usa `std::vector` e `std::string`, e o `tipos.md` manda **recusar** contêiner da STL em vez de improvisar equivalente Pascal |
| `SofifaRules` | `Player.hpp:9` | declaração adiantada da mesma coisa |
| `Sofifa.cpp`, `Sofifa.hpp` | — | 805 linhas sem consumidor: o import está desligado no `newWe2002` desde 2026-08-05 e o editor do Obocaman não tem nada equivalente |

**Nada disso sai em silêncio.** Todo item de topo de cada entrada — função,
classe, constante, `using` — tem de ser transpilado **ou** reivindicado com
razão escrita; item que ninguém reivindica recusa, e reivindicação de item que
sumiu da entrada também. É a regressão da
[CORR-WTE-034](../../docs/tasks/concluidos/CORR-WTE-034.md) no nível de item: lá o `UNITS`
esqueceu `Team.hpp` e nada no `--check` acusou.

---

## Achados da WTE-TASK-18 que **não** eram recusa

Sete defeitos da tabela da WTE-TASK-17 que nenhum guard pegava, porque nenhum
deixava token para trás. Os quatro primeiros produziriam Pascal que compila e
faz outra coisa — a categoria que este projeto inteiro existe para evitar.

A **última linha da tabela é de depois**: não veio da WTE-TASK-18, veio da
revisão dela, e é da mesma classe — Pascal que compila, roda e entrega outro
número. Fica aqui porque é aqui que os defeitos desta classe são registrados.

| Defeito | O que saía | Correção |
|---|---|---|
| SUBS aplicadas **dentro de literal** | `"Error ! Impossible to open CD image !"` virava `'Error not Impossible to open CD image !'` — a regra `!` → `not` comendo dentro do texto que o usuário lê | `_proteger()` guarda comentário e literal antes das regras |
| `&` apagado em toda posição de argumento | `ResolveMlLink(&link_euro_allstar[i*2])` passava um **Byte** onde a rotina espera ponteiro | `traduzir_enderecos()` decide por rotina chamada; rotina não classificada **recusa** |
| `(unsigned char*)` apagado | `KanjiToAscii(array, …)` onde o parâmetro é `PByte` | o cast vira `@` |
| `&&`/`\|\|` sem parênteses nos operandos | `a == 1 && b > 2` virava `a = 1 and b > 2`, que o FPC lê como `a = (1 and b) > 2` | `parentizar_booleanos()` — em C `==` liga mais forte que `&&`, em Pascal `and` liga mais forte que `=` |
| `<<` com lookbehind `(?<![\w\s])` | `hair_style<<4` (`Player.cpp:65`) atravessava intacto | regra simples, sem lookbehind |
| `static_cast<unsigned int>` depois das regras de tipo | virava `static_cast<LongWord>`, que a regra do cast não casa mais | os casts rodam **antes** das regras de tipo |
| `as` como nome de parâmetro | `as` é o operador de type-cast do Pascal; o corpo de `AsciiToKanji` não compilava | tabela `RESERVADAS`/`RENOMEIA`; identificador reservado sem mapeamento recusa |
| `AnsiChar` para campo inteiro **largo** com `Ord` ([CORR-WTE-043](../../docs/tasks/concluidos/CORR-WTE-043.md)) | `players[i].cost := Ord(buf1[0])`: o `char` do x86 tem sinal, então `0xC8` chega como **200** onde o C++ entrega **-56** | `ajustar_atribuicao()` emite `ShortInt(...)` quando o destino é largo e mantém `Ord` quando é de um byte (`UM_BYTE`) |

Faltavam também três regras que a entrada exige e a tabela não tinha: literal
hexadecimal (`0x07` → `$07`), `&`/`|` bit-a-bit e as compostas `&=`/`|=`/`^=`.
As compostas põem **parênteses no lado direito** — `x |= defence-12` significa
`x or (defence-12)`, e em Pascal `or` e `-` têm a mesma precedência: sem os
parênteses viraria `(x or defence) - 12`.

---

## O que ficou medido

| Medida | Valor | Como |
|---|---|---|
| Recusas em aberto | **0** | `port_database_pas.py --report` |
| Unidades geradas | **6** | `port_database_pas.py --check` |
| Linhas C++ de entrada | 2.504 | `transpilador.md` |
| `Read`/`Write`/`Seek`/`strcpy` | idênticos à entrada, mais a duplicação do `[[fallthrough]]` | `test_a_contagem_de_io_bate_com_a_entrada` |
| Compilação | `fpc` limpo, **zero aviso** | `test_as_seis_unidades_compilam` |
| Decisões do `tipos.md` | **26** casos, todos verdes (23 na WTE-TASK-18; 3 vieram com a [CORR-WTE-043](../../docs/tasks/concluidos/CORR-WTE-043.md)) | `wte/tests/test_camada_dados.pas` |

O que **não** está medido aqui, e é da
[WTE-TASK-20](../../docs/tasks/concluidos/20-round-trip-headless.md): que a camada Pascal
lê e grava os mesmos bytes que o `we2002_core` nas duas ROMs. Compilar e provar
as decisões de tipo é condição necessária, não suficiente — o `Load` inteiro
ainda não foi executado contra imagem nenhuma.
