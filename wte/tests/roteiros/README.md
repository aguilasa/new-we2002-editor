# `tests/roteiros/` — os roteiros de interação, fixos e versionados

Insumo da [WTE-TASK-13](../../../docs/tasks/13-trace-de-eventos.md) e, depois, do
harness golden da [WTE-TASK-22](../../../docs/tasks/22-harness-golden.md).

**Roteiro é fixo, nunca reativo.** Um driver que olha a tela e decide o próximo
passo muda o estímulo quando um lado diverge — e aí os dois param de receber a
mesma entrada, que é justamente a condição de qualquer comparação valer alguma
coisa. Aqui a sequência é escrita, versionada e idêntica nos dois lados.

## Formato

Arquivo de texto, uma diretiva por linha:

| Prefixo | Significado |
|---|---|
| `#` | comentário |
| `alvo:` | `port`, `original` ou `ambos` — de que lado o roteiro roda |
| `estado:` | `ok` ou `bloqueado: <razão>` |
| `!` | comando `xdotool`, literal, com as coordenadas **relativas à janela** |
| `~` | espera, em segundos |
| `@` | linha de trace esperada, sem o carimbo de tempo |

As coordenadas de `!` são relativas ao canto da janela alvo; quem replica soma
a origem, que muda a cada execução. O carimbo de tempo fica fora do `@` de
propósito: ele existe para ler intervalo, e a informação está na **ordem** das
linhas (ver o cabeçalho de [`../../src/retrace.pas`](../../src/retrace.pas)).

## O roteiro 06 fala outro dialeto

[`06-diff-dirigido.txt`](06-diff-dirigido.txt) é da WTE-TASK-19 e quem o
executa é [`../../tools/diff_dirigido.sh`](../../tools/diff_dirigido.sh), não a
mão. Ele acrescenta duas diretivas e troca a linha de `xdotool` crua por
verbos:

| Prefixo | Significado |
|---|---|
| `>` | espera a janela com esse nome e passa a ser a origem das coordenadas |
| `=` | corta o log de I/O; tudo até a próxima marca é a conta daquela ação |
| `!` | `clique X Y`, `duplo X Y`, `tecla <k>`, `texto <t>` |

O motivo dos verbos é a coordenada: sem window manager no `:99` a origem da
janela muda a cada corrida, e escrever `xdotool` cru obrigaria cada linha a
saber somar. As coordenadas saem do
[`../../re/dfm/MainForm.dfm`](../../re/dfm/MainForm.dfm) — `Left`/`Top` do
controle mais o do `GroupBox` pai —, e o DFM bate **1:1** com o cliente da
janela: medido, `ClientWidth` 522 × `ClientHeight` 475 é exatamente o que o
`xdotool getwindowgeometry` devolve.

**Uma armadilha que custou dois diagnósticos:** a lista suspensa de um
`TComboBox` fica **mapeada** depois do clique no item e segura o ponteiro —
todo clique seguinte morre nela, inclusive num botão do outro lado da janela.
Trocar de item pelo teclado (`Down`) evita a lista. E o sintoma "o clique
parou de funcionar" tem um segundo culpado, que é pior: o `wte.exe` **cai** ao
carregar um time com as ROMs deste repositório, e a janela sobrevive ao
processo. Confira `ps -o stat` procurando `Z`, e não a tela.

## Replicar

Lado port, com o trace num arquivo próprio:

```sh
WTE_TRACE_FILE=/tmp/t.log ./wte/build/wte &
# some a origem da janela em cada linha '!' e execute
```

Lado original: `make wte-99`, mesma sequência, **sem** trace — o `wte.exe` não
loga nada, e a leitura é por efeito de tela. Ver
[`../../re/eventos.md`](../../re/eventos.md).

## Limite medido, e é duro: **teclado não chega no app LCL no `:99`**

Nenhum roteiro do lado port usa tecla. Não é escolha: no `:99` não há window
manager, o GTK2 nunca considera a janela ativa, e **nenhuma tecla é entregue** —
nem por `xdotool key` depois de `windowfocus`, nem por `xdotool key --window`
(que usa `XSendEvent`, e o GTK2 descarta). Medido: zero diferença de pixel no
campo e zero linha no trace. O mouse funciona normalmente.

O `wte.exe` **não** tem esse problema: o Wine implementa o próprio foco e
recebe tecla no `:99` desde sempre — é o que o `golden_run.sh` do `newWe2002`
já explora para digitar o caminho da imagem.

Consequência para a WTE-TASK-22: ou o harness dirige o port **só por mouse**,
ou o `:99` ganha um window manager. Nenhum está instalado nesta máquina
(`twm`, `openbox`, `metacity`, `mutter`, `xfwm4`, `i3`, `fluxbox`, `icewm`,
`jwm`, `matchbox`, `marco`, `herbstluftwm`, `dwm`, `awesome` — nenhum
encontrado). **Instalar pacote é decisão do usuário.**
