---
id: CORR-WTE-138
title: "Correção: os ids 69 e 86 do item 2 da §8.8 estão marcados sem terem sido medidos"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-138: dois dos ids sem bandeira própria nunca foram à tela

## Problema identificado

O item 2 da §8.8 é "Time sem bandeira própria (**57..63, 69, 86** e o 56) →
caixas desabilitadas e import/export recusado", marcado `[x]` no inventário e
na [PAR-TASK-07](/docs/tasks/concluidos/PAR-TASK-07.md).

A evidência registrada cobre **56** (onde os dois lados divergem, como previsto)
e **57..63** (onde concordam). Sobre **69** e **86** não há uma linha — nem
captura, nem veredito, nem menção.

E eles não são mais do mesmo: 57..63 e 56 são seleções/all-star, tratados pelo
primeiro ramo do `OnButtgraf`; **69 e 86 são clubes de Master League**, abertos
pelo **segundo** ramo, que lê de `squad_ml[id-64]` em vez de
`squad_nazall[id-1]`:

```cpp
// legacy/mfc/edDlg.cpp, OnButtgraf
if(id>0 && id<64)   { ... squad_nazall[id-1] ... }
if(id>63 && id<96)  { ... squad_ml[id-64] ... }
```

O port faz o mesmo em [`src/app/Commands.cpp:65`](../../../src/app/Commands.cpp),
com `db_.teams[id-1]` e `db_.ml_teams[id-64]`. Medir 57..63 não exercita esse
segundo caminho, e é justamente por ele que 69 e 86 passam.

## Evidência

A §8.8 do inventário, na íntegra do que diz sobre este item:

```text
> No id 56 (World All-Stars) o port desabilita as caixas de cor e o ed.exe as
> habilita -- capturado nos dois. [...] Nos ids 57..63 os dois lados concordam
> (ambos desabilitam), e o export é recusado com a mesma mensagem em ambos
```

Nada sobre 69 nem 86, nas duas metades do item (caixas desabilitadas; export
recusado).

O que **está** verificado por leitura, e por isso a expectativa é de acordo, não
de divergência — as duas guardas do original excluem os dois ids, e a do port
também:

```cpp
// legacy/mfc/graf.cpp:271   (OnInitDialog, desabilita)
if((id>56 && id<64) || (id == 69 || id == 86))
// legacy/mfc/graf.cpp:681   (import/export, recusa)
if(id>0 && id != 69 && id != 86 && (id<56 || id>63))
// src/app/FlagKitDialog.cpp:118  (o teste único do port)
return team_id_ > 0 && team_id_ != 69 && team_id_ != 86 &&
       (team_id_ < 56 || team_id_ > 63);
```

Concordância esperada não é medição — é a hipótese que o item existia para
testar.

## Causa raiz

O item foi fechado com as duas metades medidas nos ids que o `8.8-prelude.sh`
alcança com poucos `Down` (`PAR_TEAM`), e os dois ids de Master League ficaram
de fora sem que a lacuna fosse registrada.

## Correção

Medir os dois, com `PAR_TEAM=69` e `PAR_TEAM=86`, nas duas metades:

1. **Caixas desabilitadas** — captura dos dois lados, como foi feito para o 56 e
   para 57..63.
2. **Export recusado** — clicar `CMD_EXPORT_FLAG` e conferir que os dois lados
   recusam com `Choose a team (that has "indipendent" flag too) !` e não geram
   arquivo.

Se algum dos dois divergir, é achado e vira CORR nova. Se concordarem — o
esperado —, o item passa a dizer quais ids foram medidos, em vez de listar ids
que não foram.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PARIDADE-FUNCIONAL.md` | modificar — item 2 da §8.8 |
| `docs/tasks/concluidos/PAR-TASK-07.md` | modificar — o Log do item 2 |

## Verificação

- [x] `PAR_TEAM=69` e `PAR_TEAM=86` medidos nos dois lados, com veredito escrito
- [x] O item 2 nomeia os ids efetivamente medidos
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-31

**Resumo do que foi feito:**

Medidos os dois ids, nas duas metades, nos dois lados — duas corridas de
`golden_check.sh` em modo `gui`, uma por id, cada uma exercitando os dois lados
e produzindo captura de cada um.

**Concordam, que era a hipótese.** Caixas de cor desabilitadas em ambos os lados
nos dois ids, com `Style` 54 no 69 e 56 no 86 — o mesmo valor dos dois lados, e
os valores das duas camisas também iguais. `CMD_EXPORT_FLAG` recusado em ambos:
nenhum diálogo de arquivo abre, e sobe a caixa
`Choose a team (that has "indipendent" flag too) !`. Golden `OK` nas duas
corridas.

O estímulo ficou versionado em `tools/par/8.8-sem-bandeira.sh`, com o id em
`PAR_TEAM` — pela mesma razão da [CORR-WTE-123](/docs/tasks/concluidos/CORR-WTE-123.md):
verde sem estímulo versionado não é repetível.

**Problemas encontrados:**

Nenhum na medição. O roteiro nasceu com as três lições que a
[CORR-WTE-137](/docs/tasks/concluidos/CORR-WTE-137.md) tinha acabado de pagar — dispensar
aviso com o ponteiro sobre ele, teclar uma vez e esperar, e fechar o
`FlagKitDialog` no fim —, e por isso saiu certo na primeira corrida.

Vale registrar o que este roteiro **não** afirma: ele não grava nada, então os
dois lados saem `IDENTICAL` contra a imagem original a menos das
não-idempotências. Aqui isso é o resultado certo, e não um falso verde, porque o
que se mede é justamente que nada foi exportado nem alterado — o veredito vem da
tela e da ausência do diálogo de arquivo, não da imagem.

**Arquivos criados/modificados:**

| Arquivo | O quê |
|---|---|
| `tools/par/8.8-sem-bandeira.sh` | criado — o estímulo, parametrizado por `PAR_TEAM` |
| `docs/PARIDADE-FUNCIONAL.md` | o item 2 da §8.8, com os dois ids e o porquê de serem outro caminho |
| `docs/tasks/concluidos/PAR-TASK-07.md` | nota posterior no Log |
