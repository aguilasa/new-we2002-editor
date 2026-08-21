---
id: CORR-WTE-074
title: "Correção: a confrontação Pascal × Python do .mcr aponta para um arquivo transitório"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-074: a confrontação Pascal × Python do `.mcr` aponta para um arquivo transitório

## Problema identificado

`TestPascalConcorda.test_a_leitura_bate_com_a_do_python`, em
[`wte/tools/test_dump_mcr.py`](../../wte/tools/test_dump_mcr.py), é **a única
prova de que o leitor Pascal e o leitor Python enxergam o mesmo cartão de
verdade** — os invariantes sem cartão não cobrem isso. Ele procura a fixture
num caminho fixo:

```python
CARTAO = M.ROOT / "work" / "saida.mcr"
```

`work/saida.mcr` é **transitório**: o `golden_check.sh` apaga
`work/<artefato>` antes de cada lado da corrida, e as corridas de
`golden-07-mcr`, `golden-12-mcr2iso` e `golden-13-roundtrip` usam justamente
`--artefato saida.mcr`. A fixture estável tem outro nome — `work/entrada.mcr`,
que é a cópia que o próprio cabeçalho do `golden-13-roundtrip` manda fazer:

```text
#   cp work/saida.mcr work/entrada.mcr     # a fixture, gerada por 27-mcr.txt
```

Resultado: numa máquina que rodou o gate — que é a máquina onde a task foi
fechada —, a confrontação **pula**, e o teste diz isso alto. O que ele não diz
é que a fixture está ali ao lado, com outro nome.

## Evidência

Estado do `work/` desta revisão, depois de rodar o `golden-13-roundtrip` nos
modos controle e golden:

```text
-rw-rw-r-- 1 ingmar ingmar 131072 ago 20 17:18 work/entrada.mcr
-rw-rw-r-- 1 ingmar ingmar 131072 ago 20 18:23 work/volta.mcr
```

Não há `work/saida.mcr`. A bateria Python:

```text
Ran 31 tests in 0.486s
OK (skipped=2)
```

E a razão dos dois pulos:

```text
test_a_leitura_bate_com_a_do_python ... skipped 'sem work/saida.mcr -- as duas
leituras NAO foram confrontadas. Gere a fixture com o roteiro
wte/tests/roteiros/27-mcr.txt'
O que a spec do `grabar_memoryClick` mediu, o leitor recupera. ... skipped
'sem a fixture'
```

O pulo é honesto e diz o que deixou de medir — não é o defeito. O defeito é o
nome: a fixture existe, tem os 131.072 bytes, e o teste passa ao largo dela.

## Causa raiz

O caminho da fixture foi escrito quando `saida.mcr` era o produto da sonda
`27-mcr.txt`; ao virar também o `--artefato` dos três goldens, o mesmo nome
passou a ser apagado a cada corrida, e ninguém revisitou o teste.

## Correção

### Arquivo: `wte/tools/test_dump_mcr.py`

A fixture passa a ser resolvida numa ordem, com a variável de ambiente na
frente — a mesma forma do `WTE_MCR_ENTRADA` que o gate já usa:

```python
@classmethod
def cartao(cls) -> Path | None:
    """A primeira fixture que existir, ou `None`.

    `work/saida.mcr` e TRANSITORIO: o `golden_check.sh` o apaga antes de
    cada lado das corridas que usam `--artefato saida.mcr`. A copia estavel
    e a `work/entrada.mcr`, que o cabecalho do `golden-13-roundtrip` manda
    fazer.
    """
    do_ambiente = os.environ.get("WTE_MCR_FIXTURE")
    candidatos = ([Path(do_ambiente)] if do_ambiente else []) + [
        M.ROOT / "work" / "entrada.mcr",
        M.ROOT / "work" / "saida.mcr",
    ]
    return next((c for c in candidatos if c.is_file()), None)
```

A mensagem do `skipTest` acompanha: cita os dois caminhos e a variável, para
quem lê o pulo saber onde pôr o arquivo.

O segundo teste que pula pelo mesmo motivo — o que confere a fixture contra a
spec do `grabar_memoryClick` — usa o mesmo resolvedor.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_dump_mcr.py` | modificar |

## Verificação

- [x] Com `work/entrada.mcr` no disco e sem `work/saida.mcr`,
      `python3 -m unittest test_dump_mcr` roda a confrontação em vez de pular —
      32 testes, `OK (skipped=2)` virou `OK`
- [x] `WTE_MCR_FIXTURE=/caminho/outro.mcr` é respeitado — os três casos da
      `TestPascalConcorda` passam com a cópia fora de `work/`
- [x] Sem fixture nenhuma, o pulo continua e a mensagem cita a variável e os
      dois caminhos
- [x] `make -C wte check` verde — 644 testes, `OK (skipped=1)`, rc=0 (eram 3
      pulos)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-20

**Resumo do que foi feito:**

A fixture passou a ser resolvida por ordem — `$WTE_MCR_FIXTURE`,
`work/entrada.mcr`, `work/saida.mcr` — num `classmethod cartao()` que os dois
testes usam. A estável vem antes da transitória, e o docstring diz por quê: as
corridas `golden-07-mcr`, `golden-12-mcr2iso` e `golden-13-roundtrip` usam
`--artefato saida.mcr`, e o `golden_check.sh` apaga o artefato antes de cada
lado.

A mensagem do `skipTest` ficou única (`sem_fixture()`) e cita a variável e os
dois caminhos, para quem lê o pulo saber onde pôr o arquivo. O segundo teste,
que só dizia "sem a fixture", passou a dizer o mesmo.

Efeito medido no gate: `make -C wte check` caiu de `OK (skipped=3)` para
`OK (skipped=1)` — os dois pulos que sumiram são justamente a confrontação
Pascal × Python e a conferência contra a spec do `grabar_memoryClick`.

**Problemas encontrados:**

`relative_to(M.ROOT)` na mensagem do pulo estourava com fixture fora da árvore,
que é exatamente o caso do `WTE_MCR_FIXTURE`. Ganhou o mesmo `_curto()` que o
`gravacao_controle.py` já usa pelo mesmo motivo.

**Arquivos criados/modificados:**

- `wte/tools/test_dump_mcr.py`
