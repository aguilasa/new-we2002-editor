---
id: CORR-WTE-078
title: "Correção: o Log da sétima passagem conta 7 casos novos no test_dump_zonas.py, e são 9"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-078: o Log da sétima passagem conta 7 casos novos no `test_dump_zonas.py`, e são 9

## Problema identificado

O Log da sétima passagem da
[WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md), na lista de arquivos
modificados, diz:

> `wte/tools/test_dump_zonas.py` (**7 casos novos**, cinco deles recusas)

O commit que fechou a task (`671a1f9`) acrescentou **9**. A metade da frase que
importa mais — "cinco deles recusas" — está **certa**, e é o que dá valor ao
guard; o que não bate é a contagem total.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
diff <(git show "671a1f9^:wte/tools/test_dump_zonas.py" | grep -oE 'def test_[a-z_0-9]+') \
     <(grep -oE 'def test_[a-z_0-9]+' wte/tools/test_dump_zonas.py)
```

```text
10a11,19
> def test_as_duas_fecham_como_estao
> def test_passo_errado_muda_a_contagem_de_colunas
> def test_folga_errada_desloca_o_primeiro_marcador
> def test_prefixo_trocado_nao_acha_marcador
> def test_constantes_diferentes_entre_as_malhas_reprovam
> def test_folga_diferente_reprova_antes_pela_coordenada
> def test_os_tres_numeros_saem_do_exe
> def test_cada_malha_le_a_propria_imagem
> def test_os_prefixos_sao_os_do_formulario
```

São 9 linhas, de 10 para 19 casos. As cinco recusas são
`passo_errado`, `folga_errada`, `prefixo_trocado`, `constantes_diferentes` e
`folga_diferente` — a conta de recusas fecha.

## Causa raiz

Contagem escrita no Log antes dos dois últimos casos entrarem, e não revisada
ao commitar.

## Correção

### Arquivo: `docs/tasks/29-camisa-e-bandeira-2d.md`

No Log da sétima passagem: `7 casos novos` → `9 casos novos`.

Vale escrever ao lado **como se remede**, porque é a mesma pergunta toda vez:
`grep -c 'def test' wte/tools/test_dump_zonas.py` contra o mesmo `grep` no
commit anterior.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/29-camisa-e-bandeira-2d.md` | modificar |

## Verificação

- [ ] O número do Log e o `diff` dos `def test` entre `671a1f9^` e `671a1f9`
      são o mesmo
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
