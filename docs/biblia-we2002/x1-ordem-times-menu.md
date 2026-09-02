# X1 — Mudando a ordem ou retirando times do menu

> Dicas e manhas especiais. Voltar ao [índice geral](/docs/biblia-we2002/README.md).

**Programas usados nesse tutorial:** editor hexadecimal HEDIT.

## Introdução

Você pode pegar um patch na internet e não querer que os times fiquem naquela
ordem, ou pode não querer alguns times e retirá-los, deixando o lugar vazio. E
pra isso não precisa usar editores e métodos difíceis: basta fazer a mudança via
hexadecimal.

## Executando

**1)** Execute seu programa hexadecimal e mande abrir a ISO do jogo.

**2)** Aperte `CTRL+G` e indique que deseja ir para o offset **`0x2861B0`**.

**3)** Nesse offset você vai ver uma ordem assim:

```
00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E
```

Isso é uma numeração **hexadecimal** — ou seja, o `00` corresponde aqui ao
primeiro time (número 1), já o `0A` seria o correspondente ao nosso 10, o `0B` ao
nosso 11, e por aí vai.

**4)** Assim, no jogo original, o `00` corresponde à **IRLANDA**, o `01`
corresponde à **ESCÓCIA**, o `02` é o **GALES**, e por aí vai. O Brasil é o
quadragésimo segundo time, logo o **BRASIL é o `29`**.

A ordem é essa aqui:

| Posição | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Valor** | `00` | `01` | `02` | `03` | `04` | `05` | `06` | `07` | `08` | `09` | `0A` | `0B` | `0C` | `0D` |

| Posição | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Valor** | `0E` | `0F` | `10` | `11` | `12` | `13` | `14` | `15` | `16` | `17` | `18` | `19` | `1A` | `1B` |

| Posição | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 | 41 | 42 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Valor** | `1C` | `1D` | `1E` | `1F` | `20` | `21` | `22` | `23` | `24` | `25` | `26` | `27` | `28` | `29` |

| Posição | 43 | 44 | 45 | 46 | 47 | 48 | 49 | 50 | 51 | 52 | 53 | 54 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Valor** | `2A` | `2B` | `2C` | `2D` | `2E` | `2F` | `30` | `31` | `32` | `33` | `34` | `35` |

**5)** Agora, para mudar um time de lugar, é só identificar o número desse time e
trocá-lo com o que você desejar.

**6)** Já se o que você deseja é **excluir** o time, então no lugar do número dele
coloque:

| Valor | Efeito |
| --- | --- |
| `99` | o espaço daquele time fica **vazio** |
| `FF` | os times **se realinham**, sem deixar buracos ao retirar um time do meio |

---

Próxima seção: [X2 — Colocando os times do menu com nomes completos](/docs/biblia-we2002/x2-nomes-completos.md)
