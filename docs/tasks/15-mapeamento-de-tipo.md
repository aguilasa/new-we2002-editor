---
id: WTE-TASK-15
title: "Decidir o mapeamento de tipo C++ → Pascal"
type: decisão
category: dados
phase: 3
depends_on: ["WTE-TASK-02"]
status: pendente
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

- [ ] Tabela fechada, uma razão por linha
- [ ] As três linhas difíceis decididas por escrito, não deixadas para o gerador
- [ ] Cada decisão com o teste que a prova nomeado
- [ ] Nenhum tipo de tamanho dependente de plataforma na tabela
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
