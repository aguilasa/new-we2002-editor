---
id: WTE-TASK-32
title: "Preço derivado dos atributos — jogador e time inteiro"
type: implementação
category: features
phase: 5
depends_on: ["WTE-TASK-24", "WTE-TASK-25"]
status: pendente
---

# WTE-TASK-32: Preço do jogador

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.1.
- Primeira das quatro features que motivaram o projeto: **o `ed.exe` não
  *oferece* preço** — o editor do Obocaman oferece. Novidade da v0.98 para o
  jogador e da v0.99 para o time inteiro ("calculate credits for a whole team
  with just one click").

> **A frase acima dizia "o `ed.exe` não calcula preço", e isso era falso**
> ([CORR-WTE-094](/docs/tasks/CORR-WTE-094.md), 2026-08-24). Ele calcula: a
> fórmula está em `legacy/mfc/edDlg.cpp:7703` (`CalcolaCostoGiocatore`), o laço
> do time inteiro em `:7948`, e o handler no message map em `:1286`. O que não
> existe é o **controle** — `CMD_CALCCOSTI` (1244) está no `resource.h` e não
> no `ed.rc`, o mesmo caso do `MainForm.Button2Click` no binário do Obocaman.
>
> **Isso dá a esta task um oráculo B que ela não sabia ter**, e já em Pascal:
> `ComputePlayerCost` em `wte/src/we2002_database.pas:1776`, transpilado de
> `src/core/Database.cpp:1465`.
>
> **Sem presumir fórmula igual.** A do `ed.exe` é `double`, parte de `k = 16`,
> ramifica por posição e fecha em `if (k<1) k = 1; return (int)ceil(k);`; a do
> Obocaman é inteira, sobre uma soma, com `0x2DC6C0`, `0x9C40`, `0x2BC`, `7`,
> um `+5` e a variante `× 5 div 3`. O valor dele é **desenhar a amostragem**:
> os três riscos da seção "onde a tabela pode enganar" estão todos
> exemplificados lá — saturação no `if (k<1)`, arredondamento no `ceil`, e
> termo cruzado nos bônus `== 19` e no `if(foot == 2)`.

**Vem primeiro entre as quatro, e fora de ordem no plano geral** (§10, passo 5):
entrega valor antes de a Fase 4 fechar, é isolada e valida o ferramental de
decompilação num alvo pequeno e conferível.

> **"Não depende de gravação" era metade verdade, e a
> [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) mediu a outra metade em
> 2026-08-21.** Vale para o `etiqprecioClick`, que só mostra o número na tela.
> **Não vale** para o preço do time inteiro: o `base_teamClick` percorre os 23
> slots e **grava um byte em cada**, no offset da terceira coluna da tabela de
> offsets — a mesma coluna condicional que a `0x004046E8` usa. A régua desta
> task é **dupla**: tela para a fórmula, byte para o time inteiro.

---

## Objetivo

Recuperar a fórmula e implementá-la, com prova numérica.

### Alvos

| Handler | Formulário | Endereço | O que falta |
|---|---|---|---|
| `etiqprecioClick` | `jugador` | `0x00408bb8` | a fórmula, e o número na tela |
| `casilla_precioKeyPress` | `jugador` | `0x00408b9c` | o filtro de tecla do campo |
| `base_teamClick` | `MainForm` | `0x00410ff4` | **o laço dos 23 e a gravação** |

O `base_teamClick` chegou nesta lista pela WTE-TASK-30, que implementou a
**moldura** dele — posicionar o `ficha_creditos_equipo`, mostrá-lo e desistir
em `mrCancel` — e deixou o miolo aqui, com o veredito `aberto` e o dono
nomeado. A spec medida está em
[`wte/re/spec/MainForm.base_teamClick.md`](../../wte/re/spec/MainForm.base_teamClick.md)
e já traz a faixa de endereços da fórmula (`0x004110E7`..`0x0041112A`), as
constantes que aparecem nela (`0x2DC6C0`, `0x9C40`, `0x2BC`, `7`, `+5`) e a
variante `× 5 div 3` de `0x00411142`.

**Quem separa titular de reserva ali é o ponteiro do `Sender`**, comparado com
o campo `base_team`, e não o nome — o `LadoTitular` do `.aux.inc` não serve.

### O método que **não** precisa de decompilador

A fórmula é aritmética pura sobre atributos já decodificados. Então dá para
recuperá-la por **tabela de verdade**:

1. Abrir o original no Wine com um jogador conhecido.
2. Variar **um** atributo por vez, ler o preço na tela, tabelar.
3. Repetir para cada atributo.
4. Ajustar a fórmula contra a tabela.

Isso é observação, não engenharia reversa de código — e produz evidência mais
forte que ler assembly, porque mede o comportamento em vez de interpretá-lo.

**Use o decompilador para conferir a fórmula recuperada, não para descobri-la.**
As duas fontes concordando é a melhor evidência que este projeto pode ter.

### Onde a tabela pode enganar

- **Saturação.** Se o preço satura num teto, variar atributo alto não move nada
  e a tabela sugere coeficiente zero.
- **Arredondamento.** Divisão inteira vs. real muda o resultado em ±1 e some no
  olho. Amostrar valores que caiam perto de meio.
- **Termo cruzado.** Se a fórmula tiver produto de dois atributos, variar um por
  vez não revela. Testar pelo menos um par variando junto.

### O time inteiro

O botão de time é presumivelmente a soma dos jogadores — **presumivelmente**.
Conferir: pode haver desconto, teto, ou tratamento diferente do goleiro.

### Critério

Acerto em **100%** de uma amostra grande, não numa amostra escolhida. Gerar a
amostra a partir dos jogadores reais das duas ROMs e comparar app contra
original, jogador a jogador.

**Não precisa de golden test de imagem** — o preço não é gravado, é exibido.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/etiqprecioClick.md` | criar |
| `wte/re/preco.md` | criar — a fórmula, a tabela de verdade, as duas fontes |
| `wte/src/we2002_preco.pas` | criar |
| `wte/tests/test_preco.pas` | criar |

---

## Critério de conclusão

- [ ] Fórmula recuperada por tabela de verdade
- [ ] Fórmula conferida contra o disassembly, e as duas fontes concordando
- [ ] Saturação, arredondamento e termo cruzado testados explicitamente
- [ ] Cálculo do time inteiro conferido, não presumido soma
- [ ] `base_teamClick` com golden verde — **byte, não tela** —, com o controle
      fechando antes, e o veredito dele trocado de `aberto` no
      `re/spec/INDICE.md`
- [ ] 100% de acerto sobre amostra grande das duas ROMs
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
