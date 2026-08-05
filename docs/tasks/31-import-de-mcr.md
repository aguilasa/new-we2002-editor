---
id: WTE-TASK-31
title: "Import e export de .mcr — memory card do PSX"
type: implementação
category: features
phase: 5
depends_on: ["WTE-TASK-08", "WTE-TASK-24", "WTE-TASK-27"]
status: pendente
---

# WTE-TASK-31: Import de `.mcr`

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.2.
- Segunda das quatro features. Permite trazer jogador de memory card para a
  imagem de CD — o `ed.exe` não faz.

| Handler | Endereço | Papel |
|---|---|---|
| `boton_mcrClick` | `0x0040c2c8` | abre o `.mcr` |
| `boton_mcr2isoClick` | `0x0040c46c` | grava o jogador na imagem |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` |

O readme do original registra que a v0.98 corrigiu "the problem with the captain
and kickers when loading from .mcr files" e "the problem with the Eire's
goalkeeper" — sinal de que o mapeamento `.mcr` → imagem tem casos especiais.

---

## Objetivo

Ler, escrever e converter, com fixture reproduzível.

### O risco declarado, e a mitigação

**Pode faltar `.mcr` de teste variado.** Mitigação prevista no plano: o
`grabar_memoryClick` do próprio original **escreve** `.mcr`. Então dá para gerar
fixture — editar um jogador conhecido no original, exportar, e usar o arquivo
como entrada do teste de import.

`data/dat.bin` começa com `MC` e tem 145.408 bytes contra os 131.072 de um
memory card padrão. A WTE-TASK-08 já deve ter classificado o arquivo e explicado
os 14.336 de diferença; se não explicou, explicar aqui antes de usá-lo como
fixture.

### O formato

Memory card do PSX é parcialmente documentado publicamente — cabeçalho, tabela
de blocos, diretório. Usar a documentação pública para o **contêiner**, e
engenharia reversa só para o **conteúdo** do bloco do WE2002, que é específico
do jogo.

Essa divisão poupa a maior parte do trabalho.

### Os casos especiais

O readme aponta três, e cada um vira teste:

1. **Capitão e cobradores** ao carregar de `.mcr`
2. **Goleiro da Eire** — provável caso de índice fora do padrão
3. **Espaços no nome do jogador**

Um bug corrigido pelo autor é um caso que o formato tem; reproduzir a *correção*,
não o bug.

### Round-trip

Exportar do app e importar de volta tem de dar o mesmo estado. E exportar do app
vs. exportar do original, a partir do mesmo jogador, tem de dar o **mesmo
arquivo** — é o golden test desta feature.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/boton_mcr*.md` | criar |
| `wte/re/mcr.md` | criar — contêiner (público) e conteúdo (revertido) |
| `wte/src/we2002_mcr.pas` | criar |
| `wte/tests/fixtures/*.mcr` | criar — geradas pelo próprio original |
| `wte/tests/test_mcr.pas` | criar |

---

## Critério de conclusão

- [ ] Contêiner lido conforme documentação pública, com a fonte citada
- [ ] Conteúdo do bloco do WE2002 mapeado
- [ ] Fixtures geradas pelo original, não à mão
- [ ] Os três casos especiais do readme cobertos por teste
- [ ] Round-trip export/import estável
- [ ] Export do app byte-idêntico ao export do original
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
