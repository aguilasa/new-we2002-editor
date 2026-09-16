---
id: CORR-LOOKS-046
title: "Correção: um `.refused` velho faz o `--score` pular uma tupla que já desenha, e o gate passa sem julgá-la"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-046: o `confront.run` apaga o PNG velho e deixa a recusa velha

## Problema identificado

O `confront.run` começa renderizando o **nosso** lado de cada tupla. Antes de
renderizar ele apaga o PNG anterior — e **não** apaga o `.refused` anterior:

```python
# tools/looks/confront.py, run()
path = os.path.join(where, "ours-%d-%s.png" % (slot, text))
if os.path.exists(path):
    os.remove(path)
picture, why = render(text, SLOT_FIGURE[slot], path)
if picture is None:
    with open(path + ".refused", "w", encoding="utf-8") as handle:
```

E o `--score` decide pelo `.refused` **primeiro**:

```python
if os.path.exists(path + ".refused"):
    refused[text] = ...          # a tupla sai da matriz
else:
    ours[text] = ui_check.picture(path)
```

Então uma tupla que **era** recusada e **passou** a desenhar fica com os dois
arquivos, e o `--score` a trata como recusada: ela **sai da matriz**, não é
julgada, e o confronto imprime `ok`. É a forma que o perfil chama de Alta — um
gate que passa sem medir — e não tem sintoma: a linha `our side refuses` é
exatamente a que se espera ver para uma tupla recusada.

**Por que é para agora e não um detalhe:** as duas medições que ficaram abertas
são justamente as que viram recusa em desenho. A
[`CORR-LOOKS-047`](/docs/tasks/looks/CORR-LOOKS-047.md) (mapa do goleiro) faz
`A-I3-A-A-A` e `A-H1-A-A-A` desenharem no slot 1, e a
[`CORR-LOOKS-048`](/docs/tasks/looks/CORR-LOOKS-048.md) (`F` e `G` da barba)
faz o mesmo com toda tupla de barba `F`/`G`. Sem este conserto, a corrida que
validaria cada uma delas **pula as tuplas que a medição destravou**, e sai
verde. Por isso as duas dependem desta.

## Evidência

As duas leituras do código acima, e o laço do `run` nas linhas de hoje:

```text
$ grep -n "\.refused" tools/looks/confront.py
667:                with open(path + ".refused", "w", encoding="utf-8") as handle:
715:            if os.path.exists(path + ".refused"):
716:                with open(path + ".refused", encoding="utf-8") as handle:
```

Nenhuma linha remove o `.refused`. No lote das CORR-LOOKS-042 a 045 isso não
mordeu porque a direção foi a contrária — tuplas que desenhavam passaram a
recusar —, e o re-render daquele lote usou um script próprio que apaga os dois.

## Causa raiz

O `run` foi escrito quando nenhuma tupla mudava de estado entre corridas: a
limpeza cobriu o arquivo que ele sabia estar sobrescrevendo, e não o que ele só
escreve às vezes.

## Correção

### Arquivo: `tools/looks/confront.py`

1. Apagar **os dois** — o PNG e o `.refused` — antes de renderizar, e separar o
   laço do nosso lado numa função (`render_ours`, por exemplo) que o `run` chama
   e que dá para chamar sozinha, sem emulador: é o que se usou à mão no lote
   anterior, e é o que a 047 e a 048 vão precisar para re-julgar.
2. No `--score`, **recusar** o estado ambíguo em vez de escolher um lado: se
   existem os dois arquivos, é corrida velha misturada com nova, e isso é falha
   com mensagem, não uma tupla recusada.

### Arquivo: `tools/looks/controls.py`

Um controle que devolva o `run` a apagar só o PNG, e um caso no `self_check()`
com os dois arquivos presentes exigindo a falha.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/confront.py` | modificar |
| `tools/looks/controls.py` | modificar |
| `docs/prompts/perfil-looks.md` | modificar, se a linha do `--score` na tabela de gates precisar dizer como re-renderizar sem emulador |

## Verificação

- [ ] com um `.refused` velho ao lado de um PNG novo, o `--score` **falha**
      nomeando a tupla, em vez de a pular
- [ ] o re-render do nosso lado existe como comando, sem emulador, e apaga os
      dois arquivos
- [ ] `python tools/looks/confront.py --score` sobre a corrida atual continua
      `ok`, com os mesmos placares
- [ ] controle negativo vermelho
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
