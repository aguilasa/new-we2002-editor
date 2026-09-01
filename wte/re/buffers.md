# `re/buffers.md` — campos de tamanho fixo, e o que acontece na borda

**GERADO — não editar à mão.** A correção entra no gerador:

```sh
python3 wte/tools/dump_buffers.py
python3 wte/tools/dump_buffers.py --check   # o que `make -C wte check` roda
```

Produto da [WTE-TASK-36](../../docs/tasks/concluidos/36-buffers-e-truncamento.md).
**Todo número daqui saiu do script.**

## As duas fontes, conciliadas

O enunciado manda conciliar a **camada de dados** (todo
`array[0..N-1] of AnsiChar`) com as **specs de edição** (todo campo com
`MaxLength`), e diz o que fazer com a diferença: *campo com `MaxLength`
20 gravando em array de 16 é bug esperando a entrada certa*. O gerador
**aborta** nesse caso — não relata, aborta.

São **4 campos de digitação**, e nos 4 o limite cabe no vetor.

| Controle | Formulário | Vetor | Capacidade | Limite | Origem | Modo |
|---|---|---|---:|---|---|---|
| `edit_nombre1` | MainForm | `kanji_name` | 20 B | 5..13 | runtime | dois bytes |
| `edit_nombre2` | MainForm | `names` | 20 B | 7..19 | runtime | um byte |
| `edit_nombre3` | MainForm | `abbreviations` | 4 B | 3 | dfm | um byte |
| `casilla_nombre` | jugador | `name` | 11 B | 10 | dfm | um byte |

## A terceira fonte, que o enunciado não previa

`MaxLength` não está só no DFM. Dos quatro campos, **dois recebem o
limite em tempo de execução**: `edit_nombre1` e `edit_nombre2` são
carregados por `lista_equiposChange`, que lê a largura do registro de
uma tabela por time e põe `largura - 1`. O limite deles **muda com o
time selecionado**.

| Tabela | Times | Mínimo | Máximo | `MaxLength` resultante |
|---|---:|---:|---:|---|
| `TEAM_NAME_KANJI_LEN` | 95 | 6 | 14 | 5..13 |
| `TEAM_NAME_LEN_3` | 95 | 8 | 20 | 7..19 |

Um inventário que olhasse só o DFM veria os `MaxLength` estáticos e
concluiria que os campos de nome de time **não têm limite** — que é o
contrário da verdade. É por isso que a coluna `origem` existe.

## Os campos numéricos, e por que `MaxLength` não guarda nada neles

O destino deles não é vetor com capacidade — é uma **faixa**, e quem a
guarda é a validação do handler de gravação. Os dois são
desproporcionais, e é o que o inventário existe para mostrar:

| Controle | Formulário | `MaxLength` | Aceita digitar até | Faixa válida | Destino |
|---|---|---:|---|---|---|
| `casilla_precio` | `jugador` | 3 | `999` | 1..250 | o byte de credito de `OFS_COST_*` |
| `casilla_dorsal` | `jugador` | 10 | `9999999999` | 1..99 (1..32 fora de Master League) | o campo de numero de camisa (`SquadNumbers`) |

O `casilla_dorsal` é o extremo: **dez dígitos** para um número que não
passa de 99. Se a validação do handler sumisse, o `MaxLength` não
seguraria coisa nenhuma — e é exatamente esse o predicado que o gerador
confere no `.inc`, um por campo. Ele **aborta** se a faixa sair do
handler, porque aí o campo fica aberto e nada na tela diz isso.

**A borda dos dez dígitos é benigna, e a razão é do Pascal:**
`StrToIntDef` devolve o padrão `0` quando a cadeia não cabe num
`Integer`, e `0` reprova na faixa `1..99` como qualquer outro valor
inválido. Não há estouro silencioso — há recusa, que é o que o original
também faz.

## Os vetores que não são campo de digitação

Entram no inventário para a conta fechar, e ficam fora dos testes de
borda: têm tamanho fixo, mas ninguém digita neles.

| Vetor | Arquivo | O que é |
|---|---|---|
| `raw_formation` (31 B) | `we2002_team.pas` | 30 bytes de posicao de jogador |
| `raw_kanji_name` (40 B) | `we2002_team.pas` | o slot cru, antes do decodificador |
| `mixed_case_name` (20 B) | `we2002_team.pas` | nome em caixa mista, so leitura |
| `link` (46 B) | `we2002_team.pas` | 46 indices de jogador |
| `url` (500 B) | `we2002_player.pas` | sidecar do SoFIFA, nao vai para a imagem |

A camada de dados declara **17** vetores de tamanho
fixo ao todo; os demais são tabelas constantes e buffers locais.

