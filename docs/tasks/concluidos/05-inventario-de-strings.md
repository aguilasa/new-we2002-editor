---
id: WTE-TASK-05
title: "re/strings.tsv — strings com endereço e quem as usa"
type: extração
category: engenharia-reversa
phase: 1
depends_on: ["WTE-TASK-02"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §1.5 e Fase 1 item 3"
status: concluído
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

- [x] Toda string de `.data` listada com VA
- [x] `referenciada_por` preenchida onde houver referência por imediato
- [x] `handler` cruzado com `published_methods.tsv`
- [x] As strings com suspeita de truncamento marcadas
- [x] As três perguntas respondidas em `strings.md`
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-05

- **Resumo do que foi feito:**

  `wte/tools/dump_strings.py` (stdlib pura, `--check`, saída byte-estável) lê
  o `.exe` e o `published_methods.tsv` e escreve `wte/re/strings.tsv` (765
  strings) e `wte/re/strings.md`.

  **Reconhecimento em quatro cortes**, todos medidos: corrida de `0x20..0x7E`
  terminada em NUL; nenhum byte dentro de slot de realocação (a `.reloc`
  separa ponteiro de texto, a mesma régua do `dump_offsets.py`); comprimento
  ≥ 4; **ou** comprimento ≥ 1 com o início referenciado pelo `.text`, o que
  resgata 77 strings de uma a três letras. Sem o corte 2 e o 3, a varredura
  ingênua devolve 1.964 registros, quase todos tabela de ponteiro, a tabela de
  offsets da WTE-TASK-06 e a tabela de caracteres de 2 bytes.

  **Censo por formato:** 760 literais C, **0** `AnsiString` com cabeçalho (o
  teste — comprimento em `VA-4`, refcount `-1` em `VA-8` — está no script e o
  resultado está no `.md`), 5 UTF-16LE, todas da RTL.

  **Referência pela `.reloc`**, não por padrão de instrução. O padrão que este
  enunciado sugere (`mov r32,imm32` / `push imm32`) acha 430 das 474 e não
  inventa nenhuma; a `.reloc` acha as 474.

  **A coluna `handler` exigiu medir o fim de cada handler.** O TSV da
  WTE-TASK-04 só dá o início, e "handler anterior mais próximo" penduraria 287
  das 474 referências em `MainForm.FormShow`, por causa de um vazio de 64.684
  bytes. O script traz um decodificador de comprimento de instrução x86-32 e
  uma varredura linear que encerra no primeiro `ret`/`jmp` além de todo alvo de
  desvio já visto. Conferido contra o `objdump`: as fronteiras de instrução dos
  96 corpos coincidem nas **10.416 instruções**.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_strings.py` — criado
  - `wte/re/strings.tsv` — criado (gerado)
  - `wte/re/strings.md` — criado (gerado)
  - este arquivo — critérios e log

- **Problemas encontrados:**

  1. **As 70 strings com enchimento não estão em `.data`.** Medido: **13** com
     conteúdo e dois ou mais espaços no fim (mais 16 com um espaço só, sinal
     fraco, contadas à parte). Nos 18 `.dfm` de `wte/re/dfm/`, pelo mesmo
     critério, há **80** — o número da §1.5 é do `.rsrc`, isto é, de caption de
     formulário, não de `.data`. A conclusão da §1.5 continua valendo; muda
     onde procurar.
  2. **Não é "cp1252 quebrado".** Zero bytes acima de `0x7E` nas 765 strings: o
     tradutor removeu os acentos. Não há encoding a consertar.
  3. **O bloco de literais aparece três vezes em `.data`**, em `+0x8598` e
     `+0x9b80`, e as duas cópias altas não são referenciadas por ponteiro
     nenhum. Elas **não** são idênticas à viva, e é isso que interessa: a
     mensagem que a §8.8 dá como perdida (`somente na Mastere`) tem, na cópia
     morta, o parêntese fechado e `Master` inteiro. A regra de validação sai
     das duas do mesmo jeito — **a spec daquele handler pode ser escrita sem o
     binário espanhol**. A asserção da RTL também difere entre as cópias (nome
     de variável), o que diz que elas vêm de compilações diferentes e não de
     duas passadas de tradução.
  4. Duas armadilhas de alinhamento na varredura UTF-16 (`(null)` estreita
     seguida da larga; `+NAN` estreita seguida de `-INF` larga) produziam
     corridas bem formadas deslocadas de dois bytes. Resolvido exigindo que o
     código referencie o início da corrida larga — está documentado no script.
