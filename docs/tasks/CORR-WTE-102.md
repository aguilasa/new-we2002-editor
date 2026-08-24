---
id: CORR-WTE-102
title: "Correção: quatro sítios vivos ainda dizem \"as 94 specs\" onde o índice conta 96"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-102: "as 94 specs" onde hoje são 96

## Problema identificado

A conta de dezessete gravações foi derivada *"lendo a seção `## Bytes tocados`
das **94** specs"*. Era verdade quando a
[WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) a mediu, na primeira
passagem: faltavam as duas specs de preço. A
[WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) as escreveu, e desde
2026-08-24 o índice fecha em **96 com spec**.

A frase sobreviveu em quatro sítios vivos, incluindo o plano — que a usa no
presente, como a receita de quem quiser rederivar o número:

- `docs/PLAN-WTE-LAZARUS.md:943` — quatorze linhas **abaixo** de "96 dos 96 com
  veredito fechado", no mesmo bloco
- `docs/tasks/progresso.md:445`
- `wte/tools/check_fase4.py:28` — cabeçalho do gerador
- `wte/tools/check_fase4.py:95` — *"São as que as 94 specs usam **hoje**"*

**O 17 não muda**, e é por isso que isto é confusão e não defeito de conta: as
duas specs novas declaram `Nenhum` em `## Bytes tocados`, então a população
cresceu e o resultado não. O que engana é a receita — quem a repetir hoje lê 96
arquivos e vai procurar onde perdeu dois.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "94 specs" docs/PLAN-WTE-LAZARUS.md docs/tasks/progresso.md wte/tools/check_fase4.py
python3 wte/tools/spec_index.py --check
ls wte/re/spec/*.md | grep -vcE 'GABARITO|INDICE|README'
```

```text
docs/PLAN-WTE-LAZARUS.md:943:gravação; lendo a seção `## Bytes tocados` das 94 specs, entram os sete de
docs/tasks/progresso.md:445:      lendo a seção `## Bytes tocados` das 94 specs, **entram** os sete de
wte/tools/check_fase4.py:28:`## Bytes tocados` das 94 specs, a diferenca aparece nos dois sentidos:
wte/tools/check_fase4.py:95:# `## Bytes tocados`. Sao as que as 94 specs usam hoje.

96 handlers indexados, 96 com spec, 0 abertos
96
```

E o resultado que não muda, contado na tabela gerada:

```bash
awk '/^## Quem grava na imagem/,/^## A bateria/' wte/re/fase-4.md | grep -c '^| `0x'
```

```text
17
```

| Sítio | População afirmada | Medido hoje |
|---|---:|---:|
| plano, `progresso.md`, `check_fase4.py` (×2) | 94 | **96** |

**Fora do escopo desta correção:** a ocorrência no Log da primeira passagem da
WTE-TASK-31 (`docs/tasks/31-fechamento-fase-4.md:121`). Ali 94 é o que se
mediu naquele dia, e Log é registro histórico.

## Causa raiz

A população cresceu de 94 para 96 quando a WTE-TASK-32 escreveu as duas specs
de preço, e a frase que a cita ficou escrita no presente em quatro lugares.

## Correção

### Arquivos: `docs/PLAN-WTE-LAZARUS.md`, `docs/tasks/progresso.md`

`das 94 specs` → `das 96 specs`. Nos dois casos a frase continua idêntica no
resto: o que entra e o que sai da conta não muda.

### Arquivo: `wte/tools/check_fase4.py`

Linhas 28 e 95: mesma troca. Na 95 (*"as que as 94 specs usam hoje"*) o melhor
é tirar o número — a frase fala das **formas** de escrever "não grava" que o
gerador reconhece, e a população ali é ruído que envelhece sozinho.

### Guarda, se sair barato

O número da população é derivável: o gerador já sabe quantos handlers têm spec.
Emitir a frase com o valor calculado, em vez de literal no comentário, é o que
impede a terceira rodada disto — é o mesmo remédio da
[CORR-WTE-101](/docs/tasks/CORR-WTE-101.md).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar |
| `docs/tasks/progresso.md` | modificar |
| `wte/tools/check_fase4.py` | modificar |

## Verificação

- [ ] `grep -rn "94 specs" docs wte` devolve só o Log da WTE-TASK-31
- [ ] `python3 wte/tools/spec_index.py --check` continua em `96 com spec`
- [ ] A tabela de escritores do `fase-4.md` continua com 17 linhas
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
