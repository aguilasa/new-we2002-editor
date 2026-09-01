---
id: CORR-WTE-046
title: "Correção: três vereditos citam `case N` onde o `Database.cpp` tem `if(i == N)`"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-046: a prova do veredito aponta para uma construção que não está lá

## Problema identificado

A tabela **"Os 50, um a um — o veredito de cada"** do
[`wte/re/offsets-novos.md`](../../../wte/re/offsets-novos.md) fecha o critério da
[WTE-TASK-19](/docs/tasks/concluidos/19-os-50-offsets-restantes.md): 33 endereçados, 14
`retomada de fronteira`, 3 `base de varredura`. A coluna **prova** de cada
`retomada` diz `` `case N` no `Database.cpp` ``.

Em **3 das 14** linhas essa citação não se confere:

| `Offsets.hpp` | prova impressa | o que o `Database.cpp` tem |
|---|---|---|
| `OFS_FORMATIONS_A` | `case 32` | `if(i == 32)` — `src/core/Database.cpp:376` — e **não existe** `case 32 :` no arquivo |
| `OFS_TEAM_NAME_5_A` | `case 57` | `if(i == 57)` — `src/core/Database.cpp:204` — e **não existe** `case 57 :` |
| `OFS_ML_TEAM_NAME_8_A` | `case 30` | `if(i == 30)` — `src/core/Database.cpp:296` — mas **existe** um `case 30 :` sem relação, em `503` e `1077` |

O veredito em si está certo: `if(i == N)` é retomada de fronteira tanto quanto
`case N :`, e o classificador (`papel_no_legado`) casa as duas construções de
propósito — `RE_CASO` **ou** `RE_SE`. O que está errado é a **prova escrita**,
que descarta qual das duas casou e imprime `case` sempre.

O terceiro caso é o pior: quem for conferir `OFS_ML_TEAM_NAME_8_A` grepando
`case 30` acha um bloco de verdade, e ele é de outra leitura. Prova que leva ao
sítio errado é pior do que prova ausente, porque parece conferida.

Este é o único ponto em que o critério da task se apoia em algo que não é
medição do `strace` — os 17 saem do fonte —, então a rastreabilidade dessa
coluna é o que sustenta o fechamento da task.

## Evidência

Medido com o próprio classificador, cruzando o gatilho contra o fonte:

```
$ python3 - <<'EOF'
import sys, re, pathlib; sys.path.insert(0,'wte/tools')
import analisar_io as a
src = pathlib.Path('src/core/Database.cpp').read_text()
for n,(papel,g) in sorted(a.papel_no_legado().items()):
    if papel != "retomada": continue
    tem_case = bool(re.search(r"\bcase\s+"+re.escape(g)+r"\s*:", src))
    print(n, g, "case_no_fonte=", tem_case)
EOF
...
OFS_FORMATIONS_A      32  case_no_fonte= False
OFS_TEAM_NAME_5_A     57  case_no_fonte= False
OFS_ML_TEAM_NAME_8_A  30  case_no_fonte= True    <- mas em 503/1077, outro bloco
```

O sítio real de cada um:

```
$ grep -n "if(i == 57)\|if(i == 30)\|if(i == 32)" src/core/Database.cpp
204:		if(i == 57)
296:		if(i == 30)
376:		if(i == 32)
...
$ grep -n "OFS_TEAM_NAME_5_A\|OFS_ML_TEAM_NAME_8_A\|OFS_FORMATIONS_A" src/core/Database.cpp | head -3
209:			image_file.Seek(OFS_TEAM_NAME_5_A);
298:			image_file.Seek(OFS_ML_TEAM_NAME_8_A);
381:			image_file.Seek(OFS_FORMATIONS_A);
```

A fonte do defeito, em `wte/tools/analisar_io.py:672`:

```python
elif papel == "retomada":
    vered = "retomada de fronteira"
    prova = f"`case {gatilho}` no `Database.cpp`"
```

e em `papel_no_legado` (linhas 430-437), que casa `RE_CASO` **ou** `RE_SE` e
devolve só `("retomada", gatilho)` — a construção que casou se perde ali.

## Causa raiz

`papel_no_legado()` não devolve **qual** construção casou, e o gerador assume
`case` para as duas.

## Correção

### Arquivo: `wte/tools/analisar_io.py`

Fazer o classificador devolver a construção junto do gatilho, e o gerador
imprimir a que casou:

```python
        for j in range(i, max(-1, i - JANELA_BLOCO) - 1, -1):
            c = RE_CASO.search(linhas[j])
            if c:
                gatilho, forma = c.group(1).strip(), "case"
                break
            c = RE_SE.search(linhas[j])
            if c:
                gatilho, forma = c.group(1).strip(), "if"
                break
```

e, na tabela:

```python
    prova = (f"`case {gatilho} :`" if forma == "case"
             else f"`if (i == {gatilho})`") + " no `Database.cpp`"
```

O `forma` entra como terceiro item da tupla de retorno; os chamadores atuais
(o gerador e o `test_todo_offset_ausente_tem_veredito`) usam só o índice 0 e
não quebram, mas a mudança de aridade tem de ser feita nos dois sítios de
desempacotamento.

Vale acrescentar o **número da linha** do `Seek` à prova — é o que torna a
citação conferível por `grep` mesmo quando o gatilho se repete no arquivo.

### Arquivo: `wte/re/offsets-novos.md`

Regerar (`python3 wte/tools/analisar_io.py`, sem `--check`).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/analisar_io.py` | modificar |
| `wte/tools/test_analisar_io.py` | modificar — fonte plantado com `if(i == N)` e com `case N :`, exigindo prova distinta |
| `wte/re/offsets-novos.md` | modificar (regerado) |

## Verificação

- [x] cada prova da coluna casa por `grep` no `src/core/Database.cpp` — a de
      `if` acha `if(i == N)`, a de `case` acha `case N :`. Conferido nas 14:
      `14 ok`, zero falha
- [x] teste com fonte plantado nas duas formas reprova se a prova voltar a ser
      sempre `case`
- [x] a contagem 33 / 14 / 3 não muda (a correção é de rótulo, não de veredito)
- [x] `python3 wte/tools/analisar_io.py --check` verde; gerar duas vezes dá o
      mesmo md5 (`61995638008e...`)
- [x] `make -C wte check` verde — 378 testes, `rc=0`
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

`papel_no_legado()` passou a devolver uma `NamedTuple` `Papel` em vez de tupla
crua de dois campos. O laço que procura o gatilho deixou de usar
`RE_CASO.search(...) or RE_SE.search(...)` — que é onde a informação se perdia
— e passa pelas duas separadamente, guardando:

| campo | o que é |
|---|---|
| `papel` | `retomada` / `varredura` / `direto`, como antes |
| `gatilho` | o `N`, como antes |
| `forma` | `case` ou `if` — qual construção casou |
| `linha` | a linha do `Seek`, 1-based |
| `constr` | o **texto literal** que casou no fonte |

O `constr` existe porque a prova precisa ser greppável **verbatim**: o legado
escreve `if(i == 57)`, sem espaço depois do `if`, e uma prova sintetizada como
`if (i == 57)` não seria achada por quem for conferir. A prova impressa passou
a ser `` `if(i == 32)` no `Database.cpp`, `Seek` em :381 ``.

A linha do `Seek` resolve o terceiro caso, que era o pior: `OFS_ML_TEAM_NAME_8_A`
tem gatilho 30, e existe um `case 30 :` de verdade em `503` e `1077`, sem
relação nenhuma. Com `:301` na prova, a citação não tem para onde escorregar.

Três testes novos e um de evidência:

- `test_a_construcao_que_casou_nao_e_descartada` — mesmo gatilho (30) nas duas
  formas; exige `forma` distinta e os dois `Papel` diferentes entre si;
- `test_a_linha_do_seek_e_1_based`;
- os dois testes de tupla existentes passaram a comparar a `Papel` inteira, o
  que fixa `forma` e `constr` junto;
- `TestEvidencia.test_toda_prova_de_retomada_casa_no_Database_cpp` — lê as 14
  linhas `retomada de fronteira` do `offsets-novos.md` gerado e confere contra
  o fonte: o `Seek` do `OFS_*` está na linha citada, e a construção citada está
  nas `JANELA_BLOCO` linhas acima dela.

**Problemas encontrados:**

O `grep` transcrito na seção Evidência desta CORR dá `298` para o `Seek` de
`OFS_ML_TEAM_NAME_8_A`; a linha é **301**. Não muda nada do diagnóstico — os
três casos e a causa raiz reproduzem —, e o número que entrou no markdown é
derivado pelo gerador, não copiado da CORR. Fica registrado porque é
exatamente o tipo de transcrição à mão que a [CORR-WTE-015](/docs/tasks/concluidos/CORR-WTE-015.md)
mandou parar de fazer.

**Arquivos criados/modificados:**

- `wte/tools/analisar_io.py` — `Papel` (nova), `papel_no_legado()`,
  `secao_veredito_dos_50()` e o texto do veredito
- `wte/tools/test_analisar_io.py` — dois testes novos em `TestPapelNoLegado`,
  um em `TestEvidencia`, dois atualizados
- `wte/re/offsets-novos.md` — regerado
