---
id: PAR-TASK-07
title: "Bandeira, uniformes e os times sem bandeira própria"
type: verificação
category: ui
projeto: newWe2002
depends_on: ["PAR-TASK-01"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.8"
status: concluído
---

# PAR-TASK-07: Bandeira, uniformes e os times sem bandeira própria

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.8.
- **Projeto:** `newWe2002` (port Qt do `ed.exe`), **não** o `wte/` Lazarus.

---

## Método

O mesmo para toda a série, e é o que a §8 do inventário já fixa: **fazer a
mesma coisa no `ed.exe` sob Wine e no port, gravar as duas cópias e comparar
com `tools/golden_compare.py`.**

```sh
cp roms/ptbr-remaster.bin  "$SCRATCH/v.bin"
DISPLAY=:98 ./build/src/app/newWe2002 "$SCRATCH/v.bin"
```

**Critério de aprovação:** a única divergência é `405724..405739`, o slot 64 do
array de 63. Qualquer outra faixa é achado, e vira CORR.

**Sempre sobre cópia, sempre no `:98`.** O `roms/` nunca é alvo. Feche qualquer
editor aberto no display antes: os dois lados acham o diálogo principal pelo
tamanho, e uma janela esquecida é dirigida no lugar da que está sob teste.

**A imagem preferida desta série é a `ptbr-remaster.bin`.** Ela é a única com
oráculo vivo nos dois editores e com os ramos do codec exercitados — medido na
[PROPOSTA-IMAGEM-GOLDEN](/docs/PROPOSTA-IMAGEM-GOLDEN.md) §8.4. Onde o item
pedir nome latino legível, é ela; onde pedir kanji, a `japanese-shift-jis.bin`.

---

## Itens a conferir

- [x] Cores no teto (65535) e acima
- [x] Time sem bandeira própria (57..63, 69, 86 e o 56) → caixas desabilitadas e
      import/export recusado
- [x] `.b2002` e `.m2002`: exportar do port e importar no `ed.exe`, e vice-versa

O segundo item carrega uma **divergência deliberada** da Fase 5: o port usa teste
único de "tem bandeira própria" onde o original repetia a condição. Ela está na
lista de divergências aceitas do [/docs/PLAN-LINUX.md](/docs/PLAN-LINUX.md) e
não aparece nos golden tests — este item é onde ela finalmente se mede na tela.

O terceiro é ida e volta de arquivo, como o `.t2002` da PAR-TASK-06.

---

## Definição de pronto

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.8
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito
- [x] Divergência fora de `405724..405739` registrada como CORR, com a faixa e o
      offset simbólico — **nenhuma nova**; a do id 56 é a deliberada da Fase 5
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31 — **COMPLETA, 3 de 3.**

**Resumo:**

Duas corridas de `golden_check.sh` em modo `gui` (`OK` nas duas) para o item 1,
e medição por captura e por arquivo para os itens 2 e 3. Nenhuma divergência
nova, nenhuma CORR aberta.

**O que se aprendeu:**

**A divergência deliberada da Fase 5 apareceu na tela, e é exatamente a
prevista.** No id 56 o port desabilita as caixas de cor e o `ed.exe` as
habilita; nos ids 57..63 os dois concordam. O `graf` original tinha **dois**
testes de "tem bandeira própria" que discordavam nessa borda, e o port usa um
só — este item era onde isso finalmente se mediria, e mediu. Não é CORR: está
na lista de aceitas do plano.

**A recusa de export é idêntica nos dois**, com a mesma mensagem
(`Choose a team (that has "indipendent" flag too) !`) e sem gerar arquivo. O
botão não é desabilitado em nenhum dos dois — quem recusa é a ação.

**O `.b2002` e o `.m2002` fazem o que o `.t2002` não faz.** Os arquivos saem
**byte-idênticos** dos dois lados (41 e 40 bytes), e importar o mesmo arquivo
alterado em cada um grava o mesmo `OFS_FLAG_COLOURS+2`, com as imagens saindo
idênticas salvo a faixa conhecida. É a troca nos dois sentidos funcionando —
contra o `.t2002`, onde o port grava 52 bytes contra 56 e o `ed.exe` recusa até
o próprio arquivo ([CORR-WTE-132](/docs/tasks/CORR-WTE-132.md)). **Formatos
vizinhos do mesmo diálogo podem estar em estados opostos**, e um não autoriza
conclusão sobre o outro.

**Problemas encontrados:** nenhum.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — os três itens da §8.8 e a nota da divergência
- `docs/tasks/PAR-TASK-07.md` — este Log e o `status`
- `docs/tasks/progresso.md` — a linha da tabela do anexo
- `tools/par/8.8-prelude.sh` — o prelúdio (abre o `FlagKitDialog`; escolhe o
  time por `PAR_TEAM`)
- `tools/par/8.8-cores-teto.sh`, `8.8-b2002-exportar.sh`,
  `8.8-b2002-importar.sh` — um roteiro por caminho medido
