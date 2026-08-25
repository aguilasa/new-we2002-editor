# `re/golden.md` — a bateria golden completa

**GERADO — não editar à mão.** A correção entra no gerador, ou na
bateria que escreve o TSV, e o arquivo é regerado:

```sh
bash wte/tools/golden_suite.sh          # roda e escreve o re/golden.tsv
python3 wte/tools/check_golden.py       # regera este arquivo
python3 wte/tools/check_golden.py --check
```

Produto da [WTE-TASK-34](../../docs/tasks/34-bateria-golden-completa.md).
Fonte: [`golden.tsv`](golden.tsv), 96 corrida(s)
registrada(s), a mais recente de 2026-08-25.
**Todo número daqui saiu do script.**

## O critério, e o que ele custou para virar mensurável

> Para cada operação que grava, `wte.exe` sob Wine e o app Lazarus
> produzem **imagem byte-idêntica** a partir da mesma imagem de
> entrada, nas duas ROMs.

**48 de 48 corridas verdes na japonesa.** Na europeia,
23 de 48 não têm oráculo — ver a seção das duas ROMs.

## Operação × ROM × resultado

Cada roteiro roda **duas vezes por ROM**: `controle` (oráculo contra
oráculo, que prova que o par roteiro+imagem é determinístico) e
`golden` (oráculo contra o app Lazarus). A célula traz os dois, nessa
ordem, porque é nessa ordem que eles valem.

| Roteiro | japonesa | europeia |
|---|---|---|
| [golden-01-arranque](../tests/roteiros/golden-01-arranque.txt) | PASSOU / PASSOU | PASSOU / PASSOU |
| [golden-03-barras](../tests/roteiros/golden-03-barras.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-04-barras-editada](../tests/roteiros/golden-04-barras-editada.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-05-nomes](../tests/roteiros/golden-05-nomes.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-06-textura](../tests/roteiros/golden-06-textura.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-07-mcr](../tests/roteiros/golden-07-mcr.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-08-dorsal-mcr](../tests/roteiros/golden-08-dorsal-mcr.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-09-mover](../tests/roteiros/golden-09-mover.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-10-mover-ml](../tests/roteiros/golden-10-mover-ml.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-11-descarte-ml](../tests/roteiros/golden-11-descarte-ml.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-12-mcr2iso](../tests/roteiros/golden-12-mcr2iso.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-13-roundtrip](../tests/roteiros/golden-13-roundtrip.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-14-uniforme](../tests/roteiros/golden-14-uniforme.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-15-ficha](../tests/roteiros/golden-15-ficha.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-16-cor](../tests/roteiros/golden-16-cor.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-17-tatica](../tests/roteiros/golden-17-tatica.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-18-ficha-edicao](../tests/roteiros/golden-18-ficha-edicao.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-19-ficha-original](../tests/roteiros/golden-19-ficha-original.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-20-ficha-reserva](../tests/roteiros/golden-20-ficha-reserva.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-21-arrasto](../tests/roteiros/golden-21-arrasto.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-22-precos](../tests/roteiros/golden-22-precos.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-23-multiplas-edicoes](../tests/roteiros/golden-23-multiplas-edicoes.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-24-gravacao-dupla](../tests/roteiros/golden-24-gravacao-dupla.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |
| [golden-25-retorno](../tests/roteiros/golden-25-retorno.txt) | PASSOU / PASSOU | SEM_ORACULO / NAO_APLICAVEL |

**Nenhuma célula vazia** — era o quarto critério da task, e a guarda 2
do gerador o mecaniza: roteiro com par em disco e ausente do TSV
**aborta** a geração.

## Distribuição dos vereditos

| Veredito | Corridas |
|---|---:|
| `PASSOU` | 50 |
| `REPROVOU` | 0 |
| `SEM_ORACULO` | 23 |
| `NAO_APLICAVEL` | 23 |
| `ESTOUROU_TEMPO` | 0 |
| **total** | **96** |

`REPROVOU` é a única que acusa o port. `SEM_ORACULO` diz que o
`wte.exe` morreu com `c0000005` e gravou menos; `NAO_APLICAVEL` diz que
o `controle` daquele par não passou, e um `golden` ali seria ilegível.

## As duas combinações que só aparecem nesta fase

As tasks 27, 31 e 32 rodaram golden **por operação**, isoladas. Estas
duas exercitam o que teste isolado não alcança, e as duas nasceram
aqui:

| Roteiro | O que só ele exercita | Japonesa |
|---|---|---|
| [golden-23-multiplas-edicoes](../tests/roteiros/golden-23-multiplas-edicoes.txt) | edicao multipla antes de gravar | PASSOU / PASSOU |
| [golden-24-gravacao-dupla](../tests/roteiros/golden-24-gravacao-dupla.txt) | gravar duas vezes seguidas | PASSOU / PASSOU |

**A edição múltipla** põe duas edições de naturezas diferentes na mesma
sessão — uma barra num `TTrackBar` e os três nomes em `TEdit` — e grava
pelos dois botões sem recarregar o time. É a classe de bug que teste
isolado não pega: se o original recalculasse algo ao trocar de contexto
de edição, a segunda gravação sairia de um estado que nenhum gate da
fase 4 chegou a produzir.

**A gravação dupla** grava a tática duas vezes no mesmo time, com
recarga entre elas. A tática é a escolha certa porque é a gravação que
carrega `OFS_KICKER`: o `newWe2002` registra que o **`ed.exe`** não é
idempotente — `Load`+`Save` troca os dois primeiros cobradores de cada
clube de Master League, e gravar duas vezes volta ao início. Se o app
Lazarus não reproduzisse esse vaivém, a segunda gravação divergiria
mesmo com a primeira byte-idêntica.

**E nenhum dos dois prova sozinho que o estímulo aconteceu.** É a lição
1 da quarta passagem da
[WTE-TASK-31](../../docs/tasks/31-fechamento-fase-4.md): se os dois
lados não fizerem nada, os dois concordam. O terceiro ponto de cada um
é o par que grava **uma** vez pelo mesmo caminho —
`golden-04-barras-editada` e `golden-05-nomes` para o primeiro, e para o
segundo o próprio `golden-24` truncado depois da descarga.

### O terceiro ponto da gravação dupla, medido

Rodado em 2026-08-25, e o resultado é **negativo — e decisivo**:

| Medida | Bytes |
|---|---:|
| uma gravação × duas gravações | **0** |
| ROM virgem × uma gravação | 11962 |

**O `wte.exe` não tem o vaivém.** Uma gravação e duas produzem a mesma
imagem, e os seis cobradores do time 5 (em `2329086`)
saem intactos dos três estados:

| Estado | `OFS_KICKER` do time |
|---|---|
| ROM virgem | `[9, 5, 5, 5, 7, 5]` |
| uma gravação | `[9, 5, 5, 5, 7, 5]` |
| duas gravações | `[9, 5, 5, 5, 7, 5]` |

**E as duas gravações aconteceram**, que é o que impede o zero de ser
trivial: contra a ROM virgem a imagem muda em 11962
bytes. O gate não está medindo dois lados parados.

**O time 5 não é escolha livre**, e é aí que estava o defeito
que a [CORR-WTE-104](../../docs/tasks/CORR-WTE-104.md) achou. O roteiro
gravava no time 2, cujos dois primeiros cobradores são iguais
(`[7, 7, …]`): ali a troca que se procura é a identidade, e o roteiro
passaria com vaivém e sem ele. São 41 dos 96 times em que ela seria
visível; o 5 é o primeiro deles, com
`[9, 5]` no primeiro par.

**O que isto decide.** A não-idempotência que o enunciado da fase 6
cita é do `ed.exe` — outro binário, outro caminho de código. O
`wte.exe` **não** a tem neste caminho, então não há divergência a
reproduzir e o port não deve inventá-la. É entrada da
[WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md) como
resultado negativo, não como divergência.

## As duas ROMs, e por que a resposta não é simétrica

O critério diz "nas duas ROMs", e esta bateria **rodou as duas** em vez
de decidir por prosa que uma não valia. O resultado da europeia é
medida, não suposição:

| ROM | Corridas | `PASSOU` | `SEM_ORACULO` | `NAO_APLICAVEL` | `REPROVOU` |
|---|---:|---:|---:|---:|---:|
| japonesa | 48 | 48 | 0 | 0 | 0 |
| europeia | 48 | 2 | 23 | 23 | 0 |

Com a europeia o `wte.exe` morre ao trocar de time: a carga do time
escreve além do fim da tabela de `0x00433580` e deixa `0x00010001` onde
estaria o ponteiro de `dorsal1`, que passa no teste de `nil` e não é
objeto nenhum ([`crash-causa.md`](crash-causa.md)). **Oráculo que morre
no meio grava menos**, e nenhuma das duas palavras usuais serve: verde
seria mentira, e vermelho acusaria o port por bytes que o original nunca
chegou a escrever. Por isso o vocabulário tem `SEM_ORACULO`.

**O que isso fecha, e o que não fecha.** Fecha a pergunta que a
WTE-TASK-31 deixou nomeada — *a europeia é da 34* —, e a resposta é que
ela foi medida, roteiro a roteiro, em vez de dispensada em bloco por uma
medição de 2026-08-18 feita sobre um roteiro só. Não fecha a paridade na
europeia, que **continua sem oráculo**: enquanto o `wte.exe` cair ali,
nenhuma bateria pode julgar o port contra ele naquela imagem.

## Custo

**6700 segundos de relógio** (1.9 h) nas
96 corridas. Cada uma faz duas cópias da imagem e as
apaga no fim: ~586 MB de temporário com a japonesa, ~950 MB com a
europeia. **`roms/` nunca é alvo** — a guarda 4 do `golden_check.sh`.

Não roda em CI, e o plano já registra isso: precisa de Wine, do `:98` e
do binário do Obocaman, que é gitignored.

