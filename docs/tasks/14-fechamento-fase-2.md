---
id: WTE-TASK-14
title: "Fechamento da fase 2 — a casca está fiel?"
type: fechamento
category: ui
phase: 2
depends_on: ["WTE-TASK-12", "WTE-TASK-13"]
status: concluído
---

# WTE-TASK-14: Fechamento da fase 2

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 2, critério de pronto.
- A fase 2 entrega ~60% do volume de código do projeto por gerador. Se ela
  fechar com controle faltando ou evento fora de ordem, todo handler da Fase 4
  é implementado contra uma casca errada.

---

## Objetivo

Aceitar a fase, ou listar o que falta.

### Conferências

1. **`--check` do `dfm2lfm.py` verde** e registrado na bateria de testes.
2. **Nenhum `.lfm` ou unidade gerada editado à mão** — provar rodando o
   `--check` sobre a árvore commitada.
3. **Os 96 stubs existem e logam**, um por linha do `published_methods.tsv`.
4. **Os 18 formulários conferidos visualmente**, com veredito escrito.
5. **`eventos.md` sem pergunta em aberto** que a Fase 4 vá precisar.

### Métrica a registrar

Quantas linhas de Pascal existem, e quantas são geradas. Este número é a
verificação da tese da §4.4 — se a fração gerada for muito menor que o esperado,
a tese está errada e o plano precisa dizer isso.

### O que ainda não foi provado

A casca não toca a imagem de CD. Nada nesta fase diz que o app **funciona** —
só que ele **parece** e **reage**. Escrever isso, para o vocabulário não inflar.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase2.py` | criar — mede e **aborta**; `re/fase-2.md` é saída dele |
| `wte/tools/test_check_fase2.py` | criar — as rotas de aborto |
| `wte/re/fase-2.md` | criar (gerado) |
| `docs/PLAN-WTE-LAZARUS.md` | modificar — §4.4 e o critério de pronto da fase 2 |
| `wte/tools/README.md` | modificar — as duas tabelas |
| `docs/tasks/progresso.md` | modificar |

O `fase-2.md` não é escrito à mão, pelo mesmo motivo do `fase-1.md`: ele é só
números, e número em doc tem de vir de ferramenta. O `check_fase2.py` entra na
bateria pelo `wildcard` do Makefile, sem editar alvo nenhum.

---

## Critério de conclusão

- [x] `--check` do gerador verde e na bateria de testes — 216 testes, 10
      geradores, incluindo o `check_fase2.py` novo
- [x] Provado que nenhum arquivo gerado foi editado à mão — pelo
      `dfm2lfm.py --check`, que é de quem essa prova é; o `check_fase2.py`
      **não** a refaz, para não criar segunda cópia da medida
- [x] Os 96 stubs conferidos contra o TSV — e contra a unidade que declara a
      classe, que é a parte que o enunciado não pedia e é onde o erro moraria
- [x] Os 18 formulários com veredito visual — conferido por leitura da tabela
      do `re/visual.md`, não por confiança
- [x] Fração de código gerado medida e comparada com a tese da §4.4 —
      **96,2%**
- [x] Escrito o que a fase **não** prova — quatro itens
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  A fase 2 fecha. O produto é o [`../../wte/re/fase-2.md`](../../wte/re/fase-2.md),
  **gerado** pelo `check_fase2.py` — o `fase-2.md` é só número, e número em doc
  tem de sair de ferramenta, como o `fase-1.md` já fazia.

  **A tese da §4.4 se confirma, e com folga: 96,2% do Pascal da casca é saída
  de gerador** — 8.982 linhas geradas (18 unidades, 2.214; estrutura dos 18
  `.lfm`, 6.768) contra 353 escritas à mão, que são `wte.lpr` (31),
  `retrace.pas` (125) e `wtemain.pas` (197). As três são andaime de projeto,
  não lógica do editor.

  As **25.712 linhas de hex** dos 118 blobs ficam **fora** da conta, e isso é
  decisão, não descuido: contadas junto, a fração vai a 99,0% e passa a medir
  bitmap em vez de geração de código. O script parte o `.lfm` por estado
  (`Data = {` … `}`), não por regex de "linha só com hexadecimal", porque essa
  heurística erraria em silêncio.

  **O que a fase 2 não prova** ficou escrito em quatro itens, e o segundo
  obrigou a corrigir o plano: o critério de pronto pedia "os 18 formulários são
  navegáveis", e isso era **impossível por construção** — quem abre formulário
  são os handlers, que nesta fase são stub. Virou "aparecem", com a nota de que
  navegação é da WTE-TASK-25. Medido: 18 de 18 abrem no `:99` por `--show`,
  96 de 96 stubs logam, 16 `FormCreate` no arranque.

  A conferência que rendeu mais foi a que o enunciado não pedia: **cruzar cada
  stub com a unidade que declara a classe**, e não só com o TSV. Contar 96
  `REStub` não prova nada — 96 stubs no arquivo errado dariam o mesmo número.

- **Problemas encontrados:**

  1. **"Fração de código gerado" não é um número, são dois.** Com o hex dos
     blobs a resposta é 99,0%, sem ele 96,2%, e só o segundo responde à §4.4.
     Publicar um sem o outro seria escolher o número que soa melhor.
  2. **A §4.3 afirma que a UI é 60% do volume, e isso continua sem
     verificação.** Não é falha da medição: a UI é a única camada que existe
     hoje. Só fecha depois da fase 3 (dados, gerada) e da 4 (os 96 corpos, à
     mão). Registrado no `fase-2.md` e na §4.4 do plano em vez de deixar a
     afirmação solta.
  3. Nenhum problema de ferramenta. O `check_fase2.py` entrou na bateria pelo
     `wildcard` do Makefile sem tocar em alvo nenhum, como a WTE-TASK-02
     desenhou.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/check_fase2.py` | criar |
  | `wte/tools/test_check_fase2.py` | criar (14 testes) |
  | `wte/re/fase-2.md` | criar (gerado) |
  | `docs/PLAN-WTE-LAZARUS.md` | modificar — §4.4 e o critério de pronto da fase 2 |
  | `wte/tools/README.md` | modificar |
  | `docs/tasks/progresso.md` | modificar |
