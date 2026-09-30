---
id: CORR-LOOKS-055
title: "Correção: `screen.py --report` morre no `■` da ajuda, e a mensagem de falha do `--screen` morreria igual"
type: correção
category: ferramenta
status: done
depends_on: []
origin: LOOKS-TASK-21
severity: medium
done_on: 2026-09-17
done_commit: 45b9763
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

- [x] `python tools/looks/screen.py --report` imprime as doze linhas e sai 0
      **sem** `PYTHONIOENCODING`
- [x] uma mensagem de `OracleError` que carregue a ajuda de uma linha imprime
      sem estourar
- [x] o controle negativo fica vermelho (`controls.py`)
- [x] `python tools/looks/selftest.py --quiet` verde, e o `■` continua na
      tabela medida

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

A evidência reproduz em `45b9763`: `screen.py --report` sai **1** com um
`UnicodeEncodeError` de `charmap`, com pipe e sem pipe, e imprime as 32 linhas
só com `PYTHONIOENCODING=utf-8`.

O conserto é o primeiro dos dois que a CORR admitia: `screen.make_printable`
pede UTF-8 **com `errors="replace"`** à saída, e `screen.printable_output()`
faz isso com as duas padrão. O `main()` do `screen.py` e o do `oracle.py`
chamam antes de qualquer impressão — o do oracle com a razão escrita ao lado,
que é a mensagem de erro do `_walk_row`, não o `--report`.

**O `■` não saiu da medição.** Ele é o que a tela desenha, e continua no
`screen.json` e no `help_text`; quem se ajusta é a saída. Um console que não
carregue um caractere imprime substituto em vez de derrubar a corrida.

### Gates

```text
$ python tools/looks/screen.py --report > /dev/null 2>&1; echo $?
0                                  # era 1
$ python tools/looks/screen.py --report | wc -l
32                                 # as doze linhas, os dois slots, as regiões
$ python tools/looks/screen.py --report | grep -c Turn
6                                  # as seis ajudas que trazem o glifo

$ python - <<'PY'                  # o caminho que custava uma corrida
import sys; sys.path.insert(0, "tools/looks")
import screen, oracle
screen.printable_output()
print(oracle.OracleError("pressed Down 2 time(s) to reach SKIN and the help "
                         "reads %r" % "Skin Colour \u25a0 Turn"))
PY
pressed Down 2 time(s) to reach SKIN and the help reads 'Skin Colour ■ Turn'
exit=0

$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
$ python tools/looks/oracle.py --check
oracle.py: 0 failure(s)
$ python tools/looks/controls.py --only screen-output-left-as-the-console
  RED    screen-output-left-as-the-console screen.py :: make_printable
$ python tools/looks/selftest.py --quiet
  ..... 69 of 69 controls red
looks_selftest: 0 failure(s)
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**O que não foi re-rodado, e por quê:** o `oracle.py --screen` inteiro (~12
min). A mudança é de saída, não de medição, e a caminhada fechou verde
(`0 difference(s)`, 716 s) em `9ed647b`, meia hora antes. O `oracle.py --check`
cobre o módulo alterado.

`roms/` intocada; nenhum emulador subiu nesta correção.

### Problemas encontrados

- A primeira edição do `controls.py` casou a linha errada e emendou os dois
  controles de tela num só, duplicando o da CORR-LOOKS-054. O `--list` acusou
  70 catalogados; o bloco duplicado saiu e são **69**, sem id repetido.

### Arquivos criados/modificados

- `tools/looks/screen.py` — `make_printable`, `printable_output`, três casos no
  `self_check()`, e a chamada no `main()`
- `tools/looks/oracle.py` — a chamada no `main()`
- `tools/looks/controls.py` — `screen-output-left-as-the-console`
- `docs/PLAN-LOOKS-PY.md` — a armadilha de console da §1.11, que dizia que o
  jeito era a variável de ambiente
- `docs/prompts/perfil-looks.md` — armadilha 38
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
