---
id: CORR-PES2-024
title: "Correção: o `--measure-menu` é gate, não confere se está no menu, e nenhum comando versionado o coloca lá"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-PES2-024: o caso vermelho depende de um estado que nada versionado produz, e não confere a tela

## Problema identificado

O `--measure-menu` é o **caso vermelho** desta fase. O perfil o promove a gate:

> | rota de emulador | `mcp_drive.py --self-check` verde, e `--measure-menu`
> contra o jogo vivo: ele mede as sete linhas do menu e depois pede sete, o
> que **tem de falhar**. Verde que nunca pôde ser vermelho é decoração |

Ele funciona — esta revisão o viu ficar vermelho. Mas ele tem dois furos, e
os dois são de precondição.

**1. Nada versionado leva o emulador ao estado em que ele roda.** O
`--help` diz *"against a running game already on the main menu"*, e não há
comando que produza isso:

- toda rota do `mcp_drive.py` **encerra o emulador ao sair**
  (`McpSession.__exit__` chama `fork.kill`), então
  `--screen main-menu` não deixa o jogo de pé;
- `fork.py launch` deixa o emulador de pé, mas na abertura, não no menu;
- `pad.py` manda um toque por vez, à mão — não é rito repetível.

O único caminho que funciona hoje passa por um save state **não versionado**
que sobrou da execução da task, em
`~/.local/share/duckstation/savestates/SLES-03957_1.sav`. Numa máquina sem
ele, ou com ele parado noutra tela, o gate não tem como ser exercitado — e
nada no plano, no perfil ou no `--help` diz isso.

**2. `measure_menu` não confere que está no menu principal.** Ele chama
`menu_rows()` direto. Compare com o `from_main_menu`, que faz a verificação
certa antes de confiar num estado carregado:

```python
frame = s.capture()
if abs(frame.stats()[0] - MAIN_MENU_MEAN) <= MAIN_MENU_TOL:
    s.say("the state was on the main menu")
```

Sem essa cerca, `--measure-menu` rodado na tela errada mede o que der e
imprime `the main menu has N rows (measured, not declared)` — uma afirmação
sobre o menu principal feita sobre outra tela. É a armadilha 33 da §6.11
("**'Não preto' não é 'chegou'**") na ferramenta que nasceu para consertá-la.

## Evidência

Que a rota mata o emulador que subiu:

```
$ grep -n "kill" tools/pes2/mcp_drive.py
209:            fork.kill(verbose=False)      # dentro de __exit__

$ python3 tools/pes2/mcp_drive.py "<copia.cue>" --screen main-menu --out-dir <dir>
MCP DRIVE OK: <dir>  51.9s, 8 presses, 160 frames stepped
$ python3 tools/pes2/mcp_drive.py --measure-menu
skipping: no MCP server at http://127.0.0.1:2346/mcp -- the DuckStation fork
is not running. [URLError]
```

Que só o save state deixado para trás salva o gate:

```
$ python3 tools/pes2/fork.py launch "<copia.cue>"
$ python3 tools/pes2/mcp.py --call load_state slot=1
{ "status": "loaded", "slot": 1 }
$ python3 tools/pes2/mcp_drive.py --measure-menu
  the list wraps: row 7 is row 0 again -> 7 rows
the main menu has 7 rows (measured, not declared)
RED CASE OK: asking for 7 rows failed -- press 7 of 7 landed back on row 0
```

Que `measure_menu` não verifica a tela:

```python
def measure_menu(s):
    rows = s.menu_rows()                    # nenhuma checagem de MAIN_MENU_MEAN
    print(f"the main menu has {rows} rows (measured, not declared)")
```

## Causa raiz

O caso vermelho foi escrito para ser rodado **à mão, na sessão em que a
navegação acabara de acontecer** — e por isso a precondição ficou implícita
nos dedos de quem estava ali, em vez de no código.

## Correção

### Arquivo: `tools/pes2/mcp_drive.py`

Duas mudanças, e a primeira é a que importa:

1. **`measure_menu` verifica a tela antes de medir.** Reusar o limiar que já
   existe, e falhar alto quando não bater:

```python
def measure_menu(s):
    frame = s.capture()
    mean = frame.stats()[0]
    if abs(mean - MAIN_MENU_MEAN) > MAIN_MENU_TOL:
        raise Fail(f"not on the main menu: mean={mean:.6f}, expected "
                   f"{MAIN_MENU_MEAN} +-{MAIN_MENU_TOL} -- park it there "
                   f"with --screen main-menu --save-state, then --keep-alive")
    rows = s.menu_rows()
    ...
```

2. **Um caminho versionado até o estado.** A forma mais barata é uma opção
   que impeça o `__exit__` de matar o que a rota subiu — `--keep-alive`, que
   só põe `s._own = False` —, e então o rito fica em dois comandos:

```sh
python3 tools/pes2/mcp_drive.py "<copia.cue>" --screen main-menu --keep-alive
python3 tools/pes2/mcp_drive.py --measure-menu
```

Alternativa igualmente aceitável, se `--keep-alive` parecer ganho pequeno:
`--measure-menu` aceitar uma imagem e, quando receber uma, dirigir ele mesmo
por `from_main_menu` antes de medir. O critério é que **o gate seja
alcançável por comando versionado**, não que a opção se chame assim.

### Arquivo: `docs/prompts/perfil-pes2.md` e `docs/PLAN-PES2-PSX.md` §6.14

Escrever o rito de duas linhas na tabela de gates e na seção, onde hoje o
comando aparece sozinho como se bastasse.

### Arquivo: `tools/pes2/mcp_drive.py` (`self_check`)

Um caso a mais, sem emulador: que a média da tela errada é recusada pela
cerca nova — o mesmo formato dos que já comparam `SAME_ROW` com as leituras
medidas.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/mcp_drive.py` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |
| `docs/PLAN-PES2-PSX.md` | modificar |

## Verificação

- [ ] `python3 tools/pes2/mcp_drive.py --self-check` verde, com o caso novo
- [ ] `ctest --test-dir build -R pes2_selftest` verde
- [ ] o rito de duas linhas leva do disco ao `RED CASE OK`, numa máquina
      **sem** save state prévio (mova o `.sav` para fora e repita)
- [ ] `--measure-menu` rodado na tela de título **falha** dizendo que não
      está no menu, em vez de imprimir uma contagem
- [ ] `roms/` intocada; nenhum quadro do jogo versionado

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
