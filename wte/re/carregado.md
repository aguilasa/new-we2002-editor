# `re/carregado.md` — os formulários com a lógica ligada

Gerado por [`../tools/check_carregado.py`](../tools/check_carregado.py) a partir dos 18 `.dfm`, dos 18 `.lfm`, de `wte/src/` e das capturas de [`visual/carregado/`](visual/carregado). **Não editar à mão:**

```sh
bash wte/tools/captura_ui.sh ui-01-telas ui-02-transferencia ui-03-avisos
python3 wte/tools/check_carregado.py
python3 wte/tools/check_carregado.py --check
```

A tabela está em [`carregado.tsv`](carregado.tsv); este arquivo é a leitura dela. **Todo número daqui saiu do script.**

## Resumo

| Medida | Valor |
|---|---:|
| Formulários | 18 |
| Sem nenhum `Show`/`ShowModal` em `wte/src/` | 2 |
| Fotografados dos **dois** lados | 15 |
| Fotografados só do oráculo | 1 |
| Sem foto nenhuma | 2 |
| Com a mesma cor de fundo dos dois lados | 15 de 15 |
| Rótulos que declaram `Color` | 178 |
| Deles, com cor diferente entre os dois lados | 68 |

## Por formulário

| Formulário | quem abre no port | foto oráculo | foto port | fundo oráculo | fundo port | `TStaticText` | no fundo (orác./port) | rótulos com `Color` | divergentes |
|---|---|---|---|---|---|---:|---|---:|---:|
| `MainForm` | (principal) | 522x475 | 522x475 | #76B6FF | #76B6FF | 34 | 5/4 | 27 | 0 |
| `estrategia` | ep2002_mainform.mostrar_estrategiaClick.inc | 529x498 | 529x498 | #418FE6 | #418FE6 | 0 | 0/0 | 43 | 18 |
| `ficha_about` | ep2002_mainform.SpeedButton1Click.inc | 319x274 | 319x274 | #39DADB | #39DADB | 0 | 0/0 | 0 | 0 |
| `ficha_color` | ep2002_mainform.colorearClick.inc | 542x225 | 542x225 | #418FE6 | #418FE6 | 3 | 3/3 | 34 | 18 |
| `ficha_creditos_equipo` | ep2002_mainform.base_teamClick.inc | 285x124 | 285x124 | #DCDC3C | #DCDC3C | 0 | 0/0 | 0 | 0 |
| `ficha_dorsal` | ep2002_mainform.dorsalClick.inc | 135x153 | 129x121 | #418FE6 | #418FE6 | 0 | 0/0 | 1 | 1 |
| `ficha_enlaza` | — | — | — | — | — | 0 | —/— | 0 | — |
| `ficha_error` | ep2002_mainform.aux.inc | 335x121 | 329x89 | #000080 | #000080 | 0 | 0/0 | 0 | 0 |
| `ficha_error2` | ep2002_estrategia.BitBtn3Click.inc,ep2002_jugador.BitBtn3Click.inc,ep2002_mainform.boton_nombres2isoClick.inc,ep2002_mainform.grabar_camisetaClick.inc,ep2002_mainform.grabar_memoryClick.inc,ep2002_mainform.pabajoClick.inc | 382x122 | 376x90 | #000080 | #000080 | 0 | 0/0 | 0 | 0 |
| `ficha_info` | ep2002_color.SpeedButton1Click.inc | 264x196 | 258x164 | #3CDCDC | #3CDCDC | 0 | 0/0 | 5 | 0 |
| `ficha_info2` | ep2002_error.SpeedButton1Click.inc | 414x189 | 408x157 | #3CDCDC | #3CDCDC | 0 | 0/0 | 5 | 0 |
| `ficha_info3` | ep2002_mainform.base_teamClick.inc,ep2002_mainform.boton_barras2isoClick.inc,ep2002_mainform.boton_nombres2isoClick.inc,ep2002_mainform.boton_tex2isoClick.inc,ep2002_mainform.grabar_camisetaClick.inc,ep2002_mainform.grabar_memoryClick.inc | 282x113 | 276x81 | #3CDCDC | #3CDCDC | 0 | 0/0 | 1 | 0 |
| `ficha_info4` | wte_ficha.pas | — | — | — | — | 0 | —/— | 3 | — |
| `ficha_movertodos` | ep2002_mainform.aux.inc | 239x124 | 239x124 | #DCDC3C | #DCDC3C | 0 | 0/0 | 0 | 0 |
| `ficha_salida` | ep2002_mainform.SpeedButton2Click.inc | 231x122 | 225x90 | #DCDC3C | #DCDC3C | 0 | 0/0 | 0 | 0 |
| `ficha_warning` | — | 339x169 | — | #DC3C3C | — | 0 | 0/— | 0 | — |
| `ficha_warning_2` | ep2002_estrategia.BitBtn3Click.inc | 340x172 | 340x172 | #DC3C3C | #DC3C3C | 0 | 0/0 | 0 | 0 |
| `jugador` | ep2002_mainform.mostrar_jugadorClick.inc | 707x273 | 707x273 | #418FE6 | #418FE6 | 0 | 0/0 | 59 | 31 |

## Como ler a coluna `no fundo`

Quantos `TStaticText` do formulário têm, no retângulo deles, a **mesma cor dominante** do formulário inteiro. É a releitura do achado 4 da [WTE-TASK-12](../../docs/tasks/12-comparacao-visual.md) com o fundo de execução por baixo: os que declaram `Color` próprio ficam **fora** dessa conta nos dois lados — é o que se espera, e é o que faz a medida valer alguma coisa —, e os que herdam a cor do pai entram nela nos dois. Contagem diferente entre os lados é o sintoma que a §8.9 do plano mandava procurar.

## E a coluna `divergentes`

Quantos rótulos que declaram `Color` no DFM têm **cor de fundo diferente entre os dois lados**. É a §8.9 generalizada: ela manda conferir os 37 `TStaticText`, e são **151 `TLabel`** que declaram `Color` pelo mesmo DFM. Nenhum dos dois grupos declara `Transparent`, então quem decide se a cor aparece é o *default* do widgetset — e os dois defaults não são o mesmo.

