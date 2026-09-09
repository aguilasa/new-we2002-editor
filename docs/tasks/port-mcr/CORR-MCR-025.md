---
id: CORR-MCR-025
title: "Correção: o julgamento do filtro dos diálogos não tem caso vermelho plantado, e o motor que o plantaria está no mesmo arquivo"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-MCR-025: guarda nova sem controle negativo, conferida à mão uma vez

## Problema identificado

A MCR-TASK-16 acrescentou uma asserção ao `_judge_open` do `ui_check.py`: os
três formatos têm de aparecer na string que os dois diálogos passam
(`tools/mcr/ui_check.py:540-548`). É a única coisa que impede a janela de
voltar a oferecer só `.mcr` enquanto o núcleo lê e grava três embalagens.

**Nenhum controle plantado a exercita.** O Log da task diz como ela foi
conferida:

> a asserção foi conferida à mão, plantando um filtro só de `.mcr` numa cópia
> da árvore: `FAIL: the file dialogs do not offer .mcd, .gme`

Conferência à mão não fica no repositório e não roda de novo. É exatamente o
que o perfil deste ciclo proíbe em letras — "**controle negativo se roda, não
se descreve**" — e a MCR-TASK-15, que abriu esta mesma tela, fixou a regra para
a Fase 5: "há controle plantado que prova que trocar a ligação fica vermelho".

**E o motor está no mesmo arquivo, a uma tupla de distância.** O `ui_check.py`
já planta seis defeitos que o `controls.py` não alcança, porque precisam do
venv e do `:98`: `BREAKS` (2, a conversão do arraste), `OUTSIDE_BREAKS` (2, o
valor fora do onze) e `OPEN_BREAKS` (2, as duas portas de abrir cartão). A
guarda nova é do `--open-probe`, julgada pelo mesmo `_judge_open` que o
`OPEN_BREAKS` exercita, e cabe ali.

O risco não é teórico: o `CARD_FILTER` é uma **string de rótulo** em
`ui/main_window.py`, fora do alcance de qualquer teste do núcleo, e a Regra 3
garante que nada em `ui/` importa `gme.py` — quem tem de casar as duas pontas é
esta asserção, e ela é a única.

## Evidência

Os seis plantados hoje, e nenhum é o filtro:

```
$ grep -n "^BREAKS\|^OUTSIDE_BREAKS\|^OPEN_BREAKS" tools/mcr/ui_check.py
122:BREAKS = (
134:OUTSIDE_BREAKS = (
486:OPEN_BREAKS = (

$ sed -n '486,493p' tools/mcr/ui_check.py
OPEN_BREAKS = (
    ("the button's wiring",
     "        self.open_button.clicked.connect(self.act_open.trigger)",
     "        self.open_button.clicked.connect(lambda: None)"),
    ("the dirty guard",
     "        if self._dirty and not self._confirm_discard():",
     "        if False:"),
)
```

A guarda que ficou sem par:

```
$ sed -n '540,548p' tools/mcr/ui_check.py
    missing = [e for e in (".mcr", ".mcd", ".gme")
               if e not in r.get("card_filter", "")]
    if missing:
        bad.append(f"the file dialogs do not offer {', '.join(missing)}: "
                   f"{r.get('card_filter')!r}")
```

E o alvo do plantio, uma linha literal como as outras seis pedem:

```
$ grep -n "^CARD_FILTER" tools/mcr/ui/main_window.py
66:CARD_FILTER = ("Memory cards (*.mcr *.mcd *.gme);;"
```

O `mcr_ui` passa hoje (`4/4` com fixture e `:98`), então **não há vermelho
faltando**: falta a prova de que ele saberia ficar vermelho.

## Causa raiz

A asserção nasceu no julgador e o caso vermelho nasceu num script descartável,
que não entrou no repositório — o mesmo padrão que as
[CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md) e
[CORR-MCR-011](/docs/tasks/port-mcr/CORR-MCR-011.md) mediram para a prosa.

## Correção

### Arquivo: `tools/mcr/ui_check.py`

Uma tupla a mais em `OPEN_BREAKS`, na forma literal que as outras seis usam —
arquivo, o que a linha é, o que ela vira. A substituição tem de casar **uma**
vez; a linha do `CARD_FILTER` é a primeira de um literal de quatro linhas, e o
que importa é que o resultado ofereça só `.mcr`:

```python
    ("the dialog filter",
     'CARD_FILTER = ("Memory cards (*.mcr *.mcd *.gme);;"',
     'CARD_FILTER = ("Memory cards (*.mcr);;"'),
```

O plantio já é feito por `_plant_open`, e o julgamento já é o `_judge_open`, que
tem a asserção — logo o vermelho esperado é a linha que o Log da task obteve à
mão: `the file dialogs do not offer .mcd, .gme`.

**Confira que a substituição casou.** Literal que não bate deixa a cópia
intacta e a corrida sai verde, que é o defeito registrado no perfil e o que
mordeu os dois controles novos desta mesma task.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/ui_check.py` | modificar |
| `docs/prompts/perfil-mcr.md` | modificar (a linha do `mcr_ui` diz "os seis controles negativos") |

## Verificação

- [ ] `WE2002_MCR_CARD=$PWD/work/entrada.mcr DISPLAY=:98 python3
      tools/mcr/ui_check.py` verde, e a corrida relata o controle novo **em
      vermelho**, nomeando-o
- [ ] o plantio casa **uma** vez — cópia intacta é controle quebrado, não
      vermelho
- [ ] `ctest -R mcr` = 4/4 com fixture e `:98`
- [ ] `python3 tools/mcr/selftest.py` e `python3 tools/mcr/controls.py`
      inalterados (`22 of 22 red`) — este controle não é do motor deles
- [ ] a linha do `mcr_ui` no perfil diz quantos são, ou aponta para a saída
- [ ] `mcr/` e `roms/` intocadas; `sha256sum work/entrada.mcr` =
      `e53f4895…c47546`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
