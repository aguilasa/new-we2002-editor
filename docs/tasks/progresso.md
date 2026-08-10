# Progresso — de `.exe` a editor em Lazarus (WE2002 Team Editor, Obocaman)

Rastreamento das tasks de [`../PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md),
que é a fonte de verdade do projeto. Este arquivo registra **andamento**; o
plano registra **objetivo e critério**. Divergência entre os dois se resolve a
favor do plano.

**Projeto separado do `newWe2002`.** Não compartilha build nem código. O que
compartilha é conhecimento de formato: `Offsets.hpp`, `Tables.cpp` e o
`we2002_core` inteiro, que é a entrada do transpilador da fase 3.

## Resumo

| ID | Tarefa | Fase | Dependências | Status | Concluída em | Revisado em |
| -- | ------ | ---- | ------------ | ------ | ------------ | ----------- |
| [WTE-TASK-01](/docs/tasks/01-ferramental.md) | Ferramental (Lazarus, FPC, Ghidra) | 0 | — | ✅ Concluído | 2026-08-05 | 2026-08-05 |
| [WTE-TASK-02](/docs/tasks/02-esqueleto-do-projeto.md) | Esqueleto de `wte/` e build | 0 | 01 | ✅ Concluído | 2026-08-05 | 2026-08-05 |
| [WTE-TASK-03](/docs/tasks/03-extrator-de-dfm.md) | `dfm_extract.py` — os 18 formulários | 1 | 02 | ✅ Concluído | 2026-08-05 | 2026-08-05 |
| [WTE-TASK-04](/docs/tasks/04-mapa-de-handlers.md) | `published_methods.tsv` — os 96, com dono | 1 | 02 | ✅ Concluído | 2026-08-05 | 2026-08-06 |
| [WTE-TASK-05](/docs/tasks/05-inventario-de-strings.md) | `re/strings.tsv` | 1 | 02 | ✅ Concluído | 2026-08-05 | 2026-08-06 |
| [WTE-TASK-06](/docs/tasks/06-mapa-de-offsets.md) | `re/offsets.md` — a tabela em `.data` | 1 | 02 | ✅ Concluído | 2026-08-05 | 2026-08-06 |
| [WTE-TASK-07](/docs/tasks/07-unidades-duvidosas.md) | Veredito das 4 unidades VCL duvidosas | 1 | 02 | ✅ Concluído | 2026-08-05 | 2026-08-06 |
| [WTE-TASK-08](/docs/tasks/08-convencao-dos-assets.md) | Convenção dos 198 bitmaps e do `dat.bin` | 1 | 05 | ✅ Concluído | 2026-08-06 | 2026-08-06 |
| [WTE-TASK-09](/docs/tasks/09-fechamento-fase-1.md) | Fechamento da fase 1 | 1 | 03-08 | ✅ Concluído | 2026-08-06 | 2026-08-06 |
| [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md) | `dfm2lfm.py` — os `.lfm` e os esqueletos | 2 | 03, 04, 07 | ✅ Concluído | 2026-08-06 | 2026-08-09 |
| [WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md) | App com os 18 formulários e 96 stubs | 2 | 10 | ✅ Concluído | 2026-08-06 | 2026-08-09 |
| [WTE-TASK-12](/docs/tasks/12-comparacao-visual.md) | Comparação visual dos 18 formulários | 2 | 11 | ✅ Concluído | 2026-08-09 | ⬜ pendente |
| [WTE-TASK-13](/docs/tasks/13-trace-de-eventos.md) | Trace de eventos contra o original | 2 | 11 | ✅ Concluído | 2026-08-09 | ⬜ pendente |
| [WTE-TASK-14](/docs/tasks/14-fechamento-fase-2.md) | Fechamento da fase 2 | 2 | 12, 13 | ⬜ Pendente | — | — |
| [WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) | Decidir o mapeamento de tipo C++ → Pascal | 3 | 02 | ✅ Concluído | 2026-08-09 | ⬜ pendente |
| [WTE-TASK-16](/docs/tasks/16-gerador-de-tabelas.md) | `gen_tables_pas.py` — offsets e tabelas | 3 | 15 | ⬜ Pendente | — | — |
| [WTE-TASK-17](/docs/tasks/17-transpilador-da-camada-de-dados.md) | `port_database_pas.py` — o transpilador | 3 | 15, 16 | ⬜ Pendente | — | — |
| [WTE-TASK-18](/docs/tasks/18-camada-de-dados-gerada.md) | Gerar a camada de dados | 3 | 17 | ⬜ Pendente | — | — |
| [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) | Os offsets que o Obocaman tem e nós não | 3 | 06, 18 | ⬜ Pendente | — | — |
| [WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) | Round-trip headless contra o `we2002_core` | 3 | 18, 19 | ⬜ Pendente | — | — |
| [WTE-TASK-21](/docs/tasks/21-fechamento-fase-3.md) | Fechamento da fase 3 | 3 | 20 | ⬜ Pendente | — | — |
| [WTE-TASK-22](/docs/tasks/22-harness-golden.md) | `golden_check.sh` — **o gate** | 4 | 11, 21 | ⬜ Pendente | — | — |
| [WTE-TASK-23](/docs/tasks/23-formato-da-spec.md) | Formato de `re/spec/` e vocabulário de veredito | 4 | 09 | ✅ Concluído | 2026-08-09 | ⬜ pendente |
| [WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md) | Ghidra com a convenção Borland | 4 | 04, 06 | ⬜ Pendente | — | — |
| [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | Handlers de carga | 4 | 22, 23, 24 | ⬜ Pendente | — | — |
| [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | Handlers de edição | 4 | 25 | ⬜ Pendente | — | — |
| [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) | Handlers de gravação | 4 | 26 | ⬜ Pendente | — | — |
| [WTE-TASK-28](/docs/tasks/28-handlers-auxiliares.md) | Handlers dos 13 diálogos auxiliares | 4 | 25 | ⬜ Pendente | — | — |
| [WTE-TASK-29](/docs/tasks/29-fechamento-fase-4.md) | Fechamento da fase 4 | 4 | 25-28 | ⬜ Pendente | — | — |
| [WTE-TASK-30](/docs/tasks/30-preco-do-jogador.md) | Preço derivado dos atributos | 5 | 24, 25 | ⬜ Pendente | — | — |
| [WTE-TASK-31](/docs/tasks/31-import-de-mcr.md) | Import e export de `.mcr` | 5 | 08, 24, 27 | ⬜ Pendente | — | — |
| [WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md) | Camisa e bandeira 2D | 5 | 08, 24, 27 | ⬜ Pendente | — | — |
| [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) | Contador de slots livres de ML | 5 | 20 | ⬜ Pendente | — | — |
| [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) | Bateria golden completa | 6 | 29-33 | ⬜ Pendente | — | — |
| [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) | Registro das divergências deliberadas | 6 | 34 | ⬜ Pendente | — | — |
| [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md) | Buffers de tamanho fixo e truncamento | 6 | 26, 34 | ⬜ Pendente | — | — |
| [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md) | Reconferência de UI com a lógica ligada | 6 | 34 | ⬜ Pendente | — | — |
| [WTE-TASK-38](/docs/tasks/38-nome-e-linhagem.md) | Nome do produto e linhagem no `NOTICE.md` | 7 | 35 | ⬜ Pendente | — | — |
| [WTE-TASK-39](/docs/tasks/39-empacotamento.md) | Ícone, `.desktop`, AppStream, `install` | 7 | 38 | ⬜ Pendente | — | — |
| [WTE-TASK-40](/docs/tasks/40-verificacao-final.md) | Verificação final | 7 | 36, 37, 39 | ⬜ Pendente | — | — |

**Legenda:** ⬜ Pendente · 🔄 Em andamento · ✅ Concluído · ❌ Bloqueado · ⏭️ Pulado

**As duas colunas de data são datas de commit**, não datas de intenção.

- **"Concluída em"** — o commit que fechou a tarefa. Tarefa pendente leva `—`.
- **"Revisado em"** — o commit da revisão. Tarefa concluída e ainda não revisada
  leva `⬜ pendente`; tarefa que nem começou leva `—`, porque não há o que
  revisar.

**Revisão sem discrepância também preenche a coluna.** É resultado legítimo, e
sem a data não há como distinguir "revisada, nada achado" de "nunca revisada".

---

## Escopo e fases

Reimplementar o **WE2002 Team Editor v0.99** do Obocaman como aplicação
**Lazarus/FPC nativa no Linux**, com paridade verificada byte a byte contra o
binário original. Ver [`../PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md) para o
objetivo completo e o modelo de verificação.

| Fase | Tasks | O que entrega |
| --- | --- | --- |
| 0 — Infra | 01 a 02 | ferramental instalado e provado; `wte/` compilando vazio |
| 1 — Extração estática | 03 a 09 | os 18 DFM, os 96 handlers, strings, offsets, assets — **sem decompilador** |
| 2 — Casca | 10 a 14 | a UI inteira gerada, navegável, com os 96 stubs logando |
| 3 — Dados | 15 a 21 | camada de dados **gerada** do `we2002_core`, lendo as duas ROMs |
| 4 — Comportamento | 22 a 29 | o gate golden, e os 96 handlers com veredito |
| 5 — Features | 30 a 33 | preço, `.mcr`, camisa/bandeira 2D, slots de ML |
| 6 — Paridade | 34 a 37 | bateria completa, divergências registradas, bordas de buffer |
| 7 — Acabamento | 38 a 40 | nome, linhagem, empacotamento, verificação final |

**A fase 5 é o motivo do projeto.** As quatro features são o que o `ed.exe` não
tem; o resto do trabalho existe para chegar até elas com verificação.

**O que não pode ser pulado:** a fase 1 antes da 2 (sem os DFM não há gerador),
a 3 antes da 4 (handler sem camada de dados não tem o que manipular), e a
**22 antes de qualquer handler** — sem gate, cada implementação é opinião.

---

## Grafo de dependências

```text
Fase 0
  01 ──► 02
          │
Fase 1    ├──► 03 ──┐
          ├──► 04 ──┤
          ├──► 05 ──┼──► 09 (fechamento)
          ├──► 06 ──┤        │
          ├──► 07 ──┤        │
          │    └► 08┘        │
          │                  │
Fase 2    └► (03,04,07) ►10 ►11 ──┬──► 12 ──┐
                          │       └──► 13 ──┼──► 14
Fase 3    02 ──► 15 ──► 16 ──► 17 ──► 18 ──┬──► 19 ──► 20 ──► 21
                                            └─────────►│        │
                    06 ─────────────────────────────────┘        │
Fase 4                                                            │
   11 ─────────────────────────────────────────────────► 22 ◄────┘
   09 ──► 23 ──┐         04,06 ──► 24 ──┐
               └────────────┬───────────┴──► 25 ──┬──► 26 ──► 27
                            22 ─────────┘         └──► 28
                                                  25-28 ──► 29
Fase 5
   24,25 ──► 30
   08,24,27 ──► 31
   08,24,27 ──► 32
   20 ──────► 33
                29,30,31,32,33 ──► 34
Fase 6                              ├──► 35 ──► 38 ──► 39 ──┐
                                    ├──► 36 ─────────────────┼──► 40
                                    └──► 37 ─────────────────┘
```

**Sequência mínima de execução:**

```text
1.  01, 02 (infra)
2.  03, 04, 05, 06, 07 em paralelo — nenhuma depende da outra
3.  08 (depois de 05), depois 09 (fechamento da fase 1)
4.  10, depois 11
5.  12 e 13 em paralelo, depois 14
6.  15 (decisao), 16, 17, 18 — em serie, o gerador depende do tipo
7.  19, 20, 21
8.  22 (o gate) e 24 (Ghidra) em paralelo; 23 pode vir desde a 09
9.  25, depois 26 e 28 em paralelo, depois 27
10. 30 pode entrar aqui, fora de ordem — ver abaixo
11. 29 (fechamento da fase 4)
12. 31, 32, 33 em paralelo
13. 34, depois 35, 36 e 37 em paralelo
14. 38, 39
15. 40 (aceite final)
```

**A 30 (preço) entra fora de ordem de propósito** — plano §10 passo 5. É
isolada, não depende de gravação, entrega a feature mais desejada antes de a
fase 4 fechar, e valida o ferramental de decompilação num alvo pequeno e
conferível.

---

## Checklist geral

### Fase 0 — Infra

- [x] `lazbuild` compila projeto LCL vazio e abre janela no `:99`
- [x] `make wte` ainda abre o original (o oráculo A depende do stack X i386)
- [x] Ghidra importa o `.exe`
- [x] `wte/` compilando, com `re/` versionado e saída de build ignorada
- [x] Decidido onde mora a bateria de `--check` dos geradores
      (`wte/Makefile` autônomo — ver [`../../wte/README.md`](../../wte/README.md))

### Fase 1 — Extração estática

- [x] Os 18 formulários decodificados inteiros, blobs binários preservados
- [x] Os 96 handlers com endereço **e formulário dono**
- [x] Strings com referência cruzada para os handlers
- [x] Limite da tabela de offsets **medido**, não estimado
- [x] Offsets que o `newWe2002` não tem, listados
- [x] `Registry`, `Printers`, `Comobj`, `Winhelpviewer` com veredito
- [x] Convenção de nome dos 198 bitmaps resolvida
- [x] Os números da §1 do plano remedidos por ferramenta versionada

### Fase 2 — Casca

- [x] Os 18 `.lfm` gerados e aceitos pelo `lazbuild`
- [x] Os 96 stubs na unidade certa, logando
- [x] Comparação visual dos 18, com veredito escrito
- [x] Diferenças de ordem de evento LCL × VCL registradas
- [ ] Fração de código gerado medida contra a tese da §4.4
- [ ] Nenhum arquivo gerado editado à mão (provado por `--check`)

### Fase 3 — Dados

- [x] Mapeamento de tipo decidido, incluindo `char[N]`, bitfield e `CdImage`
- [ ] `FORBIDDEN` e `check_seeks()` no transpilador, testados com entrada plantada
- [ ] As cinco unidades de dados geradas e compilando
- [ ] Toda recusa do `FORBIDDEN` com rota escolhida e razão
- [ ] Diff de controle (gravar sem editar) medido antes de qualquer offset novo
- [ ] Dumps Pascal e C++ idênticos nas duas ROMs
- [ ] Bitfield de `SquadNumbers` conferido contra imagem real
- [ ] Registrado se o Ghidra foi necessário na fase 3

### Fase 4 — Comportamento

- [ ] Harness golden com as quatro guardas, controle verde e positivo detectado
- [x] Gabarito de spec com o campo **evidência**, e a proibição de colar decompilado
- [ ] Convenção Borland aplicada; `colorearClick` com assinatura correta
- [ ] Os 96 nomes aplicados no Ghidra por script
- [ ] Rota de VMT decidida com o teste das cinco chamadas
- [ ] 96 entradas em `re/spec/`, nenhuma `aberto`
- [ ] Toda gravação byte-idêntica nas duas ROMs
- [ ] Cinco `trivial` reamostrados e reconferidos

### Fase 5 — Features

- [ ] Fórmula de preço por tabela de verdade **e** conferida no disassembly
- [ ] Saturação, arredondamento e termo cruzado testados
- [ ] `.mcr`: contêiner por documentação pública, conteúdo revertido
- [ ] Os três casos especiais do readme do original cobertos
- [ ] Render 2D: paleta vs. pixel decidido, tolerância **medida**
- [ ] `grabar_camisetaClick` byte-idêntico, sem tolerância
- [ ] Slots de ML batendo com a tela do original nas duas ROMs

### Fase 6 — Paridade

- [ ] Bateria completa: operação × ROM, sem célula vazia
- [ ] Edição múltipla e gravação dupla cobertas
- [ ] Toda exceção do golden com entrada em `divergencias.md`
- [ ] Inventário de buffers com os quatro casos de borda, nas duas ROMs
- [ ] Nenhuma ação destrutiva alcançável por `Return`

### Fase 7 — Acabamento

- [ ] Nome do produto escolhido, distinto do original
- [ ] Linhagem do Obocaman no `NOTICE.md`; nenhum `LICENSE` adicionado
- [ ] Árvore instalada funciona depois de movida
- [ ] Assets ausentes produzem mensagem que diz o que falta
- [ ] Condição 3 testada em ambiente **sem** Wine
- [ ] Vocabulário escrito: verificado, não verificado, divergente por decisão

---

## Decisões de design

Vindas de [`../PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md) e de erro já pago
no `newWe2002`.

| Decisão | Escolha | Razão |
| --- | --- | --- |
| Método de RE | recuperação de especificação, não transcrição | decompilado de C++Builder é ilegível, e transcrevê-lo faria obra derivada de binário sem licença |
| Fonte do Pascal | gerador onde der, mão só nos 96 handlers | forma, offsets, tabelas e camada de dados são mecânicos |
| Origem da camada de dados | `we2002_core` deste repo, **não** o `.exe` | já é byte-idêntico ao `ed.exe`; transpilar código nosso é auditável |
| Limite do transpilador | só entrada deste repositório | com decompilado o `FORBIDDEN` deixa de segurar e o gerador emite Pascal quebrado com cara de certo |
| Oráculos | dois — `wte.exe` (comportamento) e `we2002_core` (formato) | o diff diz *onde* mudou, o core diz *o que* aquilo significa |
| Ordem de ataque | casca antes de recheio | o stub que loga vira ferramenta de RE: mostra a ordem real de disparo |
| Prioridade de método | diff antes de decompilador | cada offset custa dois minutos de tela contra horas de disassembly |
| Layout de formulário | geometria absoluta, sem layout automático | 441 controles posicionados à mão em 2002; fidelidade é o critério |
| Reprodução de bug do original | permitida **não** reproduzir, obrigatório registrar | diferente do `newWe2002`, onde clonar o `ed.exe` inclusive nos defeitos era o objetivo |
| Idioma | docs em português; **commits em inglês, conventional** | convenção deste repositório, diferente da do projeto `snes` |

---

## Armadilhas medidas que valem para todas as fases

Cada uma custou tempo real, aqui ou no `newWe2002`.

1. **Ghidra assume `__cdecl` e o C++Builder passa `this` em `EAX`.** Sem
   convenção customizada, a saída do decompilador é ruído convincente — o pior
   tipo de erro, porque parece certo. (§8.1)
2. **Não alimentar o transpilador com decompilado.** A tentação aparece quando a
   fase 4 fica cara. O resultado é Pascal que compila, passa em teste unitário e
   grava bytes errados. (§8.10)
3. **`[^x]` casa `\n` em regex.** Foi assim que um `Seek(begin)` virou
   `SeekCurrent` no `port_database.py`: compilava, passava nos testes, passava
   no ASan, e só o confronto com o `ed.exe` mostrou.
4. **Cópia, sempre.** Os três editores gravam in-place e cada imagem tem ~474 MB.
   Nunca apontar nada para `roms/`.
5. **Diff de controle antes de medir qualquer coisa.** `Load`+`Save` sem editar
   já muda bytes: o `Save` reconstrói as all-star, e o original troca os dois
   primeiros cobradores de cada clube de ML. Sem o controle, toda medição vem
   contaminada.
6. **Janela esquecida no `:99` derruba o golden test.** Os dois lados acham a
   janela por heurística; uma sobra de teste manual é dirigida em vez da que
   está sob teste, e o diff parece bug do port.
7. **`Ctrl+A` não seleciona tudo num `TEdit`.** Limpar campo com `End`,
   `shift+Home`, `BackSpace` — senão os dois lados recebem textos diferentes.
8. **`xdotool type --window` embaralha string longa.** Digitar curto; mapear
   unidade para encurtar caminho, como o `make wte` já faz.
9. **Tipo de tamanho dependente de plataforma embaralha número de camisa.**
   `DWORD` virou 64-bit no Linux LP64 e custou o bug inteiro. Em FPC o risco
   irmão é a ordem de bit do `bitpacked record`. (§8.6, §8.11)
10. **Release não é o mesmo teste que Debug.** Um `strcpy` estourando um byte
    era invisível em Debug e derrubava o app em Release, com
    `_FORTIFY_SOURCE`. Testar nos dois.
11. **Todo número em doc vem de ferramenta.** Os números da §1 do plano foram
    medidos por script descartável em 2026-08-05; a WTE-TASK-09 os remede com
    ferramenta versionada e reconcilia.

---

## Pendências externas

- **Publicação depende do usuário.** O binário do Obocaman é sem licença, como
  todo o código herdado que o [`../../NOTICE.md`](../../NOTICE.md) registra. A
  WTE-TASK-38 prepara a linhagem; **publicar não é decisão do executor.**
- **Assets não redistribuídos, com uma exceção.** Os 198 BMP e o `dat.bin` ficam
  com o usuário, como `roms/`. O app precisa falhar com mensagem clara sem eles.
  A exceção são os 118 blobs de formulário (816.880 B), que **estão** versionados
  em hex nos `wte/forms/*.lfm` — decisão de 2026-08-06, registrada em
  [`../../wte/re/dfm/README.md`](../../wte/re/dfm/README.md) e no §2 do
  [`PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md).
- **Nada disso roda em CI.** O golden test precisa de Wine, do `:99` e de ~1 GB
  de temporário por rodada. O CI do repositório, aliás, está com `push` e
  `pull_request` desligados por decisão, e religar é para o fim do projeto.
- **Binário original em espanhol seria bom ter, e não é bloqueante.** O `.exe` é
  a tradução PT-BR com 13 strings de `.data` truncadas por padding — mais 80
  literais nos DFM, que são outra população (WTE-TASK-09). As três mensagens em
  que isso importa já têm cópia legível **dentro do próprio `.exe`** — o bloco
  de literais aparece três vezes na `.data`, e as duas cópias mortas
  preservaram o texto original (WTE-TASK-05; marcadas `gemea_difere` no
  `wte/re/strings.tsv`). O item continua desejável, só deixou de ser
  necessário; `.text` é idêntico, então nada da análise muda. (§1.5)

---

## Estrutura de pastas (estado final esperado)

```text
new-we2002-editor/
├── docs/
│   ├── PLAN-WTE-LAZARUS.md           ← fonte de verdade
│   └── tasks/
│       ├── 01-...md ... 40-verificacao-final.md
│       └── progresso.md              ← este arquivo
├── wte/
│   ├── wte.lpi, wte.lpr              ← WTE-TASK-02
│   ├── src/
│   │   ├── ep2002_*.pas              ← WTE-TASK-10 (gerado) + 25-28 (corpos)
│   │   ├── we2002_offsets.pas        ← WTE-TASK-16 (gerado)
│   │   ├── we2002_tables.pas         ← WTE-TASK-16 (gerado)
│   │   ├── we2002_database.pas       ← WTE-TASK-18 (gerado)
│   │   ├── we2002_player.pas         ← WTE-TASK-18 (gerado)
│   │   ├── we2002_cdimage.pas        ← WTE-TASK-18 (gerado)
│   │   ├── we2002_textcodec.pas      ← WTE-TASK-18 (gerado)
│   │   ├── we2002_types.pas          ← WTE-TASK-18 (gerado)
│   │   ├── we2002_preco.pas          ← WTE-TASK-30
│   │   ├── we2002_mcr.pas            ← WTE-TASK-31
│   │   ├── we2002_render.pas         ← WTE-TASK-32
│   │   ├── we2002_ml.pas             ← WTE-TASK-33
│   │   └── datafiles.pas             ← WTE-TASK-39
│   ├── forms/*.lfm                   ← WTE-TASK-10 (gerado)
│   ├── assets/                       ← aponta para we-team-editor/ (gitignored)
│   ├── re/                           ← versionado
│   │   ├── ambiente.md               ← WTE-TASK-01
│   │   ├── dfm/                      ← WTE-TASK-03
│   │   ├── published_methods.tsv     ← WTE-TASK-04
│   │   ├── strings.tsv               ← WTE-TASK-05
│   │   ├── offsets.md                ← WTE-TASK-06, 19
│   │   ├── unidades-vcl.md           ← WTE-TASK-07
│   │   ├── assets.md                 ← WTE-TASK-08
│   │   ├── fase-1.md                 ← WTE-TASK-09
│   │   ├── eventos.md                ← WTE-TASK-13
│   │   ├── tipos.md                  ← WTE-TASK-15
│   │   ├── recusas.md                ← WTE-TASK-18
│   │   ├── vmt.md                    ← WTE-TASK-24
│   │   ├── spec/                     ← WTE-TASK-23 a 33
│   │   ├── golden.md                 ← WTE-TASK-34
│   │   ├── divergencias.md           ← WTE-TASK-35
│   │   └── buffers.md                ← WTE-TASK-36
│   ├── tools/
│   │   ├── dfm_extract.py            ← WTE-TASK-03
│   │   ├── check_fase1.py            ← WTE-TASK-09
│   │   ├── dfm2lfm.py                ← WTE-TASK-10
│   │   ├── gen_tables_pas.py         ← WTE-TASK-16
│   │   ├── port_database_pas.py      ← WTE-TASK-17
│   │   ├── golden_check.sh           ← WTE-TASK-22
│   │   ├── golden_suite.sh           ← WTE-TASK-34
│   │   ├── ghidra/                   ← WTE-TASK-24
│   │   └── make_icon.py              ← WTE-TASK-39
│   ├── packaging/                    ← WTE-TASK-39
│   └── tests/
└── src/core/                         ← entrada do transpilador, NAO alvo
```

---

## Estado medido, reconciliado pela WTE-TASK-09

A primeira medição foi feita na criação destas tasks (2026-08-05), com
`objdump`, `strings` e script Python descartável. A **WTE-TASK-09 remediu tudo
com ferramenta versionada** e corrigiu quatro linhas; o confronto item a item,
com a causa de cada correção, está em
[`../../wte/re/fase-1.md`](../../wte/re/fase-1.md).

| Eixo | Estado |
| --- | --- |
| Toolchain do original | **Borland C++Builder 6** (não Delphi) |
| Tamanho do `.exe` | 1.151.488 bytes, PE32 i386, 8 seções |
| `.text` (código do autor) | 138.240 bytes — a VCL está em runtime packages |
| `.rsrc` | 912.384 bytes, 79% do arquivo |
| Imports | 322, sendo 267 de `rtl60.bpl`/`vcl60.bpl` — *corrigido* |
| Formulários DFM | 18, 441 componentes, 20 classes distintas — *corrigido* |
| Handlers publicados | 96, com endereço recuperado do VMT |
| Unidades nomeadas | 13 (`Tep2002_*`), pelos exports de finalização |
| Offsets nossos que batem | **19 de 69**, em tabela a partir de `0x004231a0` |
| Strings com enchimento do tradutor | 13 em `.data`, 80 nos DFM — *corrigido* |
| Assets externos | 198 `.bmp` + `dat.bin` de 145.408 B — *corrigido* |
| Ferramental instalado | **nenhum** — sem Lazarus, FPC, Ghidra ou `pefile`. **Superado pela WTE-TASK-01**: ver [`../../wte/re/ambiente.md`](../../wte/re/ambiente.md) |

Censo de componentes, medido nos 18 DFM pelo `dfm_extract.py` — o detalhe por
formulário está em [`../../wte/re/dfm/censo.md`](../../wte/re/dfm/censo.md):

```
TLabel        182     TGroupBox      10
TImage         45     TRadioButton    9
TStaticText    37     TEdit           6
TBitBtn        32     TOpenDialog     3
TShape         32     TTrackBar       3
TSpeedButton   28     TActionList     2
TScrollBar     20     TBevel          2
TUpDown        12     TBrowseURL      2   <- unico sem par na LCL
TComboBox      11     TListBox        2
                      TSaveDialog     2
                      TTimer          1
```

Um dos 441 **não tem nome** — um `TStaticText` de 4×4 px no `MainForm`. É o que
separa a contagem exata da apressada, e o `check_fase1.py` aborta se a
recontagem dos `.dfm` discordar do censo.

---

## Notas de execução

*(preenchido conforme as tasks forem executadas — mesmo formato do "Log de
Execução" de cada arquivo de task, resumido aqui quando houver algo relevante
para o conjunto)*

**WTE-TASK-09 — número velho agora é falha de build, não achado de revisão.**
O `check_fase1.py` varre os markdowns de `docs/` e `wte/re/` atrás de afirmação
viva dos quatro números que a fase 1 corrigiu, e **aborta** se achar alguma. Vale
para o resto do projeto: reintroduzir 197, ~430, 300 ou 70 num doc derruba
`make -C wte check`. O perímetro deixa de fora o documento que **narra** a
correção (os `CORR-*`, o `correcoes-progresso.md`, o `assets.md`, o
`strings.md`), o **Log de Execução** de qualquer tarefa, e o **enunciado de
tarefa já concluída** — este último porque enunciado executado é história;
tarefa pendente continua dentro, e foi assim que a 38 e a 39 entraram na
correção antes de serem executadas contra um número inexistente.
`docs/prompts/` **está dentro** desde a
[CORR-WTE-018](/docs/tasks/CORR-WTE-018.md): a exclusão que ele tinha valia
para destino de link placeholder, não para número afirmado em prosa. E o número
velho escrito na forma `velho → corrente` não derruba nada — é história, e a
guarda sabe disso desde a mesma correção.
