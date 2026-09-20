---
id: LOOKS-TASK-30
title: "Incógnita (n) — o uniforme: qual `TEX_*.BIN`, na guarda, e as primitivas vestidas"
type: implementação
category: textura
phase: 10
depends_on: ["LOOKS-TASK-20"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (n)"
status: pendente
---

# LOOKS-TASK-30: O uniforme

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (n) e §6 (f).
- **237 primitivas da figura 0 (429 da figura 1) saem cinza** porque amostram
  páginas dos `TEX_*.BIN` (`assembly.py --check-image`), e a guarda não lê o
  que não sabe conferir.
- **Toda leitura de textura sai do disco japonês** (Fase 3), com o digest no
  `layout.py` antes do primeiro byte. Na `golden-european-deluxe.bin`, 18 dos
  105 são form 2 (§8, item 5); no japonês, medir.
- **Qual arquivo a tela carrega se mede na VRAM**, não pelo nome.

---

## Objetivo

Vestir o boneco com o uniforme que a tela `LOOKS SET` mostra: o `TEX_*.BIN`
certo, pela guarda, com páginas e CLUTs resolvidos.

---

## Critério de conclusão

- [x] Os digests dos `TEX_*.BIN` japoneses no `layout.py`, com a forma de
      cada um medida, e o `iso_source.py --check-discs` estendido.
- [x] Qual `TEX_*.BIN` a tela dos dois states carrega, medido contra a VRAM.
- [x] Zero `no image` no relatório do `ui/app.py`, ou o resto nomeado com o
      motivo.
- [x] **O confronto de cor da §5.3 re-rodado com o uniforme:** as tuplas
      continuam em primeiro lugar.
- [x] Controle negativo: o `TEX_*.BIN` de outro time fica vermelho.
- [x] §6 (f) e §10.3 (n) com o veredito e a data.

---

## Log de Execução

- **Executado em:** 2026-09-20
- **Resumo do que foi feito:** o uniforme é **por time** e mora nos 105
  `TEX_*.BIN`, que entraram na guarda com digest medido — todos **form 1** e
  **idênticos nos dois discos**, medido, o que é por que o `--check-discs`
  passou a aceitá-los dos dois lados. Qual deles a tela veste **se mede na
  VRAM** (`oracle.py --kit`, novo): cada retângulo que cada contêiner declara
  contra o frame buffer do console, halfword a halfword. Nos dois states é o
  **`TEX_A4`**, que reproduz exatas a página (576, 384) e as paletas (0, 486) e
  (0, 488), e nenhum outro contêiner reproduz nenhuma das três — o mais
  próximo erra 789 halfwords delas. Com ele no `draw_list`, o boneco sai
  vestido: **593 de 593** primitivas texturizadas na figura 0 e **629 de 629**
  na figura 1, zero `no image` e zero `no palette`.
- **Arquivos criados/modificados:** `tools/looks/layout.py` (os 105 digests em
  `KIT_DIGEST`, `KIT_TAGS`, `KIT_FILES`, `kit_path`/`kit_tag`,
  `expected_digest`, a família da guarda e `KIT_ON_SCREEN`);
  `tools/looks/iso_source.py` (`Disc.form_of`, os kits no `--check-discs` e a
  expectativa do disco inglês corrigida); `tools/looks/oracle.py` (`--kit`:
  `check_kit`, `_kit_records`, `_kit_payload`, `_record_difference`,
  `_kit_difference`, `_vram_words`); `tools/looks/assembly.py` (`draw_list`
  com o contêiner do kit e o `container` em cada entrada);
  `tools/looks/scene.py` (`build`/`from_image`/`Builder` com o kit, a chave da
  `Surface` com o contêiner, e o `--check-image` exigindo as duas figuras
  vestidas com o caso sem kit ao lado); `tools/looks/confront.py`
  (`--kit-control`, e `render` com kit e peça); `tools/looks/ui/app.py`
  (`--kit`); `tools/looks/ui_check.py` (`judge_whole` exigindo
  `textured == primitives`, o controle plantado do kit, e o `plant` julgando
  também os números do `--smoke`); `docs/PLAN-LOOKS-PY.md` (§6 (f) e §10.3 (n)
  fechadas, e a §8 item 5 com a forma medida no japonês);
  `docs/prompts/perfil-looks.md` (armadilhas 77 a 79, duas linhas de gate e a
  do `looks_ui` atualizada); `CLAUDE.md` (duas linhas de comando, o item do
  uniforme reescrito e o estado do ciclo).
- **Problemas encontrados:**
  1. **Somar os sete retângulos não decide nada.** A tela sobe três; os outros
     quatro diferem em milhares para todos os 105, e o total dava 12.138
     contra 13.274 — 1,09x. Quem nomeia o kit é o retângulo **exato**.
  2. **Cada contêiner guarda o conjunto duas vezes**, nas mesmas coordenadas,
     e o console sobe um. No `TEX_A4` os dois são byte a byte iguais, então
     qual deles a tela subiu não se distingue aqui.
  3. **A página (576, 256) tem um bloco de 48 linhas que a tela sobrescreve**
     — 480 halfwords de 8.192, os mesmos pixels nos dois states, e em nenhum
     contêiner. Registrado; não é o uniforme.
  4. **O confronto de cor não testa o uniforme.** Ele desenha `--piece head`
     por decisão medida: com o kit ligado, os três desenhos deram a **mesma**
     pontuação até o terceiro decimal. O controle do kit passou a desenhar a
     figura inteira (armadilha 78).
  5. **Dois contêineres têm registros no mesmo offset**, e a chave da textura
     não os separava: o viewer morreu com `KeyError` numa chave legítima. O
     contêiner entrou na chave.
  6. **O controle plantado do kit ficou verde na primeira corrida**: o
     `plant()` do `looks_ui` só rodava os julgamentos de imagem, e um corpo
     cinza desenha todas elas perfeitamente. O `plant()` passou a julgar
     também os números do `--smoke`.
  7. **O `--check-discs` já vinha vermelho antes desta task**: o `ANIME.BIN` é
     idêntico nos dois discos e a expectativa do comando só abria exceção para
     a geometria. Corrigido junto, porque os 105 kits entram na mesma lista.

**Gates, na árvore commitada:** `selftest` 0 falhas, 90 de 90 controles
vermelhos; `cli check` 10 de 10; `iso_source --check-discs` ok, com 105 de 105
kits aceitos nos dois discos; `oracle.py --kit` 0 problemas nos dois slots;
`confront.py --kit-control` 0 problemas (0,218, 0,218, 0,148 e 0,063 de
margem); `confront.py --render` + `--score` 3 vitórias e 2 ranqueadas por
slot, 0 inexplicadas; `looks_ui` 10 de 10 controles vermelhos; `check_tasks`
138 ok.
