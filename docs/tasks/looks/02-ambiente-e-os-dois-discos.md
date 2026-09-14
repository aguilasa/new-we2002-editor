---
id: LOOKS-TASK-02
title: "Ambiente — o venv, os dois discos e seus papéis, e a armadilha do MSYS"
type: infraestrutura
category: ambiente
phase: 0
depends_on: ["LOOKS-TASK-01"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §4"
status: concluído
---

# LOOKS-TASK-02: O ambiente, e a divisão entre os dois discos

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4, e a
  §1.3, que é quem mede a divisão entre os discos.
- **Esta é a task que evita o erro silencioso do ciclo.** O disco inglês tem os
  menus legíveis e geometria byte a byte idêntica; o `DAT2D.BIN` dele
  **difere**. Ler paleta no disco errado entrega gráfico diferente sem erro
  nenhum.

---

## Objetivo

Deixar a máquina pronta e a regra dos dois discos gravada onde a ferramenta a
lê, não só onde a prosa a conta.

---

## Critério de conclusão

- [x] `work/venv-looks/` criado com PySide6, **nunca** por gerenciador de
      pacote do sistema — a armadilha do Python duplo está na §4.1.
- [x] `WE2002_LOOKS_IMAGE` nomeada e documentada, apontando para a **japonesa**
      (`roms/japanese-shift-jis.bin`).
- [x] `WE2002_LOOKS_DRIVE_IMAGE` (ou nome equivalente) nomeada para o `.cue`
      **inglês**, o de dirigir o emulador.
- [x] O `iso_source.py` (ou `layout.py`) **recusa** ler textura/paleta de uma
      imagem cujo `DAT2D.BIN` não bata com o digest da japonesa. A regra não
      pode existir só em prosa — é caso de controle negativo.
- [x] Fica registrado que `roms/japanese-shift-jis.bin` e
      `we-2002-original-japao.bin` são **o mesmo dump**
      (`sha256 e853eb14f5bddd50…`), e o comando que reconfere isso.
- [x] `MSYS_NO_PATHCONV=1` documentado em toda receita que passe caminho de
      dentro do ISO (§4.2).

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

A máquina ficou pronta e a regra dos dois discos virou **código com caso
vermelho**, que era o ponto da task: uma regra que só vive na prosa não impede
ninguém de ler paleta do disco errado, e esse erro não tem sintoma.

O que se aprendeu, em três pontos.

**1. A guarda certa é por digest de arquivo, não de imagem.** As duas coisas
parecem equivalentes e não são. Dois dumps da mesma release podem divergir na
cauda e trazer assets idênticos; um patch de tradução pode manter o tamanho do
disco e trocar exatamente um arquivo — que é o que acontece aqui. O
`tools/looks/layout.py` guarda o sha256 de cada um dos quatro arquivos **como
lido de dentro do disco**, medido em 2026-09-14:

```
/BIN/EDT_MOD.BIN     lba=5000   size=36072    IDENTICO
   japones 6ff56894e7ce94aa655047200143087afe85d70cda777e5aee30dedf9d427dd3
/BIN/MODEL.BIN       lba=8100   size=64800    IDENTICO
   japones 0b3814bb0d3b47f4ac3b13a1eb9f64ce9c50f8f08331790716827c618c0578cb
/BIN/DAT2D.BIN       lba=5300   size=81124    DIFERE
   japones 0e914e584c889635f0c3a7a64d87ed5c773541c76b35455b6475c19c9f50de7b
   ingles  4a4d6a4fe301b1169535c6e5acf7e31c584d725be1571e689ed6fb5696beef60
/SELECT.BIN          lba=850    size=300648   DIFERE
   japones 86d14a66a3cd72b9363832260d4f3842e15d530c2f76eb0d6a3f6823cd603ce1
   ingles  c9e1eaf89151b0c026dda80e490276ec510409423e774423ce7ac145071461b3
```

Os prefixos `6ff56894e7ce` e `0b3814bb0d3b` que a §1.3 do plano cita batem
exatamente, e os dois "difere" dela ganharam o digest do lado inglês — que a
§1.3 não tinha, e é justamente o valor que faz a guarda ser guarda.

**2. A guarda foi vista ficando vermelha contra os discos reais**, não só no
sintético. `python tools/looks/layout.py --check-discs <japonês> <inglês>`:

```
Japanese disc -- everything must be accepted
  accepted /BIN/EDT_MOD.BIN
  accepted /BIN/MODEL.BIN
  accepted /BIN/DAT2D.BIN
  accepted /SELECT.BIN
English disc -- geometry accepted, texture refused
  accepted /BIN/EDT_MOD.BIN     (wanted accepted) ok
  accepted /BIN/MODEL.BIN       (wanted accepted) ok
  refused  /BIN/DAT2D.BIN       (wanted refused) ok
  refused  /SELECT.BIN          (wanted refused) ok
layout --check-discs: ok
```

E a **mensagem** recebeu tanto cuidado quanto a recusa, porque o erro que ela
pega é "você abriu o disco inglês" e uma exceção que só diga *digest mismatch*
manda o leitor olhar o parser:

```
/BIN/DAT2D.BIN: read 4a4d6a4f… from we2002-english.bin, expected 0e914e58….
  /BIN/DAT2D.BIN differs between the Japanese original and the English
  translation patch, and textures and palettes may only be read from the
  Japanese one.  Point WE2002_LOOKS_IMAGE at it; WE2002_LOOKS_DRIVE_IMAGE is
  the disc you drive, not the disc you read.
```

O `--check` sintético tem **três** casos vermelhos e roda sem imagem, sem venv
e sem display: conteúdo estranho no `DAT2D.BIN`, caminho que ninguém mediu (que
é recusado em vez de passar por omissão), e geometria que não bate — esta com
texto próprio, porque ali a causa é um **terceiro** disco e não o inglês.

**3. Há uma saída melhor do que lembrar do `MSYS_NO_PATHCONV=1`.** A armadilha
foi reproduzida palavra por palavra, e está na §4.2 do plano com as duas
corridas lado a lado. Mas os caminhos de dentro do ISO deste projeto são
**quatro e fixos**, então viraram constante do `layout.py` e **não atravessam
shell nenhum** — o `--check-discs` recebe caminho de arquivo do host, e não de
dentro da imagem. A variável continua obrigatória para as ferramentas de
`tools/pes2/`, que recebem o caminho como argumento.

### O ambiente

`work/venv-looks/`, criado com o `python` do Windows (3.13.14) e **não** por
gerenciador de pacote:

```
PySide6==6.11.2
PySide6_Addons==6.11.2
PySide6_Essentials==6.11.2
shiboken6==6.11.2
```

`from PySide6.QtOpenGLWidgets import QOpenGLWidget` importa — conferido na
mesma corrida, e é o widget de que a Fase 5 depende. O venv cai em `work/`, que
o `.gitignore` já ignora inteiro (`git check-ignore` confirma na linha 48).

**O interpretador se chama por caminho, não por `activate`:** receita que
dependa de ativação não sobrevive a um agente que não guarda estado de shell
entre comandos.

### As duas variáveis

| variável | aponta para |
| --- | --- |
| `WE2002_LOOKS_IMAGE` | `roms/japanese-shift-jis.bin` — a trilha de dados japonesa |
| `WE2002_LOOKS_DRIVE_IMAGE` | o `.cue` inglês (`C:\games\ps1\work\we2002-english.cue`) |

São duas porque são dois arquivos, e o segundo é `.cue` e não `.bin`. É a mesma
razão de o PES2 ter `WE2002_PES2_*` e `PES2_*` — lá a receita passou um tempo
só com a primeira, e nesse tempo o único gate que punha o jogo na tela se
reportava *skipped* em 0,01 s enquanto a corrida imprimia `100% tests passed`.

O mesmo-dump da §1.3 foi reconferido: `roms/japanese-shift-jis.bin` e
`C:\games\ps1\roms\we2002\we-2002-original-japao.bin` dão o mesmo
`sha256 e853eb14f5bddd50a4a5e77a1da4d22c989a0d99ad5a4927e24e1dba7475abf3`,
307.187.664 bytes; o inglês tem 306.834.864 e
`f645367d4dc3945ea6b0c3851b8d41016dd98240a0ae866502148634e118fe82`. Os comandos
que reconferem estão na §1.3.

### Arquivos criados/modificados

- `tools/looks/layout.py` — **novo**. Os nomes das duas variáveis, os quatro
  caminhos de dentro do ISO, os quatro digests, `WrongDisc`, `require()`,
  `self_check()` com três casos vermelhos e o `--check-discs` vivo
- `docs/PLAN-LOOKS-PY.md` — §1.3 (os comandos que reconferem o dump), §3.2 (a
  linha do `layout.py`), §4.1 (a receita do venv e o `pip freeze`), §4.2 (a
  armadilha reproduzida e a saída por constante) e a **§4.5 nova**, que é onde
  as duas variáveis e a guarda passam a morar
- `docs/tasks/looks/03-fonte-de-disco-e-layout.md` — o encaminhamento: o
  `layout.py` já existe e se estende, e o `_check_discs()` é dívida dela
- `docs/tasks/looks/20-reconciliacao-e-entregaveis.md` — o encaminhamento do
  `CLAUDE.md`, que descreve cinco projetos e não menciona o sexto
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 0
- `docs/tasks/looks/02-ambiente-e-os-dois-discos.md` — este arquivo

`work/venv-looks/` **não** aparece no commit, e é isso que se espera dele.

### Problemas encontrados

Um de escopo, resolvido escrevendo em vez de decidindo sozinho.

**Onde plantar a guarda.** O critério desta task diz "`iso_source.py` (ou
`layout.py`)", e os dois são da **LOOKS-TASK-03**. Plantar a guarda exigia
abrir um dos dois uma fase antes. A escolha foi o `layout.py`, porque saber
qual disco é qual é conhecimento de *localização*, que é o que a regra 1 do
plano concentra ali — e porque o `iso_source.py` é fachada de leitura, que a 03
escreve inteira. O que isso deixou de dívida está escrito **na 03**, não só
aqui: ela estende o arquivo em vez de criá-lo, e move o `_check_discs()` para
trás do `iso_source.py`, deixando o `layout.py` sem I/O — que é o contrato dele.

E uma observação para a 03: a §3.2 do plano foi ajustada para dizer que o
`layout.py` também carrega a identidade dos discos. Lista de módulos que não
descreve o módulo envelhece em uma task.
