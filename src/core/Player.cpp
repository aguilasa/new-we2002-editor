// Bit-packing of the 12-byte player attribute blob.
//
// Ported verbatim from legacy/mfc/giocatore.cpp. Every mask, shift and the
// order of the read-modify-write pairs are unchanged: Encode() relies on
// clearing and setting overlapping bits in a specific sequence, so reordering
// even two adjacent lines can change the result.
//
// The original spelled this pair backwards -- its decoder was called
// "codifica_carat" and its encoder "decodifica". Phase 3.5 straightened that
// out: Decode() unpacks the blob into members, Encode() packs them back.

#include "we2002/Player.hpp"

namespace we2002 {

Player::Player() = default;

void Player::Decode()
{
// blob -> members
	position = raw_attributes[0]&0x07;
	skin_colour = raw_attributes[4]&0x03;
	hair_style = ((raw_attributes[0]>>4)&0x0f) + ((raw_attributes[1]<<4)&0x10);
	hair_colour = (raw_attributes[1]>>1)&0x07;
	beard_style = (raw_attributes[1]>>5)&0x07;
	beard_colour = (raw_attributes[2]>>1)&0x07;
	height = 148 + ((raw_attributes[2]>>4)&0x0f) + ((raw_attributes[3]<<4)&0x30);
	build = (raw_attributes[4]>>2)&0x07;
	age = 15 + ((raw_attributes[4]>>5)&0x07) + ((raw_attributes[5]<<3)&0x18);
	boots = (raw_attributes[11]>>3)&0x07;
	foot = (raw_attributes[11]>>6)&0x03;
	attack = 12 + ((raw_attributes[7]>>5)&0x07);
	defence = 12 + (raw_attributes[8]&0x07);
	strength = 12 + ((raw_attributes[5]>>6)&0x03) + ((raw_attributes[6]<<2)&0x04);
	stamina = 12 + ((raw_attributes[6]>>1)&0x07);
	speed = 12 + ((raw_attributes[6]>>7)&0x01) + ((raw_attributes[7]<<1)&0x06);
	acceleration = 12 + ((raw_attributes[7]>>2)&0x07);
	passing = 12 + ((raw_attributes[9]>>1)&0x07);
	shot_power = 12 + ((raw_attributes[8]>>3)&0x07);
	shot_accuracy = 12 + ((raw_attributes[8]>>6)&0x03) + ((raw_attributes[9]<<2)&0x04);
	jump = 12 + ((raw_attributes[10]>>2)&0x07);
	heading = 12 + ((raw_attributes[9]>>7)&0x01) + ((raw_attributes[10]<<1)&0x06);
	technique = 12 + ((raw_attributes[9]>>4)&0x07);
	dribbling = 12 + ((raw_attributes[6]>>4)&0x07);
	swerve = 12 + ((raw_attributes[10]>>5)&0x07);
	aggression = 12 + (raw_attributes[11]&0x07);
	reflexes = 12 + ((raw_attributes[5]>>2)&0x07);
	out_of_position = (raw_attributes[3]>>7)&0x01;
	number = 1 + ((raw_attributes[3]>>2)&0x1f);
}

void Player::Encode()
{
// members -> blob
	raw_attributes[3] &= 0x01;
	raw_attributes[3] |= (number-1)<<2;

	raw_attributes[3] &= 0x7f;
	raw_attributes[3] |= out_of_position<<7;
	raw_attributes[0] &= 0xf8;
	raw_attributes[0] |= position;
	raw_attributes[4] &= 0xfc;
	raw_attributes[4] |= skin_colour;
	raw_attributes[0] &= 0x0f;
	raw_attributes[0] |= hair_style<<4;
	raw_attributes[1] &= 0xfe;
	raw_attributes[1] |= hair_style>>4;
	raw_attributes[1] &= 0xf1;
	raw_attributes[1] |= hair_colour<<1;
	raw_attributes[1] &= 0x1f;
	raw_attributes[1] |= beard_style<<5;
	raw_attributes[2] &= 0xf1;
	raw_attributes[2] |= beard_colour<<1;
	raw_attributes[2] &= 0x0f;
	raw_attributes[2] |= (height-148)<<4;
	raw_attributes[3] &= 0xfc;
	raw_attributes[3] |= (height-148)>>4;
	raw_attributes[4] &= 0xe3;
	raw_attributes[4] |= build<<2;
	raw_attributes[4] &= 0x1f;
	raw_attributes[4] |= (age-15)<<5;
	raw_attributes[5] &= 0xfc;
	raw_attributes[5] |= (age-15)>>3;		
	raw_attributes[11] &= 0xc7;
	raw_attributes[11] |= boots<<3;
	raw_attributes[11] &= 0x3f;
	raw_attributes[11] |= foot<<6;
	raw_attributes[7] &= 0x1f;
	raw_attributes[7] |= (attack-12)<<5;
	raw_attributes[8] &= 0xf8;
	raw_attributes[8] |= defence-12;	
	raw_attributes[5] &= 0x3f;
	raw_attributes[5] |= (strength-12)<<6;
	raw_attributes[6] &= 0xfe;
	raw_attributes[6] |= (strength-12)>>2;
	raw_attributes[6] &= 0xf1;
	raw_attributes[6] |= (stamina-12)<<1;
	raw_attributes[6] &= 0x7f;
	raw_attributes[6] |= (speed-12)<<7;
	raw_attributes[7] &= 0xfc;
	raw_attributes[7] |= (speed-12)>>1;
	raw_attributes[7] &= 0xe3;
	raw_attributes[7] |= (acceleration-12)<<2;
	raw_attributes[9] &= 0xf1;
	raw_attributes[9] |= (passing-12)<<1;
	raw_attributes[8] &= 0xc7;
	raw_attributes[8] |= (shot_power-12)<<3;
	raw_attributes[8] &= 0x3f;
	raw_attributes[8] |= (shot_accuracy-12)<<6;
	raw_attributes[9] &= 0xfe;
	raw_attributes[9] |= (shot_accuracy-12)>>2;
	raw_attributes[10] &= 0xe3;
	raw_attributes[10] |= (jump-12)<<2;	
	raw_attributes[9] &= 0x7f;
	raw_attributes[9] |= (heading-12)<<7;
	raw_attributes[10] &= 0xfc;
	raw_attributes[10] |= (heading-12)>>1;
	raw_attributes[9] &= 0x8f;
	raw_attributes[9] |= (technique-12)<<4;
	raw_attributes[6] &= 0x8f;
	raw_attributes[6] |= (dribbling-12)<<4;
	raw_attributes[10] &= 0x1f;
	raw_attributes[10] |= (swerve-12)<<5;
	raw_attributes[11] &= 0xf8;
	raw_attributes[11] |= aggression-12;
	raw_attributes[5] &= 0xe3;
	raw_attributes[5] |= (reflexes-12)<<2;
}

}  // namespace we2002
