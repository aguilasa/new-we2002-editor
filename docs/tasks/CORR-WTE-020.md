---
id: CORR-WTE-020
title: "Correção: a tabela de propriedades do dfm2lfm.py diz ter sido medida na LCL 3.0, e nada remede — LCL_VERSAO é código morto"
type: correção
category: ui
status: pendente
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

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
