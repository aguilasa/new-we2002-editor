# Correções — visualizador 3D da aparência do jogador

Correções abertas pelo `/revisar` sobre as tasks deste ciclo. O andamento das
**tarefas** fica em [`progresso.md`](/docs/tasks/looks/progresso.md).

**O prefixo deste pool é `CORR-LOOKS-`**, com numeração contínua a partir de
`001`. O pool é único dentro do ciclo, e não se cruza com o de nenhuma outra
pasta — o ciclo de PES2 tem o seu em
[`/docs/tasks/correcoes-progresso.md`](/docs/tasks/correcoes-progresso.md), o
do port do `.mcr` em
[`/docs/tasks/port-mcr/correcoes-progresso.md`](/docs/tasks/port-mcr/correcoes-progresso.md),
e o ciclo arquivado, o dele em
[`/docs/tasks/concluidos/correcoes-progresso.md`](/docs/tasks/concluidos/correcoes-progresso.md).

## Resumo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
| -- | -------------- | ------ | ----------- | ------ | ------------ |
| [CORR-LOOKS-001](/docs/tasks/looks/CORR-LOOKS-001.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | A raiz do Superpack tem treze pastas de jogo, não catorze | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-002](/docs/tasks/looks/CORR-LOOKS-002.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | O comentário do `.gitignore` guarda o número que a própria task derrubou | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-003](/docs/tasks/looks/CORR-LOOKS-003.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | `superpack_count.py` descarta entrada ilegível em silêncio | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-004](/docs/tasks/looks/CORR-LOOKS-004.md) | [LOOKS-TASK-01](/docs/tasks/looks/01-base-legal-e-linhagem.md) | A LOOKS-TASK-18 se contradiz sobre as 50 tuplas em dois bullets seguidos | Baixa | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-005](/docs/tasks/looks/CORR-LOOKS-005.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | A guarda dos dois discos não tem quem a chame, e nada obriga a 03 a chamá-la | Alta | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-006](/docs/tasks/looks/CORR-LOOKS-006.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | A recusa do `/SELECT.BIN` sai como `digest mismatch` pelado | Média | [x] concluída | 2026-09-14 |
| [CORR-LOOKS-007](/docs/tasks/looks/CORR-LOOKS-007.md) | [LOOKS-TASK-02](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) | O `layout.py` diz que não faz I/O, e faz | Baixa | [x] concluída | 2026-09-14 |

**Legenda de status:** `[ ] pendente` · `[~] em andamento` · `[x] concluída`

**Criticidade** é sobre o efeito, não sobre o tamanho do conserto:

- **Alta** — a task entregou algo que mede errado, ou um gate que passa sem
  medir. Neste ciclo isso inclui qualquer guarda que fique verde lendo o disco
  errado, porque esse erro não tem sintoma.
- **Média** — o resultado está certo mas a evidência não sustenta, ou o código
  viola uma das três regras de desenho.
- **Baixa** — documentação, número que não reproduz, link ou nome.

## Checklist

- [x] CORR-LOOKS-001 — treze pastas na raiz do Superpack, não catorze
- [x] CORR-LOOKS-002 — o `.gitignore` ainda descreve a raiz com o número da subpasta
- [x] CORR-LOOKS-003 — `superpack_count.py` tem de falhar alto no que não conseguiu ler
- [x] CORR-LOOKS-004 — o primeiro bullet da LOOKS-TASK-18 desmente o terceiro
- [x] CORR-LOOKS-005 — nada obriga o `iso_source.py` a passar pela guarda
- [x] CORR-LOOKS-006 — o `/SELECT.BIN` recusa sem dizer que o disco é o inglês
- [x] CORR-LOOKS-007 — o docstring do `layout.py` promete o que a dívida da 03 ainda deve

## Detalhes por correção

### CORR-LOOKS-001

- **Arquivo com problema:** `NOTICE.md`, `docs/PLAN-LOOKS-PY.md` §2 e o Log da
  `01-base-legal-e-linhagem.md`
- **Sintoma:** os três dizem "catorze pastas de jogo" na raiz do Superpack; são
  treze, e a frase do plano lista treze nomes logo em seguida
- **Como foi detectado:** `python tools/looks/superpack_count.py
  "C:/games/we2002/Superpackv6"` imprime catorze **linhas**, das quais uma é o
  `Cronologia We-Pes-IssPro.htm`; um `os.listdir` separando por tipo dá 13 e 1
- **Fix:** trocar o número nos três, dizendo "pastas" e não "jogos" — as três
  `We2000 *` são um jogo só

### CORR-LOOKS-002

- **Arquivo com problema:** `.gitignore`, comentário da entrada `/Superpackv6/`
- **Sintoma:** o comentário descreve a coletânea inteira como "4,2 GB, 28.720
  arquivos", que é a subpasta `We2002\` — exatamente o erro que esta task
  corrigiu no plano e no `NOTICE.md`, no mesmo commit
- **Como foi detectado:** confronto das três descrições do Superpack no
  repositório contra a saída do `superpack_count.py` (4,50 GiB, 31.790)
- **Fix:** `4,5 GiB, 31.790 arquivos` no comentário, com meia linha dizendo que
  28.720 deles estão em `We2002\`

### CORR-LOOKS-003

- **Arquivo com problema:** `tools/looks/superpack_count.py`
- **Sintoma:** arquivo ilegível some da conta (`except OSError: continue`),
  entrada de topo ilegível some da repartição (`except OSError: pass`) e
  subpasta sem permissão some inteira, porque `os.walk` roda com o
  `onerror=None` de default. A saída sai somada e com cara de completa
- **Como foi detectado:** leitura dirigida pela pergunta que o `02-revisar.md`
  faz de toda ferramenta — falha alto ou emite parcial? — e por
  `os.walk` sobre raiz ilegível devolver zero entrada sem erro. O número de
  hoje está certo: a revisão o reproduziu byte a byte
- **Fix:** contar o que foi pulado, imprimir `skipped: N`, sair != 0 quando
  `N > 0`, e um caso vermelho no `self_check()` exigindo `skipped == 1`

### CORR-LOOKS-004

- **Arquivo com problema:** `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md`
- **Sintoma:** o primeiro bullet do Contexto diz que os 50 JPGs são "nomeados
  pela tupla exata" e o terceiro diz que são 49 — o achado entrou por bullet
  novo sem corrigir a frase que ele desmente
- **Como foi detectado:** leitura do arquivo contra a §5.4 do plano, que a
  mesma execução corrigiu certo, mais a contagem da pasta (50 `.jpg`, o
  primeiro em ordem sendo `0.jpg`)
- **Fix:** reescrever o primeiro bullet na forma da §5.4

### CORR-LOOKS-005

- **Arquivo com problema:** `docs/tasks/looks/03-fonte-de-disco-e-layout.md` e
  a §4.5 do plano
- **Sintoma:** `layout.require()` recusa certo, mas o único chamador é o
  `_check_discs()` — que a 03 tem por critério **mover**. Nenhum critério da 03
  manda o `iso_source.py` passar pela guarda, e fechada ao pé da letra o ciclo
  fica com uma guarda testada e inalcançável
- **Como foi detectado:** `grep -rn "require(" tools/ --include=*.py` acha três
  ocorrências, todas dentro do próprio `layout.py`, mais a leitura do critério
  da 03
- **Fix:** item de critério na 03 exigindo que toda leitura passe por
  `layout.require()`, com caso vermelho vivo pelo `iso_source.py`, e a §4.5
  dizendo quem chama a guarda e não só que ela existe

### CORR-LOOKS-006

- **Arquivo com problema:** `tools/looks/layout.py`, ramo de dica do `require()`
- **Sintoma:** `/SELECT.BIN` não está em `TEXTURE_FILES` nem em
  `GEOMETRY_FILES`, então recusa com `digest mismatch` pelado — a mensagem que
  o docstring do módulo diz ser a errada. É um dos dois arquivos que diferem
  entre os discos, e a causa provável da recusa é a mesma do `DAT2D.BIN`
- **Como foi detectado:** `require(layout.SELECT, …)` direto, comparado com o
  mesmo estímulo no `DAT2D.BIN`; e os digests dos dois discos remedidos
  (`86d14a66…` × `c9e1eaf8…`)
- **Fix:** dica própria para o `/SELECT.BIN` e um `assert` no `self_check()` de
  que **todo** caminho de `DIGEST` produz dica não vazia

### CORR-LOOKS-007

- **Arquivo com problema:** `tools/looks/layout.py`, docstring de topo
- **Sintoma:** diz "It also does no I/O" e o `_check_discs()` do mesmo arquivo
  abre duas imagens de CD. A dívida é conhecida e está na 03; o que está errado
  é afirmar hoje a propriedade que só vale depois dela
- **Como foi detectado:** leitura do módulo contra ele mesmo — `grep -n
  "iso.Image\|import iso" tools/looks/layout.py` dá três linhas
- **Fix:** ressalva no docstring, com a data e o destino, e a linha da 03
  mandando removê-la junto com a função

