---
id: CORR-LOOKS-060
title: "Correção: \"todos os outros ficam abaixo de 2,3x\" — a corrida imprime 2,5x na cabeça do slot 2"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-LOOKS-060: o limiar que separa junta de não-junta está escrito 0,2 abaixo do medido

## Problema identificado

A [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md) mede a
hierarquia por dispersão: cinco pares se separam do resto, e o resto "não se
separa". O número que delimita o "resto" aparece em quatro lugares — o veredito
da §10.3 (k), o critério de conclusão, o Log da task e a armadilha 45 do perfil
— sempre como **2,3x**:

```text
docs/PLAN-LOOKS-PY.md:2639
>   4,6x) —, e **todos os outros ficam abaixo de 2,3x**, o que é dizer que não
docs/tasks/looks/25-a-pose-de-referencia.md:63,181
docs/prompts/perfil-looks.md:442
```

**A corrida imprime 2,5x.** No slot 2, a `head` não tem mãe e a razão dela é
`2.5x`; é o maior "outro" das duas corridas, e o próprio Log da task diz isso
na transcrição do slot 2 — *"os outros sete abaixo de 2,5x"* —, contradizendo
a frase três linhas acima dele.

O veredito não muda: 2,5x continua sendo "não se separa" contra os 4,6x do
primeiro par de verdade. O que muda é quem for conferir: rodando o comando
hoje, o maior "outro" **viola** o limite que o plano afirma, e a diferença fica
parecendo achado.

## Evidência

Corrida de 2026-09-18, na árvore de `a2d580e`, os dois slots:

```text
$ python tools/looks/oracle.py --poses
  -- slot 1 (goalkeeper) --
      head          child of root          spread     6.3, next torso at 20.6 (3.3x)
      ... (os outros seis: 1,1x a 2,2x)
  -- slot 2 (outfield player) --
      head          no parent              spread     7.9, next torso at 19.7 (2.5x)
      thigh a       no parent              spread    23.9, next forearm b at 43.2 (1.8x)
      thigh b       no parent              spread    28.5, next foot a at 41.9 (1.5x)
      forearm a     no parent              spread    20.7, next torso at 24.0 (1.2x)
      forearm b     no parent              spread    19.2, next root at 23.3 (1.2x)
      foot a        no parent              spread    21.9, next root at 25.1 (1.1x)
      torso         no parent              spread    22.3, next forearm a at 25.2 (1.1x)
oracle --pose: 0 problem(s) over 8 frame(s) and 2 slot(s)
```

`2.5 > 2.3`. As cinco separações verdadeiras reproduzem número a número
(14,5x/14,6x, 10,5x/9,2x, 9,9x/12,8x, 5,3x/4,9x, 5,0x/4,6x), e o pior desvio de
composição também (0,0071 e 0,0015) — o resto do veredito está de pé.

## Causa raiz

O limiar foi escrito olhando o slot 1, onde o maior "outro" é 2,2x, e a linha
do slot 2 (2,5x) entrou na transcrição do Log sem voltar para a frase.

## Correção

### Arquivos: `docs/PLAN-LOOKS-PY.md` (§10.3 (k)), `docs/prompts/perfil-looks.md` (armadilha 45) e `docs/tasks/looks/25-a-pose-de-referencia.md`

Trocar **2,3x** por **2,5x** nos quatro lugares — ou, melhor, dizer o que a
medição separa: *o primeiro par verdadeiro está em 4,6x e o maior dos outros em
2,5x*, que é a folga real e não envelhece se um deles mudar de corrida.

Vale conferir na mesma passada se o número se repete: as duas corridas de
2026-09-18 deram 2,5x no slot 2, então o valor é estável nas duas medições que
existem.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/prompts/perfil-looks.md` | modificar |
| `docs/tasks/looks/25-a-pose-de-referencia.md` | modificar |

## Verificação

- [x] `grep -rn "2,3x" docs/` não acha a afirmação
- [x] o número escrito é o que `oracle.py --poses` imprime como maior "outro"
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-18

### Resumo do que foi feito

A evidência reproduz em `a12d753`: o `--poses` imprime `head … next torso at
19.7 (2.5x)` no slot 2, e quatro documentos afirmavam que todos os outros ficam
abaixo de **2,3x**.

**A conferência mostrou mais do que a CORR previa, e o número sozinho não
bastava.** No slot 1 a linha da `head` diz **3,3x** — e ela não é um "outro":
é o par raiz↔cabeça visto do outro lado, o mesmo que a linha da `root` mede em
14,5x. Trocar 2,3 por 2,5 deixaria a frase falsa de novo, agora pelo slot 1.

Por isso a frase passou a delimitar o conjunto: **nenhuma linha fora dos cinco
pares passa de 2,5x** — 2,2x no slot 1, 2,5x no slot 2, na cabeça, cuja melhor
candidata própria é o tronco enquanto o par verdadeiro a nomeia do lado da
raiz. A folga do veredito fica dita como ela é: **4,6x contra 2,5x**.

Corrigido nos quatro lugares, cada um com a data e o que dizia antes: §10.3 (k)
do plano, armadilha 48 do perfil, critério de conclusão e Log da LOOKS-TASK-25,
mais a linha da Fase 9 do `progresso.md`, que a CORR não listava e repetia a
mesma frase.

### Gates

```text
$ python tools/looks/oracle.py --poses            # 2026-09-18, os dois slots
  -- slot 1 (goalkeeper) --
      head          child of root    spread  6.3, next torso at 20.6 (3.3x)
      thigh a       no parent        spread 25.0, next forearm b at 55.7 (2.2x)
      ... (as outras cinco linhas fora dos pares: 1,1x a 1,7x)
  -- slot 2 (outfield player) --
      head          no parent        spread  7.9, next torso at 19.7 (2.5x)
      ... (as outras seis: 1,1x a 1,8x)
oracle --pose: 0 problem(s) over 8 frame(s) and 2 slot(s)
```

As cinco separações reproduzem número a número — 14,5x/14,6x, 10,5x/9,2x,
9,9x/12,8x, 5,3x/4,9x e 5,0x/4,6x.

```text
$ grep -rn "2,3x" docs tools
docs/PLAN-LOOKS-PY.md:2643      # o registro datado
docs/prompts/perfil-looks.md:443 # idem
                                 # mais a tabela de correções, que nomeia o erro
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
$ python tools/looks/selftest.py --quiet
  ..... 78 of 78 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada (leitura pura); os dois states só carregados; nenhum
DuckStation de pé no fim. As capturas de pose caem em `work/looks-pose/`, em
JSON de alguns KB — nenhuma cópia de imagem.

### Problemas encontrados

- A CORR aponta a armadilha **45** do perfil; ela é a **48** hoje — o arquivo
  ganhou três armadilhas entre a revisão e esta execução. Achada pelo texto,
  não pelo número.

### Arquivos criados/modificados

- `docs/PLAN-LOOKS-PY.md` §10.3 (k)
- `docs/prompts/perfil-looks.md` — armadilha 48
- `docs/tasks/looks/25-a-pose-de-referencia.md` — critério e Log
- `docs/tasks/looks/progresso.md` — a linha da Fase 9
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
