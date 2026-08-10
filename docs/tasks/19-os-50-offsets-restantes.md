---
id: WTE-TASK-19
title: "Descobrir os offsets que o Obocaman tem e nós não"
type: extração
category: dados
phase: 3
depends_on: ["WTE-TASK-06", "WTE-TASK-18"]
status: em andamento
---

# WTE-TASK-19: Os offsets restantes

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.2 e Fase 3 item 4.
- **Onde o método do projeto se prova.** A §4.2 diz: *sempre tentar o diff antes
  do decompilador*. Esta task é a aplicação pura disso — cada offset custa dois
  minutos de tela, contra horas de disassembly.

O `wte.exe` edita coisa que o `ed.exe` não edita: camisa 2D, bandeira, dados que
vêm de `.mcr`. Os offsets dessas regiões, se existirem, **não estão em
`Offsets.hpp`** — este repositório nunca precisou deles.

---

## Objetivo

Fechar a lista de regiões que o app Lazarus precisa endereçar.

### Método: diff dirigido

Para cada campo editável do original que a WTE-TASK-06 não resolveu:

1. Cópia limpa da ROM (**sempre cópia** — o editor grava in-place, e são 474 MB).
2. Abrir no Wine, mudar **um** campo, gravar, fechar.
3. `cmp` contra a cópia limpa.
4. O offset que mudou é o offset do campo.

### Cuidado que evita falso positivo

O `Load`+`Save` do original **não é idempotente**: ele troca os dois primeiros
cobradores de cada clube de ML (`OFS_KICKER`), porque `Load` lê o par trocado e
`Save` grava na ordem declarada. E o `Save` reconstrói as all-star a partir dos
links.

**Então o diff de controle vem primeiro:** abrir e gravar **sem editar nada**, e
registrar as faixas que mudam de graça. Só o que aparecer *além* dessas faixas é
efeito da edição.

Sem esse controle, toda medição vem contaminada e parece que campos aleatórios
se movem.

### Campos a cobrir

| Área | Origem |
|---|---|
| os 50 `OFS_*` não confirmados | WTE-TASK-06 |
| cor de camisa (casa/fora, menu) | `ficha_color`, `grabar_camisetaClick` |
| bandeira e cor de radar | `colorearClick`, novidade da v0.99 |
| aparência (cabelo, barba, `careto`) | WTE-TASK-08 |
| preço do jogador | `etiqprecioClick` |
| slots de ML livres | `ficha_movertodos` |

### Saída

Os offsets confirmados entram na **entrada do gerador** (WTE-TASK-16), nunca no
arquivo gerado.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/diff_dirigido.sh` | criar — automatiza copiar, editar, gravar, `cmp` |
| `wte/re/offsets.md` | modificar |
| `wte/re/offsets-novos.md` | criar — os que o `newWe2002` não tem |

---

## Critério de conclusão

- [x] Diff de controle (gravar sem editar) medido e registrado **antes** do resto
- [ ] Os 50 resolvidos ou declarados irrelevantes, um a um
      — **14 dos 50** resolvidos por execução; os 36 restantes esperam a
      release de 474.431.328 bytes (ver o Log)
- [ ] As seis áreas da tabela cobertas
      — **nenhuma.** O `wte.exe` cai ao carregar um time com as ROMs deste
      repositório, e os botões de gravação por área não escrevem byte nenhum
      sem time selecionado. As duas coisas medidas
- [x] Offsets novos documentados com a região que endereçam
- [x] Nenhuma medição feita sobre `roms/` diretamente
- [x] Commit no formato conventional, em inglês

**A task não fecha.** Dois dos seis critérios dependem de dirigir o `wte.exe`
além da tela de carga, e isso está bloqueado por falta da imagem certa.

## Log de Execução

- **Executado em:** 2026-08-10 — **parcial, e o bloqueio é externo**
  (retomada no mesmo dia: a hipótese do tamanho foi testada e refutada, e o
  instrumento ganhou dois consertos que mudavam número)

- **Resumo do que foi feito:**

  A régua trocou, e essa é a decisão da execução. O enunciado pede `cmp` depois
  de editar um campo; `cmp` só enxerga **escrita de valor diferente**, e o
  editor do Obocaman grava, na maior parte das áreas, exatamente o que leu —
  ali um `cmp` limpo não distingue *não gravou* de *gravou igual*. Pior: `cmp`
  não vê **leitura** nenhuma, que é a metade da resposta que diz onde os 50
  `OFS_*` ausentes moram. Então o `wte.exe` passou a rodar sob `strace`, e cada
  `_llseek` + `read`/`write` virou uma faixa `(offset, tamanho)`. O `cmp`
  continua, como segunda régua independente.

  **O diff de controle veio primeiro, e ele é maior do que a task supunha.**
  Abrir a imagem, sem tocar em nada, já grava **14.337 bytes em 8 faixas** —
  sete setores inteiros (5 a 11, byte 24 ao 2071) mais um byte solto em
  1.921.862. Não é o `Load`+`Save` não idempotente do `ed.exe`: aqui não há
  `Save` nenhum, o `wte.exe` escreve **durante a carga**, antes de a janela
  principal aparecer. As duas réguas concordam byte a byte: as sete faixas do
  `cmp` estão contidas nas oito do trace.

  Resultado: **28 `OFS_*` confirmados por execução**, dos quais **14 eram
  `ausente`** na classificação estática da WTE-TASK-06 — inclusive dois `H3`,
  a classe que a WTE-TASK-06 marcou como "sem base derivável"
  (`OFS_KIT_PREVIEW` e `OFS_FLAG_COLOURS`). E **13 faixas que nenhum `OFS_*`
  explica**, três delas casando com candidatos que a WTE-TASK-06 extraiu do
  `.text` (`2736694`, `1921862`, `12544268`), e uma em **14.368.636** — 1,8 MB
  **acima** do maior offset que o `newWe2002` conhece.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/diff_dirigido.sh` | criado — copia a ROM, dirige o `wte.exe` sob `strace` por roteiro, `cmp` contra a cópia limpa |
  | `wte/tools/analisar_io.py` | criado — trace → faixas, e faixas → `offsets-novos.md` |
  | `wte/tools/test_analisar_io.py` | criado — 15 testes, parser com linha plantada |
  | `wte/tests/roteiros/06-diff-dirigido.txt` | criado |
  | `wte/re/io-medido.tsv` | criado — a evidência |
  | `wte/re/offsets-novos.md` | criado, **gerado** |
  | `wte/re/offsets.md`, `wte/tools/dump_offsets.py` | coluna **medido** na tabela dos 50 |
  | `wte/re/io-conteudo.tsv` | criado — amostra do conteúdo de cada faixa lida |
  | `wte/tools/README.md`, `wte/tests/roteiros/README.md` | atualizados |

- **Problemas encontrados:**

  **O bloqueio, e ele não é desta task só: o `wte.exe` morre ao carregar um
  time.** `SIGSEGV`/`SEGV_MAPERR` em `NULL`, logo depois de ler os dados do
  primeiro time selecionado, com as duas ROMs deste repositório — e com
  qualquer time, não só o primeiro.

  **A primeira hipótese estava errada, e a correção é o achado da retomada.**
  O editor avisa na abertura que o tamanho não corresponde — quer 474.431.328
  bytes exatos, e a European Deluxe tem 474.784.128. A diferença é
  **352.800 = exatamente 150 setores** de 2352, toda ela na cauda, muito depois
  do maior offset conhecido. Truncar a cópia para o tamanho exato e repetir o
  roteiro: **o aviso some, e mais nada muda** — o mapa de I/O sai idêntico
  faixa a faixa, e o app cai no mesmo ponto. Tamanho não era a causa; o que a
  hipótese explicava era o aviso, e o aviso nunca foi o problema.

  O que sobra como pista é **conteúdo**: a última leitura antes do `SIGSEGV`
  são 512 bytes em `14368636`, e amostrando 64 bytes ali esta release tem
  **4 não-zero** — contra 32 a 64 em toda outra faixa que o editor lê. Não
  prova a causa; prova que nesta release **não há o que ler** onde ele foi ler.
  O pedido deixou de ser "a release de 474.431.328 bytes" e passou a ser
  "uma release cuja região em 14368636 seja populada".

  O custo maior não é aqui. O `wte.exe` é o **oráculo comportamental** do
  projeto (§4.2 do plano), e a WTE-TASK-22 monta o gate golden em cima dele.
  Um oráculo que não passa da tela de carga não sustenta gate nenhum. Ficou
  registrado nas Pendências externas do `progresso.md`.

  **Dois defeitos do próprio instrumento, que mudavam número em silêncio.** Os
  dois só apareceram porque a segunda régua passou a ser conferida de verdade
  (`analisar_io.py --conferir`), e o script prometia essa conferência desde o
  primeiro commit sem executá-la:

  1. **a marca era número de linha**, e o `strace` bufferiza o log — `wc -l` no
     instante da marca fica atrás das syscalls que já aconteceram, e a faixa ia
     para a ação errada. Virou relógio (`strace -tt`);
  2. **o parser ignorava syscall partida** em `<unfinished ...>` +
     `<... resumed>`, que sobre a imagem é a **maioria** delas — 1.529 numa
     sessão só. Duas faixas mudavam no arquivo sem aparecer no trace.

  Com os dois consertados, as duas réguas fecham: as 7 faixas do `cmp` cabem
  nas 8 faixas de escrita do trace, nas duas sessões.

  **Três diagnósticos custaram tempo e viraram nota escrita**, porque os três
  se disfarçam de "o clique parou de funcionar":

  1. a janela **sobrevive** ao processo — o `wineserver` a mantém mapeada —,
     então a tela continua parecendo viva depois do `SIGSEGV`. Confira
     `ps -o stat` procurando `Z`;
  2. a lista suspensa de um `TComboBox` fica **mapeada** depois do clique no
     item e segura o ponteiro; todo clique seguinte morre nela, mesmo num botão
     do outro lado da janela. Trocar de item pelo teclado (`Down`) evita;
  3. um terceiro método tentado — encher a cópia com `0xA5` depois do Load e
     ver o que sobrevive à gravação — **derruba o app**: ele não lê tudo no
     Load, lê sob demanda. Está registrado no `offsets-novos.md` para que
     ninguém repita.

  **Medida negativa que também é resultado:** os botões de gravação por área
  (`boton_barras2iso`, `boton_nombres2iso`, `colorear`, `grabar_camiseta`,
  `grabar_memory`) não escrevem byte nenhum enquanto não houver time
  selecionado. Isso não é "o clique não chegou": o mesmo roteiro reabre o
  splash `Sobre...` por clique, com a janela mapeando.

  **O que ficou pendente**, e volta quando houver a imagem certa: as seis áreas
  da tabela, os 36 `OFS_*` restantes, e o diff dirigido *stricto sensu* —
  editar um campo e gravar. A ferramenta e o roteiro já estão prontos para
  isso; falta o oráculo funcionar.
