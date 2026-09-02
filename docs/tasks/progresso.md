# Progresso — mapeamento do Pro Evolution Soccer 2 (PSX), rumo a um editor

Rastreamento das tasks de [`../PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md), que
é a fonte de verdade do projeto. Este arquivo registra **andamento**; o plano
registra **objetivo e critério**. Divergência entre os dois se resolve a favor
do plano.

**Perfil deste ciclo:** [`/docs/prompts/perfil-pes2.md`](/docs/prompts/perfil-pes2.md).

Os prompts de `docs/prompts/` têm o **rito** e são agnósticos de projeto; o que
é **deste ciclo** — decisões confirmadas, armadilhas, fontes binárias, o que é
gerado, os gates, os arquivos quentes e as verificações por fase — mora no
perfil, e é este campo que o nomeia. Mesma mecânica do `fonte_de_verdade` da
task, um nível acima: a task nomeia o plano contra o qual se mede, o progresso
nomeia o perfil sob o qual o ciclo roda. O ciclo anterior tem o seu em
[`/docs/prompts/perfil-wte.md`](/docs/prompts/perfil-wte.md), e ele **não vale
aqui**.

**Projeto separado do `newWe2002`, do `wte/` e dos planos de Windows.** Não
compartilha build nem código: nada em `src/` sabe o que é PES2, e
`tools/pes2/` é Python 3 e shell puros. O que compartilha é **conhecimento de
formato** — a aritmética de setor, os 69 `OFS_*` de `Offsets.hpp` como índice
de onde procurar (§1.4 do plano), e o `KanjiToAscii` do WE2002, que decodifica
o título de save do PES2 sem uma linha de adaptação. A §6.9 do plano **proíbe**
estender o `we2002_core` para PES2; o que for compartilhado é copiado com
atribuição no comentário.

**Este pool nasce em 2026-09-01** e resolve o item que estava aberto desde
2026-08-30 na §7.1 do [PES2-AJUSTES](/docs/PES2-AJUSTES.md): *"criar as tasks
das seis fases … ou decidir que o projeto segue fora do pool."* Enquanto não
existiam tasks, **o backlog de PES2 era a §7 daquele arquivo**. Agora é este
quadro; a §7 vira registro histórico.

**A Fase 7 entrou em 2026-09-01**, depois de medir que as features do
[PLAN-FEATURES](/docs/PLAN-FEATURES.md) — escrito para o WE2002 a partir das
ferramentas do CARP — se aplicam ao PES2 sem tradução: mesmo cabeçalho de
contêiner, mesmo codec LZSS, 2.070 bytes de fluxo comprimido idênticos entre
os dois discos, e o mesmo cabeçalho VAB nos `.RA`. A evidência está na §1.14
do plano. Ela **corre em paralelo** com as Fases 3 a 5 e trava só a
PES2-TASK-22.

## Resumo

| ID | Tarefa | Fase | Dependências | Status | Concluída em | Revisado em |
| -- | ------ | ---- | ------------ | ------ | ------------ | ----------- |
| [PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md) | `numpy` e desmontador MIPS — decisão do dono da máquina | 0 | — | ✅ Concluído | 2026-09-01 | 2026-09-01 |
| [PES2-TASK-02](/docs/tasks/02-poke-por-conjunto-de-copias.md) | `poke.py` — gravação pelo conjunto de cópias | 2 | — | ✅ Concluído | 2026-09-01 | 2026-09-01 |
| [PES2-TASK-03](/docs/tasks/03-direcao-do-emulador.md) | Direção do DuckStation — navegar e capturar | 2 | — | ⬜ Pendente | — | — |
| [PES2-TASK-04](/docs/tasks/04-poke-de-validacao.md) | O `poke` de PIEMONTE em todas as telas — **fecha a Fase 2** | 2 | 02, 03 | ⬜ Pendente | — | — |
| [PES2-TASK-05](/docs/tasks/05-diferencial-de-cartao.md) | Harness de diferencial de memory card | 3 | 03 | ⬜ Pendente | — | — |
| [PES2-TASK-06](/docs/tasks/06-registro-de-jogador-no-cartao.md) | Estrutura do registro de jogador, pelo cartão | 3 | 05 | ⬜ Pendente | — | — |
| [PES2-TASK-07](/docs/tasks/07-dump-de-ram-e-casamento.md) | Dump de RAM e casamento com o bloco do disco | 3 | 06 | ⬜ Pendente | — | — |
| [PES2-TASK-08](/docs/tasks/08-indice-do-bloco-de-nomes.md) | Os 624 candidatos de 16 bits — há índice? | 3 | — | ⬜ Pendente | — | — |
| [PES2-TASK-09](/docs/tasks/09-os-blocos-extras-de-selectc.md) | Os 25 blocos de nome depois do pool | 3 | — | ⬜ Pendente | — | — |
| [PES2-TASK-10](/docs/tasks/10-fechamento-fase-3.md) | Fechamento da Fase 3 — o registro de jogador | 3 | 06, 07, 08, 09 | ⬜ Pendente | — | — |
| [PES2-TASK-11](/docs/tasks/11-elenco-de-time.md) | Elenco por time — que jogador pertence a que clube | 4 | 10 | ⬜ Pendente | — | — |
| [PES2-TASK-12](/docs/tasks/12-formacoes.md) | Formações — a tabela tática por time | 4 | 11 | ⬜ Pendente | — | — |
| [PES2-TASK-13](/docs/tasks/13-uniforme-e-cores.md) | Uniforme e cores de time | 4 | 11 | ⬜ Pendente | — | — |
| [PES2-TASK-14](/docs/tasks/14-bandeiras.md) | Bandeiras — forma e cores | 4 | 13 | ⬜ Pendente | — | — |
| [PES2-TASK-15](/docs/tasks/15-master-league.md) | Master League — custos, slots e elencos | 4 | 11 | ⬜ Pendente | — | — |
| [PES2-TASK-16](/docs/tasks/16-fechamento-fase-4.md) | Fechamento da Fase 4 — o resto do banco | 4 | 11, 12, 13, 14, 15 | ⬜ Pendente | — | — |
| [PES2-TASK-17](/docs/tasks/17-formato-do-mapa.md) | O formato do `pes2_map.json` | 5 | 10 | ⬜ Pendente | — | — |
| [PES2-TASK-18](/docs/tasks/18-mapa-consolidado.md) | `pes2_map.json` — o mapa consolidado | 5 | 16, 17 | ⬜ Pendente | — | — |
| [PES2-TASK-19](/docs/tasks/19-gerador-e-guarda.md) | O gerador — do mapa ao código, com `--check` | 5 | 18 | ⬜ Pendente | — | — |
| [PES2-TASK-20](/docs/tasks/20-round-trip-pelo-mapa.md) | Round-trip headless pelo mapa | 5 | 19 | ⬜ Pendente | — | — |
| [PES2-TASK-21](/docs/tasks/21-fechamento-fase-5.md) | Fechamento da Fase 5 — **o portão da Fase 6** | 5 | 04, 18, 20 | ⬜ Pendente | — | — |
| [PES2-TASK-22](/docs/tasks/22-decisao-de-linguagem-e-ui.md) | Decisão de linguagem e UI do editor | 6 | 21, 30 | ⬜ Pendente | — | — |
| [PES2-TASK-23](/docs/tasks/23-editor-leitura.md) | O editor — leitura e exibição | 6 | 22 | ⬜ Pendente | — | — |
| [PES2-TASK-24](/docs/tasks/24-editor-gravacao.md) | O editor — gravação | 6 | 23 | ⬜ Pendente | — | — |
| [PES2-TASK-25](/docs/tasks/25-verificacao-final.md) | Verificação final contra a definição de pronto | 6 | 24 | ⬜ Pendente | — | — |
| [PES2-TASK-26](/docs/tasks/26-codec-lzss.md) | O codec LZSS dos contêineres `BIN/*.BIN` | 7 | — | ✅ Concluído | 2026-09-01 | 2026-09-01 |
| [PES2-TASK-27](/docs/tasks/27-conteiner-e-tim.md) | Cabeçalho de contêiner e entradas TIM | 7 | 26 | ✅ Concluído | 2026-09-01 | 2026-09-01 |
| [PES2-TASK-28](/docs/tasks/28-t-name-copias-de-idioma.md) | `T_NAME_I`/`T_NAME_S` — o conjunto de cópias por idioma | 7 | 27 | ⬜ Pendente | — | — |
| [PES2-TASK-29](/docs/tasks/29-gravacao-de-asset.md) | Gravação de asset — fit-or-fail | 7 | 27 | ✅ Concluído | 2026-09-01 | 2026-09-01 |
| [PES2-TASK-30](/docs/tasks/30-fechamento-fase-7.md) | Fechamento da Fase 7 — **o portão da 22** | 7 | 27, 28, 29 | ⬜ Pendente | — | — |
| [PES2-TASK-31](/docs/tasks/31-audio-ra-e-vag.md) | Áudio — o banco `.RA` (VAB) e os VAG | 7 | — | ⬜ Pendente | — | — |
| [PES2-TASK-32](/docs/tasks/32-poc-do-mcp-do-duckstation.md) | Prova de conceito do MCP do DuckStation | 0 | — | ⬜ Pendente | — | — |

**Legenda:** ⬜ Pendente · 🔄 Em andamento · ✅ Concluído · ❌ Bloqueado · ⏭️ Pulado

**As duas colunas de data são datas de commit**, não datas de intenção.

- **"Concluída em"** — o commit que fechou a tarefa. Tarefa pendente leva `—`.
- **"Revisado em"** — o commit da revisão. Tarefa concluída e ainda não
  revisada leva `⬜ pendente`; tarefa que nem começou leva `—`, porque não há o
  que revisar.

**Revisão sem discrepância também preenche a coluna.** É resultado legítimo, e
sem a data não há como distinguir "revisada, nada achado" de "nunca revisada".

**Não há task de Fase 0 nem de Fase 1 de trabalho.** As duas estão fechadas e
verdes desde 2026-08-30, com ferramenta versionada e reexecutável (§5.1 e §5,
Fase 1 do plano). A única task de fase 0 no quadro — a PES2-TASK-01 — é uma
**decisão do dono da máquina** que sobrou da §7.1 do `PES2-AJUSTES.md`, e não
bloqueava nada até a Fase 4. Foi tomada em 2026-09-01, com instalação: a
Fase 0 está inteira fechada.

**A Fase 2 entra com um item só.** A varredura, as contagens, os digests e a
correspondência entre as oito listas estão feitos; falta o `poke` de
validação, e é ele que fecha a fase — as PES2-TASK-02 a 04 são exatamente isso,
partido em ferramenta, direção e medida.

---

## Escopo e fases

O projeto entrega um **mapa de offsets versionado** da imagem de PES2 e, sobre
ele, um editor que lê e grava direto no `.bin`. Ele se verifica contra **o
próprio jogo rodando** — não há editor conhecido para PES2, e portanto não há
oráculo (§4.1 do plano). Ver [`../PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md)
para o objetivo completo e o modelo de verificação.

| Fase | Tasks | O que entrega |
| --- | --- | --- |
| 0 — Infra | 01 | `iso.py`, round-trip, controle negativo, emulador e o ferramental das fases 3–4 — **fechada** |
| 1 — Diferencial barato | — | âncoras `OFS_*`, diff entre releases — **fechada** |
| 2 — Inventário de texto | 02 a 04 | o `poke` de validação, verificado em tela |
| 3 — O registro de jogador | 05 a 10 | campo, deslocamento, largura em bits, domínio |
| 4 — O resto do banco | 11 a 16 | elenco, formação, uniforme, bandeira, Master League |
| 5 — Mapa e leitor | 17 a 21 | `pes2_map.json`, gerador, round-trip headless |
| 6 — Editor | 22 a 25 | o editor, e a verificação contra a definição de pronto |
| 7 — Assets do disco | 26 a 31 | codec LZSS, contêiner e TIM, cópias por idioma, gravação, áudio — **em paralelo com 3 a 5** |

**O que não pode ser pulado:**

- **A 02 antes da 04.** Não há como gravar em todas as cópias sem o gravador
  que sabe o conjunto delas — e gravar uma só cópia produz um jogo
  inconsistente, que é o modo de falha que a §6.1 do plano cataloga.
- **A 03 antes da 04.** Sem chegar às telas não há como medir o `poke`. O
  jogo é o oráculo; tela não vista é afirmação não verificada.
- **A 05 antes da 06.** O cartão é a única fonte de campo **rotulado** — quem
  editou sabe o quê. Sem o ciclo, "o byte 7 mudou" não diz de que campo.
- **A 10 antes da 11.** O elenco de time indexa a tabela de jogador; sem saber
  qual das duas tabelas (o pool de 1.399 ou a lista de 1.449 do executável) o
  índice aponta, metade dos elencos sai errada e a lista continua parecendo um
  elenco.
- **A 17 antes da 18.** O formato do mapa já se provou insuficiente três vezes
  antes de haver um registro: delta assinado, contagem por tabela,
  correspondência por conteúdo. Escrever o mapa e descobrir a quarta custa
  reescrever tudo.
- **A 21 antes da 22.** É o portão da §0. Decidir linguagem e UI antes de o
  mapa estar verificado é decidir sobre o que a UI não tem o que mostrar.
- **A 26 antes da 27.** Não há como parsear a lista de entradas de um
  contêiner sem descomprimi-lo, e o início do fluxo depende do cabeçalho de
  largura variável da §6.13 — cravar constante lê do lugar errado em 205 dos
  208 arquivos.
- **A 30 antes da 22.** Mesmo argumento do item acima, uma camada adiante: a
  Fase 7 acrescentou grade de imagem × paleta, import/export e cópias por
  idioma. Decidir a UI sem a lista que a 30 entrega desenha uma janela sem
  lugar para metade do que o editor vai mostrar.

---

## Grafo de dependências

```text
Fase 0/2
  01 (decisão, solta)

  02 ──┐
  03 ──┴──► 04 ─────────────────────────────┐
       │                                     │
Fase 3 └──► 05 ──► 06 ──► 07 ──┐             │
            08 ───────────────┤             │
            09 ───────────────┴──► 10 ──┬───┼──► 17 ──┐
                                        │   │         │
Fase 4                                  └─► 11 ──┬──► 12
                                                 ├──► 13 ──► 14
                                                 └──► 15
                                            11..15 ──► 16 ──► 18 ◄─┘
Fase 5                                                      18 ──► 19 ──► 20
                                                      04, 18, 20 ──► 21
Fase 6                                                  21, 30 ──► 22 ──► 23 ──► 24 ──► 25

Fase 7 (paralela, não depende de nenhuma das acima)
  26 ──► 27 ──┬──► 28 ──┐
              └──► 29 ──┴──► 30 ──────────────────────────────► (portão da 22)
  31 (áudio, solto e fora do portão)
```

**Sequência mínima de execução:**

```text
1.  02, 03 em paralelo — nenhuma depende da outra
2.  04 (fecha a Fase 2; é o primeiro laço fechado do projeto)
3.  05, 08, 09 em paralelo — a 08 e a 09 são leitura pura e não precisam do emulador
4.  06, depois 07
5.  10 (fechamento da Fase 3)
6.  11, e daí 12, 13, 15 em paralelo; 14 depois da 13
7.  16 (fechamento da Fase 4)
8.  17 pode ser antecipada — ver abaixo
9.  18, 19, 20, 21
10. 22, 23, 24, 25

A Fase 7 corre por fora, a qualquer momento a partir de agora:

    a. 26 (leitura pura, sem emulador — pode começar hoje)
    b. 27
    c. 28 e 29 em paralelo
    d. 30 — e é ela que libera a 22
    e. 31 quando der; não trava nada
```

**A Fase 7 não depende de nenhuma das outras, e é onde está o trabalho barato.**
As tasks 26, 27 e 31 são varredura sobre a imagem — nem emulador, nem cartão,
nem cópia gravável. Junto com a 08 e a 09, são o que continua rendendo se a
Fase 2 travar no DuckStation. A origem delas é o
[PLAN-FEATURES](/docs/PLAN-FEATURES.md), escrito para o WE2002, e a §1.14 do
plano mede por que ele se aplica aqui: mesmo cabeçalho de contêiner, mesmo
codec, 2.070 bytes de fluxo comprimido idênticos entre os dois jogos.

**A Fase 8 daquele plano já está feita deste lado.** O `iso.py` faz a camada
ISO9660 inteira, com round-trip e controle negativo, e lê a imagem do WE2002
sem adaptação. Quem começar a 26 começa com essa camada de pé.

**A 17 é antecipável, e vale antecipar.** Ela depende só da 10, não da 16: as
quatro exigências que o formato do mapa já tem de atender — delta assinado,
contagem por tabela, correspondência por conteúdo, esquema por tabela — saem
todas de coisa **já medida**, das §1.10, §1.13 e §6.1 do plano. Escrever o
esquema cedo dá às tasks da Fase 4 um lugar para registrar o que acharem, em
vez de acumular achado em prosa e consolidar no fim.

**A 08 e a 09 podem correr a qualquer momento.** Nenhuma delas depende de
emulador nem de cartão — são varredura sobre a imagem, e as duas respondem
perguntas que o plano já deixou escritas. Se a Fase 2 travar por causa do
emulador, são elas o trabalho barato que continua.

---

## Checklist geral

### Fase 2 — Inventário de texto

- [x] `poke.py` grava em todas as cópias, com `--dry-run` que não toca a imagem
- [x] `poke.py` recusa nome que não cabe no slot alinhado, dizendo o tamanho
- [ ] Pelo menos três telas do jogo alcançadas por roteiro repetível
- [ ] `PIEMONTE2` visível nessas telas **e** `PIEMONTE` ausente de todas
- [ ] Round-trip de volta: `cmp` zero contra o original

### Fase 3 — O registro de jogador

- [ ] Passo do registro no cartão medido por duas medições independentes
- [ ] Três atributos isolados com offset, máscara de bits e domínio
- [ ] Cada campo verificado nos **dois** sentidos: tela → byte e byte → tela
- [ ] O bloco correspondente localizado no disco, ou o diagnóstico de por quê não
- [ ] Os 624 candidatos de 16 bits classificados; índice localizado ou "linear"
- [ ] Os 25 blocos extras de `SELECTC.BIN` contados, com esquema e ordem medidos

### Fase 4 — O resto do banco

- [ ] Tabela de elenco reproduzindo os 54 elencos de seleção, 23 de 23
- [ ] Qual tabela de jogador o índice de elenco aponta — pool ou executável
- [ ] Formação, uniforme, bandeira e Master League: cada um com âncora, delta
      assinado, contagem e um `poke` verificado
- [ ] A conta dos três números por eixo: mapeado, verificado, aberto

### Fase 5 — Mapa e leitor

- [ ] Esquema do mapa recusando `mapping: by-index` entre listas de tamanhos
      diferentes
- [ ] `tools/pes2/tables.py` alimentado pelo mapa em vez de pelo código
- [ ] `--check` do mapa verde nas duas releases: âncora, contagem, digest
- [ ] Gerador com `--check` que falha quando o gerado é editado à mão
- [ ] Round-trip pelo mapa: `cmp` zero nas duas releases, com controle negativo

### Fase 6 — Editor

- [ ] Abre as duas releases e exibe o mesmo banco
- [ ] Recusa imagem que não seja PES2, com mensagem legível
- [ ] Nenhuma constante de offset no código do editor
- [ ] Recusa gravar em `roms/`
- [ ] Um campo de cada família editado e verificado na tela do emulador
- [ ] Os sete entregáveis da §7 do plano com estado medido

### Fase 7 — Assets do disco

- [x] Os contêineres de cada release classificados: descomprimiu inteiro,
      parou no meio, não é LZSS — **790 contêineres nos quatro discos, 646
      inteiros, 12 parciais, 132 não-LZSS** (§1.14(e))
- [x] `decompress(compress(x)) == x` em 100% dos blocos — **8.217 de 8.217**
- [x] O início do fluxo de `TEX_00.BIN` decidido — **48**; a §5c do
      `PLAN-FEATURES` corrigida no arquivo dela
- [x] `w × h × bpp / 8` batendo com o tamanho descomprimido em 100% das
      entradas gráficas — **918/960/637/815 registros de imagem nos quatro
      discos; zero divergência fora dos estádios e do disco hackeado**
      (§1.14(f))
- [x] Conjunto de cópias por idioma **varrido**, e a ferramenta recusando se
      sobrar cópia fora do plano — **3 conjuntos por release; o `T_NAME` é o
      mesmo arquivo nas duas, 5 cópias em 2 discos** (§6.12)
- [ ] Um nome de `T_NAME` visto na tela nos dois idiomas, e o antigo ausente
- [x] Abrir e salvar sem editar devolve `cmp` zero nas duas releases — **139
      contêineres com índice reescritos, imagem byte a byte igual**
- [x] Estouro de orçamento recusa, dizendo quantos bytes faltaram — **22 bytes
      acima no `TITLE.BIN` entrada 0**
- [x] Política de EDC/ECC decidida por medição, e escrita na §6.7 —
      **preservar; o jogo boota e desenha com a cauda obsoleta**
- [ ] Estádios (`GDC_*`/`GRDM_*`) medidos e registrados como fora de escopo
- [ ] Lista do que a UI tem de cobrir, entregue à PES2-TASK-22
- [ ] *(fora do portão)* um clipe de áudio trocado e ouvido no emulador

---

## Decisões de design

Vindas de [`../PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) e de erro já pago.

| Decisão | Escolha | Razão |
| --- | --- | --- |
| Oráculo | **o jogo rodando** | não existe editor conhecido para PES2 (§4.1); um campo só está mapeado quando um `poke` muda o que a tela mostra |
| Ancoragem | **marcador + delta assinado**, nunca offset constante | três das sete cópias se deslocam entre as releases; um mapa constante parece funcionar e escreve lixo (§1.12, §6.6) |
| Correspondência entre cópias | **por conteúdo** | as oito listas de nome de time têm 106, 99, 95, 94, 123, 32, 99 e 99 entradas e diferem em conteúdo; casar por índice grava no time errado (§6.1) |
| O conjunto de cópias | **varrido, nunca declarado** | gravar as cinco listadas deixava o nome velho vivo em três lugares; o `poke.py` varre todo `form1` depois de planejar e recusa se sobrar (§6.1) |
| Nome maior que o slot | **truncar**, não deslocar | a margem entre a última tabela e a próxima é de **zero byte** (§1.13); até haver prova de índice reconstruível (§6.2) |
| EDC/ECC | **preservar** | o jogo não confere; corrigir muda bytes que nenhum teste espera e destrói a comparação de round-trip (§6.7) |
| Entrada das ferramentas | **o `(Track 1).bin`** | dump multi-track; concatenar as trilhas produz offsets que não existem (§1.1, §6.4) |
| Compartilhamento com o `newWe2002` | **conhecimento de formato, nunca código** | o `we2002_core` é a única coisa verificada byte a byte do repositório; um `if` de jogo dentro dele põe isso em risco (§6.9) |
| Fonte do código de leitura/gravação | **o mapa é o fonte**, o resto é gerado com `--check` | mesma disciplina do `newWe2002`, onde ela pegou dois erros de gerador e um seek trocado |
| Conteúdo do jogo no git | **nunca** | mapa é fato sobre o formato; tabela copiada de dentro da imagem é conteúdo comercial (§2). Vale para quadro de emulador, save state e dump de RAM |
| Display | **`:98`, sem exceção** | regra do [CLAUDE.md](../../CLAUDE.md), e a §6.10 do plano diz que não há exceção para este projeto |
| Asset que não cabe no extent | **fit-or-fail**, e rebuild de ISO fica fora do projeto | o jogo não acha arquivo por nome — as LBAs estão cravadas no MIPS e o buffer de destino continua do tamanho antigo mesmo com o diretório ISO corrigido (§5a do `PLAN-FEATURES`) |
| Entrada de contêiner não editada | **nunca recomprime** | o compressor do CARP nunca reproduz os bytes da Konami; guardar os originais é o que dá o "abrir e salvar sem editar devolve `cmp` zero" da §0 |
| Cópias de asset por idioma | **varrido, nunca declarado** | `T_NAME_I` e `T_NAME_S` são byte a byte idênticos; gravar um só repete a §6.1 uma camada acima, e o erro é invisível para quem joga no idioma gravado (§6.12) |
| Largura do cabeçalho de contêiner | **derivada, nunca constante** | dezesseis larguras distintas em `/BIN/`, de 0 a 204 palavras; constante lê do lugar errado em 205 dos 208 arquivos (§6.13) |

---

## Armadilhas medidas que valem para todas as fases

Cada uma custou tempo real. As nove de dirigir o DuckStation estão na §6.11 do
plano e todas já resolvidas dentro do `run_duckstation.sh` — estas são as que
alcançam qualquer task.

1. **"Cópia" de tabela não quer dizer mesma lista.** As oito cópias de nome de
   time têm 106, 99, 95, 94, 123, 32, 99 e 99 entradas, e o índice 34 de uma é
   outro time no índice 34 da outra — `ALWAYS ARGENTINA` contra `Classic Brazil`. Casar
   por índice grava no time errado, e o resultado parece plausível em tela
   nenhuma acusa. Usar o `team_map.py`, sempre.
2. **A ordem de armazenamento é propriedade da tabela.** `SELECTC.BIN` guarda
   elenco de trás para frente; o executável de boot, de frente para trás. Quem
   assume uma inverte 23 jogadores por time em metade das tabelas, e o erro é
   invisível porque a lista continua parecendo um elenco.
3. **`SELECTC.BIN` é pool deduplicado; o executável é ordenado por vaga.** Os
   dois guardam os mesmos 1.399 nomes; o executável repete 50, porque jogador
   em dois elencos ocupa duas vagas. Ler o pool como lista de elenco desalinha
   tudo depois do primeiro nome repetido — e foi exatamente isso que fez a §3.3
   reportar três elencos "parciais" que não existiam.
4. **O esquema de registro muda de tabela para tabela.** String + terminador
   alinhada a 4 numa; 10 B fixos **sem terminador quando o nome enche os 10**
   noutra — no disco lê-se `NachtegallHeggem` corrido. Tratar as duas do mesmo
   jeito trunca onde caberia mais e **corrompe o primeiro caractere do vizinho**
   no outro sentido.
5. **Nenhuma tabela tem sentinela de fim.** O que separa uma da seguinte é só a
   contagem, e no caso mais apertado a margem é **zero byte**: os 106 nomes vão
   até 4292, e 4292 é onde `PTA\0` começa. Escrever um 107º nome invade a
   primeira abreviação.
6. **O marcador pode cair no meio da tabela que ancora.** `Oranges001` resolve
   em 7060 e a tabela começa em 5320 — registro 174 de 463, delta **−1740**.
   Não é exceção: quem escolhe o literal procura um trecho **único**, não um
   trecho inicial.
7. **A fronteira de setor continua mordendo.** Um registro que atravessa o fim
   dos 2.048 B de dados salta 304 bytes no offset absoluto. Trabalhar sempre em
   offset relativo ao arquivo, e converter só na hora de gravar. Foi a causa
   dos três `OFS_TEAM_NAME_1`, `_END` e `_A` do WE2002, e o controle negativo
   do `iso.py` cai exatamente nesse caso.
8. **O diretório ISO nomeia arquivo que não está no Track 1.** Os sete
   `/SD/DA/*.DA` começam no LBA 198606 e o Track 1 acaba em 198456. Ler por
   LBA sem conferir o limite devolve menos bytes do que se pediu, **em
   silêncio**, e o erro aparece três camadas adiante.
9. **`roms/` tem os originais, e PES2 grava in-place.** Copiar a release
   inteira (571 MiB, as oito trilhas) para o scratchpad antes de apontar
   qualquer coisa que escreva. Um `poke` errado sem cópia custa um novo
   download.
10. **Versionar uma medição é diferente de repeti-la.** Quando a §2 do
    `PES2-AJUSTES.md` transformou em ferramenta o que era prosa, a ferramenta
    **discordou duas vezes**: o diff entre releases era 202/27/7 e não 204/32,
    e os 54 elencos casavam todos, sem parcial nenhum. Medida sem comando que a
    reproduza é lembrança.
11. **Asset também tem conjunto de cópias, e ele é por idioma.**
    `/BIN/T_NAME_I.BIN` e `/BIN/T_NAME_S.BIN` têm 62.196 bytes e são **byte a
    byte idênticos**; o jogo escolhe por idioma. Gravar um e deixar o outro é
    a armadilha 1 desta lista uma camada acima — e pior, porque a verificação
    passa se o roteiro do emulador não trocar de idioma. Vale igual para
    `DAT2D_I`/`_S`, `DATSEL_I`/`2I`/`3I`, `LC_*` e `FNOTE_{G,I,S}`.
12. **O cabeçalho de contêiner não tem tamanho fixo.** São ponteiros de RAM
    da PSX, e a contagem é propriedade do arquivo: 0 palavras em
    `DEMODATA.BIN`, 2 em `DAT2D.BIN`, 12 em todo `TEX_*`, 204 em `ANIME.BIN`.
    E **zero conta como palavra** — `TEX_00.BIN` tem uma nula no índice 6 com
    ponteiros válidos depois; parar no primeiro zero encurta o cabeçalho pela
    metade.
13. **Os nomes licenciados não estão no disco.** Procurar `JUVENTUS` e concluir
    "está criptografado" custou uma varredura de delta na imagem inteira. A
    release europeia é integralmente fictícia nos clubes; as seleções têm nome
    real. O mapa fictício → real é conhecimento externo
    ([PES2-NOMES](/docs/PES2-NOMES.md)).

---

## Pendências externas

- ~~**`numpy` e um desmontador MIPS**~~ — **resolvido em 2026-09-01** pela
  [PES2-TASK-01](/docs/tasks/01-ferramental-das-fases-3-e-4.md), a pedido do
  dono da máquina: `numpy` 2.5.2, `radare2` 5.5.0 e
  `mipsel-linux-gnu-objdump` 2.42. **Ghidra ficou de fora**, com razão escrita
  na §3.2 do plano — se a Fase 4 pedir decompilação de verdade, a decisão se
  retoma ali.
- **Os dois FAQs de terceiros** que sustentam o mapa fictício → real de
  `docs/PES2-NOMES.md` não entram no git, e o GameFAQs recusa requisição
  automatizada (HTTP 403 e desafio Cloudflare). O que entra é o `faq_check.py`,
  que os confere quando o usuário os baixar de novo.

---

## Estrutura de pastas (estado final esperado)

```text
new-we2002-editor/
├── docs/
│   ├── PLAN-PES2-PSX.md              ← fonte de verdade
│   ├── PES2-AJUSTES.md               ← a revisão de 2026-08-30; §7 era o backlog
│   ├── PES2-NOMES.md                 ← o apêndice de nomes fictícios
│   ├── samples/pes2-*.md             ← saídas geradas pelas ferramentas
│   └── tasks/
│       ├── 01-...md ... 25-...md
│       ├── progresso.md              ← este arquivo
│       └── correcoes-progresso.md
└── tools/pes2/                       ← Python 3 e shell; nada de C++, nada de Qt
    ├── iso.py tables.py memcard.py team_map.py player_map.py …
    ├── lzss.py bin_archive.py            ← a partir da PES2-TASK-26 e 27
    ├── pes2_map.json                 ← a partir da PES2-TASK-18
    └── run_duckstation.sh boot_check.sh
```

---

## Estado medido, herdado das Fases 0 e 1

Medido em 2026-08-29 e 2026-08-30, e **reconferido por ferramenta versionada**
na revisão da mesma semana — a §2 do `PES2-AJUSTES.md` existe exatamente para
que estes números tenham comando que os reproduza.

| Eixo | Estado |
| --- | --- |
| Track 1 `(EsIt)` | 466.768.512 B = 198.456 setores exatos |
| Arquivos no ISO | 252 — **244 `form1`**, 1 `form2`, 7 fora do Track 1 |
| Round-trip do `iso.py` | **byte a byte idêntico**, 244 arquivos reescritos |
| Controle negativo | **exatamente um byte** muda, no offset absoluto 2002800, atravessando fronteira de setor |
| Marcadores da §1.13 | **11** pares (arquivo, literal), cada um ocorrendo **uma vez** nas duas releases — *corrigido*: eram 8 |
| Tabelas de texto | **14**, com contagem e digest SHA-256 idênticos nas duas releases — *corrigido*: eram 11 |
| Nomes de time | 106 em `SELECT.BIN` — 2 de cabeçalho + 104 times |
| Abreviações | 95 — os 7 *classic* e os 2 *allstars* **não têm** |
| Nomes de jogador | 1.399 em `SELECTC.BIN`, 1.449 no executável; **os mesmos 1.399 distintos** |
| Fronteiras de elenco | **54 de 54 exatas**, 23 de 23 nomes — *corrigido*: eram "49 + 2 e três parciais" |
| Diff entre releases | 202 idênticos, 27 diferem, 7 não comparáveis — *corrigido*: era 204/32 |
| Os 8 que diferem sem mudar de tamanho | **nenhum guarda dado de jogo** — 99,6% a 100% é rotina MIPS realocada, `+3176` dominando |
| Os 69 `OFS_*` do WE2002 | **69 de 69** mapeados, em 13 arquivos, os 13 presentes no PES2 |
| Contêineres `form1` em `/BIN/` | **por disco, não por jogo**: 208 em PES2 `(EsIt)`, **210** em PES2 `(EnFrDe)`, 177 na European Deluxe e 195 na japonesa — 790 nos quatro (§1.14(e), com o comando que os reproduz). Os 13 de diferença que a medição de 2026-08-30 atribuiu a cópia de idioma são entre `(EsIt)` e a japonesa, as duas pontas que ela comparou; a faixa tem quatro valores |
| Cabeçalho de contêiner | ponteiros de RAM, **16 larguras** distintas, **mesmo histograma nos dois jogos** |
| `DAT2D.BIN` entre os dois jogos | **2.070 bytes de fluxo comprimido idênticos** a partir do byte 8 |
| `T_NAME_I` × `T_NAME_S` | 62.196 B cada, **byte a byte idênticos** |
| `SD/*.RA` | cabeçalho **VAB** (`VABp`, v7, 4 programas, 64 tones, 29 VAGs), **idêntico** ao do WE2002, mesmo LBA 20000 |
| Estádios | 51 `GDC_*`/`GRDM_*` em cada jogo, `GDC_AD.BIN` no mesmo LBA 12560 — **fora de escopo** |
| Boot no `:98` | janela 800×655, dois quadros com desvio-padrão 0,228 e 0,243 e **259.994 de 524.000 pixels diferentes** |

---

## Notas de execução

*(preenchido conforme as tasks forem executadas — mesmo formato do "Log de
Execução" de cada arquivo de task, resumido aqui quando houver algo relevante
para o conjunto)*
