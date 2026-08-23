---
id: CORR-WTE-088
title: "Correção: nove comentários de comportamento corrente ainda dizem :99 depois da mudança para o :98"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-088: comentário de comportamento corrente ainda diz `:99`

## Problema identificado

O display dos gates virou `:98` em 2026-08-20, e o
[CLAUDE.md](../../CLAUDE.md) é explícito sobre o que fica e o que muda:
**registro histórico continua dizendo `:99`**; texto que descreve o
comportamento de hoje, não.

Nove comentários de ferramenta viva continuam descrevendo o presente com o
número velho, e o mais visível deles é a lista de guardas do
[`golden_check.sh`](../../wte/tools/golden_check.sh) — o cabeçalho que se lê
justamente para saber o que o gate garante:

```text
# 2. recusa comecar com janela grande ja aberta no `:99`;
```

O código dessa guarda usa `$DISPLAY`, que a `roteiro_display` fixa em `:98`.
A [CORR-WTE-073](/docs/tasks/CORR-WTE-073.md) varreu o **código executável**
(`check_lcl_combo.py`, que pulava em silêncio); os comentários ficaram.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n ':99' wte/tools/golden_check.sh wte/tools/roteiro.sh \
             wte/tools/golden_run_wte.sh wte/tools/compara_tela.sh \
             wte/tools/diff_dirigido.sh
```

```text
golden_check.sh:34:# 2. recusa comecar com janela grande ja aberta no `:99`;
golden_check.sh:60:# ... Nao roda em CI -- precisa de Wine, do `:99` e
golden_check.sh:101:# Guarda 2: janela grande ja aberta no :99. ...
roteiro.sh:39:# Sem window manager no `:99` a origem da janela muda a cada corrida. ...
roteiro.sh:58:# ... Sem gerenciador de janela no `:99` o GTK2 nunca
golden_run_wte.sh:86:# viva no `:99`. A guarda 2 do `golden_check.sh` recusaria a proxima corrida --
compara_tela.sh:34:# `we-team-editor.exe` no `:99` depois de uma medicao de apoio, e processo
diff_dirigido.sh:38:# ## Regra do :99 (CLAUDE.md)
diff_dirigido.sh:87:# ... a fixacao do `:99` moram em `roteiro.sh`. ...
```

E o valor corrente, no mesmo diretório:

```bash
grep -n 'WTE_DISPLAY' wte/tools/roteiro.sh wte/tools/compara_tela.sh
```

```text
roteiro.sh:85:  export DISPLAY="${WTE_DISPLAY:-:98}"
compara_tela.sh:42:export DISPLAY="${WTE_DISPLAY:-:98}"   # fixado aqui, nunca herdado
```

**Quatro ocorrências não entram nesta correção**, porque são registro histórico
e o CLAUDE.md manda deixar: `roteiro.sh:80,82,150` (o parágrafo que **narra** a
troca, e uma medição "no `:99` o `ficha_dorsal` do port ficava…") e
`compara_tela.sh:91` ("Medidas no `:99`, nos dois lados, em 2026-08-12").

## Causa raiz

A mudança de display foi feita onde ela quebrava execução — variável e código
— e não nos comentários que descrevem o ambiente.

## Correção

### Arquivos: `wte/tools/{golden_check,roteiro,golden_run_wte,compara_tela,diff_dirigido}.sh`

Trocar `:99` por `:98` **só** nas nove linhas listadas acima, preservando as
quatro históricas. Onde a frase fala do display como escolha (`golden_check.sh`
linha 60, `diff_dirigido.sh` linha 38), escrever `:98` e não repetir a
justificativa — ela já mora inteira no `roteiro.sh:80-84` e no CLAUDE.md.

### Guarda, para não voltar

O `wte/tools/README.md` já tem a seção de convenções das ferramentas. Registrar
ali a regra em uma linha — *`:99` em comentário só como data medida; o alvo é
o `:98`* — e, se sair barato, um caso no `test_roteiro.py` que reprove `:99`
numa linha sem ano nem `WTE-TASK`/`CORR-` ao lado.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/golden_check.sh` | modificar |
| `wte/tools/roteiro.sh` | modificar |
| `wte/tools/golden_run_wte.sh` | modificar |
| `wte/tools/compara_tela.sh` | modificar |
| `wte/tools/diff_dirigido.sh` | modificar |
| `wte/tools/README.md` | modificar |
| `wte/tools/test_roteiro.py` | modificar (opcional — a guarda) |

## Verificação

- [ ] `grep -n ':99' wte/tools/*.sh` devolve só as quatro linhas históricas
- [ ] `make -C wte check` continua verde
- [ ] `bash wte/tools/golden_check.sh wte/tests/roteiros/golden-08-dorsal-mcr.txt --modo controle --artefato saida.mcr` continua `PASSOU: byte-identico`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
