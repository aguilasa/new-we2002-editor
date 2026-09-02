---
id: PES2-TASK-05
title: "Harness de diferencial de memory card"
type: ferramenta
category: engenharia-reversa
phase: 3
depends_on: ["PES2-TASK-03"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §4.2 (alavanca 3)"
status: pendente
---

# PES2-TASK-05: Harness de diferencial de memory card

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §4.2, alavanca 3, e §3.3.
- **É a alavanca mais barata que sobrou.** O Edit Mode do PES2 grava o time
  editado no cartão; editar *um* atributo de *um* jogador, salvar, e comparar
  dois `.mcr` isola o campo — **com rótulo**, porque quem editou sabe o quê.

O que já existe: `tools/pes2/memcard.py` lê o cartão, acha os 1.242 registros
de 10 B em @516 e alinha os 54 elencos contra o disco. O que falta é o
**ciclo**: cartão antes → editar na tela → cartão depois → diferença isolada.

Uma alavanca que a §6.2 do `PES2-AJUSTES.md` já disse que **não** existe: os
três "parciais" de Noruega, Argentina e Austrália não eram pares
editado/original. Não havia divergência nenhuma; a busca é que estava
estreita. Começar deste ciclo, e não daquele achado.

---

## Objetivo

`tools/pes2/card_diff.py`, mais o roteiro de emulador que o alimenta.

```
python3 tools/pes2/drive.py <copia> --screen edit-player --save-card <scratch>/antes.mcd
# … edita um atributo na tela …
python3 tools/pes2/drive.py … --save-card <scratch>/depois.mcd
python3 tools/pes2/card_diff.py <scratch>/antes.mcd <scratch>/depois.mcd
```

Saída: a lista de bytes que mudaram, cada um com offset absoluto no cartão,
offset **relativo ao registro do jogador** (uma vez que a origem do registro
esteja conhecida), valor antigo e novo, e os bits que se mexeram.

### Por que bit, e não byte

O WE2002 guarda atributo em **campo de bits** — `SquadNumbers` é um
`std::uint32_t` com bitfields, e o `Player::Decode`/`Encode` do core
desempacota. Se a engine é a mesma (§1.4), o PES2 faz o mesmo, e um
diferencial que só reporte "o byte 7 mudou de 0x4A para 0x4E" perde a
informação de que foram os bits 2–3. **Reportar máscara**, sempre.

### Disciplina do ciclo

- **Um atributo por vez.** Dois de uma vez e o mapeamento fica ambíguo.
- **Anotar o valor antigo e o novo na tela**, não só que mudou — é isso que
  dá o domínio do campo (0–99? 1–8? enum?).
- **O cartão do usuário nunca é escrito.** O `run_duckstation.sh` já usa
  `XDG_DATA_HOME` isolado com cartão próprio; o ciclo herda isso.

---

## Critério de conclusão

- [ ] O ciclo inteiro roda e é repetível: mesma edição, mesma diferença.
- [ ] Pelo menos **três** atributos diferentes isolados, cada um com offset,
      máscara de bits e domínio observado.
- [ ] A ferramenta acusa alto quando os dois cartões diferem em mais lugares
      do que uma edição justifica — cabeçalho de save, contador, checksum —
      e sabe separar o ruído fixo do sinal.
- [ ] Registrada no `check_image.py`, ou com o motivo escrito de por que não
      dá (o ciclo pede emulador e mão humana).

---

## Log de Execução

*(a preencher)*
