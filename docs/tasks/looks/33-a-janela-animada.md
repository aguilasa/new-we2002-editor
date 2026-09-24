---
id: LOOKS-TASK-33
title: "A janela animada — o boneco caminhando na tela `LOOKS SET`, no ritmo do jogo"
type: implementação
category: render
phase: 11
depends_on: [LOOKS-TASK-28, LOOKS-TASK-32, LOOKS-TASK-40]
status: pending
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.4"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
resources: [emulador, tela]
---

# LOOKS-TASK-33: A janela animada

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1 e §10.4.
- **É o pedido do usuário por inteiro:** a tela como a gravação e os save
  states a mostram, com o boneco andando e as linhas trocáveis ao mesmo tempo.
- **O ritmo é o da [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md)**, em quadros do jogo; o relógio da janela converte
  para tempo, não o contrário.
- **Trocar um valor não reinicia o passo** — ou reinicia, se o jogo reinicia:
  mede-se na tela do jogo.
- **A câmera muda com a linha** desde a [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md): numa linha de cabeça o
  painel desenha o close-up, e a animação anda com a câmera que a linha pede.
- **Gate precisa de quadro determinístico.** O timer é para quem olha; o gate
  desenha `--frame N`.

---

- **Da [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md):** o
  ritmo está medido e o reprodutor existe — `anime.py --frame N` entrega a pose
  da passada N do ciclo, do arquivo, e `oracle.py --walk` escreve o ciclo em
  `work/looks-walk/slotN.json`. Três coisas que mudam o que esta task
  implementa: o ciclo tem **34 passadas** (17 quadros do arquivo, o segundo
  lado espelhado), a unidade é a **passada de desenho** e não o quadro de vídeo
  (a tela desenha a figura a cada dois ou três quadros, sem período em
  quadros), e a vaga de par em que uma passada abre é **propriedade do save
  state** — a janela lê a do plano, não uma constante. O `--frame N` recusa
  rodar sem o ciclo medido, então o gate determinístico que esta task pede já
  tem de onde sair.

---

## Objetivo

O painel da tela `LOOKS SET` anima a caminhada em loop, no ritmo do jogo, com a
figura montada e a câmera do jogo, enquanto as linhas continuam trocáveis.

---

## Critério de conclusão

- [ ] O painel anima por default; uma tecla pausa e outra anda um quadro,
      sem colidir com as setas das linhas; `--frame N` desenha parado.
- [ ] O ritmo: um ciclo da janela dura o período da [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md) convertido pela taxa
      de quadros do jogo, medida e escrita.
- [ ] O que acontece com o passo ao trocar um valor, medido no jogo e
      reproduzido.
- [ ] **O gate:** `confront.py --silhouette` em pelo menos oito N do ciclo,
      nos dois slots, dentro do limiar da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md).
- [ ] O `ui_check.py` confere que dois `--frame` diferentes dão imagens
      diferentes e o mesmo `--frame` duas vezes dá a mesma.

---

- **Da [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md):** qual
  câmera vale em cada linha já está resolvido —
  `scene.load_camera(slot, escala, linha)` lê o arquivo da linha quando ela
  tem um, e `scene.close_up_rows` diz quais têm. O que fica para a janela
  animada é o **giro**: nas cinco linhas de cabeça o jogo gira o modelo
  continuamente, e o arquivo guarda um instante dele — medido, a vista lida
  onde o jogo a constrói já está ~1° (61 a 80 de 4096) atrás da matriz da
  carga no mesmo quadro, e entre capturas o giro anda +18,3°, −16,9° e
  +16,9°. Uma janela animada terá de modelar esse giro, não interpolar entre
  dois arquivos.

## Log de Execução

*(preencher ao executar)*
