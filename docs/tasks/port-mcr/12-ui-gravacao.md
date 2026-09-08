---
id: MCR-TASK-12
title: "Gravação pela UI: ficha, formação e dorsais"
type: implementação
category: ui
phase: 3
depends_on: ["MCR-TASK-11"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §3"
status: pendente
---

# MCR-TASK-12: A UI em gravação

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §3 e §5.1.
- **O gate da MCR-TASK-10 é pré-requisito duro.** Gravação pela tela sem gate é
  a combinação que perde cartão do usuário.
- **O veredito do `0x6500` (MCR-TASK-13) muda o que esta tela desenha**: se for
  capitão, há um campo "capitão"; se for o sexto cobrador, há seis cobradores.
  Descobrir depois é refazer a tela.

---

## Objetivo

Editar e gravar pela janela, com a garantia de que o arquivo gravado continua
passando no round-trip.

---

## Critério de conclusão

- [ ] **A porta da UI é o `model`, e a gravação precisa da segunda.** A Regra 3
      proíbe `tools/mcr/ui/**.py` de importar `layout`, `card` e `mcrio`, e o
      `selftest` varre por isso — o controle `ui-imports-an-address` fica
      vermelho quando alguém tenta. A MCR-TASK-11 abriu a primeira porta,
      `model.load()`, que delega ao `mcrio` por import adiado (o `mcrio`
      importa o `model` no topo, então o caminho contrário só funciona dentro
      da função). A gravação precisa da porta correspondente — `model.store()`
      ou equivalente —, com as recusas do `mcrio` intactas: nada de um
      gravador próprio da tela, que é como uma janela grava um cartão que o
      gate teria recusado.
- [ ] **Nada na tela de leitura grava, e isso é estrutural.** Todo valor da
      ficha é um `QLabel`; não há widget editável nem sinal que alcance
      `Save.write`. Ao tornar a tela editável, o que se perde é essa garantia
      por construção — então a substituta tem de ser medida, não prometida.
- [ ] **`X*7` e `Y*2` moram só no `ui/formation_view.py`.** Arrastar um
      jogador no campo tem de converter de volta (dividir) **na UI**, e o que
      chega ao modelo são as unidades do cartão. A armadilha 7 do perfil é
      exatamente isto: os fatores no núcleo matam o round-trip.

- [ ] Edição de ficha, de dorsal, de papel e de posição no campo (arrastar),
      todas indo para o modelo e de lá para os bytes.
- [ ] **Gravar sempre em cópia por padrão**; sobrescrever o original exige
      confirmação explícita.
- [ ] O arquivo gravado pela UI passa no `mcr roundtrip` — a tela não pode
      produzir cartão que o núcleo recuse.
- [ ] Uma edição medida ponta a ponta: mudar um atributo pela tela muda
      exatamente os bytes previstos, e nada mais.
- [ ] O `0x6500` desenhado conforme o veredito da MCR-TASK-13, ou ausente se
      ela ainda não tiver fechado.
- [ ] Captura de tela no `:98`, antes e depois, anexada ao Log.
- [ ] Diálogo, confirmação e mensagem de erro da gravação **em en-US**, como o
      resto da UI (§3.5).

---

## Log de Execução

*(a preencher)*
