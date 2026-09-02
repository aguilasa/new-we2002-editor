---
id: PES2-TASK-29
title: "Gravação de asset — fit-or-fail, recompressão só do editado"
type: ferramenta
category: formato
phase: 7
depends_on: [PES2-TASK-27]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.14"
status: concluído
---

# PES2-TASK-29: Gravação de asset

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §1.14, §6.7 e §6.13; a §5(a) e a
  §5(c) do [PLAN-FEATURES](/docs/PLAN-FEATURES.md), que são as duas decisões
  estruturais que esta task herda.
- **É a primeira vez que o projeto escreve fora do banco de texto.** O
  `iso.py inject` já sabe reinjetar arquivo preservando setor e cauda; o que
  falta é remontar o **conteúdo** do arquivo.

### As duas decisões que vêm prontas

**Fit-or-fail.** Orçamento = tamanho original arredondado para cima até o fim
do último setor. Não coube, **recusa e diz quantos bytes faltaram**. Rebuild
de ISO e realocação de extent ficam **fora do projeto** — não "para depois".
O motivo é medido no WE2002 e vale igual aqui: o jogo não acha arquivo por
nome, as LBAs estão cravadas no código MIPS, e o buffer de destino continua do
tamanho antigo mesmo que o diretório ISO seja corrigido.

**Entrada não editada nunca recomprime.** O arquivo guarda os bytes
comprimidos originais de cada entrada e regenera só as que o usuário tocou.
É isso que dá a invariante que serve de teste: *abrir e salvar sem editar
devolve a imagem byte a byte idêntica* — a mesma condição 3 da §0.

### A divergência que esta task tem de resolver, não herdar

A §5(b) do `PLAN-FEATURES` decidiu **recalcular EDC/ECC** no caminho de
assets. A §6.7 deste plano decide **preservar**. As duas não podem valer no
mesmo comando.

A reconciliação proposta, e que a task deve confirmar por medição: **preservar
por padrão** — é o que mantém o round-trip da §0 e o controle negativo do
`iso.py` honestos — e oferecer o recálculo como **comando avulso opt-in**,
que é exatamente o escape hatch `fixecc` que o próprio PLAN-FEATURES prevê.
Nunca ligado à gravação.

---

## Objetivo

Escrever um asset editado de volta na imagem, sem crescer o extent e sem
mexer no que não foi tocado.

### Método

1. **Importar PNG indexado**, validando dimensão, profundidade e paleta contra
   a entrada de destino. Divergência é recusa, não conversão silenciosa.
2. **Recomprimir só a entrada tocada**, remontar o contêiner e conferir o
   orçamento **antes** de escrever.
3. **Descomprimir de volta e comparar antes de ir para o disco** — sem
   exceção, sem flag para desligar.
4. **Escrever pelo `iso.py inject`**, que já preserva setor e cauda.
5. **Controle negativo**, como o do `iso.py`: uma edição de um pixel tem de
   produzir diferença **localizada e contável**, senão a guarda não sabe ficar
   vermelha.

---

### Vindo da PES2-TASK-27: o que o gravador vai encontrar

1. **O registro de entrada tem 16 bytes, não 32**, e há dois tipos: `0x0a`
   imagem (retângulo de VRAM + offset de um fluxo LZSS) e `0x09` CLUT
   (`largura × 1`, carga **crua**, 16 ou 256 cores). Gravar imagem mexe em
   fluxo comprimido; gravar paleta mexe em bytes crus, e as duas coisas têm
   orçamentos diferentes.
2. **A profundidade não está no registro de imagem** — quem a diz é a largura
   do CLUT do contêiner: 16 cores ⇒ 4 bpp, 256 ⇒ 8 bpp. Um gravador que
   assuma 8 bpp escreve metade da largura em `LOGO.BIN`.
3. **Nem todo contêiner tem índice.** Nesta release, 36 têm fluxo e nenhuma
   lista de registros — entre eles `DATSEL_I.BIN` e `DATSEL2I.BIN`, que são
   justamente as cópias de idioma da PES2-TASK-28. Sem índice não há como
   validar dimensão antes de gravar; a política de recusa tem de cobrir esse
   caso explicitamente.
4. **A imagem golden European Deluxe discorda de si mesma em cinco entradas** —
   fluxos que rendem 15.481, 16.395, 16.430, 16.501 e 16.345 bytes onde o
   registro declara 16.384 ou 8.192. É disco **hackeado**, e é a evidência
   direta de que *entrada regravada sem conferir contra o registro produz
   exatamente esse estado*. A japonesa, não hackeada, não tem nenhuma.

### Vindo da PES2-TASK-28: o orçamento já foi visto mordendo

Medido em 2026-09-01 com `tools/pes2/tname.py swap`, que recomprime uma
entrada de `T_NAME_I.BIN` e confere contra a folga até o próximo registro:

- copiar a banda 3 sobre a 2 dá **1.904 B contra 1.868 B de folga** —
  recusado, 36 bytes acima;
- copiar a banda 2 sobre a 3 dá **1.817 B** — passa, e a gravação fecha nas
  duas cópias com round-trip byte a byte.

Duas coisas para o gravador desta task:

1. **A folga é até o próximo registro ou próximo fluxo**, o que vier antes —
   não até o fim do arquivo. É essa a conta que decide o *fit-or-fail*.
2. **"Recomprimir sempre encolhe" é falso por entrada.** Sobre as 28 entradas
   do `T_NAME_I`, o total sai −0,8% (61.212 B contra 61.688), dentro da faixa
   que a §5c mediu — mas **6 das 28 saem maiores**. A §5c fala do agregado; um
   gravador decide por entrada.

## Critério de conclusão

- [x] Abrir e salvar sem editar devolve a imagem **byte a byte idêntica**, nas
      duas releases.
- [x] Trocar uma cor de paleta altera **exatamente** os setores daquele
      arquivo, com a conta.
- [x] Estouro de orçamento **recusa**, dizendo quantos bytes faltaram.
- [x] Toda entrada regravada é descomprimida e comparada antes de ir ao disco.
- [x] Política de EDC/ECC decidida por medição e escrita na §6.7 — com o
      recálculo, se entrar, como comando avulso e nunca no caminho de gravação.
- [x] Controle negativo versionado, provando que a guarda fica vermelha.
- [x] A tela alterada vista no emulador (§4.1 — o oráculo é o jogo).
- [x] Alvo de `ctest` cobrindo o round-trip; *skipped* sem imagem.

---

## Log de Execução

**Executado em:** 2026-09-01. Os oito critérios fechados.

**Resumo do que foi feito.** `tools/pes2/asset_write.py` importa PNG indexado,
recomprime **só** a entrada tocada, confere antes de gravar e recusa o que não
couber; `tools/pes2/asset_screen.sh` produz os quadros do boot no `:98`, que é
a evidência que a §4.1 cobra. O leitor de PNG foi escrito à mão, com os cinco
tipos de filtro, porque `tools/pes2` não tem dependência e o PNG virá do
editor do usuário, não do `bin_archive.write_png`.

**A correção de escopo que a task pedia: são dois orçamentos, não um.** O
markdown definia orçamento como "tamanho original arredondado até o fim do
último setor" — o do *extent*. Esse sai de graça: o `iso.py write_file` recusa
qualquer mudança de comprimento. O que morde é o da **entrada** — a distância
do offset do fluxo até o próximo registro ou próximo fluxo, o que vier antes —
e ele é apertadíssimo: a folga medida nas entradas de `TITLE.BIN` e `LOGO.BIN`
é de **0 a 4 bytes**. Os dois são conferidos, o da entrada primeiro.

**A consequência que um editor precisa saber antes de prometer round-trip:**
reimportar o PNG exportado **sem alterar nada** é recusado em algumas
entradas. `TITLE.BIN` entrada 0 pede 7.858 B e tem 7.836 — 22 acima. Não é
defeito; é o compressor daqui não ser o da Konami. Das 13 entradas de
`TITLE.BIN` e `LOGO.BIN`, **10 recomprimem dentro do próprio orçamento e 3
não**.

**A divergência de EDC/ECC, resolvida por medição.** A §5(b) do
`PLAN-FEATURES` mandava recalcular, a §6.7 mandava preservar. Duas medidas
decidem a favor de preservar:

1. a gravação preserva mesmo — depois de trocar uma cor de paleta do
   `TITLE.BIN`, o setor 4711 tem **2 bytes de dados diferentes**, cabeçalho
   igual e os **280 B de cauda idênticos**; idem no setor 4608 do `LOGO.BIN`,
   com 89 bytes;
2. **o jogo boota e desenha com a cauda obsoleta.** É a prova direta de que
   ele não confere EDC.

A §6.7 foi reescrita com as duas, e o recálculo fica como comando avulso
opt-in (`fixecc`), nunca ligado a gravar.

**A tela, que é o oráculo (§4.1).** Repintei as paletas do `LOGO.BIN` e do
`TITLE.BIN` numa cópia de trabalho — 598 bytes em **2 setores** — e bootei a
release no `:98`. Aos 125 s o disco chega à tela de título e o logotipo, o
`PRESS ANY BUTTON`, o `POWERED BY UMBRO` e o aviso de copyright saem **todos
em magenta**; **11.854 de 76.800 pixels** diferem do mesmo quadro do disco
original. Nenhum quadro entra no git — o que entra é o comando e o número.

**Resultado medido**, `asset_write.py check`, dentro do `pes2_image`:

| Garantia | Medida |
|---|---|
| salvar sem editar | 139 contêineres reescritos, imagem byte a byte igual |
| orçamento recusa | `TITLE.BIN` entrada 0, 22 bytes acima, nada gravado |
| conferir antes do disco | `decompress(compress(x)) == x` nos bytes que vão ser gravados, sem flag |
| controle negativo | um pixel no `LOGO.BIN` entrada 2 muda **745 bytes**, o primeiro no offset da entrada |
| cor de paleta | 2 bytes, **1 setor** (4711), absoluto 11081454 — previsto e medido |
| cauda EDC/ECC | preservada nos dois setores tocados |
| `roms/` | recusado, como no `poke.py` |

`ctest -R pes2` verde em 12,91 s. O disco editado continua passando o
`bin_archive.py check` e o `iso.py roundtrip`.

**Arquivos criados/modificados**

- `tools/pes2/asset_write.py` — novo
- `tools/pes2/asset_screen.sh` — novo
- `tools/pes2/check_image.py` — o `check` de gravação no `pes2_image`
- `tests/CMakeLists.txt` — o comentário do que o `pes2_image` cobre
- `docs/PLAN-PES2-PSX.md` — a §1.14(g) e a §6.7 reescrita
- `docs/tasks/progresso.md`, `docs/prompts/perfil-pes2.md`, `CLAUDE.md` — o
  gate novo e as duas ferramentas

**Problemas encontrados.** Três, todos no caminho e nenhum aberto:

1. **O `depends_on` desta task dizia só a 27.** O critério de tela parecia
   exigir a PES2-TASK-03, e não exige: a tela que um asset editado muda é a de
   **título**, que vem antes de qualquer menu. Não há navegação no caminho, e
   o `asset_screen.sh` só espera. O quadro fica como está.
2. **O FMV de abertura não é pulável por `Start`.** Três `Return` entre 5 s e
   11 s não mudaram um dígito do desvio-padrão dos quadros — o filme
   (`MOVIE/WE2002.STR`, 37 MB) roda até o fim. Por isso a tela de título só
   aparece por volta de **125 s**, e as capturas esperam. Entregar teclas ao
   jogo é assunto da PES2-TASK-03; aqui não foi preciso.
3. **Um susto que não era nada.** O `bin_archive.py check` sobre o disco
   editado passou a relatar "1 contêiner de largura de CLUT mista" onde a
   memória dizia 107 de 8 bpp — parecia registro fantasma criado pelos bytes
   de paleta. Rodando o mesmo comando sobre o original: **idêntico**. É o
   `DAT2D.BIN` que a CORR-PES2-016 já documentou, e a lembrança é que era
   velha.
