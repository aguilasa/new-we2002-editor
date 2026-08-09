---
id: CORR-WTE-018
title: "Correção: o `02-revisar.md` cita ~430, 70 e 197 como “o que já está no plano”, e o plano não diz mais isso"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-018: o prompt de revisão dá exemplo com três números aposentados

## Problema identificado

A etapa 2 do [`02-revisar.md`](/docs/prompts/02-revisar.md) manda remedir toda
contagem que a task afirma, e dá a lista de exemplos (linha 88):

```
**Contagens que a task afirma se remede, não se relê.** Exemplos do que já está
no plano e pode ter mudado: 18 formulários, ~430 componentes, 96 handlers, 19 de
69 offsets, 70 strings com padding, 13 unidades, 197 bitmaps.
```

A frase promete "o que já está no plano". Depois da WTE-TASK-09 o plano diz
outra coisa em três dos sete: componentes são **441**, strings com enchimento em
`.data` são **13**, bitmaps são **198**. Os outros quatro batem.

O efeito não é decorativo. Quem revisa lê essa linha como o valor de referência
e reprova uma task correta por discordar dela — foi exatamente o modo de falha
que a [CORR-WTE-006](/docs/tasks/CORR-WTE-006.md) descreveu quando o mesmo
arquivo pedia `FormCreate` 17 vezes.

**Por que a guarda não pega.** O `check_fase1.py` exclui `docs/prompts/` do
perímetro por decisão registrada — gabarito, com destino de exemplo. A decisão
está certa para o **destino de link**; ela não cobre número de referência
afirmado em prosa. A [CORR-WTE-016](/docs/tasks/CORR-WTE-016.md) alargou o
perímetro para `wte/` e deixou `docs/prompts/` como estava, porque o sítio dela
era outro.

## Evidência

```
$ sed -n '86,88p' docs/prompts/02-revisar.md
**Contagens que a task afirma se remede, não se relê.** Exemplos do que já está
no plano e pode ter mudado: 18 formulários, ~430 componentes, 96 handlers, 19 de
69 offsets, 70 strings com padding, 13 unidades, 197 bitmaps.
```

Contra a §5 do [`fase-1.md`](../../wte/re/fase-1.md), que é o quadro de
reconciliação gerado:

```
| ~430 componentes        | 441 | **corrigido** |
| 70 strings com padding  |  13 | **corrigido** |
| 197 bitmaps             | 198 | **corrigido** |
```

E a guarda verde ao lado, provando que ela não alcança o arquivo:

```
$ python3 wte/tools/check_fase1.py --check
1 arquivo em dia com os produtos da fase 1 + we-team-editor/we-team-editor.exe;
0 sitio com numero velho
```

## Causa raiz

`docs/prompts/` saiu do perímetro por causa dos **destinos de exemplo**
(`/docs/tasks/CORR-WTE-XXX.md`, `XX-nome-do-arquivo.md`), que são placeholder e
não podem ser conferidos. Número de referência citado em prosa entrou de carona
nessa exclusão, e é conteúdo de outra natureza: ele envelhece igual ao do plano.

## Correção

### Arquivo: `docs/prompts/02-revisar.md`

Trocar a lista pelos valores medidos, e apontar de onde eles saem, para que a
próxima reconciliação tenha um sítio a menos:

```markdown
**Contagens que a task afirma se remede, não se relê.** Os valores correntes
estão na §5 de [`wte/re/fase-1.md`](../../wte/re/fase-1.md), que é gerada — não
os copie para cá. Exemplos do que já mudou uma vez: componentes (`~430` → 441),
strings com enchimento (70 → 13), bitmaps (197 → 198).
```

Citar o número velho **ao lado do novo**, como história, é o que mantém a linha
útil sem transformá-la em sítio: é a mesma forma que a CORR-WTE-016 deu ao bloco
do `wte/README.md`.

### Arquivo: `wte/tools/check_fase1.py`

Decidir e registrar o perímetro de `docs/prompts/`. Duas rotas, e a escolha é do
executor:

1. **manter a exclusão** e escrever no docstring que ela vale para destino de
   link, não para número — deixando o `02-revisar.md` como sítio manual; ou
2. **trazer `docs/prompts/` para dentro**, o que exige conferir se algum outro
   prompt cita número da §1 antes de o `--check` ficar vermelho.

A rota 2 é a que fecha o buraco de vez, e é coerente com o que a CORR-WTE-016
mediu: o perímetro estreito é o que deixa número velho sobreviver. Se ela for
escolhida, a coluna `antes` de `SITIOS` tem de ser remedida de novo, com
`git archive 65cc4be docs wte`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/02-revisar.md` | modificar |
| `wte/tools/check_fase1.py` | modificar (perímetro e/ou docstring) |
| `wte/tools/test_check_fase1.py` | modificar, se a rota 2 for escolhida |
| `wte/re/fase-1.md` | modificar (**pelo gerador**), se o perímetro mudar |

## Verificação

- [ ] O `02-revisar.md` não afirma número da §1 que a §5 do `fase-1.md`
      contradiga
- [ ] `python3 wte/tools/check_fase1.py --check` verde
- [ ] `python3 -m unittest test_check_fase1` verde
- [ ] `make -C wte check` verde de ponta a ponta
- [ ] Se o perímetro mudou, a coluna `antes` de `SITIOS` foi **remedida**, não
      ajustada à mão

## Log de Execução

**Executado em:** 2026-08-09

**Resumo do que foi feito:** Rota **2** — `docs/prompts/` entrou no perímetro do
`check_fase1.py`. A lista de contagens do `02-revisar.md` virou ponteiro para a
§5 do `fase-1.md` (que é gerada) com os quatro pares `velho → corrente` como
história. A coluna `antes` de `SITIOS` foi **remedida** com o perímetro novo
sobre `git archive 65cc4be docs wte`: 10/5/2/5, total 22 (era 9/4/2/4 = 19), e
os três sítios somados são exatamente os do `02-revisar.md`.

**Problemas encontrados:** Um, e ele obrigou a alargar a correção.

A rota 2 e o texto que a própria CORR propõe são **incompatíveis** como
estavam: `bitmaps (197 → 198)` tem o número velho e a palavra de contexto na
mesma linha, então a guarda o acusaria. Descobri isso ao rodar o gerador — ele
apontou a minha linha de exemplo, que dizia literalmente ``escrever `197
bitmaps` dispara``.

O jeito como o repositório escapava disso era **acidente de quebra de linha**:
o bloco que a CORR-WTE-016 escreveu no `wte/README.md` tem o `197` numa linha e
a palavra `bitmap` noutra, e bastaria reflowar o parágrafo para o `--check`
ficar vermelho sem nada ter piorado. Sem resolver isso, a rota 2 tornaria
impossível escrever história em prosa corrida.

Então `_e_historia()` entrou no gerador: linha que escreve `velho → corrente`
(seta ASCII ou Unicode, com marcação entre os dois) diz o que mudou e não
conta; seta para **outro** número continua contando, senão qualquer seta seria
passe livre. `SITIOS` ganhou uma coluna com o valor corrente para isso.

**Arquivos criados/modificados:**

- `docs/prompts/02-revisar.md` (a lista de contagens)
- `wte/tools/check_fase1.py` (perímetro, `_e_historia`, `SITIOS`, docstring e
  a prosa da §6 gerada)
- `wte/tools/test_check_fase1.py` (nova classe `TesteFormaDeHistoria` com 4
  testes, `docs/prompts/` movido para dentro nos testes de perímetro, e
  `test_varrer_acha_residuo_em_prompt`; 24 testes no arquivo, 164 na bateria)
- `wte/re/fase-1.md` (**regenerado**)
- `docs/tasks/progresso.md` (descrição do perímetro — discrepância achada no
  caminho: ela enumerava as exclusões e ficaria incompleta)
