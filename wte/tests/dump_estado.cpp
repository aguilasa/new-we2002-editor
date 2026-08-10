// Despeja, em texto estavel e diffavel, todo o estado que o `we2002_core`
// carrega de uma imagem. Irmao em C++ do `dump_estado.pas`.
//
// Produto da WTE-TASK-20. Os dois lados escrevem o MESMO formato, e o criterio
// e `diff` vazio -- aqui e leitura pura, nao ha comportamento indefinido para
// preservar, entao zero divergencia e o unico resultado aceitavel. (O golden
// test de imagem do newWe2002 aceita uma faixa de 16 bytes; este nao aceita
// nada.)
//
// Por que um irmao em vez de um verbo novo no `tests/golden_tool.cpp`: aquele
// arquivo e do newWe2002, cujo escopo esta fechado e verificado. Um binario a
// parte, compilado pelo `compare_dumps.py` com `g++` direto sobre
// `src/core/*.cpp`, nao toca no gate do projeto irmao -- e mantem o `wte/`
// independente do CMake da raiz, como decidiu o `wte/README.md`.
//
// O par ser bilingue e o ponto: `fpc` lendo o Pascal gerado e `g++` lendo o C++
// original. Dois dumpers na mesma linguagem esconderiam erro de leitura de
// literal, que apareceria igual dos dois lados.
//
//   dump_estado_cpp <imagem.bin>
//
// Compilar (o `compare_dumps.py` faz isto sozinho):
//   g++ -std=c++17 -Isrc/core/include src/core/{CdImage,Database,Player,\
//       Tables,Team,TextCodec}.cpp wte/tests/dump_estado.cpp -o dump_cpp
//
// `Sofifa.cpp` fica de fora de proposito: e o unico que puxa libcurl, e nada
// do estado que se despeja aqui vem dele.

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>

#include "we2002/Database.hpp"
#include "we2002/Types.hpp"

namespace {

// --------------------------------------------------------------- formato ---
//
// `<n>:<hex>` -- n e o tamanho declarado do vetor, e o hex vai ate o ultimo
// byte nao-zero. Tudo depois disso e zero por definicao, entao a forma e
// **sem perda** e nao gasta 500 caracteres por URL vazia.
//
// Hex minusculo, decimal com sinal, uma chave por linha, `\n`. Cada uma dessas
// escolhas precisa valer nos dois lados; divergencia de formatacao viraria
// divergencia de dado no diff, que e o pior tipo de falso positivo.

std::string HexTrim(const void* data, std::size_t n) {
    const auto* p = static_cast<const unsigned char*>(data);
    std::size_t fim = n;
    while (fim > 0 && p[fim - 1] == 0) --fim;
    std::string s = std::to_string(n) + ":";
    static const char* D = "0123456789abcdef";
    for (std::size_t i = 0; i < fim; ++i) {
        s += D[p[i] >> 4];
        s += D[p[i] & 15];
    }
    return s;
}

std::string CsvSigned(const char* p, std::size_t n) {
    std::string s;
    for (std::size_t i = 0; i < n; ++i) {
        if (i) s += ",";
        s += std::to_string(static_cast<int>(static_cast<signed char>(p[i])));
    }
    return s;
}

std::string CsvUnsigned(const unsigned char* p, std::size_t n) {
    std::string s;
    for (std::size_t i = 0; i < n; ++i) {
        if (i) s += ",";
        s += std::to_string(static_cast<unsigned>(p[i]));
    }
    return s;
}

std::string CsvU16(const unsigned short* p, std::size_t n) {
    std::string s;
    for (std::size_t i = 0; i < n; ++i) {
        if (i) s += ",";
        s += std::to_string(static_cast<unsigned>(p[i]));
    }
    return s;
}

void Linha(const std::string& chave, const std::string& valor) {
    std::fputs(chave.c_str(), stdout);
    std::fputs(" = ", stdout);
    std::fputs(valor.c_str(), stdout);
    std::fputc('\n', stdout);
}

void LinhaInt(const std::string& chave, long v) {
    Linha(chave, std::to_string(v));
}

// -------------------------------------------------------------- despejos ---

void DespejaJogador(int i, const we2002::Player& p) {
    const std::string k = "players[" + std::to_string(i) + "].";
    Linha(k + "url", HexTrim(p.url, sizeof(p.url)));
    Linha(k + "name", HexTrim(p.name, sizeof(p.name)));
    LinhaInt(k + "position", p.position);
    LinhaInt(k + "skin_colour", p.skin_colour);
    LinhaInt(k + "hair_style", p.hair_style);
    LinhaInt(k + "hair_colour", p.hair_colour);
    LinhaInt(k + "beard_style", p.beard_style);
    LinhaInt(k + "beard_colour", p.beard_colour);
    LinhaInt(k + "height", p.height);
    LinhaInt(k + "build", p.build);
    LinhaInt(k + "age", p.age);
    LinhaInt(k + "boots", p.boots);
    LinhaInt(k + "foot", p.foot);
    LinhaInt(k + "attack", p.attack);
    LinhaInt(k + "defence", p.defence);
    LinhaInt(k + "strength", p.strength);
    LinhaInt(k + "stamina", p.stamina);
    LinhaInt(k + "speed", p.speed);
    LinhaInt(k + "acceleration", p.acceleration);
    LinhaInt(k + "passing", p.passing);
    LinhaInt(k + "shot_power", p.shot_power);
    LinhaInt(k + "shot_accuracy", p.shot_accuracy);
    LinhaInt(k + "jump", p.jump);
    LinhaInt(k + "heading", p.heading);
    LinhaInt(k + "technique", p.technique);
    LinhaInt(k + "dribbling", p.dribbling);
    LinhaInt(k + "swerve", p.swerve);
    LinhaInt(k + "aggression", p.aggression);
    LinhaInt(k + "reflexes", p.reflexes);
    LinhaInt(k + "out_of_position", p.out_of_position);
    LinhaInt(k + "number", p.number);
    LinhaInt(k + "cost", p.cost);
    Linha(k + "raw_attributes",
          CsvSigned(p.raw_attributes, sizeof(p.raw_attributes)));
}

// Os campos comuns a Team e MlTeam. O gerador do Pascal manteve os nomes, e
// manter a ordem aqui e o que faz `diff` de linha valer alguma coisa.
template <typename T>
void DespejaComuns(const std::string& k, const T& t, int nomes) {
    for (int j = 0; j < nomes; ++j)
        Linha(k + "names[" + std::to_string(j) + "]",
              HexTrim(t.names[j], sizeof(t.names[j])));
    Linha(k + "mixed_case_name",
          HexTrim(t.mixed_case_name, sizeof(t.mixed_case_name)));
    for (int j = 0; j < 3; ++j)
        Linha(k + "abbreviations[" + std::to_string(j) + "]",
              HexTrim(t.abbreviations[j], sizeof(t.abbreviations[j])));
    Linha(k + "kanji_name", HexTrim(t.kanji_name, sizeof(t.kanji_name)));
    Linha(k + "raw_kanji_name",
          HexTrim(t.raw_kanji_name, sizeof(t.raw_kanji_name)));
    LinhaInt(k + "bar_attack", static_cast<signed char>(t.bar_attack));
    LinhaInt(k + "bar_defence", static_cast<signed char>(t.bar_defence));
    LinhaInt(k + "bar_power", static_cast<signed char>(t.bar_power));
    LinhaInt(k + "bar_speed", static_cast<signed char>(t.bar_speed));
    LinhaInt(k + "bar_technique", static_cast<signed char>(t.bar_technique));
    LinhaInt(k + "kick_long_fk", static_cast<signed char>(t.kick_long_fk));
    LinhaInt(k + "kick_short_fk", static_cast<signed char>(t.kick_short_fk));
    LinhaInt(k + "kick_left_corner",
             static_cast<signed char>(t.kick_left_corner));
    LinhaInt(k + "kick_right_corner",
             static_cast<signed char>(t.kick_right_corner));
    LinhaInt(k + "kick_penalty", static_cast<signed char>(t.kick_penalty));
    LinhaInt(k + "captain", static_cast<signed char>(t.captain));
    Linha(k + "raw_formation",
          HexTrim(t.raw_formation, sizeof(t.raw_formation)));
    Linha(k + "slot_role", CsvSigned(t.slot_role, 10));
    Linha(k + "slot_x", CsvSigned(t.slot_x, 10));
    Linha(k + "slot_y", CsvSigned(t.slot_y, 10));
    LinhaInt(k + "flag_shape", static_cast<signed char>(t.flag_shape));
    Linha(k + "flag_colours", CsvU16(t.flag_colours, 16));
    Linha(k + "home_kit", CsvU16(t.home_kit, 16));
    Linha(k + "away_kit", CsvU16(t.away_kit, 16));
    Linha(k + "raw_strategy", CsvSigned(t.raw_strategy, 4));
}

void DespejaTime(int i, const we2002::Team& t) {
    const std::string k = "teams[" + std::to_string(i) + "].";
    DespejaComuns(k, t, 6);
    // Os 23 numeros DESEMPACOTADOS mais as quatro palavras cruas. As duas
    // formas de proposito: o Pascal nao tem o bitfield do C++, tem um layout
    // escrito a mao (tipos.md, decisao 2), e so despejar o valor cru deixaria
    // um erro de deslocamento passar. Isto e a conferencia do bitfield contra
    // imagem real que a fase 3 pede.
    std::string ns;
    for (int j = 0; j < 23; ++j) {
        if (j) ns += ",";
        ns += std::to_string(we2002::SquadNumberAt(t.squad_numbers, j));
    }
    Linha(k + "squad_numbers", ns);
    std::uint32_t cru[4];
    std::memcpy(cru, &t.squad_numbers, sizeof(cru));
    std::string rs;
    for (int j = 0; j < 4; ++j) {
        if (j) rs += ",";
        rs += std::to_string(cru[j]);
    }
    Linha(k + "squad_numbers.raw", rs);
}

void DespejaMl(const std::string& k, const we2002::MlTeam& t) {
    DespejaComuns(k, t, 8);
    Linha(k + "raw_numbers", CsvSigned(t.raw_numbers, 23));
    Linha(k + "link", CsvUnsigned(t.link, 46));
}

void DespejaFormacao(int i, const we2002::Formation& f) {
    const std::string k = "preset_formations[" + std::to_string(i) + "].";
    Linha(k + "name", HexTrim(f.name, sizeof(f.name)));
    Linha(k + "roles", CsvSigned(f.roles, 11));
    Linha(k + "x", CsvSigned(f.x, 10));
    Linha(k + "y", CsvSigned(f.y, 10));
}

}  // namespace

int main(int argc, char** argv) {
    // `--roundtrip` e Load+Save sem saida nenhuma: a metade de GRAVACAO do
    // aceite da fase 3. Mora aqui, e nao num binario a parte, porque tem de
    // ser exatamente o mesmo `Database` que o dump usa -- dois executaveis
    // divergiriam no dia em que um fosse recompilado e o outro nao.
    const bool roundtrip = argc == 3 && std::string(argv[1]) == "--roundtrip";
    if (argc != 2 && !roundtrip) {
        std::fprintf(stderr,
                     "uso: dump_estado_cpp [--roundtrip] <imagem.bin>\n");
        return 2;
    }
    const char* imagem = roundtrip ? argv[2] : argv[1];

    we2002::Database db;
    // Reporter vazio: a mensagem de tamanho e ruido aqui, e escrever no stdout
    // contaminaria o dump.
    if (!db.Load(imagem, nullptr)) {
        std::fprintf(stderr, "dump_estado_cpp: nao abre %s\n", imagem);
        return 1;
    }
    if (roundtrip) {
        if (!db.Save(imagem, nullptr)) {
            std::fprintf(stderr, "dump_estado_cpp: nao grava %s\n", imagem);
            return 1;
        }
        return 0;
    }

    Linha("dump", "we2002-state v1");
    LinhaInt("counts.players", we2002::PLAYERS_TOTAL);
    LinhaInt("counts.teams", we2002::TEAMS_NATIONAL_ALLSTAR_SLOTS);
    LinhaInt("counts.ml_teams", we2002::TEAMS_ML);
    LinhaInt("counts.formations", 16);

    for (int i = 0; i < we2002::PLAYERS_TOTAL; ++i)
        DespejaJogador(i, db.players[i]);
    for (int i = 0; i < we2002::TEAMS_NATIONAL_ALLSTAR_SLOTS; ++i)
        DespejaTime(i, db.teams[i]);
    for (int i = 0; i < we2002::TEAMS_ML; ++i)
        DespejaMl("ml_teams[" + std::to_string(i) + "].", db.ml_teams[i]);
    DespejaMl("ml_default.", db.ml_default);
    for (int i = 0; i < 16; ++i)
        DespejaFormacao(i, db.preset_formations[i]);
    Linha("link_euro_allstar", CsvUnsigned(db.link_euro_allstar, 46));
    Linha("link_world_allstar", CsvUnsigned(db.link_world_allstar, 46));
    return 0;
}
