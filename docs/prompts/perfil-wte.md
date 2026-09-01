# Perfil de ciclo — WE2002 Team Editor → Lazarus (`wte/`)

**Este arquivo é o perfil do ciclo `wte/` Lazarus**, e é carregado pelos
prompts de `docs/prompts/` quando o `progresso.md` em vigor o nomeia no campo
`perfil:`. Os prompts têm o **rito** — ler o progresso, achar a próxima
pendente, conferir `depends_on`, medir contra o `fonte_de_verdade` da task,
varrer discrepância, `[x]` só depois do commit. O que é **deste ciclo** mora
aqui.

> **Ciclo fechado.** As 195 tasks e correções desceram para
> [`docs/tasks/concluidos/`](/docs/tasks/concluidos/progresso.md) em
> 2026-09-01. Este perfil continua no lugar porque o `wte/` pode ser reaberto,
> e porque o que ele registra foi medido — não vale para o ciclo vivo, e não
> deve ser lido como se valesse. O perfil em vigor é o que o
> [`progresso.md`](/docs/tasks/progresso.md) nomear.

---

## Contexto essencial — decisões já confirmadas

**Leia isto antes de tocar em qualquer arquivo.** São decisões já tomadas que
**não devem ser revertidas** sem o usuário pedir. A fonte delas é o
[`PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md); se a task em mãos declarar
outro `fonte_de_verdade`, leia o dela.

- **O original é Borland C++Builder 6, não Delphi.** Os dois usam a mesma VCL,
  os mesmos `rtl60.bpl`/`vcl60.bpl` e o mesmo `.dfm`; o que separa é o mangling
  `$qqr`, os símbolos `___CPPdebugHook`/`__GetExceptDLLinfo` e a string
  `c:\bcb\emuvcl\utilcls.h`. (§1.1)
- **Recuperação de especificação, não transcrição.** O decompilador serve para
  *responder perguntas*; a resposta vai para `wte/re/spec/<handler>.md`, e o
  Pascal é escrito **a partir do `.md`**. Nunca cole C++ decompilado em spec nem
  em código. (§2)
- **O que dá para gerar, se gera.** Formulários, esqueletos de unidade,
  offsets, tabelas e a camada de dados inteira saem de gerador. Corrigir arquivo
  gerado à mão não conta como correção — a correção entra no gerador e o
  arquivo é regenerado. (§4.4)
- **A camada de dados vem do `we2002_core` deste repositório, não do `.exe`.**
  Ele já é byte-idêntico ao `ed.exe` nas duas ROMs. (§4.5)
- **O transpilador só digere código deste repositório.** Nunca apontá-lo para
  saída de decompilador: ali o `FORBIDDEN` deixa de segurar e a saída é Pascal
  quebrado com cara de certo. (§8.10)
- **Diff antes de decompilador.** Pergunta de *onde* se responde com `cmp` em
  dois minutos; o decompilador é para pergunta de *fórmula*. (§4.2)
- **"100%" significa toda divergência conhecida e escrita**, não zero
  divergência. (§0, §9)
- **O `newWe2002` está com escopo fechado e verificado.** Mexer em `src/core/`
  exige rodar `ctest` e o golden dele depois. Só a WTE-TASK-18 prevê isso.

---

## Armadilhas medidas neste ciclo

Cada uma custou tempo real, aqui ou no `newWe2002`. As de GUI e de cópia valem
para o repositório inteiro e estão no [`CLAUDE.md`](../../CLAUDE.md); as
específicas deste ciclo são as de engenharia reversa e de gerador.

1. **Ghidra assume `__cdecl`; o C++Builder passa `this` em `EAX`.** Sem
   convenção customizada (`EAX, EDX, ECX`), a saída do decompilador é ruído
   convincente — o pior tipo de erro, porque parece certo. (§8.1)
2. **`[^x]` casa `\n` em regex.** Foi assim que um `Seek(begin)` virou
   `SeekCurrent` no `port_database.py`: compilava, passava nos testes, passava
   no ASan, e só o confronto com o `ed.exe` mostrou.
3. **Diff de controle antes de medir qualquer coisa.** `Load`+`Save` sem editar
   já muda bytes: o `Save` reconstrói as all-star, e o original troca os dois
   primeiros cobradores de cada clube de ML. Sem o controle, toda medição vem
   contaminada.
4. **`Ctrl+A` não seleciona tudo num `TEdit`.** Limpar campo com `End`,
   `shift+Home`, `BackSpace` — senão os dois lados recebem textos diferentes.
5. **Tipo de tamanho dependente de plataforma embaralha número de camisa.**
   `DWORD` virou 64-bit no Linux LP64 e custou o bug inteiro. Em FPC o risco
   irmão é a ordem de bit do `bitpacked record`. (§8.6, §8.11)
6. **Release não é o mesmo teste que Debug.** Um `strcpy` estourando um byte
   era invisível em Debug e derrubava o app em Release com `_FORTIFY_SOURCE`.
7. **Os números da §1 do plano** foram medidos por script descartável em
   2026-08-05; a WTE-TASK-09 os remede com ferramenta versionada e reconcilia.

---

## As duas fontes de verdade binárias

| Fonte | Papel | Pode escrever? |
| --- | --- | --- |
| `we-team-editor/we-team-editor.exe` | alvo da RE, oráculo comportamental | **não** — leitura pura |
| `roms/*.bin` | imagens de teste, ~474 MB cada | **não** — sempre cópia |
| `src/core/` (`we2002_core`) | oráculo de formato, entrada do transpilador | só na rota 2 da WTE-TASK-18, com golden do `newWe2002` depois |

O `.exe` **não é editável** — diferente do `.diz` do projeto `snes`, aqui não há
ferramenta que escreva no binário e nem deve haver.

### Os dois oráculos

- **Oráculo A, comportamental:** `wte.exe` sob Wine 32-bit, dirigido por
  `xdotool` no `:98`. Responde *que bytes esta operação grava?*
- **Oráculo B, de formato:** o `we2002_core`, já byte-idêntico ao `ed.exe`.
  Responde *o que significam estes bytes?*

Combinados, a semântica sai sem decompilar. Ver §4.2 do plano.

---

## O que é gerado

Se o alvo de uma correção estiver nesta lista, **a correção entra no gerador**,
e o arquivo é regenerado. **Editar a saída à mão não é correção — é a
discrepância que a revisão deveria ter pegado.**

| Saída | Gerador |
| --- | --- |
| `wte/re/dfm/*.dfm` | `wte/tools/dfm_extract.py` |
| `wte/forms/*.lfm`, esqueleto das units | `wte/tools/dfm2lfm.py` |
| `wte/src/we2002_offsets.pas`, `we2002_tables.pas` | `wte/tools/gen_tables_pas.py` |
| `wte/src/we2002_{database,player,team,cdimage,textcodec,types}.pas` | `wte/tools/port_database_pas.py` |
| `wte/re/spec/INDICE.md` | `wte/tools/spec_index.py` |

---

## Estrutura

```text
new-we2002-editor/
  docs/
    PLAN-WTE-LAZARUS.md    # fonte das tasks do wte/ Lazarus
    PLAN-LINUX.md          # como o port Qt (newWe2002) foi feito
    PARIDADE-FUNCIONAL.md  # fonte das tasks de paridade do newWe2002
  wte/                     # o projeto Lazarus
    src/ forms/ re/ tools/ tests/ packaging/
  src/core/                # we2002_core -- entrada do transpilador, NAO alvo
  we-team-editor/          # o binario do Obocaman (gitignored)
```

---

## Gates deste ciclo

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor

make wte            # abre o editor do Obocaman (oraculo A) no DISPLAY do shell
make wte-98         # idem, no Xvfb :98
make run-98         # abre o newWe2002 (o port Qt) no :98
make test           # ctest do newWe2002, sem os golden

python3 wte/tools/dfm_extract.py --check       # e os demais geradores
lazbuild wte/wte.lpi                           # a partir da WTE-TASK-02
bash wte/tools/golden_check.sh                 # a partir da WTE-TASK-22
ctest --preset debug                           # o newWe2002 nao regrediu
```

| Se a tarefa ou correção tocou | Gate |
| --- | --- |
| gerador ou saída de gerador | `--check` verde; rodar duas vezes dá bytes iguais |
| Pascal | `lazbuild wte/wte.lpi` sem warning novo |
| comportamento (handler, gravação) | `golden_check.sh` verde, com o **controle** fechando antes |
| `src/core/` | `ctest --preset debug` e o golden do `newWe2002` verdes |

**Contagens que a task afirma se remede, não se relê.** Os valores correntes
estão na §5 de [`wte/re/fase-1.md`](../../wte/re/fase-1.md), que é **gerada** —
não os copie para cá, senão esta linha vira mais um sítio a reconciliar.
Exemplos do que já mudou uma vez: componentes (`~430` → 441), strings com
enchimento (70 → 13), bitmaps (197 → 198), imports de `rtl60`/`vcl60`
(300 → 267). Este arquivo está **dentro** do perímetro do `check_fase1.py`
desde a CORR-WTE-018: número velho afirmado aqui reprova task correta.

---

## Arquivos quentes deste ciclo

Para a matriz de conflito dos prompts em lote, presumir conflito em:
`wte/re/offsets.md`, `wte/re/strings.tsv`, `wte/re/published_methods.tsv`,
`wte/re/tipos.md`, `wte/re/divergencias.md`, `wte/re/spec/*`,
[`PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md).

E um caso que já mordeu: **`wte/Makefile`** — a bateria de `--check` mora ali
(decisão da WTE-TASK-01, ver `wte/README.md`), e toda tarefa de fase 1 que cria
gerador acrescenta um alvo. As 03, 04, 05 e 06 queriam a mesma mão no mesmo
arquivo.

Recursos serializados deste ciclo, além dos do repositório: **Wine /
`work/wineprefix*`** (prefix único por editor, `wineserver` compartilhado),
**`lazbuild` / saída de build** (unidades compiladas e binário únicos), e o
**projeto do Ghidra** (banco de dados único, escrita exclusiva).

---

## Antecipação — os dois precedentes deste ciclo

Tarefa fora da vez só entra com **pedido explícito do usuário**. Duas couberam
no critério, e o critério é o mesmo: `depends_on` inteiramente concluído, e
razão escrita.

- **WTE-TASK-32 (preço)** — plano §10 passo 5, se a 24 e a 25 estiverem
  concluídas. É isolada, não depende de gravação, e valida o ferramental de
  decompilação num alvo pequeno. Até a renumeração de 2026-08-19 isso se
  chamava "fora de ordem", e era: preço era a 30 e o fechamento da fase 4 era a
  29. Depois dela, antecipar virou só escolher quando.
- **WTE-TASK-33 (slots de ML)** — antecipada em 2026-08-19, a pedido. É fase 5,
  e a razão é que a fase 4 dependia dela: a
  [WTE-TASK-27](/docs/tasks/concluidos/27-handlers-de-gravacao.md) tinha o ramo
  de destino de Master League da `0x00404820` parado esperando o contador
  `0x004335c0`, que é a 33 quem calcula. Não era ciclo — a 33 depende só da 20
  —, era inversão de ordem entre fases, e a regra de seleção (fase antes de
  número) faria a 27 ser escolhida para sempre sem nunca fechar.

**O padrão a reconhecer, e este é agnóstico:** tarefa de fase adiante que uma
tarefa da fase corrente precisa. Renumerar resolveria, mas mover uma task
arrasta as vizinhas; antecipar com pedido explícito custa uma linha.

---

## Verificações específicas por fase

**Fase 0-1 (WTE-TASK-01 a 09) — infra e extração estática:**

- O gerador é **determinístico**? Rodar duas vezes dá bytes iguais? Sem isso o
  `--check` é decorativo
- Ele **falha alto** em construção que não reconhece, ou emite parcial? Saída
  truncada que "parece completa" é o furo principal desta fase
- Os 18 DFM decodificaram **inteiros**? Os três que o protótipo truncou
  (`ficha_creditos_equipo`, `ficha_movertodos`, `ficha_warning_2`) estão
  completos?
- Os blobs binários foram **preservados**, ou viraram `<bin N>`?
- O limite da tabela de offsets foi **medido** ou estimado pelo olho? Estimar
  aqui é a armadilha §8.7 — o slot 64 de um array de 63
- Todo número do doc veio de ferramenta versionada, não de script descartável?

**Fase 2 (WTE-TASK-10 a 14) — casca:**

- Algum `.lfm` ou unidade gerada foi **editado à mão**? Rode o `--check` sobre a
  árvore commitada. **Editar o gerado em vez do gerador é discrepância crítica**
- Propriedade que a LCL não tem virou **comentário**, ou sumiu calado? Sumir
  calado é diferença visual que só aparece muito depois da causa
- Os 96 stubs estão na **unidade certa**? A coluna `formulario` existe e foi
  conferida?

**Fase 3 (WTE-TASK-15 a 21) — dados:**

- A ordem de bit do `bitpacked record` foi **medida**, não presumida?
- O teste rodou nas **duas** ROMs, ou só na europeia?
- A camada de dados veio do `we2002_core`, ou foi reescrita do decompilado?

**Fase 4-5 (WTE-TASK-22 a 33) — comportamento e features:**

- O golden rodou com **controle** (original contra original) fechando antes?
- A spec do handler tem campo **evidência**, e ele diz de onde veio o fato?
- Tem decompilado **colado** em spec ou em Pascal? É discrepância crítica
- Gravação divergente ficou **sem veredito** — nem "bug aberto", nem
  "deliberada"?

**Fase 6-7 (WTE-TASK-34 a 40):**

- A bateria cobre **edição múltipla** e **gravação dupla**, ou só operação
  isolada? Gravação dupla continua valendo a pena — o que só aparece na segunda
  gravação não aparece em lugar nenhum. **Mas o motivo mudou:** este item dizia
  "o editor não é idempotente", herdando do `newWe2002` uma frase sobre o
  `ed.exe`. Medido em 2026-08-25
  ([CORR-WTE-109](/docs/tasks/concluidos/CORR-WTE-109.md)), o `wte.exe` **é**
  idempotente nos dois caminhos que tocam `OFS_KICKER` — e o gate serve
  justamente para isso continuar sendo verdade
- Toda exceção do golden tem entrada em `divergencias.md`? Exceção sem entrada é
  divergência silenciosa
- Divergência sem causa conhecida foi classificada como **bug aberto**, ou
  entrou como "deliberada"? Confundir os dois é como lista de problemas
  conhecidos vira desculpa
- A condição "roda sem Wine" foi **testada**, ou presumida?
- Algum asset do Obocaman foi versionado? (`we-team-editor/` é gitignored)
- Foi adicionado `LICENSE`? **Não deve haver.**
