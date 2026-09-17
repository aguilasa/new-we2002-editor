---
id: LOOKS-TASK-24
title: "Incógnita (j) — de onde vem a pose: `ANIME.BIN`, código ou outra tabela"
type: investigação
category: oráculo
phase: 9
depends_on: ["LOOKS-TASK-20"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (j)"
status: concluído
---

# LOOKS-TASK-24: De onde vem a pose

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.2 e §10.3 (j), e §6 (e).
- **É a task de maior risco da v2, e abre a Fase 9 pelo mesmo motivo que a
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) veio antes da Fase 3:** um leitor de formato escrito para o arquivo
  errado lê perfeitamente e desenha outra coisa. Que a caminhada sai do
  `ANIME.BIN` é hipótese **pelo nome do arquivo**, e nada mais.
- **O `ANIME.BIN` é cru** — 396.804 B, form1, sem LZSS, cabeçalho de 204
  palavras de ponteiro KSEG0 (§10.2) —, então, se estiver em RAM, está byte a
  byte, como os dois arquivos de modelo estavam (§1.3).
- **Onde a matriz entra.** Na PSX a pose de uma peça chega ao GTE como matriz
  de rotação 3×3 em ponto fixo 4.12 e um vetor de translação, carregados antes
  de os vértices daquela peça serem transformados. Um breakpoint nessa carga,
  com a peça identificada pela primitiva que vem a seguir, diz **de onde os
  números saíram** — a técnica do `layout.HAIR_QUAD_STORE` da [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md), um nível
  acima.
- **Toda medição começa em `load_state`**, nos dois slots. O boneco anima:
  diff de memória sem baseline mede a animação inteira.

---

## Objetivo

Dizer, com evidência, **de onde vêm as matrizes que posicionam cada peça** na
tela `LOOKS SET`, e se o `ANIME.BIN` está entre as fontes — antes de qualquer
leitor de pose existir.

---

## Critério de conclusão

- [x] O `ANIME.BIN` está em RAM nessa tela, **por conteúdo**: o arquivo
      inteiro — 396.804 de 396.804 bytes — contra a memória, nos dois slots,
      com a base e o digest no `layout.py`. **A base não veio do
      `layout.derive_base()`**, que erra este arquivo por 96 bytes; veio de uma
      corrida de 64 bytes que aparece uma vez só na RAM, e a razão de a regra
      falhar está escrita no `ANIME_BASE`.
      *(O critério dizia "no endereço que o cabeçalho deriva
      (`layout.derive_base()`)". Derivar não funcionou, e por que não
      funcionou virou parte do resultado.)*
- [x] Onde o GTE recebe a matriz: **duas** instruções carregam quase tudo, de
      30 candidatas e 5 que rodam na tela. **Quais peças** passam por elas é o
      que fica para a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md), com a linha escrita lá: a contagem de
      paradas antes de a sequência repetir **varia entre corridas**, então não
      é contagem de quadro.
- [x] **De onde os números saem**, por watchpoint de leitura: entrada 5 do
      cabeçalho → lista de quadros → quadro corrente → quatro instruções que o
      leem → ângulos **empacotados** desempacotados para o scratchpad. Os nove
      números da matriz não estão no arquivo. O veredito tem o **controle do
      instrumento** ao lado: um watchpoint de leitura sobre um objeto de texto
      que a rotina de impressão recebe dispara nesta build.
- [x] Nos dois slots, e não difere nada: mesma base, mesma entrada 5, mesmas
      instruções, mesmos ponteiros de lista e de quadro.
- [x] `oracle.py --pose [SLOT]` reproduz, com 77 sem as variáveis e os states,
      e está na tabela de gates do perfil.
- [x] §10.3 (j) do plano com o veredito e a data, e a §6 (e) corrigida no
      lugar.

---

## Log de Execução

**Executado em:** 2026-09-17

### O que se aprendeu

**A pose vem do `ANIME.BIN`, e a cadeia inteira está medida.** O arquivo está na
RAM **byte a byte** (396.804 de 396.804, nos dois slots) em `0x8017EE00`; o
cabeçalho é de 204 entradas, uma por animação, e a tela toca a **entrada 5** —
nenhuma outra é lida; a entrada aponta uma **lista de quadros**, e o estado em
`layout.ANIME_STATE` guarda a lista, o quadro corrente e um índice que anda a
cada quadro e **volta a zero** no fim da lista, que é a passada se repetindo;
quatro instruções leem o quadro, e o código ao redor **desempacota ângulos** de
uma palavra para o scratchpad; a matriz chega ao GTE em duas instruções, de 30
candidatas e cinco que rodam.

**Os nove números não estão no arquivo.** O que está são ângulos empacotados —
o que explica o candidato "matrizes calculadas em código" da §10.3 (j) sem que
ele seja a fonte. Um leitor do `ANIME.BIN` que esperasse encontrar matrizes
prontas leria lixo com ar de dado.

**A base não se deriva, se mede.** O `layout.derive_base()` — a regra dos dois
arquivos de modelo — erra este arquivo por 96 bytes, por duas razões
independentes: ele reconhece a corrida de ponteiros por "bit alto" e o payload
abre com `0x9000040A`; e supõe que o ponteiro mais baixo mira logo depois da
corrida, quando aqui ele mira o offset 912 e não o 816. Contra a base derivada,
**279.034 bytes diferem** — que é justamente o controle vermelho do comando.

### Gates, na árvore de `0b2d087`

Tirados **depois** do commit da task, que é a regra do perfil.

```text
# na arvore de 0b2d087
$ python tools/looks/selftest.py
  ..... 75 of 75 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 6 of 6 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --pose          # os dois slots, identicos
  /BIN/ANIME.BIN at 0x8017ee00: 396804 of 396804 byte(s) equal
    control: the text object at 0x800C7B00 is read, so a read watchpoint
    fires on this build
    header entry 5 (0x8017EE14) read 3 time(s), by 0x800270B8
    the state at 0x80076040 plays list 0x801947F4, frame 0x80194194
    the frame is read by 0x80011E80, 0x80011E94, 0x80011EB0, 0x80011ECC
    30 instruction(s) write the GTE's first matrix word; 5 run on this
    screen: 0x80012168 x18, 0x8001229C x18, 0x8003C990 x2, 0x80010E38 x1,
    0x800407C0 x1
oracle --pose: 0 problem(s)
```

**O vermelho, na cópia da árvore com a base que o `derive_base()` calcula**
(`ANIME_BASE = 0x8017EE60`):

```text
$ python <copia>/tools/looks/oracle.py --pose 2
  /BIN/ANIME.BIN at 0x8017ee60: 117770 of 396804 byte(s) equal
  FAIL  slot 2: 279034 of 396804 bytes of /BIN/ANIME.BIN differ at 0x8017ee60
  FAIL  slot 2: none of the 204 header entries of /BIN/ANIME.BIN was read
oracle --pose: 2 problem(s)
```

### Arquivos criados/modificados

Conferidos contra `git show --stat --format= HEAD`:

- `tools/looks/layout.py` — `ANIME` (caminho, digest, LBA, tamanho),
  `ANIMATION_FILES`, `ANIME_BASE` com a razão de o `derive_base()` falhar,
  `ANIME_STATE` e seus três offsets, `ANIME_HEADER_WORDS`, `POSE_MATRIX` e
  `POSE_MATRIX_SECOND`.
- `tools/looks/oracle.py` — `--pose`: o arquivo contra a RAM, o controle do
  watchpoint, as 204 entradas armadas de uma vez, a cadeia até o quadro, a
  varredura de `ctc2` e as instruções que rodam; mais os casos de self-check
  da varredura.
- `tools/looks/controls.py` — dois controles plantados novos
  (`oracle-matrix-scan-takes-any-ctc2`,
  `oracle-matrix-scan-skips-the-last-word`).
- `docs/PLAN-LOOKS-PY.md` — §10.3 (j) com o veredito datado, e a §6 (e)
  corrigida no lugar.
- `docs/prompts/perfil-looks.md` — armadilhas 42, 43 e 44, e a linha do
  `--pose` na tabela de gates.
- `docs/tasks/looks/25-a-pose-de-referencia.md` e
  `docs/tasks/looks/26-o-formato-do-anime-bin.md` — o que esta task deixou
  para cada uma, escrito **na task de destino**.
- `docs/tasks/looks/progresso.md` e este arquivo.

### Problemas encontrados

1. **Quatro endereços de um arquivo de 400 KB são silêncio, não resposta.** A
   primeira sonda vigiou quatro pontos do `ANIME.BIN`, não viu leitura nenhuma
   em 8 s cada, e a conclusão pronta era "a pose não vem daí". A entrada que o
   jogo lê é a **sexta palavra** do cabeçalho: armando as 204 de uma vez, ela
   aparece na primeira corrida. Virou a armadilha 42 do perfil, junto com a
   regra que a segura: **controle do instrumento antes** — um watchpoint de
   leitura sobre um objeto que a rotina de impressão recebe dispara, e é ele
   que dá direito de ler silêncio como resposta.
2. **Um `continue` nomeia a primeira instrução que dispara, não as que
   disparam.** As mesmas 30 armadas deram `0x80012168` numa corrida e
   `0x80010E38` na seguinte — as duas verdadeiras, nenhuma sendo a pergunta.
   Soltando o emulador dezenas de vezes e lendo o `hit_count`, são **cinco**
   que rodam, duas delas com quase toda a carga. Armadilha 43.
3. **O self-check achou um defeito meu na varredura.** O laço parava uma
   palavra antes do fim (`len(ram) - 4`), o que é invisível em dois megabytes e
   **total** num caso de quatro bytes — que foi o que o teste passou para ele.
   Vale como controle plantado desde então.
4. **`derive_base()` não generaliza**, e isso não é defeito dele: é a regra
   medida de dois arquivos, aplicada a um terceiro. Armadilha 44.
