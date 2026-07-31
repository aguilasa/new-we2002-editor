// Field-by-field copy of a Player.
//
// The original open-coded this three times over -- twice in selezDlg's
// substitution and twice more in OnOrdinaPanchina's bench sort -- as runs of
// thirty-odd assignments. Two details are worth keeping rather than replacing
// with a plain struct assignment:
//
//   * `url` is copied by the substitution but NOT by the bench sort, so in the
//     original a reordered bench leaves its SoFIFA links attached to the slot
//     instead of following the player. `with_url` preserves that difference.
//   * `raw_attributes` is never copied. It does not need to be: Load() decodes
//     it into the members and Save() re-encodes from them, so between the two
//     it holds nothing that is not already in the fields below.

#pragma once

#include <cstring>

#include "we2002/Player.hpp"

inline void CopyPlayerFields(we2002::Player& dst, const we2002::Player& src,
                             bool with_url) {
    std::memcpy(dst.name, src.name, sizeof(dst.name));
    if (with_url) {
        std::memcpy(dst.url, src.url, sizeof(dst.url));
    }
    dst.position = src.position;
    dst.skin_colour = src.skin_colour;
    dst.hair_style = src.hair_style;
    dst.hair_colour = src.hair_colour;
    dst.beard_style = src.beard_style;
    dst.beard_colour = src.beard_colour;
    dst.height = src.height;
    dst.build = src.build;
    dst.age = src.age;
    dst.boots = src.boots;
    dst.foot = src.foot;
    dst.attack = src.attack;
    dst.defence = src.defence;
    dst.strength = src.strength;
    dst.stamina = src.stamina;
    dst.speed = src.speed;
    dst.acceleration = src.acceleration;
    dst.passing = src.passing;
    dst.shot_power = src.shot_power;
    dst.shot_accuracy = src.shot_accuracy;
    dst.jump = src.jump;
    dst.heading = src.heading;
    dst.technique = src.technique;
    dst.dribbling = src.dribbling;
    dst.swerve = src.swerve;
    dst.aggression = src.aggression;
    dst.reflexes = src.reflexes;
    dst.out_of_position = src.out_of_position;
    dst.number = src.number;
    dst.cost = src.cost;
}
