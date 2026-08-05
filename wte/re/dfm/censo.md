# Censo de componentes dos 18 formularios

Gerado por `wte/tools/dfm_extract.py` a partir de `we-team-editor/we-team-editor.exe`.
**Nao editar a mao** -- correcao entra no script e o diretorio e regerado.

A contagem e de **componentes**: o objeto raiz de cada formulario (a
classe `T<nome>`) fica de fora, porque ele e o formulario, nao um componente
dentro dele.

## Blobs binarios

As propriedades `vaBinary` (`Icon.Data`, `Picture.Data`, `Glyph.Data`) **nao**
estao inline nos `.dfm`. Cada uma virou `blobs/<formulario>/<dono>.<prop>.bin`,
referenciada no `.dfm` por
`{blob <arquivo> <tamanho> sha256:<hash>}`.

A razao esta na secao 2 do plano: os 118 blobs somam 798 KiB de arte do
Obocaman, da mesma natureza dos 198 `.bmp` de `we-team-editor/` -- pasta que o
repositorio ignora justamente por ser binario de terceiro sem licenca. Hex e so
uma codificacao; colar os bytes no `.dfm` reintroduziria no versionamento o que
o `.gitignore` mantem fora dele. O SHA-256 no `.dfm` e o que preserva a
verificacao byte a byte sem versionar os bytes: `--check` confere os 798 KiB
contra o hash.

`blobs/` e ignorado pelo git e renasce do `.exe`, como `wte/assets` -- mas so no
**modo de escrita**. O `--check` nao materializa nada: num clone limpo os 118
`.bin` faltam, e isso sai como aviso, nao como divergencia. Blob presente e
diferente do `.exe`, ou blob sobrando, continuam falha.

## Por formulario

Na ordem em que os recursos aparecem em `.rsrc` -- que o linker mantem
ordenada pelo nome do recurso (`TESTRATEGIA`, `TFICHA_*`, `TJUGADOR`,
`TMAINFORM`), e nao pelo nome do objeto. Determinismo sem reordenar nada.

| Formulario | Classe raiz | Componentes | Classes | Blobs |
|---|---|---:|---:|---:|
| `estrategia` | `Testrategia` | 89 | 7 | 8 |
| `ficha_about` | `Tficha_about` | 6 | 5 | 5 |
| `ficha_color` | `Tficha_color` | 65 | 11 | 12 |
| `ficha_creditos_equipo` | `Tficha_creditos_equipo` | 3 | 2 | 3 |
| `ficha_dorsal` | `Tficha_dorsal` | 4 | 4 | 2 |
| `ficha_enlaza` | `Tficha_enlaza` | 6 | 2 | 3 |
| `ficha_error` | `Tficha_error` | 3 | 3 | 3 |
| `ficha_error2` | `Tficha_error2` | 2 | 2 | 2 |
| `ficha_info` | `Tficha_info` | 6 | 2 | 2 |
| `ficha_info2` | `Tficha_info2` | 6 | 2 | 2 |
| `ficha_info3` | `Tficha_info3` | 2 | 2 | 2 |
| `ficha_info4` | `Tficha_info4` | 4 | 2 | 2 |
| `ficha_movertodos` | `Tficha_movertodos` | 3 | 2 | 3 |
| `ficha_salida` | `Tficha_salida` | 3 | 2 | 3 |
| `ficha_warning` | `Tficha_warning` | 5 | 2 | 3 |
| `ficha_warning_2` | `Tficha_warning_2` | 5 | 2 | 3 |
| `jugador` | `Tjugador` | 113 | 6 | 24 |
| `MainForm` | `TMainForm` | 116 | 15 | 36 |

### `estrategia`

| Classe | Qtd |
|---|---:|
| `TLabel` | 54 |
| `TShape` | 23 |
| `TImage` | 5 |
| `TBitBtn` | 3 |
| `TComboBox` | 2 |
| `TListBox` | 1 |
| `TTimer` | 1 |

### `ficha_about`

| Classe | Qtd |
|---|---:|
| `TImage` | 2 |
| `TActionList` | 1 |
| `TBitBtn` | 1 |
| `TBrowseURL` | 1 |
| `TSpeedButton` | 1 |

### `ficha_color`

| Classe | Qtd |
|---|---:|
| `TLabel` | 34 |
| `TBitBtn` | 6 |
| `TComboBox` | 4 |
| `TImage` | 4 |
| `TRadioButton` | 4 |
| `TGroupBox` | 3 |
| `TScrollBar` | 3 |
| `TStaticText` | 3 |
| `TTrackBar` | 2 |
| `TBevel` | 1 |
| `TSpeedButton` | 1 |

### `ficha_creditos_equipo`

| Classe | Qtd |
|---|---:|
| `TBitBtn` | 2 |
| `TLabel` | 1 |

### `ficha_dorsal`

| Classe | Qtd |
|---|---:|
| `TBevel` | 1 |
| `TBitBtn` | 1 |
| `TLabel` | 1 |
| `TScrollBar` | 1 |

### `ficha_enlaza`

| Classe | Qtd |
|---|---:|
| `TLabel` | 4 |
| `TBitBtn` | 2 |

### `ficha_error`

| Classe | Qtd |
|---|---:|
| `TBitBtn` | 1 |
| `TLabel` | 1 |
| `TSpeedButton` | 1 |

### `ficha_error2`

| Classe | Qtd |
|---|---:|
| `TBitBtn` | 1 |
| `TLabel` | 1 |

### `ficha_info`

| Classe | Qtd |
|---|---:|
| `TLabel` | 5 |
| `TBitBtn` | 1 |

### `ficha_info2`

| Classe | Qtd |
|---|---:|
| `TLabel` | 5 |
| `TBitBtn` | 1 |

### `ficha_info3`

| Classe | Qtd |
|---|---:|
| `TBitBtn` | 1 |
| `TLabel` | 1 |

### `ficha_info4`

| Classe | Qtd |
|---|---:|
| `TLabel` | 3 |
| `TBitBtn` | 1 |

### `ficha_movertodos`

| Classe | Qtd |
|---|---:|
| `TBitBtn` | 2 |
| `TLabel` | 1 |

### `ficha_salida`

| Classe | Qtd |
|---|---:|
| `TBitBtn` | 2 |
| `TLabel` | 1 |

### `ficha_warning`

| Classe | Qtd |
|---|---:|
| `TLabel` | 3 |
| `TBitBtn` | 2 |

### `ficha_warning_2`

| Classe | Qtd |
|---|---:|
| `TLabel` | 3 |
| `TBitBtn` | 2 |

### `jugador`

| Classe | Qtd |
|---|---:|
| `TLabel` | 59 |
| `TImage` | 20 |
| `TScrollBar` | 16 |
| `TUpDown` | 12 |
| `TBitBtn` | 3 |
| `TEdit` | 3 |

### `MainForm`

| Classe | Qtd |
|---|---:|
| `TStaticText` | 34 |
| `TSpeedButton` | 25 |
| `TImage` | 14 |
| `TShape` | 9 |
| `TGroupBox` | 7 |
| `TComboBox` | 5 |
| `TLabel` | 5 |
| `TRadioButton` | 5 |
| `TEdit` | 3 |
| `TOpenDialog` | 3 |
| `TSaveDialog` | 2 |
| `TActionList` | 1 |
| `TBrowseURL` | 1 |
| `TListBox` | 1 |
| `TTrackBar` | 1 |

## Total

| Classe | Qtd |
|---|---:|
| `TLabel` | 182 |
| `TImage` | 45 |
| `TStaticText` | 37 |
| `TBitBtn` | 32 |
| `TShape` | 32 |
| `TSpeedButton` | 28 |
| `TScrollBar` | 20 |
| `TUpDown` | 12 |
| `TComboBox` | 11 |
| `TGroupBox` | 10 |
| `TRadioButton` | 9 |
| `TEdit` | 6 |
| `TOpenDialog` | 3 |
| `TTrackBar` | 3 |
| `TActionList` | 2 |
| `TBevel` | 2 |
| `TBrowseURL` | 2 |
| `TListBox` | 2 |
| `TSaveDialog` | 2 |
| `TTimer` | 1 |
| **total** | **441** |

20 classes distintas, 441 componentes em 18 formularios.
