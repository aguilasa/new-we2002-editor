---
id: CORR-WTE-103
title: "Correção: no estado zero o fase-4.md perde a linha em branco antes do título seguinte"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-103: linha em branco que só existe quando há o que listar

## Problema identificado

A quinta passagem da [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md)
consertou dois lugares em que o `check_fase4.py` **degradava mal no zero** —
uma frase que se contradizia e uma tabela vazia. Ficou um terceiro do mesmo
tipo, uma linha acima do primeiro: a linha em branco que separa a contagem de
specs do título seguinte é emitida **dentro** do `if`, e no zero o `if` não
roda.

```python
    a(f"{com_spec} dos {total} têm arquivo de spec.")
    if m["sem_spec"]:
        a("Os que não têm:")
        a("")
        for chave in m["sem_spec"]:
            a(f"- `{chave}`")
        a("")            # <- a unica linha em branco do bloco

    a("## Os que continuam `aberto`")
```

Com `sem_spec` vazio — que é o estado de fechamento, e o estado que este
arquivo vai ter de agora em diante — o gerado sai com o título colado no
parágrafo. É a única junção do arquivo sem a linha em branco.

O CommonMark deixa um título ATX interromper parágrafo, então o GitHub ainda
renderiza como título; o que se perde é a consistência do gerado, e a próxima
ferramenta que fatiar o arquivo por parágrafo não terá a mesma sorte.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
sed -n '38,42p' wte/re/fase-4.md | cat -A | sed 's/\$$/<EOL>/'
```

```text
| **total** | **96** |<EOL>
<EOL>
96 dos 96 tM-CM-*m arquivo de spec.<EOL>
## Os que continuam `aberto`<EOL>
<EOL>
```

Todas as outras junções do arquivo têm a linha em branco:

```bash
grep -B1 '^## ' wte/re/fase-4.md | grep -v '^--$' | grep -vc '^$'
```

## Causa raiz

A linha em branco de fecho do bloco ficou dentro do ramo que lista os
handlers sem spec, em vez de depois dele.

## Correção

### Arquivo: `wte/tools/check_fase4.py`

Mover o `a("")` para fora do `if`, que é onde ele fecha o bloco nos dois
estados:

```python
    a(f"{com_spec} dos {total} têm arquivo de spec.")
    if m["sem_spec"]:
        a("Os que não têm:")
        a("")
        for chave in m["sem_spec"]:
            a(f"- `{chave}`")
    a("")
```

### Arquivo: `wte/re/fase-4.md`

**Não editar.** É gerado; sai certo com o gerador corrigido e reexecutado.

### Guarda

Vale mais que o conserto, porque a família já custou três achados na mesma
passagem: um caso no `test_check_fase4.py` que rode o gerador e recuse
`^## ` imediatamente depois de linha não vazia. É uma varredura de duas linhas
sobre a saída, pega os três casos de uma vez e qualquer quarto.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase4.py` | modificar |
| `wte/tools/test_check_fase4.py` | modificar — a guarda |
| `wte/re/fase-4.md` | regerar |

## Verificação

- [ ] `grep -B1 '^## ' wte/re/fase-4.md | grep -v '^--$' | grep -c '^$'` conta
      uma linha em branco por título
- [ ] O caso novo reprova com um `a("")` removido de propósito
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
