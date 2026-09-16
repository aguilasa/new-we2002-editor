---
id: LOOKS-TASK-20
title: "Reconciliação do plano, `perfil-looks.md` e os entregáveis"
type: documentação
category: fechamento
phase: 7
depends_on: ["LOOKS-TASK-19"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §9"
status: pendente
---

# LOOKS-TASK-20: Reconciliação e fechamento

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §9.
- A regra do repositório: **o que a execução muda no plano, muda na seção que
  mudou**, não num apêndice de erratas. O banner do plano indexa as mudanças.
- As incógnitas da §6 ou foram respondidas, ou continuam abertas **com a razão
  medida** — nenhuma das duas coisas pode ficar implícita.

---

- **Dívida com o ciclo de PES2, medida aqui e não corrigida aqui.** Em
  2026-09-15 a [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md)
  mediu que o campo 7 do registro de `BIN/*.BIN` **não é a tag constante
  `0x800f`** que o `tools/pes2/bin_archive.py` documenta: é o banco de 64 KiB do
  offset de 16 bits do campo 6, com viés para que o banco 0 valha `0x800f`
  (§1.7 do plano, com a tabela de seis contêineres que o prova pelo LZSS). O
  efeito **alcança os discos de PES2**: hoje o `entries()` não vê as listas de
  `DAT_CG.BIN`, `DATSEL2I.BIN`, `DATSEL_I.BIN` e `EDTR_2D.BIN` na release
  `(EsIt)`. Não foi consertado por aqui porque `bin_archive.py` é de outro ciclo
  e o pool de correções não atravessa pasta. **Esta task leva o item adiante:
  registrar a dívida para o ciclo de PES2 é entregável, consertá-la lá é decisão
  do usuário.**

---

- **Três incógnitas chegam aqui abertas da LOOKS-TASK-17, cada uma com a razão
  medida.** 2026-09-16
  ([`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md)):
  **(1) a pose** — onde cada peça fica não está em arquivo nenhum lido, e o
  confronto não precisou dela porque a métrica é de cor; quem posiciona é a
  display list, que dá coordenada de tela e não de modelo. **(2) o uniforme** —
  237 das 593 primitivas amostram páginas dos 105 `TEX_*.BIN`, que não têm
  digest no `layout.py`; o confronto foi feito na cabeça para não depender
  deles. **(3) sete quads da cabeça não aparecem nas duas faixas de display list
  lidas** no quadro de referência (`confront.py --score`, `absent 7`) — a
  hipótese é descarte de face de costas para a câmera do jogo, e não foi
  medida. As três vão para a §6 como abertas, com isto escrito.
- **E uma quarta, da LOOKS-TASK-18: forma não tem testemunha.** 2026-09-16
  ([`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md)):
  histograma de cor resolve pele, cor de cabelo e cor de barba, e **não**
  resolve estilo de cabelo nem barba — nem contra os quadros do emulador, onde a
  verdade é conhecida (`corpus.py --score`, o controle). Nenhum dos dois
  confrontos do ciclo verifica, então, que a **malha** desenhada é a do estilo
  certo; quem verifica isso hoje é só o `--patched` da LOOKS-TASK-14. Fica
  aberta, com a razão.

---

## Objetivo

Fechar o ciclo com plano, perfil e entregáveis batendo com o que existe no
disco.

---

## Critério de conclusão

- [ ] Cada incógnita da §6 tem veredito escrito: respondida (com a medição) ou
      aberta (com a razão e o que a destravaria).
- [ ] Cada afirmação da §1 que a execução tiver desmentido está **corrigida no
      lugar**, com a data e o que ela dizia antes.
- [ ] `perfil-looks.md` reflete as armadilhas que o ciclo realmente encontrou,
      e não só as previstas. **Duas já têm conserto medido**, encaminhadas
      pela [`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md) em
      2026-09-14:
      - a **armadilha 2** diz “o par de zeros que separa grupos”; são **8
        bytes no `MODEL.BIN` e 12 nas duas primeiras folgas do
        `EDT_MOD.BIN`**, então a regra é *corrida de palavras zero*, e a
        forma fixa é que produz o `nPrim` na casa dos bilhões (§1.4);
      - a **armadilha 3** diz que varrer o `EDT_MOD.BIN` sem a lista
        “pega uma seção e para”. Com a regra da corrida a varredura
        **acha as onze e termina no EOF exato**; a lista continua
        necessária, mas pela **ordem** — que é outra (§1.5). Reescrever a
        armadilha pelo motivo certo vale mais que apagá-la.
- [ ] A definição de pronto da §0 é percorrida item a item, com o resultado de
      cada um.
- [ ] `python tools/check_tasks.py` verde, e a conferência de link do
      [.claude/rules/links.md](../../../.claude/rules/links.md) sem linha nova.
- [ ] `NOTICE.md` conferido contra o que o projeto de fato usou.
- [ ] **O `CLAUDE.md` ganha a seção do `looks`.** Ele descreve cinco
      projetos e não menciona o sexto — nem as duas variáveis da §4.5 do
      plano (`WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`), nem o
      `work/venv-looks/`, nem os alvos de `ctest`. Encaminhado pela
      [`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md)
      em 2026-09-14, que criou as duas variáveis e o venv: documentar no
      plano era o critério dela, e o `CLAUDE.md` é o arquivo que quem chega
      lê primeiro.

---

## Log de Execução

*(preencher ao executar)*
