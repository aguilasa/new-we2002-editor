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
| [WTE-TASK-12](/docs/tasks/12-comparacao-visual.md) | Comparação visual dos 18 formulários | 2 | 11 | ✅ Concluído | 2026-08-09 | 2026-08-09 |
| [WTE-TASK-13](/docs/tasks/13-trace-de-eventos.md) | Trace de eventos contra o original | 2 | 11 | ✅ Concluído | 2026-08-09 | 2026-08-09 |
| [WTE-TASK-14](/docs/tasks/14-fechamento-fase-2.md) | Fechamento da fase 2 | 2 | 12, 13 | ✅ Concluído | 2026-08-09 | 2026-08-09 |
| [WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) | Decidir o mapeamento de tipo C++ → Pascal | 3 | 02 | ✅ Concluído | 2026-08-09 | 2026-08-09 |
| [WTE-TASK-16](/docs/tasks/16-gerador-de-tabelas.md) | `gen_tables_pas.py` — offsets e tabelas | 3 | 15 | ✅ Concluído | 2026-08-09 | 2026-08-09 |
| [WTE-TASK-17](/docs/tasks/17-transpilador-da-camada-de-dados.md) | `port_database_pas.py` — o transpilador | 3 | 15, 16 | ✅ Concluído | 2026-08-09 | 2026-08-10 |
| [WTE-TASK-18](/docs/tasks/18-camada-de-dados-gerada.md) | Gerar a camada de dados | 3 | 17 | ✅ Concluído | 2026-08-10 | 2026-08-10 |
| [WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) | Os offsets que o Obocaman tem e nós não | 3 | 06, 18 | ✅ Concluído | 2026-08-10 | 2026-08-10 |
| [WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) | Round-trip headless contra o `we2002_core` | 3 | 18, 19 | ✅ Concluído | 2026-08-10 | 2026-08-10 |
| [WTE-TASK-21](/docs/tasks/21-fechamento-fase-3.md) | Fechamento da fase 3 | 3 | 20 | ✅ Concluído | 2026-08-10 | 2026-08-10 |
| [WTE-TASK-22](/docs/tasks/22-harness-golden.md) | `golden_check.sh` — **o gate** | 4 | 11, 21 | ✅ Concluído | 2026-08-10 | 2026-08-11 |
| [WTE-TASK-23](/docs/tasks/23-formato-da-spec.md) | Formato de `re/spec/` e vocabulário de veredito | 4 | 09 | ✅ Concluído | 2026-08-09 | 2026-08-10 |
| [WTE-TASK-24](/docs/tasks/24-ghidra-convencao-borland.md) | Ghidra com a convenção Borland | 4 | 04, 06 | ✅ Concluído | 2026-08-09 | 2026-08-11 |
| [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | Handlers de carga | 4 | 22, 23, 24 | ✅ Concluído | 2026-08-11 | 2026-08-11 |
| [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | Handlers de edição | 4 | 25 | ✅ Concluído | 2026-08-18 | 2026-08-18 |
| [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) | Handlers de gravação | 4 | 26 | ✅ Concluído | 2026-08-20 | 2026-08-20 |
| [WTE-TASK-28](/docs/tasks/28-import-de-mcr.md) | Import e export de `.mcr` | 4 | 08, 24, 27 | ✅ Concluído | 2026-08-20 | 2026-08-20 |
| [WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md) | Camisa e bandeira 2D | 4 | 08, 24, 27 | ✅ Concluído | 2026-08-21 | 2026-08-21 |
| [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) | Handlers dos 13 diálogos auxiliares | 4 | 25 | ✅ Concluído | 2026-08-21 | 2026-08-23 |
| [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) | Fechamento da fase 4 | 4 | 25-30 | ✅ Concluído | 2026-08-24 | 2026-08-24 |
| [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) | Preço derivado dos atributos | 5 | 24, 25 | ✅ Concluído | 2026-08-24 | 2026-08-24 |
| [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md) | Contador de slots livres de ML | 5 | 20 | ✅ Concluído | 2026-08-19 | 2026-08-19 |
| [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) | Bateria golden completa | 6 | 31-33 | ⬜ Pendente | — | — |
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

**A WTE-TASK-19 percorreu `❌ Bloqueado` → `🔄 Em andamento` → `✅ Concluído` em
2026-08-10, e cada troca foi de natureza.** Ela ficou `❌` enquanto os critérios
abertos não dependessem de esforço — dependiam do oráculo funcionar, e três
passagens seguidas só produziram diagnóstico melhor. A
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez isso; a 4ª passagem cobriu as
seis áreas com um time carregado, e a 5ª fechou o critério dos 50.

**E o fecho veio de duas réguas, não de uma.** A 5ª passagem clicou o que
faltava (roteiro 10) e desceu na lista de times (roteiro 11), levando os
endereçados por execução de 15 para **33**. Os **17** restantes não estavam
esperando clique: o `Database.cpp` do `newWe2002` mostra que eles não são
endereço de campo — 14 são ponto de retomada em fronteira de setor e 3 são base
de varredura, e cada um é endereçado por **um** registro só. A ausência deles
num trace é a previsão do papel que têm, e um teste
(`test_todo_offset_ausente_tem_veredito`) reprova se algum dos 50 voltar a ficar
sem veredito.

Achado que sai da fase 3 e vale para a 5: extrair a camisa lê **16 setores
contíguos em `21168024`..`21203815`**, 8 MB acima do maior offset do
`Offsets.hpp`. É a maior região nova desta task, e é a entrada da
[WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md).

**A WTE-TASK-20 foi executada antes de a 19 fechar**, e isso foi decisão, não
descuido. O `depends_on` dela lista a 19, mas o que ela verifica é contra o
**oráculo B** (o `we2002_core`): dump Pascal × dump C++, o codec de texto,
round-trip de gravação. Nenhum dos seis critérios pede janela, e a parte da 19
de que ela precisaria — offsets novos — já tinha vindo. O que a 19 ainda devia
era **veredito** sobre offsets que o `we2002_core` já declara, e veredito não
muda dump nenhum: os dois lados leem a mesma tabela.

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
| 2 — Casca | 10 a 14 | a UI inteira gerada, os 18 abrindo por `--show` (andaime, retirado na 25), com os 96 stubs logando |
| 3 — Dados | 15 a 21 | camada de dados **gerada** do `we2002_core`, lendo as duas ROMs |
| 4 — Comportamento | 22 a 31 | o gate golden, os 96 handlers com veredito, e as duas features que alimentam gravação |
| 5 — Features | 32 a 33 | preço derivado dos atributos, slots de ML |
| 6 — Paridade | 34 a 37 | bateria completa, divergências registradas, bordas de buffer |
| 7 — Acabamento | 38 a 40 | nome, linhagem, empacotamento, verificação final |

**As quatro features são o motivo do projeto** — são o que o `ed.exe` não tem, e
o resto do trabalho existe para chegar até elas com verificação. **Duas delas
executam na fase 4**, e isso não é desvio de rota: o `.mcr` e a camisa 2D são a
*origem dos bytes* de duas das dezessete gravações, e ficar na mesma task que a
gravação é o que desfaz o ciclo que a numeração antiga carregava (a 27 dependia
delas e elas dependiam da 27). Ver a tabela-âncora `§ → task → fase` na Fase 5
de [`../PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md).

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
                            22 ─────────┘         └──► 30
                                          08,24,27 ──► 28
                                          08,24,27 ──► 29
                                             25-30 ──► 31
Fase 5
   24,25 ──► 32
   20 ──────► 33
                   31,32,33 ──► 34
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
9.  25, depois 26 e 30 em paralelo, depois 27
10. 28 e 29 — as duas features que fecham as gravacoes restantes da 27
11. 31 (fechamento da fase 4)
12. 32 e 33 em paralelo; a 32 pode ser antecipada — ver abaixo
13. 34, depois 35, 36 e 37 em paralelo
14. 38, 39
15. 40 (aceite final)
```

**A 32 (preço) é antecipável por dependência** — plano §10 passo 5. Ela depende
só da 24 e da 25, as duas concluídas, então nada a prende ao fim da fase 4: é
isolada, não depende de gravação, entrega a feature mais desejada antes de a
fase 4 fechar, e valida o ferramental de decompilação num alvo pequeno e
conferível.

Até 2026-08-19 isso se chamava "entra **fora de ordem**", e era verdade: preço
era a 30 e o fechamento da fase 4 era a 29. Com a renumeração o fechamento virou
a 31 e o preço a 32 — a antecipação deixou de contrariar a ordem e passou a ser
só uma escolha de quando.

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
- [x] Fração de código gerado medida contra a tese da §4.4
- [x] Nenhum arquivo gerado editado à mão (provado por `--check`)

### Fase 3 — Dados

- [x] Mapeamento de tipo decidido, incluindo `char[N]`, bitfield e `CdImage`
- [x] Offsets e tabelas gerados, com os valores conferidos por **dois
      compiladores** — não pelo parser do próprio gerador
- [x] `FORBIDDEN` e `check_seeks()` no transpilador, testados com entrada plantada
- [x] As seis unidades de dados geradas e compilando
- [x] Toda recusa do `FORBIDDEN` com rota escolhida e razão
- [x] Diff de controle (gravar sem editar) medido antes de qualquer offset novo
- [x] Dumps Pascal e C++ idênticos nas duas ROMs
- [x] Bitfield de `SquadNumbers` conferido contra imagem real
- [x] Registrado se o Ghidra foi necessário na fase 3 — **não foi**, e a
      medida está na seção 4 do
      [`fase-3-fechamento.md`](../../wte/re/fase-3-fechamento.md)

### Fase 4 — Comportamento

- [x] Harness golden com as quatro guardas, controle verde e positivo detectado
      — os três modos medidos em 2026-08-10: controle byte-idêntico, byte
      plantado detectado com offset, e `golden` passando só com as nove
      faixas declaradas no roteiro
- [x] Gabarito de spec com o campo **evidência**, e a proibição de colar decompilado
- [x] Convenção Borland aplicada; `colorearClick` com assinatura correta
- [x] Os 96 nomes aplicados no Ghidra por script
- [x] Rota de VMT decidida com o teste das cinco chamadas
- [x] 96 entradas em `re/spec/`, nenhuma `aberto` — **96 de 96 têm arquivo e
      veredito fechado** (2026-08-24, quinta passagem da
      [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md), medido pelo
      `check_fase4.py`): 69 `implementado`, 19 `trivial`, 6 `divergencia
      deliberada`, 2 `nao portado`, **0 `aberto`**, 0 sem spec. Registro em
      [`wte/re/fase-4.md`](../../wte/re/fase-4.md).
      **O critério percorreu 78 → 81 → 93 → 96 em quatro passagens, e nenhuma
      delas implementou um handler** — o que segurava era régua que não
      alcançava, dono não nomeado ou prosa vencida; doze dos dezesseis `aberto`
      da primeira passagem já tinham corpo Pascal escrito. Os três últimos
      eram de preço e vieram com a
      [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md)
- [x] **Três `aberto` estavam presos por "nada exercita o corpo" e a bateria
      golden já os exercitava** *(medido na
      [CORR-WTE-089](/docs/tasks/CORR-WTE-089.md), 2026-08-24)*. A frase tinha
      sido escrita a partir do `compara_tela.sh`, que é régua de **pixel** e não
      clica a lista de jogadores; a régua de **byte** clica, e sempre clicou. O
      `lista_jugadores_1Change` dispara em **quatro** gates verdes
      (`golden-09`, `-10`, `-11`, `-15`), o `lista_equipos_2Change` em três —
      com **64** disparos em dois deles, que é a lista inteira até o primeiro
      clube de ML — e o `parribaClick` no `golden-11`, guardando o buffer que o
      `pabajo` grava logo depois. Os três passaram a `implementado`. **Uma das
      três razões era minha, de um dia antes**, e o registro fica na spec: o
      número (69 disparos do irmão, zero deste) estava certo e a conclusão
      generalizava de um instrumento para todos. Mecanizado pelo
      [`cobertura_gate.py`](../../wte/tools/cobertura_gate.py), que versiona a
      cobertura em [`fase-4-cobertura.tsv`](../../wte/re/fase-4-cobertura.tsv) e
      **aborta** se uma spec citar o TSV como evidência sem ter linha nele
- [x] **Três `aberto` esperavam decisão, não medição, e um deles fechava um
      ciclo entre fases** *(CORR-WTE-090, 2026-08-24)*. O
      `jugador.flechasapaClick` esperava exclusão **já decidida** em 2026-08-18
      pela [CORR-WTE-063](/docs/tasks/CORR-WTE-063.md); o
      `MainForm.boton_dialogo_weClick` tinha as duas razões antigas caídas e
      sobrava uma diferença de estrutura por decisão — o port tem uma rota de
      injeção onde o original tem duas; e o `estrategia.ComboBoxDrawItem`
      esperava a [WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md), **que é
      fase 6 e depende da 34, que depende desta** — esperar travava as três
      para sempre. Viraram `divergencia deliberada`, `divergencia deliberada` e
      `nao portado` com justificativa de **escopo**, que é o que o critério da
      fase 4 prevê e o `MainForm.Button2Click` já usava. A decisão de
      *owner-draw* continua sendo da 37; o que mudou é que ela deixou de
      bloquear o fechamento da fase 4
- [x] **Handler de *desfazer* não se julga sozinho** *(CORR-WTE-091,
      2026-08-24)*. O `jugador.BitBtn1Click` (o botão `Original `) tem seis
      bytes e esperava mudança de estrutura, não código: a `PreencheFicha`
      morava no `.aux.inc` do `MainForm`, invisível de fora, e desceu para a
      [`wte_ficha`](../../wte/src/wte_ficha.pas) como a CORR-WTE-081 já fizera
      com o buffer de jogador. **A régua teve de ser um par**, e essa é a lição:
      clicar `Original ` sem ter editado nada antes passaria com o corpo vazio.
      O [`golden-18-ficha-edicao`](../../wte/tests/roteiros/golden-18-ficha-edicao.txt)
      edita o número de camisa e grava `0xc0`; o
      [`golden-19-ficha-original`](../../wte/tests/roteiros/golden-19-ficha-original.txt)
      edita, clica `Original ` e grava `0x80` — **o valor que a ROM intocada já
      tinha**. Os quatro gates deram byte-idêntico, e o par fechou também o
      `casilla_dorsalKeyPress`, que ele exercita de passagem
- [x] **Gate verde não prova que o estímulo aconteceu** *(CORR-WTE-092,
      2026-08-24)*. Se os dois lados não fizerem nada, os dois concordam. O
      harness ganhou o verbo `arrasta` — não havia um `mousedown` sequer em
      `wte/tools/*.sh` — e dois roteiros novos, e **os dois passaram antes de
      estarem certos**. O arrasto na coordenada do `.lfm` caía no `campo` (as
      bolas medem 10×10 em execução e estão onde a `PreencheTelaDeTatica` as
      pôs, não onde o `.lfm` diz); corrigida a coordenada, o `bolaMouseDown`
      **disparava** e o gate seguia medindo zero, porque soltar fora da zona da
      própria bola devolve a bola ao lugar. Só dentro da zona os bytes mudam —
      dois, o X e o Y. A régua que pegou as duas foi sempre a mesma: comparar
      com uma corrida **sem** o estímulo. Fecharam o
      `estrategia.bolaMouseDown` e o ramo do reserva do
      `MainForm.mostrar_jugadorClick`, este último provado por escrever noutro
      registro de jogador (`388807` contra `388567`)
- [x] **Os dois últimos corpos fora de preço** *(CORR-WTE-093, 2026-08-24)*. Os
      quatro laços de 11 iterações do `estrategia.FormCreate` — a única pergunta
      que a spec se recusava a adivinhar — são a montagem da **tabela de
      formações**: quatro colunas de 11 intercaladas em registros de 44, dezoito
      vezes. **A leitura terminou em decidir não escrever código**, porque o
      `dump_formacoes.py` já gera a mesma tabela; o corpo faz só o que sobra. O
      slot virtual `0xcc` do fim foi medido no VMT de `TListBox`
      (`SetItemIndex`), pelo mesmo método do `SetEnabled = VMT[0x64]`. E o
      `boton_dialogo_texClick` virou `divergencia deliberada`: o original guarda
      um `FILE*` aberto pela sessão e o port guarda caminho, divergência que o
      `we2002_estado` já documentava antes do corpo existir
- [x] **Sete dos dezesseis `aberto` estavam presos por prosa vencida** *(achado
      da WTE-TASK-31, terceira passagem, 2026-08-23)*. A spec dizia *"aberto
      porque a `0x…` não está portada"*, outra task portava a rotina, e ninguém
      voltava ao arquivo — o veredito seguia afirmando um bloqueio que não
      existia mais. **Três foram promovidos com a régua rodando no dia**: o
      `lista_equiposChange` (`compara_tela.sh 2 68`, 5 de 5 barras em pixel e 0
      de 8.960 / 0 de 9.800 px em bandeira e uniforme), o `FormShow` (para
      `divergencia deliberada`, pelas duas divergências de `dat.bin` que ele já
      declarava) e o `estrategia.relojTimer` (a `0x0040a0b4` caiu na
      CORR-WTE-082: abrir a tática dispara o handler cinco vezes, quatro quadros
      mais o encaixe, e as posições viram os 30 bytes que o `golden-17-tatica`
      compara). **Os outros quatro tiveram a razão reescrita e continuam
      `aberto`**, porque nenhuma régua os alcança. A classe ficou trancada pela
      guarda `BLOQUEIO_VENCIDO` do `check_fase4.py`: numa spec `aberto`,
      endereço citado como "não portada" que apareça no Pascal **aborta** o
      fechamento — recusa vista, com a frase plantada de volta
- [x] **Três gravações órfãs, achado da WTE-TASK-30 (2026-08-21), fechadas
      pela [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md).** O grupo `auxiliar` não era
      de "avisos e confirmações": o `OK` do `ficha_color` (`0x004069e8`), o
      `Comple.` do `jugador` (`0x00408548`) e o ` Accept` do `estrategia`
      (`0x0040a660`) **escrevem na imagem**. A WTE-TASK-27 contava seis
      gravações; medido, são **nove**. As três specs estão completas e dizem o
      que falta em cada uma, e a correção fixa a ordem — `jugador`,
      `ficha_color`, `estrategia` —, cada uma com o controle fechando antes do
      golden. **Ela vem antes da
      [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md)**, que é fechamento e
      não implementa: sem isso a 31 só teria como listar a falta.
      **Duas das três fecharam em 2026-08-21.** O `Comple.` do `jugador`
      está `implementado`, com o par `golden-15-ficha` verde nos três modos;
      ele trouxe a unidade neutra `wte/src/wte_ficha.pas`, para onde desceu o
      buffer de jogador — o que destrava o `jugador.BitBtn1Click` também — e
      corrigiu o filtro de nome do `0x0040b2d8`, que era divergência de tela e
      virou divergência de byte no dia em que a ficha ganhou botão que grava.
      O `OK` do `ficha_color` fechou com o par `golden-16-cor`, também nos três
      modos, e trouxe o gerador `wte/tools/dump_blococor.py` — a tabela de 95
      bytes que diz qual paleta de bandeira cada time usa **não é identidade**,
      e escrevê-la à mão seria copiar 95 números sem quem os conferisse. Falta
      o `estrategia`, e o pré-requisito dele **caiu em 2026-08-21**: a
      [CORR-WTE-082](/docs/tasks/CORR-WTE-082.md) portou a `0x0040A0B4` como
      `PreencheTelaDeTatica`, na `wte/src/wte_tatica.pas`, e com ela fecharam o
      `estrategia.BitBtn1Click` e o `MainForm.mostrar_estrategiaClick` — mais
      as duas divergências que a spec do `lista_formacionesClick` devia àquela
      rotina. Medida a tela contra o oráculo em três times pelo
      `compara_tela.sh --malha`.
      **As três fecharam em 2026-08-21**, e com elas a CORR-WTE-081: o
      ` Accept` do `estrategia` é a oitava rota de escrita, 45 bytes por time,
      com o par `golden-17-tatica` verde nos três modos. O índice saiu de 23
      `aberto` no dia em que a correção abriu para **18**
- [x] Corpo de handler escrito à mão tem onde morar sem quebrar a regra de
      arquivo gerado: `wte/src/impl/*.inc` referenciado por `{$I}`, com o
      `dfm2lfm.py` abortando em `.inc` órfão
- [x] Toda gravação byte-idêntica — **as 17, com gate declarado cada uma**, e
      desde 2026-08-20 sem exceção nenhuma: os dois remendos literais de
      arranque foram portados e **nenhum roteiro do gate declara faixa
      `conhecida:`**. O `.mcr` (28) e a camisa (29) entraram, e a bateria da
      quinta passagem fechou **42 de 42 corridas verdes** — 21 roteiros com par,
      cada um com controle e golden, 3.958 s. *Adaptado de "nas duas ROMs":*
      **medido em 2026-08-18 que a europeia não hospeda este grupo** — o
      `wte.exe` morre na troca de time (49.749 violações de acesso) e a gravação
      nunca acontece, então o oráculo não existe daquele lado. O critério vale
      como está para a japonesa e a europeia é da
      [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md); ver
      [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md).
      **E "gravação" nem sempre quer dizer a imagem:** o `grabar_memory` emite
      um `.mcr` e deixa a ROM intacta, então o gate ganhou `--artefato` em
      2026-08-19 — comparar só as duas imagens aprovaria um port inerte; quatro
      roteiros usam
- [x] Cinco `trivial` reamostrados e reconferidos — na WTE-TASK-31
      (2026-08-22), por disassembly, com o registro em
      [`wte/re/fase-4-trivial.tsv`](../../wte/re/fase-4-trivial.tsv). A amostra
      é **declarada, não sorteada**: cinco espaçados uniformemente pela lista
      ordenada por endereço, para o `--check` poder refazê-la. Os cinco
      confirmaram, e nos três `FormCreate` a cor que o original passa a
      `TControl::SetColor` é a mesma que o `.inc` do port escreve
- [x] **Dez times desenham bandeira preta** *(achado da WTE-TASK-31,
      2026-08-22, fechado pela
      [CORR-WTE-083](/docs/tasks/CORR-WTE-083.md) em 2026-08-23)*. O
      `compara_tela.sh` mediu quatro times: 2 e 0 batem em pixel nas cinco
      barras, na bandeira e no uniforme; o **56** (`CLASSIC ENGLAND`) e o combo
      **68** (`ml_teams[5]`, `HIGHLANDS`) divergem em 3.840 de 3.840 pixels de
      bandeira, com barras e uniforme batendo na mesma corrida. `flag_colours`
      carrega como dezesseis zeros em `teams[56..63]`, `ml_teams[5]` e
      `ml_teams[22]`. **Não é defeito do port:** o laço é transpilado do
      `we2002_core`, o `ed.exe` para no time 55 e pula o 5 e o 22 do bloco de
      ML, e ele nunca precisou dessas cores porque não desenha bandeira. O
      editor do Obocaman desenha, e as lê pela tabela de offsets em `.data`.
      **Consertado no mesmo dia pela rota B**, com a
      `CarregaBandeirasQueOCoreNaoLe` da `wte_cor` preenchendo, depois do
      `Load` e fora dele, só o que o core deixou zerado — o `compare_dumps.py`
      continua idêntico nas duas ROMs. Medido antes de virar código: dos 95
      slots, **85 batem** entre a carga do core e a tabela do Obocaman, 10 estão
      zerados e **um diverge de propósito** (`teams[39]`). Oito dos nove
      alcançáveis fecham em 0 de 3.840; são **sete** CLASSIC e não oito, porque
      o `teams[63]` tem nome vazio e nenhum item do combo o alcança. O nono, o
      combo 85, ficou um dia com o que se leu como diferença de POSIÇÃO, e a
      [CORR-WTE-084](/docs/tasks/CORR-WTE-084.md) mediu em 2026-08-23 que o
      desvio era da régua: a `bandas()` do `compara_tela.py` somava pixel por
      linha e contava a camisa remanejada. **Os onze times medidos fecham em
      pixel** — 0, 2, 56–62, 68 e 85
- [x] **A fase 4 fechou: 96 de 96 vereditos** *(2026-08-24)*. O último era o
      `MainForm.base_teamClick`, e ele é preço — a
      [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) o fechou junto com os
      dois handlers de preço da ficha, que nem spec tinham. **E o preço é a
      décima oitava rota de escrita**, com gate próprio
      ([`golden-22-precos`](../../wte/tests/roteiros/golden-22-precos.txt)),
      controle antes e byte-idêntico
- [x] **As gravações não são nove, são dezessete** *(medido na WTE-TASK-31,
      2026-08-22)*. Nove era a conta de quem alguém *chamou* de gravação;
      lendo a seção `## Bytes tocados` das 96 specs, **entram** os sete de
      mover jogador e número de camisa e os dois do arranque (`FormShow`,
      `boton_dialogo_weClick`), e **saem** o `grabar_memoryClick` e o
      `grabar_camisetaClick`, que emitem arquivo e deixam a ROM intacta. A
      tabela de gates do `check_fase4.py` é guardada: gravação sem roteiro
      declarado aborta o fechamento — era por não existir essa conta que três
      ficaram sem dono até a WTE-TASK-30
- [x] `.mcr`: contêiner por documentação pública, conteúdo revertido — 16
      destinos mapeados dos **dois** lados em
      [`wte/re/mcr.md`](../../wte/re/mcr.md), com o contêiner lido do molde e
      não suposto
- [x] Os três casos especiais do readme do original cobertos, cada um pelo
      instrumento que alcança onde ele mora: **capitão e cobradores** e
      **espaços no nome** em `test_mcr.pas` sobre cartão sintético (com
      mutação vista reprovando nos dois); **goleiro da Eire** pelo `--check` do
      `dump_mcr.py`, que lê do `.text` o carimbo `+0x16 := 0xFF` da
      `0x0040478c` e o compara com o Pascal, mais o `golden-13-roundtrip`, que
      importa **no time 0** — o único onde o caso se manifesta
- [x] `boton_mcr2isoClick` byte-idêntico — dois gates verdes, o
      `golden-12-mcr2iso` (time 3) e o `golden-13-roundtrip` (time 0, com
      exportação de volta e `--artefato`). **O EDC/ECC saiu por refutação:** a
      premissa do critério estava errada, este handler **não** escreve setor
      inteiro. As sete faixas que ele grava cabem todas no payload de 2048 B — a
      maior tem 276 bytes —, e a conta é a do `gravacao_controle.py`: 164 faixas
      em 12 sessões, nenhuma tocando byte de EDC/ECC nem cabeçalho de setor.
      Escrita de cartão inteiro existe, mas é no `.mcr`, que é plano
- [x] Render 2D: paleta vs. pixel decidido, tolerância **medida** — **é
      paleta** (as três rotinas reescrevem entradas em `0x36`, nenhuma toca
      pixel), a aritmética de escurecer/clarear é na palavra BGR555 empacotada,
      e o gradiente acumula em `Single` e **trunca para zero** — as duas causas
      do risco nomeado da §9, medidas em
      [`wte/re/render2d.md`](../../wte/re/render2d.md). **E a tolerância é
      zero, medida em três réguas.** As duas primeiras mediam a paleta como ela
      veio da imagem: `compara_tela.sh 2 9 63` compara `bandera`, `home1` e
      `home2` pixel a pixel e dá 0 de 8.960 px (9.800 no clube de ML), e
      `--cor` compara as **16 amostras** do editor e dá 0 de 5.168 px. A
      terceira é a **grade** do enunciado, e ela mede depois de *calcular*:
      `--grade` clica três vezes em escurecer, uma em clarear e uma no
      gradiente, nos dois lados, e nos mesmos três times **16 de 16 amostras
      mudam** e a divergência continua 0 nos dois recortes. Quatro recusas
      vistas, entre elas a faixa aberta no escurecer (12 de 16 amostras, 3.792
      de 3.840 px da bandeira) e o gradiente escrevendo a partir da ponta (15
      de 16)
- [x] `grabar_camisetaClick` byte-idêntico, sem tolerância — **fechado em
      2026-08-21** pelo [`golden-14-uniforme`](../../wte/tests/roteiros/golden-14-uniforme.txt),
      com controle antes: 30.956 bytes idênticos nos dois lados, e a imagem
      intacta nos dois. Ele **não grava na imagem**: lê dela e emite arquivo,
      com o laço saltando cabeçalho e EDC/ECC de cada setor, então o gate é
      `--artefato` e o critério de EDC/ECC não se aplica. A recusa foi vista —
      sem o `+ 32` do campo de tamanho o artefato sai com 30.924 bytes

Os cinco bullets acima vinham da Fase 5 até 2026-08-19. Eles desceram junto com
as tasks: cada uma das duas features fechou de vir depois da gravação que ela
alimenta e passou a **carregar** essa gravação.

### Fase 5 — Features

- [x] Fórmula de preço por tabela de verdade **e** conferida no disassembly —
      `s⁴ div 3000000 + s³ div 40000 + s² div 700 + s div 7 + 5`, com
      `× 5 div 3` para goleiro, sobre a soma das dezesseis barras de
      habilidade. **132 jogadores em 6 times, 100% de acerto**
      ([`wte/re/preco.md`](../../wte/re/preco.md)). E as fontes são três, não
      duas: os **dois** handlers foram lidos instrução a instrução e são a
      mesma fórmula compilada duas vezes
- [x] Saturação, arredondamento e termo cruzado testados — 12 conferências em
      [`test_preco.pas`](../../wte/tests/test_preco.pas). **A saturação não é
      teto, é transbordo de 32 bits**: o original faz `imul` de 32×32 e um
      `cdq` logo em seguida, que joga fora a metade alta. O ponto de virada foi
      medido — soma **216** —, e a partir dali o preço do original **cai**
      enquanto o de 64 bits sobe. Reproduzido de propósito, com `LongInt`
- [x] Slots de ML batendo com a tela do original nas duas ROMs — europeia `13` nos dois lados; japonesa `1` nos dois com o mesmo conteúdo de arquivo (o oráculo altera a imagem ao abrir, ver a [WTE-TASK-33](/docs/tasks/33-slots-de-master-league.md))

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
- **~~O `wte.exe` não passa da tela de carga~~ — resolvido em 2026-08-10, com a
  ROM japonesa.** Fica registrado porque a história explica três passagens da
  WTE-TASK-19 e o desenho do gate da 22. Medido na WTE-TASK-19: o editor
  **morre** ao trocar de time, com a ROM europeia deste repositório — a
  japonesa nunca tinha sido medida neste caminho, e passa. A atribuição é medida, não lida da tela — os roteiros
  [07](../../wte/tests/roteiros/07-controle-sem-time.txt) e
  [08](../../wte/tests/roteiros/08-so-troca-de-time.txt) são iguais linha a
  linha até `= ARRANQUE` e o 08 só acrescenta a troca de time: **0 violações de
  acesso no 07, 309 no 08**.

  **Duas hipóteses de causa já caíram, as duas por experimento.** *Não é o
  tamanho*: truncar a European Deluxe para os 474.431.328 bytes exatos que o
  editor pede (150 setores a menos, todos na cauda) faz o aviso sumir e não
  muda uma faixa do mapa de I/O. *E não é a região vazia em `14368636`* — a
  última leitura antes da falha, com 4 bytes não-zero em 64 amostrados contra
  32 a 64 em toda outra faixa: isso é correlação, e o `analisar_io.py` só
  enxerga I/O, então não tinha como distinguir.

  **A causa medida é outra:** com `WINEDEBUG=+seh,+loaddll`, a violação de
  acesso cai dentro do `vcl60.bpl`, em `Graphics::TFont::SetSize`, com o `this`
  **nulo** — chamada de uma rotina do `.exe` que procura um controle por
  `FindComponent("dorsal" + N)`. **É estado de interface, não leitura da
  imagem:** falta o objeto, não o byte. Detalhe, com endereços e chamadores, em
  [`../../wte/re/crash.md`](../../wte/re/crash.md).

  **Veredito (CORR-WTE-044, 2026-08-10): resolvida — o oráculo é dirigível com
  a ROM japonesa.** O controle **existe** (os 23 `dorsalN` estão vivos no
  `MainForm`, `TStaticText`, com `Font` não nula); o que não presta é o
  ponteiro em `0x004335e4`, que a carga do time sobrescreve com dado de uma
  tabela vizinha. Mesmo roteiro 08, mesmas marcas, só a imagem muda:
  **49.749 violações de acesso com `roms/golden-european-deluxe.bin`, 0 com
  `roms/japanese-shift-jis.bin`** — e nesta o ponteiro recebe o `dorsal1` certo.
  Refeito duas vezes. A frase acima sobre a região em `14368636` fica de pé por
  outra razão ainda: as duas imagens leem **essa mesma faixa** ao trocar de
  time, e só uma trava.

  Consequência: o gate golden da
  [WTE-TASK-22](/docs/tasks/22-harness-golden.md) **tem em que se apoiar**,
  desde que fixe a imagem japonesa e diga por quê. A circularidade que a
  [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) existia para quebrar — 22 precisa
  do oráculo vivo, entendê-lo seria a WTE-TASK-25, e a 25 depende da 22 — está
  desfeita sem implementar handler nenhum. Medição, ressalvas e o que ficou sem
  resposta em [`../../wte/re/crash-causa.md`](../../wte/re/crash-causa.md).
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
│   │   ├── ep2002_*.pas              ← WTE-TASK-10 (gerado; diz NÃO EDITAR)
│   │   ├── impl/*.inc, *.aux.inc     ← WTE-TASK-25 a 30 (os corpos, incluídos
│   │   │                               nos ep2002_*.pas por {$I impl/...})
│   │   ├── we2002_estado.pas         ← WTE-TASK-25 (o estado global do app)
│   │   ├── we2002_offsets.pas        ← WTE-TASK-16 (gerado)
│   │   ├── we2002_tables.pas         ← WTE-TASK-16 (gerado)
│   │   ├── we2002_database.pas       ← WTE-TASK-18 (gerado)
│   │   ├── we2002_player.pas         ← WTE-TASK-18 (gerado)
│   │   ├── we2002_cdimage.pas        ← WTE-TASK-18 (gerado)
│   │   ├── we2002_textcodec.pas      ← WTE-TASK-18 (gerado)
│   │   ├── we2002_types.pas          ← WTE-TASK-18 (gerado)
│   │   ├── we2002_team.pas           ← WTE-TASK-18 (gerado)
│   │   ├── we2002_preco.pas          ← WTE-TASK-32
│   │   ├── we2002_mcr.pas            ← WTE-TASK-28
│   │   ├── we2002_render.pas         ← WTE-TASK-29
│   │   ├── we2002_bmp.pas            ← WTE-TASK-29
│   │   ├── wte_render2d.pas          ← WTE-TASK-29 (a unica que usa LCL)
│   │   ├── wte_uniformes.pas         ← WTE-TASK-29 (gerado)
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
│   │   ├── fase-3.md                 ← WTE-TASK-20 (os valores batem?)
│   │   ├── fase-3-fechamento.md      ← WTE-TASK-21 (quem escreveu o código?)
│   │   ├── vmt.md                    ← WTE-TASK-24
│   │   ├── campos.tsv, campos.md     ← WTE-TASK-25 (nome → deslocamento)
│   │   ├── arranque.tsv, arranque.md ← WTE-TASK-25 (os 18 FormCreate/FormShow)
│   │   ├── auxiliares.tsv, .md       ← WTE-TASK-25 (as rotinas nao publicadas)
│   │   ├── spec/                     ← WTE-TASK-23 a 33
│   │   ├── golden.md                 ← WTE-TASK-34
│   │   ├── divergencias.md           ← WTE-TASK-35
│   │   └── buffers.md                ← WTE-TASK-36
│   ├── tools/
│   │   ├── dfm_extract.py            ← WTE-TASK-03
│   │   ├── check_fase1.py            ← WTE-TASK-09
│   │   ├── dump_campos.py            ← WTE-TASK-25
│   │   ├── dump_arranque.py          ← WTE-TASK-25
│   │   ├── dump_auxiliares.py        ← WTE-TASK-25
│   │   ├── check_barras.py           ← WTE-TASK-25
│   │   ├── check_lcl_combo.py        ← WTE-TASK-25
│   │   ├── compara_tela.py, .sh      ← WTE-TASK-25, CORR-WTE-057
│   │   ├── dfm2lfm.py                ← WTE-TASK-10
│   │   ├── gen_tables_pas.py         ← WTE-TASK-16
│   │   ├── port_database_pas.py      ← WTE-TASK-17
│   │   ├── check_fase3.py            ← WTE-TASK-21
│   │   ├── roteiro.sh                ← WTE-TASK-19, 22 (biblioteca)
│   │   ├── golden_check.sh           ← WTE-TASK-22
│   │   ├── golden_run_wte.sh         ← WTE-TASK-22 (lado oraculo)
│   │   ├── golden_run_laz.sh         ← WTE-TASK-22 (lado port)
│   │   ├── golden_veredito.py        ← WTE-TASK-22
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

**WTE-TASK-21 — a fase 3 fecha com 91,8%, e o que sobra tem nome.** A camada de
dados é saída de gerador nos oito arquivos, mas nem toda linha emitida é
transpilação: 303 delas são Pascal escrito à mão que mora nas constantes do
próprio gerador — as quatro peças que o `tipos.md` já decidira que não
transpilam. "100% gerado" seria verdade de arquivo e mentira de conteúdo, e a
§4.5 fala de conteúdo. A medida sai do
[`check_fase3.py`](../../wte/tools/check_fase3.py), e conta **linha física dos
dois lados** — a fração foi publicada como 92,5% até a
[CORR-WTE-051](/docs/tasks/CORR-WTE-051.md), quando o total contava linha em
branco e o manual não.

**E o app ainda não lia o jogo no fechamento da fase 3 — medido, não opinado.**
Zero unidade da casca dava `uses we2002_database`; quem consumia eram dois
programas de console de `wte/tests/`. A integração mínima ficou para a
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md), **depois** do gate da
[22](/docs/tasks/22-harness-golden.md): fazê-la no fechamento seria implementar
dois handlers sem o gate que os julga.

**Entrou em 2026-08-11, e a régua acompanhou.** `src/we2002_estado.pas` abre a
imagem e carrega o banco; o `test_so_teste_consome_a_camada` — que existia
prevendo a própria falha — teve a asserção invertida, e o
`fase-3-fechamento.md` foi regerado pelo ramo que o gerador já tinha escrito.
Popular o combo de times continua aberto.

**A lição que atravessa fase:** corrigir prosa de documento não alcança a cópia
que mora dentro de um gerador. A CORR-WTE-049 consertou no `progresso.md` a
frase que trocava duas populações de offset; a mesma frase continuou no
`compare_dumps.py`, e de lá saía para o `fase-3.md` a cada regeração. A varredura
de sítios da WTE-TASK-09 varre markdown — esta cópia era Python.

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

**WTE-TASK-20 — a premissa do codec estava invertida, e o enunciado foi
corrigido.** A task dizia que a ROM japonesa é *o único teste real* do
`KanjiToAscii`. Medido: o codec só conhece os bytes de chefe 130 (`0x82`,
latino de largura dupla) e 129 (`0x81`, o ponto), então quem exercita os ramos
de mapeamento é a **European Deluxe** (95 de 95 campos decodificados) e a
japonesa exercita o **ramo padrão** (0 de 95 — katakana vira espaço). As duas
continuam necessárias, por motivos trocados. Vale como aviso geral: *"sem esta
entrada o código X não é exercitado"* é afirmação sobre cobertura, e cobertura
se mede — [`../../wte/re/fase-3.md`](../../wte/re/fase-3.md).

**E zero contra zero não prova nada.** O critério da 20 é que as duas gravações
saiam byte a byte iguais; se o `Save` parasse de gravar, elas continuariam
iguais e o critério passaria verde. Por isso a evidência mede também o
round-trip **contra o original** (270 B em 4 faixas na europeia, 1.249 B em 15
na japonesa) e há teste exigindo que esse número seja maior que zero. Todo
critério da forma "os dois lados concordam" precisa do par: concordam, **e**
fizeram alguma coisa.

**WTE-TASK-25 — a ordem do `.dfm` não é a ordem dos campos, e derivar dali é o
erro que parece certo.** Todo handler do `.exe` referencia controle por
deslocamento, e a derivação barata seria "primeiro `object` do `.dfm` no
primeiro campo". Medido pelo
[`dump_campos.py`](../../wte/tools/dump_campos.py): essa regra acerta **73 de
440**, e no `MainForm` **zero de 116**. A ordem do `.dfm` é a de criação, a dos
campos é a da declaração no `.h`. O mapa certo sai da *published field table*
que o VMT aponta em **-56** — irmã da published method table da WTE-TASK-04, e
viva pelo mesmo motivo: sem ela o formulário não carrega. É a armadilha 1 por
outro caminho, e sem a field table o `MainForm.FormCreate` teria sido lido
guardando `dorsal4`, `dorsal22` e `dorsal23` em global, quando o que ele guarda
é `bandera`, `home1` e `home2`.

**E a fração da §4.4 estava medindo duas populações diferentes.** O mecanismo de
`wte/src/impl/*.inc` tira o corpo do `.pas` gerado — que encolhe — e o põe num
`.inc` que o `check_fase2.py` não contava: a fração **subia** a cada handler
implementado. Com os 303 na conta ela cai de 95,9% para **93,0%**, e daqui em
diante cai de novo a cada corpo escrito, que é o sinal certo. É a
[CORR-WTE-051](/docs/tasks/CORR-WTE-051.md) de novo, e das duas vezes quem
achou foi revisão. Agora há guarda: o `check_fase2.py` **reprova** se a frase da
§4.4 do plano não trouxer a fração medida no dia — número em documento de fonte
de verdade passou a ser falha de build, como os quatro da WTE-TASK-09.

**WTE-TASK-25 — os dois oráculos falam do mesmo lugar, e provar isso custou
minutos.** O original não guarda offset para as barras de força: ele calcula,
`2352 * (t div 2048) + (t mod 2048) + 0x1e8178`, com `t = 0x45ff0 + 5*índice`.
A conta leva o time 0 para **2328184** — a `OFS_TEAM_BARS` que o `we2002_core`
já conhece — e a conferência byte a byte contra o `dump_estado.pas` mostra que
os 95 itens da lista são os **63 `teams` seguidos dos 32 `ml_teams`**. O port
pode ler a camada de dados em vez de reabrir a imagem, e isso não é suposição.
É o método da §4.2 rendendo o que promete: o diff diz *onde*, o core diz *o
que*. Virou guarda de build no
[`check_barras.py`](../../wte/tools/check_barras.py), que decodifica as
constantes do próprio corpo do handler — constante que mude no binário derruba
a conferência em vez de passar.

**E spec medida com veredito `aberto` vale mais que meio corpo escrito.** O
`lista_equiposChange` chama auxiliares que não são dele, parte deles de outra
task. Escrever a metade que dá faria o `check_fase2.py` contar o handler como
"com corpo escrito" — índice afirmando pronto o que está pela metade, que é o
defeito que a CORR-WTE-049 e a CORR-WTE-051 já pagaram. O `.inc` só entra
quando o corpo inteiro entrar.

**WTE-TASK-25, quarta passagem — a lista desses auxiliares era escrita à mão, e
por isso estava curta.** A spec listava cinco endereços; medido pelo
[`dump_auxiliares.py`](../../wte/tools/dump_auxiliares.py), o handler chama
**treze** rotinas internas. Parte é biblioteca, que uma lista à mão descartaria
de propósito — mas `0x004050d0` e `0x0040cbc8` carregam dado do jogo, e essas
não estavam sendo descartadas: não estavam sendo vistas. É a armadilha 11 numa
população nova: enquanto a fase 4 tiver handler `aberto`, cada um carrega uma
lista dessas, e lista à mão erra da forma que não aparece.

**Dois encontros novos entre os oráculos, os dois virados guarda.**
`0x00403388` não recebe offset: pergunta ao `ftell` onde está e, se `posição
mod 2352 = 2072`, avança 304 — a mesma geometria de setor que o `we2002_core`
tem pré-somada nos `OFS_*`, só que resolvida em tempo de execução. E
`0x0040cbc8` varre a tabela de offsets a partir de `0x004231a0`, exatamente
onde a [WTE-TASK-06](/docs/tasks/06-mapa-de-offsets.md) a registrou por outro
caminho. As duas afirmações são decodificadas do corpo das próprias rotinas a
cada `make -C wte check`, e a segunda confronta o `offsets.tsv` em vez de
repetir o número.

**Achado que vai para a WTE-TASK-35:** o que parecia decodificador de nome é
**filtro**. As duas tabelas que `0x0040b2d8` indexa são identidade, então a
rotina copia letra, dígito, `.` e espaço, troca byte acima de `z` por `?` e
descarta o resto — enquanto o `we2002_core` devolve espaço para byte
desconhecido. Divergência de tela, não de gravação.

**WTE-TASK-25, quinta passagem — a LCL não é o Qt, e isso se mede.** O Win32
não dispara `CBN_SELCHANGE` em `SetCurSel`; o Qt **dispara**
`currentIndexChanged` em `setCurrentIndex`, e o `newWe2002` precisou de
`QSignalBlocker` nas cargas de time. Medido em gtk2 pelo
[`test_lcl_combo.pas`](../../wte/tests/test_lcl_combo.pas): **nenhum** dos cinco
casos dispara — nem `ItemIndex :=`, nem reatribuir o mesmo índice, nem
`Items.Clear` com item selecionado. A LCL se comporta como o original, e os
corpos da fase 4 dispensam bloqueio de sinal. Virou guarda de build
([`check_lcl_combo.py`](../../wte/tools/check_lcl_combo.py)) porque a resposta é
propriedade do **widgetset instalado**, e pode virar num upgrade sem que uma
linha deste repositório mude.

**E entrou a casa dos auxiliares:** `wte/src/impl/<unidade>.aux.inc`, um por
unidade, incluído antes dos handlers — em Pascal a ordem de declaração é o que
autoriza a chamada. As linhas dele já entram na conta de escrito à mão do
`check_fase2.py` por wildcard, e a fração da §4.4 caiu de 93,0% para **92,1%**,
com o guard do próprio `check_fase2.py` reprovando até o plano trazer o número
novo.

**Armadilha 6 por uma porta nova.** Um `wte` esquecido no `:99` sobrou de uma
**captura de tela minha**, não de teste manual: `kill %1` não funciona em shell
não interativo. A guarda do `golden_check.sh` pega janela grande antes de
começar; processo solto de medição de apoio não passa por ela.

**WTE-TASK-25 — fechou em dez passagens, e o que a fechou foi a conferência de
tela.** Ela achou dois erros que nenhum teste pegaria: a ordem dos três campos
de nome (`names[1]`, `names[0]`, `abbreviations[0]`, e não `names[0..2]`), e o
terceiro campo ser a **abreviatura** — este só apareceu num clube de Master
League, porque para uma seleção os dois caminhos dão a mesma cadeia. **Testar
uma família só de time não teria pego**, e é o argumento para o terceiro caso
ser de outra família, não o terceiro índice qualquer.

**A conferência tem três pontas, e a terceira é a que importa.** Comparar o
port com o oráculo mostra que os dois desenham o mesmo pixel — e isso passaria
igual se **ambos** estivessem lendo o time errado. O `compara_tela.py --dump`
inverte a largura da barra (`11*v + 9`) e a confronta com o que o `we2002_core`
carregou. Vale como regra: *"os dois lados concordam"* nunca é conferência
completa; falta amarrar num terceiro que não é nenhum dos dois.

**E o método da §4.2 pagou três vezes nesta task.** As barras caem na
`OFS_TEAM_BARS`; a fronteira de setor de `0x00403388` é a mesma geometria dos
`OFS_*`; a tabela que `0x0040cbc8` varre é a que a WTE-TASK-06 registrou. Com
isso, `0x00404374` (881 B) e `0x00403f00` (328 B) **nunca precisaram ser
lidos** — o original calcula endereços de bytes cujo lugar já se conhecia por
outro caminho.

**WTE-TASK-26 — o símbolo que "nunca é chamado" era virtual, e a busca é que
estava errada.** A WTE-TASK-25 fechou registrando como dívida sem dono: a
`.text` inteira tem **zero** `call rel32` para `TControl::SetEnabled`, e por
isso a seção Saída da spec do `lista_equiposChange` não podia dizer
`disassembly lido`. O original chama `call DWORD PTR [reg+0x64]` depois de
carregar o VMT — três vezes dentro daquele mesmo handler. **Chamada virtual não
deixa `call rel32`.** O slot é medido, não afirmado: o valor exportado de
`SetEnabled` aparece a `0x64` bytes do início do VMT em **108 classes** do
`vcl60.bpl`, com o nome de cada uma lido de `[vmt - 0x2c]`, e a conferência
roda a cada `make -C wte check`. Vale como aviso geral: *"o símbolo não é
chamado"* é afirmação sobre a **forma** da chamada procurada, não sobre o
programa.

**E existe um buffer de edição, que não é cache.** As cinco barras de força não
vão da imagem para a tela: vão para `0x00434592`, e é dali que sai a largura. A
carga enche, o `track_barraChange` grava, o `boton_barras2isoClick` lê para
gravar na imagem — os três tocam o mesmo endereço, conferido por
[`check_barras.py`](../../wte/tools/check_barras.py). Se o port desenhasse a
barra a partir de `Jogo.teams[].bar_*`, editar mudaria o pixel e a gravação
escreveria o valor velho, **com o golden acusando a gravação** por um defeito da
edição. É a forma que todo grupo de edição da fase 4 deve ter, e vale procurar
o buffer antes de escrever o corpo.

**E o teclado chega ao port — a recusa do gate estava apoiada em medição
superada.** O `golden_run_laz.sh` reprovava roteiro com `! tecla`/`! texto`
desde a WTE-TASK-22, citando a WTE-TASK-13; aquela medição valia para `xdotool
key` **sem foco** e para `key --window` (que usa `XSendEvent`), e não para
`xdotool windowfocus` — `XSetInputFocus`, que dispensa gerenciador de janela. O
`compara_tela.sh` da WTE-TASK-25 já trocava de time com `Down` por esse
caminho: **a contradição estava na árvore havia uma semana**, em dois arquivos
que ninguém tinha lido juntos. Remedido pelo próprio harness — 3 `! tecla Down`
dão 3 disparos de `lista_equiposChange` no trace do port —, e o foco ficou
atrás de `ROTEIRO_FOCO`, ligado só no lado port para não invalidar o controle.
Sem isso, metade da WTE-TASK-26 não teria gate nenhum.

**WTE-TASK-26 — decisão do usuário, 2026-08-12: a 26 fecha por pixel, a 27
herda o byte.** O critério da 26 pedia "editar pela tela nos dois lados, então
gravar nos dois, e o golden compara", e o segundo verbo é da
[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), que `depends_on` a 26 —
a mesma forma de circularidade que a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para o gate e que a decisão
de 2026-08-11 desfez para o critério de tela da 25. **A metade excluída virou
critério de conclusão da 27**, com o par gravação × edição escrito; exclusão
sem dono nomeado é buraco, e este projeto já pagou por isso.

A decisão alcançou o **vocabulário de veredito**, e tinha de alcançar:
`implementado` dizia "golden verde", o que tornaria impossível fechar qualquer
handler de edição — o veredito mediria a ordem das tasks, não o estado do
handler. Passou a dizer "a régua da task do handler verde", com a tabela por
grupo no [`GABARITO.md`](../../wte/re/spec/GABARITO.md).

**E a régua existe e fechou verde:** `compara_tela.sh --edicao` edita a barra
`defesa` do time 2 nos dois lados e mede — 4 → 6 nos dois, com as outras quatro
ainda ancoradas no `we2002_core`, o que mostra que a edição não respingou. Duas
lições de ferramenta saíram junto: **`Position :=` dispara `OnChange` na LCL**
(oposto do `TComboBox`, que o `check_lcl_combo.py` mediu), e **coordenada de
clique não é comum aos dois lados no rodapé do formulário** — o gtk2 desenha
6 px de borda que o Wine não desenha, e a diferença cresce descendo a janela.
