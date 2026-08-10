# Mapeamento de tipo C++ → Pascal — WTE-TASK-15

A única decisão de projeto real da fase 3, e ela bloqueia os dois geradores
(WTE-TASK-16 e 17). Errar aqui produz código que compila, roda, passa em teste
unitário e **grava bytes errados**.

Precedente medido no `newWe2002`: `DWORD` virou 64-bit no Linux LP64 e
embaralhou todos os números de camisa. A correção foi `std::uint32_t`
explícito. O mesmo risco atravessa para Pascal com outra roupa — ver a §8.11 do
[`PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md).

**Escopo:** o que a camada de dados gerada usa. *Como* o gerador implementa é da
[WTE-TASK-17](/docs/tasks/17-transpilador-da-camada-de-dados.md).

**Entrada real medida** — os tipos que de fato aparecem em
`src/core/Database.cpp`, `Player.cpp`, `CdImage.cpp`, `TextCodec.cpp` e
`Types.hpp`, que são as ~2.150 linhas que o transpilador digere.

---

## Regra zero: nada de tipo cujo tamanho dependa da plataforma

`Integer`, `Cardinal`, `PtrInt`, `PtrUInt`, `NativeInt`, `SizeInt` e `LongInt`
**não são equivalentes** em FPC. `Integer` é 16 bits em `{$mode tp}`;
`PtrInt`/`NativeInt` seguem o ponteiro; `SizeInt` idem. Nenhum deles entra em
campo de registro nem em variável que toque a imagem.

Os tipos usados abaixo são todos de largura fixa por definição do FPC:
`Byte` (8), `ShortInt` (8, com sinal), `Word` (16), `LongWord` (32),
`LongInt` (32, com sinal), `Int64` (64), `AnsiChar` (8), `Double` (64).

---

## A tabela

| C++ (`we2002_core`) | Pascal (FPC) | Motivo |
|---|---|---|
| `std::uint8_t`, `unsigned char` | `Byte` | 8 bits sem sinal dos dois lados |
| `std::uint16_t`, `unsigned short` | `Word` | as 48 cores de bandeira/uniforme por time |
| `std::uint32_t` | `LongWord` | **nunca** `Cardinal` sem conferir, nunca tipo de plataforma |
| `std::int32_t`, `int` | `LongInt` | os 30 atributos de `Player` |
| `unsigned int` | `LongWord` | 3 usos, todos contadores locais |
| `bool` | `Boolean` | |
| `double` | `Double` | só em `ComputePlayerCost`; `std::ceil` → `Ceil` de `Math` |
| `Offset` (= `std::int64_t`) | `Int64` | ver "Seek" abaixo |
| `std::size_t` | `SizeInt` | **só** na fronteira do `CdImage`; nunca em campo de registro |
| `char[N]` **de texto** | `array[0..N-1] of AnsiChar` | **não** `string` — ver decisão 1 |
| `char` **numérico** | `ShortInt` | com sinal, como o `char` do x86 — ver decisão 4 |
| bitfield de `SquadNumbers` | acessor explícito sobre `array[0..3] of LongWord` | ver decisão 2 |
| `CdImage` | invólucro sobre `TFileStream` | ver decisão 3 |
| `std::string`, `std::filesystem::path` | `string` (= `AnsiString`) | **só** em assinatura; nunca em campo de registro |
| `std::function<void(const std::string&)>` (`Reporter`) | `TReporter = procedure(const Msg: string) of object` | pode ser `nil`, como o `std::function` vazio |
| `std::ofstream` (o sidecar `_url.txt`) | `TFileStream` com `#10` explícito | ver decisão 5 |

### Registro empacotado: só onde a imagem manda

As classes do core **não são lidas em bloco** — `Load`/`Save` percorrem campo a
campo. Logo os registros Pascal **não** precisam ser `packed`, e forçar
empacotamento só perderia alinhamento sem ganhar nada.

**Uma exceção, e é a que importa:** `SquadNumbers` é lido e gravado como blob de
16 bytes (`Database.cpp:412` e `:1069`). Esse é `packed`, e a decisão 2 governa.

---

## Decisão 1 — `char[N]` não pode virar `string`, e o `strcpy` vem junto

O original é C++Builder com `char` fixo e `strcpy`; o truncamento silencioso
pode ser load-bearing no formato. `string` gerenciada **esconderia** o
truncamento em vez de reproduzi-lo.

**Decisão: array fixo de `AnsiChar`, indexado de 0**, com o mesmo tamanho
declarado no C++ — `Player.name` é `array[0..10]`, `Player.url` é
`array[0..499]`, `Team.raw_formation` é `array[0..30]`.

Isso não basta sozinho, porque a entrada tem **40 `strcpy` e 10 `strcat`** em
`Database.cpp` — 38 `strcpy` e os 10 `strcat` no corpo do `Load()`, mais duas
`std::strcpy` em `CopyAllStarNames()` (linhas 98 e 100), que o `Load()` chama na
linha 778. **A regra de cópia tem de casar as duas grafias**, qualificada e nua:
uma substituição ancorada em `strcpy(` atravessa as duas últimas sem tocá-las. Um `Move` não os substitui: eles copiam *até o NUL inclusive*, e
o comprimento não está escrito em lugar nenhum. **Decisão: o gerador emite duas
rotinas de cópia com semântica de C — copiar byte a byte até o `#0` inclusive,
sem checar limite** — e nunca `StrPCopy`/`StrLCopy`, que truncam de outro jeito.

Não checar limite é deliberado. O `newWe2002` mediu que um desses `strcpy`
estourava um byte em **toda** imagem aberta: `Load` lê 30 bytes de formação e
copia para `raw_formation`, e o terminador caía em `slot_role[0]`. O port
resolveu **alargando o destino para 31**, e não silenciando a cópia. O Pascal
herda o 31 e a mesma cópia franca.

> **Teste que prova:** `raw_formation` com 30 bytes sem `#0` na entrada — a
> cópia tem de escrever 31 bytes e não corromper `slot_role`; e `Save` tem de
> gravar 30, nunca 31. É o irmão Pascal do `TestLoadUnterminatedFormation` do
> `newWe2002`, que roda contra uma imagem esparsa sintética.

---

## Decisão 2 — bitfield: acessor por máscara e deslocamento, não `bitpacked`

`SquadNumbers` são 23 números de camisa de 5 bits em 16 bytes, lidos e gravados
como blob.

O FPC tem `bitpacked record`, **mas a ordem de bit é definida pelo compilador e
pelo endianness** e não é obrigada a casar com o que o MSVC fez em 2002. A
§8.11 recomenda o acessor, e a decisão é essa.

**Decisão: `packed record Palavras: array[0..3] of LongWord; end`, com
`SquadNumberAt`/`SetSquadNumberAt` por máscara e deslocamento.** O layout a
reproduzir, já fixado por teste no `newWe2002`
(`tests/test_main.cpp:47`, `TestSquadNumbersLayout`):

- quatro unidades de 32 bits, little-endian;
- dentro de cada unidade os campos são alocados **do bit menos significativo
  para cima**, 5 bits cada;
- unidades 0 a 2 levam 6 números + 2 bits de enchimento; a unidade 3 leva 5
  números + 7 bits;
- logo `numero[k]` mora na unidade `k div 6`, deslocado `5 * (k mod 6)` — para
  `k` de 0 a 22.

Índice fora de 0..22 **devolve 0 e ignora escrita**, como o `SquadNumberAt` do
C++, em vez de alcançar o campo vizinho.

> **Teste que prova, e são dois.** (a) O mesmo vetor do
> `TestSquadNumbersLayout`: gravar 1..6 nos seis primeiros e conferir que a
> primeira `LongWord` vale `1 or (2 shl 5) or (3 shl 10) or (4 shl 15) or
> (5 shl 20) or (6 shl 25)`; gravar 31 no sétimo e conferir que o byte 4 abre a
> segunda unidade. (b) Contra **imagem real**, na fase 3 e não na 6: ler os
> números de camisa de um time e conferir contra o que o `we2002_core` reporta
> para o mesmo time.

---

## Decisão 3 — `CdImage`: `TFileStream`, e `Read` nunca `ReadBuffer`

O `CFile` do MFC tem três propriedades que o `newWe2002` preservou de propósito
e que o Pascal tem de preservar de novo: ponteiro de arquivo único, **leitura
curta não é erro**, e sempre binário. O `TFileStream` levanta exceção onde o
`CFile` devolvia curto — mas só num dos dois métodos.

**Decisões, todas verificáveis por leitura do fonte:**

| Ponto | Escolha |
|---|---|
| Leitura | **`TStream.Read`**, que devolve quantos bytes leu. **Nunca `ReadBuffer`**, que levanta `EReadError` no fim do arquivo — é ali que a diferença mora |
| Escrita | `TStream.Write`; `WriteBuffer` é aceitável porque escrita curta ali **é** erro |
| Abertura para gravar | `fmOpenReadWrite or fmShareDenyNone`. **Nunca `fmCreate`**: ele trunca uma imagem de 474 MB |
| Posicionamento | `Seek(const Offset: Int64; Origin: TSeekOrigin)`, com `soBeginning` e `soCurrent` |
| EDC/ECC | **não recalcular.** Comportamento do original; "corrigir" quebraria a paridade |
| Modo texto | não existe em `TFileStream`. O risco de `0x0A → 0x0D 0x0A` que o `std::ios::binary` cobria no Windows não se aplica |

Sobre o `Seek`: usar **sempre** a sobrecarga de `Int64`. A antiga
(`Seek(Offset: LongInt; Origin: Word)`) é obsoleta e aceita as mesmas chamadas
com outro significado de `Origin`. Hoje as imagens têm ~474 MB e cabem em
`LongInt`, então a escolha **não** conserta um estouro real — ela evita que
`soBeginning` (0) e `soFromBeginning` (0) e `soCurrent` (1) e
`soFromCurrent` (1) se misturem em revisão futura.

E vale o alerta da §4.5: o `check_seeks()` do transpilador conta seek absoluto
contra relativo, e `soBeginning`/`soCurrent` **têm a mesma cara**. Foi assim que
um `Seek(begin)` virou `SeekCurrent` no `port_database.py` — compilava, passava
nos testes, passava no ASan, e só o confronto com o `ed.exe` mostrou.

> **Teste que prova:** ler 64 bytes a 32 do fim de um arquivo temporário —
> `Read` devolve 32 e **não** levanta exceção; e abrir uma cópia com o modo
> escolhido e fechar sem escrever deixa o tamanho intacto.

---

## Decisão 4 — `char` numérico é `ShortInt`, e `Byte` estaria errado

Não é preciosismo, e a medida é do lado do consumidor.

Os campos `char` que carregam número — `Team.bar_attack` e as outras quatro
barras, `kick_*`, `captain`, `flag_shape`, `slot_role`, `slot_x`, `slot_y`,
`Formation.roles/x/y` — nunca sofrem aritmética em `Database.cpp`: são lidos de
um byte do disco e regravados como um byte. Aí tanto faz.

**O que decide é onde a UI os alarga.** O `newWe2002` faz
`static_cast<int>(f.x[i])` e `static_cast<int>(flag_shape_)`
(`src/app/DefaultTacticsDialog.cpp:122` e `src/app/FlagKitDialog.cpp:123`), e
`char` no x86 **tem sinal**: um byte 200 chega à tela como −56. Mapear para
`Byte` faria o app Lazarus mostrar 200 onde a referência mostra −56 — uma
divergência silenciosa, na tela, num campo que o usuário edita.

**Decisão: `ShortInt`.** `AnsiChar` fica para `char` que carrega texto;
`unsigned char` (o `link[46]` das ML) continua `Byte`, porque no C++ ele já é
sem sinal.

> **Teste que prova:** gravar `$C8` (200) num byte de posição e conferir que o
> lado Pascal lê −56, igual ao `we2002_core`.

---

## Decisão 5 — o sidecar `_url.txt` é byte a byte, e por isso não é `TStringList`

O `Save` grava um arquivo de texto ao lado da imagem, com as 1.911 URLs
(`Database.cpp:1453`), por `std::ofstream` com `std::endl` — no Linux, `LF`.
Esse arquivo é do usuário e não pode ser reescrito com outra convenção.

**Decisão: `TFileStream` com `#10` escrito à mão.** `TStringList.SaveToFile`
usa `LineEnding` da plataforma e, pior, tem `WriteBOM`; nenhuma das duas coisas
deve depender de configuração. `Rewrite`/`WriteLn` de `TextFile` também não,
porque o `TextRec` insere buffer e tradução.

---

## O que **não** entra na camada de dados

`std::map`, `std::vector` e `std::function` aparecem no `we2002_core` **só** em
`Sofifa.hpp`/`Player.hpp` (a classe `FifaPlayer`) e na assinatura do
`Reporter`. O import do SoFIFA está desligado no `newWe2002` desde 2026-08-05 e
**não** é entrada do transpilador. Se um deles aparecer na entrada, o
`FORBIDDEN` da WTE-TASK-17 deve **recusar**, não improvisar contêiner.

---

## Resumo para a WTE-TASK-17

1. Largura fixa em tudo que toca a imagem; `Integer`/`Cardinal`/`PtrInt`
   proibidos por regra, não por gosto.
2. `packed` só no `SquadNumbers`.
3. Cópia de string com semântica de C, sem checagem, e `raw_formation` com 31.
4. Números de camisa por máscara e deslocamento, com os dois testes.
5. `Read` (não `ReadBuffer`), `fmOpenReadWrite` (não `fmCreate`), `Seek` de
   `Int64`, EDC/ECC intocado.
6. `char` numérico com sinal.
7. Contêiner da STL na entrada = recusa do `FORBIDDEN`.
