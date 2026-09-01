---
id: PES2-TASK-03
title: "Direção do DuckStation — navegar até a tela e capturar"
type: ferramenta
category: verificação
phase: 2
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §3.4"
status: pendente
---

# PES2-TASK-03: Direção do emulador

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §3.4 e §6.11, e a regra do `:98` do
  [CLAUDE.md](../../CLAUDE.md).
- **Sem oráculo, o jogo é o oráculo** (§4.1). Um campo só está mapeado quando
  um `poke` nele muda o que a tela mostra. Isso exige chegar à tela.

`tools/pes2/run_duckstation.sh` já sobe o jogo isolado no `:98`, com binding
de teclado, renderer de software e limpeza de instância. `boot_check.sh` já
mede que ele botou. O que não existe é **navegação**: sair do laço de
atração, entrar no menu, chegar à tela de seleção de time, e capturar.

---

## Objetivo

`tools/pes2/drive.sh` (ou `drive.py`), que recebe um **roteiro nomeado** e
entrega um PNG por tela pedida.

```
tools/pes2/drive.sh <copia/track1.bin> --screen team-select --out /tmp/a.png
tools/pes2/drive.sh <copia/track1.bin> --screen replay,result --out-dir /tmp/
```

### Os roteiros que a Fase 2 precisa

Um por tela onde um nome de time aparece — que é o conjunto de cópias da
§1.5, visto do outro lado:

| Roteiro | Onde o nome aparece | Cópia que o alimenta |
|---|---|---|
| `team-select` | seleção de time | `SELECT.BIN` @3128 |
| `result` | tela de resultado | `RESULT.BIN` @524 |
| `replay` | replay | `REPLAYS.BIN` @11380 |
| `ending` | fim de campeonato | `ENDING.BIN` @1256 |
| `edit` | modo de edição | `SELECTC.BIN` @16576 |

Nem todas serão alcançáveis em minutos de navegação — `ending` pode exigir
*save state*. **Declarar o que não deu, e como se pretende chegar lá**, é
resultado legítimo; fingir que uma tela foi vista não é.

### As armadilhas já pagas, e que este script herda

As nove da §6.11, todas dentro do `run_duckstation.sh` — reusar o script,
não reescrever a subida. Mais as do `CLAUDE.md` sobre dirigir janela sem
window manager:

- `xdotool windowactivate` **falha** no `:98` (`XGetInputFocus returned the
  focused window of 1`). Dirigir por coordenada absoluta.
- **O foco de teclado segue o ponteiro** (`PointerRoot`). `xdotool
  mousemove --window <janela>` antes de qualquer `key`.
- **Teclar uma vez e esperar o efeito**, nunca em laço.
- Capturar com `import -window <id>`; se falhar com `Resource temporarily
  unavailable`, a janela está obscurecida ou fora da tela — **não** é o
  emulador travado (§6.11, armadilha 5).

### Save state como atalho

O DuckStation tem *save state* (§3.4). Um estado salvo na tela certa
transforma "navegar por três minutos de menu" em "carregar e capturar", e
torna o roteiro repetível. **O estado não entra no git** — é derivado de
jogo comercial, mesma regra de `roms/` e dos quadros do `boot_check.sh`.
O que entra é o script que o cria e o caminho de onde ele mora.

---

## Critério de conclusão

- [ ] Pelo menos **três** das cinco telas alcançadas e capturadas, com o PNG
      mostrando um nome de time legível.
- [ ] O roteiro é repetível: duas corridas seguidas produzem a mesma tela
      (dentro da tolerância do `PES2_TOLERANCE`, pela mesma razão do
      `boot_check.sh` — emulação não é exata quadro a quadro).
- [ ] As telas não alcançadas estão listadas, com o motivo e a via proposta.
- [ ] Encerra sempre pelo `run_duckstation.sh --kill`, sem deixar montagem
      FUSE nem janela órfã no `:98`.
- [ ] Roda no `DISPLAY=:98`. Sem exceção (§6.10).

---

## Log de Execução

*(a preencher)*
