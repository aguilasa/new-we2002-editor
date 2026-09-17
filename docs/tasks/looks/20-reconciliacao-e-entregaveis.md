---
id: LOOKS-TASK-20
title: "Reconciliação do plano, `perfil-looks.md` e os entregáveis"
type: documentação
category: fechamento
phase: 7
depends_on: ["LOOKS-TASK-19"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §9"
status: concluído
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

- [x] Cada incógnita da §6 tem veredito escrito: respondida (com a medição) ou
      aberta (com a razão e o que a destravaria). As quatro originais estavam
      respondidas; os resíduos da (c) ganharam o estado de 2026-09-17; e as
      cinco que a execução abriu entraram como (e) a (i), abertas.
- [x] Cada afirmação da §1 que a execução tiver desmentido está **corrigida no
      lugar**, com a data e o que ela dizia antes — as que as tasks e CORRs já
      tinham corrigido, conferidas, e três novas: o título da §1.7, a frase dela
      sobre os discos de PES2, e o veredito da hipótese dos 14 jogadores na
      §1.5.
- [x] `perfil-looks.md` reflete as armadilhas que o ciclo realmente encontrou,
      e não só as previstas — são 32, contadas na seção do perfil, e as duas abaixo conferidas. **Duas já têm conserto medido**, encaminhadas
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
- [x] A definição de pronto da §0 é percorrida item a item, com o resultado de
      cada um — tabela na própria §0.
- [x] `python tools/check_tasks.py` verde, e a conferência de link do
      [.claude/rules/links.md](../../../.claude/rules/links.md) sem linha nova.
- [x] `NOTICE.md` conferido contra o que o projeto de fato usou.
- [x] **O `CLAUDE.md` ganha a seção do `looks`.** Ele descreve cinco
      projetos e não menciona o sexto — nem as duas variáveis da §4.5 do
      plano (`WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`), nem o
      `work/venv-looks/`, nem os alvos de `ctest`. Encaminhado pela
      [`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md)
      em 2026-09-14, que criou as duas variáveis e o venv: documentar no
      plano era o critério dela, e o `CLAUDE.md` é o arquivo que quem chega
      lê primeiro.

---

## Log de Execução

**Executado em:** 2026-09-17 — **CONCLUÍDA**.

### O que se aprendeu

**A reconciliação achou uma contradição dentro de uma seção só.** A §1.7 dizia
que a tag fixa `0x800f` *"nunca esteve errada"* nos discos de PES2 e, parágrafos
abaixo, listava contêineres de PES2 que ela perde. Medido numa cópia da
`(EsIt)`: o `bin_archive.py` acha **zero** registros em `DAT_CG.BIN`,
`EDTR_2D.BIN`, `DATSEL_I.BIN` e `DATSEL2I.BIN`, e parte do `ENDCSR.BIN` — que a
lista desta própria task não tinha. As duas frases tinham sido escritas no
mesmo dia, por tasks diferentes; nenhuma leu a outra.

**O banner do plano dizia "nenhuma fase executada" no fim do ciclo.** É a prosa
vencida que o rito descreve: o documento envelheceu enquanto as seções abaixo
dele eram corrigidas uma a uma.

**A definição de pronto passou, com uma ressalva que ela não previa.** O item 3
pede "um boneco reconhecível", e a janela desenha uma **prateleira** de peças
com o uniforme cinza — a cabeça é reconhecível e traz a pele, o cabelo e a barba
da tupla, mas a pose (e) e o uniforme (f) estão abertos. Está escrito na tabela
da §0 em vez de arredondado para "cumprido".

**E o `NOTICE.md` creditava ao `we3d` uma coisa que o projeto não usou** — o
agrupamento em 14 modelos — e não dizia que duas leituras dele mediram errado.

### Os critérios, um a um

- **§6.** (a), (b) e (d) respondidas. Na (c), os três estilos que não
  escreveram nada (`H1`, `M1`, `N1`) e os quads de nove cabeças continuam
  abertos, com o estado medido em 2026-09-17 (`scene.py --corpus` ainda recusa
  `A-H1-A-A-A` e `D-H1-A-A-A`; `layout.HAIR_QUADS` com as mesmas quatro
  cabeças); a comparação desenho contra desenho foi feita pelas 17 e 18. Novas,
  todas abertas com razão e destrave: **(e)** pose, **(f)** uniforme, **(g)** os
  7 quads ausentes, **(h)** forma sem testemunha e **(i)** as duas corridas de
  ponteiros do `MODEL.BIN`, que é onde a hipótese dos 14 jogadores seria
  conferida.
- **§1.** Corrigidas no lugar: o título da §1.7 (*"e falta a lista de
  paletas"*), a frase sobre PES2, e um veredito datado na §1.5. As demais
  correções da §1 já estavam no lugar, cada uma com a data e a CORR.
- **Perfil.** A **armadilha 2** passou a dizer *corrida de palavras zero*, com
  os 8 e 12 bytes da §1.4. A **armadilha 3 já estava reescrita**, pela
  [`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md), pelo motivo certo —
  e o enunciado deste critério está vencido: ele diz que a varredura "acha as
  onze", e ela acha as **20** a partir do 216. Também corrigidos: a tabela de
  fontes binárias (1.242 → **1.449** registros) e o arquivo quente do
  `bin_archive.py`, que o ciclo não tocou.
- **§0.** Os cinco itens com resultado e ferramenta, na tabela que a §0 ganhou:
  1, 2, 4 e 5 cumpridos; o 3 cumprido na metade que ele mede, com a ressalva da
  prateleira.
- **§9.** Os módulos da §3.2 comparados com o disco: faltava o
  `superpack_count.py` na lista, que entrou. O resto está na tabela da §9.
- **`NOTICE.md`.** A linha do `we3d` diz o que foi tomado e as três leituras não
  tomadas; a do Superpack ganhou o `cabellowe2002.bmp`, que o
  `atlas.py --compare` lê.
- **`CLAUDE.md`.** A seção do sexto projeto: plano, ciclo, as quatro
  variáveis, o venv, os comandos, os quatro alvos e quatro armadilhas.
- **A dívida com PES2** está no
  [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md), na seção (f) do índice do
  contêiner, com a medição. Conserto é decisão do usuário.

### Gates medidos

Na árvore de `4023c65`:

```text
$ ctest --test-dir <build> -R looks          # sem as três variáveis
1/4 Test #10: looks_selftest ...................   Passed   20.45 sec
2/4 Test #11: looks_image ......................***Skipped   0.10 sec
3/4 Test #12: looks_ui .........................***Skipped   0.29 sec
4/4 Test #13: looks_live .......................***Skipped   0.11 sec
100% tests passed out of 4

$ WE2002_LOOKS_IMAGE=<japonesa> WE2002_LOOKS_DRIVE_IMAGE=<inglesa .cue> \
    ctest --test-dir <build> -R looks
1/4 Test #10: looks_selftest ...................   Passed   18.91 sec
2/4 Test #11: looks_image ......................   Passed    2.04 sec
3/4 Test #12: looks_ui .........................   Passed   47.84 sec
4/4 Test #13: looks_live .......................   Passed    9.38 sec
100% tests passed out of 4
# nenhum processo DuckStation depois

$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 21 file(s), 15908 line(s)
  ..... 64 of 64 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py sections
/BIN/EDT_MOD.BIN  36072 B   from   216:  20 section(s), 1218 vertices, 1074 primitives, ... stops at 36072  (the end of the file)
/BIN/MODEL.BIN    64800 B   from  1816: 106 section(s), 2461 vertices, 1767 primitives, ... stops at 64800  (the end of the file)
$ python tools/looks/cli.py check
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok

$ python tools/check_tasks.py               check_tasks: 123 task(s), ok
```

E as corridas que sustentam a §0 e a §6, na mesma sessão e sem mudança de
código desde elas: `ui/app.py --looks A-I3-A-E-A --screenshot` saiu **0**, e
`--looks A-H1-A-A-A` saiu **2** com a mensagem do `HAIR_MAP`;
`confront.py --score` deu `3 win, 2 ranked, 0 expected, 0 unexplained` nos dois
slots, repetíveis em 0 pixel, e `absent 7`; `corpus.py --score` e
`assembly.py --check-image` deram `ok`; `scene.py --corpus` deu
`47 drawn, 3 refused`.

A conferência de link: a varredura de forma do `.claude/rules/links.md` dá a
**mesma saída** antes e depois (diff vazio), e a de destino não acusa nada.

### Problemas encontrados, e para onde foram

- **A contradição da §1.7 sobre PES2** — corrigida no lugar, e a dívida
  registrada no plano de PES2.
- **O enunciado da armadilha 3 neste arquivo está vencido** ("acha as onze") —
  anotado aqui; a armadilha no perfil já estava certa.
- **Nada ficou sem destino.** As cinco incógnitas abertas estão na §6, cada uma
  com o que a destravaria; o ciclo não tem task seguinte para recebê-las.

### Arquivos criados/modificados

Commit `4023c65`:

- `docs/PLAN-LOOKS-PY.md` — banner, §0 (a tabela), §1.5, §1.7, §3.2, §6
  ((c) e as abertas), §8 item 1 e §9 (a tabela)
- `docs/prompts/perfil-looks.md` — armadilha 2, fontes binárias, arquivo quente
- `docs/tasks/looks/progresso.md` — duas armadilhas e a estrutura de pastas
- `docs/PLAN-PES2-PSX.md` — a dívida do campo 7, medida
- `NOTICE.md` — as linhas do `we3d` e do Superpack
- `CLAUDE.md` — a seção do projeto

Commit seguinte: este Log, os critérios e `docs/tasks/looks/progresso.md`.
