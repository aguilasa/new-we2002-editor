---
id: PES2-TASK-14
title: "Bandeiras — forma e cores"
type: engenharia-reversa
category: formato
phase: 4
depends_on: ["PES2-TASK-13"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 4)"
status: pendente
---

# PES2-TASK-14: Bandeiras

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 4, e §1.11.
- **A âncora é a mesma da PES2-TASK-13:** `BIN/DAT2D.BIN`, e o
  `OFS_FLAG_COLOURS_SENEGAL` do WE2002 que cai nele. Por isso esta task vem
  depois — a vizinhança já terá sido lida uma vez.
- **O editor do Obocaman desenha bandeira 2D em tempo real com colar-cores**
  (ver o `CLAUDE.md`, seção do `make wte`), o que prova que o formato do
  WE2002 é simples e legível. Não é o mesmo jogo; é a mesma engine (§1.4).

---

## Objetivo

A estrutura de bandeira: forma (o padrão de faixas ou o desenho) e as cores.

### O que o WE2002 separa, e que vale conferir aqui

No WE2002 há uma decisão explícita do port sobre bandeira — o *"teste único
de tem bandeira própria"* é uma das quatro divergências deliberadas da Fase 5
do `newWe2002`. Isso diz que o formato tem pelo menos dois níveis: **ter ou
não bandeira própria**, e **qual**. Conferir se o PES2 mantém a distinção.

### Verificação

Como a PES2-TASK-13: bandeira é visual, e um `poke` fecha o laço em uma
corrida. A tela de seleção de seleção nacional mostra a bandeira, e é
alcançável pelo roteiro `team-select` da PES2-TASK-03.

---

## Critério de conclusão

- [ ] Tabela de bandeira localizada, com âncora, delta assinado e contagem.
- [ ] Forma e cores separadas, cada uma com codificação medida.
- [ ] Verificado por `poke`: mudar a bandeira no disco muda o desenho na tela.
- [ ] A distinção "tem bandeira própria" conferida — existe no PES2 ou não.
- [ ] Ferramenta versionada, registrada no `check_image.py`.

---

## Log de Execução

*(a preencher)*
