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
| o estado de habilitacao | **medido**, por mudanca de aparencia (`--habilitacao`) |
| os campos de texto, os 23 dorsais, a lista de jogadores | montagem lado a lado, para olho humano |

## O criterio enumera cinco grupos, e o recorte medido cobre dois

A [CORR-WTE-057](../../docs/tasks/CORR-WTE-057.md) achou o buraco: o recorte de
520x240 termina em y 240, e a `lista_jugadores_1` esta em y 392 e os
`dorsal1..23` em y 432. Tres passagens marcaram o criterio `[x]` sem que os dois
grupos tivessem sido olhados uma vez. A montagem passou a sair da janela
**inteira**, e `confere_cobertura` reprova a montagem que nao os alcance --
recorte curto volta a ser erro dito, nao grupo silenciosamente ausente.

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
import re
from collections import Counter

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

# --------------------------------------------------------- estado de controle --
#
# As coordenadas sao de CLIENTE do `MainForm`, somadas pela cadeia de pais do
# `wte/re/dfm/MainForm.dfm` -- `GroupBox4` em (216, 8), `grupo_barras` em
# (8, 72), `GroupBox1` em (8, 320). O `Left`/`Top` do proprio formulario
# (132, 72) NAO entra: e posicao de tela, nao deslocamento de filho. Somar o do
# formulario foi o primeiro erro desta medicao, e ele passa despercebido porque
# o resultado continua parecendo coordenada.
#
# `ANCORA` calibra a captura: `barra0` esta em (92, 90) no DFM, e a primeira
# banda laranja detectada da a mesma coisa na imagem. A diferenca e o
# deslocamento do cliente dentro da janela capturada -- medido em 2026-08-11:
# (0, 0) no oraculo e (6, 6) no port, que e a borda que o gtk2 desenha e o Wine
# nao. Sem calibrar, todo retangulo do port sai 6 px torto.
ANCORA = (92, 90)

# **A deriva, e por que a faixa medida termina em 240.** O deslocamento do port
# NAO e constante: o gtk2 desenha cada linha um pouco mais alta que o Win32, e
# o erro se acumula para baixo. Medido na mesma captura de 2026-08-11, pelos
# topos das cinco barras e pela faixa dos dorsais:
#
#     barra0  y  90 -> deriva  6      barra3  y 138 -> deriva  8
#     barra1  y 106 -> deriva  6      barra4  y 154 -> deriva  8
#     barra2  y 122 -> deriva  7      dorsais y 432 -> deriva 21
#
# Ate y 240 a deriva cabe em 3 px sobre controle de 16 a 25 px de altura, e o
# retangulo do DFM ainda nomeia o controle certo. Depois dela nao: 21 px de
# deriva sobre um botao de 25 mede a vizinhanca. Por isso o que esta abaixo e
# declarado `fora_da_faixa` e vai para o olho humano na montagem -- e nao
# medido com regua que ali nao vale.
FAIXA_CALIBRADA_Y = 240

# A altura do recorte `topo` que o `compara_tela.sh` corta, e a janela em que a
# ancora e procurada. Tem de casar com o `REC_H` de la.
REC_ALTURA_MEDIDA = 240

# Grupos:
#   segue_nacional  o handler faz `.Enabled := nacional` -- tem de MUDAR de
#                   aparencia entre um time nacional e o time-modelo
#   sempre_ligado   `.Enabled := True` incondicional -- NAO pode mudar. Os
#                   `etiq_nombreN` sao a assimetria medida do original: o campo
#                   segue `nacional`, o rotulo ao lado nao
#   pendente_32     `.Visible := nacional`, mas quem DESENHA e a WTE-TASK-29.
#                   Medido e relatado, nunca reprova
#   glifo_cinza     `.Enabled := nacional` roda nos dois, mas o glifo e
#                   INVARIANTE sob o `gdeDisabled` da LCL -- desenhado so com
#                   preto e branco puros sobre a cor transparente, e grayscale
#                   nao mexe em pixel com R=G=B. O estado logico esta certo dos
#                   dois lados; o que nao aparece e o desenho. Divergencia
#                   deliberada da WTE-TASK-35, medida pela CORR-WTE-060 e
#                   travada pelo `check_glifos_disabled.py`. Medido e relatado,
#                   nunca reprova
#   conteudo        o texto muda junto com o time, entao mudanca de pixel nao
#                   distingue habilitacao de conteudo. Olho humano, na montagem
#   fora_da_faixa   abaixo de `FAIXA_CALIBRADA_Y`, onde a deriva do port passa
#                   de 20 px. Olho humano, pelo motivo dito ali em cima
CONTROLES = {
    "sel_barra0":           (16,  88,  73, 16, "segue_nacional"),
    "sel_barra1":           (16, 104,  73, 16, "segue_nacional"),
    "sel_barra2":           (16, 120,  73, 16, "segue_nacional"),
    "sel_barra3":           (16, 136,  73, 16, "segue_nacional"),
    "sel_barra4":           (16, 152,  73, 16, "segue_nacional"),
    "track_barra":          (96, 184, 105, 25, "segue_nacional"),
    "boton_barras2iso":     (16, 184,  73, 25, "segue_nacional"),
    "iguala_nombres":      (344, 184,  73, 25, "glifo_cinza"),
    "boton_nombres2iso":   (432, 184,  73, 25, "segue_nacional"),
    "colorear":            (224, 184,  97, 25, "segue_nacional"),
    "etiq_nombre1":        (344,  64,  41, 17, "sempre_ligado"),
    "etiq_nombre2":        (344, 104,  41, 17, "sempre_ligado"),
    "etiq_nombre3":        (344, 144,  41, 17, "sempre_ligado"),
    "boton_mcr":            (16, 248,  25, 25, "fora_da_faixa"),
    "boton_dialogo_tex":   (480, 248,  25, 25, "fora_da_faixa"),
    "grabar_memory":        (96, 280,  25, 25, "fora_da_faixa"),
    "grabar_camiseta":     (400, 280,  25, 25, "fora_da_faixa"),
    "parriba":             (160, 336,  33, 49, "fora_da_faixa"),
    "mostrar_estrategia_1": (16, 360,  25, 21, "fora_da_faixa"),
    "mostrar_jugador_1":    (16, 392,  25, 21, "fora_da_faixa"),
    "bandera":             (232,  36,  80, 48, "pendente_32"),
    "home1":               (232, 104,  80, 42, "pendente_32"),
    "home2":               (232, 146,  80, 22, "pendente_32"),
    "banderita1":          (122, 339,  30, 12, "fora_da_faixa"),
    "edit_nombre1":        (392,  64, 113, 21, "conteudo"),
    "edit_nombre2":        (392, 104, 113, 21, "conteudo"),
    "edit_nombre3":        (392, 144,  33, 21, "conteudo"),
    "base_team":            (16, 336,  98, 23, "conteudo"),
    "lista_jugadores_1":    (48, 392, 129, 21, "conteudo"),
}

# O `punto` (TShape de 2x2 em (312, 125)) fica de fora: dois pixels nao
# sobrevivem a calibracao de 1 px, e ele e da mesma WTE-TASK-29 dos outros.

# Quantos pixels precisam diferir para a regiao contar como mudada. Zero seria
# certo em teoria -- a mesma janela, o mesmo lado, renderizacao determinista --
# e 4 e a folga contra 1 px de calibracao numa borda.
LIMIAR_MUDANCA = 4

# O ultimo pixel que a montagem TEM de conter, em coordenadas de cliente: a base
# dos `dorsal1..23` (y 432 + 17). Abaixo disso o criterio da WTE-TASK-25 fica
# com dois grupos por olhar, que foi o defeito da CORR-WTE-057.
COBERTURA_MINIMA_Y = 449


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


def confere_editada(m: dict, barra: int, valor: int) -> list[str]:
    """A barra que o roteiro editou tem de ler `valor` nos DOIS lados.

    Da WTE-TASK-26, modo `--edicao` do `compara_tela.sh`. Sem esta conferencia
    o modo passaria com a barra intacta: `compara()` so exige que os dois lados
    desenhem a mesma largura, e uma edicao que nao aconteceu em lado nenhum
    desenha a mesma largura muito bem. E o par da WTE-TASK-20 -- concordam, **e**
    fizeram alguma coisa.

    A previsao usa `11*v + 9`, a mesma aritmetica da carga; que ela seja mesmo
    a mesma no binario e o `check_barras.py` quem prova.
    """
    previsto = 11 * valor + 9
    erros = []
    for lado in ("oraculo", "port"):
        medido = m[lado][barra]
        if medido != previsto:
            erros.append(
                f"{NOMES_DAS_BARRAS[barra]} no {lado}: a edicao previa "
                f"{valor} ({previsto} px) e a tela mede {medido} px")
    return erros


def confere_contra_dump(m: dict, caminho: Path, editada: int | None = None) -> dict:
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
        if i == editada:
            # A barra editada DEVE divergir do dump: o dump e do estado
            # carregado, e a edicao aconteceu depois. Quem a julga e o
            # `confere_editada`. As outras quatro continuam ancoradas -- e sao
            # elas que provam que a edicao nao respingou.
            continue
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



# --------------------------------------------- os tres campos de nome --

LFM_MAINFORM = Path(__file__).resolve().parents[1] / "forms/ep2002_mainform.lfm"

# Quanto se descarta da borda do `TEdit` antes de procurar glifo. **A primeira
# versao nao descartava nada e o veredito saiu verde medindo a BORDA:** os tres
# campos deram largura de tinta igual a largura deles, e a coincidencia passou
# por "os dois lados concordam". Tres pixels tiram a moldura dos dois
# widgetsets sem comer a primeira coluna de glifo.
BORDA = 3

# Quanto um pixel precisa se afastar do fundo do campo para contar como tinta.
# Frouxo de proposito: o que se mede e ONDE ha glifo, nao a cor dele.
LIMIAR_TINTA = 60

CAMPOS_DE_NOME = ("edit_nombre1", "edit_nombre2", "edit_nombre3")

# Quanto os dois lados podem diferir na largura da tinta de um campo.
#
# Nao e folga escolhida por conveniencia: e **meio glifo**. O que se mede aqui e
# quantos caracteres o filtro deixou passar, e um caractere a mais ou a menos
# vale 7 a 8 px nesta fonte -- entao 4 px pega qualquer divergencia de contagem
# e nao pega o tremor de renderizacao entre gtk2 e Win32. Medido em 2026-08-18:
# com os dois lados de acordo a diferenca foi de 0 a 1 px; com um caractere de
# diferenca, 10 px.
TOLERANCIA_PX = 4


def retangulos_do_lfm(nomes) -> dict:
    """Os retangulos dos controles, somados pela cadeia de pais do `.lfm`.

    **Lidos, nao digitados.** A primeira versao trazia os quatro numeros de cada
    campo escritos a mao e um deles estava errado -- o `edit_nombre3` tem 33 px
    de largura, nao 113 --, o que fez a regua medir a moldura de um campo que
    nem existia daquele tamanho. O formulario raiz fica de fora da soma: o
    `Left`/`Top` dele e posicao de tela.
    """
    pilha, fora = [], {}
    for linha in LFM_MAINFORM.read_text(encoding="utf-8",
                                        errors="replace").splitlines():
        ind = len(linha) - len(linha.lstrip())
        corte = linha.strip()
        m = re.match(r"object (\w+): (\w+)", corte)
        if m:
            while pilha and pilha[-1][0] >= ind:
                pilha.pop()
            pilha.append([ind, m.group(1), 0, 0, 0, 0])
        elif corte == "end":
            while pilha and pilha[-1][0] >= ind:
                pilha.pop()
        elif pilha:
            m2 = re.match(r"(Left|Top|Width|Height) = (-?\d+)", corte)
            if m2:
                pilha[-1][{"Left": 2, "Top": 3,
                           "Width": 4, "Height": 5}[m2.group(1)]] = \
                    int(m2.group(2))
            if pilha[-1][1] in nomes and corte.startswith("Height"):
                fora[pilha[-1][1]] = (sum(e[2] for e in pilha[1:]),
                                      sum(e[3] for e in pilha[1:]),
                                      pilha[-1][4], pilha[-1][5])
    faltando = set(nomes) - set(fora)
    if faltando:
        raise TelaError(f"{LFM_MAINFORM.name}: nao achei {sorted(faltando)}")
    return fora


def tinta(img, rect, off: tuple[int, int], rotulo: str) -> tuple[int, int]:
    """(largura da tinta, largura util do campo) dentro de um `TEdit`.

    **Nao se compara o texto pixel a pixel entre os dois lados, e nao e
    desleixo:** gtk2 e Win32 nao desenham a mesma fonte, o `MS Sans Serif` do
    original nem esta instalado, e um diff estrito acusaria divergencia em
    qualquer campo com letra dentro. O que sobrevive a troca de widgetset e a
    PROPRIEDADE que o filtro impoe -- quantos caracteres passaram --, e a
    largura da tinta e o proxy dela que se le do pixel.

    O fundo sai da propria regiao, pela cor mais frequente: campo de `TEdit` e
    quase todo fundo, e assim a medida nao depende de saber qual creme cada
    lado pinta.
    """
    x, y, w, h = rect
    dentro = (x + BORDA, y + BORDA, w - 2 * BORDA, h - 2 * BORDA)
    r = regiao(img, dentro, off, rotulo)
    px = list(r.getdata())
    fundo, quantos = Counter(px).most_common(1)[0]
    # Se a cor mais frequente nao for maioria, ela pode nao ser o fundo -- e ai
    # a medida se INVERTE em silencio, medindo o buraco entre os glifos. Num
    # `TEdit` de 11 px o texto nunca chega perto de metade; se chegar, a regiao
    # nao e um campo de texto e a leitura nao vale.
    if quantos * 2 <= len(px):
        raise TelaError(
            f"{rotulo}: a cor mais frequente ocupa {quantos} de {len(px)} "
            f"pixels e nao da para trata-la como fundo")
    colunas = [cx for cx in range(r.width)
               if any(sum(abs(a - b)
                          for a, b in zip(px[cy * r.width + cx], fundo))
                      > LIMIAR_TINTA for cy in range(r.height))]
    largura = 0 if not colunas else colunas[-1] - colunas[0] + 1
    return largura, r.width


def compara_nomes(oraculo, port) -> dict:
    """As larguras de tinta dos tres campos, nos dois lados."""
    rects = retangulos_do_lfm(CAMPOS_DE_NOME)
    medida = {}
    for lado, img in (("oraculo", oraculo), ("port", port)):
        off = calibra(img, lado)
        medida[lado] = {n: tinta(img, rects[n], off, f"{lado}/{n}")
                        for n in CAMPOS_DE_NOME}
    erros = []
    for lado, m in medida.items():
        for nome, (largura, util) in m.items():
            if largura == 0:
                erros.append(f"{lado}: {nome} sem texto -- a digitacao nao "
                             f"chegou, ou o filtro comeu tudo")
            elif largura >= util:
                # A guarda que faltava na primeira versao. Tinta ocupando o
                # campo inteiro nao distingue "texto transbordou" de "a moldura
                # entrou na conta", e as duas leituras dao verde.
                erros.append(f"{lado}: {nome} tem tinta em toda a largura util "
                             f"({largura} de {util} px) -- ou o texto "
                             f"transbordou, ou a borda entrou na medida")
    # A comparacao que importa e ORACULO CONTRA PORT, campo a campo.
    #
    # A primeira versao tinha, alem desta, duas regras sobre a forma da tela --
    # "nombre1 e nombre2 tem o mesmo filtro, logo a mesma tinta" e "nombre3 tem
    # de sair mais curto". A segunda vale; **a primeira estava errada**: os dois
    # campos tem o mesmo filtro e `MaxLength` DIFERENTES (5 e 19), e a regra
    # reprovava o oraculo por se comportar como ele e. Regra estrutural
    # inventada sobre o app reprova o app; a comparacao entre os lados nao
    # inventa nada.
    if not erros:
        for nome in CAMPOS_DE_NOME:
            o, pt = medida["oraculo"][nome][0], medida["port"][nome][0]
            if abs(o - pt) > TOLERANCIA_PX:
                erros.append(
                    f"{nome}: {o} px de tinta no oraculo contra {pt} no port "
                    f"-- diferenca de {abs(o - pt)} px, mais que um glifo")
    return {"medida": medida, "erros": erros}


def relata_nomes(r: dict) -> int:
    for lado in ("oraculo", "port"):
        m = r["medida"][lado]
        print(f"  tinta {lado:8} " + "  ".join(
            f"{n[-1]}={m[n][0]}/{m[n][1]}px" for n in CAMPOS_DE_NOME))
    if r["erros"]:
        print("REPROVOU:")
        for e in r["erros"]:
            print("  " + e)
        return 1
    print("  PASSOU: os tres filtros de nome se comportam igual nos dois lados")
    return 0


# ------------------------------------------------ calibracao e cobertura --
def calibra(img, rotulo: str) -> tuple[int, int]:
    """`(dx, dy)` do cliente dentro da janela capturada, pela ancora `barra0`.

    O oraculo da (0, 0) e o port da (6, 6) mais ou menos, e o "mais ou menos" e
    o problema: ISTO NAO E UM DESLOCAMENTO, E UMA ESCALA.

    A explicacao antiga -- "o gtk2 desenha uma borda que o Wine nao desenha" --
    foi escrita na segunda passagem da WTE-TASK-26 a partir de uma amostra perto
    do topo da janela, e ela nao sobrevive a medicao da decima terceira: o
    `wte.lpr` faz `Application.Scaled := True`, e a janela do port sai
    **1,0421 vez** a do projeto. Medido no `:99`: 544x495 contra os 522x475 que
    o `.lfm` declara, e os dois quocientes batem na quarta casa.

    E isso explica o que a borda nao explicava. A propria segunda passagem
    registrou que "a diferenca cresce descendo a janela" e escolheu `y = 200`
    como intersecao para a `track_barra`; o controle esta em `y = 192` no
    projeto, e `192 * 0,0421 = 8,1` -- exatamente a deriva observada. Borda e
    constante; escala nao.

    Enquanto o alvo for um controle so, perto do topo, o deslocamento constante
    passa. Para um recorte grande -- a ficha do jogador, com 16 barrinhas cuja
    LARGURA e o que se mede -- ele deixa de passar: uma largura de `7*v + 8`
    chega ao port multiplicada por 1,0421, e a comparacao acusaria divergencia
    onde ha so escala.
    """
    topo = img.crop((0, 0, min(FAIXA_X[1] + 20, img.width),
                     min(REC_ALTURA_MEDIDA, img.height)))
    achadas = bandas(topo)
    if not achadas:
        raise TelaError(
            f"{rotulo}: nenhuma banda de barra no canto superior -- sem a "
            f"ancora `barra0` nao ha como calibrar o recorte")
    y0 = achadas[0][0]
    linha = min(y0 + 3, topo.height - 1)
    xs = [x for x in range(FAIXA_X[0], min(FAIXA_X[1], topo.width))
          if e_preenchimento(topo.getpixel((x, linha)))]
    if not xs:
        raise TelaError(f"{rotulo}: a banda da ancora nao tem pixel na linha "
                        f"{linha} -- calibracao impossivel")
    return min(xs) - ANCORA[0], y0 - ANCORA[1]


def confere_cobertura(img, rotulo: str, off: tuple[int, int]) -> None:
    """A montagem tem de alcancar os `dorsal1..23`, ou nao ha o que olhar.

    O criterio da WTE-TASK-25 enumera cinco grupos; o recorte de 520x240 cobria
    dois deles e ninguem notou por tres passagens. Aqui recorte curto vira erro
    dito.
    """
    preciso = COBERTURA_MINIMA_Y + off[1]
    if img.height < preciso:
        raise TelaError(
            f"{rotulo}: a captura tem {img.height} px de altura e a base dos "
            f"`dorsal1..23` esta em {preciso} -- os 23 numeros de camisa e a "
            f"`lista_jugadores_1` ficariam de fora da montagem")


# --------------------------------------------- o estado de habilitacao --
def regiao(img, rect, off: tuple[int, int], rotulo: str):
    x, y, w, h = rect[0] + off[0], rect[1] + off[1], rect[2], rect[3]
    if x < 0 or y < 0 or x + w > img.width or y + h > img.height:
        raise TelaError(
            f"{rotulo}: o retangulo ({x}, {y}, {w}, {h}) cai fora da captura "
            f"de {img.width}x{img.height}")
    return img.crop((x, y, x + w, y + h))


def difere(a, b, rect, off_a, off_b, rotulo: str) -> int:
    """Pixels diferentes na MESMA regiao de duas capturas do MESMO lado."""
    ra = regiao(a, rect, off_a, rotulo + "/a")
    rb = regiao(b, rect, off_b, rotulo + "/b")
    return sum(1 for pa, pb in zip(ra.getdata(), rb.getdata()) if pa != pb)


def confere_faixa() -> None:
    """Nenhum controle medido pode cair abaixo de `FAIXA_CALIBRADA_Y`.

    Guarda contra o modo de falha mais provavel desta tabela: alguem acrescenta
    um controle de y grande, a regua nao vale la, e o veredito sai com cara de
    medida.
    """
    fora = [n for n, r in CONTROLES.items()
            if r[4] in ("segue_nacional", "sempre_ligado", "pendente_32")
            and r[1] + r[3] > FAIXA_CALIBRADA_Y]
    if fora:
        raise TelaError(
            f"{', '.join(sorted(fora))}: medidos, mas abaixo de y "
            f"{FAIXA_CALIBRADA_Y}, onde a deriva do port passa de 20 px. "
            f"Ou o grupo vira `fora_da_faixa`, ou a calibracao passa a ter "
            f"duas ancoras")


# ------------------------------------------------- a bandeira e o uniforme --
# Os tres `TImage` que a WTE-TASK-29 desenha. Ao contrario dos campos de texto,
# estes SE COMPARAM pixel a pixel: nao ha fonte no meio, e o conteudo e um
# bitmap de 8 bpp com a paleta trocada -- o mesmo arquivo dos dois lados, a
# mesma paleta, o mesmo esticamento. Divergencia aqui e cor errada, ponto.
RENDER = ("bandera", "home1", "home2")


def retangulo_do_render(nome: str, rects: dict, indice: int):
    """O retangulo de um dos tres, com o remanejo que o handler faz.

    O `lista_equiposChange` move e alarga o `home1` para indice > 62 -- clube de
    Master League e selecao classica usam camisa de 51 px, e o controle vai para
    `Left = 7, Width = 100`. Ler so o `.lfm` mediria o lugar errado em um terco
    dos times, e mediria BEM: o recorte pegaria fundo dos dois lados e passaria.
    """
    x, y, w, h = rects[nome]
    if nome == "home1" and indice > 62:
        # o `.lfm` diz Left = 16, Width = 80; o handler troca os dois
        x, w = x - 16 + 7, 100
    return x, y, w, h


def compara_render(oraculo, port, indice: int) -> dict:
    """Os tres bitmaps, pixel a pixel, cada lado na sua calibracao.

    Devolve, por controle, quantos pixels diferem e o maior desvio de canal. O
    desvio existe na saida porque "quantos pixels" nao distingue um degrade
    deslocado de um vermelho virado azul, e a §9 do plano previu tolerancia --
    se um dia houver, o numero tem de estar na mesa.
    """
    rects = retangulos_do_lfm(RENDER)
    off_o = calibra(oraculo, "oraculo")
    off_p = calibra(port, "port")
    saida = {}
    for nome in RENDER:
        rect = retangulo_do_render(nome, rects, indice)
        ra = regiao(oraculo, rect, off_o, f"oraculo/{nome}")
        rb = regiao(port, rect, off_p, f"port/{nome}")
        pa, pb = list(ra.get_flattened_data()), list(rb.get_flattened_data())
        difs = [(x, y) for x, y in zip(pa, pb) if x != y]
        pior = max((max(abs(c - d) for c, d in zip(x, y)) for x, y in difs),
                   default=0)
        saida[nome] = {"pixels": len(pa), "diferentes": len(difs),
                       "pior_canal": pior, "rect": rect}
    return saida


def relata_render(r: dict) -> int:
    ruins = [n for n, v in r.items() if v["diferentes"]]
    for nome, v in r.items():
        print(f"  {nome}: {v['diferentes']}/{v['pixels']} px diferentes, "
              f"maior desvio de canal {v['pior_canal']}")
    if ruins:
        print("DIVERGE no render 2D: " + ", ".join(ruins), file=sys.stderr)
        return 1
    total = sum(v["pixels"] for v in r.values())
    print(f"  PASSOU: bandeira e uniforme batem em pixel ({total} px, "
          f"tolerancia zero)")
    return 0


def compara_habilitacao(nac_orac, nac_port, mod_orac, mod_port) -> dict:
    """Que controles mudam de aparencia quando `nacional` vira falso.

    A regua nao e a cor do cinza -- gtk2 e Win32 nao desenham o mesmo cinza, e
    exigir isso seria reprovar o port por ser gtk2. A regua e **mudou ou nao
    mudou**, dentro de cada lado, entre um time nacional (indice 2) e o
    time-modelo (indice 95, `95 Master L. `). O conjunto que muda de um lado tem
    de ser o conjunto que muda do outro.

    Isso responde a unica pergunta que a secao **Saida** da spec deixou aberta:
    `TControl::SetEnabled` nao tem uma `call rel32` sequer na `.text`, entao os
    ~27 `.Enabled :=` do Pascal nunca foram confirmados no disassembly.
    """
    offs = {
        "nac_orac": calibra(nac_orac, "oraculo/nacional"),
        "nac_port": calibra(nac_port, "port/nacional"),
        "mod_orac": calibra(mod_orac, "oraculo/modelo"),
        "mod_port": calibra(mod_port, "port/modelo"),
    }
    confere_faixa()
    linhas, erros = [], []
    for nome, rect in CONTROLES.items():
        grupo = rect[4]
        if grupo in ("conteudo", "fora_da_faixa"):
            linhas.append({
                "nome": nome, "grupo": grupo, "oraculo": None, "port": None,
                "veredito": ("olho humano" if grupo == "conteudo"
                             else "olho humano (deriva do port)")})
            continue
        n_orac = difere(nac_orac, mod_orac, rect, offs["nac_orac"],
                        offs["mod_orac"], nome)
        n_port = difere(nac_port, mod_port, rect, offs["nac_port"],
                        offs["mod_port"], nome)
        m_orac = n_orac > LIMIAR_MUDANCA
        m_port = n_port > LIMIAR_MUDANCA
        esperado = grupo != "sempre_ligado"
        if m_orac != m_port and grupo not in ("pendente_32", "glifo_cinza"):
            veredito = "DIVERGE"
            erros.append(
                f"{nome}: oraculo {'muda' if m_orac else 'nao muda'} "
                f"({n_orac} px), port {'muda' if m_port else 'nao muda'} "
                f"({n_port} px)")
        elif m_orac != m_port and grupo == "glifo_cinza":
            veredito = "divergencia deliberada (WTE-TASK-35)"
        elif m_orac != m_port:
            veredito = "pendente da WTE-TASK-29"
        elif m_orac != esperado and grupo == "segue_nacional":
            veredito = "CONTRARIA A SPEC"
            erros.append(
                f"{nome}: a spec diz `.Enabled := nacional`, e nenhum dos dois "
                f"lados muda ({n_orac} px / {n_port} px)")
        elif m_orac != esperado and grupo == "sempre_ligado":
            veredito = "CONTRARIA A SPEC"
            erros.append(
                f"{nome}: a spec diz `.Enabled := True` incondicional, e os "
                f"dois lados mudam ({n_orac} px / {n_port} px)")
        else:
            veredito = "bate"
        linhas.append({"nome": nome, "grupo": grupo, "oraculo": n_orac,
                       "port": n_port, "veredito": veredito})
    return {"linhas": linhas, "erros": erros}


def relata_habilitacao(r: dict) -> int:
    print("compara_tela --habilitacao: time nacional x time-modelo, "
          "pixels que mudam por controle")
    for l in r["linhas"]:
        if l["oraculo"] is None:
            print(f"  {l['nome']:22s} {l['grupo']:14s} "
                  f"{'-':>7s} {'-':>7s}  {l['veredito']}")
        else:
            print(f"  {l['nome']:22s} {l['grupo']:14s} "
                  f"{l['oraculo']:7d} {l['port']:7d}  {l['veredito']}")
    if r["erros"]:
        print("DIVERGE:", file=sys.stderr)
        for e in r["erros"]:
            print("  " + e, file=sys.stderr)
        return 1
    medidos = sum(1 for l in r["linhas"] if l["oraculo"] is not None)
    print(f"  PASSOU: {medidos} controles medidos, o conjunto que muda e o "
          f"mesmo nos dois lados")
    return 0


def relata(m: dict) -> int:
    print(f"compara_tela: time {m['indice']}")
    print(f"  barras oraculo: {m['oraculo']}")
    print(f"  barras port   : {m['port']}")
    print("  valores do jogo: "
          + ", ".join(f"{n}=" + ("?" if v is None else f"{v:g}")
                      for n, v in zip(NOMES_DAS_BARRAS, m["valores"])))
    if "editada" in m:
        e = m["editada"]
        if e["erros"]:
            print("DIVERGE da edicao pedida:", file=sys.stderr)
            for d in e["erros"]:
                print("  " + d, file=sys.stderr)
            return 1
        print(f"  a edicao chegou: {NOMES_DAS_BARRAS[e['barra']]} = "
              f"{e['valor']} ({11 * e['valor'] + 9} px) nos dois lados")
    if "dump" in m:
        for r in m["dump"]["curtas"]:
            print("  curta: " + r)
        if m["dump"]["erros"]:
            print("DIVERGE da camada de dados:", file=sys.stderr)
            for d in m["dump"]["erros"]:
                print("  " + d, file=sys.stderr)
            return 1
        total = BARRAS - (1 if "editada" in m else 0)
        n = total - len(m["dump"]["curtas"])
        print(f"  a tela bate com o we2002_core em {n} de {total} barras"
              + (" (o resto curto pelo degrade, igual nos dois lados)"
                 if m["dump"]["curtas"] else ""))
    if m["diferencas"]:
        print("DIVERGE:", file=sys.stderr)
        for d in m["diferencas"]:
            print(f"  {d['barra']}: oraculo {d['oraculo']} px, "
                  f"port {d['port']} px", file=sys.stderr)
        return 1
    print(f"  PASSOU: as {BARRAS} barras batem em pixel")
    if "render" in m and relata_render(m["render"]):
        return 1
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
    if argv[:1] == ["--habilitacao"]:
        return main_habilitacao(argv[1:])
    if argv[:1] == ["--nomes"]:
        return main_nomes(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("oraculo", type=Path)
    ap.add_argument("port", type=Path)
    ap.add_argument("--indice", type=int, required=True)
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--dump", type=Path,
                    help="saida do dump_estado.pas, para confrontar a largura "
                         "invertida com o que a camada de dados carregou")
    ap.add_argument("--cheia-oraculo", type=Path,
                    help="captura da janela INTEIRA do oraculo; e dela que sai "
                         "a montagem, porque o recorte medido para em y 240 e "
                         "os dorsais estao em y 432")
    ap.add_argument("--cheia-port", type=Path)
    ap.add_argument("--editada", metavar="N=V",
                    help="modo --edicao do compara_tela.sh: a barra N (0..4) "
                         "foi editada para o valor V. Ela sai da conferencia "
                         "contra o dump, que e do estado CARREGADO, e ganha "
                         "conferencia propria")
    args = ap.parse_args(argv)
    editada = None
    if args.editada:
        n, _, v = args.editada.partition("=")
        editada = (int(n), int(v))
    try:
        o = carrega(args.oraculo)
        p = carrega(args.port)
        m = compara(o, p, args.indice)
        if args.saida:
            args.saida.mkdir(parents=True, exist_ok=True)
            destino = args.saida / f"time-{args.indice}-lado-a-lado.png"
            if args.cheia_oraculo and args.cheia_port:
                oc, pc = carrega(args.cheia_oraculo), carrega(args.cheia_port)
                confere_cobertura(oc, "oraculo", calibra(oc, "oraculo"))
                confere_cobertura(pc, "port", calibra(pc, "port"))
                montagem(oc, pc, destino)
                print(f"  montagem: {destino} (janela inteira -- com os 23 "
                      f"dorsais e a lista de jogadores)")
                m["render"] = compara_render(oc, pc, args.indice)
            else:
                montagem(o, p, destino)
                print(f"  montagem: {destino} (SO o recorte medido -- sem os "
                      f"dorsais nem a lista de jogadores)")
        if editada:
            m["editada"] = {"barra": editada[0], "valor": editada[1],
                            "erros": confere_editada(m, *editada)}
        if args.dump:
            m["dump"] = confere_contra_dump(
                m, args.dump, editada[0] if editada else None)
    except TelaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return relata(m)


def main_habilitacao(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="compara_tela.py --habilitacao",
        description="Compara o estado de habilitacao entre um time nacional e "
                    "o time-modelo, nos dois lados.")
    ap.add_argument("nacional_oraculo", type=Path)
    ap.add_argument("nacional_port", type=Path)
    ap.add_argument("modelo_oraculo", type=Path)
    ap.add_argument("modelo_port", type=Path)
    ap.add_argument("--saida", type=Path)
    args = ap.parse_args(argv)
    try:
        no, np_ = carrega(args.nacional_oraculo), carrega(args.nacional_port)
        mo, mp = carrega(args.modelo_oraculo), carrega(args.modelo_port)
        r = compara_habilitacao(no, np_, mo, mp)
        if args.saida:
            args.saida.mkdir(parents=True, exist_ok=True)
            montagem(mo, mp, args.saida / "modelo-lado-a-lado.png")
            print(f"  montagem: {args.saida / 'modelo-lado-a-lado.png'}")
    except TelaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return relata_habilitacao(r)


def main_nomes(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="compara_tela.py --nomes",
        description="Compara os tres campos de nome depois de os dois lados "
                    "receberem o MESMO texto pelo teclado.")
    ap.add_argument("oraculo", type=Path)
    ap.add_argument("port", type=Path)
    args = ap.parse_args(argv)
    try:
        r = compara_nomes(carrega(args.oraculo), carrega(args.port))
    except TelaError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return relata_nomes(r)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
