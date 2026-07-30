// Bit-packing of the 12-byte player attribute blob.
//
// Ported verbatim from legacy/mfc/giocatore.cpp. Every mask, shift and the
// order of the read-modify-write pairs are unchanged: decodifica() relies on
// clearing and setting overlapping bits in a specific sequence, so reordering
// even two adjacent lines can change the result.
//
// Naming quirk inherited from the original: codifica_carat() *decodes* the
// blob into members, decodifica() *encodes* the members back. The names are
// backwards; they are kept so the port stays diffable against the legacy
// source.

#include "we2002/Player.hpp"

namespace we2002 {

Player::Player() = default;

void Player::codifica_carat()
{
// codifica dalla stringa alle varibili membro
	posizione = str_carat[0]&0x07;
	col_pelle = str_carat[4]&0x03;
	stile_capelli = ((str_carat[0]>>4)&0x0f) + ((str_carat[1]<<4)&0x10);
	col_capelli = (str_carat[1]>>1)&0x07;
	stile_barba = (str_carat[1]>>5)&0x07;
	col_barba = (str_carat[2]>>1)&0x07;
	altezza = 148 + ((str_carat[2]>>4)&0x0f) + ((str_carat[3]<<4)&0x30);
	corporatura = (str_carat[4]>>2)&0x07;
	eta = 15 + ((str_carat[4]>>5)&0x07) + ((str_carat[5]<<3)&0x18);
	scarpe = (str_carat[11]>>3)&0x07;
	piede = (str_carat[11]>>6)&0x03;
	attacco = 12 + ((str_carat[7]>>5)&0x07);
	difesa = 12 + (str_carat[8]&0x07);
	forza = 12 + ((str_carat[5]>>6)&0x03) + ((str_carat[6]<<2)&0x04);
	resistenza = 12 + ((str_carat[6]>>1)&0x07);
	velocita = 12 + ((str_carat[6]>>7)&0x01) + ((str_carat[7]<<1)&0x06);
	accel = 12 + ((str_carat[7]>>2)&0x07);
	passaggio = 12 + ((str_carat[9]>>1)&0x07);
	pot_tiro = 12 + ((str_carat[8]>>3)&0x07);
	prec_tiro = 12 + ((str_carat[8]>>6)&0x03) + ((str_carat[9]<<2)&0x04);
	salto = 12 + ((str_carat[10]>>2)&0x07);
	testa = 12 + ((str_carat[9]>>7)&0x01) + ((str_carat[10]<<1)&0x06);
	tecnica = 12 + ((str_carat[9]>>4)&0x07);
	dribbling = 12 + ((str_carat[6]>>4)&0x07);
	effetto = 12 + ((str_carat[10]>>5)&0x07);
	aggress = 12 + (str_carat[11]&0x07);
	riflessi = 12 + ((str_carat[5]>>2)&0x07);
	fuori_ruolo = (str_carat[3]>>7)&0x01;
	numero = 1 + ((str_carat[3]>>2)&0x1f);
}

void Player::decodifica()
{
// decodifica dalle varibili membro alla stringa
	str_carat[3] &= 0x01;
	str_carat[3] |= (numero-1)<<2;

	str_carat[3] &= 0x7f;
	str_carat[3] |= fuori_ruolo<<7;
	str_carat[0] &= 0xf8;
	str_carat[0] |= posizione;
	str_carat[4] &= 0xfc;
	str_carat[4] |= col_pelle;
	str_carat[0] &= 0x0f;
	str_carat[0] |= stile_capelli<<4;
	str_carat[1] &= 0xfe;
	str_carat[1] |= stile_capelli>>4;
	str_carat[1] &= 0xf1;
	str_carat[1] |= col_capelli<<1;
	str_carat[1] &= 0x1f;
	str_carat[1] |= stile_barba<<5;
	str_carat[2] &= 0xf1;
	str_carat[2] |= col_barba<<1;
	str_carat[2] &= 0x0f;
	str_carat[2] |= (altezza-148)<<4;
	str_carat[3] &= 0xfc;
	str_carat[3] |= (altezza-148)>>4;
	str_carat[4] &= 0xe3;
	str_carat[4] |= corporatura<<2;
	str_carat[4] &= 0x1f;
	str_carat[4] |= (eta-15)<<5;
	str_carat[5] &= 0xfc;
	str_carat[5] |= (eta-15)>>3;		
	str_carat[11] &= 0xc7;
	str_carat[11] |= scarpe<<3;
	str_carat[11] &= 0x3f;
	str_carat[11] |= piede<<6;
	str_carat[7] &= 0x1f;
	str_carat[7] |= (attacco-12)<<5;
	str_carat[8] &= 0xf8;
	str_carat[8] |= difesa-12;	
	str_carat[5] &= 0x3f;
	str_carat[5] |= (forza-12)<<6;
	str_carat[6] &= 0xfe;
	str_carat[6] |= (forza-12)>>2;
	str_carat[6] &= 0xf1;
	str_carat[6] |= (resistenza-12)<<1;
	str_carat[6] &= 0x7f;
	str_carat[6] |= (velocita-12)<<7;
	str_carat[7] &= 0xfc;
	str_carat[7] |= (velocita-12)>>1;
	str_carat[7] &= 0xe3;
	str_carat[7] |= (accel-12)<<2;
	str_carat[9] &= 0xf1;
	str_carat[9] |= (passaggio-12)<<1;
	str_carat[8] &= 0xc7;
	str_carat[8] |= (pot_tiro-12)<<3;
	str_carat[8] &= 0x3f;
	str_carat[8] |= (prec_tiro-12)<<6;
	str_carat[9] &= 0xfe;
	str_carat[9] |= (prec_tiro-12)>>2;
	str_carat[10] &= 0xe3;
	str_carat[10] |= (salto-12)<<2;	
	str_carat[9] &= 0x7f;
	str_carat[9] |= (testa-12)<<7;
	str_carat[10] &= 0xfc;
	str_carat[10] |= (testa-12)>>1;
	str_carat[9] &= 0x8f;
	str_carat[9] |= (tecnica-12)<<4;
	str_carat[6] &= 0x8f;
	str_carat[6] |= (dribbling-12)<<4;
	str_carat[10] &= 0x1f;
	str_carat[10] |= (effetto-12)<<5;
	str_carat[11] &= 0xf8;
	str_carat[11] |= aggress-12;
	str_carat[5] &= 0xe3;
	str_carat[5] |= (riflessi-12)<<2;
}

}  // namespace we2002
