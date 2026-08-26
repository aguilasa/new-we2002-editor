#!/usr/bin/env python3
"""Guarda do `wte_datafiles.pas` -- CORR-WTE-117.

O `RaizDosAssets` procurava os assets em QUATRO lugares e a
`MensagemDeAssetsAusentes` oferecia TRES. O quarto -- `<exe>/../../assets` --
nao tinha comentario, nao aparecia na mensagem, e nada no repositorio o criava:
nem o `make -C wte assets`, que liga `wte/assets` (o candidato 1), nem o
`make -C wte install`, que popula `share/<slug>` (o 2).

Um caminho que a busca aceita e a mensagem nao oferece atende quem acertar por
acaso e nao ajuda ninguem -- e o numero dos documentos (`wte/README.md`, o
criterio da WTE-TASK-39) e copiado da mensagem, entao ele fica errado em
silencio. O quarto foi apagado; esta guarda impede o proximo.

## Por que ler o Pascal em vez de rodar o app

Rodar o binario responderia "achou" ou "nao achou" para UM layout de cada vez, e
a pergunta e sobre a lista inteira. O que se afirma aqui e estrutural -- a busca
e a mensagem falam dos mesmos lugares --, e isso se le da fonte, sem `:98`, sem
compilar e sem os assets.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FONTE = RAIZ / "wte" / "src" / "wte_datafiles.pas"


def corpo(nome: str) -> str:
    """O corpo de uma funcao, do `function` ate o `end;` da coluna zero."""
    texto = FONTE.read_text(encoding="utf-8")
    i = texto.index(f"function {nome}: string;\nvar") if f"function {nome}: string;\nvar" in texto \
        else texto.index(f"function {nome}: string;\nbegin")
    j = texto.index("\nend;", i)
    return texto[i:j]


class TestCandidatos(unittest.TestCase):
    """A busca e a mensagem falam dos mesmos lugares."""

    def candidatos(self) -> list[str]:
        return re.findall(r"^  candidatos\[(\d+)\] :=", corpo("RaizDosAssets"),
                          re.M)

    def itens_da_mensagem(self) -> list[str]:
        return re.findall(r"'  (\d+)\. ", corpo("MensagemDeAssetsAusentes"))

    def test_a_busca_e_a_mensagem_tem_o_mesmo_tamanho(self) -> None:
        """O defeito literal: 4 contra 3."""
        self.assertEqual(len(self.candidatos()), len(self.itens_da_mensagem()),
                         "candidato que a busca aceita e a mensagem nao "
                         "oferece atende quem acertar por acaso, e deixa o "
                         "numero dos documentos errado em silencio")

    def test_sao_tres_hoje(self) -> None:
        """O numero que o `wte/README.md` e a WTE-TASK-39 publicam."""
        self.assertEqual(len(self.candidatos()), 3)

    def test_o_array_e_do_tamanho_da_lista(self) -> None:
        """`array[0..N]` maior que a lista deixaria um candidato VAZIO no laco.

        `TemAssets('')` devolve False, entao nao quebraria nada -- e e
        exatamente por isso que passaria despercebido.
        """
        m = re.search(r"candidatos: array\[0\.\.(\d+)\] of string",
                      corpo("RaizDosAssets"))
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)) + 1, len(self.candidatos()))

    def test_os_indices_sao_contiguos_desde_zero(self) -> None:
        self.assertEqual(self.candidatos(),
                         [str(i) for i in range(len(self.candidatos()))])

    def test_os_itens_da_mensagem_sao_numerados_desde_um(self) -> None:
        self.assertEqual(self.itens_da_mensagem(),
                         [str(i + 1) for i in range(len(self.itens_da_mensagem()))])

    def test_o_caminho_apagado_nao_voltou(self) -> None:
        """`<exe>/../../assets`, o quarto candidato da CORR-WTE-117.

        A forma no Pascal e `'..' + DirectorySeparator + '..'` -- dois niveis
        acima do executavel. Nenhum layout deste repositorio o cria.
        """
        self.assertNotIn("'..' + DirectorySeparator + '..'",
                         corpo("RaizDosAssets"))

    @staticmethod
    def _ate_o_parentese(texto: str, i: int) -> str:
        """Do indice `i` ate o `)` que fecha o `(` aberto ali.

        A mensagem e UMA expressao com varios `ExpandFileName(...)` dentro, e
        uma regex nao-gananciosa nao acha o fim certo -- ela para no primeiro
        `)`, que e o do proprio `ExpandFileName` so por sorte, ou atravessa
        tudo. Contar parenteses e o que resolve.
        """
        nivel, comeco = 0, i
        for j in range(i, len(texto)):
            if texto[j] == "(":
                nivel += 1
                if nivel == 1:
                    comeco = j + 1
            elif texto[j] == ")":
                nivel -= 1
                if nivel == 0:
                    return texto[comeco:j]
        raise AssertionError("parentese nao fechado")

    def test_todo_candidato_relativo_aparece_na_mensagem(self) -> None:
        """O par por par, e nao so a contagem.

        A busca monta com `base + '..' + ...`; a mensagem, com
        `ExpandFileName(DirDoExecutavel + '..' + ...)`. Tirando o prefixo, o
        resto tem de ser o mesmo texto Pascal.
        """
        def normaliza(s: str) -> str:
            return re.sub(r"\s+", " ", s).strip().rstrip("+").strip()

        busca = {normaliza(x) for x in re.findall(
            r"^  candidatos\[\d+\] := base \+ (.+?);$",
            corpo("RaizDosAssets"), re.M | re.S)}

        texto = corpo("MensagemDeAssetsAusentes")
        msg = set()
        for m in re.finditer(r"ExpandFileName", texto):
            dentro = self._ate_o_parentese(texto, m.end())
            msg.add(normaliza(dentro.replace("DirDoExecutavel +", "", 1)))

        self.assertTrue(busca, "nenhum candidato relativo lido")
        self.assertEqual(busca, msg,
                         "a busca e a mensagem montam caminhos diferentes")


if __name__ == "__main__":
    unittest.main()
