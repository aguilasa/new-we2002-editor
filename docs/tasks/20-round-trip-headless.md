---
id: WTE-TASK-20
title: "Round-trip headless contra o we2002_core, nas duas ROMs"
type: verificação
category: dados
phase: 3
depends_on: ["WTE-TASK-18", "WTE-TASK-19"]
status: pendente
---

# WTE-TASK-20: Round-trip headless

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.2 (oráculo B), §6 e Fase 3
  itens 5 e 6.
- É o **aceite da fase 3**, e o primeiro momento em que o projeto afirma algo
  verificado sobre dados.

O oráculo aqui não é o `wte.exe` — é o `we2002_core`, cujo `Load`/`Save` já é
byte-idêntico ao `ed.exe`. Comparação campo a campo, não por olho.

---

## Objetivo

Um programa de console em Pascal que abre a ROM, lê tudo, e um comparador que
confronta com o `we2002_core`.

### 1. O dumper Pascal

Emite, em formato estável e diffável, todo o estado que a camada de dados
carrega: times, jogadores, times de ML, formações predefinidas, números de
camisa, cobradores, links.

### 2. O dumper C++

O equivalente do lado do `we2002_core`. O repositório já tem
`tests/golden_tool.cpp` headless; ou se estende, ou se escreve um irmão.

### 3. O comparador

`diff` dos dois dumps. **Zero divergência** é o critério — diferente do golden
test de imagem, que aceita a faixa conhecida de 16 bytes. Aqui é leitura pura:
não há comportamento indefinido para preservar.

### 4. As duas ROMs

| ROM | O que valida |
|---|---|
| `roms/golden-european-deluxe.bin` | offsets, nomes latinos |
| `roms/japanese-shift-jis.bin` | `KanjiToAscii`/`AsciiToKanji` |

A japonesa é o único teste real do codec de texto. Sem ela, o codec é código não
exercitado.

### 5. Round-trip de gravação

Além de ler: gravar com a camada Pascal e comparar com a gravação do
`we2002_core` a partir do mesmo estado. Aqui a comparação é **byte a byte da
imagem**, e agora sim vale a ressalva conhecida — o `Save` reconstrói as
all-star, e o `Load`+`Save` do original não é idempotente.

### 6. `--check` na bateria

Os `--check` dos geradores das tasks 16, 17 e 18 registrados onde a
WTE-TASK-02 decidiu que a bateria mora.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_estado.pas` | criar |
| `wte/tools/compare_dumps.py` | criar |
| `tests/` (do `newWe2002`) | modificar, se o dumper C++ for extensão do existente |
| `wte/re/fase-3.md` | criar |

---

## Critério de conclusão

- [ ] Dump Pascal e dump C++ idênticos nas **duas** ROMs, zero divergência
- [ ] Codec de texto exercitado pela ROM japonesa
- [ ] Round-trip de gravação byte a byte, com a ressalva das all-star registrada
- [ ] Bitfield de `SquadNumbers` conferido contra imagem real (§8.11)
- [ ] `--check` dos três geradores na bateria de testes
- [ ] Trabalhado só sobre cópia; `roms/` intocada
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
