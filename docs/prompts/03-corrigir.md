# Corrigir

Você vai trabalhar no projeto **WE2002 Team Editor → Lazarus**, localizado em:

- **Projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`

A documentação de correções está em:

`docs/tasks/`

O arquivo de progresso das correções está em:

`docs/tasks/correcoes-progresso.md`

Os detalhes das correções estão nos arquivos `CORR-WTE-*.md` no mesmo diretório.

## Objetivo

Quero que você execute **uma única correção por invocação** deste prompt. Nada
mais.

> **EXCLUSÃO OBRIGATÓRIA — uma correção por execução, nunca em paralelo:**
> Cada invocação executa exatamente **uma** correção.
> Nunca execute duas em paralelo nem em sequência na mesma invocação.
> Após concluir e commitar, **pare imediatamente**.

1. Leia `correcoes-progresso.md`
2. Identifique a **próxima correção não executada** (primeira com `[ ]`)
3. Respeite a ordem dos IDs e as dependências em `depends_on`
4. Abra **somente** o markdown dessa correção
5. Leia os arquivos mencionados **nessa correção** — e **confirme o problema com
   a ferramenta** antes de corrigir. O sintoma descrito pode já ter sido
   resolvido por uma task posterior; corrigir o que não está mais quebrado é
   como se introduz regressão em código que estava certo
6. Implemente exatamente a correção descrita na seção **Correção**
7. Atualize `correcoes-progresso.md` marcando `[x]`
8. Preencha o **Log de Execução** no arquivo da correção
9. **Pare.** Não leia nem execute a próxima correção

---

## Regras de seleção

1. Primeira correção com `[ ]` no `correcoes-progresso.md`
2. Se `depends_on` não estiver `[x]`, informe o bloqueio e pare
3. Se alguma correção estiver marcada como "em andamento", conclua-a antes

> **EXCLUSÃO OBRIGATÓRIA 1 — escopo de arquivo:**
> Abra **apenas o `CORR-WTE-XXX.md` da correção selecionada**. Não leia os
> outros, mesmo que apontem para o mesmo gerador ou o mesmo formulário.
>
> **EXCLUSÃO OBRIGATÓRIA 2 — uma CORR por execução:**
> Após concluir, **pare**. Não avance para a próxima `[ ]`, mesmo que seja no
> mesmo arquivo.
>
> **EXCLUSÃO OBRIGATÓRIA 3 — sem tasks:**
> Este prompt é exclusivo para `CORR-WTE-XXX`. **Nunca** execute `WTE-TASK-XX`
> por aqui — elas são do `prompts/01-executar.md` e rastreadas em
> `progresso.md`.
>
> **EXCLUSÃO OBRIGATÓRIA 4 — respeitar as decisões confirmadas:**
> Confirme que o fix é compatível com `docs/PLAN-WTE-LAZARUS.md` §2, §4.4, §4.5
> e §8.10. Nunca use a correção como desculpa para: **editar à mão arquivo que
> um gerador produz**, **colar saída de decompilador** em spec ou em Pascal,
> **apontar o transpilador para decompilado**, ou **escrever no
> `we-team-editor.exe` / em `roms/`** — a menos que a CORR diga isso
> explicitamente e o usuário tenha confirmado.

---

## Discrepância achada no caminho: conserte, não só registre

A lista "Arquivos a criar ou modificar" de uma CORR é o **mínimo**, não o teto.
Se durante a execução você achar uma discrepância que a correção cria, revela
ou torna enganosa, **resolva na mesma invocação**. Registrar no Log e seguir em
frente não é resposta: quem lê o doc errado no dia seguinte não lê o seu Log.

Isso vale principalmente para o caso mais comum aqui — **o doc que descrevia o
defeito envelhece junto com o conserto**. Neste repositório o padrão já
apareceu: o `CLAUDE.md` afirmou "Delphi 6" em dois lugares durante meses, e o
plano novo nasceu contradizendo-o; corrigir um sem o outro deixaria o
repositório dizendo as duas coisas.

Alvos prováveis de varredura, por serem os que repetem número e afirmação:

- `docs/PLAN-WTE-LAZARUS.md` (§1 é quase só número medido)
- `docs/tasks/progresso.md` (a seção "Estado medido na criação destas tasks")
- `docs/tasks/<a task de origem>.md`
- `wte/re/*.md`
- `CLAUDE.md`

Antes de commitar, faça a varredura:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "<o termo ou numero que voce mudou>" docs wte/re CLAUDE.md
```

Toda ocorrência que ficou falsa, incompleta ou apontando para o estado velho
entra nesta invocação.

**Como isso convive com o escopo (não há conflito):**

| Você achou | O que fazer |
| --- | --- |
| doc que a sua correção tornou falso ou incompleto | **conserte agora** |
| número que a sua ferramenta remede e não bate com o doc | **conserte agora**, com a data |
| rótulo ambíguo que a sua mudança cria | **conserte agora** |
| bug ou dívida sem relação com esta CORR | **abra `CORR-WTE-XXX` novo** e siga |
| handler a implementar, formulário a gerar, trabalho de `WTE-TASK` | **não faça** — as exclusões 2, 3 e 4 continuam valendo |

**Commit separado.** A correção num commit; a reconciliação de doc que ela
obrigou, em commit próprio, dizendo no corpo qual correção o provocou. Dois
commits na mesma invocação está certo.

**Se a discrepância for grande** — muda a conclusão de uma task, exige rodar o
golden inteiro (que custa ~1 GB de temporário e uma sessão de Wine), ou toca
decisão do plano — não a resolva de afogadilho: abra a CORR nova, registre o que
mediu, e reporte.

---

## Arquitetura do projeto

### O que é leitura pura

| Fonte | Papel |
| --- | --- |
| `we-team-editor/we-team-editor.exe` | alvo da RE e oráculo comportamental. **Não editável** |
| `roms/*.bin` | as duas imagens de teste, ~474 MB cada. **Sempre cópia** |

Não existe ferramenta que escreva no `.exe`, e não deve haver. Diferente do
projeto `snes`, onde o `.diz` é editado pelo `ImportCli`.

### O que é gerado

Se o alvo da correção estiver nesta lista, **a correção entra no gerador**, e o
arquivo é regenerado:

| Saída | Gerador |
| --- | --- |
| `wte/re/dfm/*.dfm` | `wte/tools/dfm_extract.py` |
| `wte/forms/*.lfm`, esqueleto das units | `wte/tools/dfm2lfm.py` |
| `wte/src/we2002_offsets.pas`, `we2002_tables.pas` | `wte/tools/gen_tables_pas.py` |
| `wte/src/we2002_{database,player,cdimage,textcodec,types}.pas` | `wte/tools/port_database_pas.py` |
| `wte/re/spec/INDICE.md` | `wte/tools/spec_index.py` |

**Editar a saída à mão não é correção — é a discrepância que a revisão deveria
ter pegado.**

### Estrutura

```text
new-we2002-editor/
  docs/
    PLAN-WTE-LAZARUS.md    # fonte de verdade deste projeto
    tasks/                 # tasks, CORRs e progresso
    prompts/               # estes prompts
  wte/
    src/ forms/ re/ tools/ tests/ packaging/
  src/core/                # we2002_core -- entrada do transpilador
  we-team-editor/          # binario do Obocaman (gitignored)
  roms/                    # as duas imagens (gitignored)
  work/                    # copias de trabalho (gitignored)
```

### Comandos de validação

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor

python3 wte/tools/<gerador>.py --check    # o gerado bate com o commitado
lazbuild wte/wte.lpi                      # o app compila
bash wte/tools/golden_check.sh            # o gate de comportamento
ctest --preset debug                      # o newWe2002 nao regrediu
```

### A regra do `:99`

Toda execução com GUI acontece no `DISPLAY=:99`, com o `XAUTHORITY` resolvido
pelo `ps` (ver `CLAUDE.md`). **Feche qualquer janela grande no `:99` antes de
rodar o golden** — os dois lados acham a janela por heurística, e uma sobra de
teste manual é dirigida em vez da que está sob teste.

---

## Como executar

### 1) Ler contexto

- Ler `correcoes-progresso.md`
- Ler o `CORR-WTE-XXX.md`
- **Reproduzir a evidência** da seção "Evidência" com o mesmo comando. Se o
  resultado não bater com o que a CORR descreve, **pare e reporte** — a CORR
  pode ter envelhecido
- Se a correção tocar comportamento, reler a spec do handler em `wte/re/spec/`

### 2) Implementar

- Implementar exatamente o que está na seção **Correção**
- Não antecipar trabalho de outra fase. A lista de arquivos da CORR é o
  **mínimo**: discrepância que o conserto revelar entra nesta invocação, na
  regra "Discrepância achada no caminho" acima
- **Se o alvo for arquivo gerado, a correção entra no gerador e a árvore é
  regenerada.** Ver a tabela acima
- **Se a correção for de spec, ela não pode virar transcrição.** O campo
  evidência diz de onde veio o fato; trecho de decompilado vai parafraseado,
  nunca copiado (§2)
- **Se a correção tocar `src/core/`**, lembre que o `newWe2002` está com escopo
  fechado e verificado: rode `ctest` e o golden dele depois, e diga o resultado

### 3) Validar

Antes de marcar como concluída, todos os itens do checklist **Verificação** da
CORR, mais os gates que se aplicarem:

| Se a correção tocou | Gate |
| --- | --- |
| gerador ou saída de gerador | `--check` verde; rodar duas vezes dá bytes iguais |
| Pascal | `lazbuild wte/wte.lpi` sem warning novo |
| comportamento (handler, gravação) | `golden_check.sh` verde, com o **controle** (original contra original) fechando antes |
| `src/core/` | `ctest --preset debug` e o golden do `newWe2002` verdes |
| número em doc | o número novo veio de ferramenta, não de soma à mão |
| qualquer coisa que rode o oráculo | trabalhou sobre cópia; `roms/` intocada |

Antes de fechar, a varredura de discrepância:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "<o termo que voce mudou>" docs wte/re CLAUDE.md
```

Toda ocorrência que ficou falsa, incompleta ou apontando para o estado velho é
trabalho **desta** invocação.

Se a correção ficar parcialmente pronta:
- Não marcar como concluída
- Atualizar o **Log de Execução** com o status parcial e as pendências

### 4) Atualizar progresso

Se concluída:
- Trocar `[ ]` por `[x]` no `correcoes-progresso.md` (tabela E checklist)
- Preencher a coluna **"Concluída em"** com a data do commit que aplicou a
  correção (`git log -1 --date=short --pretty=%ad`), formato `AAAA-MM-DD`. É a
  mesma data do `Executado em` do Log — se divergirem, uma delas está errada
- Conferir que a célula do ID é link para o markdown da correção
  (`[CORR-WTE-XXX](CORR-WTE-XXX.md)`, **relativo simples**); se a linha veio sem
  link, ponha
- Preencher o **Log de Execução**:
  - **Executado em:** data de hoje
  - **Resumo do que foi feito:** 2-3 linhas
  - **Problemas encontrados:** ou "Nenhum"
  - **Arquivos criados/modificados:** lista

> **Marcar `[x]` não é o passo final — o commit é.** `[x]` descreve um estado
> que precisa **já existir commitado** quando você escrever isso, não uma
> intenção.

### 5) Commit

Código e documentação da correção juntos, no mesmo commit:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git add <arquivos específicos> docs/tasks/CORR-WTE-XXX.md docs/tasks/correcoes-progresso.md
git commit -m "fix: <titulo curto no imperativo>"
```

- **Inglês, conventional commit** — `fix:`, `docs:`, `refactor:`… Primeira linha
  < 72 caracteres, imperativo
- O corpo diz **o que se aprendeu** — as boas mensagens deste repo registram a
  armadilha que quase pegou
- **Sem footer de co-autoria**
- Nunca `git add -A` nem `git add .`
- **Não versione:** `we-team-editor/`, `roms/`, `work/`, saída de build,
  cópias de imagem, projeto do Ghidra
- **`git commit` precisa rodar de fato.** Depois, `git status --short` limpo
  para esta correção
- **Existe remote**, mas **`push` só se o usuário pedir**

---

## Formato de saída esperado

1. Qual correção foi selecionada e por quê
2. **Confirmação de que o problema foi reproduzido**, com o comando e a saída
3. Resumo do que foi feito
4. Arquivos criados ou modificados
5. Resultado de cada gate aplicável, com o número medido
6. **SHA do commit** e confirmação de `git status --short` limpo
7. Bloqueios ou pendências

---

## Regra final

Não me entregue um plano.
Execute **uma única** correção pendente (a próxima `[ ]`), atualize o progresso
ao final e **pare**.
**Não marque `[x]` sem o commit já ter sido feito.**
Não avance para a seguinte mesmo que seja no mesmo arquivo.
Uma correção por invocação — nunca em paralelo, nunca em sequência na mesma
invocação.
