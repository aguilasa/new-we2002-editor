---
id: CORR-WTE-069
title: "Correção: as três funções novas do we2002_ml entraram no caminho de gravação sem um teste sequer"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-069: `IndiceDoBlocoMl`, `ParDoIndiceLinearMl` e `PrimeiroBlocoLivreMl` sem teste

## Problema identificado

A oitava passagem da WTE-TASK-27 acrescentou três funções à **interface** do
`wte/src/we2002_ml.pas`:

```pascal
function IndiceDoBlocoMl(time, slot: Integer): Integer;
procedure ParDoIndiceLinearMl(indice: Integer; out time, slot: Integer);
function PrimeiroBlocoLivreMl: Integer;
```

As três são o miolo do ramo de Master League da `0x00404820` — a
`ParDoIndiceLinearMl` é o port da `0x0040427c`, o **inverso** do índice linear,
e é ela quem decide para que par `(time, slot)` o bloco alocado vai. Nenhuma
delas tem caso em `wte/tests/test_ml.pas` nem em `wte/tools/test_conta_ml.py`:

```text
$ grep -n 'PrimeiroBlocoLivreMl\|ParDoIndiceLinearMl\|IndiceDoBlocoMl' \
      wte/tests/test_ml.pas wte/tools/test_conta_ml.py
(nenhum resultado)
```

As funções antigas da mesma unidade têm — o `test_ml.pas` confere o prefixo, o
teto do vetor e a conta contra a do Python, e reporta `CASOS 8`. As três novas
estão cobertas **só** pelo `golden-11-descarte-ml`, que exercita **uma**
alocação: o bloco 350. Uma função inversa verificada num ponto é uma função
inversa não verificada — o erro típico dela é de fronteira (primeiro slot de um
time, time de contagem zero, índice igual ao total), e nenhum desses pontos é o
350.

Não é discrepância de comportamento: o gate está verde e eu o reproduzi. É
lacuna de régua, no grupo que o próprio enunciado da task chama de "o mais
arriscado do projeto".

## Evidência

O que o `test_ml.pas` cobre hoje, rodado contra `work/ml-eu.bin`:

```text
OK	prefixo do time 0 e zero
OK	prefixo depois do ultimo time e o total
OK	o teto do vetor cobre o maior indice possivel
OK	imagem inexistente devolve o total
OK	a conta bate com a do conta_ml.py
CASOS	8
```

Nenhum caso nomeia as três funções novas. A única execução delas em todo o
repositório é indireta:

```text
wte/src/impl/ep2002_mainform.aux.inc:1233:      novo := PrimeiroBlocoLivreMl;
wte/src/impl/ep2002_mainform.aux.inc:1239:      ParDoIndiceLinearMl(novo, t, sl);
```

E o disassembly de `0x0040427c` mostra o que precisa valer (percorre a tabela
somando, e devolve `slot = indice - corrido + 23`, o `add al,0x17` de
`0x004042a7`):

```text
4042a4:	8a 4d fc             	mov    cl,BYTE PTR [ebp-0x4]
4042a7:	04 17                	add    al,0x17
4042a9:	88 0d e8 35 43 00    	mov    BYTE PTR ds:0x4335e8,cl
```

## Causa raiz

A passagem tratou o golden como régua suficiente para código novo de unidade,
e o golden só passa pelos caminhos que o roteiro alcança.

## Correção

### Arquivo: `wte/tests/test_ml.pas`

Casos novos, no estilo dos que já existem (uma linha `OK`/`FALHA` por caso, e
o `CASOS N` batendo):

- **ida e volta**: para todo time com `ML_NC_POR_TIME[t] > 0` e todo slot
  válido, `ParDoIndiceLinearMl(IndiceDoBlocoMl(t, s))` devolve `(t, s)`;
- **fronteiras**: primeiro e último slot de um time, e o primeiro time com
  contagem zero — que não pode ser devolvido por `ParDoIndiceLinearMl` para
  índice nenhum;
- **fora da faixa**: índice negativo e índice `>= 462` saem com `(-1, -1)`;
- **`PrimeiroBlocoLivreMl`** com `OcupacaoMl` montado à mão: vetor cheio devolve
  `-1`, vetor com um furo devolve o furo, e o furo em 0 devolve 0.

Atualizar o `CASOS` esperado no `test_invariantes_sem_imagem` do
`test_conta_ml.py`: ele afirma `CASOS 7` — que é o número correto hoje sem
imagem, conferido — e é justamente essa asserção que impede caso novo de sumir
calado. Acrescentando casos, o número tem de subir junto, ou o teste reprova.

### Arquivo: `wte/tools/test_conta_ml.py` *(opcional, se a ida e volta for espelhada em Python)*

O `conta_ml.py` tem `indice_do_bloco()`; não tem o inverso. Se o inverso for
escrito lá para confrontar com o Pascal, é o mesmo padrão do
`TestPascalConcorda` que já existe.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/test_ml.pas` | modificar |
| `wte/tools/test_conta_ml.py` | modificar |

## Verificação

- [x] `cd wte/tools && python3 -m unittest test_conta_ml` verde, com o `CASOS`
      novo
- [x] Um erro plantado no `+ ML_SLOT_MIN` da `ParDoIndiceLinearMl` reprova pelo
      menos um caso novo — guard nunca exercitado é guard ausente
- [x] `lazbuild wte/wte.lpi` compila
- [x] `make -C wte check` rc 0
- [x] `bash wte/tools/golden_check.sh wte/tests/roteiros/golden-11-descarte-ml.txt
      --modo golden --roteiro-port …` continua byte-idêntico
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-20

**Resumo do que foi feito:**

Doze casos novos no `test_ml.pas`, em três procedimentos:

- **`IdaEVoltaDoIndiceLinear`** — `ParDoIndiceLinearMl(IndiceDoBlocoMl(t, s))`
  devolve `(t, s)` para **todo** bloco válido dos 120 times, não para um; mais
  o primeiro e o último slot de um time isolados, que são onde erro de um no
  `+ ML_SLOT_MIN` aparece; mais a garantia de que time com zero NC não sai do
  inverso para índice nenhum — que é justamente a condição que faz o
  **original** escrever fora do vetor.
- **`ForaDaFaixaSaiMenosUm`** — índice negativo, índice igual ao total, e
  `IndiceDoBlocoMl` com time além da tabela.
- **`AlocadorDeBloco`** — `OcupacaoMl` plantado à mão: vetor cheio devolve
  `-1`, o furo devolve o furo, furo em 0 devolve 0, o **último** bloco ainda é
  alcançado, e bloco livre **além** do total não é alocado (a folga do vetor
  existe para contar índice fora da faixa sem atingir vizinho, não para
  alocar). Nenhum desses estados acontece com as duas imagens, por isso o
  golden nunca os veria.

O `CASOS` sem imagem subiu de **7** para **19**, e a asserção do
`test_invariantes_sem_imagem` subiu junto — é ela que impede caso de sumir
calado.

**Problemas encontrados:**

O `Format` de um argumento só não compila (`Wrong number of parameters`): em
FPC ele exige o array de const. Era string constante disfarçada de `Format`.

O teste de mutação pedido pela verificação foi feito: com
`slot := indice - corrido + ML_SLOT_MIN - 1` plantado na
`ParDoIndiceLinearMl`, **três** casos novos reprovam —
`ida e volta fecha em todo bloco valido` (`(0,23) -> 0 -> (0,22)`),
`o primeiro slot de um time volta igual` e `o ultimo slot de um time volta
igual`. A unidade foi restaurada; `git diff` de `we2002_ml.pas` vazio.

O espelho em Python do inverso ficou de fora, e a CORR já o marcava opcional:
o `conta_ml.py` leria a **mesma** tabela do `.exe` que o Pascal usa, então o
confronto não seria de implementações independentes — a ida e volta em Pascal
cobre o que importa.

**Arquivos criados/modificados:**

- `wte/tests/test_ml.pas`
- `wte/tools/test_conta_ml.py`
