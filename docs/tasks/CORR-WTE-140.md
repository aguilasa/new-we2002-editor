---
id: CORR-WTE-140
title: "Correção: cancelar o diálogo de abertura encerra o port e deixa o `ed.exe` com a janela vazia"
type: correção
category: comportamento
status: pendente
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

- [ ] O comentário do `main.cpp` descreve o que o MFC faz, não o que parecia
- [ ] A decisão está escrita, com a razão, em `/docs/PARIDADE-FUNCIONAL.md`
- [ ] Se a escolha for reproduzir: `tools/par/8.10-ciclo-port.sh` passa a
      relatar janela principal viva depois do cancelamento
- [ ] `ctest --preset debug` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
