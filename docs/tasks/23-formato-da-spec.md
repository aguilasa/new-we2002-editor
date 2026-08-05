---
id: WTE-TASK-23
title: "Decidir o formato de re/spec/ e o vocabulário de veredito"
type: decisão
category: comportamento
phase: 4
depends_on: ["WTE-TASK-09"]
status: pendente
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
`published_methods.tsv` mais os `.md`. É o que a WTE-TASK-29 confere.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/GABARITO.md` | criar |
| `wte/tools/spec_index.py` | criar — gera o índice a partir dos `.md` |
| `wte/re/spec/INDICE.md` | criar (gerado) |

---

## Critério de conclusão

- [ ] Gabarito com os seis campos, e a exigência de evidência por campo
- [ ] Vocabulário de veredito fechado
- [ ] A proibição de colar decompilado escrita no gabarito
- [ ] Gerador de índice funcionando sobre um `.md` de exemplo
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
