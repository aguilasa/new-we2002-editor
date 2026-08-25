# `re/retorno.md` — o que o `Return` alcança, e a ordem de tabulação

Gerado por [`../tools/check_retorno.py`](../tools/check_retorno.py) a partir dos 18 `.dfm`, dos 18 `.lfm`, de [`published_methods.tsv`](published_methods.tsv) e das specs de [`spec/`](spec). **Não editar à mão:**

```sh
python3 wte/tools/check_retorno.py
python3 wte/tools/check_retorno.py --check
```

A tabela está em [`retorno.tsv`](retorno.tsv); este arquivo é a leitura dela. **Todo número daqui saiu do script.**

## Resumo

| Medida | Valor |
|---|---:|
| Formulários | 18 |
| Com botão `Default` | 13 |
| Cujo `Default` grava na imagem | 1 |
| Ordem de tabulação divergente entre DFM e LFM | 0 |

## Por formulário

| Formulário | `Default` | handler | `ModalResult` | bytes | `Cancel` | controles com `TabOrder` | ordem igual |
|---|---|---|---|---|---|---:|---|
| `MainForm` | — | — | — | sem handler | — | 56 | sim |
| `estrategia` | — | — | — | sem handler | — | 6 | sim |
| `ficha_about` | `BitBtn3` | — | 1 | sem handler | — | 1 | sim |
| `ficha_color` | `BitBtn3` | `BitBtn3Click` | 1 | imagem | `BitBtn2` | 25 | sim |
| `ficha_creditos_equipo` | `BitBtn1` | — | 6 | sem handler | `BitBtn2` | 2 | sim |
| `ficha_dorsal` | `BitBtn1` | `BitBtn1Click` | 1 | nenhum | — | 2 | sim |
| `ficha_enlaza` | `BitBtn1` | — | 6 | sem handler | `BitBtn2` | 2 | sim |
| `ficha_error` | `BitBtn3` | — | 1 | sem handler | — | 1 | sim |
| `ficha_error2` | `BitBtn3` | — | 1 | sem handler | — | 1 | sim |
| `ficha_info` | `BitBtn3` | — | 1 | sem handler | — | 1 | sim |
| `ficha_info2` | `BitBtn3` | — | 1 | sem handler | — | 1 | sim |
| `ficha_info3` | — | — | — | sem handler | — | 1 | sim |
| `ficha_info4` | — | — | — | sem handler | — | 1 | sim |
| `ficha_movertodos` | `BitBtn1` | — | 6 | sem handler | `BitBtn2` | 2 | sim |
| `ficha_salida` | `BitBtn1` | — | 6 | sem handler | `BitBtn2` | 2 | sim |
| `ficha_warning` | `BitBtn1` | — | 6 | sem handler | `BitBtn2` | 2 | sim |
| `ficha_warning_2` | `BitBtn1` | — | 6 | sem handler | `BitBtn2` | 2 | sim |
| `jugador` | — | — | — | sem handler | — | 34 | sim |

## A evidência de cada `bytes`

A primeira linha da seção `## Bytes tocados` da spec do handler — é dela que a classificação sai.

- **`ficha_color.BitBtn3Click`** (`imagem`): Sete regiões por time, todas endereçadas por global de offset em vez de
- **`ficha_dorsal.BitBtn1Click`** (`nenhum`): **Nenhum.** Não há chamada de escrita no corpo — a única chamada é o

