---
id: CORR-WTE-066
title: "Correção: a tabela de endereços atropelados lista um que nunca é alcançado e esconde o quarto"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-066: `0x004335f4` é atropelado e não aparece em lugar nenhum

## Problema identificado

`wte/re/ml-slots.md`, seção *"Escrita fora do vetor, e a causa do travamento
da ROM europeia"*, apresenta uma tabela sob a frase **"Os enderecos alcancados
sao dados vivos"**:

| indice | endereco | o que mora la |
|---|---|---|
| 462 | `0x004335c0` | o proprio contador |
| 480 | `0x004335e4` | o ponteiro de time da rotina de realce |
| 512, 514 | `0x00433624`, `0x00433628` | vizinhos do mesmo bloco |

A tabela é escrita à mão dentro do `gera_md()` do `conta_ml.py` (linhas
233-236), e a mesma ferramenta **mede** quais índices de fato são alcançados.
Os dois não batem em dois pontos:

1. **O índice 462 não é alcançado** em nenhuma das duas imagens. Ele é
   alcançável em tese; a tabela o lista sob "alcançados".
2. **`0x004335f4` (índices 488 e 489) é alcançado** na europeia, e não está na
   tabela, nem em `crash-causa.md`, nem em nenhum outro arquivo do repositório.

O segundo é o que importa: `crash-causa.md` mediu **três** DWORDs mudando de
`0x0` para `0x00010001`, e a WTE-TASK-33 os nomeou como consequência do `inc`
de `0x0040435d`. O modelo da própria ferramenta prevê **quatro**. Ou o dump
daquela medição estava recortado, ou o quarto endereço não é escrito ao vivo —
e nenhuma das duas hipóteses está registrada.

## Evidência

Os oito índices que a `conta_ml.conta()` reporta em `fora` para a europeia, com
o endereço de cada um (`0x00433224 + 2*i`) e o par que o produziu:

```text
  480 0x4335e4 [(637, 20, 189)]
  481 0x4335e6 [(656, 21, 190)]
  488 0x4335f4 [(267, 43, 121)]     <== ausente de toda a documentação
  489 0x4335f6 [(269, 43, 122)]
  512 0x433624 [(659, 21, 221)]
  513 0x433626 [(660, 21, 222)]
  514 0x433628 [(663, 21, 223)]
  515 0x43362a [(666, 21, 224)]
```

Agrupados por DWORD, que é a granularidade em que `crash-causa.md` lê:

| DWORD | índices | aparece em `crash-causa.md` |
|---|---|:-:|
| `0x004335e4` | 480, 481 | sim |
| `0x004335f4` | 488, 489 | **não** |
| `0x00433624` | 512, 513 | sim |
| `0x00433628` | 514, 515 | sim |

O `fora_do_vetor` do `ml-slots-medido.tsv` já diz `8` para a europeia — a
tabela de três linhas ao lado dele não fecha com esse 8, e o leitor não tem
como reconciliar.

Índice 462 (`0x004335c0`) não aparece na lista medida de nenhuma das duas
imagens.

```text
grep -rn '4335f4\|4335f6' wte/ docs/     # nenhuma ocorrência
```

## Causa raiz

A tabela de endereços é literal dentro do gerador, escrita a partir dos três
endereços que `crash-causa.md` já trazia, em vez de sair da medição que o
próprio `conta_ml.py` faz.

## Correção

### Arquivo: `wte/tools/conta_ml.py`

A tabela de "endereços alcançados" passa a ser **gerada a partir do medido**:
uma linha por índice de `fora`, com endereço, o par `(time, slot)` que o
produziu e a imagem em que foi visto. Para isso o `--medir` precisa guardar os
índices, não só a contagem — coluna nova no `ml-slots-medido.tsv`, ou um
`ml-slots-fora.tsv` ao lado.

O índice 462 sai da tabela de alcançados e vira uma frase à parte: é o primeiro
endereço depois do vetor, e é o contador — alcançável, não alcançado.

### Arquivo: `wte/re/crash-causa.md` (ou o texto novo de `ml-slots.md`)

Registrar a divergência entre modelo e medição ao vivo: quatro DWORDs previstos,
três observados. Dizer qual das duas hipóteses vale — dump recortado, ou
`0x004335f4` não escrito ao vivo — e, se ficar sem medir, deixar como **pergunta
aberta nomeada**, não como silêncio. Se o dump for refeito, `0x004335f4` é o
endereço a olhar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/conta_ml.py` | modificar |
| `wte/re/ml-slots.md` | modificar (via gerador) |
| `wte/re/ml-slots-medido.tsv` | modificar (via `--medir`) |
| `wte/re/crash-causa.md` | modificar |

## Verificação

- [x] `wte/re/ml-slots.md` lista os oito índices medidos, `0x004335f4`
      inclusive, e não lista 462 como alcançado
- [x] `python3 wte/tools/conta_ml.py --check` verde
- [x] `cd wte/tools && python3 -m unittest test_conta_ml` verde
- [x] `make -C wte check` rc 0
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-19

**Resumo do que foi feito:**

O `--medir` passou a escrever uma segunda medição, `wte/re/ml-slots-fora.tsv`,
com uma linha por índice alcançado fora do vetor — imagem, índice, endereço, o
par que o produziu, `b0` e `b1`. A tabela de endereços atropelados do
`ml-slots.md` sai dela, e não mais literal do `gera_md()`: são os oito índices
da europeia, `0x004335f4` inclusive. O índice 462 saiu da tabela e virou frase
à parte — é o primeiro endereço depois do vetor e o alvo mais óbvio, e
justamente por isso importa dizer que é **alcançável e não alcançado**.

A divergência entre modelo e medição ao vivo ficou registrada nos dois lados: o
gerador confronta os DWORDs medidos com a constante `CRASH_DWORDS` (os três que
o `crash-causa.md` viu) e emite a seção "Pergunta aberta: `0x004335f4`"
sozinho; o `crash-causa.md` ganhou o item correspondente em "O que não foi
respondido", com os pares 267 e 269 que produzem o endereço, para quem refizer
o dump saber onde olhar.

**Problemas encontrados:**

A medição de `work/ml-eu.bin` só vale para a pergunta se a cópia for fiel: o
oráculo altera a imagem ao abri-la, e foi assim que a japonesa perdeu um bloco
livre. Conferido por leitura pura — a região de vínculo (`OFS_LINK_ML`, 760
pares mais folga de setor) é byte a byte igual à de `roms/golden-european-deluxe.bin`.
Sem isso a divergência de quatro contra três poderia ser artefato da cópia.

Não há dump de `.data` guardado em disco daquela sessão, então responder qual
das duas hipóteses vale exigiria refazer a corrida sob Wine no `:99` — trabalho
de outra invocação. Ficou como pergunta nomeada, que é o que a correção pedia.

**Resolvida em 2026-08-20**, a pedido: a corrida foi refeita com
`python3 wte/tools/sonda_dorsal.py wte/tests/roteiros/08-so-troca-de-time.txt
--vizinhanca`, sobre cópia nova da europeia, e o dump traz
`0x004335f4  0x0 -> 0x00010001` no **mesmo** bloco dos outros três. Vale a
primeira hipótese: a transcrição de 2026-08-11 é que saiu com três linhas — a
janela do `--vizinhanca` é `0x00433580 + 0xc0` e sempre alcançou o endereço.
`CRASH_DWORDS` passou a ter os quatro, e o gerador troca a seção "pergunta
aberta" por uma frase de concordância que ele mesmo confere.

A varredura puxou dois sítios que a lista da CORR não previa: a
`wte/tools/README.md`, que descrevia as saídas do `--medir`, e a WTE-TASK-33,
que afirmava "os índices 480, 512 e 514 caem exatamente naqueles três
endereços" — a mesma omissão do `0x004335f4`, em outro arquivo.

**Arquivos criados/modificados:**

- `wte/tools/conta_ml.py`
- `wte/re/ml-slots-fora.tsv` (criado, via `--medir`; o
  `ml-slots-medido.tsv` foi reescrito pela mesma corrida e saiu
  byte a byte igual)
- `wte/re/ml-slots.md` (via gerador)
- `wte/re/crash-causa.md`
- `wte/tools/README.md`
- `docs/tasks/33-slots-de-master-league.md`
