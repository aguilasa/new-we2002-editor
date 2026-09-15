---
id: LOOKS-TASK-15
title: "`ui/viewer.py` e `ui/app.py` — `QOpenGLWidget`, câmera orbital e uma tupla na tela"
type: implementação
category: ui
phase: 5
depends_on: ["LOOKS-TASK-14"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §3.2"
status: pendente
---

# LOOKS-TASK-15: O visualizador

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §3.2, §3.3
  (regra 3) e §4.3.
- **`QOpenGLWidget`, não Qt3D nem rasterizador em Python.** O Qt3D é módulo
  grande e meio abandonado no Qt6 (§4b do
  [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md)); rasterizar em Python puro é
  inviável sem `numpy`, que **não está instalado** e cuja instalação é decisão
  do dono da máquina.
- A UI **não conhece endereço** e o núcleo **não conhece Qt**.

---

- **Existe um gabarito da geometria já desenhada, e ele é alcançável.** Medido
  em 2026-09-15 pela
  [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) com
  `python tools/looks/oracle.py --buffers`: as duas faixas de RAM em que todo
  campo de LOOKS escreve são **listas de display do PSX**, dobradas —
  `0x80153000` e `0x80162000`, a `0xF000` uma da outra, com 365 e 440 nós, a
  maioria esmagadora deles **quad texturizado**. Cada nó é `[link][pacote]`, e o
  pacote traz os `(u, v)`, o CLUT e a página de textura **já resolvidos**, mais
  as coordenadas de tela. Se o render sair diferente do jogo, é ali que se
  compara vértice a vértice, em vez de só comparar quadros.

---

- **O atlas já é exportável, colorido, por comando.** Desde 2026-09-15
  ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)):
  `python tools/looks/atlas.py --export <dir>` grava as 23 imagens do
  `DAT2D.BIN` como PNG de paleta, cada uma na profundidade e com a paleta que a
  própria geometria nomeia. O `atlas.texel()` e o `atlas.image_at()` são o que o
  renderizador precisa para ir de `(página, u, v)` ao texel certo.
- **E o uniforme vem de outro arquivo, por time.** As páginas e as paletas de
  kit estão em **105 `TEX_*.BIN`**, com **cinco** paletas de 256 entradas em
  cada — duas em (0, 486), duas em (0, 488) e uma em (256, 480) que a geometria
  não nomeia ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)). Qual
  das duas de uma id o jogo usa é pergunta da
  [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md), e chega aqui
  decidida. Um visualizador que carregue só o `DAT2D.BIN` desenha o boneco
  pelado — não por bug, por arquivo faltando.
- **Duas paletas que a geometria nomeia não estão em contêiner nenhum do
  disco:** (0, 485) e (336, 510). Se o render sair com uma peça cinza, é uma
  delas, e não um erro de leitura.

---

## Objetivo

Uma janela que desenha o boneco de uma tupla de LOOKS, e que se deixa dirigir
de fora.

---

## Critério de conclusão

- [ ] `ui/viewer.py` desenha as peças com `QOpenGLWidget`, câmera orbital, e os
      modos sólido e wireframe.
- [ ] A cor chega pelo caminho que a LOOKS-TASK-12 decidiu.
- [ ] `ui/app.py --looks A-I3-A-F-A` monta e desenha aquela tupla.
- [ ] `--smoke` abre a janela, pinta um quadro e sai com 0.
- [ ] `--screenshot out.png` grava a imagem **fora da tela** — `:98` no Linux,
      janela em −32000 no Windows (§4.3). Nenhuma janela aparece para o
      usuário.
- [ ] Varredura: nenhum `import layout` em `ui/`; e depois de importar o núcleo
      inteiro, `PySide6` não está em `sys.modules`.

---

## Log de Execução

*(preencher ao executar)*
