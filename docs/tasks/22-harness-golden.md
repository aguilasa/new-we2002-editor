---
id: WTE-TASK-22
title: "golden_check.sh — o gate: wte.exe contra o app Lazarus"
type: ferramenta
category: verificação
phase: 4
depends_on: ["WTE-TASK-11", "WTE-TASK-21"]
status: concluído
---

# WTE-TASK-22: Harness golden

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §6.
- **É o gate da fase 4.** Nenhum handler entra sem ele verde. Vem antes dos
  handlers de propósito: sem gate, cada implementação é opinião.

A estrutura já existe neste repositório — `tools/golden_check.sh` faz duas
cópias da imagem, passa uma pelo oráculo sob Wine e a outra pelo port, e
compara. Aqui é o mesmo, trocando o oráculo:

```
copia_A.bin --> we-team-editor.exe (Wine 32-bit, :99, xdotool) --+
                                                                  |-- cmp
copia_B.bin --> app Lazarus (nativo, :99, xdotool) --------------+
```

---

## Objetivo

`wte/tools/golden_check.sh`, herdando **todas** as guardas do existente.

### As guardas, e por que cada uma existe

| Guarda | Custo que ela evita |
|---|---|
| fixar `DISPLAY=:99` dentro do script | o runner de teste repassa o `DISPLAY` do shell (`:1` aqui), e as janelas da sessão real derrubam a detecção |
| recusar-se a começar com janela grande já aberta no `:99` | uma janela esquecida de teste manual é dirigida em vez da que está sob teste, e o resultado é um diff que parece bug do port |
| restringir candidatos ao `_NET_WM_PID` do processo lançado | mesma causa, outra defesa |
| nunca apontar para `roms/` | os três editores gravam in-place, e cada imagem tem ~474 MB |

### O que muda em relação ao original

**O `wte.exe` tem título de janela** (`W11 Team Editor...`), ao contrário do
`IDD_ED_DIALOG` do `ed.exe`, que só se acha pelo tamanho. Isso simplifica —
mas exige que o app Lazarus tenha título **diferente** (WTE-TASK-11), senão os
dois lados se confundem.

### Dirigir a janela: as armadilhas já pagas

- Sem window manager no `:99`: `xdotool windowactivate` falha. Dirigir por
  coordenada absoluta.
- `xdotool type --window` usa `XSendEvent` e **embaralha string longa**. Digitar
  curto.
- **`Ctrl+A` não seleciona tudo num `TEdit`.** Limpar campo com `End`,
  `shift+Home`, `BackSpace`. Com `ctrl+a` os dois lados recebem textos
  diferentes e o diff acusa divergência que não existe.
- O diálogo de abrir do original não engole caminho longo digitado — o
  `make wte` mapeia `E:` para `work/` por isso. Reusar o truque.

### Roteiro de edição

Como o `GOLDEN_EDIT` do `golden_run.sh` existente: um trecho de shell que faz a
edição na tela antes de gravar, para os dois lados. Um roteiro por operação.

### Ordem de grandeza do custo

O script existente usa ~950 MB de temporário por rodada. Este usa o dobro,
porque são duas imagens de ~474 MB. Não roda em CI, e o plano já registra isso.

---

## Três medidas da WTE-TASK-12 e da 13 que esta task herda

### 1. ~~**Bloqueante:**~~ o oráculo A quebra ao selecionar um time — **com a imagem europeia**

Medido na WTE-TASK-12, com cópia byte-idêntica a `roms/`: escolher um time no
combo do `MainForm` dispara **310 `EXCEPTION_ACCESS_VIOLATION`** e o processo
morre. A primeira é leitura em ponteiro nulo + `0x1c` em `ip=0x005f5ea0`; as
seguintes são chamada para o endereço 0, até `stack overflow`. Determinístico.
As janelas X sobrevivem órfãs sob o `wineserver`, então **o app parece vivo numa
captura** — não confie na tela para decidir se ele está de pé.

Descartados como causa: cópia corrompida, os cliques em `TSpeedButton` (sem
time, `Sobre...` e `Sair` abrem seus formulários normalmente) e estado sujo do
Wine. Confundidor que esta máquina não consegue eliminar: o único runner é
`wine-experimental.bleeding.edge…(TkG Plain)`, que o log anuncia como versão de
teste, e não há Wine de sistema.

**Quase toda operação do editor começa por escolher um time**, então isto foi
bloqueante do dia da WTE-TASK-12 até a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md). Diagnóstico e comando de
reprodução em [`../../wte/re/visual.md`](../../wte/re/visual.md), achado 1.

**Deixou de ser bloqueante em 2026-08-10, e o que resolveu foi a imagem.** A
CORR-WTE-044 mediu a causa: o ponteiro global `0x004335e4`, que a rotina de
realce dos `dorsalN` usa, é sobrescrito pela carga do time com dado de uma
tabela vizinha, e o valor (`0x00010001`) passa no teste de nulo que a rotina
faz. Não é controle faltando — os 23 `dorsalN` estão vivos e com `Font`. Mesmo
roteiro, mesmas marcas, só a imagem muda:

| imagem | violações de acesso ao trocar de time |
|---|---:|
| `roms/golden-european-deluxe.bin` | 49.749 |
| `roms/japanese-shift-jis.bin` | **0** |

**Consequência dura para esta task: o harness fixa `roms/japanese-shift-jis.bin`
do lado do oráculo, e escreve no script por quê.** Trocar por hábito para a
imagem golden do `newWe2002` devolve dezenas de milhares de violações de acesso
e parece defeito do harness. E o gate deve tratar `code=c0000005` no
`wine.log` como **falha do lado do oráculo**, nunca silenciá-la: está provado
que este caminho é imune com a japonesa, não que a imagem inteira seja.

As três ressalvas e o que ficou sem resposta estão em
[`../../wte/re/crash-causa.md`](../../wte/re/crash-causa.md).

### 2. O controle **não** é "imagem intocada"

Aceitar o aviso de tamanho — o caminho normal, porque o editor espera
474.431.328 bytes e nenhuma das duas imagens tem esse tamanho — grava na imagem
antes de qualquer edição. Medido passo a passo: o diálogo de arquivo não grava,
o "Sim" do aviso grava, e nem o splash nem a seleção de time acrescentam byte.

**Toda medida abaixo diz de qual imagem fala**, porque as duas não gravam a
mesma coisa e este harness não usa a mesma imagem da task que originou o
número:

| imagem | tamanho | de onde vem a medida |
|---|---:|---|
| `roms/golden-european-deluxe.bin` | 474.784.128 B | WTE-TASK-12, achado 2 |
| `roms/japanese-shift-jis.bin` | 307.187.664 B | esta task — é a que o gate fixa (seção 1) |

**Na europeia** a WTE-TASK-12 mediu **11.952 bytes**, dentro de
`11796..26527` — **offsets 0-based, inclusivos** —, **setores 5 a 11**.

**Na japonesa** os mesmos 11.952 bytes aparecem, distribuídos nos mesmos sete
setores, **mais 3 que a europeia não tem** — 11.955 no total:

```
$ cmp -l work/dd-clean.bin work/dd-run.bin | awk '{p=$1-1;
    if (NR==1) {ini=p; prev=p; n=1; next}
    if (p>prev+304) {print ini".."prev": "n" B"; ini=p; n=0}
    prev=p; n++} END {print ini".."prev": "n" B"}'
11796..13831: 1443 B      ┐
14136..16183: 2048 B      │
16488..18535: 2035 B      │
18840..20887: 1917 B      ├ os sete setores: 11.952 B, os mesmos da europeia
21192..23239: 1906 B      │
23544..25591: 1977 B      │
25896..26527:  626 B      ┘
1921862..1921862:   1 B   ┐ só na japonesa
2012984..2012985:   2 B   ┘
```

Os saltos de 304 bytes entre os sete são os cabeçalhos e o EDC/ECC de setor,
que o editor não toca — por isso a **faixa** da europeia é uma e a **medição**
da japonesa são sete: é a mesma escrita, recortada pelos limites de setor
(`CLAUDE.md`, "Formato da imagem"). As duas de baixo estão em região de dados
(`OFS_TEAM_NAME_2` e `OFS_LINK_ML1`) e continuam sem explicação medida; a
WTE-TASK-19 já tinha visto `1921862` como escrita do arranque que **não** muda
byte na europeia — daí ela não aparecer lá.

**Não copie os extremos do `cmp -l`:** ele numera bytes a partir de 1 e imprime
`11797..26528` para a faixa da europeia. O comando que mede na base certa está
em [`../../wte/re/visual.md`](../../wte/re/visual.md), achado 2.

*Original contra original* continua dando zero — os dois lados gravam os mesmos
bytes. Mas o port terá de **reproduzir** essa gravação, ou o harness terá de
declarar a faixa como exceção conhecida, no mesmo espírito dos 16 bytes do slot
64 do `newWe2002`. Decidir qual, e escrever a razão.

**Decidido: declarar.** O roteiro do gate nasceu com as **nove** faixas acima
como `conhecida:`. Quantas estão declaradas **hoje** não se lê aqui — se lê no
[`golden-01-arranque.txt`](../../wte/tests/roteiros/golden-01-arranque.txt),
que é o arquivo que o veredito consulta; a WTE-TASK-25 já baixou para **duas**
ao fazer o port injetar os sete setores a partir do `dat.bin`. Número de faixa
copiado para prosa envelhece com o primeiro handler que fecha uma delas.

### 3. O lado port não recebe teclado no `:99`

Da WTE-TASK-13: sem window manager o GTK2 nunca considera a janela ativa, e
**nenhuma tecla chega** — nem `xdotool key` depois de `windowfocus`, nem
`key --window`. O mouse funciona. O `wte.exe` não sofre disso, porque o Wine
implementa o próprio foco.

Some com o outro achado da 13 — **o original confirma texto por tecla, não ao
sair do campo; não existe `OnExit` em nenhum dos 96** — e a conta fecha assim:
sem teclado do lado port, a operação "editar nome" não tem como ser comparada.
Ou o harness dirige o port só por mouse, ou o `:99` ganha um window manager
(nenhum instalado; instalar é decisão do usuário).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/golden_check.sh` | criar |
| `wte/tools/golden_run_wte.sh` | criar — lado do original |
| `wte/tools/golden_run_laz.sh` | criar — lado do port |
| `wte/tools/roteiro.sh` | criar — o driver, extraído do `diff_dirigido.sh` |
| `wte/tools/golden_veredito.py` | criar — o veredito, e o que os testes alcançam |
| `wte/tests/roteiros/golden-*.txt` | criar — **e não `wte/tools/roteiros/*.sh`** |

**Correção ao enunciado, registrada na execução:** os roteiros ficam em
`wte/tests/roteiros/`, com os da WTE-TASK-13 e da 19, e são **arquivos de
roteiro** no dialeto já existente — não `.sh`. Roteiro em shell seria um
segundo dialeto para a mesma coisa, e o gate precisa executar o **mesmo**
arquivo nos dois lados.

---

## Critério de conclusão

- [x] As quatro guardas da tabela implementadas
      — `DISPLAY=:99` fixado no `roteiro.sh`; recusa de janela ≥ 400×300 já
      aberta; filtro por `_NET_WM_PID` do processo lançado; `roms/` só como
      origem de cópia, e as duas cópias apagadas por `trap`
- [x] **O crash do oráculo ao selecionar time resolvido** — pela
      [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md): o harness fixa
      `roms/japanese-shift-jis.bin` e o lado oráculo **reprova com código 4**
      se achar `c0000005` no log do Wine
- [x] Controle verde: **PASSOU, byte-idêntico** — oráculo contra oráculo, mesmo
      roteiro, zero divergência
- [x] Decidido: a faixa vira **exceção declarada**, e no roteiro, não no script
      — nove linhas `conhecida:` no
      [`golden-01-arranque.txt`](../../wte/tests/roteiros/golden-01-arranque.txt),
      offsets 0-based e inclusivos. **E a declaração que some reprova** (código
      3): gate que só subtrai exceção passa verde quando o roteiro para de
      exercitar o que dizia
- [x] Positivo: byte plantado detectado — `405228..405228 1 byte(s) data
      OFS_SQUAD_NUMBERS_NATIONAL+512`
- [x] Roteiro de edição parametrizável, um por operação
      — `@IMAGEM@` no lugar do nome do arquivo, e um roteiro por operação em
      `wte/tests/roteiros/golden-*.txt`
- [x] `roms/` nunca tocada; temporário limpo no fim
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-10

- **Resumo do que foi feito:**

  O gate existe e os **três modos** fecharam na mesma tarde:

  | modo | lado A | lado B | resultado medido |
  |---|---|---|---|
  | `controle` | oráculo | oráculo | **PASSOU, byte-idêntico** |
  | `positivo` | oráculo | oráculo + 1 byte plantado | **detectado**, com offset e região |
  | `golden` | oráculo | app Lazarus | **PASSOU**, só as 9 faixas declaradas |

  Verde e vermelho não significam nada sem os dois primeiros, e é por isso que
  eles são modo do script e não experimento avulso: zero divergência no
  `golden` tanto pode ser paridade quanto os dois lados não terem gravado nada.

  **O driver de roteiro virou biblioteca.** O `diff_dirigido.sh` da
  WTE-TASK-19 já tinha o dialeto, a busca de janela por nome e por tamanho e a
  fixação do `:99`; duplicar aquilo no gate seria duas cópias divergindo em
  silêncio, com o sintoma de sempre — diff de bytes com cara de bug do port.
  Extraí para [`roteiro.sh`](../../wte/tools/roteiro.sh), e o `diff_dirigido`
  passou a usá-lo. Regressão medida: roteiro 07 refeito, mesmas 9 faixas, as
  duas réguas fechando.

  **O veredito é Python, e o gate é shell.** A parte que decide — faixa
  declarada contra faixa medida — mora no
  [`golden_veredito.py`](../../wte/tools/golden_veredito.py), com 18 testes;
  shell não é testável e esta é a peça que não pode errar.

  ```
  $ grep -c "    def test_" wte/tools/test_golden_veredito.py
  18
  ```

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/roteiro.sh` | criado — o driver, extraído do `diff_dirigido.sh` |
  | `wte/tools/golden_run_wte.sh` | criado — lado oráculo, com o `c0000005` como falha |
  | `wte/tools/golden_run_laz.sh` | criado — lado port, com a recusa de roteiro com teclado |
  | `wte/tools/golden_veredito.py` | criado — o veredito, três códigos de saída |
  | `wte/tools/test_golden_veredito.py` | criado — 18 testes (`grep -c "    def test_"`) |
  | `wte/tools/golden_check.sh` | criado — o gate, três modos, quatro guardas |
  | `wte/tests/roteiros/golden-01-arranque.txt` | criado — e o par `.port.txt` |
  | `wte/tools/diff_dirigido.sh` | passou a usar a biblioteca |
  | `wte/src/wtemain.pas` | aceita o caminho da imagem como argumento posicional — **guarda e registra, não lê** |
  | `wte/re/fase-2.md` | regerado: a fração da casca caiu de 96,2% para 95,9% |
  | `docs/PLAN-WTE-LAZARUS.md` | §4.4 com a fração nova e o porquê |

- **Problemas encontrados:**

  **O app morria antes de abrir janela quando recebia o caminho da imagem.**
  O `TrataLinhaDeComando` levantava exceção em qualquer argumento que não
  fosse `--show`/`--list`/`--help`, e o gate precisa passar a cópia para o lado
  port — os dois lados têm de receber a **mesma** entrada. Agora um argumento
  posicional é aceito, guardado e registrado no trace; ler continua sendo
  trabalho de handler, que tem gate próprio. Opção desconhecida começando por
  `-` continua sendo erro: engolir `--sho` em silêncio faria a captura da
  WTE-TASK-12 sair do formulário errado.

  **Corrida que falha no meio deixava processo vivo**, e a corrida seguinte
  batia na guarda 2 — que é o comportamento certo da guarda, e uma rodada
  perdida. Os dois lados ganharam `trap` de encerramento.

  **A fração da fase 2 se moveu, e isso é o sistema funcionando.** As 33 linhas
  novas do `wtemain.pas` levaram a casca de 96,2% para 95,9%; o
  `check_fase2.py --check` reprovou até o `fase-2.md` ser regerado, e a §4.4 do
  plano foi corrigida junto. Número medido em doc é para se mover quando a
  medida muda.

  **O que ficou fora, por escrito:** o roteiro do lado port ainda é um arquivo
  separado (`golden-01-arranque.port.txt`), porque o port não abre imagem nem
  recebe teclado no `:99`. Os dois convergem na WTE-TASK-25, e o arquivo diz
  isso no cabeçalho.
