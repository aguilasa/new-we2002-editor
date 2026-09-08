---
id: CORR-MCR-020
title: "Correção: um cobrador ou capitão fora do onze aparece na tela como 10, calado — o núcleo preserva o byte e a janela mostra outro"
type: correção
category: ui
status: concluído
depends_on: []
---

# CORR-MCR-020: o único lugar deste port que normaliza um valor em silêncio

## Problema identificado

A MCR-TASK-13 fixou o domínio dos cinco cobradores e do capitão em `0..10` — a
posição no onze inicial —, e a tela passou a oferecer isso:

```python
            spin.setRange(0, STARTERS - 1)      # ui/formation_view.py:283
        self.captain.setRange(0, STARTERS - 1)  # ui/formation_view.py:291
```

A divisão está **certa**: o núcleo valida byte (`0..255`) e preserva o que
achar, e o `0..10` é constrangimento de tela. O que falta é o que este ciclo faz
em todos os outros lugares da mesma classe — **dizer** que o valor não cabe, em
vez de mostrar outro:

- `domains.label()` devolve `UNNAMED` (`"?"`) para índice em faixa e sem nome, e
  **levanta** só fora de faixa — a MCR-TASK-11 escreveu em letras que "a tela
  precisa distinguir as duas coisas, senão um cartão legítimo vira erro";
- as duas cópias do dorsal em desacordo são **reportadas**, nunca reconciliadas
  (§1.5), porque reconciliar queimaria o melhor tripwire do port;
- o `formation.write` recusa papel fora da faixa **nomeando o byte armazenado**,
  desde a MCR-TASK-09.

Aqui não: um `QSpinBox` com máximo 10 recebendo 15 mostra **10**, sem rótulo,
sem tooltip, sem cor. A legenda ao lado diz "as positions in the starting 11
(0..10)" — declara o domínio, não que o cartão aberto está fora dele.

E o domínio, ao contrário dos rótulos, vem da **grade do editor de terceiro**
(`malla2`, seis colunas por onze linhas em `wte/re/zonas.md`), não do formato.
O experimento desta task produziu `0..5`; nada mediu o teto. Um cartão de outra
release, ou gravado por outra ferramenta, pode legitimamente cair fora.

## Evidência

Cópia da fixture com dois valores fora do onze — o `cmp` prova que o núcleo os
atravessa intactos:

```
$ # plantados numa cópia: CAPTAIN=15, kicker0=19
$ python3 tools/mcr/mcrio.py <cópia> --roundtrip
form 1: 0 byte(s) differ
form 2: 0 byte(s) differ
```

Abrindo essa cópia na janela:

```
model after the screen loaded it:  captain=15 kickers=[19, 7, 8, 7, 7]
captain spin shows: 10   kicker0 spin shows: 10
```

E o `Save` sobre ela devolve o arquivo **idêntico** — o valor não se perde:

```
$ cmp <cópia> <gravado pela tela>      # sem saída: iguais
captain: 15  kickers: [19, 7, 8, 7, 7]
```

Ou seja: **o dado está seguro e a tela mente sobre ele.** A captura da aba
Formation dessa cópia mostra `SF 10` e `CP 10` onde o cartão guarda 19 e 15,
sem nada dizendo que houve corte.

O caminho em que o valor **se perde** existe e é curto: mexer na seta de
qualquer uma das seis caixas dispara `valueChanged` a partir do 10 recortado, e
aí o 19 vira 10 ou 11. É edição do usuário, não gravação silenciosa — mas ele
edita a partir de um número que não é o do cartão.

## Causa raiz

O recorte do `QSpinBox` é usado como se fosse validação, e um widget que
recorta não tem como distinguir "o cartão diz 10" de "o cartão diz 15 e eu não
sei mostrar".

## Correção

### Arquivo: `tools/mcr/ui/formation_view.py`

Duas escolhas, e qualquer uma serve desde que a tela pare de calar:

1. **Alargar e marcar.** `setRange(0, 0xFF)`, que é o que o núcleo aceita, e
   pintar/rotular o valor quando ele sai de `0..10` — um sufixo no
   `setSuffix()` ou um `setToolTip` dizendo "outside the starting 11; the card
   holds this, and the upstream's grid only offers 0..10". Mantém o domínio
   medido como **orientação** e o cartão como verdade.
2. **Manter `0..10` e recusar-se a fingir.** Detectar na carga que o valor não
   cabe, desabilitar as seis caixas e mostrar o número real num rótulo ao lado,
   com a razão — a mesma forma que o `_open_byte` usava antes deste veredito.

A primeira é mais barata e mais fiel ao resto do port, que **mostra e anota** em
vez de esconder.

### A legenda

Acrescentar de onde vem o `0..10`: a grade `malla2` do editor de terceiro, seis
colunas por onze linhas, e não o formato. É a mesma ressalva que a linha ao lado
já faz sobre os nomes de papel.

### O caso vermelho

Registrar em `controls.py`, ou como passo do `ui_check.py`: abrir uma cópia com
`CAPTAIN=15`, exigir que a tela **relate** 15 — no valor ou no rótulo — e não
10. Sem ele o conserto não fica exercitado, e este é um defeito que só aparece
com um cartão que ninguém tem à mão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/ui/formation_view.py` | modificar |
| `tools/mcr/ui_check.py` ou `tools/mcr/controls.py` | modificar (o caso vermelho) |
| `docs/tasks/port-mcr/13-oraculo-e-veredito.md` | modificar (a contagem de controles, se mudar) |

## Verificação

- [x] com uma cópia da fixture em que `CAPTAIN=15` e `kicker0=19`, a aba
      Formation **mostra 15 e 19**, ou diz que não os mostra e por quê
- [x] a cópia gravada pela tela continua `cmp`-idêntica à de entrada quando
      nada foi editado
- [x] o caso vermelho: com o conserto revertido, o passo novo fica vermelho
- [x] `python3 tools/mcr/mcrio.py <cópia> --roundtrip` = 0 bytes nas duas formas
- [x] `WE2002_MCR_CARD=… ctest -R mcr` = **3 de 3**; `make test` verde
- [x] `python3 tools/mcr/controls.py` todos vermelhos
- [x] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

O sintoma reproduziu exato. Numa cópia da fixture com `captain=15` e
`kickers[0]=19`, o round-trip dá **0 bytes nas duas formas** — o núcleo
atravessa os dois intactos — e a `FormationView` carregada com ela mostrava
`captain=10 kicker0=10`, com `toolTip()` e `suffix()` **vazios**.

Foi a **opção 1** da CORR, alargar e marcar, que é a que o resto do port já
segue. As seis caixas passaram a `0..0xFF`, que é o que o núcleo aceita, e um
valor fora de `0..10` ganha um **sufixo visível** — `(outside the 11)` — mais um
tooltip que diz quanto o cartão guarda, de onde vem o domínio e por que o
cartão pode legitimamente estar fora dele. O `_clamped` virou `_show`/`_mark`:
o `_mark` é o que os dois `_commit_*` chamam quando o usuário edita, para a
marca sumir ao voltar para dentro sem reentrar no `valueChanged`.

A legenda passou a dizer de onde vem o `0..10` — a grade do editor de terceiro,
seis colunas por onze linhas — e que o campo é um byte, como a linha ao lado já
faz sobre os nomes de papel.

**O caso vermelho ficou no `ui_check.py`**, ao lado dos dois que já moram lá:
o motor do `controls.py` roda `<módulo>.py --self-check` sem Qt, e quem pega
este defeito precisa de PySide6, do venv e de display — a mesma razão da
[CORR-MCR-018](/docs/tasks/port-mcr/CORR-MCR-018.md). O `app.py` ganhou
`--report-formation`, que abre o cartão e reporta **o que as seis caixas
mostram** (valor, sufixo e tooltip) ao lado do que o cartão guarda; o
`ui_check.py` ganhou `outside_probe`, que planta os dois valores numa cópia,
exige que ela passe no round-trip **antes** de olhar a tela — senão estaria
medindo o núcleo — e julga.

**Problemas encontrados:**

**1. O meu primeiro juiz aceitava o tooltip, e com isso a primeira quebra saiu
verde.** A regra é "mostra ou nomeia", e eu tinha escrito "nomeia" como
"sufixo **ou** tooltip". Repondo o teto em `0..10`, a caixa lê 10 e o tooltip
continua dizendo "The card holds 15" — e o juiz chamava isso de aprovação. Um
tooltip **não é exibição**: ele custa um passar de mouse que ninguém faz sobre
um número que parece comum, e o número que parece comum é justamente a falha. O
juiz passou a exigir **sufixo**; o tooltip viaja junto e é impresso na queixa,
como diagnóstico e nunca como resposta. Com isso as duas quebras ficam
vermelhas.

**2. A segunda quebra que eu escolhera não media nada.** Era apagar o sufixo, e
com a caixa larga o número exibido continua sendo o do cartão — honesto pela
regra. Ela só passou a valer depois da correção acima, que exige marca visível
também quando o número está certo mas fora do domínio. As duas ficaram: repor o
teto, e apagar a marca.

**3. `STARTERS` não existia no `ui_check.py`, e ele não pode importar a
`ui/`** — precisaria de PySide6. Em vez de repetir o `11`, ele o **deriva**:
`layout.OUTFIELD_COUNT + 1`, os dez que a formação carrega X e Y mais o
goleiro, que é a razão de a grade ter onze linhas.

**4. `--tab 2` não é a aba Formation.** São duas abas; a Formation é a **1**. A
primeira captura saiu na Players sem erro nenhum — o índice fora de faixa é
ignorado em silêncio pelo `QTabWidget`.

**Medições:**

| gate | número |
|---|---|
| a cópia plantada, round-trip | form 1 e form 2, **0 byte(s) differ** |
| a tela, antes | `captain=10 kicker0=10`, sufixo `''`, tooltip `''` |
| a tela, depois | `captain=15 kicker0=19`, sufixo `'  (outside the 11)'` nos dois; os outros quatro cobradores sem marca |
| a fixture na mesma tela | `captain=8 kicker0=7`, sufixo `''` — nada marcado |
| editar de volta para dentro | valor 4, sufixo `''`, modelo 4 |
| abrir e gravar sem editar | `cmp` **idêntico**; relido, `captain=15 kickers=[19, 7, 8, 7, 7]` |
| captura da aba Formation | `SF 19 (outside the 11)` e `CP 15 (outside the 11)` |
| o caso vermelho | **2 de 2**: repor o teto → "shows 10, with no visible label naming 15"; apagar a marca → "shows it with no visible mark" |
| os dois controles antigos do `ui_check` | continuam vermelhos (`to_card_x`, `to_card_y`) |
| `ui_check.py` | `rc=0` |
| `controls.py` | **20 de 20 vermelhos (19 substitutions, 1 new file)** — inalterado, o caso novo não mora lá |
| `selftest.py` | `0 failure(s)` sobre 12 módulos |
| `glossary.py` / `layout.py --rule1` | **0** queixas / **0** endereços |
| `ctest -R mcr` | **3 de 3** |
| `make test` | **10/10** |
| `check_tasks.py` / `ctest -R tasks` | `100 task(s), ok` / **1/1** |
| fixture / `roms/` | `sha256 e53f4895…c47546`, intocada; `roms/` sem alteração |

**Arquivos criados/modificados:**

- `tools/mcr/ui/formation_view.py` — `BYTE_MAX`, `OUTSIDE_SUFFIX`, `_show` e
  `_mark` no lugar do `_clamped`, a marca nos dois `_commit_*`, o título do
  grupo e a legenda
- `tools/mcr/ui/app.py` — `--report-formation` e `report_formation()`
- `tools/mcr/ui_check.py` — `_sandbox` extraído, `outside_probe`,
  `_judge_formation`, `_plant_outside`, `OUTSIDE_BREAKS` e `STARTERS` derivado
- `tools/mcr/controls.py` — a nota do que **não** mora lá passou a citar os dois
  casos (varredura)
- `docs/prompts/perfil-mcr.md` — a linha do `mcr_ui`: quatro controles, e o
  passo novo
- `docs/tasks/port-mcr/13-oraculo-e-veredito.md` — o `0..10` como orientação, e
  o `ui_check` plantando quatro
