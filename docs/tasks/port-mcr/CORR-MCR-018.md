---
id: CORR-MCR-018
title: "Correção: quem arrasta é quem corrige a prova — a conversão de volta do arraste é julgada pela própria aritmética que ela usa"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-MCR-018: a armadilha 7, no sentido que só existe desde esta task, não tem juiz

## Problema identificado

O critério desta task diz, em letras:

> **`X*7` e `Y*2` moram só no `ui/formation_view.py`.** Arrastar um jogador no
> campo tem de converter de volta (**dividir**) **na UI**, e o que chega ao
> modelo são as unidades do cartão. A armadilha 7 do perfil é exatamente isto.

O sentido de ida — os fatores vazando para dentro do núcleo — **tem** guarda: o
controle `formation-screen-factor` planta `X*7` no `formation.write` e fica
vermelho. O sentido de volta, que só passou a existir com o arraste desta task,
**não tem nenhuma**.

O `app.py --write-probe` arrasta e depois relata:

```python
    room = formation_view.X_MAX / 2
    _drag(app, window.formation.pitch, 0,
          PROBE_DRAG if formation.x[0] < room else -PROBE_DRAG, PROBE_DRAG)
    report["xy_before"] = list(before)
    report["xy_after"] = [formation.x[0], formation.y[0]]
```

`xy_after` é lido **do modelo depois do arraste** — isto é, é o resultado da
conversão. E o `ui_check.py` julga assim:

```python
                    ("x", [f.x[0], f.y[0]], r["xy_after"]),
                    ...
            if r["xy_after"] == r["xy_before"]:
                bad.append("the drag moved no player")
```

Compara o modelo relido do disco contra **o mesmo número que a conversão
produziu**. Os dois lados vêm da mesma aritmética, então concordam sempre. A
única asserção que sobra é "mexeu alguma coisa".

`PROBE_DRAG` — o deslocamento em **pixels de campo**, que é o único dado de
entrada da conversão — não entra no relatório. O juiz não tem como calcular o
que deveria ter saído.

Isto contraria a lição 3 do próprio Log desta task — *"Quem mede não é quem
julga"* —, que foi aplicada à **localidade dos bytes** e não à conversão de
coordenada, onde a tela continua sendo as duas coisas.

## Evidência

Cópia da árvore em sandbox dentro do repositório, com o venv e o `wte/`
alcançáveis, `WE2002_MCR_CARD` apontado, `DISPLAY=:98` e `XAUTHORITY` vazio.
Baseline verde. Uma substituição, que é o defeito que o critério nomeia — a
divisão que deixa de acontecer:

```python
 def to_card_x(pitch_px: float) -> int:
     """Pitch pixels back to the card's X. The inverse of `x * X_SCALE`."""
-    return max(0, min(X_MAX, round(pitch_px / X_SCALE)))
+    return max(0, min(X_MAX, round(pitch_px)))
```

A substituição casou 1×. Resultado:

```
probe: one attribute moved 1 byte(s) at ['0x590d'], inside slot 0's record at 0x05904
probe: the drag moved outfield slot 1 from [11, 32] to [48, 43], in the card's own units
probe: both written cards round-trip, and probe-edited.mcr is a copy, not the card opened
rc=0

$ selftest --fast   ->  rc=0
```

O gate sai **verde**, e a linha que ele imprime declara `[48, 43]` "in the
card's own units" com a mesma confiança com que declara `[14, 43]` quando está
certo. O round-trip não pode pegar: 48 é um byte de X perfeitamente legal.

E não há segunda rede — a conversão não é exercitada por mais nada:

```
$ grep -rn "to_card_x\|to_card_y" tools/mcr/ | grep -v ui/formation_view.py
(vazio)

$ grep -rn "def self_check" tools/mcr/ui/          -> (nenhum)
$ grep -n "^MODULES" -A2 tools/mcr/selftest.py     -> os 12 do núcleo, sem ui/
$ grep -n "formation_view" tools/mcr/controls.py   -> (nenhum)
```

## Causa raiz

O valor esperado do arraste é produzido pelo código sob teste e entregue ao
juiz como se fosse independente.

## Correção

O juiz precisa de um número que a conversão **não** produziu. Duas formas, e a
segunda é a melhor:

### Arquivo: `tools/mcr/ui/app.py` — o mínimo

Relatar o estímulo, não só o efeito:

```python
    dx = PROBE_DRAG if formation.x[0] < room else -PROBE_DRAG
    _drag(app, window.formation.pitch, 0, dx, PROBE_DRAG)
    report["drag_pixels"] = [dx, PROBE_DRAG]
    report["scales"] = [formation_view.X_SCALE, formation_view.Y_SCALE]
```

### Arquivo: `tools/mcr/ui_check.py` — quem julga

Com o estímulo em mãos, a relação é do juiz:

```python
        dx, dy = r["drag_pixels"]
        sx, sy = r["scales"]
        want = [r["xy_before"][0] + round(dx / sx),
                r["xy_before"][1] + round(dy / sy)]
        if r["xy_after"] != want:
            bad.append(f"the drag landed at {r['xy_after']}, and "
                       f"{dx},{dy} pitch pixels over {sx},{sy} is {want}")
```

**A forma melhor**, se couber: o probe arrastar para um **alvo em unidades de
cartão** escolhido pelo gate (`--write-probe DIR --drag-to 14,43`), e o juiz
exigir exatamente esse par. Aí a tela não fornece nem o esperado nem a regra —
só executa.

### E o controle que fecha

Registrar em `controls.py` a substituição da Evidência (`ui/formation_view.py`
:: `to_card_x`), com `expect_red` sobre o gate. Se o motor de controles não
alcançar o `ui_check.py` — ele planta e roda `--self-check` de módulo —, então
o caso vermelho tem de ficar no **`ui_check.py`**, como um passo que quebra a
conversão numa cópia e exige o vermelho, do mesmo jeito que o `mcrio.negative`
faz com as cinco injeções da §5.2.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/ui/app.py` | modificar |
| `tools/mcr/ui_check.py` | modificar |
| `tools/mcr/controls.py` | modificar (o controle da conversão) |
| `docs/tasks/port-mcr/12-ui-gravacao.md` | modificar (a contagem de controles no Log) |

## Verificação

- [ ] com a substituição da Evidência aplicada numa cópia da árvore,
      `python3 tools/mcr/ui_check.py` sai **`rc=1`**, dizendo onde o arraste
      deveria ter caído
- [ ] sem ela, `rc=0`, e a linha do arraste continua `[11, 32] -> [14, 43]`
- [ ] o mesmo para `to_card_y`, com `Y_SCALE`
- [ ] `python3 tools/mcr/controls.py` continua **todos vermelhos**, com o total
      novo declarado no Log da task
- [ ] `ctest -R mcr` = **3 de 3** com `WE2002_MCR_CARD`, e `make test` verde
- [ ] os dois cartões gravados continuam passando nas duas formas do round-trip
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
