# `re/edicao-cobertura.md` — o instrumento de cada handler de edição

Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md), o
critério *conferência verde para cada grupo de edição*. Gerado por
[`../tools/check_edicao.py`](../tools/check_edicao.py). **Não editar à mão.**

## Por que este arquivo existe

A resposta ao critério era **prosa**: o log da task dizia qual régua
cobria o quê, e prosa não reprova. Handler novo entra sem instrumento,
script muda de nome, conferência passa a ser pulada — e o texto continua
afirmando cobertura.

O gerador **reprova** se algum dos handlers do grupo ficar sem
instrumento, se o instrumento nomeado não existir, ou se um instrumento
estático não passar no próprio `--check`.

## A tabela

### atributos

| Handler | Classe | Instrumento | Por quê |
|---|---|---|---|
| `barrhabScroll` | estatico | `check_bitfields.py` | a ficha nao e mensuravel em pixel -- o `TScrollBar` do gtk2 cobre a faixa das linhas 2 a 16; o que se confere e a IDENTIDADE do campo |
| `barrhab_bisScroll` | estatico | `check_bitfields.py` | idem |

### barras

| Handler | Classe | Instrumento | Por quê |
|---|---|---|---|
| `sel_barraClick` | tela | `compara_tela.sh --edicao` | a largura da barra e `11*v + 9`: numero do jogo virado pixel |
| `track_barraChange` | tela | `compara_tela.sh --edicao` | idem -- os dois lados sao levados ao mesmo time e a mesma trilha |

### mover

| Handler | Classe | Instrumento | Por quê |
|---|---|---|---|
| `flechasapaClick` | estatico | `check_bitfields.py` | nao grava na imagem; o que ele mostra sao os campos de aparencia, e a ordem deles e o que a conferencia estatica prende |
| `pabajoClick` | outra_task | `WTE-TASK-27` | opcao A |
| `paderecha2Click` | outra_task | `WTE-TASK-27` | opcao A |
| `paderechaClick` | outra_task | `WTE-TASK-27` | opcao A, 2026-08-12 |
| `paderechaeizquierdaClick` | outra_task | `WTE-TASK-27` | opcao A |
| `paizquierda2Click` | outra_task | `WTE-TASK-27` | opcao A |
| `paizquierdaClick` | outra_task | `WTE-TASK-27` | opcao A |
| `parribaClick` | outra_task | `WTE-TASK-27` | opcao A |

### nomes

| Handler | Classe | Instrumento | Por quê |
|---|---|---|---|
| `casilla_nombreKeyPress` | estatico | `dump_truncamento.py` | o campo mora na ficha, que nao e mensuravel em pixel; o limite e o `MaxLength` do DFM contra a largura de `Player.name` |
| `edit_nombre1KeyPress` | tela | `compara_tela.sh --nomes` | o filtro decide quantos caracteres sobram, e a tinta mede isso |
| `edit_nombre2KeyPress` | tela | `compara_tela.sh --nomes` | idem |
| `edit_nombre3KeyPress` | tela | `compara_tela.sh --nomes` | idem, e o filtro dele e mais estrito -- recusa espaco e ponto |
| `iguala_nombresClick` | outra_task | `WTE-TASK-35` | o clique copia e trunca; o botao nao acinzenta no port porque o glifo e invariante sob o `gdeDisabled` da LCL -- causa medida pela CORR-WTE-060, divergencia deliberada, travada pelo `check_glifos_disabled.py` |

### numeros

| Handler | Classe | Instrumento | Por quê |
|---|---|---|---|
| `casilla_dorsalKeyPress` | estatico | `dump_truncamento.py` | idem -- e o `MaxLength` de 10 dele nao governa nada, o que so o documento de truncamento diz |
| `dorsalClick` | outra_task | `WTE-TASK-27` | grava o numero de camisa -- opcao A, 2026-08-12 |
| `dorsalMouseDown` | estatico | `check_bitfields.py` | dispara com o botao DIREITO e termina abrindo a ficha do jogador -- sub-dialogo que nenhuma regua de tela alcanca. Esta entrada dizia `compara_tela.sh --edicao` ate a evidencia de trace mostrar que aquele modo nao clica camisa nenhuma |
| `scroll_dorsalChange` | estatico | `dump_truncamento.py` | mora no `ficha_dorsal`, sub-dialogo que nenhuma regua de tela alcanca |

### tatica

| Handler | Classe | Instrumento | Por quê |
|---|---|---|---|
| `bolaEndDrag` | estatico | `dump_zonas.py` | idem |
| `bolaMouseDown` | estatico | `dump_zonas.py` | o retangulo que ele desenha sai da tabela de zonas, conferida contra o tamanho do `campo` no `.lfm` |
| `bolaMouseMove` | estatico | `dump_zonas.py` | idem |
| `campoMouseMove` | estatico | `dump_zonas.py` | idem |
| `rectanguloDragDrop` | estatico | `dump_zonas.py` | idem |
| `rectanguloDragOver` | estatico | `dump_zonas.py` | idem |
| `relojTimer` | estatico | `dump_zonas.py` | as seis tabelas da animacao nascem do mesmo `.bss`, e o destino final e a mesma geometria |

## As quatro classes

| classe | o que é | quem verifica |
|---|---|---|
| `tela` | uma sequência do `compara_tela.sh` | o próprio, no `:99`, com Wine |
| `estatico` | um gerador com `--check` | este script roda, e o resultado está abaixo |
| `outra_task` | a conferência mora em outra task, por decisão registrada | este script confere que a task existe |
| `sem_instrumento` | não há — e o script **reprova** | — |

A terceira **não é escapatória**: ela existe porque a **opção A**,
decidida pelo usuário em 2026-08-12, põe a metade de gravação de nove
handlers na [WTE-TASK-27](../../docs/tasks/27-handlers-de-gravacao.md).

**E o grupo `mover` não tem régua de tela por medição, não por
conveniência:** o `GravaJogador` do port devolve o código do caminho
feliz e não escreve byte nenhum — a gravação é da 27. O
`PreencheJogadores` seguinte repovoa com dado igual e **a tela do port
não muda**. Régua de tela ali seria teste que tem de falhar até a 27
existir.

## O que este gerador rodou

| Instrumento estático | `--check` |
|---|--:|
| `check_bitfields.py` | passou |
| `dump_truncamento.py` | passou |
| `dump_zonas.py` | passou |
