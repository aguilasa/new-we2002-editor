# Retro — kits-3d

Date: 2026-10-12

## Numbers

De `rite stats kits-3d --json`:

- **Tasks:** 19, todas `done` (0 blocked, 0 skipped).
- **Fixes:** 35, todas `done` (0 stale). Por severidade: 0 critical, 3 high, 20 medium e 12 low.
- **Fixes por task:** 1,84. Mediana até a revisão: 0 dias; máximo: 1 dia, sobre 19 tasks revisadas.
- **Fixes por fase:**

  | Fase | Tasks | Fixes |
  |---|---|---|
  | 1 | 3 | 1 |
  | 2 | 3 | 3 |
  | 3 | 3 | 5 |
  | 4 | 3 | 4 |
  | 5 | 3 | 6 |
  | 6 | 1 | 3 |
  | 7 | 3 | 13 |

- **Origens com mais fixes:** K3D-TASK-18 e K3D-TASK-19 (4 cada); K3D-TASK-07, 14, 16 e 17 (3 cada).
  A CORR-K3D-026 originou duas (030, 031).

A fase 7 (replays, G8) concentra 13 das 35 fixes em 3 tasks, e as três high
(020, 026, 030) estão nas fases 6 e 7 — as investigações no emulador.

## Root-cause groups

Total: 8 de escrituração (A + B) e 27 de engenharia (C a I), somando 35.

- **A — Edição fora do `files` declarado: 5, escrituração.** Quase sempre nota de passagem
  escrita no arquivo da task seguinte. IDs: 002, 006, 018, 025, 028. A 009 também tinha um
  `files` velho, contada em C. É a mesma armadilha K1 do ciclo `kits` (14 fixes), que já
  estava no arquivo de armadilhas e repetiu assim mesmo.
- **B — Linha `$` ou passo do Log que não é o que rodou: 3, escrituração.** Saída aparada (004),
  recorte e montagem sem comando (010), `--frame-json` omitido da linha `$` (033).
- **C — Número sem ferramenta versionada na HEAD: 5, engenharia.** Sonda descartável (005, 035),
  faixa escrita de um subconjunto das corridas (009), número derivado à mão da tabela (029),
  prosa de memória contrariando a saída colada ao lado (032).
- **D — Verificador que não mede o que afirma: 10, engenharia.** Três formas:
  - valor esperado tirado da própria captura, ou tabela comparada com ela mesma (012, 020 — high);
  - vermelho da planta vindo de outro ramo ou de efeito colateral, não da asserção (007, 013, 016, 024);
  - asserção ausente ou só impressa (008, 011, 023, 030 — high).
- **E — Veredito mudou e a varredura não chegou a quem dizia o anterior: 6, engenharia.**
  IDs: 001, 003, 017, 019, 021, 027.
- **F — Afirmação sem corrida na HEAD que a sustente: 3, engenharia.** Título "no lugar da 15" sem
  figura que o mostre (015), negativa do Cross vinda de corrida avulsa anterior à reordenação
  (022), coluna `still` afirmada e nunca calculada (026 — high).
- **G — Um caso tomado como regra: 1, engenharia.** Conclusão do Bokšić generalizada às três
  capturas (034).
- **H — Ambiente: controle físico vazando ao emulador: 1, engenharia.** O `[Pad1]` é `SDL-0`, e um
  controle ligado mandou botões ao fork no `:98`; quatro corridas deram quatro tabelas (031).
- **I — Rótulo de contagem errado: 1, engenharia.** "whole figure(s)" contando as cortadas (014).

## Proposals

### Keep in next profile

Entradas para `docs/prompts/perfil-kits-3d.armadilhas.md`, no formato do arquivo:

- **K1 — Juiz não tira o esperado do medido (012, 020).** O valor que o plano afirma vira constante
  por (slot, linha) no oráculo; cabeça, número e contagem lidos da própria captura só provam
  consistência interna.
- **K2 — A planta tem de derrubar a asserção que diz cobrir (007, 013, 016, 024).** O juiz imprime
  qual asserção falhou, e o Log mostra essa linha; vermelho por outro ramo, por reenquadramento da
  vista ou por "não há segunda figura" não conta.
- **K3 — Linha `$` é a que rodou, com toda flag (004, 010, 033).** Inclusive `--frame-json`; passo de
  recorte ou montagem sem comando versionado não entra no Log.
- **K4 — Controle físico desligado antes de dirigir o fork (031).** O `[Pad1]` da máquina é `SDL-0`,
  e o SDL entrega o controle a qualquer display; corridas divergentes sem toque são o sintoma.
- **K5 — Reordenou botão ou constante, refaz a corrida e a prosa (021, 022).** Docstring e negativa
  escritas antes da reordenação descrevem um comando que a HEAD não roda.
- **Atualizar** a entrada existente "Edição fora do `files` declarado" com `proven by` 002, 006,
  018, 025, 028 deste ciclo.

### Promote to rite.toml / CLAUDE.md

- **P1 — Quinta regra em "Convenções da documentação" do `CLAUDE.md`: nota de passagem não vai no
  arquivo da task seguinte.** Causou 14 fixes no `kits` e 5 aqui (002, 006, 018, 025, 028), mesmo com
  a armadilha K1 do `kits` copiada para este ciclo. A armadilha não bastou; a regra sobe.
- Os grupos C, D e E (21 fixes) já são regras do `CLAUDE.md`. Seguem sendo a maior parte; não há
  lugar mais alto para elas no repositório — ver R1 para a parte que a ferramenta poderia pegar.

### Rite issues (plugin)

- **R1 — `rite close` registra "Outside declared files" e fecha assim mesmo.**
  - Medido: `rite_lib/ops.py:373-381` acrescenta a lista ao Log e devolve `outside_files`, sem recusar.
  - Casos: 5 fixes aqui (002, 006, 018, 025, 028) e 14 no ciclo `kits`, todas abertas pelo revisor
    lendo exatamente essa linha que o fechamento já tinha escrito.
  - Pedido: opção de configuração (por exemplo `[scope] outside_files = "refuse"`) para o `close`
    sair 1 nomeando os arquivos, até que um `rite set <ID> --files …` os declare.

### Prune

- **Nada a podar.** O perfil tem 8.274 bytes e as armadilhas 2.060 (`wc -c`), sob `max_kb = 84`.
  Todas as verificações por fase foram usadas pelas revisões, e as cinco armadilhas herdadas
  continuam valendo (a de `files` repetiu).

## Applied

Escolha do usuário (2026-10-12):

- **Keep K1 a K5:** gravadas em `docs/prompts/perfil-kits-3d.armadilhas.md`, e a entrada de `files`
  ganhou as cinco fixes deste ciclo no `proven by`.
- **Promote P1:** quinta regra em "Convenções da documentação" do `CLAUDE.md`.
- **Issue R1:** não aberta; fica rascunhada aqui.
- **Prune:** nada.
