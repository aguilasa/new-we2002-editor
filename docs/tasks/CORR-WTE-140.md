---
id: CORR-WTE-140
title: "Correção: cancelar o diálogo de abertura encerra o port e deixa o `ed.exe` com a janela vazia"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-140: `return FALSE` no `OnInitDialog` não fecha diálogo nenhum

## Problema identificado

Cancelar o `IMAGE CD SELECTION` do arranque leva os dois lados a lugares
diferentes:

| | depois de cancelar e dispensar o aviso |
|---|---|
| `ed.exe` | **fica de pé, com o diálogo principal inteiro e vazio** — combo de times sem itens, todos os campos em branco, e o botão `Write into CD image` ali |
| port | **encerra**; nenhuma janela sobra |

Os dois mostram o mesmo aviso (`Impossible editing without CD image !`) antes
disso.

**E o comentário do port afirma o contrário do que o original faz.** Em
[`src/app/main.cpp`](../../src/app/main.cpp):

```cpp
// The original asked for the image inside OnInitDialog and bailed out of
// the dialog if the user cancelled. Same order here: no image, no window.
if (!window.OpenImage(image)) {
    return 1;
}
```

O original **não** sai do diálogo. `aprifilebin()` devolve `FALSE`,
`OnInitDialog` faz `return FALSE` (`legacy/mfc/edDlg.cpp:1331`) — e em MFC o
retorno de `OnInitDialog` **não decide se o diálogo vive**: ele só diz se o
framework deve mover o foco para o primeiro controle. Para abortar seria preciso
`EndDialog`, que não é chamado. O editor continua, sem imagem carregada.

## Evidência

Medido em 2026-08-31 com `tools/par/8.10-ciclo-oraculo.sh` e
`tools/par/8.10-ciclo-port.sh`, `ptbr-remaster.bin`.

Oráculo:

```text
== item 1: cancelar o diálogo de abertura ==
  diálogo de abertura apareceu (id 14680085)
  aviso apareceu; captura em /tmp/c09/ora-cancelar.png
  ed.exe ainda vivo? sim
  janela principal? 0xe00001
```

E a captura da janela que sobra mostra o diálogo completo, **vazio** — nenhum
nome de time, nenhuma barra, nenhum jogador.

Port:

```text
== item 1: cancelar o diálogo de abertura ==
  diálogo de abertura apareceu (id 4194313)
  janelas logo após cancelar:
    4194317 Geometry: 321x100 :: WE2002 Editor      <- o aviso
  processo ainda vivo? NAO
  janelas ao final:
    543 Geometry: 1280x1024 ::                       <- só a raiz
```

O fonte, dos dois lados, confirma a leitura:

```cpp
// legacy/mfc/edDlg.cpp:1331, dentro de OnInitDialog
if(! aprifilebin("WE2002 CD Image (we2002.bin)|...||"))
{
    return FALSE;      // NAO fecha o diálogo
}
```

## Causa raiz

Uma armadilha de MFC lida ao pé da letra: `BOOL OnInitDialog()` parece um
"deu certo / não deu", e é um "eu mesmo cuidei do foco". Quem portou leu como
aborto, escreveu o comentário afirmando isso, e o `main.cpp` encerra.

## Correção

**Decidir primeiro, e a decisão é do usuário**, porque as duas saídas são
defensáveis:

1. **Reproduzir o original** — mostrar a janela vazia. É o que a régua de
   paridade pede em todo o resto do projeto, inclusive onde o original está
   errado (a troca dos cobradores é reproduzida de propósito). O custo é uma
   janela em que `Write into CD image` está clicável sem imagem carregada;
   convém medir o que o original faz nesse clique antes de copiá-lo.
2. **Manter o encerramento** e registrá-lo como **divergência deliberada**, ao
   lado das quatro da Fase 5, com a razão escrita.

**O que não pode ficar como está, em qualquer dos dois casos: o comentário do
`main.cpp`.** Ele afirma um fato falso sobre o original, e é o tipo de frase
que a próxima pessoa cita como se fosse medida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/main.cpp` | modificar — o comentário, e o comportamento se a decisão for 1 |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 1 da §8.10 e, se for o caso, a §6 |
| `docs/PLAN-LINUX.md` | modificar — a lista de divergências deliberadas, se for o caso |

## Verificação

- [x] O comentário do `main.cpp` descreve o que o MFC faz, não o que parecia
- [x] A decisão está escrita, com a razão, em `/docs/PARIDADE-FUNCIONAL.md`
- [x] ~~Se a escolha for reproduzir: `tools/par/8.10-ciclo-port.sh` passa a
      relatar janela principal viva depois do cancelamento~~ — **não se aplica**:
      a escolha foi a 2, manter o encerramento. O roteiro segue relatando
      `processo ainda vivo? NAO`, que passa a ser o comportamento esperado
- [x] `ctest --preset debug` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31

**Resumo do que foi feito:** a decisão foi do usuário e foi a **opção 2** —
manter o encerramento do port e registrá-lo como divergência deliberada. Não
houve mudança de comportamento; o trabalho foi de comentário e de registro.

A evidência foi reproduzida de forma estática antes de editar, porque o sintoma
é de fonte, não de tela: `src/app/main.cpp:40-41` afirmava que o original
abandonava o diálogo, e `legacy/mfc/edDlg.cpp:1331` mostra o `return FALSE` sem
nenhum `EndDialog` no `OnInitDialog` (medido com `awk` sobre as linhas 1300-1500:
zero ocorrências). O comentário estava errado como a CORR descreve.

Três sítios, cada um dizendo a mesma coisa no seu registro:

1. `src/app/main.cpp` — o comentário passa a dizer o que o MFC faz (`return
   FALSE` só declara que o foco foi tratado) e nomeia o encerramento do port
   como divergência deliberada, com o ponteiro para a §6 e para esta CORR.
2. `docs/PARIDADE-FUNCIONAL.md` — nova linha **7** na tabela da §6, e o item 1
   da §8.10 passa de "esperando decisão" para a decisão escrita.
3. `docs/PLAN-LINUX.md` — a lista de divergências deliberadas da Fase 5 ganha a
   entrada, com a origem dita (decidida depois, pela paridade de tela), para o
   leitor não a confundir com as quatro da própria fase.

A razão registrada nos três: janela com `Write into CD image` clicável e sem
imagem carregada é pior que nenhuma janela, e o que o original faz nesse clique
nunca foi medido — copiar o comportamento seria copiar um risco não medido.

**Problemas encontrados:** o preâmbulo da §6 conta as divergências em prosa
("as quatro primeiras... a última"), então acrescentar uma linha exige reescrevê-lo.
Ficou com a contagem de **sete**, coerente com esta etapa; a
[CORR-WTE-141](/docs/tasks/CORR-WTE-141.md), que sai em commit próprio, é quem o
leva a oito.

**Gates:** `ctest --preset debug` — **9 testes, 5 rodaram, 5 passaram, 0
falharam**; os 4 pulados são os que precisam de imagem ou do `:98` (`golden`,
`golden_gui`, `pes2_image`, `pes2_boot`), pulados como sempre. `roms/` intocada
e `work/` sem cópia — esta correção não abriu editor nem golden.

**Arquivos criados/modificados:**

- `src/app/main.cpp` — modificado (comentário)
- `docs/PARIDADE-FUNCIONAL.md` — modificado (§6 linha 7 e preâmbulo, §8.10 item 1)
- `docs/PLAN-LINUX.md` — modificado (divergências deliberadas)
- `docs/tasks/correcoes-progresso.md` — modificado (tabela e checklist)
