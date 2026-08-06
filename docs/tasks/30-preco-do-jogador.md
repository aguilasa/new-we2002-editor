---
id: WTE-TASK-30
title: "Preço derivado dos atributos — jogador e time inteiro"
type: implementação
category: features
phase: 5
depends_on: ["WTE-TASK-24", "WTE-TASK-25"]
status: pendente
---

# WTE-TASK-30: Preço do jogador

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §5.1.
- Primeira das quatro features que motivaram o projeto: o `ed.exe` não calcula
  preço, o editor do Obocaman calcula. Novidade da v0.98 para o jogador e da
  v0.99 para o time inteiro ("calculate credits for a whole team with just one
  click").

**Vem primeiro entre as quatro, e fora de ordem no plano geral** (§10, passo 5):
entrega valor antes de a Fase 4 fechar, é isolada, não depende de gravação, e
valida o ferramental de decompilação num alvo pequeno e conferível.

---

## Objetivo

Recuperar a fórmula e implementá-la, com prova numérica.

### Alvos

| Handler | Endereço |
|---|---|
| `etiqprecioClick` | `0x00408bb8` |
| `casilla_precioKeyPress` | `0x00408b9c` |
| formulário `jugador` | — |

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
- [ ] 100% de acerto sobre amostra grande das duas ROMs
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
