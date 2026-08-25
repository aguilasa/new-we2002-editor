---
id: CORR-WTE-112
title: "Correção: o `filtro` de cada campo é publicado no buffers.md e nunca conferido contra o KeyPress"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-112: o `filtro` é afirmação de doc sem guarda

## Problema identificado

O [`buffers.md`](../../wte/re/buffers.md) publica, por campo, o conjunto de
caracteres que o `KeyPress` deixa passar — `[A-Za-z0-9 .]` nos três de nome,
`[A-Za-z0-9]` na abreviatura, `[0-9]` nos dois numéricos. O valor é
**declarado à mão** na tabela `CAMPOS` do
[`dump_buffers.py`](../../wte/tools/dump_buffers.py) e **nunca conferido**
contra o handler que o implementa.

O contraste está dentro do mesmo arquivo: o `predicado` de faixa dos campos
numéricos **é** conferido — o gerador lê o `.inc` e aborta se a validação
sumir, com a mensagem dizendo o que o `MaxLength` deixaria passar sem ela. O
`filtro` do vizinho, não.

Consequência prática: se alguém mexer no `KeyPress` — trocar o conjunto,
acrescentar o hífen, deixar o ponto entrar na abreviatura —, o `buffers.md`
continua afirmando o conjunto antigo, e o banner dele diz **"todo número daqui
saiu do script"**. É a definição de prosa vencida num arquivo gerado, e o
`grupo 4` do [`test_bordas.pas`](../../wte/tests/test_bordas.pas) — que é
*sobre* caractere fora do conjunto — não fecha esse buraco: ele mede o codec e
a camada de dados, não o filtro de tela.

## Evidência

O `filtro` só é escrito e impresso, nunca lido para conferir:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "filtro" wte/tools/dump_buffers.py
```

```text
83:        "filtro": "[A-Za-z0-9 .]",
93:        "filtro": "[A-Za-z0-9 .]",
103:        "filtro": "[A-Za-z0-9]",
113:        "filtro": "[A-Za-z0-9 .]",
137:        "filtro": "[0-9]",
147:        "filtro": "[0-9]",
278:            "modo": c["modo"], "filtro": c["filtro"], "cabe": cabe,
325:           "limite_max\tmodo\tfiltro\n")
329:        f"{l['filtro']}\n"
```

Todas as ocorrências são declaração (83–147), repasse (278) e impressão
(325, 329). Nenhuma abre um `.inc`.

E o que o gerador **faz** com o irmão dele, o `predicado` dos numéricos:

```text
291:        if n["predicado"] not in corpo:
292:            problemas.append(
293:                f"{n['controle']}: a validacao de faixa ({n['faixa']}) sumiu de "
```

| Claim publicado | Fonte | Guarda |
|---|---|---|
| faixa numérica (`1..250`, `1..99`) | o `.inc` do handler | **aborta se sumir** |
| conjunto de caracteres (`[A-Za-z0-9 .]`) | a tabela à mão | **nenhuma** |

## Causa raiz

O `filtro` entrou na tabela como coluna descritiva do inventário, e não ganhou
o mesmo tratamento que o `predicado` de faixa, que nasceu como guarda.

## Correção

### Arquivo: `wte/tools/dump_buffers.py`

Dar ao `filtro` a forma que o `predicado` já tem: o trecho **literal** do
`KeyPress` que o implementa, conferido por substring no `.inc` do handler —
literal, e não regex, pela mesma razão que a task registrou no Log (*"escrever
regex com escape através de heredoc aninhado é frágil… o predicado é texto
Pascal"*).

Cada campo passa a ter o handler e o trecho, e o gerador **aborta** quando o
trecho some. A tabela publicada continua mostrando o conjunto legível — o que
muda é que ele passa a ser derivado de algo conferido.

Se um dos seis não tiver filtro de `KeyPress` (o `casilla_nombre` pode não
ter), a linha diz **`sem filtro`** e isso também é conferido: filtro que
aparece onde a tabela diz que não há é a outra direção da mesma guarda.

### Guarda

Um caso em `test_check_bordas.py` no molde do que já existe para a faixa —
plantar a remoção do trecho num `.inc` copiado e ver o gerador recusar. O
`test_predicado_da_faixa_nao_casa_por_prefixo` é o modelo: ele muta o corpo em
memória e afirma que o predicado deixa de casar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_buffers.py` | modificar |
| `wte/tools/test_check_bordas.py` | modificar — a recusa plantada |
| `wte/re/buffers.md`, `wte/re/buffers.tsv` | regerar |

## Verificação

- [ ] O gerador abre um `.inc` por campo de texto e aborta quando o trecho do
      filtro some — recusa vista, com a plantação
- [ ] O `filtro` publicado no `buffers.md` continua igual ao de hoje para os
      seis campos, ou a mudança está explicada
- [ ] `python3 wte/tools/dump_buffers.py --check` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
