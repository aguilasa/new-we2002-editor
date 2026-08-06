---
id: WTE-TASK-28
title: "Handlers dos 13 diálogos auxiliares"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25"]
status: pendente
---

# WTE-TASK-28: Handlers auxiliares

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- O resto dos 96: os handlers dos formulários `ficha_*`, que na maior parte são
  avisos e confirmações. Espera-se que a maioria receba veredito **`trivial`** —
  fecha o formulário, devolve um resultado, não toca a imagem.

**"Espera-se" não é veredito.** Cada um precisa ser olhado; o barato é que
olhar custa pouco quando o handler tem seis instruções.

---

## Objetivo

Fechar os handlers que sobraram, com veredito para cada.

### Alvos

Os `ficha_*`: `about`, `color`, `creditos_equipo`, `dorsal`, `enlaza`, `error`,
`error2`, `info`, `info2`, `info3`, `info4`, `movertodos`, `salida`, `warning`,
`warning_2`.

Handlers repetidos por vários formulários — `BitBtn1Click` (4×),
`BitBtn2Click` (2×), `BitBtn3Click` (3×), `SpeedButton1Click` (3×).

Os outros seis do escopo têm nome parecido mas **não** se repetem — cada um
aparece uma vez só: `SpeedButton2Click`, `Button2Click`, `Image3Click`,
`base_teamClick` (todos de `MainForm`), `botonClick` (`ficha_color`) e
`imagen_urlClick` (`ficha_about`).

**A coluna `formulario` do `published_methods.tsv` é indispensável aqui** — sem
ela, "implementar `BitBtn1Click`" é ambíguo entre quatro formulários.

### O que fica de fora, e por quê

Estes pertencem a `ficha_color`, `jugador`, `MainForm` e `estrategia` mas são
**fórmula**, não diálogo, e são das tasks 30 e 32:

| Handler | Formulário | Dono |
|---|---|---|
| `etiqprecioClick`, `casilla_precioKeyPress` | `jugador` | WTE-TASK-30 (preço) |
| `colorearClick` | `MainForm` | WTE-TASK-32 (render 2D) |
| `gradienteClick`, `oscurecerClick`, `aclararClick`, `lista_col0..3Change`, `colorMouseDown`, `barraChange`, `barra1Change`, `barra2Change` | `ficha_color` | WTE-TASK-32 (render 2D) |
| `malla1MouseDown`, `malla2MouseDown` | `estrategia` | WTE-TASK-32 (render 2D) |

Aqui se implementa **a moldura** desses formulários — abrir, fechar, OK/Cancelar
— e as tasks 30 e 32 preenchem o miolo.

### `ficha_enlaza` merece atenção

"Enlaza" = vincula. O `newWe2002` já sabe que os links (`OFS_PLAYER_ATTR_8`) são
o que o `Save` usa para reconstruir as all-star. Um diálogo que edita link **não
é trivial**, mesmo parecendo. Conferir antes de marcar.

### `ficha_movertodos` idem

É a tela de "mover todos os jogadores de cada time com um clique". Toca dados.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/src/ep2002_*.pas` | modificar |

---

## Critério de conclusão

- [ ] Todo handler restante com veredito escrito
- [ ] Handlers de nome repetido resolvidos pelo formulário dono
- [ ] `ficha_enlaza` e `ficha_movertodos` analisados, não presumidos triviais
- [ ] A moldura dos formulários das tasks 30 e 32 pronta
- [ ] Nenhum `trivial` atribuído sem ter olhado o código
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
