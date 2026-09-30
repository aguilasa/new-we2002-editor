---
id: CORR-LOOKS-035
title: "Correção: a definição de pronto do plano pede uma tupla que a tabela recusa"
type: correção
category: processo
status: done
depends_on: []
origin: LOOKS-TASK-15
severity: medium
done_on: 2026-09-16
done_commit: 0a2a6cf
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

- [x] o comando do item 3 roda e sai **0**, escrevendo um PNG de 640×640
- [x] a recusa continua escrita como resultado esperado, com a saída 2
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

As duas metades rodaram antes de a linha ser escrita:

```text
$ <venv>/python tools/looks/ui/app.py --screenshot out.png --looks A-I3-A-E-A
  A-I3-A-E-A, figure 0: 598 primitive(s), 361 textured, 5 surface(s), 1196 triangle(s)
  wrote …/done3.png, 640x640
exit=0

$ … --looks A-I3-A-F-A
app: A-I3-A-F-A refuses -- FACE=F is value 5, and the screen was measured to
reach 5 …
exit=2
```

O item 3 passou a pedir a `A-I3-A-E-A` — a vizinha imediata, e a que a
LOOKS-TASK-15 desenhou — **e** a recusa da `A-I3-A-F-A` com saída 2. A recusa
entrou como **segunda metade do critério**, não como ressalva: desenhar um `E`
calado no lugar de um `F` é exatamente a falha que o ciclo existe para não
cometer, então saber recusar é resultado.

E a linha sobre o corpus está lá, medida:

```text
$ python tools/looks/scene.py --corpus <os 50 JPGs>
      31 drawn, 19 refused
      13 x FACE=F is value 5
       3 x FACE=G is value 6
```

**Dezesseis das cinquenta** caem na recusa por `FACE`, e a LOOKS-TASK-18 vai
ler isso como alcance de campo em vez de falha de render quando chegar.

### Problemas encontrados

Nenhum nesta correção. A varredura que a antecedeu puxou um defeito de rótulo
no `app.py` — ele chamava toda nota da cena de "not textured", o que é falso
para a `colour borrowed` e para a `band unmeasured` —, consertado em commit
próprio antes deste.

### Arquivos criados/modificados

- `docs/PLAN-LOOKS-PY.md` — a Definição de pronto, item 3
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-035.md` — este arquivo
_Migrated on 2026-09-21: done_commit approximated from the last commit touching this file._
