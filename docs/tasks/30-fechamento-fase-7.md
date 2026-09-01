---
id: PES2-TASK-30
title: "Fechamento da Fase 7 — o que o editor precisa mostrar"
type: verificação
category: formato
phase: 7
depends_on: [PES2-TASK-27, PES2-TASK-28, PES2-TASK-29]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5, Fase 7"
status: pendente
---

# PES2-TASK-30: Fechamento da Fase 7

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5 Fase 7 e §7; a §5 Fase 12 do
  [PLAN-FEATURES](/docs/PLAN-FEATURES.md), que descreve o navegador de assets.
- **É o portão da PES2-TASK-22.** A §0 adverte que decidir linguagem e UI
  antes de o mapa estar verificado é decidir sobre o que a UI não tem o que
  mostrar. O mesmo vale para os assets: um editor desenhado sem saber que há
  grade de imagem × paleta nasce sem lugar para ela.

---

## Objetivo

Fechar a conta da Fase 7 e entregar à PES2-TASK-22 uma lista do que a UI tem
de cobrir.

### Método

1. **A conta dos três números, por eixo** — como a Fase 4 faz: mapeado,
   verificado, aberto. Os eixos são contêiner, entrada gráfica, paleta,
   cópia de idioma e áudio.
2. **O que fica de fora, com razão escrita.** Os `GDC_*` de estádio (34
   arquivos, mais 17 `GRDM_*`) existem no PES2 nos **mesmos LBAs** do WE2002,
   e são TMD — malha 3D. Ficam fora pelo mesmo motivo do
   [PLAN-STADIUMS](/docs/PLAN-STADIUMS.md): é projeto, não feature. Registrar
   que foi medido, para não ser redescoberto e proposto de novo.
3. **A lista para a PES2-TASK-22**: que telas o editor precisa ter, que
   operação cada uma faz, e o que cada uma exige do mapa.
4. **Reconciliar as duas fontes.** Onde a §1.14 e o `PLAN-FEATURES.md`
   divergirem depois das tasks 26–29, corrigir **as duas**, não só a daqui.

---

## Critério de conclusão

- [ ] Os três números por eixo, escritos na §5 Fase 7 do plano.
- [ ] Entregável da Fase 7 preenchido na §7.
- [ ] Estádios (`GDC_*`/`GRDM_*`) medidos e registrados como fora de escopo,
      com o número de arquivos e a coincidência de LBA.
- [ ] Lista do que a UI tem de cobrir, dentro da PES2-TASK-22.
- [ ] Divergências entre `PLAN-PES2-PSX.md` e `PLAN-FEATURES.md` reconciliadas
      nos dois arquivos.
- [ ] `ctest -R pes2` verde, com os alvos novos.

---

## Log de Execução

*(a preencher)*
