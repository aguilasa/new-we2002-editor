---
id: CORR-WTE-085
title: "Correção: o plano e o progresso ainda dizem \"seis gravações\" onde a ferramenta mede dezessete"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-085: o plano e o progresso ainda dizem "seis gravações"

## Problema identificado

A [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) refutou a conta de seis
gravações — mediu **nove** — e a
[WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) a remediu por ferramenta:
são **dezessete**. O número corrente entrou no
[`wte/re/fase-4.md`](../../wte/re/fase-4.md) (gerado pelo
[`check_fase4.py`](../../wte/tools/check_fase4.py)) e na Fase 4 do plano, mas
**duas linhas vivas continuam afirmando seis**, uma delas no próprio plano, que
é a fonte de verdade do projeto:

- `docs/PLAN-WTE-LAZARUS.md:945` — no preâmbulo da Fase 5
- `docs/tasks/progresso.md:122` — no mesmo parágrafo, copiado

O plano se contradiz a **dezesseis linhas de distância**: a linha 929 diz
"nem seis nem nove, são dezessete", e a 945 diz "duas das seis gravações".

Nenhum gate pega isso: `make -C wte check` fecha verde, e o perímetro do
`check_fase1.py` só varre os quatro números da fase 1.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "seis gravações" docs/PLAN-WTE-LAZARUS.md docs/tasks/progresso.md
grep -n "nem seis nem nove" docs/PLAN-WTE-LAZARUS.md
grep -n "São \*\*17\*\*" wte/re/fase-4.md
```

```text
docs/tasks/progresso.md:122:*origem dos bytes* de duas das seis gravações, e ficar na mesma task que a
docs/PLAN-WTE-LAZARUS.md:945:(§5.2) e a camisa 2D (§5.3) são a *origem dos bytes* de duas das seis gravações
docs/PLAN-WTE-LAZARUS.md:929:seis nem nove, são dezessete.** Nove é o número de quem alguém *chamou* de
wte/re/fase-4.md:73:São **17**, e o número não é o que as tasks
```

| Sítio | Valor afirmado | Fonte |
|---|---|---|
| `docs/PLAN-WTE-LAZARUS.md:945` | 6 | escrito na época da WTE-TASK-27 |
| `docs/tasks/progresso.md:122` | 6 | cópia do parágrafo do plano |
| `docs/PLAN-WTE-LAZARUS.md:929` | 17 | WTE-TASK-31 |
| `wte/re/fase-4.md:73` | 17 | `check_fase4.py`, gerado |

## Causa raiz

A conta subiu duas vezes (6 → 9 na WTE-TASK-30, 9 → 17 na WTE-TASK-31) e o
parágrafo do preâmbulo da Fase 5, que fala de *duas* gravações e usa o total só
como pano de fundo, não foi varrido em nenhuma das duas.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

Linha 945: `duas das seis gravações` → `duas das dezessete gravações`. O que a
frase precisa dizer continua sendo "duas delas", e o total só situa; escrever o
número corrente evita que a próxima leitura tome o preâmbulo por atualizado.

### Arquivo: `docs/tasks/progresso.md`

Linha 122: mesma troca, e o parágrafo já linka a tabela-âncora do plano.

### Arquivo: `wte/tools/check_fase1.py` *(opcional, decidir na execução)*

O `6` é dígito curto demais para virar sítio do `check_fase1.py` sem falso
positivo. A alternativa barata é o `check_fase4.py` — que já conhece o número
corrente — passar a recusar a forma `\bseis gravaç` e `\bnove gravaç` fora dos
arquivos de narração (`docs/tasks/*.md` concluídas, `correcoes-progresso.md`),
que é o mesmo desenho de perímetro que a fase 1 usa.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar |
| `docs/tasks/progresso.md` | modificar |
| `wte/tools/check_fase4.py` | modificar (opcional — a guarda) |

## Verificação

- [ ] `grep -rn "seis gravações" docs/PLAN-WTE-LAZARUS.md docs/tasks/progresso.md` sai vazio
- [ ] `make -C wte check` continua verde
- [ ] Se a guarda entrar: ela reprova com um `seis gravações` plantado numa
      linha viva, e passa com a citação histórica do `correcoes-progresso.md`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
