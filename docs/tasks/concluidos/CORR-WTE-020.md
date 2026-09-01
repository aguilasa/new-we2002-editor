---
id: CORR-WTE-020
title: "Correção: a tabela de propriedades do dfm2lfm.py diz ter sido medida na LCL 3.0, e nada remede — LCL_VERSAO é código morto"
type: correção
category: ui
status: concluído
depends_on: []
---

# CORR-WTE-020: a tabela `ACEITA`/`DESCARTA` não tem remedição versionada

## Problema identificado

O cabeçalho de `wte/tools/dfm2lfm.py` faz uma afirmação forte sobre a tabela que
decide o destino de cada uma das 5.480 propriedades dos 18 DFM:

> `PROPRIEDADES` diz, para cada classe da LCL, quais propriedades são aceitas e
> quais são descartadas. Ela **não é palpite**: saiu das fontes da LCL 3.0
> instaladas em `/usr/lib/lazarus/3.0/lcl`, varrendo as seções `published` de
> cada classe e de todos os ancestrais dela [...]

A varredura foi feita, e **o resultado está certo hoje** — esta revisão o
remediu e achou zero divergência além das oito entradas `Left`/`Top` que o
próprio cabeçalho explica. O problema é que a medição foi um script
descartável: nada em `make -C wte check` toca `/usr/lib/lazarus`, nenhum dos 64
testes de `test_dfm2lfm.py` menciona a LCL, e a única coisa que fixa a versão
medida é

```python
LCL_VERSAO = "3.0"   # Trocar de versao pede remedir -- nao e para editar a mao.
```

que **nunca é lida por ninguém**. `grep -rn LCL_VERSAO wte/` devolve só a
própria declaração. É um pino de versão que não pina nada.

O modo de falha é o que o gerador foi construído para não ter. `ACEITA` é a
lista do que sai **verbatim** para o `.lfm`; propriedade que entre ali por
engano — ou que a LCL perca numa versão nova — não aborta e não vira descarte:
é emitida, o `--check` fica verde porque o `--check` compara a saída consigo
mesma, o `lazbuild` compila porque `{$R}` só embute bytes, e a janela **explode
ao abrir**. É a mesma falha que o cabeçalho descreve para o comentário em LFM,
pela mesma razão, e contra ela o gerador não tem guarda.

Esta é a armadilha 11 do `progresso.md` — "todo número em doc vem de
ferramenta" — na sua forma de tabela.

## Evidência

A afirmação, e o pino morto:

```
$ sed -n '99,108p' wte/tools/dfm2lfm.py
`PROPRIEDADES` diz, para cada classe da LCL, quais propriedades sao aceitas e
quais sao descartadas. Ela **nao e palpite**: saiu das fontes da LCL 3.0
instaladas em `/usr/lib/lazarus/3.0/lcl`, varrendo as secoes `published` de
cada classe e de todos os ancestrais dela, cruzado com as propriedades que
ocorrem de fato nos 18 DFM.

$ grep -rn "LCL_VERSAO" wte/
wte/tools/dfm2lfm.py:159:LCL_VERSAO = "3.0"

$ grep -n "lazarus\|/usr/lib\|LCL 3" wte/tools/test_dfm2lfm.py
(nenhuma saída)
```

A remedição desta revisão, com um varredor de seções `published` sobre
`/usr/lib/lazarus/3.0/lcl` subindo a cadeia de ancestrais:

```
ACEITA sem published correspondente:
   ('TActionList', 'Left', 5)      ('TOpenDialog', 'Left', 15)
   ('TActionList', 'Top', 5)       ('TOpenDialog', 'Top', 15)
   ('TSaveDialog', 'Left', 15)     ('TTimer', 'Left', 5)
   ('TSaveDialog', 'Top', 15)      ('TTimer', 'Top', 5)
total suspeito: 8
```

As oito são exatamente as que o cabeçalho já justifica (`Left`/`Top` de
componente não visual vêm do `TComponent.DefineProperties` sobre o
`DesignInfo`, não de seção `published`). As quatro entradas de `DESCARTA`
também conferem — `grep -rn "property Ctl3D\|property ParentCtl3D\|property
OldCreateOrder\|property TextHeight" /usr/lib/lazarus/3.0/lcl/` não devolve
nada. E os 40 nomes de `IDENTIFICADORES` mais os 6 de
`ELEMENTOS_DE_CONJUNTO` ocorrem todos nas fontes da LCL 3.0.

Ou seja: a tabela está certa, e essa certeza não é reproduzível por nenhum
comando versionado do repositório.

## Causa raiz

A varredura das fontes da LCL foi feita uma vez, à mão, e o resultado foi
transcrito para o gerador em vez de o varredor virar ferramenta.

## Correção

### Arquivo: `wte/tools/check_lcl_props.py`

Novo. Faz o que o cabeçalho descreve, e falha alto:

1. Lê `ACEITA`, `DESCARTA`, `IDENTIFICADORES`, `ELEMENTOS_DE_CONJUNTO` e
   `LCL_VERSAO` importando `dfm2lfm.py` — a tabela continua tendo um dono só.
2. Descobre o caminho da LCL instalada (`lazbuild --version`, ou
   `/usr/lib/lazarus/<LCL_VERSAO>/lcl`) e **aborta** se a versão no disco não
   for a de `LCL_VERSAO`. É o que faz o pino existir de verdade.
3. Varre as seções `published` de cada classe e ancestrais e confere:
   - toda entrada de `ACEITA` tem `published` correspondente, com a **exceção
     nomeada** das oito `Left`/`Top` de componente não visual — a exceção é
     lista fechada no script, não um `if` genérico;
   - toda entrada de `DESCARTA` **não** tem;
   - todo `IDENTIFICADORES`/`ELEMENTOS_DE_CONJUNTO` ocorre nas fontes.
4. `--check` para o modo de conferência, mesmo contrato dos outros seis.

Exercitar as três guardas com entrada plantada em `wte/tools/test_*.py`:
propriedade inventada em `ACEITA`, propriedade real em `DESCARTA`, e
`LCL_VERSAO` divergindo do disco. Guarda nunca exercitada é guarda ausente.

### Arquivo: `wte/Makefile`

Acrescentar `check_lcl_props.py --check` à bateria, ao lado dos outros.

### Arquivo: `wte/tools/dfm2lfm.py`

No cabeçalho, trocar "saiu das fontes da LCL 3.0" pelo comando que refaz a
conta, e no comentário de `LCL_VERSAO` dizer quem o lê.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_lcl_props.py` | criar |
| `wte/tools/test_check_lcl_props.py` | criar |
| `wte/Makefile` | modificar |
| `wte/tools/dfm2lfm.py` | modificar (cabeçalho e comentário de `LCL_VERSAO`) |

## Verificação

- [ ] `python3 wte/tools/check_lcl_props.py --check` verde na LCL 3.0 instalada
- [ ] plantar `"NaoExiste"` em `ACEITA["TLabel"]` faz o script sair 2 nomeando
      a classe e a propriedade
- [ ] plantar `"Caption"` em `DESCARTA["TLabel"]` faz o script sair 2
- [ ] mexer em `LCL_VERSAO` faz o script recusar antes de varrer
- [ ] `python3 wte/tools/dfm2lfm.py --check` continua verde e **nenhum `.lfm`
      ou `.pas` muda** — esta correção não regera nada
- [ ] `make -C wte check` verde, agora com sete geradores + o novo
- [ ] `lazbuild -B wte/wte.lpi` compila sem warning novo
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-09

**Resumo do que foi feito:** O varredor descartável virou ferramenta.
`check_lcl_props.py` lê `ACEITA`, `DESCARTA`, `IDENTIFICADORES`,
`ELEMENTOS_DE_CONJUNTO` e `LCL_VERSAO` **importando** o `dfm2lfm.py` — a tabela
continua com um dono só —, indexa as 1.976 classes da LCL instalada com
ancestral e seções `published`, e confere os três sentidos. Contra a LCL 3.0 do
disco: 289 propriedades de `ACEITA` e 12 de `DESCARTA` conferidas, zero
divergência, o que reproduz o que a revisão tinha medido à mão. O pino de
versão passou a pinar: ele compara `LCL_VERSAO` com o `laz_major`/`laz_minor`
de `components/lazutils/lazversion.pas` e aborta **antes** de varrer.

As três guardas foram exercitadas com entrada plantada no `dfm2lfm.py` de
verdade, e as três saem 2 nomeando o que quebrou:

```
ACEITA inventada (TLabel.NaoExiste):   TLabel.NaoExiste: em ACEITA e sem published correspondente na LCL
DESCARTA que existe (TLabel.Caption):  TLabel.Caption: em DESCARTA e a LCL **tem** -- descartar propriedade existente perde dado do formulario
LCL_VERSAO = "4.2":                    LCL nao encontrada em /usr/lib/lazarus/4.2/lcl -- LCL_VERSAO do dfm2lfm.py diz '4.2'
```

Mais 19 testes hermes em `test_check_lcl_props.py`, sobre uma LCL sintética em
diretório temporário, para que os três sentidos sejam exercitados sem depender
do que está instalado na máquina.

**Problemas encontrados:** Três, todos no caminho.

1. **A primeira planta de `DESCARTA` foi inócua e passou.** Plantei `Caption`
   em `DESCARTA["TComboBox"]` e o script saiu 0 — corretamente: o `TComboBox`
   da LCL **não** publica `Caption` (publica `Text`). A guarda estava certa e
   a planta é que era ruim. Refeita em `TLabel`, que publica, e aí acusa.
   Vale como lembrete de que planta que não reproduz o defeito testa nada.
2. **O `__pycache__` mascarou a restauração.** `LCL_VERSAO = "3.0"` e `"4.2"`
   têm o **mesmo tamanho em bytes**, e a escrita caiu no mesmo segundo — o
   Python invalida `.pyc` por (mtime, tamanho), então reusou o compilado da
   planta depois de eu já ter restaurado o arquivo. O laço de plantas passou a
   apagar o `__pycache__` a cada volta.
3. **O `wte/Makefile` não precisou de linha nova**, ao contrário do que a
   correção previa: o `GENERATORS` já é um `wildcard` sobre `tools/*.py`, então
   o conferidor entrou na bateria sozinho. O que entrou foi comentário, nos
   dois lugares que catalogam as ferramentas — o item não é gerador, e quem
   ler a lista precisa saber disso.

**Arquivos criados/modificados:**

- `wte/tools/check_lcl_props.py` (**criado**)
- `wte/tools/test_check_lcl_props.py` (**criado** — 19 testes)
- `wte/tools/dfm2lfm.py` (cabeçalho e o comentário de `LCL_VERSAO`)
- `wte/Makefile` (comentário do `GENERATORS`)
- `wte/tools/README.md` (as duas tabelas de catálogo — discrepância achada no
  caminho: elas enumeram toda ferramenta e não conheciam as duas novas)
