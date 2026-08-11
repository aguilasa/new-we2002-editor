#!/usr/bin/env python3
"""Compara a tela do oraculo com a do port depois de carregar um time.

Da [WTE-TASK-25](../../docs/tasks/25-handlers-de-carga.md), criterio "tela
conferida contra o original para pelo menos 3 times distintos". Quem dirige os
dois lados e [`compara_tela.sh`](compara_tela.sh); este arquivo **mede**.

## Por que ele existe, e o que ele NAO tenta fazer

A conferencia de tela ja pagou o proprio custo: comparando Gales lado a lado,
apareceu que os tres campos de nome estavam trocados no port -- `names[0..2]`
em vez de `names[1], names[0], names[2]`. Compilava, nao quebrava teste nenhum
e estava errado. Nenhuma outra regra deste projeto pegaria isso.

Mas nem tudo na tela se compara por maquina. Os dois lados usam **fontes
diferentes** (o oraculo roda sob Wine com as substitutas do Fontconfig, o port
usa a fonte que o gtk2 escolher), entao texto renderizado nao bate pixel a
pixel nem deveria. O proprio enunciado da task pede "comparacao humana dos
campos preenchidos (nao de pixel)".

Entao a divisao e esta, e ela e deliberada:

| O que | Como |
|---|---|
| as cinco barras de forca | **medido**, em pixels, e reprova se divergir |
| os campos de texto | montagem lado a lado, para olho humano |

A barra e o alvo certo para a parte medida: a largura e `11*v + 9` com `v`
vindo do dado, entao ela e **numero do jogo virado pixel**. Se o port pegou o
time errado, o vetor errado ou o campo errado, a largura muda.

## O indice tem de ser confirmado nos dois lados

Foi o que invalidou duas das tres medicoes da setima passagem: os dois lados
receberam numero diferente de `Down`, o port foi parar em `78 Ajax` e a
comparacao virou lixo. Aqui o indice esperado e argumento, e o `compara_tela.sh`
confirma o do port pelo log de disparo antes de chamar este script.

Uso:

    python3 wte/tools/compara_tela.py <oraculo.png> <port.png> \\
        --indice 2 --saida <dir>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

GENERATOR = "wte/tools/compara_tela.py"

# Faixa de cor do preenchimento da barra. O DFM desenha um degrade laranja
# sobre fundo azul-escuro; o que se conta e o laranja.
def e_preenchimento(p: tuple[int, int, int]) -> bool:
    r, g, b = p[0], p[1], p[2]
    return r > 150 and g > 90 and b < 90


# Janela horizontal em que as barras vivem, em coordenadas do recorte da
# janela. Larga o bastante para as cinco e estreita o bastante para nao pegar
# o uniforme 2D, que tambem tem laranja.
FAIXA_X = (80, 230)

# Altura minima de uma banda para ela contar como barra, em pixels. Abaixo
# disso e borda ou artefato de recorte -- na setima passagem uma linha de 1 px
# entrou na lista e desalinhou a comparacao.
ALTURA_MINIMA = 4

# Largura minima para uma banda contar como barra. A barra vazia tem
# exatamente 9 px (`11*0 + 9`), entao qualquer coisa mais estreita e outra
# coisa -- o icone laranja do botao "Sobre..." cai dentro da faixa X e foi o
# que fez a sexta banda aparecer na primeira medicao.
LARGURA_MINIMA = 9

# Folga, so para MENOS, ao confrontar a largura medida com o valor da camada de
# dados. A barra e um degrade e a ponta escura nao passa no teste de cor, entao
# a medida encurta nas barras mais largas -- 4 px no unico caso visto ate aqui
# (time 63, `bar_attack = 9`, previsto 108, medido 104 nos dois lados). NAO se
# aplica a comparacao entre os dois lados, que continua exata.
TOLERANCIA_PX = 4

BARRAS = 5
NOMES_DAS_BARRAS = ("ataque", "defesa", "equipe", "velocidade", "tecnica")


class TelaError(Exception):
    """Medicao impossivel, sempre dizendo o que faltou."""


def carrega(caminho: Path):
    try:
        from PIL import Image
    except ImportError as exc:      # pragma: no cover - depende do ambiente
        raise TelaError(
            "PIL/Pillow nao instalado -- sem ele nao ha como medir tela") from exc
    if not caminho.is_file():
        raise TelaError(f"{caminho}: nao existe")
    return Image.open(caminho).convert("RGB")


def bandas(img) -> list[tuple[int, int, int]]:
    """As bandas horizontais de preenchimento: `(topo, base, largura)`.

    A largura e o **maior** valor das linhas da banda, e nao o da linha do
    meio: a borda da barra e mais estreita, e amostrar uma linha so torna a
    medida dependente de onde a banda comecou.
    """
    largura, altura = img.size
    x0, x1 = FAIXA_X[0], min(FAIXA_X[1], largura)
    por_linha = []
    for y in range(altura):
        por_linha.append(sum(1 for x in range(x0, x1)
                             if e_preenchimento(img.getpixel((x, y)))))
    saida = []
    inicio = None
    for y, n in enumerate(por_linha + [0]):
        if n > 0 and inicio is None:
            inicio = y
        elif n == 0 and inicio is not None:
            larg = max(por_linha[inicio:y])
            if y - inicio >= ALTURA_MINIMA and larg >= LARGURA_MINIMA:
                saida.append((inicio, y - 1, larg))
            inicio = None
    return saida


def larguras(img, rotulo: str) -> list[int]:
    achadas = bandas(img)
    if len(achadas) != BARRAS:
        raise TelaError(
            f"{rotulo}: achei {len(achadas)} banda(s) de barra, esperava "
            f"{BARRAS}. Ou o recorte pegou a janela errada, ou o time nao "
            f"chegou a ser carregado -- sem as cinco nao ha o que comparar.")
    return [largura for _t, _b, largura in achadas]


def valor_da_barra(largura: int) -> float | None:
    """De volta ao valor do jogo: a largura e `11*v + 9`.

    Devolve `None` quando a conta nao fecha em inteiro. Nao e detalhe: o time
    63 mede 104 px, que dariam `v = 8,64`, e barra do jogo e inteira. Ou o
    preenchimento e cortado pelo container acima de certa largura, ou a
    contagem perde pixel na borda -- **os dois lados medem o mesmo 104**, entao
    nao e defeito do port, e imprimir `8,63636` como "valor do jogo" seria
    afirmar o que nao se mediu.
    """
    v, resto = divmod(largura - 9, 11)
    return v if resto == 0 else None


# Onde o `dump_estado.pas` guarda cada barra, e como o indice do combo vira
# indice de vetor. Os 0..62 sao `teams`; de 63 em diante sao `ml_teams`, e a
# contiguidade foi conferida byte a byte na terceira passagem da WTE-TASK-25.
TIMES_NACIONAIS = 63
CHAVES_DA_BARRA = ("bar_attack", "bar_defence", "bar_power", "bar_speed",
                   "bar_technique")


def le_dump(caminho: Path, indice: int) -> list[int]:
    """As cinco barras do time `indice`, lidas do dump da camada de dados.

    O formato e o do `dump_estado.pas`: `chave = valor`, uma por linha.
    """
    if indice < TIMES_NACIONAIS:
        prefixo = f"teams[{indice}]."
    else:
        prefixo = f"ml_teams[{indice - TIMES_NACIONAIS}]."
    valores: dict[str, int] = {}
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        chave, _, valor = linha.partition(" = ")
        if chave.startswith(prefixo):
            valores[chave[len(prefixo):]] = valor.strip()
    faltando = [c for c in CHAVES_DA_BARRA if c not in valores]
    if faltando:
        raise TelaError(
            f"{caminho}: o dump nao traz {', '.join(faltando)} de {prefixo} "
            f"-- ou o indice esta fora, ou o dump e de outra versao")
    return [int(valores[c]) for c in CHAVES_DA_BARRA]


def confere_contra_dump(m: dict, caminho: Path) -> dict:
    """A terceira ponta: tela -> valor -> camada de dados.

    O `compara_tela` ja mostra que os dois lados desenham o mesmo pixel. Isso
    provaria paridade entre eles mesmo se AMBOS estivessem lendo o time
    errado. Confrontar a largura com o que o `we2002_core` carregou fecha o
    triangulo: a tela do port vem do dado, e o dado e o do jogo.

    Devolve `{"erros": [...], "curtas": [...]}`.

    **A medida e proxy, e a folga tem tamanho medido.** A barra e um `TImage`
    com um degrade laranja de 117 px, e o que se conta e o pixel que passa no
    teste de cor. Na ponta escura do degrade o pixel nao passa, entao a medida
    fica um pouco CURTA nas barras mais largas: o time 63 tem
    `bar_attack = 9`, que por `11*v + 9` daria 108 px, e os dois lados medem
    104. Todos os outros valores conferidos ate aqui batem exatos.

    Por isso a folga e de `{TOLERANCIA_PX}` px, so para MENOS, e so quando os
    dois lados medem o mesmo. Comparar medida com medida continua exato -- os
    dois desenham o mesmo degrade --; e comparar medida com dado que precisa da
    folga. Diferenca maior que isso e erro, e foi assim que o teste
    `test_dado_diferente_reprova` ficou de pe.
    """
    do_dump = le_dump(caminho, m["indice"])
    erros, curtas = [], []
    for i, nome in enumerate(NOMES_DAS_BARRAS):
        previsto = 11 * do_dump[i] + 9
        medido = m["oraculo"][i]
        if medido == previsto:
            continue
        if (0 < previsto - medido <= TOLERANCIA_PX
                and m["oraculo"][i] == m["port"][i]):
            curtas.append(
                f"{nome}: dado {do_dump[i]} previa {previsto} px e os dois "
                f"lados medem {medido} -- {previsto - medido} px de cauda do "
                f"degrade fora do teste de cor")
        else:
            erros.append(
                f"{nome}: dado {do_dump[i]} previa {previsto} px, oraculo "
                f"{medido}, port {m['port'][i]}")
    return {"erros": erros, "curtas": curtas}


def compara(oraculo, port, indice: int) -> dict:
    a = larguras(oraculo, "oraculo")
    b = larguras(port, "port")
    diferencas = [
        {"barra": NOMES_DAS_BARRAS[i], "oraculo": a[i], "port": b[i]}
        for i in range(BARRAS) if a[i] != b[i]]
    return {"indice": indice, "oraculo": a, "port": b,
            "diferencas": diferencas,
            "valores": [valor_da_barra(x) for x in a]}


def montagem(oraculo, port, destino: Path) -> None:
    """Empilha os dois recortes, para a parte que so o olho decide."""
    from PIL import Image
    largura = max(oraculo.width, port.width)
    alvo = Image.new("RGB", (largura, oraculo.height + port.height + 8),
                     (255, 255, 255))
    alvo.paste(oraculo, (0, 0))
    alvo.paste(port, (0, oraculo.height + 8))
    alvo.save(destino)


def relata(m: dict) -> int:
    print(f"compara_tela: time {m['indice']}")
    print(f"  barras oraculo: {m['oraculo']}")
    print(f"  barras port   : {m['port']}")
    print("  valores do jogo: "
          + ", ".join(f"{n}=" + ("?" if v is None else f"{v:g}")
                      for n, v in zip(NOMES_DAS_BARRAS, m["valores"])))
    if "dump" in m:
        for r in m["dump"]["curtas"]:
            print("  curta: " + r)
        if m["dump"]["erros"]:
            print("DIVERGE da camada de dados:", file=sys.stderr)
            for d in m["dump"]["erros"]:
                print("  " + d, file=sys.stderr)
            return 1
        n = BARRAS - len(m["dump"]["curtas"])
        print(f"  a tela bate com o we2002_core em {n} de {BARRAS} barras"
              + (" (o resto curto pelo degrade, igual nos dois lados)"
                 if m["dump"]["curtas"] else ""))
    if m["diferencas"]:
        print("DIVERGE:", file=sys.stderr)
        for d in m["diferencas"]:
            print(f"  {d['barra']}: oraculo {d['oraculo']} px, "
                  f"port {d['port']} px", file=sys.stderr)
        return 1
    print(f"  PASSOU: as {BARRAS} barras batem em pixel")
    return 0


def sintetica(larguras_px: list[int]):
    """Uma tela de mentira com as bandas pedidas, para o `--check`."""
    from PIL import Image
    alt = 10 + len(larguras_px) * 20
    img = Image.new("RGB", (FAIXA_X[1] + 20, alt), (0, 0, 128))
    for i, larg in enumerate(larguras_px):
        topo = 10 + i * 20
        for y in range(topo, topo + 12):
            for x in range(FAIXA_X[0], FAIXA_X[0] + larg):
                img.putpixel((x, y), (255, 160, 0))
    return img


def autoteste() -> int:
    """`--check`: mede uma tela sintetica e confere que o numero volta.

    Este script nao gera arquivo commitado, entao nao ha o que comparar com o
    disco -- mas entrar na bateria sem medir nada seria alvo verde vazio. O que
    ele prova e que a deteccao de banda e a aritmetica `11*v + 9` continuam de
    pe na maquina de quem roda.
    """
    esperado = [9, 20, 64, 75, 141]
    try:
        img = sintetica(esperado)
        lidas = larguras(img, "sintetica")
    except TelaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    if lidas != esperado:
        print(f"ERRO: medi {lidas}, plantei {esperado}", file=sys.stderr)
        return 1
    valores = [valor_da_barra(x) for x in lidas]
    if valores != [0, 1, 5, 6, 12]:
        print(f"ERRO: `11*v + 9` invertido deu {valores}", file=sys.stderr)
        return 1
    print(f"compara_tela: {len(esperado)} bandas sinteticas medidas, "
          f"valores {valores}")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--check"]:
        return autoteste()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("oraculo", type=Path)
    ap.add_argument("port", type=Path)
    ap.add_argument("--indice", type=int, required=True)
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--dump", type=Path,
                    help="saida do dump_estado.pas, para confrontar a largura "
                         "invertida com o que a camada de dados carregou")
    args = ap.parse_args(argv)
    try:
        o = carrega(args.oraculo)
        p = carrega(args.port)
        m = compara(o, p, args.indice)
        if args.saida:
            args.saida.mkdir(parents=True, exist_ok=True)
            destino = args.saida / f"time-{args.indice}-lado-a-lado.png"
            montagem(o, p, destino)
            print(f"  montagem: {destino}")
        if args.dump:
            m["dump"] = confere_contra_dump(m, args.dump)
    except TelaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return relata(m)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
