# Save states do ciclo `kit2d`

Os save states que o ciclo [`kit2d`](/docs/tasks/kit2d/progresso.md) precisa,
em que slot gravar cada um e o que cada um destrava. A razão de existirem está
no [§4.4 do plano](/docs/PLAN-KIT2D-PY.md#4.4). Levantado em 2026-10-19.

## Os slots, hoje

Os dez slots do WE2002 (`SLPM-87056`) em `~/.local/share/duckstation/savestates/`
estão ocupados, e **todos batem byte a byte com uma cópia mestra** —
conferido com `cmp` em 2026-10-19:

| slots | cópia mestra | ciclo |
|---|---|---|
| 1, 2 | `work/looks-states/` | `looks` |
| 3 a 10 | `work/kits-states/` | `kits`, `kits-3d`, `kits-replay` |

Então qualquer slot pode ser sobrescrito sem perder nada: o slot do
DuckStation é rascunho, e quem precisa de um state antigo o restaura da mestra.

## State 1 — slot 1 (obrigatório)

- **Tela:** opções de uma partida **amistosa**, a que antecede o jogo.
- **Times:** duas seleções (índice < 63) cujos pares o `kits` já mediu como
  diferentes: **Escócia × Dinamarca** (KITS-TASK-27,
  [§4.1 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#4.1)).
- **Uniformes:** nesta tela, quem escolhe titular ou suplente é a linha
  **`KITS`** (`TYPE 1`, …) e nada mais. O state fica em `TYPE 1`, com os dois
  lados de `HOME SHIRT`; as tasks que precisam do suplente andam a linha `KITS`
  pelo MCP (`press_button`) a partir do state, e a rota (quantos `Down` até a
  linha, quantos `Right` até cada combinação) é medida e registrada na
  K2D-TASK-04.
- **Disco:** o mesmo dos states do `kits` e do `looks` — o `.cue` inglês
  apontado por `WE2002_LOOKS_DRIVE_IMAGE`.
- **Depois de gravar**, copie para a pasta do ciclo, com o nome que o plano e
  as tasks esperam:

  ```sh
  mkdir -p work/kit2d-states
  cp ~/.local/share/duckstation/savestates/SLPM-87056_1.sav work/kit2d-states/
  ```

- **Destrava:** K2D-TASK-03, 04 e 05 (fase 0) e K2D-TASK-12 (fase 2).

### Gravado em 2026-10-21

`work/kit2d-states/SLPM-87056_1.sav`, igual ao slot, mídia
`work/we2002-english.cue`: tela de opções, Escócia × Dinamarca, `KITS TYPE 1`,
os dois de `HOME SHIRT` (captura embutida, lida por `savestate.py shot`). Na
RAM (`savestate.py ram`) estão os 760 bytes da tabela de modelos e as paletas
dos 95 times, iguais aos do disco japonês.

## State 2 — slot 2 (só para a K2D-TASK-34; pode esperar)

- **Tela:** seleção de clube da Master League, com um clube de índice ≥ 63 na
  tela — de preferência um cujo titular e suplente diferem.
- **Depois de gravar:** `work/kit2d-states/SLPM-87056_2.sav`. Esse nome ainda
  não está no plano; a K2D-TASK-34 o registra no [§4.6](/docs/PLAN-KIT2D-PY.md#4.6).
- **Destrava:** K2D-TASK-34 (fase 8).

### Gravado em 2026-10-21

`work/kit2d-states/SLPM-87056_2.sav`, igual ao slot, mesma mídia: seleção de
clube com o **Man Utd**, titular e suplente lado a lado (`HOME`/`AWAY`). Tabela
de modelos e paletas presentes na RAM, como no state 1. Por mostrar os dois
uniformes do mesmo time, serve também de segundo caso na K2D-TASK-04.

## A K2D-TASK-30 talvez precise de um terceiro — não grave agora

Um state guarda a RAM. No state 1 o `SELECT2.BIN` já foi lido do disco
original, então uma edição gravada numa cópia só aparece se o jogo reler o
overlay **depois** do load. Saídas possíveis: um state uma tela antes das
opções, ou uma rota de botões a partir do boot da cópia. Em que tela o overlay
é carregado não está medido; quem decide é a própria K2D-TASK-30 (fase 7).

## Destravar as tasks

O `--unblocked-by` do Rite só vale para correção, então a condição de cada task
bloqueada está no motivo do bloqueio. Com o state no lugar:

```sh
test -f work/kit2d-states/SLPM-87056_1.sav && for n in 03 04 05 12; do
  rite mark K2D-TASK-$n pending --cycle kit2d
done
```

K2D-TASK-30 e K2D-TASK-34 continuam bloqueadas até chegar a vez delas.
