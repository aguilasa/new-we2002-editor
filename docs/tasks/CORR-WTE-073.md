---
id: CORR-WTE-073
title: "Correção: check_lcl_combo.py ficou preso no :99 depois da mudança para o :98"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-073: `check_lcl_combo.py` ficou preso no `:99` depois da mudança para o `:98`

## Problema identificado

A quarta passagem da [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) moveu todo
o projeto do `:99` para o `:98` (commit `601943f`), e o Log dela registra a
forma da mudança:

> O número passou a morar numa variável por ferramenta (`XVFB` nos dois
> `Makefile`, **`WTE_DISPLAY` nos scripts de `wte/tools/`**, `GOLDEN_DISPLAY`
> nos de `tools/`)

O [`wte/tools/check_lcl_combo.py`](../../wte/tools/check_lcl_combo.py) é um
script de `wte/tools/` que dirige GUI — compila um programa LCL e o roda para
medir o que a LCL dispara por atribuição — e **não recebeu a variável**. Ele
continua procurando o `:99` em código vivo, não em prosa:

```python
linha = next((l for l in saida.splitlines() if "Xvfb :99 " in l), None)
if linha is None:
    return None
...
return ":99", (m.group(1) if m else "")
...
if tela is None:
    raise FileNotFoundError("Xvfb :99")
```

Consequência dupla, e as duas contrariam o `CLAUDE.md`:

1. **numa máquina só com o `:98` de pé — que é a configuração que o repositório
   agora manda — o gate PULA em silêncio**, com a mensagem certa para o motivo
   errado. `make -C wte check` sai verde sem ter medido o comportamento da LCL;
2. **quando o `:99` existe, ele dirige GUI lá** — o servidor de onde o projeto
   saiu justamente porque outro projeto desta máquina ocupa aquele display.

Este é o único resto de `:99` em **código executável** da árvore. Os outros 12
lugares são prosa e registro histórico, que o `CLAUDE.md` manda preservar.

## Evidência

Com nenhum servidor de pé, o `make -C wte check` desta revisão:

```text
>> check_lcl_combo.py --check
check_lcl_combo: PULADO (sem Xvfb :99) -- o disparo de `OnChange` da LCL nao foi
medido nesta rodada
```

Depois, com o `:98` subido conforme o `CLAUDE.md` — e com um `Xvfb :99` alheio
também de pé na máquina — o script mediu, e mediu **no `:99`**:

```text
check_lcl_combo: 8 casos, LCL 3.0/gtk2: `TComboBox` e `TUpDown` nao disparam por
atribuicao; `TScrollBar.Position :=` DISPARA
```

Todo o resto da árvore já está do outro lado:

```bash
grep -rn 'WTE_DISPLAY\|GOLDEN_DISPLAY' wte/tools/ tools/
# wte/tools/roteiro.sh:79:  export DISPLAY="${WTE_DISPLAY:-:98}"
# wte/tools/compara_tela.sh:42:export DISPLAY="${WTE_DISPLAY:-:98}"
# tools/golden_run.sh:23:export DISPLAY="${GOLDEN_DISPLAY:-:98}"
# tools/golden_check.sh:24:export DISPLAY="${GOLDEN_DISPLAY:-:98}"
# tools/golden_gui.sh:22:export DISPLAY="${GOLDEN_DISPLAY:-:98}"
```

## Causa raiz

A varredura de `601943f` pegou os `.sh` e os `Makefile`, e passou ao largo do
único script Python que também resolve `DISPLAY` sozinho.

## Correção

### Arquivo: `wte/tools/check_lcl_combo.py`

O número passa a vir de `WTE_DISPLAY`, com `:98` de default — a mesma forma do
`roteiro.sh` e do `compara_tela.sh`:

```python
ALVO = os.environ.get("WTE_DISPLAY", ":98")

def display() -> tuple[str, str] | None:
    """`(DISPLAY, XAUTHORITY)` do Xvfb `ALVO`, ou `None` se ele nao esta de pe.
    ...
    """
    ...
    linha = next((l for l in saida.splitlines()
                  if f"Xvfb {ALVO} " in l), None)
    if linha is None:
        return None
    m = re.search(r"-auth (\S+)", linha)
    return ALVO, (m.group(1) if m else "")
...
    if tela is None:
        raise FileNotFoundError(f"Xvfb {ALVO}")
```

O docstring das linhas 113-124 acompanha: as quatro menções a `:99` viram
`ALVO`/`:98`. **Só as menções que descrevem o comportamento corrente** — se
alguma frase ali for registro de medição passada, ela fica como está, pela
regra do `CLAUDE.md`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_lcl_combo.py` | modificar |

## Verificação

- [ ] Com `Xvfb :98` de pé, `python3 wte/tools/check_lcl_combo.py --check`
      mede (imprime "8 casos") em vez de pular
- [ ] `WTE_DISPLAY=:97 python3 wte/tools/check_lcl_combo.py --check` pula
      dizendo `:97` — a variável é lida
- [ ] `grep -n ':99' wte/tools/check_lcl_combo.py` só devolve prosa histórica,
      se sobrar alguma
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
