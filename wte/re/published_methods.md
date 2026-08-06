# `re/published_methods.md` — os 96 handlers, com dono

Produto da [WTE-TASK-04](../../docs/tasks/04-mapa-de-handlers.md). Gerado por
[`../tools/dump_published.py`](../tools/dump_published.py), a partir de
`we-team-editor/we-team-editor.exe` e dos 18 formulários de
[`dfm/`](dfm/).
**Não editar à mão** — correção entra no script e o arquivo é regerado:

```sh
python3 wte/tools/dump_published.py
python3 wte/tools/dump_published.py --check   # o que `make -C wte check` roda
```

Os dados em forma de tabela estão em [`published_methods.tsv`](published_methods.tsv); este arquivo é a
leitura deles. **Todo número daqui saiu do script**, inclusive os do texto corrido — é
por isso que o `--check` compara o markdown inteiro byte a byte, e não só o TSV.

## O que foi medido, e com que régua

São **96 métodos publicados** em **17 dos 18 formulários** — o mesmo número que a §1.4 do plano
registra. Eles saem da *published method table* que o VCL guarda no VMT de cada
classe: a tabela que o streaming de DFM usa para resolver `OnClick = boton_mcrClick`
em ponteiro de código, e que sobreviveu ao `/STRIP`.

### Achar os VMTs

O VMT que o Delphi/C++Builder emite é um array de métodos virtuais precedido de um
cabeçalho de campos em deslocamento **negativo**, fixo desde o Delphi 4:

| Deslocamento | Campo | Uso aqui |
|---:|---|---|
| -76 | `vmtSelfPtr` | aponta para o próprio VMT — é a assinatura da varredura |
| -52 | `vmtMethodTable` | a published method table (0 quando não há nenhuma) |
| -44 | `vmtClassName` | short string com o nome da classe — a coluna `formulario` |
| -40 | `vmtInstanceSize` | validação |
| -36 | `vmtParent` | — |

Procurar o auto-ponteiro — dword cujo valor é o endereço dele mesmo mais
76 — localiza os VMTs sem depender de símbolo nenhum. Em `.data` inteira a
assinatura casa 19 vezes; 1 é rejeitada por ter `vmtClassName` nulo e
`vmtInstanceSize` zero. Sobram os **18** formulários — um por arquivo de
[`dfm/`](dfm/), sem sobra dos dois lados. Essa bijeção é o fechamento que substitui
confiar na varredura, e o script aborta se ela deixar de valer.

A tabela em si é `word contagem` seguida de `contagem` entradas de
`word tamanho`, `dword endereço`, `byte tamanho do nome`, nome. O campo `tamanho`
cobre a entrada inteira; o script confere `tamanho == 7 + len(nome)` nas 96,
que o endereço cai dentro de `.text`, e que o nome é identificador — e aborta na
primeira que discordar.

### Os 18 VMTs

| Formulário | Classe | VMT | `vmtInstanceSize` | tabela | métodos |
|---|---|---|---:|---|---:|
| `MainForm` | `TMainForm` | `0x00427dd4` | 1216 | `0x0042869f` | 37 |
| `ficha_creditos_equipo` | `Tficha_creditos_equipo` | `0x00428aac` | 768 | `0x00428bca` | 1 |
| `estrategia` | `Testrategia` | `0x00428c4c` | 1112 | `0x00429253` | 14 |
| `ficha_warning_2` | `Tficha_warning_2` | `0x004293f4` | 776 | `0x0042952a` | 1 |
| `jugador` | `Tjugador` | `0x004295a4` | 1208 | `0x00429db3` | 11 |
| `ficha_color` | `Tficha_color` | `0x00429f20` | 1016 | `0x0042a3df` | 17 |
| `ficha_info4` | `Tficha_info4` | `0x0042a5c4` | 768 | `0x0042a6ec` | 1 |
| `ficha_error2` | `Tficha_error2` | `0x0042a764` | 760 | — *(nenhuma)* | 0 |
| `ficha_info` | `Tficha_info` | `0x0042a8d8` | 776 | `0x0042aa1c` | 1 |
| `ficha_salida` | `Tficha_salida` | `0x0042aa94` | 768 | `0x0042abb2` | 1 |
| `ficha_movertodos` | `Tficha_movertodos` | `0x0042ac2c` | 768 | `0x0042ad4a` | 1 |
| `ficha_about` | `Tficha_about` | `0x0042adc8` | 776 | `0x0042af1f` | 2 |
| `ficha_info3` | `Tficha_info3` | `0x0042afb8` | 760 | `0x0042b0c8` | 1 |
| `ficha_warning` | `Tficha_warning` | `0x0042b140` | 776 | `0x0042b276` | 1 |
| `ficha_enlaza` | `Tficha_enlaza` | `0x0042b2f0` | 776 | `0x0042b432` | 2 |
| `ficha_dorsal` | `Tficha_dorsal` | `0x0042b4b8` | 768 | `0x0042b5ef` | 3 |
| `ficha_error` | `Tficha_error` | `0x004321a0` | 768 | `0x004322c3` | 1 |
| `ficha_info2` | `Tficha_info2` | `0x00432344` | 776 | `0x00432489` | 1 |

A classe é `T` + o nome do objeto raiz do `.dfm` nos 18 casos, e o script
aborta se algum dia não for: é essa regra que deixa a coluna `formulario` do TSV
usar o nome do objeto (`MainForm`, `ficha_color`) em vez do nome da classe. O nome do
objeto é o que nomeia o `.dfm`, a variável global do programa original e a futura
unidade Pascal — é a chave útil.

## VMT × DFM

As duas fontes do dono, cruzadas em vez de escolhidas:

| Fonte | O que dá | Cobertura |
|---|---|---|
| VMT | `endereco`, `handler`, `formulario` | os 96, inclusive o que nenhum DFM cita |
| DFM | `componente`, `evento`; confere `formulario` | 219 ligações `On<Evento> = <handler>` |

As 219 ligações dos 18 `.dfm` se reduzem a **95 pares (formulário, handler)
distintos**, e os 95 estão entre os 96 do VMT. **Zero discordâncias de dono:**
nenhum DFM referencia um handler publicado por outra classe — o que era esperado,
porque o streaming do próprio original não acharia o método, e é por isso que o
script trata esse caso como abortar e não como anotar.

A relação é de muitos para um: um handler serve vários componentes. Os campeões:

| Handler | Formulário | Componentes ligados | Evento |
|---|---|---:|---|
| `dorsalClick` | `MainForm` | 23 | `OnClick` |
| `dorsalMouseDown` | `MainForm` | 23 | `OnMouseDown` |
| `colorMouseDown` | `ficha_color` | 16 | `OnMouseDown` |
| `flechasapaClick` | `jugador` | 12 | `OnClick` |
| `bolaMouseMove` | `estrategia` | 10 | `OnMouseMove` |
| `bolaMouseDown` | `estrategia` | 10 | `OnMouseDown` |
| `bolaEndDrag` | `estrategia` | 10 | `OnEndDrag` |
| `barrhabScroll` | `jugador` | 9 | `OnScroll` |

No TSV as colunas `componente` e `evento` são listas separadas por `|`, do mesmo
comprimento e alinhadas por posição: o *n*-ésimo componente é ligado pelo *n*-ésimo
evento. A ordem é a de aparecimento no `.dfm`.

### O handler publicado que nenhum DFM referencia

| Endereço | Handler | Formulário |
|---|---|---|
| `0x0040c9c4` | `Button2Click` | `MainForm` |

Publicado no VMT, ligado a nenhum componente. As duas leituras possíveis são
código morto (o botão foi apagado do formulário e o método ficou) e ligação em
tempo de execução (`Componente->OnClick = ...` em `FormCreate`). **Este script não as
separava** — quem separa é o disassembly do `FormCreate` de `MainForm`
(`0x004107c8`), na fase 4. Fica marcado na coluna `nota` como
`sem referencia em DFM`.

### Homônimos — por que a coluna `formulario` existe

6 nomes aparecem em mais de um formulário, cobrindo 30 dos 96 métodos. Sem o dono,
"implementar `FormCreate`" não quer dizer nada:

| Handler | Vezes | Formulários |
|---|---:|---|
| `FormCreate` | 16 | `MainForm`, `estrategia`, `ficha_about`, `ficha_color`, `ficha_creditos_equipo`, `ficha_dorsal`, `ficha_enlaza`, `ficha_info`, `ficha_info2`, `ficha_info3`, `ficha_info4`, `ficha_movertodos`, `ficha_salida`, `ficha_warning`, `ficha_warning_2`, `jugador` |
| `BitBtn1Click` | 4 | `estrategia`, `ficha_color`, `ficha_dorsal`, `jugador` |
| `BitBtn3Click` | 3 | `estrategia`, `ficha_color`, `jugador` |
| `SpeedButton1Click` | 3 | `MainForm`, `ficha_color`, `ficha_error` |
| `BitBtn2Click` | 2 | `ficha_color`, `jugador` |
| `FormShow` | 2 | `MainForm`, `ficha_enlaza` |

## A coluna `grupo`

`grupo` é o que reparte os 96 entre as quatro tasks da fase 4. O enunciado da
WTE-TASK-04 a chama de "classificação manual", mas saída de gerador tem de ser
reproduzível: aqui ela sai de **oito regras ordenadas** mais uma **tabela de
exceções**, ambas no topo do script. A coluna `regra` do TSV diz qual decidiu cada
linha (`EX` = exceção), então discordar de uma classificação é editar uma linha
identificável, não reabrir um julgamento.

| Grupo | Task | Quantos |
|---|---|---:|
| carga | [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md) | 28 |
| edição | [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md) | 44 |
| gravação | [WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md) | 6 |
| auxiliar | [WTE-TASK-28](../../docs/tasks/28-handlers-auxiliares.md) | 18 |
| **total** | | **96** |

### As oito regras, na ordem em que são tentadas

A primeira que casa decide; a tabela de exceções vem antes de todas.

| Regra | Grupo | Critério | Handlers |
|---|---|---|---:|
| `EX` | — | tabela de exceções | 9 |
| `R1` | gravação | nome começa com `grabar_` ou contém `2iso` — os seis pontos em que o app escreve | 6 |
| `R2` | carga | `FormCreate` / `FormShow` — inicialização de formulário | 18 |
| `R3` | carga | nome começa com `boton_dialogo_` — abre arquivo por diálogo | 2 |
| `R4` | carga | nome começa com `lista_` — seleção numa lista que popula a tela | 4 |
| `R5` | carga | nome começa com `mostrar_` — abre uma tela já populada | 2 |
| `R6` | auxiliar | o formulário está entre as unidades de diálogo exportadas | 2 |
| `R7` | auxiliar | nome de componente gerado pela IDE (`BitBtn1Click`, `SpeedButton2Click`, ...) — moldura de diálogo | 14 |
| `R8` | edição | nenhuma das anteriores: altera estado em memória | 39 |

Duas das regras não são adivinhação de nome, e sim medida do binário:

- **R6** usa as **13 unidades exportadas**. O C++Builder exporta
  `@@T<unidade>@Initialize` para cada unidade com inicialização a emitir; as telas
  grandes não têm e por isso não aparecem. É o mesmo corte da §1.3 do plano, e é
  exatamente o que a WTE-TASK-28 chama de "os 13 diálogos": `ficha_about`, `ficha_creditos_equipo`, `ficha_dorsal`, `ficha_enlaza`, `ficha_error2`, `ficha_info`, `ficha_info2`, `ficha_info3`, `ficha_info4`, `ficha_movertodos`, `ficha_salida`, `ficha_warning`, `ficha_warning_2`.
- **R7** usa o nome que a IDE gera sozinha (`BitBtn1Click`, `SpeedButton2Click`,
  `Image3Click`). Componente que o autor nunca renomeou é botão de moldura —
  abrir, fechar, OK/Cancelar —, e é assim que a WTE-TASK-28 já os enumera.

### As 9 exceções

| Formulário | Handler | Grupo | Por quê |
|---|---|---|---|
| `MainForm` | `base_teamClick` | auxiliar | a WTE-TASK-28 o lista entre os auxiliares; o nome não é genérico o bastante para a R7 alcançá-lo. |
| `MainForm` | `boton_mcrClick` | carga | abre o `.mcr` do memory card: lê, não grava. O par que grava é `boton_mcr2isoClick`, e o prefixo `boton_` sozinho não separa os dois. |
| `estrategia` | `ComboBoxDrawItem` | carga | owner-draw do combo de formações — só pinta. A WTE-TASK-25 o reivindica junto com a lista que ele desenha, e é ela que ordena o trabalho. |
| `ficha_color` | `botonClick` | auxiliar | a WTE-TASK-28 o lista entre os auxiliares, ao lado dos BitBtn do mesmo formulário. |
| `ficha_color` | `lista_col0Change` | edição | lista de cor da paleta do editor 2D, não carga de dado do jogo — o prefixo `lista_` da R4 aponta para o lado errado aqui. |
| `ficha_color` | `lista_col1change` | edição | idem `lista_col0Change`. O `c` minúsculo de `change` está no binário e é transcrito verbatim. |
| `ficha_color` | `lista_col2Change` | edição | idem `lista_col0Change`. |
| `ficha_color` | `lista_col3Change` | edição | idem `lista_col0Change`. |
| `ficha_dorsal` | `scroll_dorsalChange` | edição | `ficha_dorsal` está entre os 13 diálogos exportados, mas este handler edita o número da camisa em vez de ser moldura: a WTE-TASK-26 o lista nominalmente. |

### Conferência contra a §1.4 do plano

A §1.4 já interpretou dez handlers a olho. Todos os dez caem onde a leitura dela
manda, o que é a âncora de sanidade das regras:

| Handler | Leitura da §1.4 | Formulário medido | `grupo` | `regra` |
|---|---|---|---|---|
| `boton_mcrClick` | abre o `.mcr` | `MainForm` | carga | `EX` |
| `boton_mcr2isoClick` | grava o jogador do `.mcr` na imagem | `MainForm` | gravação | `R1` |
| `grabar_camisetaClick` | grava a camisa editada | `MainForm` | gravação | `R1` |
| `grabar_memoryClick` | grava para memory card | `MainForm` | gravação | `R1` |
| `etiqprecioClick` | calcula preço do jogador | `jugador` | edição | `R8` |
| `colorearClick` | pinta camisa/bandeira | `MainForm` | edição | `R8` |
| `lista_equiposChange` | carrega time selecionado | `MainForm` | carga | `R4` |
| `lista_formacionesClick` | aplica formação | `estrategia` | carga | `R4` |
| `ComboBoxDrawItem` | owner-draw do combo | `estrategia` | carga | `EX` |
| `malla2MouseDown` | grade do editor de camisa | `estrategia` | edição | `R8` |

Duas ressalvas de leitura, não de medida:

- `lista_formacionesClick` é **carga** porque a WTE-TASK-25 o reivindica, mas a
  própria tarefa avisa que ele "aplica formação sobre o time selecionado — é ação
  destrutiva disparada por clique". Se a fase 4 preferir movê-lo para edição, o
  lugar de mudar é a tabela de exceções.
- `etiqprecioClick` é **edição** por eliminação: ele calcula e mostra o preço, não
  carrega nem grava, e não há um quinto grupo. A coluna `nota` o marca como
  `WTE-TASK-30`.

### Os 16 handlers que a WTE-TASK-28 devolve às tasks 30 e 32

A WTE-TASK-28 exclui do próprio escopo os handlers de `ficha_color` e de `jugador`
que são **fórmula**, não diálogo. Eles continuam com `grupo` entre os quatro — não
existe um quinto —, e a coluna `nota` diz quem os implementa, para que a fase 4 não
faça o trabalho duas vezes:

| Endereço | Handler | Formulário | `grupo` | `nota` |
|---|---|---|---|---|
| `0x00405e40` | `barraChange` | `ficha_color` | edição | WTE-TASK-32 |
| `0x00406358` | `barra1Change` | `ficha_color` | edição | WTE-TASK-32 |
| `0x00406384` | `barra2Change` | `ficha_color` | edição | WTE-TASK-32 |
| `0x004063b0` | `gradienteClick` | `ficha_color` | edição | WTE-TASK-32 |
| `0x004065fc` | `oscurecerClick` | `ficha_color` | edição | WTE-TASK-32 |
| `0x00406744` | `aclararClick` | `ficha_color` | edição | WTE-TASK-32 |
| `0x0040688c` | `lista_col0Change` | `ficha_color` | edição | WTE-TASK-32 |
| `0x004068b0` | `lista_col1change` | `ficha_color` | edição | WTE-TASK-32 |
| `0x004068ec` | `lista_col2Change` | `ficha_color` | edição | WTE-TASK-32 |
| `0x0040690c` | `lista_col3Change` | `ficha_color` | edição | WTE-TASK-32 |
| `0x00406a0c` | `colorMouseDown` | `ficha_color` | edição | WTE-TASK-32 |
| `0x00408b9c` | `casilla_precioKeyPress` | `jugador` | edição | WTE-TASK-30 |
| `0x00408bb8` | `etiqprecioClick` | `jugador` | edição | WTE-TASK-30 |
| `0x00409f4c` | `malla1MouseDown` | `estrategia` | edição | WTE-TASK-32 |
| `0x0040a000` | `malla2MouseDown` | `estrategia` | edição | WTE-TASK-32 |
| `0x00410ea8` | `colorearClick` | `MainForm` | edição | WTE-TASK-32 |

## Os 96, por endereço

A ordem é a do TSV: endereço crescente, que é a ordem em que o linker dispôs o
código. A coluna *componentes* é a contagem de ligações de DFM; a lista completa
está no TSV.

| Endereço | Handler | Formulário | Evento | Componentes | Grupo |
|---|---|---|---|---:|---|
| `0x00402b40` | `BitBtn1Click` | `ficha_dorsal` | `OnClick` | 1 | auxiliar |
| `0x00402b58` | `scroll_dorsalChange` | `ficha_dorsal` | `OnChange` | 1 | edição |
| `0x00402bc0` | `FormCreate` | `ficha_dorsal` | `OnCreate` | 1 | carga |
| `0x00402c44` | `FormShow` | `ficha_enlaza` | `OnShow` | 1 | carga |
| `0x00402c54` | `FormCreate` | `ficha_enlaza` | `OnCreate` | 1 | carga |
| `0x00402cdc` | `FormCreate` | `ficha_warning` | `OnCreate` | 1 | carga |
| `0x00402d60` | `FormCreate` | `ficha_info3` | `OnCreate` | 1 | carga |
| `0x00402de4` | `FormCreate` | `ficha_about` | `OnCreate` | 1 | carga |
| `0x00402de8` | `imagen_urlClick` | `ficha_about` | `OnClick` | 1 | auxiliar |
| `0x00402e84` | `FormCreate` | `ficha_movertodos` | `OnCreate` | 1 | carga |
| `0x00402f08` | `FormCreate` | `ficha_salida` | `OnCreate` | 1 | carga |
| `0x00402f8c` | `FormCreate` | `ficha_info` | `OnCreate` | 1 | carga |
| `0x0040422c` | `FormCreate` | `ficha_info4` | `OnCreate` | 1 | carga |
| `0x00405dcc` | `FormCreate` | `ficha_color` | `OnCreate` | 1 | carga |
| `0x00405e40` | `barraChange` | `ficha_color` | `OnChange` | 3 | edição |
| `0x00406078` | `botonClick` | `ficha_color` | `OnClick` | 4 | auxiliar |
| `0x00406358` | `barra1Change` | `ficha_color` | `OnChange` | 1 | edição |
| `0x00406384` | `barra2Change` | `ficha_color` | `OnChange` | 1 | edição |
| `0x004063b0` | `gradienteClick` | `ficha_color` | `OnClick` | 1 | edição |
| `0x004065fc` | `oscurecerClick` | `ficha_color` | `OnClick` | 1 | edição |
| `0x00406744` | `aclararClick` | `ficha_color` | `OnClick` | 1 | edição |
| `0x0040688c` | `lista_col0Change` | `ficha_color` | `OnChange` | 1 | edição |
| `0x004068b0` | `lista_col1change` | `ficha_color` | `OnChange` | 1 | edição |
| `0x004068ec` | `lista_col2Change` | `ficha_color` | `OnChange` | 1 | edição |
| `0x0040690c` | `lista_col3Change` | `ficha_color` | `OnChange` | 1 | edição |
| `0x00406968` | `BitBtn1Click` | `ficha_color` | `OnClick` | 1 | auxiliar |
| `0x004069c8` | `BitBtn2Click` | `ficha_color` | `OnClick` | 1 | auxiliar |
| `0x004069e8` | `BitBtn3Click` | `ficha_color` | `OnClick` | 1 | auxiliar |
| `0x00406a0c` | `colorMouseDown` | `ficha_color` | `OnMouseDown` | 16 | edição |
| `0x00406f34` | `SpeedButton1Click` | `ficha_color` | `OnClick` | 1 | auxiliar |
| `0x00407a68` | `BitBtn2Click` | `jugador` | `OnClick` | 1 | auxiliar |
| `0x00407a80` | `BitBtn1Click` | `jugador` | `OnClick` | 1 | auxiliar |
| `0x00407a88` | `barrhabScroll` | `jugador` | `OnScroll` | 9 | edição |
| `0x00407bb4` | `barrhab_bisScroll` | `jugador` | `OnScroll` | 7 | edição |
| `0x00407ce0` | `FormCreate` | `jugador` | `OnCreate` | 1 | carga |
| `0x00408088` | `flechasapaClick` | `jugador` | `OnClick` | 12 | edição |
| `0x00408548` | `BitBtn3Click` | `jugador` | `OnClick` | 1 | auxiliar |
| `0x00408af8` | `casilla_nombreKeyPress` | `jugador` | `OnKeyPress` | 1 | edição |
| `0x00408b50` | `casilla_dorsalKeyPress` | `jugador` | `OnKeyPress` | 1 | edição |
| `0x00408b9c` | `casilla_precioKeyPress` | `jugador` | `OnKeyPress` | 1 | edição |
| `0x00408bb8` | `etiqprecioClick` | `jugador` | `OnClick` | 1 | edição |
| `0x00408d88` | `FormCreate` | `ficha_warning_2` | `OnCreate` | 1 | carga |
| `0x00408e0c` | `bolaMouseMove` | `estrategia` | `OnMouseMove` | 10 | edição |
| `0x00408f00` | `bolaMouseDown` | `estrategia` | `OnMouseDown` | 10 | edição |
| `0x004090c8` | `campoMouseMove` | `estrategia` | `OnMouseMove` | 1 | edição |
| `0x004090fc` | `FormCreate` | `estrategia` | `OnCreate` | 1 | carga |
| `0x00409644` | `rectanguloDragOver` | `estrategia` | `OnDragOver` | 1 | edição |
| `0x00409780` | `rectanguloDragDrop` | `estrategia` | `OnDragDrop` | 1 | edição |
| `0x004097a4` | `bolaEndDrag` | `estrategia` | `OnEndDrag` | 10 | edição |
| `0x00409aa0` | `lista_formacionesClick` | `estrategia` | `OnClick` | 1 | carga |
| `0x00409ba4` | `relojTimer` | `estrategia` | `OnTimer` | 1 | edição |
| `0x00409f4c` | `malla1MouseDown` | `estrategia` | `OnMouseDown` | 1 | edição |
| `0x0040a000` | `malla2MouseDown` | `estrategia` | `OnMouseDown` | 1 | edição |
| `0x0040a658` | `BitBtn1Click` | `estrategia` | `OnClick` | 1 | auxiliar |
| `0x0040a660` | `BitBtn3Click` | `estrategia` | `OnClick` | 1 | auxiliar |
| `0x0040adec` | `ComboBoxDrawItem` | `estrategia` | `OnDrawItem` | 2 | carga |
| `0x0040b034` | `FormCreate` | `ficha_creditos_equipo` | `OnCreate` | 1 | carga |
| `0x0040bd60` | `boton_dialogo_weClick` | `MainForm` | `OnClick` | 1 | carga |
| `0x0040c2c8` | `boton_mcrClick` | `MainForm` | `OnClick` | 1 | carga |
| `0x0040c46c` | `boton_mcr2isoClick` | `MainForm` | `OnClick` | 1 | gravação |
| `0x0040c9c4` | `Button2Click` | `MainForm` | — | 0 | auxiliar |
| `0x0040c9d0` | `sel_barraClick` | `MainForm` | `OnClick` | 5 | edição |
| `0x0040ca10` | `track_barraChange` | `MainForm` | `OnChange` | 1 | edição |
| `0x0040cab8` | `boton_barras2isoClick` | `MainForm` | `OnClick` | 1 | gravação |
| `0x0040cd6c` | `lista_equiposChange` | `MainForm` | `OnChange` | 1 | carga |
| `0x0040d36c` | `edit_nombre1KeyPress` | `MainForm` | `OnKeyPress` | 1 | edição |
| `0x0040d3c4` | `edit_nombre2KeyPress` | `MainForm` | `OnKeyPress` | 1 | edição |
| `0x0040d41c` | `edit_nombre3KeyPress` | `MainForm` | `OnKeyPress` | 1 | edição |
| `0x0040d43c` | `iguala_nombresClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040d534` | `boton_nombres2isoClick` | `MainForm` | `OnClick` | 1 | gravação |
| `0x0040de18` | `boton_tex2isoClick` | `MainForm` | `OnClick` | 1 | gravação |
| `0x0040dfe8` | `boton_dialogo_texClick` | `MainForm` | `OnClick` | 1 | carga |
| `0x0040e1a8` | `lista_equipos_2Change` | `MainForm` | `OnChange` | 1 | carga |
| `0x0040e304` | `paderechaeizquierdaClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040e4b0` | `paizquierdaClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040e5e8` | `paderechaClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040e720` | `paderecha2Click` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040e85c` | `paizquierda2Click` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040e998` | `parribaClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040ecc0` | `pabajoClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x0040ee80` | `grabar_camisetaClick` | `MainForm` | `OnClick` | 1 | gravação |
| `0x0040f69c` | `grabar_memoryClick` | `MainForm` | `OnClick` | 1 | gravação |
| `0x0040f8b8` | `lista_jugadores_1Change` | `MainForm` | `OnChange` | 1 | carga |
| `0x0040f8d4` | `mostrar_jugadorClick` | `MainForm` | `OnClick` | 2 | carga |
| `0x00410220` | `mostrar_estrategiaClick` | `MainForm` | `OnClick` | 2 | carga |
| `0x004107c8` | `FormCreate` | `MainForm` | `OnCreate` | 1 | carga |
| `0x00410a74` | `dorsalClick` | `MainForm` | `OnClick` | 23 | edição |
| `0x00410ddc` | `dorsalMouseDown` | `MainForm` | `OnMouseDown` | 23 | edição |
| `0x00410ea8` | `colorearClick` | `MainForm` | `OnClick` | 1 | edição |
| `0x00410fa4` | `SpeedButton2Click` | `MainForm` | `OnClick` | 1 | auxiliar |
| `0x00410fc0` | `SpeedButton1Click` | `MainForm` | `OnClick` | 1 | auxiliar |
| `0x00410fd0` | `Image3Click` | `MainForm` | `OnClick` | 1 | auxiliar |
| `0x00410ff4` | `base_teamClick` | `MainForm` | `OnClick` | 2 | auxiliar |
| `0x004111d8` | `FormShow` | `MainForm` | `OnShow` | 1 | carga |
| `0x00420e84` | `FormCreate` | `ficha_info2` | `OnCreate` | 1 | carga |
| `0x00420f08` | `SpeedButton1Click` | `ficha_error` | `OnClick` | 1 | auxiliar |

## Onde o plano e as tarefas envelheceram

Tudo abaixo é contagem do script contra texto já escrito. Nenhuma delas muda uma
conclusão; todas mudam um número que alguém usaria para se conferir.

A coluna **Diz** cita o texto como ele estava quando a WTE-TASK-04 mediu. A
[CORR-WTE-006](../../docs/tasks/CORR-WTE-006.md) propagou estas linhas para os
arquivos citados, então a citação já não é o que se lê lá — é o registro do que
foi corrigido, e envelhece junto. Quem decide se a seção inteira vira histórico
ao fechar a fase 1 é a WTE-TASK-09.

| Onde | Diz | Medido |
|---|---|---|
| WTE-TASK-04 e `docs/prompts/02-revisar.md` | `FormCreate` aparece **17** vezes | **16** — `ficha_error` e `ficha_error2` não têm |
| WTE-TASK-04 | `BitBtn1Click` **duas** | **4** — `estrategia`, `ficha_color`, `ficha_dorsal`, `jugador` |
| WTE-TASK-25 | `FormCreate` / `FormShow` — **19 endereços** | **18** = 16 `FormCreate` + 2 `FormShow` |
| §5.1 do plano | `etiqprecioClick` e o formulário `ficha_creditos_equipo` | o dono é **`jugador`**; `ficha_creditos_equipo` só publica `FormCreate` |
| WTE-TASK-30 | `etiqprecioClick` e o formulário `ficha_creditos_equipo` | o dono é **`jugador`**; `ficha_creditos_equipo` só publica `FormCreate` |
| WTE-TASK-28 | `malla1MouseDown` / `malla2MouseDown` pertencem a `ficha_color` e `ficha_creditos_equipo` | o dono é **`estrategia`** |
| WTE-TASK-28 | `SpeedButton2Click` e mais 5 entre os "handlers repetidos por vários formulários" | aparecem **uma vez cada**: `SpeedButton2Click` (`MainForm`), `Button2Click` (`MainForm`), `Image3Click` (`MainForm`), `botonClick` (`ficha_color`), `base_teamClick` (`MainForm`), `imagen_urlClick` (`ficha_about`) |
| WTE-TASK-28 | `BitBtn1Click` (**3×**) na mesma lista | **4×** |
| WTE-TASK-28 | "os **13** diálogos", e o escopo lista **15** formulários `ficha_*` | os 13 são as **unidades exportadas**; `ficha_color` e `ficha_error` são telas grandes e ficam de fora deles |

Duas observações que não são correção, e sim coisa que ninguém tinha contado:

- **`ficha_error2` não publica nenhum método** (`vmtMethodTable` = 0) e o `.dfm` dele não
  tem uma ligação de evento sequer. É o único formulário do binário nessa situação:
  aparece, e nada acontece nele.

- **`Button2Click`** (`MainForm`, `0x0040c9c4`) é o único dos 96 sem ligação de
  DFM — ver a seção do cruzamento.

## Ressalvas

- **A coluna `grupo` é ordenação de trabalho, não fato do binário.** As outras
  colunas são medidas; esta é regra escrita, e as regras estão no script justamente
  para poderem ser discutidas e reexecutadas.
- **Nada aqui foi decompilado.** O que se leu do `.exe` foram estruturas de dados —
  VMT, tabela de métodos, tabela de exportação — e nomes. Nenhuma instrução foi
  interpretada, e nenhum byte do binário foi copiado para cá: no espírito da §2 do
  plano, isto é recuperação de especificação, não transcrição.
- **"Sem referência em DFM" não quer dizer "morto".** Ligação feita em tempo de
  execução tem exatamente a mesma aparência aqui. Separar é da fase 4.
- **Os nomes vêm verbatim do binário**, inclusive a inconsistência de caixa
  (`lista_col1change` contra `lista_col0Change`). Normalizar criaria um nome que não
  existe em lugar nenhum.

