---
id: CORR-MCR-020
title: "Correção: um cobrador ou capitão fora do onze aparece na tela como 10, calado — o núcleo preserva o byte e a janela mostra outro"
type: correção
category: ui
status: pendente
depends_on: []
---

# CORR-MCR-020: o único lugar deste port que normaliza um valor em silêncio

## Problema identificado

A MCR-TASK-13 fixou o domínio dos cinco cobradores e do capitão em `0..10` — a
posição no onze inicial —, e a tela passou a oferecer isso:

```python
            spin.setRange(0, STARTERS - 1)      # ui/formation_view.py:283
        self.captain.setRange(0, STARTERS - 1)  # ui/formation_view.py:291
```

A divisão está **certa**: o núcleo valida byte (`0..255`) e preserva o que
achar, e o `0..10` é constrangimento de tela. O que falta é o que este ciclo faz
em todos os outros lugares da mesma classe — **dizer** que o valor não cabe, em
vez de mostrar outro:

- `domains.label()` devolve `UNNAMED` (`"?"`) para índice em faixa e sem nome, e
  **levanta** só fora de faixa — a MCR-TASK-11 escreveu em letras que "a tela
  precisa distinguir as duas coisas, senão um cartão legítimo vira erro";
- as duas cópias do dorsal em desacordo são **reportadas**, nunca reconciliadas
  (§1.5), porque reconciliar queimaria o melhor tripwire do port;
- o `formation.write` recusa papel fora da faixa **nomeando o byte armazenado**,
  desde a MCR-TASK-09.

Aqui não: um `QSpinBox` com máximo 10 recebendo 15 mostra **10**, sem rótulo,
sem tooltip, sem cor. A legenda ao lado diz "as positions in the starting 11
(0..10)" — declara o domínio, não que o cartão aberto está fora dele.

E o domínio, ao contrário dos rótulos, vem da **grade do editor de terceiro**
(`malla2`, seis colunas por onze linhas em `wte/re/zonas.md`), não do formato.
O experimento desta task produziu `0..5`; nada mediu o teto. Um cartão de outra
release, ou gravado por outra ferramenta, pode legitimamente cair fora.

## Evidência

Cópia da fixture com dois valores fora do onze — o `cmp` prova que o núcleo os
atravessa intactos:

```
$ # plantados numa cópia: CAPTAIN=15, kicker0=19
$ python3 tools/mcr/mcrio.py <cópia> --roundtrip
form 1: 0 byte(s) differ
form 2: 0 byte(s) differ
```

Abrindo essa cópia na janela:

```
model after the screen loaded it:  captain=15 kickers=[19, 7, 8, 7, 7]
captain spin shows: 10   kicker0 spin shows: 10
```

E o `Save` sobre ela devolve o arquivo **idêntico** — o valor não se perde:

```
$ cmp <cópia> <gravado pela tela>      # sem saída: iguais
captain: 15  kickers: [19, 7, 8, 7, 7]
```

Ou seja: **o dado está seguro e a tela mente sobre ele.** A captura da aba
Formation dessa cópia mostra `SF 10` e `CP 10` onde o cartão guarda 19 e 15,
sem nada dizendo que houve corte.

O caminho em que o valor **se perde** existe e é curto: mexer na seta de
qualquer uma das seis caixas dispara `valueChanged` a partir do 10 recortado, e
aí o 19 vira 10 ou 11. É edição do usuário, não gravação silenciosa — mas ele
edita a partir de um número que não é o do cartão.

## Causa raiz

O recorte do `QSpinBox` é usado como se fosse validação, e um widget que
recorta não tem como distinguir "o cartão diz 10" de "o cartão diz 15 e eu não
sei mostrar".

## Correção

### Arquivo: `tools/mcr/ui/formation_view.py`

Duas escolhas, e qualquer uma serve desde que a tela pare de calar:

1. **Alargar e marcar.** `setRange(0, 0xFF)`, que é o que o núcleo aceita, e
   pintar/rotular o valor quando ele sai de `0..10` — um sufixo no
   `setSuffix()` ou um `setToolTip` dizendo "outside the starting 11; the card
   holds this, and the upstream's grid only offers 0..10". Mantém o domínio
   medido como **orientação** e o cartão como verdade.
2. **Manter `0..10` e recusar-se a fingir.** Detectar na carga que o valor não
   cabe, desabilitar as seis caixas e mostrar o número real num rótulo ao lado,
   com a razão — a mesma forma que o `_open_byte` usava antes deste veredito.

A primeira é mais barata e mais fiel ao resto do port, que **mostra e anota** em
vez de esconder.

### A legenda

Acrescentar de onde vem o `0..10`: a grade `malla2` do editor de terceiro, seis
colunas por onze linhas, e não o formato. É a mesma ressalva que a linha ao lado
já faz sobre os nomes de papel.

### O caso vermelho

Registrar em `controls.py`, ou como passo do `ui_check.py`: abrir uma cópia com
`CAPTAIN=15`, exigir que a tela **relate** 15 — no valor ou no rótulo — e não
10. Sem ele o conserto não fica exercitado, e este é um defeito que só aparece
com um cartão que ninguém tem à mão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/ui/formation_view.py` | modificar |
| `tools/mcr/ui_check.py` ou `tools/mcr/controls.py` | modificar (o caso vermelho) |
| `docs/tasks/port-mcr/13-oraculo-e-veredito.md` | modificar (a contagem de controles, se mudar) |

## Verificação

- [ ] com uma cópia da fixture em que `CAPTAIN=15` e `kicker0=19`, a aba
      Formation **mostra 15 e 19**, ou diz que não os mostra e por quê
- [ ] a cópia gravada pela tela continua `cmp`-idêntica à de entrada quando
      nada foi editado
- [ ] o caso vermelho: com o conserto revertido, o passo novo fica vermelho
- [ ] `python3 tools/mcr/mcrio.py <cópia> --roundtrip` = 0 bytes nas duas formas
- [ ] `WE2002_MCR_CARD=… ctest -R mcr` = **3 de 3**; `make test` verde
- [ ] `python3 tools/mcr/controls.py` todos vermelhos
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
