# `re/fase-4.md` — o fechamento da fase 4

**GERADO — não editar à mão.** Correção entra no gerador e o arquivo
é regerado:

```sh
python3 wte/tools/check_fase4.py
python3 wte/tools/check_fase4.py --check   # o que `make -C wte check` roda
```

Produto da [WTE-TASK-31](../../docs/tasks/31-fechamento-fase-4.md).
Fonte: [`published_methods.tsv`](published_methods.tsv), os `.md` de
[`spec/`](spec/), os `.inc` de [`../src/impl/`](../src/impl/), os
roteiros de [`../tests/roteiros/`](../tests/roteiros/) e o registro da
bateria em [`fase-4-golden.tsv`](fase-4-golden.tsv).
**Todo número daqui saiu do script.**

## O critério, e onde ele está

> **Pronto quando:** os 96 têm veredito e nenhum é "não portado" sem
> justificativa escrita.

**96 dos 96 têm veredito fechado; 0 não.**
A segunda metade do critério está cumprida — ver a seção do
`nao portado` abaixo —, e a primeira também: nenhum handler ficou
`aberto`, e nenhum ficou sem arquivo de spec.

## Cobertura e vereditos

| Veredito | Handlers |
|---|---:|
| `implementado` | 69 |
| `trivial` | 19 |
| `divergencia deliberada` | 6 |
| `nao portado` | 2 |
| `aberto` | 0 |
| *(sem arquivo de spec)* | 0 |
| **total** | **96** |

96 dos 96 têm arquivo de spec.

## Os que continuam `aberto`

**Nenhum.** Todos os 96 fecharam veredito, e a seção fica no lugar
porque o número que importa é o zero: se um handler voltar a
`aberto` — spec nova, veredito revisto —, ele aparece aqui.

## Quem grava na imagem, e o gate de cada um

São **17**, e o número não é o que as tasks
contavam. **Nove** é a conta de quem alguém *chamou* de gravação: seis na
WTE-TASK-27, uma na 28, uma na 29 e as três órfãs da 30. A leitura aqui é
da seção `## Bytes tocados` de cada spec, e a diferença aparece nos dois
sentidos — **entram** os sete de mover jogador e número de camisa (grupo
`edicao`, que gravam dentro da `0x00404820`), mais o `FormShow` e o
`boton_dialogo_weClick`, que gravam no arranque; **saem** o
`grabar_memoryClick` e o `grabar_camisetaClick`, que apesar do nome não
tocam a ROM — leem dela e emitem um arquivo.

A tabela abaixo é guardada: handler que a spec diz que grava e não tem
linha aqui **aborta** o fechamento. Era justamente por não existir essa
conta que três gravações ficaram sem dono até a WTE-TASK-30.

| Endereço | Handler | Grupo | Veredito | Gate |
|---|---|---|---|---|
| `0x004069e8` | [ficha_color.BitBtn3Click](spec/ficha_color.BitBtn3Click.md) | auxiliar | implementado | [golden-16-cor](../tests/roteiros/golden-16-cor.txt) |
| `0x00408548` | [jugador.BitBtn3Click](spec/jugador.BitBtn3Click.md) | auxiliar | implementado | [golden-15-ficha](../tests/roteiros/golden-15-ficha.txt), [golden-18-ficha-edicao](../tests/roteiros/golden-18-ficha-edicao.txt), [golden-19-ficha-original](../tests/roteiros/golden-19-ficha-original.txt), [golden-20-ficha-reserva](../tests/roteiros/golden-20-ficha-reserva.txt) |
| `0x0040a660` | [estrategia.BitBtn3Click](spec/estrategia.BitBtn3Click.md) | auxiliar | implementado | [golden-17-tatica](../tests/roteiros/golden-17-tatica.txt), [golden-21-arrasto](../tests/roteiros/golden-21-arrasto.txt) |
| `0x0040bd60` | [MainForm.boton_dialogo_weClick](spec/MainForm.boton_dialogo_weClick.md) | carga | divergencia deliberada | [golden-01-arranque](../tests/roteiros/golden-01-arranque.txt) |
| `0x0040c46c` | [MainForm.boton_mcr2isoClick](spec/MainForm.boton_mcr2isoClick.md) | gravacao | implementado | [golden-12-mcr2iso](../tests/roteiros/golden-12-mcr2iso.txt), [golden-13-roundtrip](../tests/roteiros/golden-13-roundtrip.txt) |
| `0x0040cab8` | [MainForm.boton_barras2isoClick](spec/MainForm.boton_barras2isoClick.md) | gravacao | implementado | [golden-03-barras](../tests/roteiros/golden-03-barras.txt), [golden-04-barras-editada](../tests/roteiros/golden-04-barras-editada.txt) |
| `0x0040d534` | [MainForm.boton_nombres2isoClick](spec/MainForm.boton_nombres2isoClick.md) | gravacao | implementado | [golden-05-nomes](../tests/roteiros/golden-05-nomes.txt) |
| `0x0040de18` | [MainForm.boton_tex2isoClick](spec/MainForm.boton_tex2isoClick.md) | gravacao | implementado | [golden-06-textura](../tests/roteiros/golden-06-textura.txt) |
| `0x0040e304` | [MainForm.paderechaeizquierdaClick](spec/MainForm.paderechaeizquierdaClick.md) | edicao | implementado | [golden-09-mover](../tests/roteiros/golden-09-mover.txt) |
| `0x0040e4b0` | [MainForm.paizquierdaClick](spec/MainForm.paizquierdaClick.md) | edicao | implementado | [golden-09-mover](../tests/roteiros/golden-09-mover.txt) |
| `0x0040e5e8` | [MainForm.paderechaClick](spec/MainForm.paderechaClick.md) | edicao | implementado | [golden-09-mover](../tests/roteiros/golden-09-mover.txt) |
| `0x0040e720` | [MainForm.paderecha2Click](spec/MainForm.paderecha2Click.md) | edicao | implementado | [golden-10-mover-ml](../tests/roteiros/golden-10-mover-ml.txt) |
| `0x0040e85c` | [MainForm.paizquierda2Click](spec/MainForm.paizquierda2Click.md) | edicao | implementado | [golden-10-mover-ml](../tests/roteiros/golden-10-mover-ml.txt) |
| `0x0040ecc0` | [MainForm.pabajoClick](spec/MainForm.pabajoClick.md) | edicao | implementado | [golden-11-descarte-ml](../tests/roteiros/golden-11-descarte-ml.txt) |
| `0x00410a74` | [MainForm.dorsalClick](spec/MainForm.dorsalClick.md) | edicao | implementado | [golden-08-dorsal-mcr](../tests/roteiros/golden-08-dorsal-mcr.txt) |
| `0x00410ff4` | [MainForm.base_teamClick](spec/MainForm.base_teamClick.md) | auxiliar | implementado | [golden-22-precos](../tests/roteiros/golden-22-precos.txt) |
| `0x004111d8` | [MainForm.FormShow](spec/MainForm.FormShow.md) | carga | divergencia deliberada | [golden-01-arranque](../tests/roteiros/golden-01-arranque.txt) |

## A bateria golden desta corrida

São 25 roteiros em disco, 24 com par do lado port, e
**21 deles rodaram nesta bateria**. Cada um desses rodou
**duas vezes**: `controle` (oráculo contra oráculo, que prova que o par
roteiro+imagem é determinístico) e `golden` (oráculo contra o app
Lazarus). **O controle vem antes do teste** — sem ele, verde e vermelho
não significam nada.

Com par e fora desta bateria: `golden-23-multiplas-edicoes`, `golden-24-gravacao-dupla`, `golden-25-retorno`. Eles são da [WTE-TASK-34](../../docs/tasks/34-bateria-golden-completa.md),
que roda a bateria completa (operação × ROM) e registra em
[`golden.tsv`](golden.tsv). O guarda de cobertura aceita as **duas**
listas: o que ele exige é que roteiro com par tenha rodado nos dois
modos e esteja escrito em lugar versionado, não que esteja escrito
*aqui* — senão o registro da fase 4 cresceria toda vez que uma fase
posterior escrevesse um roteiro, e a data desta corrida passaria a
mentir.

Fora da bateria por não ter lado port: `golden-02-gravacao`. Roteiro sem par julga o oráculo contra ele mesmo e mais nada; o
gerador **aborta** se um roteiro **com** par ficar sem as duas
corridas registradas.

**4 deles comparam um artefato além das imagens.** Nem
toda gravação é na ROM: o `grabar_memoryClick` emite um `.mcr` e o
`grabar_camisetaClick` um `.bin` de uniforme, e nos dois a imagem sai
intacta dos dois lados. Comparar só as imagens aprovaria um port que não
fizesse absolutamente nada, e é para isso que o `golden_check.sh` tem
`--artefato`. São eles: `golden-07-mcr`, `golden-08-dorsal-mcr`, `golden-13-roundtrip`, `golden-14-uniforme`.

| Roteiro | Controle | Golden | s | Tentativas |
|---|---|---|---:|---|
| [golden-01-arranque](../tests/roteiros/golden-01-arranque.txt) | PASSOU | PASSOU | 81 | 1 |
| [golden-03-barras](../tests/roteiros/golden-03-barras.txt) | PASSOU | PASSOU | 156 | 1 |
| [golden-04-barras-editada](../tests/roteiros/golden-04-barras-editada.txt) | PASSOU | PASSOU | 174 | 1 |
| [golden-05-nomes](../tests/roteiros/golden-05-nomes.txt) | PASSOU | PASSOU | 231 | 1 |
| [golden-06-textura](../tests/roteiros/golden-06-textura.txt) | PASSOU | PASSOU | 185 | **2** |
| [golden-07-mcr](../tests/roteiros/golden-07-mcr.txt) | PASSOU | PASSOU | 160 | 1 |
| [golden-08-dorsal-mcr](../tests/roteiros/golden-08-dorsal-mcr.txt) | PASSOU | PASSOU | 200 | 1 |
| [golden-09-mover](../tests/roteiros/golden-09-mover.txt) | PASSOU | PASSOU | 208 | 1 |
| [golden-10-mover-ml](../tests/roteiros/golden-10-mover-ml.txt) | PASSOU | PASSOU | 267 | 1 |
| [golden-11-descarte-ml](../tests/roteiros/golden-11-descarte-ml.txt) | PASSOU | PASSOU | 312 | 1 |
| [golden-12-mcr2iso](../tests/roteiros/golden-12-mcr2iso.txt) | PASSOU | PASSOU | 189 | 1 |
| [golden-13-roundtrip](../tests/roteiros/golden-13-roundtrip.txt) | PASSOU | PASSOU | 258 | 1 |
| [golden-14-uniforme](../tests/roteiros/golden-14-uniforme.txt) | PASSOU | PASSOU | 160 | 1 |
| [golden-15-ficha](../tests/roteiros/golden-15-ficha.txt) | PASSOU | PASSOU | 203 | 1 |
| [golden-16-cor](../tests/roteiros/golden-16-cor.txt) | PASSOU | PASSOU | 187 | 1 |
| [golden-17-tatica](../tests/roteiros/golden-17-tatica.txt) | PASSOU | PASSOU | 190 | 1 |
| [golden-18-ficha-edicao](../tests/roteiros/golden-18-ficha-edicao.txt) | PASSOU | PASSOU | 149 | **2** |
| [golden-19-ficha-original](../tests/roteiros/golden-19-ficha-original.txt) | PASSOU | PASSOU | 149 | 1 |
| [golden-20-ficha-reserva](../tests/roteiros/golden-20-ficha-reserva.txt) | PASSOU | PASSOU | 154 | 1 |
| [golden-21-arrasto](../tests/roteiros/golden-21-arrasto.txt) | PASSOU | PASSOU | 183 | 1 |
| [golden-22-precos](../tests/roteiros/golden-22-precos.txt) | PASSOU | PASSOU | 162 | **2** |

**42 de 42 corridas verdes**, 3958 segundos de relógio no total.

**E a coluna de tentativas não é enfeite.** `golden-06-textura`, `golden-18-ficha-edicao`, `golden-22-precos` precisou de mais de uma corrida; a causa de cada
caso está no Log da task que rodou a bateria. Gate que precisa de
repetição para ficar verde deixa de separar *"o port diverge"* de
*"a corrida não estava pronta"*, e essa é a classe de problema que a
[CORR-WTE-080](../../docs/tasks/CORR-WTE-080.md) nomeou — a causa não
precisa ser a mesma para o custo ser.

**As duas ROMs, e por que a conta é de uma só.** O critério da task diz
"nas duas ROMs". Com a europeia o `wte.exe` morre ao trocar de time —
49.749 violações de acesso contra 0 — e a gravação nunca acontece, então
o oráculo não existe daquele lado. Está medido e registrado em
[`gravacao-controle.md`](gravacao-controle.md); a bateria roda sobre a
japonesa, e a cobertura da europeia é da
[WTE-TASK-34](../../docs/tasks/34-bateria-golden-completa.md).

## Força da evidência

Cada uma das cinco seções obrigatórias de cada spec
carrega a sua linha `**Evidência:**`, e é essa a população contada:
evidência escrita em `## Notas`, `## Justificativa` ou `## Como o veredito
fechou` fica de fora, e são
44 linhas. A distribuição das
481 cobradas:

| Evidência | Linhas |
|---|---:|
| `diff medido` | 10 |
| `disassembly lido` | 468 |
| `observacao de tela` | 2 |
| `nao medido` | 1 |

**Nenhuma spec se apoia só em `observação de tela` ou `não medido`.**
Era a pergunta 3 da task — *"quantas são hipóteses vestidas de
spec?"* — e a resposta é zero. O `spec_index.py` já recusava essa
combinação para o veredito `implementado`; medido agora sobre os
cinco vereditos, ela não aparece em nenhum.

Os 3 pontos soltos de evidência fraca, um a um —
são seções isoladas dentro de specs cujo resto está medido:

| Handler | Seção | Evidência | Decisão |
|---|---|---|---|
| [MainForm.boton_dialogo_weClick](spec/MainForm.boton_dialogo_weClick.md) | Comportamento de erro | `observacao de tela` | **Fica.** A afirmação é sobre **ausência** de tratamento — o original não confere nada além do tamanho, e a checagem de tamanho é só aviso. Ausência não tem endereço para ler: o disassembly já mostrou que não há ramo de erro, e a tela mostrou o que acontece sem ele. |
| [MainForm.mostrar_jugadorClick](spec/MainForm.mostrar_jugadorClick.md) | Bytes tocados | `nao medido` | **Fica.** A seção diz `Nenhum gravado`, e o que ficou por medir são as faixas **lidas**. O golden do grupo prova a metade que importa para a fase 4 — ele não grava —, e o mapa de leitura só faz falta a quem for otimizar carga, que não é desta fase. |
| [MainForm.FormShow](spec/MainForm.FormShow.md) | Comportamento de erro | `observacao de tela` | **Fica, e tem dono.** O original encerra e o port não — é divergência deliberada, registrada para a [WTE-TASK-35](../../docs/tasks/35-divergencias-deliberadas.md). Para *"o original encerra"*, tela é a evidência certa: o que se mede é o efeito observável, não a instrução. |

**Nenhum dos três pede disassembly antes da Fase 6**, e a tabela acima
diz por quê, um a um. O gerador **aborta** se aparecer ponto fraco sem
decisão escrita — ou decisão sobrando, que é o sintoma de um ponto que
foi medido e a tabela não acompanhou.

## `nao portado`, e a justificativa de cada um

São 2. O `spec_index.py` **recusa** o veredito
sem uma seção `## Justificativa` não vazia, então a existência dela é
mecânica; o que a task pede a mais é que a razão seja de escopo, e
não de dificuldade.

- [`estrategia.ComboBoxDrawItem`](spec/estrategia.ComboBoxDrawItem.md)
- [`MainForm.Button2Click`](spec/MainForm.Button2Click.md)

## Os cinco `trivial` reconferidos

`trivial` é o veredito mais fácil de dar por preguiça, e o único cuja
consequência — *"não toca a imagem"* — o golden não verifica sozinho:
um handler que não deveria gravar e não grava passa igual a um que não
foi exercitado. Por isso o critério da fase manda reamostrar cinco.

**A escolha é declarada, e não sorteada.** Cinco espaçados uniformemente
pela lista ordenada por endereço dão a propriedade que o sorteio existe
para dar — ninguém escolhe quais depois de ver o resultado — e são
reproduzíveis, que é o que o `--check` exige. A amostra sai proporcional
à população, e isso importa: 14 dos 19 `trivial` são `FormCreate` da
forma "cor".

| Handler | Endereço | Bytes | Confirmado | O que o corpo faz |
|---|---|---:|---|---|
| [ficha_dorsal.BitBtn1Click](spec/ficha_dorsal.BitBtn1Click.md) | `0x00402b40` | 21 | sim | grava 1 no campo de resultado modal (+0x24C) e chama TCustomForm::Hide; nenhuma chamada de escrita |
| [ficha_warning.FormCreate](spec/ficha_warning.FormCreate.md) | `0x00402cdc` | 16 | sim | uma chamada a TControl::SetColor sobre a propria instancia, com 0x3C3CDC; o port poe $003C3CDC |
| [ficha_info.FormCreate](spec/ficha_info.FormCreate.md) | `0x00402f8c` | 16 | sim | idem, com 0xDCDC3C; o port poe $00DCDC3C |
| [ficha_warning_2.FormCreate](spec/ficha_warning_2.FormCreate.md) | `0x00408d88` | 16 | sim | idem, com 0x3C3CDC; o port poe $003C3CDC |
| [ficha_error.SpeedButton1Click](spec/ficha_error.SpeedButton1Click.md) | `0x00420f08` | 14 | sim | carrega a global _ficha_info2 e chama ShowModal pelo VMT +0xE8; resultado descartado |

**Os cinco confirmaram.** Nenhum toca a imagem, e nos três
`FormCreate` o valor de cor que o original passa a
`TControl::SetColor` é o mesmo que o `.inc` do port escreve.

Registro em [`fase-4-trivial.tsv`](fase-4-trivial.tsv); a amostra é
recalculada a cada corrida, e o gerador **aborta** se ela se deslocar sem
o registro acompanhar — handler que entra ou sai de `trivial` muda quais
são os cinco, e reconferência velha não vale para handler novo.

## Varredura por decompilado colado

238 arquivos varridos — as specs, os `.inc` de corpo escrito
à mão e as unidades de `src/`.

**Nada.** É a §2 do plano sustentada por medida em vez de honra.

