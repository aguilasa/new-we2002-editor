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

### Vindo da PES2-TASK-27: as cores de bandeira são entradas de CLUT

Medido em 2026-09-01. No WE2002 os quatro `OFS_FLAG_COLOURS*` caem em
`/BIN/DAT2D.BIN` nos offsets relativos **69798, 73254, 73728 e 75776**, e o
que está ali são **halfwords BGR555 com o bit de semitransparência ligado** —
`0x8dc3 0x8982 0x97bd …` em 69798 **na imagem japonesa**, terminando em
`0x8000 0x8000 0x8000 0x0000`, que é o fim de uma paleta. São entradas de
CLUT, não uma tabela de cor própria. (A European Deluxe é a imagem hackeada e
lê outros valores nos mesmos offsets; a japonesa é a que reproduz o literal.)

Os cinco `OFS_FLAG_SHAPE_COPY_*` são **outra coisa** — forma de bandeira, não
cor — e moram noutros arquivos: `/OPENNING.BIN` +20820, `/SELECT.BIN` +5580 e
+286580, `/SELFORM.BIN` +72400 e `/REPLAYS.BIN` +58304. O **72400** que esta
frase citava até a [CORR-PES2-015](/docs/tasks/CORR-PES2-015.md) é o do
`/SELFORM.BIN`, e em `DAT2D.BIN` +72400 lê-se `0x0d4d 0x118f 0x11d2 0x1613`,
com o bit alto **apagado** — o contrário do que a frase descreve. Quem localiza
os nove é `python3 tools/pes2/ofs_map.py <img>`.

**E é por isso que Moriero teve de cravar offset.** No `DAT2D.BIN` do WE2002 —
nas duas imagens, a japonesa e a European Deluxe — há **23 registros de imagem
e nenhum registro de CLUT**: a região de paleta começa depois da lista, em
65876, e o contêiner não a indexa. No PES2 o mesmo arquivo tem **21 imagens e
266 CLUTs**, com as cargas em 53372..64284 e a lista de registros em
64284..68540.

Consequência prática para esta task: **procure a bandeira pelo índice de CLUT,
não por offset constante.** O `tools/pes2/bin_archive.py ls <img> --file
/BIN/DAT2D.BIN` lista os 266, com offset e largura de cada um; o que falta é
descobrir qual CLUT é de qual seleção, e o caminho barato para isso é um
`poke` de cor com o `run_duckstation.sh`, do jeito que a Fase 2 fez com nome.

**E procure entre as de 16 cores.** Dos 266 CLUTs, **261 são de 16 cores e 5
de 256** — `DAT2D.BIN` é o único contêiner de largura mista dos quatro discos.
A maioria esmagadora diz 4 bpp, e a bandeira quase certamente está entre elas;
a imagem correspondente é, portanto, `largura × 4` pixels, não `largura × 2`.
Exportar com `--clut <um de 16>` já sai na geometria certa — o `export` tira a
profundidade do CLUT que recebe (§1.14(f), CORR-PES2-016). O par
imagem-paleta continua **em aberto**, e é ele que o `poke` resolve.

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
