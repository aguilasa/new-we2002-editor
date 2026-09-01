---
id: CORR-WTE-112
title: "Correção: o `filtro` de cada campo é publicado no buffers.md e nunca conferido contra o KeyPress"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-112: o `filtro` é afirmação de doc sem guarda

## Problema identificado

O [`buffers.md`](../../../wte/re/buffers.md) publica, por campo, o conjunto de
caracteres que o `KeyPress` deixa passar — `[A-Za-z0-9 .]` nos três de nome,
`[A-Za-z0-9]` na abreviatura, `[0-9]` nos dois numéricos. O valor é
**declarado à mão** na tabela `CAMPOS` do
[`dump_buffers.py`](../../../wte/tools/dump_buffers.py) e **nunca conferido**
contra o handler que o implementa.

O contraste está dentro do mesmo arquivo: o `predicado` de faixa dos campos
numéricos **é** conferido — o gerador lê o `.inc` e aborta se a validação
sumir, com a mensagem dizendo o que o `MaxLength` deixaria passar sem ela. O
`filtro` do vizinho, não.

Consequência prática: se alguém mexer no `KeyPress` — trocar o conjunto,
acrescentar o hífen, deixar o ponto entrar na abreviatura —, o `buffers.md`
continua afirmando o conjunto antigo, e o banner dele diz **"todo número daqui
saiu do script"**. É a definição de prosa vencida num arquivo gerado, e o
`grupo 4` do [`test_bordas.pas`](../../../wte/tests/test_bordas.pas) — que é
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

- [x] O gerador abre um `.inc` **por campo** — os seis, não só os de texto — e
      aborta quando o trecho some: recusa plantada em disco sai com **código
      2**, e a plantada em espelho `tempfile` levanta `BufferError`
- [x] O `filtro` publicado no `buffers.md` continua **idêntico** para os seis:
      `git diff` do arquivo gerado sai vazio depois de regerar
- [x] `python3 wte/tools/dump_buffers.py --check` verde; md5 estável
- [x] `make -C wte check` verde (832 testes, era 828)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

O `filtro` ganhou a forma que o `predicado` de faixa já tinha: cada campo passa
a declarar o `.inc` do `KeyPress` que o implementa e os **trechos literais**
que o compõem, e o `confere_filtro()` aborta quando um some. Literal, não
regex, pela razão que a task registrou — o alvo é texto Pascal, e escrever
regex com escape através de heredoc aninhado é frágil.

São **vários trechos por campo**, e não um, porque a condição dos campos de
nome quebra em duas linhas; literal multilinha dependeria da indentação.

A tabela publicada não mudou: o `git diff` do `buffers.md` sai **vazio** depois
de regerar. O que mudou é a origem — o conjunto legível passou a ser derivado
de algo conferido, que era o pedido.

Recusa exercitada nas duas formas: removendo o trecho do `.inc` em disco, o
`--check` sai com **código 2**; removendo-o num espelho `tempfile`, o `mede()`
levanta `BufferError`. O repositório não foi tocado em nenhuma das duas — o
`git diff` de `wte/src/impl/` ficou vazio.

**Problemas encontrados:**

**O `casilla_nombre` tem filtro.** A CORR admitia que ele pudesse não ter, e
previa uma linha `sem filtro` conferida nos dois sentidos. Medido, os **seis**
têm `KeyPress` com teste literal, então a construção não foi necessária — e
fica registrado que a assimetria prevista não existe.

**A guarda da [CORR-WTE-111](/docs/tasks/concluidos/CORR-WTE-111.md) reprovou as chaves
novas, e estava certa.** O `confere_filtro()` lê pelo parâmetro `campo`, e a
guarda só conhecia os nomes `c` e `n`. A saída fácil seria procurar
`["chave"]` com qualquer identificador na frente — e ela **desliga a guarda**:
a `faixa` dos campos de texto passaria por causa da leitura que os numéricos
fazem da chave homônima, que é o defeito exato que a 111 existe para pegar. Em
vez disso, a lista de leitores por tabela ganhou o `campo`, que é lido pelas
duas porque a função é chamada com as duas.

**E o `PENDENTES` esvaziou uma correção depois de nascer.** A 111 pôs ali o
`filtro` dos numéricos com dono nomeado; esta correção o tornou conferido e
tirou a linha — que é o caso da 111 que **reprova quando a chave passa a ser
lida** funcionando na primeira oportunidade. O mecanismo fica, vazio.

**Arquivos criados/modificados:**

- `wte/tools/dump_buffers.py` — `filtro_handler`, `filtro_trecho`,
  `confere_filtro()`, chamado pelos seis
- `wte/tools/test_check_bordas.py` — `TestFiltroConferido` (4 casos), o
  `PENDENTES` esvaziado e o `LEITORES` por tabela
