---
id: PES2-TASK-20
title: "Round-trip headless pelo mapa"
type: verificação
category: verificação
phase: 5
depends_on: ["PES2-TASK-19"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §0 (definição de pronto)"
status: pendente
---

# PES2-TASK-20: Round-trip pelo mapa

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §0, terceira condição da definição
  de pronto, e §5, Fase 5, terceiro item.
- **É a terceira das três condições do portão da Fase 6:** *"ler a imagem
  inteira pelo mapa, regravar sem editar nada, e o `.bin` sair byte a byte
  idêntico ao original."*

Já existe o irmão mais velho disto: `iso.py roundtrip` reescreve os 244
arquivos e a imagem sai idêntica (§5.1). Esse mede a **camada de setor**.
Este mede a **camada de mapa** — desempacotar cada campo e reempacotá-lo.

---

## Objetivo

`python3 tools/pes2/roundtrip_map.py <track1.bin>`: ler tudo pelo
`pes2_map.json`, regravar sem editar, `cmp` zero.

### Por que este é mais forte que o do `iso.py`

O `iso.py roundtrip` copia bytes: ele passaria mesmo se o mapa estivesse
inteiramente errado. Este desempacota e reempacota — e por isso pega:

- esquema de registro trocado (terminar em `NUL` um registro de 10 B cheio
  corrompe o vizinho, §1.10);
- contagem errada (ler 107 nomes invade a primeira abreviação, §1.13);
- ordem de armazenamento assumida em vez de medida (`SELECTC.BIN` guarda
  elenco de trás para frente, §3.3);
- campo de bits desempacotado com máscara errada.

### O controle negativo

Verde de round-trip não vale nada sem prova de que sabe ficar vermelho — é a
mesma regra que a §5.1 já aplicou ao `iso.py`, com o `negative`. Aqui:
alterar um campo pelo mapa tem de mudar **exatamente** os bytes que o mapa
prevê, em **todas** as cópias e em nenhum outro lugar.

### E o que o round-trip **não** deve consertar

Nada. A §6.7 é dura: preservar os 280 B de cauda EDC/ECC, e não "corrigir".
O jogo não confere, e corrigir destrói a própria comparação.

---

## Critério de conclusão

- [ ] Round-trip verde nas **duas** releases: `cmp` zero.
- [ ] Controle negativo: um campo alterado muda os bytes previstos, e só
      eles. Contagem exata, como o `iso.py negative` faz com o byte único em
      2002800.
- [ ] Registrado no `ctest` como parte de `pes2_image`, *skipped* sem imagem.
- [ ] EDC/ECC preservado — verificado, não presumido.

---

## Log de Execução

*(a preencher)*
