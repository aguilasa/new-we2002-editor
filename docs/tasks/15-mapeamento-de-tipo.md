---
id: WTE-TASK-15
title: "Decidir o mapeamento de tipo C++ → Pascal"
type: decisão
category: dados
phase: 3
depends_on: ["WTE-TASK-02"]
status: concluído
---

# WTE-TASK-15: Mapeamento de tipo

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 3 item 2, §8.6 e §8.11.
- **É a única decisão de projeto real da fase 3**, e ela bloqueia os dois
  geradores. Errar aqui produz código que compila, roda, passa em teste
  unitário e grava bytes errados.

Precedente medido no `newWe2002`: `DWORD` virou 64-bit no Linux LP64 e
**embaralhou todos os números de camisa**. A correção foi `std::uint32_t`
explícito. O mesmo risco existe na travessia para Pascal, com outra roupa.

---

## Objetivo

Escrever `wte/re/tipos.md` com a tabela fechada e a razão de cada linha.

### Ponto de partida, para aceitar ou mudar

| C++ (`we2002_core`) | Pascal (FPC) | Motivo |
|---|---|---|
| `std::uint8_t` | `Byte` | |
| `std::uint16_t` | `Word` | |
| `std::uint32_t` | `LongWord` | **nunca** tipo dependente de plataforma |
| `std::int32_t` | `LongInt` | |
| `char[N]` | `array[0..N-1] of AnsiChar` | **não** `string` — ver abaixo |
| bitfield de `SquadNumbers` | acessor explícito | ver abaixo |
| `CdImage` | wrapper sobre `TFileStream` | ver abaixo |

### As três linhas que precisam de decisão escrita, não de tabela

**1. `char[N]` não pode virar `string`.** O original é C++Builder com `char`
fixo e `strcpy`; o truncamento silencioso pode ser load-bearing no formato. O
`newWe2002` descobriu em Release que um `strcpy` estourava um byte em **toda**
imagem aberta — invisível em Debug. Aqui, `string` gerenciada esconderia o
truncamento em vez de reproduzi-lo. Decidir: array fixo, e o comportamento de
estouro vira teste.

**2. Bitfield.** `SquadNumbers` (o ex-`struct NUMERI`) é bitfield. FPC tem
`bitpacked record`, **mas a ordem de bit é definida pelo compilador e pelo
endianness** e não é obrigada a casar com o que o MSVC fez em 2002. Decidir
entre confiar no `bitpacked` (e provar com teste contra imagem real) ou gerar
acessor por máscara e deslocamento. A §8.11 recomenda o acessor.

**3. `CdImage`.** O `CFile` do MFC tem semântica que o port já imita de
propósito: ponteiro de arquivo único, **leitura curta não é erro**, sempre
binário. `TFileStream` levanta exceção onde o `CFile` devolvia curto. Decidir
onde a diferença é absorvida.

### O que não é decisão desta task

Como o gerador implementa. Aqui se decide **o quê**, a WTE-TASK-17 faz o **como**.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/tipos.md` | criar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (Fase 3 item 2, se a tabela mudar) |

---

## Critério de conclusão

- [x] Tabela fechada, uma razão por linha — 16 linhas, os tipos que a entrada
      real usa, não os que o enunciado supôs
- [x] As três linhas difíceis decididas por escrito, não deixadas para o
      gerador — e saíram **cinco**: as três previstas mais o `char` numérico e
      o sidecar `_url.txt`
- [x] Cada decisão com o teste que a prova nomeado
- [x] Nenhum tipo de tamanho dependente de plataforma na tabela
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  [`../../wte/re/tipos.md`](../../wte/re/tipos.md) fechado, e a tabela da
  Fase 3 item 2 do plano ganhou as duas linhas que faltavam mais o ponteiro
  para ele. A tabela não saiu do enunciado: saiu do **inventário do que a
  entrada real usa** — `Database.cpp`, `Player.cpp`, `CdImage.cpp`,
  `TextCodec.cpp` e `Types.hpp`, que são as ~2.150 linhas que o transpilador
  digere.

  As três decisões previstas fecharam como a §8.11 recomendava, e apareceram
  **duas que o enunciado não previa**:

  1. **`char` numérico é `ShortInt`, e `Byte` estaria errado.** Os campos
     `char` que carregam número (as cinco barras, `kick_*`, `captain`,
     `flag_shape`, `slot_role/x/y`) nunca sofrem aritmética em `Database.cpp` —
     entram de um byte do disco e saem como um byte. O que decide é o
     **consumidor**: o `newWe2002` os alarga com `static_cast<int>`
     (`DefaultTacticsDialog.cpp:122`, `FlagKitDialog.cpp:123`) e `char` no x86
     tem sinal, então o byte 200 chega à tela como −56. Com `Byte` o app
     Lazarus mostraria 200 — divergência silenciosa, na tela, num campo que o
     usuário edita.
  2. **O sidecar `_url.txt` não pode sair de `TStringList`.** O `Save` grava as
     1.911 URLs com `std::ofstream` e `std::endl`; `SaveToFile` usa o
     `LineEnding` da plataforma e tem `WriteBOM`, e nenhum dos dois deve
     depender de configuração. Fica `TFileStream` com `#10` à mão.

  Duas precisões nas previstas:

  - **`char[N]` não basta ser array.** A entrada tem **38 `strcpy` e 10
     `strcat`**, que copiam *até o `#0` inclusive* sem comprimento escrito em
     lugar nenhum. O gerador tem de emitir cópia com semântica de C, sem
     checagem — e **não** `StrPCopy`/`StrLCopy`, que truncam de outro jeito. O
     `raw_formation` de 31 bytes vem junto, herdado da correção que o
     `newWe2002` fez em Release com `_FORTIFY_SOURCE`.
  - **No `CdImage` a diferença mora em um método, não na classe.** O
     `TStream.Read` já devolve quantos bytes leu, que é a semântica do
     `CFile`; quem levanta exceção no fim do arquivo é o `ReadBuffer`. Junto
     vão `fmOpenReadWrite` (nunca `fmCreate`, que trunca 474 MB) e a
     sobrecarga de `Seek` de `Int64`.

  Fechou também que **`packed` só se aplica ao `SquadNumbers`**: as classes do
  core não são lidas em bloco — `Load`/`Save` percorrem campo a campo —, e o
  único que vai e volta como blob de 16 bytes é o dos números de camisa
  (`Database.cpp:412` e `:1069`).

- **Problemas encontrados:**

  Nenhum. A decisão que mais deu trabalho foi a do `char` numérico, e ela só
  apareceu porque a pergunta foi feita ao **consumidor** do campo em vez de ao
  campo: em `Database.cpp` os dois mapeamentos são indistinguíveis.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/re/tipos.md` | criar |
  | `docs/PLAN-WTE-LAZARUS.md` | modificar — Fase 3 item 2 |
  | `docs/tasks/15-mapeamento-de-tipo.md` | modificar — Log |
