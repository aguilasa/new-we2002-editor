# Corrigir tudo

Você vai trabalhar no projeto **WE2002 Team Editor → Lazarus**, localizado em:

- **Projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`

A documentação de correções está em:

`docs/tasks/`

O arquivo de progresso das correções está em:

`docs/tasks/correcoes-progresso.md`

Os detalhes das correções estão nos arquivos `CORR-<PREFIXO>-*.md` no mesmo
diretório. **`<PREFIXO>` é do ciclo, e quem o declara é a primeira seção do
`correcoes-progresso.md`** — hoje `PES2`, antes `WTE`. Leia o prefixo ali; não
o deduza do prefixo das tasks nem do que este prompt escreve como exemplo.

## Objetivo

Executar **todas** as correções pendentes (`[ ]`) desta invocação, em ordem de
dependência, agrupando em paralelo só o que comprovadamente não interfere.

Este prompt é o irmão em lote do `03-corrigir.md`. **Ele relaxa exatamente uma
regra daquele — "uma CORR por invocação" — e nenhuma outra.** Tudo o mais
(escopo de arquivo por CORR, reproduzir a evidência antes de corrigir, correção
no gerador e não no gerado, `[x]` só depois do commit, um commit por CORR,
reconciliação de doc em commit próprio, nada de `WTE-TASK`) continua valendo
palavra por palavra. Em dúvida sobre qualquer ponto não coberto aqui, o
`03-corrigir.md` é a fonte.

> **EXCLUSÃO OBRIGATÓRIA — sem tasks:**
> Este prompt é exclusivo para `CORR-<PREFIXO>-XXX`. **Nunca** execute `WTE-TASK-XX`
> por aqui — elas são do `01-executar.md` e rastreadas em `progresso.md`.

> **EXCLUSÃO OBRIGATÓRIA — respeitar as decisões confirmadas:**
> Nunca use uma correção como desculpa para editar à mão arquivo que um gerador
> produz, colar saída de decompilador em spec ou em Pascal, apontar o
> transpilador para decompilado, ou escrever no `we-team-editor.exe` / em
> `roms/` — a menos que a CORR diga isso explicitamente e o usuário tenha
> confirmado. Ver `docs/PLAN-WTE-LAZARUS.md` §2, §4.4, §4.5 e §8.10.

Se `$ARGUMENTS` trouxer IDs (`CORR-<PREFIXO>-013 CORR-<PREFIXO>-016`), o lote é **esse
conjunto**, ainda em ordem de dependência. Se trouxer `--plano`, pare depois
da fase 0 e entregue só o plano.

---

## Fase 0 — inventário e plano (sempre, e sempre primeiro)

1. Ler `correcoes-progresso.md` e listar **todas** as `[ ]`, da tabela **e** do
   checklist. Se as duas listas divergirem, a divergência é o primeiro achado
   do relatório — não escolha uma em silêncio.
2. Para cada pendente, ler **só** o cabeçalho do seu `CORR-<PREFIXO>-XXX.md`
   (frontmatter + seções "Problema identificado", "Evidência", "Correção",
   "Arquivos a criar ou modificar"). O escopo de arquivo do `03-corrigir.md`
   continua valendo **dentro** de cada execução: ao corrigir a 013 você não
   abre a 016.
3. Montar a **ordem de dependência**: `depends_on` não satisfeito e não
   presente no lote bloqueia; `depends_on` satisfeito por outra CORR do lote
   força ordem. Empate desfaz por ID crescente.
4. Montar a **matriz de conflito** (seção abaixo) e derivar as ondas.
5. Imprimir o plano antes de tocar em arquivo: ondas, o que é paralelo, o que é
   sequencial, e **por que** cada par ficou sequencial.

---

## Matriz de conflito — o que pode e o que não pode em paralelo

Duas correções só rodam em paralelo se **todas** as condições valerem:

- nenhuma depende da outra;
- os conjuntos de arquivos previstos são **disjuntos**;
- nenhuma das duas toca um **recurso serializado** da tabela abaixo.

### Recursos serializados (uma CORR por vez, sempre)

| Recurso | Por que serializa |
| --- | --- |
| **o `DISPLAY=:98`** | não há window manager, e os dois lados do golden acham a janela por heurística. Duas sessões de GUI simultâneas dirigem a janela uma da outra, e o diff resultante parece bug do port |
| `golden_check.sh` / `work/` | duas cópias de ~474 MB por rodada, num diretório de trabalho único. Duas rodadas simultâneas leem a cópia da outra |
| Wine / `work/wineprefix*` | prefix único por editor; `wineserver` compartilhado |
| qualquer gerador em modo de escrita | regenera a árvore inteira — duas execuções simultâneas leem a saída da outra |
| `lazbuild` / saída de build | unidades compiladas e binário únicos |
| projeto do Ghidra | banco de dados único, escrita exclusiva |
| `git` (index, `HEAD`, commit) | **sempre no thread principal**, nunca dentro de subagente |
| `correcoes-progresso.md` | toda CORR escreve nele; é o arquivo mais garantido de colidir |

**A serialização do `:98` é a mais restritiva deste projeto**, e não tem
equivalente no `snes`. Na prática, **toda CORR que exercita o oráculo, roda o
golden, ou tira captura é sequencial** — o que sobra para paralelizar é
correção de doc, de gerador e de código que não precisa de tela.

### Arquivos quentes (presumir conflito)

A varredura de discrepância do `03-corrigir.md` pode puxar **qualquer** doc para
dentro de uma correção — não dá para prever o conjunto final pela lista da CORR.
Trate como conflito provável qualquer par que possa cair nos mesmos:
`CLAUDE.md`, o plano que a CORR citar, `docs/tasks/progresso.md`,
`wte/re/offsets.md`, `wte/re/strings.tsv`, `wte/re/published_methods.tsv`,
`wte/re/tipos.md`, `wte/re/divergencias.md`, `wte/re/spec/*`,
`docs/prompts/*`, `.claude/commands/*`.

Os wrappers de `.claude/commands/` entram nessa lista pelo mesmo motivo que os
prompts: são versionados e reafirmam o mesmo rito com outras palavras. Correção
de processo costuma ter de tocar o par prompt+wrapper, e duas CORRs de processo
em paralelo colidem ali.

**Na dúvida, sequencial.** O ganho de paralelizar duas correções de doc é de
minutos; o custo de duas edições concorrentes no mesmo `.md` é uma reconciliação
manual e um número que ninguém remede.

### O que é sempre seguro em paralelo

**A reprodução da evidência.** É leitura pura: rodar `objdump`, `strings`,
`grep`, `--check`, `cmp`, `git show`. Faça isso para o lote inteiro de uma vez,
antes de editar qualquer coisa — é barato e é o que separa CORR viva de CORR
envelhecida antes de o trabalho começar.

**Ressalva:** reprodução que exige **abrir o oráculo no `:98`** não é leitura
pura para efeito de paralelismo — ela ocupa o display. Essas vão em série.

---

## Fase 1 — reproduzir a evidência do lote inteiro (paralelo)

Para cada CORR do lote, rodar o comando da seção "Evidência" e comparar com o
que ela descreve. Pode ser em paralelo, um subagente por CORR, **read-only** —
menos as que precisam do `:98`.

Três desfechos, e o terceiro é o que este prompt acrescenta ao `03`:

| Resultado | O que fazer |
| --- | --- |
| bate com a CORR | entra no lote de execução |
| não bate — o sintoma sumiu | **não corrija.** Marque como *envelhecida*, tire do lote, reporte com o comando e a saída |
| não bate — o sintoma é outro, ou maior | tire do lote e reporte. Redimensionar CORR de afogadilho no meio de um lote é pior que no singular |

Uma CORR fora do lote **não bloqueia** as outras, a menos que alguém dependa
dela.

**Achado que vira CORR nova: releia o maior número na hora de criar o arquivo.**
`ls docs/tasks/CORR-*.md | tail -1`, não o número que a fase 0 leu. Num lote
longo a distância entre inventário e criação é de horas, e um `/revisar` no meio
consome números. A CORR-WTE-137 foi criada duas vezes por isso, e a segunda
**sobrescreveu o arquivo da primeira** — mesmo nome, e o `git status` mostra só
uma modificação. Ver `03-corrigir.md`, "Se a discrepância for grande".

---

## Fase 2 — executar, onda a onda

Para cada onda, na ordem:

1. Executar as CORRs da onda — em paralelo se a matriz permitir, senão em
   sequência. Cada execução segue o `03-corrigir.md` §"Como executar" passos 2
   e 3: implementar exatamente a seção **Correção**, mais a discrepância que o
   conserto revelar.
2. **Os subagentes editam; quem commita é o thread principal.** Subagente não
   roda `git`, não roda `lazbuild`, não roda `golden_check.sh`, não roda
   gerador em modo de escrita, não abre janela no `:98`. Se uma CORR precisa de
   um desses, ela é sequencial por definição — está na tabela de recursos
   serializados.
3. Rodar os gates aplicáveis (tabela abaixo), **uma CORR por vez**, mesmo que a
   edição tenha sido paralela.
4. Commitar, **um commit por CORR**, em ordem de ID crescente dentro da onda.
   Reconciliação de doc vai em commit próprio, dizendo no corpo qual correção a
   provocou.
5. Marcar `[x]` no `correcoes-progresso.md` (tabela **e** checklist), preencher
   a coluna **"Concluída em"** com a data do commit daquela CORR (`AAAA-MM-DD`,
   a mesma do `Executado em`), conferir que a célula do ID é link para o
   `CORR-<PREFIXO>-XXX.md`, trocar o `status:` do frontmatter da CORR para
   `concluído`, e preencher o **Log de Execução**. `[x]` descreve estado
   **já commitado**, nunca intenção. Num lote as CORRs podem cair em dias
   diferentes: a data é **por CORR**, não a do fechamento do lote.

### Gates

| Se a correção tocou | Gate |
| --- | --- |
| gerador ou saída de gerador | `--check` verde; rodar duas vezes dá bytes iguais |
| Pascal | `lazbuild wte/wte.lpi` sem warning novo |
| comportamento (handler, gravação) | `golden_check.sh` verde, com o controle (original contra original) fechando antes, e nenhuma janela grande no `:98` na largada |
| `src/core/` | `ctest --preset debug` e o golden do `newWe2002` verdes |
| número em doc | o número novo veio de ferramenta, não de soma à mão |
| qualquer coisa que rode o oráculo | trabalhou sobre cópia; `roms/` intocada; temporário limpo |

### Depois de cada commit, antes do próximo

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git status --short          # limpo para a correção que acabou
grep -rn "<o termo que voce mudou>" docs wte/re .claude CLAUDE.md
```

**A varredura de discrepância se repete a cada CORR, não uma vez no fim.** Num
lote, a correção *k+1* costuma tornar falso um doc que a *k* acabou de escrever
— é a mesma armadilha do singular, só que agora dentro da mesma invocação.

### Quando uma correção falha no meio do lote

- Não marque `[x]`. Registre o status parcial e as pendências no Log de
  Execução, e commite o que estiver **coerente** (se nada estiver, não commite).
- **Não aborte o lote.** Siga para as CORRs que não dependem dela.
- Se o que falhou for um gate global (`lazbuild` não compila, `golden_check.sh`
  vermelho no **controle**, `ctest` do `newWe2002` quebrado), aí **pare o
  lote**: gate global quebrado contamina toda correção seguinte, e commit em
  cima disso é dívida que ninguém acha depois.

O caso mais provável de gate global quebrado aqui é o **controle do golden**:
se original contra original não fecha, o problema é do harness ou do `:98`, não
das correções — e nenhum resultado do lote significa nada até isso voltar.

---

## Fase 3 — fechamento do lote

1. `git status --short` limpo.
2. `git log --oneline` do lote, para conferir um commit por CORR (mais os de
   reconciliação).
3. Conferir que a tabela e o checklist do `correcoes-progresso.md` concordam,
   e que toda linha `[x]` da tabela tem data e link.
4. Varredura final de discrepância pelos termos de todas as CORRs do lote.
5. Se alguma CORR ficou de fora (envelhecida, parcial, bloqueada), ela aparece
   no relatório — nunca some em silêncio.
6. Conferir que `work/` não ficou com cópia de imagem esquecida — cada rodada de
   golden deixa ~950 MB para trás.

---

## Formato de saída esperado

1. **O plano** — lote selecionado, ordem de dependência, ondas, e a justificativa
   de cada par que ficou sequencial
2. **Fase 1** — por CORR: comando, saída, e o veredito (bate / envelheceu /
   mudou de tamanho)
3. Por CORR executada: resumo, arquivos modificados, gates com o **número
   medido**, e o **SHA do commit**
4. As CORRs que ficaram de fora, com o motivo
5. `git status --short` limpo e o `git log --oneline` do lote
6. Bloqueios e pendências

---

## Regra final

Não me entregue um plano e pare — a menos que `$ARGUMENTS` diga `--plano`.
Execute o lote inteiro, um commit por correção, `[x]` só depois do commit.
Paralelize só o que a matriz de conflito autoriza; **na dúvida, sequencial** —
e o `:98` é sempre sequencial.
Nada de `WTE-TASK`, nada de decompilado colado, nada de editar à mão o que um
gerador produz, nada de escrever no `.exe` ou em `roms/`.
`push` só se o usuário pedir.
