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

### Gates, na árvore de `SHA_DA_TASK`

*(transcritos abaixo, depois do commit)*

### Arquivos criados/modificados

*(conferidos contra `git show --stat --format= HEAD`)*

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
