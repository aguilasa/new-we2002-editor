---
id: WTE-TASK-04
title: "published_methods.tsv — os 96 handlers, com dono"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: pendente
---

# WTE-TASK-04: Mapa de handlers

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.4 e Fase 1 item 2.
- A *published method table* do VMT sobreviveu ao `/STRIP`. Varrendo `.data`
  saem **96** pares nome↔endereço. Isso é o mapa de funções do projeto: em RE
  normal, descobrir 96 nomes de função custa dias.

Formato de cada entrada: `word` tamanho, `dword` endereço, `byte` tamanho do
nome, nome. O protótipo já achou os 96 e ordenou por endereço.

---

## Objetivo

`wte/re/published_methods.tsv` completo e **com a coluna que falta: a que
formulário cada handler pertence**.

### Por que o dono importa

Há colisão de nome — `FormCreate` aparece 17 vezes, `BitBtn1Click` duas,
`SpeedButton1Click` três. Sem o dono, "implementar `FormCreate`" é ambíguo, e a
Fase 2 precisa gerar o stub na unidade certa.

O dono sai do VMT que contém a tabela: cada tabela pertence a uma classe, e o
nome da classe está no próprio VMT. Alternativa, se o VMT resistir: cruzar com
o `OnClick = '<nome>'` dos DFM da WTE-TASK-03 — o DFM diz qual formulário
referencia qual handler.

**Cruzar as duas fontes e reportar discordância** é melhor que escolher uma: um
handler declarado no VMT e não referenciado por nenhum DFM é código morto ou
ligado em runtime, e vale saber qual.

### Colunas

| Coluna | Origem |
|---|---|
| `endereco` | tabela do VMT |
| `handler` | tabela do VMT |
| `formulario` | VMT, conferido contra o DFM |
| `componente` | DFM (`OnClick` de quem) |
| `evento` | DFM (`OnClick`, `OnChange`, `OnMouseDown`, …) |
| `grupo` | classificação manual: carga / edição / gravação / auxiliar |

A coluna `grupo` é o que ordena as tasks 25 a 28.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_published.py` | criar |
| `wte/re/published_methods.tsv` | criar |

---

## Critério de conclusão

- [ ] Os 96 com endereço, ordenados
- [ ] Coluna `formulario` preenchida para todos
- [ ] VMT e DFM cruzados; discordância listada, não escondida
- [ ] Handler sem referência em DFM identificado e anotado
- [ ] `grupo` atribuído aos 96
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
