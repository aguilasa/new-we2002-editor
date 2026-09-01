# `re/campos.md` — nome → deslocamento dos campos publicados

Produto da [WTE-TASK-25](../../docs/tasks/concluidos/25-handlers-de-carga.md).
Gerado por [`../tools/dump_campos.py`](../tools/dump_campos.py), a partir
de `we-team-editor/we-team-editor.exe` e dos 18 formulários de [`dfm/`](dfm/).
**Não editar à mão** — correção entra no script e o arquivo é regerado:

```sh
python3 wte/tools/dump_campos.py
python3 wte/tools/dump_campos.py --check   # o que `make -C wte check` roda
```

A tabela em si está em [`campos.tsv`](campos.tsv); este arquivo é a leitura
dela. **Todo número daqui saiu do script**, inclusive os do texto corrido.

## Para que serve

Handler do `.exe` referencia controle por deslocamento — `mov eax,[ebx+0x33c]`.
Sem este mapa, ler um handler da fase 4 para em *"ele chama um método de
alguma coisa"*, que não dá para escrever em Pascal. Com ele, `0x33c` no
`ficha_color` é o `recuadro2`, e a frase vira spec.

## A ordem do DFM **não** serve, e é isso que o número abaixo mede

A derivação barata seria: primeiro `object` do `.dfm` no primeiro campo, e
assim por diante. Medido nos 18 formulários, essa regra acerta
**73 de 440** campos. A ordem do `.dfm` é a de criação; a dos
campos é a da declaração no `.h`, e o C++Builder não as mantém em sincronia.
Derivar dali produziria leitura errada com cara de certa — a armadilha 1 do
[`../../docs/tasks/concluidos/progresso.md`](../../docs/tasks/concluidos/progresso.md) por outro
caminho.

## De onde o mapa sai

Da *published field table* que o VMT aponta em deslocamento **-56**. Ela
existe porque o streaming de DFM precisa resolver `object lista_equipos:
TComboBox` no campo certo, por nome, em tempo de execução — e por isso
sobreviveu ao `/STRIP`, como a published method table da
[WTE-TASK-04](../../docs/tasks/concluidos/04-mapa-de-handlers.md) (-52).

```text
word  contagem
dword ponteiro para a tabela de classes
contagem x { dword deslocamento, word índice de classe, shortstring nome }
```

## O que foi medido

São **440 campos** em **18 formulários**, contra
**441 `object`** nos `.dfm`. A diferença é **1** componente **sem nome**, que não gera
campo — o `TStaticText` de 4×4 px do `MainForm` que o `progresso.md`
registra como o que separa a contagem exata da apressada.

O primeiro campo de todo formulário cai em **0x2f0** (752), que é o
tamanho de instância de `TForm` nesta VCL. O número sai medido daqui, não
escrito à mão: o script exige que os 18 concordem e aborta se um discordar —
discordância significaria que o -56 está errado ou que a classe não deriva
de `TForm`. O tamanho de instância de cada formulário é o primeiro múltiplo
de 8 a partir daí, o que explica os 4 bytes de sobra nos de contagem ímpar.

| Formulário | VMT | Instância | Campos | `object` | Sem nome | 1º campo |
|---|---|---:|---:|---:|---:|---|
| `MainForm` | `0x00427dd4` | 1216 | 115 | 116 | 1 | `lista_equipos` |
| `estrategia` | `0x00428c4c` | 1112 | 89 | 89 | 0 | `campo` |
| `ficha_about` | `0x0042adc8` | 776 | 6 | 6 | 0 | `Image1` |
| `ficha_color` | `0x00429f20` | 1016 | 65 | 65 | 0 | `seleccion` |
| `ficha_creditos_equipo` | `0x00428aac` | 768 | 3 | 3 | 0 | `etiq1` |
| `ficha_dorsal` | `0x0042b4b8` | 768 | 4 | 4 | 0 | `etiq_dorsal` |
| `ficha_enlaza` | `0x0042b2f0` | 776 | 6 | 6 | 0 | `etiq1` |
| `ficha_error` | `0x004321a0` | 768 | 3 | 3 | 0 | `SpeedButton1` |
| `ficha_error2` | `0x0042a764` | 760 | 2 | 2 | 0 | `etiq1` |
| `ficha_info` | `0x0042a8d8` | 776 | 6 | 6 | 0 | `etiq1` |
| `ficha_info2` | `0x00432344` | 776 | 6 | 6 | 0 | `Label1` |
| `ficha_info3` | `0x0042afb8` | 760 | 2 | 2 | 0 | `BitBtn6` |
| `ficha_info4` | `0x0042a5c4` | 768 | 4 | 4 | 0 | `etiq1` |
| `ficha_movertodos` | `0x0042ac2c` | 768 | 3 | 3 | 0 | `etiq1` |
| `ficha_salida` | `0x0042aa94` | 768 | 3 | 3 | 0 | `etiq1` |
| `ficha_warning` | `0x0042b140` | 776 | 5 | 5 | 0 | `etiq1` |
| `ficha_warning_2` | `0x004293f4` | 776 | 5 | 5 | 0 | `etiq1` |
| `jugador` | `0x004295a4` | 1208 | 113 | 113 | 0 | `barrhab1` |

## Como usar ao ler um handler

O `this` do formulário chega em `EAX` (convenção Borland, §8.1 do plano), e
o corpo costuma guardá-lo num registrador. `[<reg>+0x2f0]` no `MainForm` é
o `lista_equipos`; a coluna `offset` do TSV está em hexadecimal justamente
para colar contra o disassembly sem conversão no meio.
