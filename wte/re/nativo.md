# `re/nativo.md` — a condição 3: nativo, sem Wine, sem 32 bits

**Escrito à mão; todo número vem de ferramenta.** A medição é o
[`nativo_check.sh`](../tools/nativo_check.sh), e o registro dela é
[`nativo.tsv`](nativo.tsv). Produto da
[WTE-TASK-40](../../docs/tasks/concluidos/40-verificacao-final.md).

```sh
cp roms/japanese-shift-jis.bin work/copia.bin
bash wte/tools/nativo_check.sh --imagem work/copia.bin
```

## A afirmação, e a que ela não é

> **Condição 3 (plano, §0).** O app roda em Linux x86-64 nativo, sem Wine, sem
> camada 32-bit.

São **duas** afirmações, e é fácil entregar só a primeira:

| | Como se responde | O que prova |
|---|---|---|
| o app **não usa** Wine | `ldd` no binário | que o linkeditor não pediu nada de Wine |
| o app **roda onde Wine não existe** | uma máquina sem Wine | que ele não depende de nada que o Wine deixou no sistema |

Esta máquina **tem** Wine — o oráculo A depende dele, e a bateria golden
inteira também. Medir a segunda afirmação aqui exigiria desinstalar o oráculo,
que é exatamente o que não se pode fazer. A saída é a mesma do
`tools/run-sanitized.sh` do `newWe2002`: um user+mount namespace sem
privilégio, onde os caminhos do Wine ficam cobertos por `tmpfs` vazio. Só a
árvore daquele processo enxerga isso; nada no sistema muda, e o Wine continua
inteiro para a corrida seguinte do gate.

Quem fabrica esse ambiente é o [`sem_wine.sh`](../tools/sem_wine.sh), e ele
**recusa** por dois motivos — ambiente que só *parece* limpo mede tão pouco
quanto não medir. Recusa se algum alvo mascarado **não ficar vazio** dentro do
namespace, que é a cláusula com dentes nesta máquina, e recusa se
`wine`/`wine64`/`wineserver`/`winecfg` responderem no `PATH`, que é a que pega
uma máquina com o pacote do apt — aqui ela é verdadeira antes de mascarar
qualquer coisa, porque o Wine daqui nunca esteve no `PATH`. As duas estão
medidas no `test_check_nativo.py`, uma recusa por cláusula.

## O que fica coberto, e por quê cada um

Não há pacote `wine` no apt desta máquina: o Wine daqui é o runner do Bottles,
em `~/.var/app/`. Mascarar `/usr/bin/wine` não esconderia nada.

| Caminho | Por que entra |
|---|---|
| `~/.var/app/com.usebottles.bottles` | o runner `soda-9.0-1` — **é** o Wine desta máquina |
| `/var/lib/flatpak` | a instalação do Bottles e os runtimes `org.winehq.Wine.{gecko,mono}` |
| `work/wineprefix`, `work/wineprefix-wte` | os dois prefixos deste repositório; a condição pede que o app não leia nada dali |
| `/lib/i386-linux-gnu`, `/usr/lib/i386-linux-gnu` | o stack 32 bits. Sem ele o `winex11.drv` de 32 bits nem carrega — e mascarar prova a independência que a condição também pede |

## As sete medidas

Medido em **2026-08-26**, sobre a árvore **instalada** (não o `wte/build/wte`),
com a imagem japonesa copiada para fora de `roms/`.

| Medida | Valor | Veredito |
|---|---|---|
| `formato` | ELF 64-bit x86-64 | ok |
| `ldd-wine` | 0 de 56 bibliotecas | ok |
| `ldd-32` | 0 de 56 bibliotecas | ok |
| `guarda` | `wine`/`wine64`/`wineserver` ausentes no namespace | ok |
| `janela` | 522×475, título conferido | ok |
| `carga` | 3 cargas de time para 3 teclas | ok |
| `maps` | 0 mapeamentos de Wine ou 32 bits | ok |

Fonte: [`nativo.tsv`](nativo.tsv), uma linha por medida.

### Por que a medida `carga` existe

Janela vazia abre igual. As três teclas `Down` na lista de times têm de virar
três `MainForm.lista_equiposChange` no log de trace que o **próprio app**
escreve — é a diferença entre "subiu" e "funciona", e é lida do arquivo, não da
tela.

### Por que `maps` não é o mesmo que `ldd`

`ldd` mede o que o linkeditor pediu; `/proc/<pid>/maps` mede o que o processo
**abriu**, inclusive o que ele carregasse por `dlopen` já rodando. Um plugin de
tema GTK trazido em tempo de execução apareceria só na segunda.

## A árvore instalada roda **depois de movida**

Medido na [WTE-TASK-39](../../docs/tasks/concluidos/39-empacotamento.md), em 2026-08-26, e
não remedido aqui: `make -C wte install PREFIX=<p>`, `mv <p> <outro>`, e o
binário instalado abriu, achou os assets no caminho novo e carregou um time.
A regra mora no [`wte_datafiles.pas`](../src/wte_datafiles.pas) e vale para
assets **e** para o log de trace.

O defeito que essa task consertou vale registrar, porque ele se disfarça: o
binário fora de `wte/build/` morria num diálogo genérico da LCL — *File not
found. Press OK to ignore and risk data corruption.* — antes de qualquer
janela, porque o log de trace resolvia `<exe>/../re/trace.log` e o `Rewrite`
levantava `EInOutError`. Diagnóstico que mata o paciente é pior que nenhum: o
`retrace` hoje desliga o trace em vez de derrubar o app.

## O que a condição 3 **não** afirma

- **Não** afirma que o app roda em outra distribuição, com outra versão de
  GTK2. O que se mediu é esta máquina, com o Wine coberto.
- **Não** afirma que o app roda sem GTK2 nem sem X — ele é LCL/GTK2, e o
  `:98` é X. Wayland não foi testado.
- **Não** afirma nada sobre os assets do Obocaman, que não são
  redistribuídos: sem eles o app **abre e avisa**, e isso é
  [divergência registrada](divergencias.md) — o original encerra.
