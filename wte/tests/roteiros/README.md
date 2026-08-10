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

## Os roteiros 06 a 11 falam outro dialeto

Os seis são da WTE-TASK-19 e quem os executa é
[`../../tools/diff_dirigido.sh`](../../tools/diff_dirigido.sh), não a mão. Eles
acrescentam três diretivas e trocam a linha de `xdotool` crua por verbos:

| Prefixo | Significado |
|---|---|
| `>` | espera a janela com esse nome e passa a ser a origem das coordenadas |
| `>~` | idem, mas pelo **tamanho** (`529x498`) — ver abaixo |
| `=` | corta o log de I/O; tudo até a próxima marca é a conta daquela ação |
| `!` | `clique X Y`, `duplo X Y`, `tecla <k>`, `texto <t>` |

O `>~` existe porque **três formulários trocam o próprio `Caption` pelo nome do
time em tempo de execução** — `estrategia`, `jugador` e `ficha_dorsal`. Com a
ROM japonesa isso é Shift-JIS, e o que o `xdotool` vê é uma corrida de `?`: não
há regex estável. O tamanho há, e sai do `ClientWidth`/`ClientHeight` do próprio
DFM.

**Uma exceção medida:** o `ficha_dorsal` aparece como **135x153** e o DFM diz
129x121. Sem window manager o Wine desenha a moldura dentro da própria janela X,
e são 3 px de borda mais 29 de título. Só ele, entre os três — os outros dois
batem 1:1.

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

### O 07 e o 08 são um par, e é isso que os torna medida

[`07-controle-sem-time.txt`](07-controle-sem-time.txt) e
[`08-so-troca-de-time.txt`](08-so-troca-de-time.txt) são **iguais linha a
linha até a marca `= ARRANQUE`**; o 08 tem duas linhas a mais, que trocam o
time pelo teclado. Medido com `WINEDEBUG=+seh,+loaddll`: **0 violações de
acesso no 07, 309 no 08** — uma variável de diferença.

O 06 também trava, e por isso **não** serve de par: ele clica as oito áreas
antes de trocar de time, o que são oito variáveis a mais.

Editar um dos dois sem o outro quebra a afirmação; o
[`../../tools/test_analisar_crash.py`](../../tools/test_analisar_crash.py)
compara os dois cabeçalhos e falha se divergirem. O veredito de onde a falha
cai está em [`../../re/crash.md`](../../re/crash.md).

### O 09 é o que o 06 deixou de poder ser

O [`09-areas-com-time.txt`](09-areas-com-time.txt) troca de time **primeiro** e
só então exercita cada área — que é a ordem natural, e era impossível enquanto
trocar de time matasse o app. A CORR-WTE-044 mediu a causa e o contorno: com
`roms/japanese-shift-jis.bin` o `wte.exe` passa da troca de time com **zero**
violação de acesso, contra 49.749 com a europeia.

**Ele só vale com a imagem japonesa.** Rodá-lo contra a europeia mede o
travamento, não as áreas. O `--imagem` não tem padrão que sirva aqui:

```sh
bash wte/tools/diff_dirigido.sh wte/tests/roteiros/09-areas-com-time.txt \
     --imagem roms/japanese-shift-jis.bin
```

Duas coisas que ele ensina sobre dirigir este app, e que custaram três
sessões exploratórias:

- **botão de área abre diálogo, e o diálogo é modal.** `boton_barras2iso` e
  `boton_nombres2iso` abrem a caixa `W11 TE PT!` (282×113, `Ok` em (142,80));
  `colorear` abre o `ficha_color` (`Cor`, 542×225, `OK` em (492,204));
  `mostrar_jugador_1` pergunta antes (`Calcular precos`, 285×124, `Sim` em
  (182,86)). Deixar qualquer um aberto **engole todos os cliques seguintes**, e
  o roteiro parece ter parado de funcionar;
- **`xdotool windowkill` num diálogo mata o processo inteiro.** Fechar é
  clicando no botão. Foi assim que uma sessão exploratória morreu no primeiro
  passo.

### O 10 e o 11 são a 5ª passagem, e dividem o trabalho por natureza

Depois do 09 sobravam 35 dos 50 `OFS_*` sem veredito dinâmico, e eles não
faltavam pelo mesmo motivo:

- [`10-telas-que-faltavam.txt`](10-telas-que-faltavam.txt) — o que faltava era
  **tela**: a estratégia, a ficha do jogador, o dorsal, o outro lado da janela,
  a extração do uniforme, o diálogo de textura;
- [`11-varredura-de-times.txt`](11-varredura-de-times.txt) — o que faltava era
  **índice**: `OFS_PLAYER_NAME_5..8`, `OFS_PLAYER_ATTR_1..9` e os `OFS_ML_*` são
  blocos com passo de setor, e o time do topo da lista endereça sempre o
  primeiro. Nenhuma tela nova resolve isso; descer na lista resolve.

Os dois só valem com a imagem japonesa, pela mesma razão do 09.

**Arquivo que o roteiro manda gravar tem de não existir antes.** O 10 extrai o
uniforme para `E:\u.bmp`; com o arquivo no lugar, o `TSaveDialog` abre a
confirmação de sobrescrita, que roteiro fixo nenhum espera — e a corrida morre
esperando a janela seguinte. Quem apaga é o `diff_dirigido.sh`, antes de copiar
a imagem.

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
