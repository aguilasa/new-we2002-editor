---
id: CORR-LOOKS-035
title: "Correção: a definição de pronto do plano pede uma tupla que a tabela recusa"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-035: o item 3 da definição de pronto sai 2

## Problema identificado

A **Definição de pronto** do plano, que é o critério de aceitação do projeto
inteiro, tem cinco itens, e o terceiro é:

```text
docs/PLAN-LOOKS-PY.md:54
3. `python tools/looks/ui/app.py --screenshot out.png --looks A-I3-A-F-A`
   produz um boneco reconhecível, com a pele e o cabelo daquela tupla.
```

`A-I3-A-F-A` é **recusada** desde 2026-09-16: a LOOKS-TASK-14 andou a linha
`FACE` de ponta a ponta e mediu a tela alcançando **cinco** valores dos oito
que os bits guardam, então o `assembly` recusa o `F` em vez de desenhar um `E`
calado. O comando não produz boneco nenhum — imprime a recusa e sai **2**.

A LOOKS-TASK-15 sabia disso e escreveu no próprio critério que a tupla do
enunciado era uma recusa medida; corrigiu a §5.6 no lugar, como manda o perfil,
e **não** alcançou esta linha. Ela é a que alguém lê primeiro, e é a que a
LOOKS-TASK-20 vai conferir ao fechar o ciclo.

## Evidência

```text
$ <venv>/python tools/looks/ui/app.py --looks A-I3-A-F-A --screenshot out.png
app: A-I3-A-F-A refuses -- FACE=F is value 5, and the screen was measured to
reach 5 -- 16 rows a band of the same image, bands 0 to 4, and then it clamps.
Its labels name seven and its bits hold eight
exit=2
```

E não é um caso isolado do corpus: das 50 tuplas do Superpack, **dezesseis**
carregam `F` ou `G` na linha `FACE`, e são a maior parte das 19 recusas que o
`scene.py --corpus` conta.

```text
$ python tools/looks/scene.py --corpus <os 50 JPGs>
      31 drawn, 19 refused
      13 x FACE=F is value 5
       3 x FACE=G is value 6
```

## Causa raiz

A definição de pronto foi escrita antes de o alcance da barba ser medido, e a
correção de 2026-09-16 alcançou a §5.6 mas não a §0.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md` (Definição de pronto, item 3)

Trocar a tupla por uma que a tabela desenha — `A-I3-A-E-A` é a vizinha imediata
e foi a desenhada pela LOOKS-TASK-15 — e **acrescentar a recusa como segunda
metade do item**, porque ela é resultado e não obstáculo: pronto é desenhar a
tupla desenhável **e** recusar a não medida com a mensagem da tabela e saída 2.
Escrito assim, o item cobre o que o projeto aprendeu em vez de esconder.

Vale dizer ali, em uma linha, que dezesseis das cinquenta tuplas do corpus
caem na recusa por `FACE`, para que a LOOKS-TASK-18 não leia isso como falha do
render quando chegar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [ ] o comando do item 3 roda e sai **0**, escrevendo um PNG
- [ ] a recusa continua escrita como resultado esperado, com a saída 2
- [ ] `python tools/check_tasks.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
