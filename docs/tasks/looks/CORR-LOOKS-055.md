---
id: CORR-LOOKS-055
title: "Correção: `screen.py --report` morre no `■` da ajuda, e a mensagem de falha do `--screen` morreria igual"
type: correção
category: ferramenta
status: pendente
depends_on: []
---

# CORR-LOOKS-055: o `■` da ajuda derruba quem o imprime nesta máquina

## Problema identificado

A ajuda de cada linha da tela traz o glifo de botão `■` (`Skin Colour ■ Turn`),
que o `screen.help_text` guarda de propósito — é o que o jogo desenha. Quem
**imprime** esse texto nesta máquina morre: a saída padrão do Python aqui é
cp1252, e `■` (U+25A0) não existe nela.

O sintoma aparece no `--report`, que é o comando que existe para ler a tabela:

```text
$ python tools/looks/screen.py --report
display 512x240, rows from y=-79 every 12
vertical: Up wraps, Down wraps; help on load 'Visual'; cursor starts on NAT
  DEFAUL      1 value(s)  left locks right locks help 'Confirm'
            O.K.
  NAT        80 value(s)  left locks right locks help 'Nation'
            Unknown | Ireland | Scotland | Wales | ... | Hondura | Libano | New Zeland
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'charmap' codec can't encode character '■' in position 69:
character maps to <undefined>
```

Ele para na terceira linha das doze — `SKIN` é a primeira cuja ajuda tem o
glifo — e sai 1, com pipe ou sem pipe.

**E o caminho pior não é o `--report`.** O `oracle._walk_row` põe a ajuda lida
na mensagem do `OracleError` quando o cursor não chegou onde devia:

```text
tools/looks/oracle.py
        raise OracleError("pressed %s %d time(s) to reach %s and the help "
                          "reads %r" % (button, abs(target - here), name,
                                        screen_help(game)))
```

Numa corrida de doze minutos em que o cursor errasse a linha, o que sairia não
é o diagnóstico: é um `UnicodeEncodeError` vindo do `print` da própria falha, e
a linha que erraria fica sem nome. O mesmo vale para qualquer `say()` que
venha a imprimir ajuda de linha — hoje o `--screen` só imprime a de carga
(`Visual`), que é ASCII, e por isso a caminhada de 2026-09-17 passou inteira.

## Evidência

```text
$ python tools/looks/screen.py --report > /dev/null 2>&1; echo $?
1
$ PYTHONIOENCODING=utf-8 python tools/looks/screen.py --report | grep "slot"
  slot 1: plate GK, shirt 'SHIRT N', title 'S SET' (the object holds 'LOOKS SET', and this font has no 'LOOK')
  slot 2: plate CB, shirt 'SHIRT N', title 'S SET' (the object holds 'LOOKS SET', and this font has no 'LOOK')
```

Com a variável ele imprime as 12 linhas, os dois slots e as quatro regiões.
Sem ela, três linhas e um traceback.

## Causa raiz

O texto medido é Unicode e a saída da ferramenta é do console. `help_text`
normaliza para NFKC, que dobra a largura das letras e **mantém** o `■` — está
certo que mantenha, porque é o que a tela desenha. Quem não trata a saída é
quem imprime.

## Correção

### Arquivo: `tools/looks/screen.py` e `tools/looks/oracle.py`

Garantir a saída antes de imprimir texto medido: reconfigurar `stdout`/`stderr`
para UTF-8 com `errors="replace"` no `main()` das ferramentas que imprimem
ajuda (`sys.stdout.reconfigure`, que o Python 3.7+ tem), ou passar o texto por
uma função que troque o que a saída não codifica. A decisão entre as duas é de
quem executar; o que **não** serve é apagar o `■` da medição, que é o glifo que
o jogo desenha.

Onde quer que fique o conserto, ele vale para as duas saídas: a do `--report` e
a das mensagens de erro do `oracle.py`, que é a que custa uma corrida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/screen.py` | modificar |
| `tools/looks/oracle.py` | modificar |
| `tools/looks/controls.py` | modificar (o controle negativo do caso) |

## Verificação

- [ ] `python tools/looks/screen.py --report` imprime as doze linhas e sai 0
      **sem** `PYTHONIOENCODING`
- [ ] uma mensagem de `OracleError` que carregue a ajuda de uma linha imprime
      sem estourar
- [ ] o controle negativo fica vermelho (`controls.py`)
- [ ] `python tools/looks/selftest.py --quiet` verde, e o `■` continua na
      tabela medida

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
