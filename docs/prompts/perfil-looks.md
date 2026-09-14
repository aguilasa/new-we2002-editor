# Perfil de ciclo — visualizador 3D da aparência do jogador

**Este arquivo é o perfil do ciclo `looks`**, nomeado pelo campo `perfil:` do
[`docs/tasks/looks/progresso.md`](/docs/tasks/looks/progresso.md) e carregado
pelos prompts de `docs/prompts/`. Os prompts têm o **rito**; o que é deste ciclo
mora aqui.

Fonte: [`PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md). Onde este perfil e o plano
divergirem, **o plano ganha** — aqui só mora o resumo operacional, e o
`fonte_de_verdade` de cada task aponta para a seção que a mede.

**Este ciclo mora numa subpasta.** Os comandos o recebem por argumento:
`/executar looks`, `/revisar looks`, `/corrigir looks`. Sem argumento, os
comandos continuam no `docs/tasks/` raso, que é o ciclo de PES2. A regra está no
"Passo 0" de cada prompt.

---

## Contexto essencial — decisões já confirmadas

Não se revertem sem o usuário pedir.

- **v1 é só visualizador.** Não grava na imagem, não grava no cartão. Decisão do
  dono do repositório em 2026-09-13.
- **Dois discos, com papéis separados** (§1.3 do plano). `roms/japanese-shift-jis.bin`
  é a fonte de verdade dos **bytes**; o `.cue` inglês em
  `C:\games\ps1\work\we2002-english.cue` é o de **dirigir o emulador**, porque
  tem os menus legíveis. A divisão é legítima porque `EDT_MOD.BIN` e
  `MODEL.BIN` são byte a byte idênticos nos dois.
- **`roms/japanese-shift-jis.bin` e `we-2002-original-japao.bin` são o mesmo
  dump** — `sha256 e853eb14f5bddd50…`. Nomes diferentes, arquivo igual.
- **Render por `QOpenGLWidget`**, não Qt3D e não rasterizador em Python.
  `numpy` não está instalado e instalar é decisão do dono da máquina.
- **Não estende o `we2002_core`.** Nada em `src/` aprende o que é modelo 3D.
- **Nada do Superpack entra no git** — nem arquivo, nem transcrição longa.
- **O `we3d` é MIT** e entra com crédito; o fonte `en_we2000edit` é testemunha,
  não código a copiar.

---

## Armadilhas medidas neste ciclo

1. **Ler textura do disco inglês é erro silencioso.** O `DAT2D.BIN` difere entre
   as duas imagens; o offset existe nos dois e entrega gráfico diferente, sem
   nenhuma mensagem. É a razão de a LOOKS-TASK-02 plantar uma guarda por digest
   em vez de confiar em disciplina.
2. **A varredura contígua morre na seção 55 do `MODEL.BIN`.** Parece formato
   errado e é o par de zeros que separa grupos (§1.4). Foi o primeiro tropeço da
   sessão de investigação.
3. **O `EDT_MOD.BIN` não é contíguo.** Varrer do começo sem a lista de ponteiros
   pega uma seção e para.
4. **A ordem da lista não é a ordem do arquivo.** O registro do offset 24.136 vem
   antes do 22.984. Assumir a do arquivo embaralha peça sem sintoma visível.
5. **`bin_archive.py` responde `0 clut(s)` sem reclamar.** A lista de paletas do
   `DAT2D.BIN` existe e o varredor não a acha. Ler isso como "não tem paleta" é
   erro.
6. **`MSYS_NO_PATHCONV=1`** em toda chamada do Git Bash que passe caminho de
   dentro do ISO. Sem ele `/BIN/EDT_MOD.BIN` vira `C:/Program Files/Git/BIN/…` e
   a mensagem de erro acusa "not a Form 1", que culpa a coisa errada.
7. **Círculo confirma, e precisa de pelo menos 8 frames.** Com 3 o jogo não
   registra: a tela fica igual e parece botão errado. Cruz abre `Exit?` com
   `CANCEL` já selecionado.
8. **Uma tecla de cada vez.** Confirmação em laço fecha a caixa seguinte junto —
   regra do [CLAUDE.md](../../CLAUDE.md), que custou uma corrida no ciclo `wte/`.
9. **Os documentos da cena se contradizem.** O CARP rotula o offset 8 do
   `DAT2D.BIN` como "Pelos" e o 3.568 como "Caras"; o tutorial do `zeta` manda
   abrir o 3.568 para achar cabelo. Até a LOOKS-TASK-11 medir, **nenhum código
   crava nenhum dos dois**.

---

## As fontes de verdade binárias

| o que | onde | quem é fiel |
| --- | --- | --- |
| geometria | `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` | igual nos dois discos |
| textura e paleta | `/BIN/DAT2D.BIN` | **só o japonês** |
| registros de jogador | `/SELECT.BIN` +157.164, 1.242 × 12 B | japonês (a conferir na 13) |
| corpus de render | 50 JPGs do Superpack | terceiro, fora do git |

Leitura pura em todas. **Nenhuma task deste ciclo escreve em imagem de CD** —
se alguma precisar, o escopo mudou e isso é conversa com o usuário, não decisão
de execução.

---

## Estrutura

```text
tools/looks/        núcleo Python puro — ZERO Qt, ZERO endereço fora de layout.py
tools/looks/ui/     PySide6 — ZERO endereço, ZERO leitura de disco
work/venv-looks/    fora do git
docs/tasks/looks/   este ciclo
```

As três regras de desenho (§3.3 do plano) são varridas mecanicamente pelo
`selftest.py`, e a varredura usa `os.walk` — `os.listdir` não enxerga `ui/`, e
foi assim que o ciclo do `.mcr` deixou uma pasta inteira fora da regra.

---

## Gates deste ciclo

| alvo | precisa | a partir de |
| --- | --- | --- |
| `looks_selftest` | nada — **nunca pula** | LOOKS-TASK-06 |
| `looks_image` | `WE2002_LOOKS_IMAGE` (77 sem ela) | LOOKS-TASK-05 |
| `looks_ui` | venv + display (77 sem eles) | LOOKS-TASK-16 |

Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped**.

**Antes da LOOKS-TASK-06 não há gate**, e isso é esperado: as tasks 01 a 05 se
verificam pela saída da ferramenta, copiada para o Log. Depois dela, toda task
fecha com o `selftest` verde.

**E nenhum alvo pode passar sem ter medido.** Alvo que passa imprimindo um
`note:` sobre o que não mediu é a armadilha que o `mcr_ui` pagou; aqui o
contrato é: mediu e passou, ou pulou com 77.

---

## Arquivos quentes deste ciclo

- `tools/looks/layout.py` — todo endereço passa por aqui. Duas tasks editando
  este arquivo ao mesmo tempo se atropelam.
- `tools/pes2/bin_archive.py` — **arquivo de outro projeto**. A LOOKS-TASK-10
  pode precisar mexer nele; se mexer, o `pes2_selftest` tem de continuar verde,
  e isso entra no critério de conclusão, não na esperança.
- `tests/CMakeLists.txt` — os três alvos entram aqui, junto com os dos outros
  quatro projetos.
- `NOTICE.md` — tocado pela 01 e reconferido pela 20.
- `docs/PLAN-LOOKS-PY.md` — **o plano se corrige na seção que muda**, nunca num
  apêndice de erratas.

---

## Recursos serializados

- **O emulador é um só.** DuckStation usa um único diretório de dados, então
  roda **uma instância por vez**. Task que precisa do emulador não corre em
  paralelo com outra que precisa.
- **A tela do usuário.** Nada abre janela visível: `:98` no Linux, janela em
  −32000 no Windows.

---

## Antecipação

**A LOOKS-TASK-13 pode ser antecipada** assim que a 09 fechar, e provavelmente
deve: ela depende só da 09, é a task mais barata do ciclo — transcrição
conferida contra quatro implementações que já concordam — e tanto o `--looks` da
UI quanto o parser de tupla do corpus dependem dela. É o padrão que o
`01-executar.md` já autoriza: tarefa de fase adiante de que uma tarefa da fase
corrente precisa.

**O que não se antecipa:** nada que dependa da LOOKS-TASK-08. Enquanto a
incógnita (a) estiver aberta, escrever montagem ou caçar paleta é trabalhar
sobre dado que pode não ser o que a tela desenha.

---

## Verificações específicas por fase

- **Fase 0** — o `NOTICE.md` distingue os **três** materiais de terceiro e as
  três situações legais, sem fundir as duas que não têm licença com a que tem.
  O venv existe e o `pip freeze` dele vai para o Log. E a pergunta que decide a
  fase: **a guarda dos dois discos existe como código, com caso vermelho?** Uma
  regra que só vive na prosa não impede ninguém de ler paleta no disco errado,
  e esse erro não tem sintoma.
- **Fase 1** — todo módulo novo traz `self_check()` com **caso vermelho**;
  nenhum endereço fora de `layout.py`, conferido por varredura e não por
  leitura; e nada em português no código (§3.5). As contagens são **asserção**,
  não comentário: `MODEL.BIN` 106/2.461/1.767 terminando em 64.800, e
  `EDT_MOD.BIN` 11/690/611 terminando em 36.072. **Uma varredura que não chega
  ao EOF não é "quase certa", é errada** — foi exatamente assim que o formato
  revelou o separador de zeros. E o controle negativo do tamanho de primitiva
  (24 → 20) tem de ficar vermelho; se ficar verde, a varredura não está
  medindo o que diz medir.
- **Fase 2** — a rota chega à tela **sozinha**, e o Log traz a captura. A
  incógnita (a) tem veredito **com a evidência ao lado**, não com uma
  conclusão. Pergunta obrigatória da revisão: **o veredito distingue "medi e é
  isto" de "não achei o contrário"?** Os quatro TMDs de `0x00168xxx` não
  pertencem a nenhum dos dois arquivos, e "o boneco deve vir do `EDT_MOD.BIN`"
  sem medição é a hipótese confortável, não a medida. Para a 09, cada peça
  nomeada traz **como se soube** — trocar a opção e ver o que muda, nunca
  deduzir do número de vértices.
- **Fase 3** — toda leitura de textura sai do **disco japonês**, e a revisão
  confere isso explicitamente em cada comando do Log. A lista de CLUTs é achada
  **por marcador**, não por offset constante — é a regra que o
  `bin_archive.entries()` já segue e a razão de o mapa de PES2 nunca ancorar em
  constante. A contradição 8 × 3.568 tem veredito com o documento errado
  nomeado. E se o conserto tocou `tools/pes2/bin_archive.py`, o `pes2_selftest`
  verde aparece no Log.
- **Fase 4** — os domínios conferidos **campo a campo** contra
  `src/core/Player.cpp`, com o cross-check dentro do `self_check()` e não só na
  prosa da task. Para a 14, a pergunta que decide: **cada linha da tabela de
  montagem diz de onde veio?** Tabela derivada de medição e tabela plausível
  são indistinguíveis depois de escritas, e a armadilha das oito listas de nome
  de time do PES2 é o precedente. Buraco nomeado vale mais que mapeamento
  inventado.
- **Fase 5** — captura de tela no Log, e **nenhuma janela apareceu para o
  usuário** (`:98` no Linux, −32000 no Windows). O gate julga o PNG, não a
  saída do processo: duas tuplas visivelmente diferentes têm de produzir
  imagens diferentes, senão o alvo passa desenhando sempre o mesmo boneco. E a
  regra 3 varrida: nenhum `import layout` em `ui/`, e `PySide6` fora de
  `sys.modules` depois de importar o núcleo.
- **Fase 6** — **três tuplas, não uma**, e a métrica nomeada. Cada fonte de
  diferença atribuída a pose, câmera, resolução ou filtro; o que sobrar sem
  explicação é achado e vira CORR. A §5.6 já avisa que a comparação **nunca**
  bate pixel a pixel — então a revisão pergunta o contrário do usual: **o
  número foi olhado, ou só registrado?** E os piores casos do corpus são
  examinados um a um, que é onde erro sistemático aparece.
- **Fase 7** — `ctest -R looks` com o número copiado da saída, e os alvos dos
  outros quatro projetos sem regressão. Cada incógnita da §6 com veredito
  escrito: respondida com a medição, ou aberta com a razão e o que a
  destravaria. Cada afirmação da §1 que a execução desmentiu **corrigida no
  lugar**, com a data e o que ela dizia antes — o plano não ganha apêndice de
  erratas. E o `check_tasks.py` verde.
