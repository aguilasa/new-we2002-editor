---
id: LOOKS-TASK-21
title: "Incógnita (q) — a tela `LOOKS SET` medida no jogo: texto de cada valor, ajuda, cursor e valores iniciais"
type: investigação
category: oráculo
phase: 8
depends_on: ["LOOKS-TASK-20"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (q)"
status: concluído
---

# LOOKS-TASK-21: A tela `LOOKS SET`, medida

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1, §10.2 e §10.3 (q).
- **O pedido do usuário:** a janela do visualizador tem de **ser** a tela
  `LOOKS SET` que os dois save states mostram — doze linhas, cursor, valores
  trocáveis, caixa de ajuda, placa de posição. Esta task mede a tela; a
  [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) a constrói. **Texto de tela inventado a partir do rótulo é a armadilha
  17 do perfil**, e um gate que confere a janela contra uma tabela inventada
  confere a invenção.
- **O que já existe:** as doze linhas, domínios e rótulos no `looks.py`
  ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)); o `oracle.row_value` e o `confront.glyph_mask`, que leem a célula de
  valor sem o cursor que pisca (armadilha 28); e a tabela de texto da tela em
  Shift-JIS full-width na RAM (§1.10).
- **Os campos travam nas pontas** (armadilha 14) — medido nas linhas de cor e
  de cabelo. As outras seis (`DEFAUL`, `NAT`, `HEIG`, `BODY`, `AGE`, `FOOT`)
  não foram andadas.
- **Toda medição começa em `load_state`**, nos dois slots. Slot 1 é goleiro
  (placa `GK`), slot 2 jogador de linha (placa `CB`).

---

## Objetivo

Uma tabela medida, num módulo do núcleo sem Qt (`tools/looks/screen.py`), com
tudo o que a tela `LOOKS SET` escreve e como ela anda — de modo que a janela da
[`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) só desenhe o que o jogo desenha.

---

## Critério de conclusão

- [x] **O texto de cada valor de cada uma das doze linhas**, lido por
      ferramenta — da tabela de texto em RAM, ou das células capturadas —,
      nunca transcrito à mão: `A TYPE`, `A1 TYPE`, `175 cm`, `RIGHT`, e o que
      mais houver, incluindo os valores sem rótulo de terceiro
      (`FACE` e `H.F.COL.` com um valor sem nome, `FOOT` com um).
- [x] **O texto da caixa de ajuda** para cada linha sob o cursor.
- [x] **O cursor:** vertical dá a volta ou trava; horizontal trava nas pontas
      — medido nas **doze** linhas, andando até as duas pontas.
- [x] **Os valores iniciais dos dois save states**, lidos do registro do
      jogador em RAM e conferidos contra o que a tela mostra; a placa de
      posição e o nome da camisa de cada um.
- [x] O domínio da linha `NAT` — quantos valores e em que ordem — medido;
      o que ele **aplica** é da [`LOOKS-TASK-23`](/docs/tasks/looks/23-default-por-nacionalidade.md).
- [x] As regiões da tela (título, placa, painel, linhas, cursor, ajuda)
      medidas pela ferramenta, para a janela reproduzir o arranjo — **em
      pixels do display nativo de 512×240 e em frações dele**, e não em
      frações do quadro capturado, que corta overscan conforme a configuração
      do emulador (ver o Log).
- [x] `screen.py` com `self_check()` e caso vermelho, na lista do
      `selftest.py`; o comando de medição no `oracle.py` pula com 77 sem as
      variáveis e os states, e entra na tabela de gates do perfil.
- [x] §10.3 (q) do plano com o veredito e a data.

---

## Log de Execução

**Executado em:** 2026-09-17.

**O que se aprendeu.** O texto da tela não precisa ser lido da imagem: o jogo o
imprime, e dá para parar nele. A rotina `layout.SCREEN_PRINT` recebe **oito
objetos de texto por quadro** — os doze rótulos num só, as unidades (`O.K.`,
`TYPE`, `cm`) noutro, os valores de `SKIN` a `BOOTS` num terceiro, `NAT` e
`FOOT` um cada, mais placa, nome da camisa e título — e a `layout.SCREEN_GLYPH`
desenha glifo a glifo, em dois passes: um que mede a largura com tudo no mesmo
`x`, e o que desenha. Ler os objetos custa **oito paradas** por quadro; ler os
glifos custa **268**, e é o que faz a caminhada das doze linhas caber em 12
minutos. Os dois juntos são a verificação: o `screen.decode` desfaz os três
códigos de controle das strings e o resultado é conferido contra os glifos
desenhados — 34 strings, nos dois states e na ponta de cada linha.

O resto veio junto: a ajuda de cada linha por um ponteiro que o próprio jogo
compara antes de redesenhar (`layout.SCREEN_HELP`), o registro de 12 bytes do
jogador em **duas cópias vivas** que andam com a tela (`layout.PLAYER_RAM`; uma
terceira candidata fica parada), e as caixas da tela por varredura da VRAM
nativa.

**O que a tela faz**, tudo em `tools/looks/screen.json`, escrito pela
ferramenta:

| linha | valores | guardado | ajuda |
|---|---|---|---|
| `DEFAUL` | 1 (`O.K.`) | — | `Confirm` |
| `NAT` | 80 (`Unknown` … `New Zeland`) | — | `Nation` |
| `SKIN` | 4 | 0..3 | `Skin Colour ■ Turn` |
| `HAIR` | 32 | 0..31 | `Kind of Hair ■ Turn` |
| `H.COL` | 8 | 0..7 | `Hair Colour ■ Turn` |
| `FACE` | 7 | 0..6 | `Kind of Face Hair ■ Turn` |
| `H.F.COL.` | 7 | 0..6 | `Hair Face Colour ■ Turn` |
| `HEIG` | 56 (155..210 cm) | 155..210 | `Height` |
| `BODY` | 8 | 0..7 | `Body` |
| `AGE` | 32 (15..46) | 15..46 | `Age` |
| `BOOTS` | 8 | 0..7 | `Boots ■ Turn` |
| `FOOT` | 3 (`RIGHT`, `LEFT`, `BOTH`) | 0..2 | `Foot` |

As doze **travam** nas duas pontas; o cursor vertical **dá a volta** nos dois
sentidos, lido pela caixa amarela na VRAM e não pela contagem de teclas.
**O alcance da tela é menor que o do campo** em `HEIG` (56 de 64), `FACE` e
`H.F.COL.` (7 de 8) e `FOOT` (3 de 4) — e **todo rótulo de terceiro do
`looks.py` é o que o jogo escreve** em cada valor alcançável, que é a primeira
testemunha do próprio jogo sobre eles. Andar uma linha **não mexe em nenhuma
outra**, `NAT` inclusive.

Os dois states começam iguais em tudo menos a placa (`GK`, `CB`): cursor em
`NAT`, `Unknown`, `A`, `A1`, `175 cm`, `23`, `RIGHT`, e o registro em RAM diz o
mesmo. A caixa de ajuda mostra **`Visual`** ao carregar, sobra do menu, até a
primeira tecla.

**Regiões, e a adaptação do critério.** A task pedia frações **do quadro
capturado**; elas foram medidas em **pixels do display nativo de 512×240** e em
frações dele. A captura do emulador sai em 864×655 com overscan cortado
conforme a configuração — 34,6 px entre linhas que distam 12 no jogo —, então
fração de captura descreve a configuração desta máquina e não o arranjo do
jogo. Painel `(16,66)-(161,185)`, linhas `(176,37)-(496,185)`, ajuda
`(16,187)-(496,221)`, cursor na linha `NAT` `(314,53)-(476,64)` com passo de 12.
Título, placa e nome da camisa ficam como âncora de texto, em coordenadas do
centro do display, que é o sistema em que o jogo as passa.

**Gates, na árvore de `2b19a84`:**

```
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)          # e 67 of 67 controls red
$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
$ WE2002_LOOKS_IMAGE=<japonesa> python tools/looks/cli.py check
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok
```

A medição viva rodou **antes** do commit, sobre o mesmo código: o
`oracle.py --screen` deu `0 difference(s) from screen.json` em 769 s, depois de
o `--screen --write` ter escrito o arquivo em 706 s.

O controle veio antes de o verde valer: com `HEIG` `155 cm` trocado para
`154 cm` e a `BOOTS` do slot 1 para `B TYPE` no `screen.json`, a mesma corrida
acusa as duas diferenças. E os três controles negativos novos do `controls.py`
ficam vermelhos **cada um no seu próprio check** — decodificador que pula byte
desconhecido, ajuda repetida entre linhas, e o passe de medida contado como
desenho.

**Arquivos criados/modificados:** a lista confere contra
`git show --stat --format= HEAD`.

- `tools/looks/screen.py` — novo: decodificação, composição das linhas,
  varredura de caixas e cursor, a tabela e as regras de andar.
- `tools/looks/screen.json` — novo, **gerado** por `oracle.py --screen --write`.
- `tools/looks/oracle.py` — `--screen [--write]`, a leitura de objetos, glifos,
  ajuda, registro e VRAM, e a caminhada das doze linhas.
- `tools/looks/layout.py` — as cinco constantes novas da tela.
- `tools/looks/controls.py` — três controles negativos do `screen.py`.
- `tools/looks/selftest.py` — `screen` na lista de módulos.
- `docs/PLAN-LOOKS-PY.md` — §10.3 (q) com o veredito.
- `docs/prompts/perfil-looks.md` — armadilhas 33 a 36, os dois gates novos e o
  arquivo gerado do ciclo.
- `docs/tasks/looks/22-a-tela-na-janela.md` e
  `docs/tasks/looks/23-default-por-nacionalidade.md` — o que esta task deixa
  para cada uma.
- `docs/tasks/looks/progresso.md`.

**Problemas encontrados.**

1. **Oito corridas perdidas por uma pergunta feita cedo demais.**
   `get_gpu_state` **antes** do `load_state` responde 256×239, o modo da tela
   de boot; a `LOOKS SET` é 512×240. Recortar a VRAM em 256 colunas deixa o
   painel e perde a caixa das linhas. Pior que o erro foram as **três
   explicações plausíveis e falsas** que vieram antes de reler o mesmo dump com
   o recorte certo: buffer pela metade, PNG ainda sendo gravado, buffer de
   baixo deslocado para a linha 241. Virou a armadilha 33 do perfil, com a
   pergunta que teria cortado a série: *o vermelho é pela causa que eu acho?*
2. **Objeto de texto não tem lugar fixo.** O de `NAT` está em `x=-80` com
   `Unknown` e em `x=-104` com qualquer nação, e a chave por posição fazia o
   mesmo objeto virar outro — duas corridas caíram nisso. A chave passou a ser
   o endereço do objeto, e o critério de pertencer às linhas passou a ser a
   caixa em que ele é disposto. Armadilha 34.
3. **A ajuda mente logo depois do `load_state`** (`Visual` até a primeira
   tecla), o que fez a checagem recusar a linha `NAT`, que é a do cursor
   inicial. Armadilha 35.
4. **O cursor pisca, e some numa das fases** — três cores medidas e um dump em
   seis sem pixel amarelo nenhum. Armadilha 36.
5. **Uma sonda subiu o emulador sem esconder a janela.** Foi um `fork.launch`
   à mão, fora do `Oracle`; a janela pode ter aparecido por alguns segundos
   antes de o processo ser derrubado. Daí em diante toda subida passou pelo
   `Oracle`, que move a janela para −32000.
6. **Duas vezes o heredoc do shell quebrou o fonte** — `\n` virando quebra de
   linha real dentro de uma string, e o byte do `IEND` do PNG virando caractere
   não ASCII. É a armadilha que a LOOKS-TASK-19 já tinha pago; o conserto é a
   ferramenta de edição, não o heredoc.
