---
id: WTE-TASK-05
title: "re/strings.tsv — strings com endereço e quem as usa"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
status: pendente
---

# WTE-TASK-05: Inventário de strings

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §1.5 e Fase 1 item 3.
- Mensagem de erro é atalho para entender validação sem ler assembly. Saber
  que `"Numero do uniforme invalido ([33 ... 99] somente na Mastere"` é
  referenciada por um endereço dentro de `dorsalClick` entrega a regra inteira
  de graça.

**Ressalva medida:** o binário é a tradução PT-BR do `chagas_michel`, patch
in-place com padding. **70 strings terminam em espaço de enchimento** e pelo
menos uma perdeu conteúdo (`Mastere` = `Master League` decepado). O inventário
tem de marcar quais estão nessa condição — uma spec construída sobre mensagem
truncada é spec incompleta e não parece incompleta.

---

## Objetivo

`wte/re/strings.tsv` com uma linha por string de `.data`, e a coluna que dá o
valor: **quem a referencia**.

### Colunas

| Coluna | Como sai |
|---|---|
| `va` | endereço virtual |
| `texto` | conteúdo, escapado |
| `suspeita_patch` | termina em ≥2 espaços, ou parece truncada |
| `referenciada_por` | endereços em `.text` que carregam esse VA |
| `handler` | qual dos 96 contém esse endereço (cruzar com WTE-TASK-04) |

A referência sai de `objdump -d` procurando o imediato do VA. Em código
Borland i386 sem otimização o padrão é `mov eax, 0x00423xxx` — imediato direto,
fácil de casar.

### O que responder com o resultado

- Quantas strings **não** são referenciadas por nenhum dos 96? (candidatas a
  código de inicialização ou morto)
- Qual handler tem mais strings? (provável concentrador de validação)
- As 70 com padding se concentram em algum formulário?

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_strings.py` | criar |
| `wte/re/strings.tsv` | criar |
| `wte/re/strings.md` | criar — as três perguntas respondidas |

---

## Critério de conclusão

- [ ] Toda string de `.data` listada com VA
- [ ] `referenciada_por` preenchida onde houver referência por imediato
- [ ] `handler` cruzado com `published_methods.tsv`
- [ ] As strings com suspeita de truncamento marcadas
- [ ] As três perguntas respondidas em `strings.md`
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
