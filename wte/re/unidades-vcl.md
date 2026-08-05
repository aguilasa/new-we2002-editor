# `re/unidades-vcl.md` — `Registry`, `Printers`, `Comobj` e `Winhelpviewer`

Produto da [WTE-TASK-07](../../docs/tasks/07-unidades-duvidosas.md). Gerado por
[`../tools/dump_units.py`](../tools/dump_units.py), a partir de
`we-team-editor/we-team-editor.exe`, de
[`published_methods.tsv`](published_methods.tsv), de [`strings.tsv`](strings.tsv)
e dos 18 DFM de [`dfm/`](dfm/).
**Não editar à mão** — correção entra no script e o arquivo é regerado:

```sh
python3 wte/tools/dump_units.py
python3 wte/tools/dump_units.py --check   # o que `make -C wte check` roda
```

Não há TSV: são quatro unidades e 10 símbolos, e a tabela em markdown já é a
forma final do dado. **Todo número daqui saiu do script**, inclusive os do texto
corrido — é por isso que o `--check` compara o arquivo inteiro byte a byte.

## O veredito

| Unidade | Símbolos importados | Além do ciclo de vida | Chamadas | Em handler | Veredito |
|---|---:|---:|---:|---:|---|
| `Registry` | 2 | 0 | 0 | 0 | **transitiva** |
| `Printers` | 2 | 0 | 0 | 0 | **transitiva** |
| `Comobj` | 4 | 2 | 1 | 0 | **transitiva** |
| `Winhelpviewer` | 2 | 0 | 0 | 0 | **transitiva** |

**As quatro são transitivas.** Nenhuma delas tem uma única chamada partindo de
código do aplicativo, e três das quatro não têm chamada nenhuma em lugar nenhum
do binário. Consequência para o port: **nada a substituir**. Não há INI a
escrever em `~/.config/`, não há impressão a decidir escopo, não há janela de
ajuda a construir. As quatro somem, e some com elas o trabalho que a §5 do
plano reservava para o caso de serem reais.

A coluna que decide é **Em handler**. "Chamadas" conta qualquer transferência de
controle para o símbolo importado; "Em handler" conta as que caem dentro do corpo
de um dos 96 handlers publicados, isto é, dentro de código que o aplicativo
escreveu. A distinção só importa para o `Comobj`, e a seção dele explica por quê.

## O que foi medido, e com que régua

O `.exe` tem 1151488 bytes, é PE32 i386, `ImageBase` `0x400000`,
8 seções. A `.text` vai de `0x00401000` a `0x00422c00`.
São 322 imports, 267 deles de `rtl60.bpl` e `vcl60.bpl`,
distribuídos em 42 unidades Borland nomeadas.

### O import não vira `call ds:[…]`, e é aí que a medida quase deu errado

O enunciado da tarefa manda procurar `call ds:[...]` para o thunk. Não existe
nenhum: o linker do C++Builder emite **um stub `jmp *[IAT]` por import**, agrupados
no fim da `.text`, e o código chama o stub por `call rel32`. Procurar a forma
indireta no sítio de uso acharia zero nas quatro unidades — e nas outras 38
também, o que é o sinal de que o critério, não o binário, estaria errado.

São 322 stubs, **um por import, nenhum import sem stub**. O corte que os
acha é duplo: `FF 25 imm32` cujo operando a `.reloc` marca como endereço **e** cujo
valor cai num slot de IAT conhecido. Só o padrão de bytes devolve oito falsos —
três bytes `0xff` soltos dentro de outra instrução, e quatro `jmp` legítimos por
ponteiro de `.data`, que são os stubs de `printf : floating point formats not
linked` da RTL. É a mesma régua de `.reloc` que o [`offsets.md`](offsets.md) e o
[`strings.md`](strings.md) usam, no mesmo papel: separar endereço de coincidência.

### Cinco formas de referência, não uma

Para cada símbolo das quatro unidades o script procura, no arquivo inteiro e byte
a byte — todas as seções, sem exigir alinhamento:

| Forma | O que seria |
|---|---|
| `call rel32 → stub` | chamada de verdade |
| `jmp rel → stub` | chamada em posição de cauda |
| `call/jmp indireto pelo IAT` | chamada sem passar pelo stub |
| `carga do endereço do slot` | o endereço virando dado (ponteiro de função, referência de classe) |
| `entrada de tabela → stub` | o stub numa tabela de ponteiros |

Nas tabelas de sítio abaixo, **Sítio** é o endereço da instrução — exceto na quarta
forma, em que é a posição do dword. Ali a instrução que carrega o endereço não tem
forma única (`mov r32, imm32`, `mov r32, moffs32`, `push imm32`, …) e recuperar o
início dela exigiria decodificar para trás, que é palpite.

As três primeiras são o que a tarefa chama de *chamada*. A quarta e a quinta
existem porque o veredito seria falso sem elas: uma referência de classe da
Borland (`@Comobj@EOleException@`) chega ao código como **dado**, não como chamada,
e a tabela de módulos do executável guarda os `initialization` como **tabela**, não
como `call`. Procurar só `call` acharia menos do que existe.

### O corpo dos 96 handlers

O [`published_methods.tsv`](published_methods.tsv) dá o **início** dos 96 handlers.
Para responder "qual handler contém a chamada" é preciso o fim, e ele é medido com
o mesmo decodificador de comprimento x86-32 do [`dump_strings.py`](../tools/dump_strings.py) —
varredura linear que encerra no primeiro `ret` ou `jmp` situado além de todo alvo
de desvio já visto. Os 96 corpos somam 36983 bytes; o último termina em
`0x00420f16`, bem antes do fim da `.text`. Tudo o que estiver depois
disso é código que o aplicativo não escreveu, e essa é a fronteira que o veredito
do `Comobj` usa.

## O panorama que enquadra as quatro

Das 42 unidades Borland importadas, **27 importam exatamente dois símbolos**:
`@X@initialization$qqrv` e `@X@Finalization$qqrv`. Esse par não é API — é o ciclo
de vida que a tabela de módulos do executável percorre no arranque e no
encerramento. Unidade que só o importa não teve nenhuma função sua chamada.

As 27: `Activex`, `Clipbrd`, `Comconst`, `Comstrs`, `Consts`, `Contnrs`, `Extdlgs`, `Flatsb`, `Helpintfs`, `Imglist`, `Inifiles`, `Listactns`, `Mapi`, `Math`, `Menus`, `Multimon`, `Printers`, `Registry`, `Rtlconsts`, `Stdactns`, `Strutils`, `Sysconst`, `Toolwin`, `Types`, `Variants`, `Varutils`, `Winhelpviewer`.

Três das quatro sob julgamento estão nessa lista — `Registry`, `Printers`, `Winhelpviewer` —
e isso, sozinho, já é quase o veredito delas. A quarta, `Comobj`, importa dois
símbolos a mais, e é a única que exigiu ir ao disassembly.

Companhia reveladora na mesma lista: `Inifiles`. O aplicativo **não guarda
configuração em lugar nenhum** — nem no registry, nem em `.ini`. Isso fecha por
dois lados a hipótese que a §5 do plano levantava para o `Registry`.

## Unidade a unidade

### `Registry` — transitiva

| Símbolo | Slot de IAT | Stub | Referências |
|---|---|---|---:|
| `initialization$qqrv` | `0x0043e6f4` | `0x00422534` | 1 |
| `Finalization$qqrv` | `0x0043e6f8` | `0x0042253a` | 1 |

Dois símbolos, e são o par de ciclo de vida. **Nenhuma chamada em lugar nenhum**
do arquivo: as duas únicas referências são o próprio operando do stub e a entrada
na tabela de módulos.

| Sítio | Forma | Símbolo | Handler dono |
|---|---|---|---|
| `0x00401104` | entrada de tabela → stub | `initialization$qqrv` | — |
| `0x004012f6` | entrada de tabela → stub | `Finalization$qqrv` | — |

Nenhum `@Registry@TRegistry@…` é importado — nem um método, nem a referência de
classe. Sem a referência de classe não há como construir um `TRegistry`: em
Delphi e C++Builder, instanciar exige o `TMetaClass`, e ele chegaria como
import igual ao `@Comobj@EOleException@` que a seção do `Comobj` mostra.

**Substituição em LCL: nenhuma.** Não há configuração a migrar para
`~/.config/`, porque não há configuração. **Task de destino: nenhuma.**

### `Printers` — transitiva

| Símbolo | Slot de IAT | Stub | Referências |
|---|---|---|---:|
| `initialization$qqrv` | `0x0043e7f4` | `0x004225c4` | 1 |
| `Finalization$qqrv` | `0x0043e7f8` | `0x004225ca` | 1 |

Dois símbolos, e são o par de ciclo de vida. **Nenhuma chamada em lugar nenhum**
do arquivo: as duas únicas referências são o próprio operando do stub e a entrada
na tabela de módulos.

| Sítio | Forma | Símbolo | Handler dono |
|---|---|---|---|
| `0x004011b8` | entrada de tabela → stub | `initialization$qqrv` | — |
| `0x004013aa` | entrada de tabela → stub | `Finalization$qqrv` | — |

`@Printers@Printer$qqrv` — o acessor global que qualquer impressão atravessaria —
não está importado. Nos 18 formulários não há `TPrintDialog` nem `TPrinterSetupDialog`.

**Substituição em LCL: nenhuma.** Não há escopo de impressão a decidir.
**Task de destino: nenhuma.**

### `Comobj` — transitiva

| Símbolo | Slot de IAT | Stub | Referências |
|---|---|---|---:|
| `initialization$qqrv` | `0x0043e68c` | `0x004224f8` | 1 |
| `Finalization$qqrv` | `0x0043e690` | `0x004224fe` | 1 |
| `EOleException@$bctr$qqrx17System@AnsiStringlt1t1i` | `0x0043e694` | `0x00422504` | 1 |
| `EOleException@` | `0x0043e698` | `0x0042250a` | 1 |

Quatro símbolos: o par de ciclo de vida e mais dois, ambos do `EOleException` — o
construtor e a referência de classe. E, ao contrário das outras três, **há uma
chamada de verdade**.

| Sítio | Forma | Símbolo | Handler dono |
|---|---|---|---|
| `0x004010ec` | entrada de tabela → stub | `initialization$qqrv` | — |
| `0x004012de` | entrada de tabela → stub | `Finalization$qqrv` | — |
| `0x00421b57` | carga do endereço do slot | `EOleException@` | — |
| `0x00421b5b` | call rel32 → stub | `EOleException@$bctr$qqrx17System@AnsiStringlt1t1i` | — |

A chamada está em `0x00421b5b`, e a coluna do handler dono diz `—`. Não é
lacuna de medida: o último dos 96 handlers termina em `0x00420f16`, e o sítio
está 3141 bytes depois disso. A chamada está fora de todo código que o
aplicativo escreveu.

A linha de cima, a carga em `0x00421b57`, é a referência de classe
(`@Comobj@EOleException@`) chegando ao código como dado, quatro bytes antes da
chamada do construtor. É o caso que justifica a quarta forma de referência da
régua: se o script só procurasse `call`, essa linha sumiria da evidência.

#### Onde ela está, então

No caminho de falha de asserção da RTL da Borland. A rotina que contém a chamada
é alcançada por uma cadeia de três saltos a partir de uma rotina de `Variant` que
verifica `vt == rhs.vt` e, se a verificação falhar, monta a mensagem
`_ASSERTE: %s failed - %s/%d` com o nome do arquivo `VARIANT.CPP` e o número da
linha, mostra um `MessageBoxA` com o texto
`Press [Y]es to terminate, [N]o to continue and [C]ancel to Debug` e, se a
resposta for *Yes*, levanta um `EOleException` com `E_FAIL` (`0x80004005`).

Os quatro literais que provam isso — `_ASSERTE: `, `VARIANT.CPP`, `vt == rhs.vt` e
o texto do diálogo — estão no [`strings.md`](strings.md)/[`strings.tsv`](strings.tsv) da
WTE-TASK-05, e **a coluna `handler` deles também está vazia**, medida por outro
script e por outro caminho. A vizinhança confirma a origem: as strings ao redor
citam `c:\bcb\emuvcl\utilcls.h`, que é a camada em que o C++Builder emula em C++
os recursos de linguagem do Delphi.

#### Por que o veredito é *transitiva*, e não *usada*

O `EOleException` é o que a RTL levanta quando uma invariante interna dela
quebra. É código de escape, compilado junto porque veio de cabeçalho, e o
aplicativo não o alcança executando o que se propõe a fazer — só se algo dentro
da própria RTL já tiver dado errado. Chamar isso de *uso da unidade* inverteria o
sentido da pergunta que a task faz, que é se há funcionalidade a portar.

#### A armadilha 2 da tarefa, conferida

A tarefa avisa: *`Comobj` pode aparecer sem `TBrowseURL` estar envolvido; não
concluir pela hipótese*. A hipótese da §5 era o contrário — que o `Comobj` fosse
**só** o `ShellExecute` do `TBrowseURL`. Está derrubada, por três medidas:

1. o único sítio de chamada é o de asserção acima, não um `ShellExecute`;
2. o `.exe` não importa `SHELL32.DLL` — a chamada acontece dentro do `vcl60.bpl`;
3. o `TBrowseURL` não é componente de terceiro: é a ação padrão da VCL, da
   unidade `Extactns`, que o `.exe` importa à parte. As duas instâncias, em
   `MainForm` e em `ficha_about`, são disparadas por método dinâmico através do
   VMT — sem passar por `Comobj`.

**Substituição em LCL: nenhuma.** A asserção de `Variant` da Borland não tem —
nem precisa ter — equivalente: o FPC tem `{$ASSERTIONS}` e `EAssertionFailed`
próprios, e nada em `Comobj` sobrevive à troca de toolchain. **Task de destino:
nenhuma** — não há handler dono a que anexar o item.

### `Winhelpviewer` — transitiva

| Símbolo | Slot de IAT | Stub | Referências |
|---|---|---|---:|
| `initialization$qqrv` | `0x0043e924` | `0x00422688` | 1 |
| `Finalization$qqrv` | `0x0043e928` | `0x0042268e` | 1 |

Dois símbolos, e são o par de ciclo de vida. **Nenhuma chamada em lugar nenhum**
do arquivo: as duas únicas referências são o próprio operando do stub e a entrada
na tabela de módulos.

| Sítio | Forma | Símbolo | Handler dono |
|---|---|---|---|
| `0x004011ac` | entrada de tabela → stub | `initialization$qqrv` | — |
| `0x0040139e` | entrada de tabela → stub | `Finalization$qqrv` | — |

Esta é a unidade em que "zero import" precisava de reforço, e recebeu: o que o
`Winhelpviewer` faz ao inicializar é **se registrar como visualizador de ajuda**,
de modo que a ajuda seria despachada de dentro do package sem o `.exe` citar
símbolo. O reforço está na seção dos indícios — nenhum dos 18 formulários tem
`HelpFile`, `HelpContext`, `HelpType` ou `HelpKeyword`, e nenhuma das strings cita
`.hlp`. Não existe ajuda a despachar.

**Substituição em LCL: nenhuma.** Não há texto de ajuda para virar janela
própria. **Task de destino: nenhuma.**

## A inicialização de unidade, conferida à parte

A WTE-TASK-07 avisa que chamada em código de inicialização não está em handler
nenhum, e manda procurar nos dois lugares. Este script procura em todos: a
varredura de referência é do arquivo inteiro, não das regiões de código
conhecidas. Ainda assim, a inicialização merece conferência própria, porque é
exatamente onde as quatro unidades **aparecem**.

Há uma tabela de módulos em `0x00401000`..`0x00401426`: 177 registros de
6 bytes, cada um uma etiqueta de 16 bits seguida de um endereço relocado. Ela é
**identificada, não adivinhada** — os 26 `@@Tep2002_*@Initialize` e
`@@Tep2002_*@Finalize` que o próprio aplicativo exporta estão todos dentro dela, e
o script aborta se um faltar. Ao lado deles, nas mesmas colunas, estão os stubs
das unidades importadas:

| Unidade | `initialization` | `Finalization` |
|---|---|---|
| `Registry` | `0x00401104` | `0x004012f6` |
| `Printers` | `0x004011b8` | `0x004013aa` |
| `Comobj` | `0x004010ec` | `0x004012de` |
| `Winhelpviewer` | `0x004011ac` | `0x0040139e` |

É a assinatura exata de dependência transitiva: a unidade está na lista de
módulos do executável — então a seção `initialization` dela roda no arranque —,
mas nenhum código do `.exe` chama coisa alguma dela. O linker a arrastou porque
alguma unidade que o aplicativo usa a declara em `uses`.

Fora dessa tabela, os `initialization`/`Finalization` das quatro não aparecem em
mais lugar nenhum do arquivo.

## O que "sem import" não provaria sozinho

Ausência de import prova que o `.exe` não chama a unidade **por nome**. Não prova
que a funcionalidade não acontece: uma unidade cuja `initialization` se registra
num despachante entrega o serviço de dentro do package, sem o `.exe` citar
símbolo. O `Winhelpviewer` é literalmente isso — o que ele faz ao inicializar é
se registrar como visualizador de ajuda.

Por isso o veredito não parou no import. Para cada unidade o script conta os
indícios que a funcionalidade deixaria em lugares já medidos por outras tasks —
propriedade nos 18 DFM da WTE-TASK-03, texto no inventário da WTE-TASK-05:

| Unidade | Agulhas no DFM | Achadas | Expressão nas strings | Achadas |
|---|---|---:|---|---:|
| `Registry` | — | 0 | `HKEY\|SOFTWARE\\\|\.ini\b\|RegOpen\|Registry\|registro` | 0 |
| `Printers` | `TPrintDialog`, `TPrinterSetupDialog` | 0 | `Printer\|imprim\|impress\|PrintDialog` | 0 |
| `Comobj` | `TOleContainer` | 0 | `CoCreateInstance\|ProgID\|CLSID\|OleObject` | 0 |
| `Winhelpviewer` | `HelpFile`, `HelpContext`, `HelpType`, `HelpKeyword` | 0 | `\.hlp\b\|WinHelp\|ajuda` | 0 |

**Zero em todas as células.** Nenhum formulário tem `HelpFile`, `HelpContext` ou
diálogo de impressão; nenhuma string cita `.hlp`, chave de registry, `.ini` ou
CLSID. Indício positivo com zero import seria contradição, e o script aborta
nesse caso em vez de emitir veredito.

Corroboração independente vinda da tabela de import de SO: o executável importa
de três DLLs apenas — `KERNEL32.DLL` (51), `OLEAUT32.DLL` (1), `USER32.DLL` (3).
**`ADVAPI32.DLL` não aparece**, e nem `SHELL32.DLL`. De `USER32` o aplicativo usa
três funções, e nenhuma é de impressão ou de ajuda.

## Consequência para o port, e para a §5 do plano

A §5 do plano guardava uma hipótese para cada uma. Todas as quatro caem:

| Hipótese da §5 | O que a medida diz |
|---|---|
| `Registry` → config no registry vira INI em `~/.config/` | não há config nenhuma; `Inifiles` também é só ciclo de vida |
| `Printers` → "se houver impressão de verdade, decidir escopo" | não há; zero símbolo além do par, zero diálogo de impressão |
| `Comobj` → "quase certamente só o `ShellExecute` do `TBrowseURL`" | **não é isso.** O `TBrowseURL` não passa por aqui — ver a seção do `Comobj` |
| `Winhelpviewer` → o texto de ajuda vira janela própria | não há texto de ajuda; não há `.hlp`; nenhum formulário tem `HelpFile` |

Nenhuma das quatro gera item para fase alguma. Não há task de destino a apontar,
porque não há handler dono: as únicas referências vivas estão na tabela de
módulos e no caminho de asserção da RTL, e as duas somem sozinhas ao trocar o
C++Builder pelo FPC.
