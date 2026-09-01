---
id: WTE-TASK-23
title: "Decidir o formato de re/spec/ e o vocabulário de veredito"
type: decisão
category: comportamento
phase: 4
depends_on: ["WTE-TASK-09"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §2 e Fase 4"
status: concluído
---

# WTE-TASK-23: Formato da spec

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §2 e Fase 4.
- **É a task que torna o método do projeto executável.** A §2 decide
  *recuperação de especificação, não transcrição*: o decompilador responde
  perguntas, a resposta vai para um `.md`, e o Pascal é escrito a partir do
  `.md`.

Sem formato definido, "escrever a spec" vira nota livre, e a fronteira entre
spec e transcrição some — que é exatamente o que a §2 existe para impedir.

---

## Objetivo

Definir o gabarito de `wte/re/spec/<handler>.md` e o vocabulário de veredito.

### O gabarito deve exigir

| Campo | Por quê |
|---|---|
| entrada | que estado da tela e da imagem o handler lê |
| saída | que estado ele muda |
| bytes tocados | offset e tamanho, ou "nenhum" |
| pré-condições | o que o original checa antes de agir |
| comportamento de erro | o que faz com entrada inválida |
| evidência | como se sabe: diff medido, disassembly lido, ou observação de tela |

O campo **evidência** é o que separa fato de suposição. Um handler com spec
inteira marcada "observação de tela" é hipótese, não spec, e o veredito tem de
refletir isso.

### O vocabulário de veredito

Proposta de partida, para fechar:

| Veredito | Significa |
|---|---|
| `implementado` | spec escrita, Pascal escrito, golden verde |
| `trivial` | só habilita/desabilita controle; não toca imagem |
| `divergência deliberada` | o port faz diferente, de propósito, e está registrado |
| `não portado` | fora de escopo, com justificativa escrita |
| `aberto` | ainda não estudado |

**"Não portado" sem justificativa não é veredito** — o critério de pronto da
Fase 4 depende disso.

### O que a spec não deve conter

Código C++ decompilado colado. Se a spec precisar de trecho para ser entendida,
o trecho vai **parafraseado** — pseudocódigo ou prosa —, nunca copiado. Escrever
isso no gabarito, para não depender de memória.

### Índice

Um arquivo que lista os 96 com veredito corrente, gerado do
`published_methods.tsv` mais os `.md`. É o que a WTE-TASK-31 confere.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/GABARITO.md` | criar |
| `wte/tools/spec_index.py` | criar — gera o índice **e valida cada spec** |
| `wte/tools/test_spec_index.py` | criar — as rotas de recusa (eram onze na execução; as 15 do `grep -c "raise SpecError"` foram fechadas pela [CORR-WTE-041](/docs/tasks/concluidos/CORR-WTE-041.md)) |
| `wte/re/spec/INDICE.md` | criar (gerado) |
| `wte/re/spec/README.md` | modificar — deixou de dizer "vazio até a 23" |
| `wte/tools/README.md` | modificar — as duas tabelas |

---

## Critério de conclusão

- [x] Gabarito com os seis campos, e a exigência de evidência por campo
- [x] Vocabulário de veredito fechado — cinco, sem acento e sem variante
- [x] A proibição de colar decompilado escrita no gabarito — **e verificada
      pelo gerador**, não só escrita
- [x] Gerador de índice funcionando sobre um `.md` de exemplo — exemplo
      sintético, no `test_spec_index.py`; ver o Log
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  Gabarito, vocabulário fechado, gerador de índice e os 96 indexados como
  `aberto`. O gabarito tem as cinco seções obrigatórias na ordem, cada uma com
  a própria linha `**Evidência:**` escolhida entre quatro valores — `diff
  medido`, `disassembly lido`, `observação de tela`, `não medido` —, e o
  vocabulário de veredito ficou em cinco, **sem acento e sem espaço
  alternativo**, para não existirem duas grafias do mesmo veredito.

  **A decisão que mudou a natureza da task: a proibição da §2 virou código.**
  O enunciado pedia a proibição *escrita no gabarito*. Escrita, ela vale o que
  vale a memória de quem escreve a spec às duas da manhã na fase 4. O
  `spec_index.py` **recusa** o arquivo que tenha bloco marcado `c`/`cpp`, os
  nomes que o Ghidra inventa (`undefined4`, `uVar1`, `local_1c`, `param_1`,
  `DAT_…`, `FUN_…`) ou `__fastcall` — e aceita pseudocódigo em bloco `text`,
  que é a rota certa. É o irmão do `FORBIDDEN` do `port_database.py`, no
  mesmo espírito da §8.10.

  Duas outras regras do gabarito que são mecânicas e por isso moram no
  gerador, em vez de no texto:

  - `nao portado` exige seção `## Justificativa` não vazia — o critério de
    pronto da fase 4 depende disso, e a WTE-TASK-31 confere pelo índice;
  - `implementado` com **toda** a evidência em `observação de tela` / `não
    medido` é recusado: isso é hipótese, não spec, exatamente como o enunciado
    diz.

  Mais três guardas que só apareceram ao escrever: frontmatter que discorda do
  `published_methods.tsv` (endereço, dono), spec órfã (nome que não casa com
  handler nenhum — um nome errado sumiria do índice em silêncio) e seção
  faltando.

  Nome de arquivo: **`<formulario>.<handler>.md`**. O par é único nos 96, o
  nome solto não — há 16 `FormCreate`, 2 `FormShow` e quatro famílias de
  `BitBtnNClick` em formulários diferentes.

  **O "`.md` de exemplo" do critério é sintético, e de propósito.** Uma spec de
  verdade é trabalho da WTE-TASK-25 em diante; commitar uma spec inventada só
  para o gerador ter o que ler poria hipótese em `re/spec/` com cara de fato —
  que é o oposto do que o campo de evidência existe para impedir. O exemplo
  vive no `test_spec_index.py`, em diretório temporário, e são 19 testes.

- **Problemas encontrados:**

  1. **A coluna `evento` do TSV quebra tabela markdown.** Ela guarda um evento
     por controle atendido, separados por `|` — `ficha_color.barraChange` sai
     como `OnChange|OnChange|OnChange`, porque serve três barras. O `|` cru
     partia a linha da tabela em oito células. Vira `OnChange x3`, e há teste.
  2. Um dos 96, `MainForm.Button2Click`, tem a coluna `evento` **vazia**: é
     publicado e não está ligado a evento nenhum em DFM algum (a WTE-TASK-04 já
     o marcava "sem referencia em DFM"). Sai como `—` no índice.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/re/spec/GABARITO.md` | criar |
  | `wte/tools/spec_index.py` | criar |
  | `wte/tools/test_spec_index.py` | criar (19 testes) |
  | `wte/re/spec/INDICE.md` | criar (gerado) |
  | `wte/re/spec/README.md` | modificar |
  | `wte/tools/README.md` | modificar |
