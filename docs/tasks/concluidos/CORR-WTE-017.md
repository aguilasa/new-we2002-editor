---
id: CORR-WTE-017
title: "Correção: o `fase-1.md` separa offset em tabela de offset em `.text` por substring do endereço, e a igualdade que a prosa afirma não é conferida"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-017: `"0x0042" not in va` é teste de faixa escrito como teste de texto

## Problema identificado

A §3 do [`fase-1.md`](../../../wte/re/fase-1.md) responde a pergunta da
WTE-TASK-09 — "algum dos 19 caiu fora do limite da tabela?" — partindo os
confirmados em dois grupos:

| Onde o valor aparece | Quantos |
|---|---:|
| dentro de uma das duas tabelas de `.data` | 16 |
| só como imediato de instrução, em `.text` | 3 |

O corte sai daqui (`wte/tools/check_fase1.py:363-367`):

```python
# Confirmado que aparece so em .text nao mora em nenhuma das duas tabelas.
fora_da_tabela = [r for r in confirmados
                  if r["classe"] == "confirmado"
                  and "0x0042" not in r["va"]]
```

`"0x0042" not in va` é uma comparação de **faixa de endereço** feita como
comparação de **substring**. Ela funciona hoje por coincidência de dígito: as
duas tabelas e as seis cópias moram em `0x004231a0`, `0x0042b750`, `0x0042d244`
e `0x0042e6d4`, e os três imediatos moram em `0x00404xxx`/`0x00405xxx`. Mas
`.text` **não termina em `0x00422000`**:

```
.text      VA 0x00401000..0x00423000  (139264 B)
.data      VA 0x00423000..0x0043c000  (102400 B)
```

Os últimos 4 KiB de `.text` — `0x00422000` a `0x00422fff` — casam a substring
`0x0042`. Um imediato ali seria contado como morando dentro de uma tabela de
`.data`, e o veredito "nenhum caiu fora do limite" passaria a se apoiar numa
partição errada, sem nada acusando.

O segundo lado do mesmo problema: a prosa logo abaixo afirma uma igualdade que
o script nunca confere.

> Os outros são exatamente os slots preenchidos […]

Hoje é verdade — `19 − 3 = 16` e `slots preenchidos = 16` —, e é essa igualdade
que sustenta a resposta da tarefa. Ela é afirmação de texto, não asserção: se a
partição desandar, o `--check` continua verde e a frase continua impressa.

## Evidência

As faixas do PE, lidas do cabeçalho de seção do próprio binário:

```
$ python3 - <<'PY'   # cabecalho de secao de we-team-editor.exe
.text      VA 0x00401000..0x00423000  (139264 B)
.data      VA 0x00423000..0x0043c000  (102400 B)
```

Os três que o corte separa hoje, e por que ele acerta por ora:

```
$ awk -F'\t' '$1=="confirmado" && $9=="confirmado" {print $2, $7}' wte/re/offsets.tsv
…
OFS_COST_NATIONAL  0x0040448c|0x00404628
OFS_COST_NC        0x004046b9|0x00404b66
OFS_LINK_ML        0x004042fd
```

`0x004042fd` é o caso que mostra a fragilidade de perto: ele **contém** os
dígitos `0042`, e só escapa porque o prefixo `0x` obriga o casamento a começar
no início da string. Um endereço `0x00422abc` — legítimo, dentro de `.text` —
casaria.

A igualdade não conferida:

```
$ python3 -c '<contagem de offsets.tsv>'
registro: {'candidato': 90, 'ausente': 50, 'tabela_slot': 23,
           'confirmado': 19, 'tabela_copia': 6}
slots com nome: 16      # o que o fase-1.md chama de "slots preenchidos"
19 - 3 = 16             # o que a particao por substring produz
```

Os dois valores coincidem, e nenhuma linha do script exige que coincidam.

## Causa raiz

O `check_fase1.py` classifica por texto do endereço porque não tem as faixas de
seção à mão — ele foi escrito para consumir produto, não para abrir o PE —, e a
coincidência de prefixo entre `.data` e o fim de `.text` passou despercebida.

## Correção

### Arquivo: `wte/tools/check_fase1.py`

Duas mudanças pequenas, nenhuma delas exigindo um sexto leitor de PE.

**1. Trocar o teste de texto por teste numérico de faixa.** Os endereços do
`va` já são hexadecimais separados por `|`; comparar contra o início de `.data`
resolve sem ler o binário:

```python
DATA_VA = 0x00423000   # inicio de .data; .text vai ate aqui. Medido no
                       # cabecalho de secao do .exe, e conferido pelo
                       # dump_offsets.py, que ja separa .text de .data.

def _em_data(va: str) -> bool:
    """Algum dos enderecos da linha mora em `.data`."""
    return any(int(a, 16) >= DATA_VA for a in va.split("|") if a.startswith("0x"))

fora_da_tabela = [r for r in confirmados
                  if r["classe"] == "confirmado" and not _em_data(r["va"])]
```

**2. Fazer a igualdade da prosa abortar.** Junto das duas conferências de censo
que já existem em `gerar()`:

```python
if len(confirmados) - len(fora_da_tabela) != len(slots_com_nome):
    raise CheckError(
        f"a particao dos confirmados ({len(confirmados)} - "
        f"{len(fora_da_tabela)}) nao bate com os slots preenchidos "
        f"({len(slots_com_nome)}) -- a §3 afirma que sao os mesmos")
```

Preferir `DATA_VA` extraído do `dump_offsets.py`, se ele já expuser a faixa,
a redeclará-la aqui — duplicar constante medida é o que o
[`README.md`](../../../wte/tools/README.md) do diretório manda evitar.

### Arquivo: `wte/tools/test_check_fase1.py`

Um teste com entrada plantada, no espírito do `FORBIDDEN`: um `confirmado` com
`va = 0x00422abc` (dentro de `.text`, casando a substring velha) tem de sair
como imediato, não como slot de tabela. Sem entrada plantada a guarda nova é
guarda não exercitada.

### Arquivo: `wte/re/fase-1.md`

Regerar. Se os números não mudarem — e não devem —, o arquivo sai idêntico e o
`--check` continua verde; a diferença é que a §3 passa a estar sustentada por
asserção em vez de por coincidência.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase1.py` | modificar |
| `wte/tools/test_check_fase1.py` | modificar |
| `wte/re/fase-1.md` | modificar (**pelo gerador**) |

## Verificação

- [ ] `python3 wte/tools/check_fase1.py --check` verde, e a §3 continua
      publicando 16 / 3
- [ ] O teste de entrada plantada falha com o corte por substring e passa com o
      corte por faixa (provar rodando os dois)
- [ ] `python3 -m unittest test_check_fase1` verde
- [ ] `make -C wte check` verde de ponta a ponta
- [ ] `roms/` intocada; `we-team-editor.exe` só para leitura

## Log de Execução

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

O corte virou `particionar_confirmados()`: faixa numérica contra
`DATA_VA = 0x00423000` em vez de substring, mais a igualdade da §3 como
`CheckError`. A §3 da saída passou a dizer qual é o critério e que ele aborta.
Seis testes novos, com entrada plantada nos **dois** sentidos que a substring
errava.

**Problemas encontrados:**

A CORR mandava preferir a faixa vinda do `dump_offsets.py` a redeclará-la —
mas ele não expõe constante, e o `offsets.md` não publica a faixa das seções.
O que existe é melhor: a coluna `nota` do `offsets.tsv`, que o `dump_offsets.py`
preenche com o nome da seção de **cada ocorrência**, lida do PE. Então `DATA_VA`
ficou declarada aqui e o corte por faixa é confrontado com a `nota` a cada
rodada — a constante duplicada não fica sem guarda, que é o que o
[`README.md`](../../../wte/tools/README.md) do diretório pede.

Prova de que os dois cortes discordam, com a entrada plantada `0x00422abc`
somada aos 19 confirmados reais:

```
corte velho (substring): 3 -> perde o plantado, conta como slot de tabela
corte novo  (faixa)    : 4 -> ['OFS_COST_NATIONAL', 'OFS_COST_NC',
                              'OFS_LINK_ML', 'OFS_PLANTADO']
```

A §3 continua publicando 16 / 3, e o `--check` continua verde.

**Arquivos criados/modificados:**

- `wte/tools/check_fase1.py` — `DATA_VA`, `_em_data()`,
  `particionar_confirmados()`, e a §3 da saída
- `wte/tools/test_check_fase1.py` — `TesteCorteDeFaixa`, seis casos
- `wte/re/fase-1.md` — regerado
