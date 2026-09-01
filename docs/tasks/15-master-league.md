---
id: PES2-TASK-15
title: "Master League — custos, slots e elencos"
type: engenharia-reversa
category: formato
phase: 4
depends_on: ["PES2-TASK-11"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 4)"
status: pendente
---

# PES2-TASK-15: Master League

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 4, e §1.11.
- **O WE2002 dá âncora dupla:** `OFS_COST_NATIONAL` cai em `SELECT4.BIN`
  (§1.4), e há um bloco inteiro de `OFS_ML_TEAM_NAME_*` em `SELECT2.BIN` —
  incluindo os dois que a Fase 3.5 do `newWe2002` corrigiu de nome
  (`OFS_NOMI_PML1/2` não eram nomes de jogador, eram o 7º e o 8º slot de
  clube de ML).
- **`SELECT4.BIN` é um dos oito que diferem entre as releases sem mudar de
  tamanho** (§1.12), e a §6.4 do `PES2-AJUSTES.md` já o explicou: 99,8% das
  palavras que diferem são rotina realocada, e o resíduo com significado são
  **cinco `slti` de 4 para 2**. Constante de código, não banco. Ou seja: o
  banco de ML, se estiver ali, é **idêntico** nas duas releases — o que dá
  uma verificação de graça.

---

## Objetivo

O que a Master League guarda: custo por jogador, slots de clube, elencos
iniciais.

### Custo: o campo mais reconhecível do conjunto

No WE2002 o custo é **derivado dos atributos** — o editor do Obocaman calcula
preço do jogador e do time inteiro a partir deles, e o `newWe2002` tem uma
divergência deliberada exatamente aí (preço do jogador importado). Duas
consequências:

1. se o PES2 também deriva, **não há tabela de custo** e a task fecha com
   essa resposta, mais a fórmula;
2. se há tabela, ela é `N` valores com `N` igual a uma contagem de jogador
   conhecida (1.399 ou 1.449), e o domínio é largo — o que a distingue de
   quase todo o resto.

Descobrir **qual dos dois** é a primeira medida, não a última.

### Slots de clube de ML

O editor do Obocaman tem *"contador de slots de ML livres na tela"* — o
conceito existe na engine. Localizar quantos são e onde ficam.

---

## Critério de conclusão

- [ ] Custo: tabela localizada **ou** fórmula derivada identificada, com a
      medida que decide entre os dois.
- [ ] Slots de clube de ML: quantos, onde, e o registro de cada um.
- [ ] Elencos iniciais de ML localizados, ou declarados ausentes com a medida.
- [ ] Ao menos um campo verificado por `poke` na tela de Master League.
- [ ] Conferido nas **duas** releases — a §6.4 prevê que sejam idênticos, e
      divergência ali é achado, não ruído.
- [ ] Ferramenta versionada, registrada no `check_image.py`.

---

## Log de Execução

*(a preencher)*
