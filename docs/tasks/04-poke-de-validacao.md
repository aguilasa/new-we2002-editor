---
id: PES2-TASK-04
title: "O `poke` de validação — PIEMONTE em todas as telas"
type: verificação
category: verificação
phase: 2
depends_on: ["PES2-TASK-02", "PES2-TASK-03"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 2)"
status: pendente
---

# PES2-TASK-04: O `poke` de validação

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 2 — o item que a fecha.
- **É o primeiro fechamento de laço do projeto inteiro.** Até aqui tudo foi
  leitura: contagem, digest, alinhamento. Este é o primeiro gesto que
  **escreve** e pede ao jogo que confirme.

O plano diz, literalmente: *"o primeiro `poke` de validação — renomear
`PIEMONTE`, dentro do slot, em todas as cópias, e ver o nome novo no
emulador em todas as telas. É esse teste que fecha a fase, não a varredura,
e ele é o único item que sobrou dela."*

---

## Objetivo

Provar, com captura de tela, que:

1. o mapa de cópias da §1.5 está **completo** — nenhuma tela mostra o nome
   velho depois do `poke`;
2. a correspondência entre as cinco listas da §6.1 está **certa** — o nome
   novo aparece no time certo, não num vizinho plausível;
3. o jogo **não trava** com o valor novo.

### O método

```
cp -r "roms/…(EsIt)" <scratch>/pes2-poke/          # 571 MiB, as oito faixas
python3 tools/pes2/poke.py <scratch>/…/…(Track 1).bin --team <PIEMONTE> --name PIEMONTE2 --dry-run
python3 tools/pes2/poke.py <scratch>/…/…(Track 1).bin --team <PIEMONTE> --name PIEMONTE2
tools/pes2/drive.sh <scratch>/…/…(Track 1).bin --screen team-select,result,replay --out-dir <scratch>/shots/
```

**`PIEMONTE2` tem 9 caracteres, como `PIEMONTE` tem 8** — cabe no slot
alinhado sem deslocar nada, e é visivelmente diferente na tela. Se não
couber em alguma cópia, o nome escolhido está errado, não a ferramenta.

### Controle: o nome velho também tem de sumir

Verde só de "vi `PIEMONTE2` na seleção de time" não mede o que a §6.1 cobra.
A asserção é dupla: **`PIEMONTE2` aparece em todas as telas alcançadas, e
`PIEMONTE` não aparece em nenhuma.** É a diferença entre "gravou uma cópia"
e "gravou o conjunto".

### E o round-trip volta

Gravar `PIEMONTE` de volta pelo mesmo caminho tem de devolver o `.bin`
**byte a byte idêntico** ao original. É a mesma guarda da §5.1, aplicada ao
gravador novo.

---

## Critério de conclusão

- [ ] `PIEMONTE2` visível em pelo menos três telas, com PNG por tela.
- [ ] `PIEMONTE` ausente de todas as telas capturadas.
- [ ] O jogo roda pelo menos dois minutos depois do `poke` sem travar
      (medido como o `boot_check.sh` mede: dois quadros que diferem).
- [ ] Round-trip de volta: `cmp` zero contra o original.
- [ ] Resultado escrito na §5 do plano, fechando a Fase 2 — com o número, não
      com "funcionou".
- [ ] Os PNGs **não** entram no git (jogo comercial). O que entra é o script
      e a medida.

---

## Log de Execução

*(a preencher)*
