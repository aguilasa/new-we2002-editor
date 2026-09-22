---
id: CORR-LOOKS-076
title: "O primeiro critério marca um --screen que não foi rodado"
origin: LOOKS-TASK-38
severity: medium
files: [docs/tasks/looks/38-o-alinhamento-dos-valores.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-22
done_commit: be3df6bb
---

# CORR-LOOKS-076 — O primeiro critério marca um --screen que não foi rodado

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

O primeiro critério de conclusão da LOOKS-TASK-38 termina em "`--screen` remede
com 0 diferença" e está marcado `[x]`, enquanto os "Problemas encontrados" da
própria task dizem que a remedição não foi rodada ("seriam mais 19 min"). O
critério foi marcado com base no `--write` mais o `--keys`, não no check que ele
nomeia.

O revisor rodou o `--screen`: dá **0 diferença**, o que também descarta edição à
mão da tabela gerada. Falta a transcrição no arquivo.

## Evidência

```text
$ sed -n '45,47p;184,187p' docs/tasks/looks/38-o-alinhamento-dos-valores.md
- [x] O gerador grava a caixa (x, largura) e o modo de alinhamento de cada
      objeto de texto; `screen.py --check` confere, e `--screen` remede com 0 diferença.
- **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado** (seriam mais 19 min).

$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/oracle.py --screen
  screen measured in 1197s
oracle --screen: 0 difference(s) from screen.json
```

## Causa raiz

O custo da corrida (~20 min) foi trocado pela marcação. O critério está de fato
satisfeito.

## Correção

Colar a transcrição do `--screen` no bloco de Evidência e tirar o terceiro
marcador de "Problemas encontrados". Sem mudança de código.

## Arquivos

- docs/tasks/looks/38-o-alinhamento-dos-valores.md

## Verificação

`python tools/looks/oracle.py --screen` imprime `0 difference(s) from
screen.json`, e a linha aparece na Evidência da task.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22: **reproduzida**.

```text
45: - [x] O gerador grava a caixa (x, largura) e o modo de alinhamento de cada
46:       objeto de texto; `screen.py --check` confere, e `--screen` remede com
47:       0 diferença.
184: - **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado**
185:   (seriam mais 19 min). ...

$ python tools/looks/oracle.py --screen
  screen measured in 1190s
  the arrows' CLUT, read off the list: < (80,497), > (80,497)
oracle --screen: 0 difference(s) from screen.json      (saída 0, 19 min 54 s de relógio)
```

**Executado em:** 2026-09-22 — só prosa, num arquivo só.

A transcrição da triagem entrou no bloco de Evidência da task, logo abaixo do
`--screen --write` que ela remede, onde ficam as outras transcrições do
primeiro critério. **O `--screen` não foi rodado de novo aqui**: a medição da
triagem é de hoje, sobre o mesmo `screen.json` do HEAD, e repeti-la custaria
outros 20 min para reimprimir a mesma linha.

O marcador de "Problemas encontrados" não foi apagado — o que ele conta
*aconteceu*, e o custo evitado é o motivo de a task ter fechado assim. Ele foi
reescrito para dizer **de que corrida** fala ("na corrida desta task") e para
apontar a remedição posterior, de modo que o `[x]` e o corpo do arquivo digam a
mesma coisa:

```diff
-- **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado**
-  (seriam mais 19 min). O `screen.validate` fechou no gerador — ...
+- **O `--screen` não foi re-rodado na corrida desta task** (seriam mais 19
+  min). O `screen.validate` fechou no gerador — ... A remedição foi rodada
+  depois, na [`CORR-LOOKS-076`](/docs/tasks/looks/CORR-LOOKS-076.md)
+  (2026-09-22): **0 diferença**, transcrita na Evidência acima.
```

Varredura: `re-rodado` e `CORR-LOOKS-076` em `docs/`, `CLAUDE.md` e
`rite.toml`. O mesmo marcador existe na
[`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md) e na
[`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md), e ali ele
**continua certo**: nenhuma das duas tem critério que prometa o `--screen`, e
o `screen.json` que a triagem remediu é o da 38, que reescreveu o das duas.
Nada a mudar nelas.

### Gates

```text
$ sh <rite> check --quick --cycle looks
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```
- **Closed** — commit `be3df6bb` (2026-09-22): docs(looks): paste the --screen remeasurement into task 38's evidence
  - Files (`git show --name-status be3df6bb`):
    - `M docs/tasks/looks/38-o-alinhamento-dos-valores.md`
    - `M docs/tasks/looks/CORR-LOOKS-076.md`
