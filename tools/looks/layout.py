#!/usr/bin/env python3
"""Where things are, and which disc may be read for what.

This is the module the drawing rules of the plan (section 3.3, rule 1) single
out: every address of the `looks` project lives here, and nowhere else.  It
knows no file format and imports no Qt.  Callers hand it bytes or digests and
it answers questions about them, which is what lets its self_check() run on a
machine with no disc image at all.

It does no I/O at all.  It held one exception for as long as the two-disc
guard had no caller -- `--check-discs` opened both real discs itself -- and
LOOKS-TASK-03 cleared that debt on 2026-09-14: the live demonstration now lives
in `iso_source.py --check-discs`, where reading a disc is the module's job.

What is an address, and what is a format?  The line this file draws: the KSEG0
pointer table at the head of a model file is ADDRESS material, so deriving the
load base from it belongs here.  The vertices and primitives those pointers aim
at are FORMAT, and they belong to section.py.  derive_base() reads the pointer
table and stops there; it never looks at a section.

THE RULE THIS FILE EXISTS FOR
-----------------------------
There are two discs and they are not interchangeable:

* the Japanese original is the truth about BYTES.  Textures and palettes are
  read from it and from nothing else;
* the English translation patch is the disc you DRIVE, because its menus are
  legible -- and its geometry is byte-for-byte the same, so driving it is free.

Reading a palette off the English disc is a silent error.  The offset is valid
there, the graphic appears, and it is the wrong graphic: `/BIN/DAT2D.BIN`
differs between the two, and it is exactly the file that holds hair, faces,
bodies, boots and the skin palettes.  Nothing raises, nothing warns.  That is
why the rule is a digest check in code and not a sentence in a document.

Usage:
    python tools/looks/layout.py --check
    python tools/looks/layout.py --sweep
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import sys
import tokenize
import tempfile

# --- The two discs, and how a recipe names each one -----------------------
#
# Two variables because they are two different files, and the second is a
# .cue rather than a .bin: the emulator wants the sheet, the readers want the
# data track.  The PES2 tooling learned this the expensive way -- one family
# of variables for disc tools and another for emulator tools -- and the
# recipe that carried only the first left the one gate that boots the game
# reporting `skipped` in 0.01 s while the run printed `100% tests passed`.
ENV_IMAGE = "WE2002_LOOKS_IMAGE"
"""The Japanese data track (.bin).  The truth about bytes."""

ENV_DRIVE_IMAGE = "WE2002_LOOKS_DRIVE_IMAGE"
"""The English .cue.  The disc to drive the emulator with."""

ENV_CORPUS = "WE2002_LOOKS_CORPUS"
"""The folder of the fifty renders, whose names are corpus tuples.

Third party's, and not in the git tree (plan section 2), so it is named the
way every other external fixture of this repository is: by variable, and the
gate that reads it skips with 77 when it is not set.
"""

# --- Paths inside the disc ------------------------------------------------
EDT_MOD = "/BIN/EDT_MOD.BIN"
MODEL = "/BIN/MODEL.BIN"
DAT2D = "/BIN/DAT2D.BIN"
SELECT = "/SELECT.BIN"
ANIME = "/BIN/ANIME.BIN"
SELECT8 = "/SELECT8.BIN"
EDT_2D = "/BIN/EDT_2D.BIN"
SELECTC = "/SELECTC.BIN"
BOOT = "/SLPM_870.56"

KIT_DIR = "/BIN/"
KIT_PREFIX = "TEX_"
KIT_SUFFIX = ".BIN"
"""How a kit container is named on the disc: `/BIN/TEX_<tag>.BIN`.

Spelled in pieces so `kit_path` builds the name and nothing else does, and so
the 105 tags below are the only list of them.
"""

# --- Identity of what may be read, measured 2026-09-14 --------------------
#
# sha256 of the FILE as read out of the disc, not of the disc.  Keying on the
# file is what makes the check say something: two dumps of the same release
# can differ in their tail and still hold identical assets, and a translation
# patch can leave the disc the same size while replacing exactly this file.
DIGEST = {
    # Identical on both discs -- this is why the English disc may be driven.
    EDT_MOD: "6ff56894e7ce94aa655047200143087afe85d70cda777e5aee30dedf9d427dd3",
    MODEL: "0b3814bb0d3b47f4ac3b13a1eb9f64ce9c50f8f08331790716827c618c0578cb",
    # Japanese only.  The English disc has
    # 4a4d6a4fe301b1169535c6e5acf7e31c584d725be1571e689ed6fb5696beef60 here,
    # and reading a palette out of that one is the silent error above.
    DAT2D: "0e914e584c889635f0c3a7a64d87ed5c773541c76b35455b6475c19c9f50de7b",
    SELECT: "86d14a66a3cd72b9363832260d4f3842e15d530c2f76eb0d6a3f6823cd603ce1",
    # Identical on both discs too, measured 2026-09-17 (LOOKS-TASK-24): the
    # same 396,804 bytes and the same digest on the Japanese dump and on the
    # English one that drives the emulator.
    ANIME: "9b43fe0443e6818391cf2f5a106d26332e4e9c6155614ba59d2ff424bd35427a",
    # Japanese only, measured 2026-09-18 (LOOKS-TASK-29).  The English disc has
    # 9512941d8d4cb93367fdb102cb0fa43440377b2a083a328603a62fca514ac2fd here --
    # the overlay carries the screen's text, and the patch translated it.  The
    # part this cycle reads, the stature rule, is the same on both.
    SELECT8: "b735ed9c1ebaef001088de57c807c8e9680b3296516928fb23b4af612befef8e",
    # Identical on both discs, measured 2026-09-21 (LOOKS-TASK-31): the same
    # 40,360 bytes and digest on the Japanese dump and the English one.  It
    # holds the screen's own art -- the font the text is cut from included --
    # and every texel LOOKS SET samples from it decodes to what VRAM shows
    # (`oracle.py --scenery`).
    EDT_2D: "ec4bebf15b702080313972c982777974a2406cd12438cad6f23660027a1458eb",
    # Japanese only, measured 2026-09-22 (LOOKS-TASK-37).  The English disc has
    # 26a350a937eded8a4d4b2edf021b15e2d7089bb71cc1dc6a9132f44e7f5a37c0 here:
    # the two files differ in 5,201 bytes between 0x2B8 and 0x5A26, the text
    # the patch translated.  The glyph routine and its table -- what this
    # cycle reads -- are byte for byte the same in both and in the running
    # game's RAM (`GLYPH_ROUTINE`, `GLYPH_TABLE`).
    SELECTC: "205ec241d0b8a316bc2efda07f4b989bcc7b2a610c14112735d355f9122bd03a",
    # Japanese only, measured 2026-09-22 (LOOKS-TASK-39).  The English disc
    # has 983b71cf6ce6d08ede9f57c6f370b9c9ad6b93cad4075206d92f8008d825fd28
    # here.  The three windows this cycle decodes out of it -- the help box's
    # glyph call (`HELP_GLYPH_CALL`), the lookup around it and the BIOS stub
    # (`KROM_STUB`) -- are byte for byte the same in both, which is what makes
    # an address measured on the English disc the emulator drives good on the
    # Japanese one it is read from.
    BOOT: "7da7745d5b1501b7ad4433711f2c89e1264568b9c90f58240417b9acd31169b6",
}

KIT_DIGEST = {
    "00": "7323b0dc3079fc5e8c71c65a1deb8a49f37f7cd42be1b8f4d2731d0635c5a670",
    "01": "12c0be27dda713ab112f384838157cafdbaf99addca39e1f362d8c3d4199ad70",
    "02": "f88c644a86b429f252a1887799375c6c0bb4b410007680aa98654b7d2ab0520b",
    "03": "6e4c996c13a91a6a9215b11589adfd05a9875e75fa6c4585248600b99455036f",
    "04": "4de5ba822c37ad4482bd30c3530724572e7c2a28917c0036c9e83afb74898c32",
    "05": "c0fb57223f9857ab5a67256e83a266a96b03910cdc193f559a578582bf5e6c31",
    "06": "d4bf432e7e0490f925ef51bce4d69a12aa3ad3f3c04e03b0d2d4f600e7bbf814",
    "07": "30cf31982d68d582ae12adb0469166945c9ba6e0214f7398f34572b3b4278ea5",
    "08": "3d143f84b293834b254c1eb432392f1b107ba8c72a7e3de768cd51b65b07dd6f",
    "09": "0d9d580f2a8af3454c990cd12d0c2490aab065592a9a64c9d05eff9f5ee87e18",
    "10": "566cef5f90df7cf792a745fb5c784980aac00c326b3a85af144806a75f7a3bb8",
    "11": "f96a3ff6a6fbf716d0eb0ad537a5b6216c071c23208072e077402640b6452c8a",
    "12": "2082ef525bea6d5f16618c29fc69222073b515a1f513ff788ce6f110004c3485",
    "13": "8d4f3df1a334a3b3811bc6517dc95e47b832fe43ac65a794495507c96f250551",
    "14": "552509df2a5d49e3727116da2cac12cb2951f876fa2f18104e7d822074d188a2",
    "15": "babc15cfc74b23bc25303203f9af23cc4b41db9709215d9a0ba70227dadb31d3",
    "16": "7d462d8dbbbe148f0344f9e48f783144e10f6b92b1361aaf7f836fc492951afd",
    "17": "81026fa465fa36bd0d48d671c53676bdce94695c78a65821c55baf603a78514e",
    "18": "dada6a26945dd8607c26b9c03a73cc071c979e7610656cbcb5292f613cf9c9cf",
    "19": "044bd05e51a604ac4feac5846b59397fc8302356894d63a4a98437ebb63b4772",
    "20": "b48008f697cd1252113c05555374c03123796ebe0380b0a36141c3b3fdd4a9e8",
    "21": "4b05f3b871e2de30933b88f19de9561e2525c073cd27c5bb19d214c27d7eedc2",
    "22": "7f2398c241bf1adcaa695802c3855d5242a3631aec45ed999c52be2f795483ff",
    "23": "ac5bacfbba424d19ab0842cbbf098c9aac1ee1024c58b415cd307e4888d549ba",
    "24": "e439d5f4c4814bcc2bb0ac04c8bd0248f66714dc8b875385909f212950a674c8",
    "25": "88d2aff9422132c50f346557a8e089404090000e264f9903d7ab7eef1cdbd20a",
    "26": "6b01234cea6d8c53ac3418e967b6b3334611c87dad5aa3339cecad6c70a7524b",
    "27": "93b75d97b63fafbd30cef80d3c06d342fbd985f432dc61af87f1fc19cf8a9f8c",
    "28": "f55b807209f5f23a2ef19f699651cea1ff7483684ba07dda935a336157a81770",
    "29": "1e302b7e37837feb339494585c6b7f22cdc0a7198d16def223944e7b84f9cdb1",
    "30": "8f04095f49c2d7502cce82f87fa910ea0f6248ca75bf004df99bbc25b98a1976",
    "31": "15ca7205cb63113fe8307269d5098316bf8c37c793caf06920f8be813e914a6a",
    "32": "4015a3c5cc775a58d76d54a37674261efeea2e48cac0f008a50d2efebf68f379",
    "33": "d12756b06860b90ec76c96b5425ae22b11916924e99adb9a29f2c94edec77070",
    "34": "e65ac19f7e6fb6141fed0cc97fb73e206fbf16cf2842f8552021e5eb2e348842",
    "35": "fdc48e1c9cd4a8f9c81a891bc81e89a75ee38177eb30145e331942129f8d6784",
    "36": "5143a6ed3c0fc17e22564168d4dc1f19fbbf79aa2f3680a7ebede08fb831aa0a",
    "37": "32e33b5f6a7e6c825c4de93cdcf4d7c6355af375f398fbf8ead5f86d7f946fad",
    "38": "b8a644d8aa8c9c6f4e84c2d28ad7eaad3f6aa2596728e6bda485e8deda80e78f",
    "39": "e5a3d1928034bee39c13ef7a4255e829214a9d1567c2cffb938c7c79e2592afd",
    "40": "422b596c26222dd77211e1901c60b10840375adf65d8aa61f655bca234045014",
    "41": "12ecc4a0898e00b8fa60ed72a173c41ce82bc35b6258c03bd2a437f3377146d5",
    "42": "8d00ff1e9d527cf47841149777240956a6c5b0fc6ca38d2e14752651b5f73b01",
    "43": "d76ed4e39116834f2d137a9a40a9a8a2d5486562ef259bb29ce63165a314a1aa",
    "44": "ccfa76aa0ade532e8e92b24d1b811b66b59dc0874a6599bfd38858763d73383e",
    "45": "c42972bf7a21550608fb1e5f3333196d043a4133eb2bbc7684f25ba8f6e0f024",
    "46": "75292bd25e05a6a1432c4ad6bb1912ad1ce9d0cf513c728940208fcf4352b6aa",
    "47": "8a7e24a43c4632da1e0123251ddeecb13845986458dad70b422ba712a3dc3e00",
    "48": "2a6a10ea790c0fa66bd3bbc700979fea8d68c85377585b44a38b419a66c55bfc",
    "49": "363ad2010d3e0227d4331bcb560ebf380c57f0729bbbcbfa7f879e81941cff96",
    "50": "7d548b56c0520d051c2825d0638c929ad312dadb59d2f48184936deb9e4a6fee",
    "51": "4b910e2a3c1a33fe6e1573f3c4ea0c415a208a282d833e155ed874e64f8a6574",
    "52": "126751d62d49629f3f5c4a00158b0f4e8ed1c788f56eec5f1eaf8aac9413db8e",
    "53": "1cc87b99c33116b44b4f419695e6983f69f188c52f24ce47e0d98eb39817b35d",
    "54": "d75e75ca8aa1b3b75d72ce1c670c03195ed9dbc2d9ff470b6663985eaa6daa3e",
    "55": "69e8aa00738f8bb6253e5ff1672591ccf2c0c0ecd7d9b99c3ec2da7dbcdeca12",
    "56": "fec4ae845995dd150c778ed2bb9877f7f9ad0d16766a816489f0cd9a4c917be4",
    "57": "76a4772182b4de6f2897be3f23881f404415937996685646748a9f9303236dc1",
    "58": "1c0fd6d5cef10dd7ff59b8bf51f38a5c06903885f50d288c198b2fc4e10ed42c",
    "59": "78f97c935afb178f7aca2d846e0d7417f650e756882f014e83fd0459342c1c56",
    "60": "a98f6bc02f9f6e7a612c8787a31da4850cec79d889c24b18262b01f3541d96f3",
    "61": "bccc43cd6bb6338db4d7d46e8a24f401380cf4904ff06cd79b3399c6b8fe4ade",
    "62": "57cce20d09f9b88fdd9b6a45f7587ed488c310a9749ae48f6294c31eef1e7f58",
    "63": "9d3c012abbf62e6c713fa9dc5454a175df1fd78a6103dadd603b5e07492da9c7",
    "64": "b25495cea130ef69c25eeda68275fa53df815948e5e6169d66cb8da3c7a06b7b",
    "65": "6b2a1b682b95b91ce39356adfaf52aeb73d07b52aaeef86206e49c0c49ada0ad",
    "66": "823b3b3de609ec9b7323b50073cddf372c2b859edfba59924956847644463b66",
    "67": "97d20cc889493ed544eef3022e24ae53e5cc1c5b4d9247d86a5698d64f682827",
    "68": "b3d92d09476bf5f25df15b007cbab3ddadb6cd7e9a295b88a5755f0f5d6459d5",
    "69": "b67ad65107540604eac110d59d4cba79f41238e2f1aa3b9de4c70b58e06bf7e2",
    "70": "cbee81680641f397721aa20bb8e81c453f70d61533b178c73f08c1b691be78e5",
    "71": "b8bfcd7312e5a3098f218b04ce2dd979e822018ede6348e622101c016fe6b834",
    "72": "4a0cf84aec47b44609bb3494ef5141d4357b8cffe7261055b83ad74aa4376b09",
    "73": "4436e6b5bc9c0606c962275750f6df953ffe21c51a2531e02f1c5e5efcfc124b",
    "74": "592665cc44e222903eeb55c47fa0d401e0b4cad622cbe9e4a118226911f34461",
    "75": "0a488bd21730155f945d659b5f51a7e37e3c4f1aed975bc7ac4de2ff26f5f71a",
    "76": "88d147ca66796078f0a51fae6e9874f47907bfb1c1ae9a57f75f5466def51572",
    "77": "1656e5d1c6fe2553b91f704f4b7fe76066c269b5bfe68d486a6ee8c0a80498cc",
    "78": "4d88b67346ff7eb22686112db253434a5784d7c28c79838555e37d13ac964756",
    "79": "6950b8fe8e59d5d68bb25001e1c0d1f8bcc3db6612a30ddbf14edc000bbeda87",
    "80": "69381cd15ef366ea9b1e9aeb1a54751d38166e84b69d7a37dcdc5a0199958909",
    "81": "7f8c192f934538ec7dbba963884c6af13163a38bdf9bb2a1d9a0e7fc51357466",
    "82": "8ad8fb393b2dad67cbf010c92e5abe3d39bf7b3503158454ea54b454e59dc68d",
    "83": "c83794f6df5d004202fa64e5c5a1d77ec5537a21f438912f20a6087c5399a2ca",
    "84": "ef42c350033a76fa8fac4953e5dda959bb2b9b48bb0273b2455810f8734b699b",
    "85": "656cdadbb63577a2831e315d85dd37e6c5343fe3942ce7d060185196c4d55365",
    "86": "7d5b5d59a4a21b1834e848c960a404e9c010db3e1a21b15ac3fa28edec0bf1be",
    "87": "3f164adf1d386fadfa30171b4d5d272b4c72334dd9f5a9e6b95d0b058e52ceea",
    "88": "9d71f709b2fd2f47eee3009605e82ca60cc819183a8b9707e33d3286ebada3c0",
    "89": "eea058339f53c7b3811fe54087faaea6c77123e11264480bccc138433b639da7",
    "90": "3d394a0ff921f6a200554eef557386d5eb794cd4f4ac485aa57bf8459302a7f1",
    "91": "31e5c9295e82917cf34dafb7c118a0f1932961ec2c0fd395db27816399d2cd61",
    "92": "8efd0625929e34c8710ea3594b3317c22d6409cadc2629ec3a05801f69f15edf",
    "93": "0d792f5910f93e0c0df0730a2b85ebc7187309f673ac9a5583be7abad100e749",
    "94": "8ff239dc62e523a047b0aba9ed83d49288b1dc3821e1539fff7968ded5cbb644",
    "95": "e80caf5d1d9a2062130b8040d289b4048d0cfd496b1acf4fe331f1802941bf90",
    "96": "cfbede37e9bd82cf630b995720d358cf57fd250f90109d2e330732ce62d0bcc8",
    "97": "dde081e461479970491fd13d04a445fd5aaced4f99b0f4954b78f4b9aaff4615",
    "98": "9def8f0f39f53ab822264a84e9f4e1cb32299c0399fa9d581f6fbd4fcc6d6201",
    "99": "7b6c02876efd8a08a3faaa0278074095453692b45b9df882ab28597189fa234b",
    "A0": "7b6c02876efd8a08a3faaa0278074095453692b45b9df882ab28597189fa234b",
    "A1": "7b6c02876efd8a08a3faaa0278074095453692b45b9df882ab28597189fa234b",
    "A2": "7b6c02876efd8a08a3faaa0278074095453692b45b9df882ab28597189fa234b",
    "A3": "5c4286ce1cfc5e1060e45ff80b4fc02e36b7ef4075eb4ac6e1b8f3ef006f9535",
    "A4": "70d55a1dd0d9b47a4e40155075e938222b7b827c8957987c60144679572b7875",
}
"""The 105 kit containers, by tag, measured off the Japanese disc 2026-09-20.

**The uniform is per team**, which is why it is not in the common texture file
(section 1.8): each of these holds the pages the body samples -- (576, 256),
(576, 384) and (704, 256) -- and the 256-entry palettes at (0, 486), (0, 488)
and (256, 480).  The geometry names two of those pages and neither is in
`DAT2D.BIN`, so until these had a digest the figure drew 237 primitives grey
(section 6 (f)).

The tags run `00` to `99` and then `A0` to `A4`: base ten until it runs out of
two digits, and a letter after that.  Not an index -- `kit_path` builds the
name from the tag, and `KIT_TAGS` is the order they sort in.

**Identical on both discs**, measured the same day: all 105 read equal on the
Japanese dump and on the English one that drives the emulator, and all 105 are
form 1 on both.  They are guarded all the same, because a third disc is the
thing the guard exists to refuse.
"""

KIT_TAGS = tuple(sorted(KIT_DIGEST))

KIT_ON_SCREEN = "A4"
"""The kit the two save states wear, measured off VRAM on 2026-09-20.

`oracle.py --kit` reads the rectangles every container declares out of the
console's own frame buffer and compares them halfword for halfword: on both
states TEX_A4 reproduces the page at (576, 384) and the palettes at (0, 486)
and (0, 488) exactly, and no other container reproduces any of the three --
the nearest, TEX_95, differs in 789 halfwords of them.

**A default for the two states, not a rule for every team.** Which container a
team wears is not measured here; what is measured is which one these two
screens uploaded, and that is what the window draws with until a task asks the
other question.
"""

TEXTURE_FILES = frozenset({DAT2D})
"""Files that may only ever be read from the Japanese disc."""

GEOMETRY_FILES = frozenset({EDT_MOD, MODEL})
"""Files proven identical on both discs, so either may supply them.

The set is exactly the keys of BASE, and self_check() asserts that: these are
the files the game loads whole at a known address and this cycle walks as
sections.
"""

ANIMATION_FILES = frozenset({ANIME})
"""Identical on both discs too, and loaded whole -- but not geometry.

Measured on 2026-09-17 (LOOKS-TASK-24): the same 396,804 bytes and the same
digest on both dumps, so either disc may answer for it.  It is kept out of
GEOMETRY_FILES because that set is the keys of BASE, which `spans()` and
`verify_load()` walk expecting a file `section.scan` can read; ANIME.BIN is
not one, and its load address is ANIME_BASE.
"""

SCREEN_ART_FILES = frozenset({EDT_2D})
"""The screen's own 2D art, identical on both discs.

Measured on 2026-09-21 (LOOKS-TASK-31): /BIN/EDT_2D.BIN holds 4-bit images
in the VRAM columns 704-1023 of the lower half, and the LOOKS SET text, the
title and the bar beside the plate are cut from them.  Its palettes are not here -- the sprites take theirs from
DAT2D.BIN's rows 496-499 -- which is why it is a family apart from
TEXTURE_FILES: this one may be read off either disc.
"""

SCREEN_SPRITES = (
    ("title", (768, 256), (128, 498)),
    ("icon", (768, 256), (80, 499)),
    ("shirt boxes", (576, 0), (176, 496)),
    ("bar", (960, 256), (0, 497)),
    ("plate", (576, 0), None),
)
"""The static sprites of LOOKS SET, by (name, page, CLUT) in VRAM coordinates.

Measured on 2026-09-21 (LOOKS-TASK-31, fifth pass): `oracle.py --scenery`
splits the list the frame hands the GPU into commands, and these five groups
are 14 of its 142 sprites, the same in both states and cut from EDT_2D.BIN
(title, icon, bar) and DAT2D.BIN (boxes, plate).  The plate's CLUT is `None`
because it is not a constant of the screen: it follows the player's position,
`PLATE_CLUT`.  Left out on purpose: the font (LOOKS-TASK-37), the help text
the game writes into VRAM (LOOKS-TASK-39) and the arrows, which follow the
cursor (`ARROW_PAGE`).
"""

PLATE_CLUT = {"GK": (192, 499), "CB": (208, 499)}
"""The plate's CLUT by the position it reads, the only two measured.

Slot 1 is a goalkeeper and draws the plate's four sprites through (192, 499);
slot 2 is a centre back and draws the same four through (208, 499) -- same
page, same `uv`, same place (LOOKS-TASK-31).  A position neither state holds
has no measured CLUT, and the screen refuses it rather than borrow one.
"""

ARROW_PAGE = (704, 0)
"""The page the two arrows beside the cursor's value are cut from.

`uv` (128, 248) is the one on the right and (128, 240) the one on the left,
both 8x8 through the CLUT (80, 497) of DAT2D.BIN.  Where each one shows is
measured by the screen walk and kept in screen.json (LOOKS-TASK-36)."""

RECORD_FILES = frozenset({SELECT})
"""Japanese-only too, but records rather than art -- so a hint of its own.

/SELECT.BIN is the second of the two files that differ between the discs, and
it holds the player records.  Folding it into TEXTURE_FILES would refuse it
with a sentence about palettes, which is the wrong thing to go looking at.
"""

KIT_FILES = frozenset(KIT_DIR + KIT_PREFIX + tag + KIT_SUFFIX
                      for tag in KIT_DIGEST)
"""The kit containers as paths, for the guard's families below."""


def kit_path(tag: str) -> str:
    """The disc path of one kit container, by its tag.

    Refuses a tag nobody measured rather than building a name for it: a file
    this project has no digest for cannot be read through the guard anyway,
    and a path built here would fail three frames later with a message about
    digests instead of about the tag.
    """
    if tag not in KIT_DIGEST:
        raise WrongDisc("%r is not one of the %d kit tags measured on this "
                        "disc" % (tag, len(KIT_DIGEST)))
    return KIT_DIR + KIT_PREFIX + tag + KIT_SUFFIX


def kit_tag(disc_path: str) -> str:
    """The tag of a kit path, or a refusal."""
    head, tail = KIT_DIR + KIT_PREFIX, KIT_SUFFIX
    if not (disc_path.startswith(head) and disc_path.endswith(tail)):
        raise WrongDisc("%s is not a kit container" % disc_path)
    return disc_path[len(head):-len(tail)]


CODE_FILES = frozenset({SELECT8, SELECTC, BOOT})
"""Japanese-only as well, and CODE: the overlay the LOOKS SET screen runs.

Read for the stature rule (`STATURE_*` below), which is the same instructions
and the same table on both discs -- measured 2026-09-18, the bytes the rule is
made of compare equal in the Japanese file, the English file and the running
game's RAM.  The file as a whole is not, because the overlay also carries the
screen's text and the translation rewrote it.  So the guard reads it from the
Japanese disc like everything else that differs, and the hint says why.
"""

# The whole-image digest of the Japanese dump, so a recipe can confirm it is
# pointed at the right dump before reading anything.  Both copies on this
# machine -- roms/japanese-shift-jis.bin and the we-2002-original-japao.bin
# under C:\games\ps1\roms\we2002\ -- are this same dump, 307,187,664 bytes,
# measured 2026-09-14.  The English one is 306,834,864 bytes.
IMAGE_DIGEST_JAPANESE = (
    "e853eb14f5bddd50a4a5e77a1da4d22c989a0d99ad5a4927e24e1dba7475abf3"
)
IMAGE_SIZE_JAPANESE = 307187664
IMAGE_SIZE_ENGLISH = 306834864


# --- Where each file sits on the disc -------------------------------------
#
# Measured 2026-09-14 from the directory of roms/japanese-shift-jis.bin, and
# identical on the English disc -- the translation patch replaces content
# in place and moves nothing.  Nothing here READS by LBA (iso.py resolves the
# path through the filesystem, which is what makes the tooling survive a
# different dump); these are recorded because the plan cites them and because
# a changed LBA is the first sign of a rebuilt image.
LBA = {
    EDT_MOD: 5000,
    MODEL: 8100,
    DAT2D: 5300,
    SELECT: 850,
    ANIME: 3000,
    SELECT8: 1800,
    EDT_2D: 3900,
    SELECTC: 1950,
    BOOT: 24,
}

SIZE = {
    EDT_MOD: 36072,
    MODEL: 64800,
    DAT2D: 81124,
    SELECT: 300648,
    ANIME: 396804,
    SELECT8: 125176,
    EDT_2D: 40360,
    SELECTC: 106966,
    BOOT: 337920,
}

# --- Where each model file loads in RAM -----------------------------------
#
# KSEG0 addresses.  Both files are raw -- not LZSS, unlike DAT2D.BIN -- and
# the game copies them to these addresses untouched, which is why a pointer
# inside the file is an absolute RAM address and not a file offset.
#
# These are the constants derive_base() is checked AGAINST, never the source
# of the answer: see require_base().
BASE = {
    EDT_MOD: 0x8011C000,
    MODEL: 0x8016E800,
}

MODEL_GEOMETRY_START = 1816
"""Offset of the first MODEL.BIN section: 107 vertices, 88 primitives.

The number the `we3d` analysis reports for section 0, re-measured here.

EDT_MOD.BIN has no constant beside this one on purpose: its first section is
DERIVED, by geometry_start(), because deriving it is what would have caught
the scan that began at 15,704 and reported the file as read (CORR-LOOKS-010).
"""

# --- The BIN container's record model -------------------------------------
#
# A record list closes with the pair [bank word][RECORD_LIST_END], and every
# record of it carries that same bank word in field 7.  `tools/pes2/bin_archive.py`
# documents that word as "0x800f, a constant tag"; LOOKS-TASK-10 measured that
# it is the 64 KiB page of the 16-bit offset in field 6, biased so bank 0 reads
# 0x800f.  The four discs that project measured never needed the bank, because
# no payload of theirs sits past the first 64 KiB.  This one does: DAT2D.BIN's
# palettes are at bank 1 and DATSEL.BIN's images at bank 3.
RECORD_TAG_BASE = 0x800F  # not-an-address: field 7 when the payload is in bank 0
RECORD_BANK = 0x10000  # not-an-address: the 64 KiB page that field 7 counts
RECORD_LIST_END = 0x00FF  # not-an-address: the halfword that closes a list

VRAM_WIDTH = 1024  # not-an-address: PSX frame-buffer width in 16-bit units
VRAM_HEIGHT = 512  # not-an-address: PSX frame-buffer height in rows
CLUT_ROW_FIRST = 480
"""The first VRAM row a palette may live on.

The strip at the bottom of the frame buffer that PSX games keep CLUTs in, and
the rule `bin_archive.py` already states.  On this disc the four skin palettes
are rows 480 to 483, the boots row 484, and 256 narrow palettes fill 496..511.
"""

TEXTURE_EXPECTED = {
    # (image records, clut records, palettes of 16 entries, palettes of 256)
    DAT2D: (23, 267, 262, 5),
}

TEXTURE_BANK = {
    # (first byte of the palette payloads, first byte of the record list that
    # indexes them).  The payloads tile exactly between the two: 262 x 32 B
    # plus 5 x 512 B is 10,944 B, and 65,892 + 10,944 is 76,836.
    DAT2D: (65892, 76836),
}

HEAD_SECTION = 24
"""The MODEL.BIN section that is the head.

Named by LOOKS-TASK-09 -- it is the piece HAIR, FACE and SKIN share, and the
only one of the twelve that does not live in EDT_MOD.BIN.  `pieces.py` carries
the same number for the same reason; it is here as well because `atlas.py`
addresses the section by index and rule 1 owns indices into a named file.
"""

HAIR_PRIMITIVES = (1, 14)
"""The two primitives of HEAD_SECTION whose `v` the HAIR field walks.

Measured in RAM by LOOKS-TASK-08 with the game running: a step of HAIR adds
0x20 to the `v` of all four corners of these two and of nothing else.  They are
the whole evidence of section 1.8 -- their `u` is 176..199, past the halfway
mark of a 4-bit page, so what they sample is the SECOND image record of that
page and not the first.
"""

FACE_PRIMITIVES = (8, 13)
"""The two primitives of HEAD_SECTION whose `v` the FACE field walks.

Measured in RAM by LOOKS-TASK-11, both save states, a step of 0x10.  They were
nearly recorded as one primitive: `report_field` printed four hits, which is
exactly one textured quad, and the second of the pair was below the cut.
Their `u` is 152..174 -- past the halfway mark, like the hair's -- so FACE
samples the SAME image record the hair does.
"""

HAIR_IMAGE = 3568
"""The DAT2D.BIN image record hair, facial hair and face detail come from.

VRAM (544, 256), the second half of texture page 0x18.  The CARP table calls
this one "Caras" and calls 8 "Pelos"; the zeta tutorial sends the reader here
for hair.  LOOKS-TASK-11 measured that the tutorial is right -- both the two
primitives HAIR moves and the two FACE moves sample this record, and neither
field touches the one at 8.
"""

FLAG_IMAGE = 10248
"""The one other DAT2D.BIN image the geometry samples, at VRAM (672, 384).

136 primitives reach it, all of them from MODEL.BIN sections 0 and 1 -- none of
the twelve pieces LOOKS-TASK-09 named.  The CARP table calls it "Banderin
pelotas"; nothing here confirms that, and the measured claim is only that the
player is not what samples it.
"""

DAT2D_SCENE_LABELS = {
    # `Offsets WE2002 - CARP/Dat/DAT2D.BIN.txt`, transcribed 2026-09-15 so that
    # what the scene says and what the disc says can be compared row by row.
    # Opinion, not measurement: its other seventeen rows are blank or a
    # signature, and its line 20 misconverts its own hex D59C to 23,964
    # instead of 54,684.
    8: "Pelos Cuerpos y botines",
    3568: "Caras",
    7456: "Cuerpo",
    9296: "Redes del arco",
    10248: "Banderin pelotas",
    22200: "Banderitas del menu",
}

SKIN_IMAGE = 8
"""The DAT2D.BIN image record at VRAM (512, 256): bodies, boots and bare skin.

The first half of the same page, and by far the most sampled thing in the
container.  CARP's label for it, "Pelos Cuerpos y botines", is right about the
bodies and the boots and wrong about the hair.
"""

SKIN_PALETTES = (65892, 66404, 66916, 67428)
"""The four 256-entry palettes at VRAM (0, 480) to (0, 483), one per skin.

LOOKS-TASK-10 found them by tiling the palette bank; LOOKS-TASK-08 found which
one a figure uses by moving SKIN on the screen and watching the CLUT id walk
0x40 at a time, which is exactly one VRAM row.  The CARP table calls them
"Pieles A" to "Pieles D" and gets the fourth wrong -- it prints 67,248 where the
record says 67,428, two digits swapped in its own arithmetic.

They are a tuple and not four names because the index IS the field's value:
`skin_colour` is two bits in `src/core/Player.cpp`, and row = 480 + that.
"""

HAIR_MATRIX_FIRST = 65924
"""Where the eight hair colours of the first skin start: SKIN_PALETTES[0] + 32.

The offsets of the zeta tutorial's table, read out of the PDF in 2026-09-15
rather than summarised: `Tipo A` of `Raza Blanca` is 65,924, and the table walks
32 bytes per type and 512 per race.  **Thirty-two bytes past the skin palette's
own start**, which is the thing that makes it the FIRST hair colour and not the
zeroth -- LOOKS-TASK-12's own criterion wrote the matrix as
`65892 + race*512 + kind*32`, off by one column, and the disc says otherwise:
column 0 of each record is the bare-skin window, which no hair colour uses.
"""

HAIR_MATRIX_RACE_STEP = 512
"""512 B is 256 entries is one whole palette record, so one VRAM row."""

HAIR_MATRIX_KIND_STEP = 32
"""32 B is 16 entries is one 4-bit CLUT, so one step of x in the CLUT id."""

HAIR_MATRIX_KINDS = 8
"""Eight hair colours, `Tipo A` to `Tipo H` in the tutorial's own table.

The same eight `src/core/Player.cpp` packs into the three bits of
`hair_colour`, and the same eight for `beard_colour` beside it.  Two witnesses
that never met, agreeing on a count.
"""

BARE_SKIN_COLUMN = 0
"""Column 0 of a skin record: the window with no hair colour in it.

446 primitives name it -- the bare arms, legs and faces -- and it is the only
column whose sixteen entries look nothing like the other fifteen.
"""

HAIR_COLUMN = 1
"""The column `hair_colour` 0 selects.

Measured on the screen: the head's primitives carry column 1 on the disc, and
one step of H.COL takes byte 2 of the CLUT id from 1 to 2 on both save states.
The zeta table starts at the same place from the other side -- its `Tipo A` is
32 bytes past the record.
"""

BEARD_COLUMN = 9
"""The column `beard_colour` 0 selects.

Measured the same way: the two FACE primitives carry column 9 on the disc, and
one step of H.F.COL. takes them from 9 to 10, on both slots.

`src/core/Player.cpp` gives `beard_colour` three bits, and eight columns from 9
would need a column 16, which a 256-entry record does not have.  The screen
settles it: walked end to end by `oracle.py --palettes`, H.F.COL. reaches
**seven** values, columns 9 to 15, and the grid comes out exactly full.
"""

BOOT_SECTIONS = (9, 10)
"""The two EDT_MOD.BIN sections the BOOTS field rewrites, in both slots.

The only two sections the two figures share byte for byte, which is how
LOOKS-TASK-09 named them the feet before BOOTS was asked; `pieces.py` carries
the same pair as BOOTS_SECTIONS, per slot, and this is the file-level name
`oracle.py --assembly` addresses one of them by.
"""

HEAD_RUNS = ((24, 56), (74, 106))
"""The two runs of MODEL.BIN sections that are heads, as half-open ranges.

**Thirty-two sections each, byte for byte distinct** -- and that is a count of
SECTIONS, not of bodies.  Measured 2026-09-16, remeasured by CORR-LOOKS-029:
the first run holds **twelve** distinct vertex arrays and the second 24, and
fifteen of the first run's sixteen pairs share theirs byte for byte.  Thirty-two
is exactly what `hair_style` holds and two runs is exactly the two figures
EDT_MOD.BIN's two lists already showed, which is what makes the coincidence
worth refusing rather than reading.

All 32 of the first run sample HAIR_IMAGE and 16 of the second do, but **not
each with its own window**: the 32 take **fourteen** distinct windows on that
sheet, several shared -- 25, 26 and 27 take one between them -- and sections
32, 33, 36 and 37 take none at all.  `assembly.hair_windows` measures it and
`assembly.HEAD_RUN_WINDOWS` asserts it.

**The anchoring is measured, and it is not `24 + N`.**  On 2026-09-16
`oracle.py --patched HAIR` read the whole loaded file after every press and
found the row rewriting the **even** sections of the first run, one per LETTER
of the style's label: A is 24, B is 26, C 30, D 48, F 52, G 28, I 34, J 36,
K 32, L 46, O 44, P 50 -- and E in TWO, E1 in 48 which is D's and E2 in 54
which is its own, so thirteen sections for twelve whole letters and one split.
The digit picks a sixteen-row band of HAIR_IMAGE inside that section.  The table is `assembly.HAIR_MAP`, which also carries the
three values that rewrote nothing and the three even sections nobody named.

**And the goalkeeper's hair is the FIRST run too.**  Walked on slot 1
(CORR-LOOKS-047), the row rewrites the same even sections with the same bands,
and not one section of 74..105 moved at any press.  So "two runs, two figures"
is still the coincidence it was: what the second run is, nothing has measured.

The first run is therefore **sixteen pairs** rather than 32 independent heads:
`assembly.head_pairs` measures what separates a pair, and it is the beard.
"""

HAIR_QUADS = {
    24: (1, 14),
    26: (1, 3),
    34: (0, 1, 12),
    46: (0, 9, 17),
}
"""Which primitives of a head take the hair band, per MODEL.BIN section.

Measured 2026-09-16 by `oracle.py --writes`, which puts an EXECUTE breakpoint
on HAIR_QUAD_STORE and reads `a0` -- the primitive the game is writing -- at
every hit while the row is walked.  Four of the thirteen sections the row
visits came out this way; the other nine are written somewhere else, because
walking every value of the row never stopped that instruction with their
addresses in `a0`.

**So this is a measured four, not a rule for thirteen.**  The obvious rule --
"the primitives that sample the hair sheet in the hair colour's column" -- is
measured WRONG: section 30 has twelve of those and the game rewrites two.

**And the twins of these four take the same indices.**  When FACE picks the
odd section (FACE_TWIN_QUADS), the game rewrites 25's 1 and 14, 27's 1 and 3,
35's 0, 1 and 12 and 47's 0, 9 and 17 with the store's rows -- read off
`oracle.py --patched FACE` on 2026-09-16 (CORR-LOOKS-048).
"""

FACE_TWIN_QUADS = {
    25: (8, 13),
    27: (4, 7),
    29: (9, 17),
    31: (0, 3),
    33: (7, 10, 11),
    35: (7, 10, 11),
    37: (7, 10, 11),
    45: (7, 10, 11),
    47: (6, 7, 8),
    49: (0, 3),
    51: (7, 10, 11),
    53: (0, 3),
    55: (7, 10, 11),
}
"""The beard quads of each head's TWIN, the odd section FACE F and G draw.

Measured 2026-09-16 by `oracle.py --patched FACE 2 <tuple>` from a tuple on
each of the thirteen heads HAIR names (CORR-LOOKS-048): beard F rewrites
nothing of the even section and writes the odd one after it, and beard G moves
these primitives of that odd section by one band.  Section 25 is the pair
LOOKS-TASK-11 named on section 24, FACE_PRIMITIVES, one section along.

The twin holds its beard at band 5 on the disc, which is F; G is band 6.
"""

HAIR_QUAD_ROWS = (15, 1, 15, 1)
"""The row inside a band that the game writes into each corner's `v`.

Read off the store below: `v1 = band * 16 + 15` goes to bytes 0x1 and 0x9 of
the primitive -- corners 0 and 2 -- and `v0 = band * 16 + 1` to 0x5 and 0xd,
corners 1 and 3.  **An absolute value, not a displacement.**  The disc does not
hold these rows: section 24 keeps 14/1, 26 keeps 14 and 0 or 1, 34 keeps 15/2,
46 keeps 79/66.  Adding the band to the disc's `v` drew every hair quad a row
off -- measured in the game's own display list, where section 24's two quads
carry `v` 15 and the file 14 (CORR-LOOKS-042).
"""

HAIR_QUAD_STORE = 0x80011590
"""The instruction in the GAME that writes a hair quad's `v`.

Found on 2026-09-16 by a write watchpoint on section 24's own quad
(LOOKS-TASK-14), which stopped one instruction past it:

    0x80011580  andi  v0, a2, 0x00ff      the band, as the caller passed it
    0x80011584  sll   v0, v0, 4           ATLAS_BAND rows a band
    0x80011588  addiu v1, v0, 15
    0x8001158C  addiu v0, v0, 1
    0x80011590  sb v1, 0x1(a0)            <- this one
    0x80011594  sb v0, 0x5(a0)
    0x80011598  sb v1, 0x9(a0)
    0x8001159C  sb v0, 0xd(a0)

An **execute** breakpoint here is what turns "which bytes changed" into "which
primitive of which section, and with what band" -- `a0` is the primitive and
`a2` is the band -- and it sees a write even when the value written is the one
already there, which a memory diff cannot.

It is an address in the game's own code, not in a file this project reads, and
it is here for the same reason every other address is.
"""

ATLAS_BAND = 16
"""Rows of an image record that one step of HAIR or of FACE walks.

Measured 2026-09-15 by `oracle.py --assembly`, pressing each row from the
bottom of its range to the top: the `v` of the two primitives each owns moves
in blocks of sixteen rows of the record at HAIR_IMAGE, and never anything else.
"""

COLOUR_PRIMITIVES = {
    "SKIN": {
        24: (0, 1, 2, 4, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17),
        25: (0, 1, 2, 4, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17),
        26: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 20, 21),
        27: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 20, 21),
        28: (0, 1, 2, 4, 6, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25),
        29: (0, 1, 2, 4, 6, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25),
        30: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 24),
        31: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 24),
        32: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        33: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        34: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        35: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        36: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        37: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        44: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 27, 30, 31),
        45: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 27, 30, 31),
        46: (0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 24, 25, 28, 29, 30, 32, 33),
        47: (0, 1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 24, 25, 28, 29, 30, 32, 33),
        48: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23),
        49: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23),
        50: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 20, 21, 22, 23, 24, 26),
        51: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 20, 21, 22, 23, 24, 26),
        52: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 21, 22, 23, 24, 25),
        53: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 21, 22, 23, 24, 25),
        54: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        55: (0, 1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 19, 20, 21, 22),
    },
    "H.COL": {
        24: (0, 1, 2, 4, 5, 7, 9, 12, 14, 15, 16, 17),
        25: (0, 1, 2, 4, 5, 7, 9, 14, 15, 17),
        26: (0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 18, 19, 20, 21),
        27: (0, 1, 3, 5, 8, 9, 11, 12, 14, 15, 18, 19, 20, 21),
        28: (0, 1, 2, 4, 6, 8, 10, 12, 13, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25),
        29: (0, 1, 2, 6, 8, 10, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25),
        30: (1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 24),
        31: (1, 2, 4, 6, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 24),
        32: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        33: (0, 1, 2, 5, 8, 9, 12, 15, 16, 17, 19, 20, 22),
        34: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        35: (0, 1, 2, 5, 8, 9, 12, 15, 16, 17, 19, 20, 22),
        36: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        37: (0, 1, 2, 5, 8, 9, 12, 15, 16, 17, 19, 20, 22),
        44: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 27, 30, 31),
        45: (0, 1, 2, 5, 8, 9, 12, 15, 16, 17, 19, 20, 22, 23, 24, 25, 27, 30, 31),
        46: (0, 1, 2, 4, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 24, 25, 28, 29, 30, 32, 33),
        47: (0, 1, 2, 4, 9, 11, 12, 13, 15, 16, 17, 18, 22, 24, 25, 28, 29, 30, 32, 33),
        48: (1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23),
        49: (1, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23),
        50: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 20, 21, 22, 23, 24, 26),
        51: (0, 1, 2, 5, 8, 9, 12, 15, 16, 17, 20, 22, 23, 24, 26),
        52: (1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 21, 22, 23, 24, 25),
        53: (1, 2, 4, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 21, 22, 23, 24, 25),
        54: (0, 1, 2, 5, 8, 9, 12, 13, 15, 16, 17, 19, 20, 21, 22),
        55: (0, 1, 2, 5, 8, 9, 12, 15, 16, 17, 19, 20, 22),
    },
    "H.F.COL.": {
        24: (8, 13),
        25: (8, 12, 13, 16),
        26: (4, 7),
        27: (2, 4, 6, 7),
        28: (9, 17),
        29: (4, 9, 16, 17),
        30: (0, 3),
        31: (0, 3, 5, 7),
        32: (7, 10, 11),
        33: (7, 10, 11, 13, 21),
        34: (7, 10, 11),
        35: (7, 10, 11, 13, 21),
        36: (7, 10, 11),
        37: (7, 10, 11, 13, 21),
        44: (7, 10, 11),
        45: (7, 10, 11, 13, 21),
        46: (6, 7, 8),
        47: (6, 7, 8, 10, 14),
        48: (0, 3),
        49: (0, 3, 5, 7),
        50: (7, 10, 11),
        51: (7, 10, 11, 13, 21),
        52: (0, 3),
        53: (0, 3, 5, 6),
        54: (7, 10, 11),
        55: (7, 10, 11, 13, 21),
    },
    "FACE": {
        24: (8, 13),
        26: (4, 7),
        28: (9, 17),
        30: (0, 3),
        32: (7, 10, 11),
        34: (7, 10, 11),
        36: (7, 10, 11),
        44: (7, 10, 11),
        46: (6, 7, 8),
        48: (0, 3),
        50: (7, 10, 11),
        52: (0, 3),
        54: (7, 10, 11),
    },
}
"""Row -> {MODEL.BIN head section: the primitives that row moves there}.

**Measured 2026-09-16 by `oracle.py --colour <ROW> 2 <tuple ...>`**
(CORR-LOOKS-049), from a tuple on each of the thirteen heads HAIR names and on
each one's twin (beard F): the row walked to the bottom and to the top, and at
each end the loaded file read until two reads 300 frames apart agree.  A
primitive belongs to the row where its CLUT id -- or, for FACE, its texcoords
between A and E -- differs between the two ends.  Slot 1 was walked on six of
the same starts and came back identical.

**Every head has its own**, and that is the finding: the colour rows had been
applied to the other twelve heads by the indices of section 24, and on 34 SKIN
moves eighteen primitives that are not section 24's fourteen.  FACE has no twin
entries: F and G draw the twin with FACE_TWIN_QUADS.  A head missing here is a
head whose colour is not known, and the assembly refuses it.
"""

HAIR_COLOUR_PRIMITIVES = COLOUR_PRIMITIVES["H.COL"][HEAD_SECTION]
"""The HEAD_SECTION primitives whose CLUT id the H.COL field walks: twelve.

**This said seven until 2026-09-16** -- `(0, 1, 4, 9, 14, 16, 17)`, "the whole
hit list, not a sample".  It was a sample: read before the game had finished
rewriting the head (trap 18 of the profile), and remeasured from the two
settled ends of the row (CORR-LOOKS-049).  HAIR_PRIMITIVES is still a subset.
"""

SKIN_COLOUR_PRIMITIVES = COLOUR_PRIMITIVES["SKIN"][HEAD_SECTION]
"""The HEAD_SECTION primitives whose CLUT id the SKIN field walks: fourteen.

A step adds 0x40 to byte 2, one whole 256-entry record -- the row of the grid,
with the column left where it was.  **This said eight until 2026-09-16**,
`(0, 1, 8, 9, 13, 14, 16, 17)` from `oracle.py --fields SKIN`, and the union of
the three colour fields was written down as nine of eighteen, with primitive 4
the one place "row x column" did not hold (CORR-LOOKS-026).  Both were the same
partial read: from the two settled ends SKIN moves fourteen, H.COL's twelve are
all among them, primitive 4 included, and four primitives of the head -- 3, 6,
10 and 11 -- move with no colour row (CORR-LOOKS-049).
"""

BOOTS_PALETTE = 67940
"""The palette the boots sample, at VRAM (0, 484).

The CARP table labels this offset "Botines".  What confirms it is not the label
but the geometry: the two EDT_MOD.BIN sections LOOKS-TASK-09 named the feet --
by mirroring and by being the only two both figures share -- sample this
palette and nothing else, and no other section samples it.
"""

PLAYER_RECORD_OFFSET = 157164
PLAYER_RECORD_COUNT = 1449
PLAYER_RECORD_SIZE = 12
"""The packed appearance/attribute records inside /SELECT.BIN.

1,449 x 12 B = 17,388 B ending at 174,552, inside the file's 300,648.

**The offset came from a third party and is now measured**, by two witnesses
that never met it: `OFS_PLAYER_ATTR` of `src/core/include/we2002/Offsets.hpp`
resolves to exactly this byte of exactly this file (`tools/pes2/ofs_map.py`),
and that offset is one the golden tests verify against `ed.exe`.

**The count came from the same third party and was wrong.**  It said 1,242
until 2026-09-15, when LOOKS-TASK-13 measured 1,449 twice over: it is
`PLAYERS_TOTAL - PLAYERS_NC` of `src/core/include/we2002/Types.hpp`, which is
what `Database::Load` reads, and the disc says the same without being asked --
the first 1,449 records decode to a height between 155 and 202, and record
1,449 is the first that is all zero.
"""


class WrongDisc(Exception):
    """Raised when a file is read from a disc that may not supply it."""


class BadPointerList(Exception):
    """Raised when a header pointer does not lead to a list of the known shape."""


class WrongBase(Exception):
    """Raised when the load address derived from a file is not the known one."""


def digest(data: bytes) -> str:
    """sha256 of *data*, hex, lowercase -- the one spelling used here."""
    return hashlib.sha256(data).hexdigest()


def is_trusted(disc_path: str, data_digest: str) -> bool:
    """Is *data_digest* the content this project expects at *disc_path*?

    Unknown paths answer False rather than True: a file nobody measured is
    not a file anybody may trust.
    """
    return expected_digest(disc_path) == data_digest


def expected_digest(disc_path: str) -> str | None:
    """What this project measured at *disc_path*, or None for a path it has
    not measured.  The kit containers are 105 of the answers and live in
    their own table, so that DIGEST stays the short list a reader can read."""
    if disc_path in DIGEST:
        return DIGEST[disc_path]
    if disc_path in KIT_FILES:
        return KIT_DIGEST[kit_tag(disc_path)]
    return None


def _hint_for(disc_path: str) -> str:
    """The sentence that names the real problem behind a refusal at *disc_path*.

    Every path in DIGEST has to get one.  The families are not decoration: a
    mismatch means something different for each, and the reader is being told
    where to look.  self_check() walks DIGEST and demands a non-empty answer
    for every entry, because the way this went wrong the first time was by
    omission -- /SELECT.BIN belonged to no family and fell through to "",
    leaving the bare "digest mismatch" the docstring above calls the failure.
    """
    if disc_path in TEXTURE_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and textures and palettes may only "
            f"be read from the Japanese one.  Point {ENV_IMAGE} at it; "
            f"{ENV_DRIVE_IMAGE} is the disc you drive, not the disc you read."
        )
    if disc_path in RECORD_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and the player records are read from "
            f"the Japanese one.  Point {ENV_IMAGE} at it; {ENV_DRIVE_IMAGE} "
            f"is the disc you drive, not the disc you read."
        )
    if disc_path in CODE_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch -- it is the screen's overlay, text "
            f"included -- and code is read from the Japanese one like "
            f"everything else that differs.  Point {ENV_IMAGE} at it; "
            f"{ENV_DRIVE_IMAGE} is the disc you drive, not the disc you read."
        )
    if disc_path in KIT_FILES:
        return (
            f"  {disc_path} is one of the {len(KIT_FILES)} kit containers, "
            f"and they read identical on both known discs -- so a mismatch "
            f"means a third disc, another release or a modified image."
        )
    if disc_path in SCREEN_ART_FILES:
        return (
            f"  {disc_path} is the screen's own art and reads identical on "
            f"both known discs, so a mismatch means a third disc -- another "
            f"release, or a modified image."
        )
    if disc_path in GEOMETRY_FILES | ANIMATION_FILES:
        return (
            f"  {disc_path} is identical on both known discs, so a mismatch "
            f"means a third disc -- another release, or a modified image."
        )
    return ""


def require(disc_path: str, data: bytes, image: str = "<unknown image>") -> bytes:
    """Return *data*, or refuse it with a message that names the real problem.

    The message matters as much as the refusal.  The mistake this guards is
    "you opened the English disc", and an exception that only says "digest
    mismatch" sends the reader looking at the parser instead.
    """
    got = digest(data)
    if is_trusted(disc_path, got):
        return data

    expected = expected_digest(disc_path)
    if expected is None:
        raise WrongDisc(
            f"{disc_path}: nothing measured for this path, so nothing to "
            f"trust it against (read from {image})"
        )

    hint = _hint_for(disc_path)

    raise WrongDisc(
        f"{disc_path}: read {got} from {image}, expected {expected}.{hint}"
    )


def derive_base(data: bytes) -> tuple[int, int]:
    """Derive the KSEG0 load address of a model file from its own header.

    Returns (header_words, base).

    The method, not the number, is what matters -- a constant nobody can
    re-derive is a constant nobody can check.  Both model files open with a
    run of KSEG0 pointers, and the run ends at the first word that is not one
    (a count, or the 0x000000FF terminator).  The lowest of those pointers
    aims at the first byte past the run, because that is where the record
    list begins.  So:

        base = min(header pointers) - 4 * (number of header words)

    Measured 2026-09-14, and it is one rule for both files even though their
    headers are very different sizes:

        EDT_MOD.BIN   2 words, min 0x8011C008, 0x8011C008 - 8  = 0x8011C000
        MODEL.BIN    18 words, min 0x8016E848, 0x8016E848 - 72 = 0x8016E800

    The 2 and the 18 are not guessed: `lzss.py -v` reports the same header
    lengths for these files ("header 2 w -> stream at 8"), from its own
    reading, which is a second witness to where the run ends.

    **Do not run this over the whole file.** Vertex and colour data is full of
    words with the top bit set -- 642 of them in EDT_MOD.BIN, 1,703 in
    MODEL.BIN -- and only a few dozen are pointers.  Reading those as an
    address table produces targets in the billions and a base that means
    nothing.  The run at the head is bounded precisely because it stops at the
    first non-pointer.
    """
    if len(data) < 8:
        raise WrongBase("file is %d bytes: too short to hold a header" % len(data))

    words = len(data) // 4
    header = 0
    while header < words:
        word = int.from_bytes(data[header * 4:header * 4 + 4], "little")
        if word < 0x80000000:
            break
        header += 1
    else:
        raise WrongBase("every word is a KSEG0 pointer: this is not a model file")

    if header == 0:
        raise WrongBase(
            "the file does not start with a KSEG0 pointer (first word is "
            "0x%08x), so it has no pointer table to derive a base from"
            % int.from_bytes(data[0:4], "little")
        )

    pointers = [
        int.from_bytes(data[i * 4:i * 4 + 4], "little") for i in range(header)
    ]
    base = min(pointers) - 4 * header

    # Every pointer in the run has to land inside the file under that base.
    # This is the cross-check that makes the answer an answer: a base derived
    # from a coincidence would send some of its own siblings out of range.
    for index, pointer in enumerate(pointers):
        target = pointer - base
        if not 0 <= target < len(data):
            raise WrongBase(
                "base 0x%08x puts header pointer %d (0x%08x) at %d, outside "
                "the file's %d bytes" % (base, index, pointer, target, len(data))
            )

    return header, base


def pointer_density(data: bytes, base: int) -> tuple[int, int]:
    """Count the words that look like pointers, and those that land inside.

    Returns (words with the top bit set, of those, how many fall inside the
    file under *base*).  This is the measurement behind derive_base()'s
    warning not to sweep the whole file: vertex and colour data is full of
    words with the top bit set, and only a few dozen of them are addresses.
    The docstring there carries the two pairs as prose; this is how a caller
    re-derives them instead of trusting the prose.

    It lives here rather than in the caller because 0x80000000 is an address,
    and rule 1 of the plan puts every address in this file -- a caller
    counting high-bit words itself would be caught by --sweep, correctly.
    """
    high = 0
    inside = 0
    for index in range(len(data) // 4):
        word = int.from_bytes(data[index * 4:index * 4 + 4], "little")
        if word < 0x80000000:
            continue
        high += 1
        if 0 <= word - base < len(data):
            inside += 1
    return high, inside


LIST_TERMINATOR = 0x000000FF  # not-an-address: the word that closes a pointer list


def read_pointer_list(data: bytes, offset: int, base: int) -> list[int]:
    """The targets of the record list at *offset*, as file offsets.

    Thin wrapper over read_pointer_entries(); most callers want only the
    offsets.  A caller that has to tell one kind of entry from another -- and
    is_derivable() does -- wants the tags too.
    """
    return [target for _tag, target in read_pointer_entries(data, offset, base)]


def read_pointer_entries(data: bytes, offset: int, base: int) -> list:
    """Read one record list at *offset* and return its (tag, offset) entries.

    The shape this reads, measured 2026-09-14 on EDT_MOD.BIN: pairs of (tag,
    KSEG0 pointer) closed by LIST_TERMINATOR.  Both of that file's lists carry
    a [count][pad] header before the pairs, and whether a list has one can be
    read off the file rather than assumed -- if the second word is a pointer,
    the pairs have already begun.

    **The variant MODEL.BIN uses, measured 2026-09-14 by LOOKS-TASK-05: a
    (0, 0) pair is an EMPTY SLOT, not the end.** The earlier reading called
    the list at 672 malformed -- "it closes with 0x00000000 at 736 rather than
    with LIST_TERMINATOR" -- and that was wrong twice over.  The word at 736 is
    entry 8 of a pair whose tag is also zero, and the list goes on to close
    with LIST_TERMINATOR at 768 like every other one.  Skipping the empty pair
    reads it as ten targets, and all six lists that were refused read cleanly.

    A zero pointer is skipped rather than kept because it is not an address:
    keeping it would put offset 0 -- the file header -- in a list of section
    starts, and a scan handed that walks into the pointer table.

    Every target is checked against the file's length.  A list that does not
    close, or that aims outside, raises: guessing here would produce a
    plausible list of offsets and a scan that walks into the middle of a
    section.
    """
    words = len(data) // 4

    def word(index):
        if not 0 <= index < words:
            raise BadPointerList(
                "pointer list at %d runs past the file's %d bytes"
                % (offset, len(data))
            )
        return int.from_bytes(data[index * 4:index * 4 + 4], "little")

    if offset % 4:
        raise BadPointerList("pointer list at %d is not word-aligned" % offset)

    index = offset // 4
    if word(index + 1) < 0x80000000:
        index += 2  # a [count][pad] header, as in EDT_MOD.BIN

    targets = []
    while True:
        tag = word(index)
        if tag == LIST_TERMINATOR:
            return targets
        pointer = word(index + 1)
        if tag == 0 and pointer == 0:
            index += 2  # an empty slot -- see the docstring
            continue
        if pointer < 0x80000000:
            raise BadPointerList(
                "pointer list at %d: entry %d holds 0x%08x, which is not a "
                "KSEG0 pointer and is not the terminator"
                % (offset, len(targets), pointer)
            )
        target = pointer - base
        if not 0 <= target < len(data):
            raise BadPointerList(
                "pointer list at %d: entry %d aims at %d, outside the file's "
                "%d bytes" % (offset, len(targets), target, len(data))
            )
        targets.append((tag, target))
        index += 2


def record_lists(data: bytes) -> list[list[int]]:
    """Every record list the header of *data* names, in header order.

    EDT_MOD.BIN has TWO, of eleven records each, sharing two of them.  Reading
    only one of the two is how a scan came to start 43% into the file and
    still close on an exact EOF -- the counts were right for what was read,
    and what was read was half the file (CORR-LOOKS-010).

    Raises BadPointerList on MODEL.BIN today: see read_pointer_list.
    """
    header, base = derive_base(data)
    pointers = [
        int.from_bytes(data[i * 4:i * 4 + 4], "little") for i in range(header)
    ]
    return [read_pointer_list(data, p - base, base) for p in pointers]


def geometry_start(data: bytes) -> int:
    """The offset of the first section: the lowest target of any header list.

    Derived rather than stored, which is the same choice derive_base() makes
    and for the same reason: a constant nobody re-derives is a constant nobody
    checks.  Here it is also the fix for a specific failure -- a scan handed a
    hand-picked start reported an exact EOF and looked complete.

    EDT_MOD.BIN answers 216.

    **MODEL.BIN must NOT use this, and the reason is measured rather than
    procedural.** Since the empty-slot variant was understood its header lists
    all read, so the obstacle is no longer parsing -- it is the answer.
    Sixteen of its eighteen header pointers lead to lists that open with an
    entry tagged 0x80, and those entries aim at one of TWO flat runs of bare
    KSEG0 pointers: twelve at offset 104, which is 64 pointers long, and four
    at offset 232, which is 32.  Neither run is a section, and neither is a
    shape this function reads.  min over all targets therefore answers 104,
    which would hand a scan a start inside a pointer table and fail in the
    exact way deriving the start was introduced to prevent.

    The other two header pointers lead to lists of ONE entry, tagged 0x02, and
    those do name sections: 1816 and 4792, the file's first two.  So the lists
    DO state the constant -- a derivation by lowest 0x02-tagged target answers
    1816, measured.  MODEL_GEOMETRY_START stays a constant because it is cheap
    and because that derivation has not been exercised on any second file, not
    because the information is absent (CORR-LOOKS-013 measured both claims:
    this docstring used to say every list aims at 104, and that 1816 was a
    fact the lists do not state).
    """
    if not is_derivable(data):
        raise BadPointerList(
            "this file's lists name a target that is not a section (the "
            "0x80-tagged entry), so the lowest target is not the start of "
            "geometry -- use the file's recorded constant instead"
        )
    targets = [t for one in record_lists(data) for t in one]
    if not targets:
        raise BadPointerList("the header names no record at all")
    return min(targets)


def require_base(disc_path: str, data: bytes) -> int:
    """Derive the load base of *data* and demand it match the known constant.

    The constant is in BASE and the answer comes from the file, so the two
    disagreeing is a real event: a different release, a modified image, or a
    file that is not the one its name says.
    """
    expected = BASE.get(disc_path)
    if expected is None:
        raise WrongBase("%s: no load address recorded for this file" % disc_path)

    _header, got = derive_base(data)
    if got != expected:
        raise WrongBase(
            "%s: header derives base 0x%08x, expected 0x%08x -- a different "
            "release, a modified image, or not this file at all"
            % (disc_path, got, expected)
        )
    return got


def self_check() -> None:
    """Exercise the guard on made-up bytes, including the case that must fail.

    Synthetic on purpose: this runs on a machine with no image, no venv and
    no display, which is the contract of the selftest gate.  The live
    demonstration against the two real discs is `--check-discs`.
    """
    # Green: the measured content passes, by construction.
    body = b"whatever"
    saved = DIGEST[DAT2D]
    try:
        DIGEST[DAT2D] = digest(body)
        assert require(DAT2D, body, "fake") is body
        assert is_trusted(DAT2D, digest(body))

        # Red 1: the wrong content is refused, and the message says which
        # disc problem it is rather than just "mismatch".
        try:
            require(DAT2D, b"english", "fake")
        except WrongDisc as exc:
            text = str(exc)
            assert "Japanese" in text, text
            assert ENV_IMAGE in text, text
        else:
            raise AssertionError("DAT2D guard accepted foreign content")
    finally:
        DIGEST[DAT2D] = saved

    # Red 2: a path nobody measured is refused rather than waved through.
    try:
        require("/BIN/NOSUCH.BIN", b"", "fake")
    except WrongDisc as exc:
        assert "nothing measured" in str(exc), str(exc)
    else:
        raise AssertionError("unmeasured path was trusted")

    # Red 3: geometry gets its own wording, because a mismatch there means a
    # third disc and not the English one.
    try:
        require(MODEL, b"not the model", "fake")
    except WrongDisc as exc:
        assert "third disc" in str(exc), str(exc)
    else:
        raise AssertionError("geometry guard accepted foreign content")

    # Red 4: EVERY measured path gets a hint, not just the three with a
    # family.  This one is a sweep rather than a case, on purpose: /SELECT.BIN
    # was refused with a bare "digest mismatch" for exactly as long as it
    # belonged to no family, and the next path added to DIGEST would inherit
    # that silence the same way -- by omission, which no single red case
    # catches.
    for measured in DIGEST:
        assert _hint_for(measured), "no hint for %s" % measured
        try:
            require(measured, b"content from the wrong disc", "fake")
        except WrongDisc as exc:
            text = str(exc)
            assert text.rstrip().endswith("."), text
            assert len(text) > len(
                "%s: read %s from fake, expected %s."
                % (measured, digest(b"x"), DIGEST[measured])
            ), text
        else:
            raise AssertionError("%s guard accepted foreign content" % measured)

    # And the two Japanese-only files say so by name, since "you opened the
    # English disc" is the overwhelmingly likely cause of either refusal.
    for japanese_only in TEXTURE_FILES | RECORD_FILES | CODE_FILES:
        assert ENV_IMAGE in _hint_for(japanese_only), japanese_only
        assert "Japanese" in _hint_for(japanese_only), japanese_only

    # -- the kit containers ------------------------------------------------
    #
    # They are 105 and they are guarded like everything else, which is the
    # whole point of measuring them: until they had a digest the figure drew
    # its body grey, because the guard cannot hand over what it cannot check.
    assert len(KIT_DIGEST) == len(KIT_FILES) == len(KIT_TAGS), len(KIT_DIGEST)
    assert all(kit_tag(kit_path(tag)) == tag for tag in KIT_TAGS)
    assert KIT_TAGS[0] == "00" and KIT_TAGS[-1] == "A4", KIT_TAGS[:1]
    for tag in KIT_TAGS:
        assert is_trusted(kit_path(tag), KIT_DIGEST[tag]), tag
    # Red: a kit is refused like any other path, and by a sentence that names
    # the third disc rather than by a bare mismatch.
    try:
        require(kit_path(KIT_TAGS[0]), b"another team's kit", "fake")
    except WrongDisc as exc:
        assert "third disc" in str(exc), str(exc)
    else:
        raise AssertionError("the kit guard accepted foreign content")
    # Red: a tag nobody measured has no path, and says so as a tag.
    try:
        kit_path("ZZ")
    except WrongDisc as exc:
        assert "kit tags" in str(exc), str(exc)
    else:
        raise AssertionError("kit_path built a name for an unmeasured tag")
    try:
        kit_tag(DAT2D)
    except WrongDisc as exc:
        assert "not a kit container" in str(exc), str(exc)
    else:
        raise AssertionError("kit_tag read a tag out of a file that has none")
    assert expected_digest("/BIN/NOSUCH.BIN") is None

    # The two disc variables are two different names.  They have been one
    # name before, in another project, and it cost twelve runs.
    assert ENV_IMAGE != ENV_DRIVE_IMAGE

    # -- derive_base, on a synthetic header shaped like the real ones -------
    #
    # Green: two header words whose lower pointer aims at offset 8.
    synthetic = (
        (0x8011C070).to_bytes(4, "little")
        + (0x8011C008).to_bytes(4, "little")
        + b"\x00" * 512
    )
    assert derive_base(synthetic) == (2, 0x8011C000), derive_base(synthetic)

    # Red 5: a base that would throw one of its own pointers out of the file
    # is refused rather than returned.  Same shape, but the high pointer now
    # aims far past the end.
    outside = (
        (0x8011C008).to_bytes(4, "little")
        + (0x8019C070).to_bytes(4, "little")
        + b"\x00" * 512
    )
    try:
        derive_base(outside)
    except WrongBase as exc:
        assert "outside the file" in str(exc), str(exc)
    else:
        raise AssertionError("derive_base accepted a base its own pointers deny")

    # Red 6: a file that does not begin with a pointer has no table to read,
    # and saying so beats returning a number computed from nothing.
    try:
        derive_base(b"\x02\x00\x00\x00" + b"\x00" * 32)
    except WrongBase as exc:
        assert "no pointer table" in str(exc), str(exc)
    else:
        raise AssertionError("derive_base invented a base for a headerless file")

    # Red 7: require_base reports the mismatch with both numbers, because
    # "wrong base" without the derived value says nothing about which disc.
    elsewhere = (
        (0x80200070).to_bytes(4, "little")
        + (0x80200008).to_bytes(4, "little")
        + b"\x00" * 512
    )
    assert derive_base(elsewhere) == (2, 0x80200000), derive_base(elsewhere)
    try:
        require_base(EDT_MOD, elsewhere)
    except WrongBase as exc:
        assert "expected 0x8011c000" in str(exc).lower(), str(exc)
    else:
        raise AssertionError("require_base accepted a foreign base")

    # pointer_density answers about the same synthetic vector: two header
    # pointers set the top bit, the 512 zero bytes do not, and both header
    # pointers land inside by construction -- which is what derive_base just
    # demanded.  The point of the function is the ratio it reports on a real
    # file, so the assertion here is only that it counts what it says.
    assert pointer_density(synthetic, 0x8011C000) == (2, 2), pointer_density(
        synthetic, 0x8011C000
    )
    assert pointer_density(bytes(64), 0x8011C000) == (0, 0)

    # -- the address tables agree with each other ---------------------------
    #
    # Every file with a digest has an LBA and a size; a path added to one map
    # and forgotten in the others is the omission this catches, the same way
    # red 4 catches a missing hint.
    for measured in DIGEST:
        assert measured in LBA, "no LBA for %s" % measured
        assert measured in SIZE, "no size for %s" % measured
    assert set(BASE) == GEOMETRY_FILES, (set(BASE), GEOMETRY_FILES)

    # The player records fit inside the file they are said to live in.
    span = PLAYER_RECORD_OFFSET + PLAYER_RECORD_COUNT * PLAYER_RECORD_SIZE
    assert span <= SIZE[SELECT], (span, SIZE[SELECT])

    # MODEL.BIN's geometry starts after its header, not inside it.
    assert MODEL_GEOMETRY_START > 18 * 4

    # -- record_lists and geometry_start, on a synthetic model file ---------
    #
    # Built in EDT_MOD.BIN's shape: a two-word header of pointers, each aiming
    # at a [count][pad] list of (tag, pointer) pairs closed by the terminator.
    # Two lists, and the answer is the LOWEST target of either -- which is the
    # whole point: reading one list and starting there is how nine sections
    # went unread while the scan still closed on an exact EOF.
    def _word(value):
        return value.to_bytes(4, "little")

    fake_base = 0x80100000
    #      0: -> list one at 8        4: -> list two at 40
    #
    # The lower header pointer aims at offset 8, the first byte past the
    # two-word run, because that is the rule derive_base() reads.
    model = _word(fake_base + 8) + _word(fake_base + 40)
    #      8: count, pad, then two records aiming at 200 and 120
    model += _word(3) + _word(0)
    model += _word(2) + _word(fake_base + 200)
    model += _word(2) + _word(fake_base + 120)
    model += _word(LIST_TERMINATOR)
    model += bytes(40 - len(model))
    #     40: a list with no [count][pad], aiming at 300 and 360, with an
    #         EMPTY SLOT between them -- a (0, 0) pair is not the end.
    #
    # The slot is in the MIDDLE and not at the front on purpose: a list that
    # opens with (0, 0) is swallowed by the [count][pad] heuristic above,
    # which reads any non-pointer second word as a preamble.  Planted at the
    # front, the branch this exercises never runs, and its negative control
    # comes out green -- measured.
    model += _word(2) + _word(fake_base + 300)
    model += _word(0) + _word(0)
    model += _word(2) + _word(fake_base + 360)
    model += _word(LIST_TERMINATOR)
    model += bytes(400 - len(model))

    assert derive_base(model) == (2, fake_base), derive_base(model)
    assert record_lists(model) == [[200, 120], [300, 360]], record_lists(model)
    assert geometry_start(model) == 120, geometry_start(model)

    # Red 11: the empty slot is SKIPPED, not stored and not treated as the
    # end.  Both wrong readings are silent -- storing it puts offset 0, the
    # file header, in a list of section starts; ending there hid six of
    # MODEL.BIN's eighteen lists behind "this list is malformed".  Without a
    # (0, 0) pair in the synthetic above, the branch that handles it never ran
    # and its negative control came out green.
    assert 0 not in record_lists(model)[1], record_lists(model)
    assert record_lists(model)[1] == [300, 360], record_lists(model)
    entries = read_pointer_entries(model, 40, fake_base)
    assert entries == [(2, 300), (2, 360)], entries

    # Red 9: a list that aims outside the file is refused, not returned.  A
    # plausible-looking offset here sends the scan into the middle of a
    # section, where it reads a vertex count out of colour data.
    far = model[:20] + _word(fake_base + 4000) + model[24:]  # the 200 pointer
    try:
        record_lists(far)
    except BadPointerList as exc:
        assert "outside the file" in str(exc), str(exc)
    else:
        raise AssertionError("a pointer list aiming past the file was accepted")

    # Red 10: a list that never reaches its terminator is refused rather than
    # read to the end of the file.
    unclosed = model.replace(_word(LIST_TERMINATOR), _word(2), 1)
    try:
        record_lists(unclosed)
    except BadPointerList as exc:
        assert "runs past the file" in str(exc) or "not a KSEG0" in str(exc), exc
    else:
        raise AssertionError("an unterminated pointer list was accepted")

    # -- the sweep itself, on a planted tree --------------------------------
    #
    # Red 8, and the reason it is here: --sweep is only ever run against the
    # real tree, which is clean, so it was only ever observed GREEN.  A sweep
    # that stopped matching .py, or blanked a line too eagerly, or resolved
    # its root to an empty directory, prints the same "no address outside
    # layout.py" and exits 0 -- the sentence a reader takes for proof.  The
    # tree below is built to be found in, so the sweep is watched working.
    planted = {
        "bad.py": ["BASE = 0x8011C000"],
        "ok.py": ["SHIRT = 0x1234  # not-an-address: a colour, not a pointer"],
        "above.py": ["# not-an-address: this annotation is on the wrong line",
                     "Y = 0x5678"],
        ADDRESS_OWNER: ["BASE = 0x8016E800"],
        os.path.join("ui", "deep.py"): ["OFFSET = 157164"],
        os.path.join("ui", ADDRESS_OWNER): ["BASE = 0x8016E800"],
    }
    with tempfile.TemporaryDirectory() as tmp:
        for name, body in planted.items():
            full = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as handle:
                for text in body:
                    print(text, file=handle)

        stats: dict = {}
        caught = {(where, number) for where, number, _ in
                  sweep_addresses(tmp, stats)}

        # A hex literal is found, and so is a four-digit decimal in a
        # SUBDIRECTORY -- which is what proves the walk descends.  os.listdir
        # would miss ui/ entirely, and the .mcr cycle lost a whole package
        # that way.
        assert ("bad.py", 1) in caught, caught
        assert (os.path.join("ui", "deep.py"), 1) in caught, caught

        # The escape works, and it works PER LINE: an annotation written on
        # the line above excuses nothing.
        assert not any(where == "ok.py" for where, _ in caught), caught
        assert ("above.py", 2) in caught, caught

        # The owner is exempt by path.  A same-named file in a subdirectory is
        # not the owner and does not inherit the exemption.
        assert not any(where == ADDRESS_OWNER for where, _ in caught), caught
        assert (os.path.join("ui", ADDRESS_OWNER), 1) in caught, caught

        # And the sweep says how much it read, so "swept nothing" stops
        # looking like "swept everything and found nothing".
        assert stats["files"] == len(planted) - 1, stats
        assert stats["lines"] == 6, stats

        empty_stats: dict = {}
        with tempfile.TemporaryDirectory() as nothing:
            assert sweep_addresses(nothing, empty_stats) == []
        assert empty_stats == {"files": 0, "lines": 0}, empty_stats

    print("layout: self_check ok")


def is_derivable(data: bytes) -> bool:
    """Can geometry_start() be trusted for this file?

    True when every entry of every header list is a plain section pointer.
    False when any entry carries the 0x80 tag, which MODEL.BIN uses for the
    entry that aims at its flat pointer array -- see geometry_start().

    **It reads the ENTRY tags, not the first word each header pointer lands
    on.** Those are the same word in MODEL.BIN, whose lists open straight into
    pairs, and different in EDT_MOD.BIN, whose lists carry a [count][pad]
    preamble.  A check that read the landing word answered correctly on both
    real files while comparing two different things, and a list that combined
    a preamble with a tagged entry walked past it.
    """
    try:
        header, base = derive_base(data)
        for index in range(header):
            pointer = int.from_bytes(data[index * 4:index * 4 + 4], "little")
            entries = read_pointer_entries(data, pointer - base, base)
            if any(tag == SUBLIST_TAG for tag, _target in entries):
                return False
    except (WrongBase, BadPointerList):
        return False
    return True


SUBLIST_TAG = 0x80  # not-an-address: the tag MODEL.BIN's lists open with

GEOMETRY_EXPECTED = {
    # (sections, vertices, primitives, end) for a scan from the file's start
    # of geometry.  Counts rather than addresses, but they belong here for the
    # same reason SIZE does: they are facts about one named file, and rule 1
    # keeps modelfile.py free of numbers it would otherwise have to carry.
    #
    # **Each one is only meaningful with the offset the scan began at**, which
    # is why GEOMETRY_START sits beside it.  A scan of EDT_MOD.BIN from 15,704
    # reports 11/690/611 and an exact EOF, looks complete, and is 43% of the
    # file (CORR-LOOKS-010).
    MODEL: (106, 2461, 1767, 64800),
    EDT_MOD: (20, 1218, 1074, 36072),
}

GEOMETRY_START = {
    MODEL: MODEL_GEOMETRY_START,
    EDT_MOD: 216,
}
"""Where a scan of each file begins.

EDT_MOD.BIN's entry is the answer geometry_start() derives, kept here so a
caller can compare the two; MODEL.BIN's is the constant, because its lists do
not state it.  self_check() demands the derived and the recorded agree.
"""


TMD_CLAIMED = (0x8016821C, 0x80168C0C, 0x8016A2C4, 0x8016A650)
"""The four textured TMDs section 1.6 of the plan records living in RAM.

Recorded there on 2026-09-13 as unknown (a) -- real Sony TMDs, already fixed by
`OpenTMD`, textured, with 92, 261, 30 and 18 vertices, belonging to neither
model file.  They are here because they are ADDRESSES and this module owns
addresses, and because what LOOKS-TASK-08 measured about them has to sit beside
them: **in both save states all four hold nothing but zeros**, and the TMDs that
really are in RAM on that screen are 29 small ones between 0x800C1678 and
0x800C4948, 4 to 54 vertices each, that no LOOKS field touches.  So the four
addresses are not reproducible from the states, and nothing in this cycle may
be built on them.
"""

TMD_MAGIC = 0x00000041
"""The first word of a Sony TMD."""


# --- the LOOKS SET screen, in the game's own RAM and code -----------------
#
# Found on 2026-09-17 by LOOKS-TASK-21, on the ENGLISH disc the emulator is
# driven with -- the text the screen writes is the patch's, so these are
# addresses of that build of the game, and the measurement that uses them
# re-proves each one every run rather than trusting it.

SCREEN_PRINT = 0x8010AA0C
"""The game routine that prints ONE text object.

Found by a read watchpoint on the row labels (`DEFAUL\\nNAT \\n...`), which
stopped in the glyph loop; this is the entry of the function around it.  `a0`
is the object:

    +0  s16  x, from the centre of the 512x240 display
    +2  s16  y, likewise
    +6  u16  width of the box the text is laid out in
    +8  u32  pointer to the string, with the control bytes screen.py decodes
    +12 u8   kind: 32 and 33 are the ASCII fonts this screen uses

An execute breakpoint here stops eight times per frame on LOOKS SET -- once per
object, all twelve rows in five objects -- where the glyph routine below stops
268 times.  That is what makes walking every value of every row affordable.
"""

SCREEN_GLYPH = 0x8010BB04
"""The game routine that draws ONE glyph: `a0` the code, `a1` x, `a2` y.

`a3` says which of two passes: 1 is the pass that measures the string's width
(every glyph at the same x), 0 is the pass that draws it.  Only the draw pass
is what the screen shows, and it is the witness the decoding of SCREEN_PRINT's
strings is checked against.

It does not touch the GPU.  Read on 2026-09-21 (LOOKS-TASK-31): it fills a
libgs `GsSPRITE` in the scratchpad at 0x1F8000B8 -- width off a table, height
12, page word 27, which is VRAM (704, 256) at 4 bits, and CLUT (0, 497) -- and
its caller hands that to the sprite sort with the frame's own `GsOT`, whose tag
is the head GPU_LIST_SUBMIT sends.  So the text IS in the list, as sprites.
"""

SELECTC_BASE = 0x800FC000
"""Where `/SELECTC.BIN` loads in RAM while LOOKS SET runs.

Measured by content on 2026-09-22 (LOOKS-TASK-37): the 64 bytes at
SCREEN_GLYPH occur once on each disc, at offset 0xFB04 of this file, and the
glyph table at 0x8010D008 at 0x11008 -- the same distance apart as in RAM.
SELECT8.BIN, the overlay the stature rule is in, ends at 0x800E98F8 and holds
neither.
"""

GLYPH_ROUTINE = (0x8010BB04, 0x8010C0D8)
GLYPH_ROUTINE_DIGEST = (
    "3610cf53539d5c36a55f71d5a57ff2f8e85e180715a46121fda17545f420fcfe"
)
"""The glyph routine, SCREEN_GLYPH up to the word after its `jr ra`, and the
sha256 of its bytes.

`glyphs.py` transcribes the routine's code ranges -- which code takes its `u`
and width from the table and which `v` each band of codes gets -- and a
transcription is only as good as the code it was read from.  So the rule is
refused unless these bytes are the ones it was read from: the same on the
Japanese disc, the English disc and the running game's RAM (2026-09-22).
"""

GLYPH_TABLE = 0x8010D008
"""(u, width) byte pairs, one per character code from 32 up.

The routine indexes it by `code - 32` for codes 32 to 127, and by `code - 65`
for 161 to 166 -- which reads pairs 96 to 101, right after the ASCII ones.
"""

GLYPH_PAGE = (704, 256)
GLYPH_CLUT = (0, 497)
GLYPH_HEIGHT = 12
"""What the routine writes into every glyph's `GsSPRITE`, whatever the code:
page word 27 -- VRAM (704, 256) at 4 bits --, CLUT (0, 497), height 12."""

SCREEN_HELP = 0x800E8338
"""A pointer to the help string the box at the bottom shows.

The setter at 0x800CFCC8 compares its argument against this pointer with
`strcmp` and redraws only when they differ, so this is the text on screen, not
the text asked for.  Found by a read watchpoint on `Skin Colour` in Shift-JIS,
which fired inside that `strcmp` when Down moved the cursor to SKIN.
"""

# --- The help box's text, and where its glyphs come from -------------------
#
# Measured 2026-09-22 (LOOKS-TASK-39).  The help box's letters are not cut
# from any image on the disc: the game asks the CONSOLE for each one.  The
# chain, and every address of it, is below; `oracle.py --help-box` re-measures
# it against the running game and refuses each instruction that is not what it
# is said to be.

BOOT_MAGIC = b"PS-X EXE"
BOOT_HEADER = 2048  # not-an-address: the bytes of the PS-EXE header
BOOT_LOAD_FIELD = 0x18  # not-an-address: `t_addr` in that header
BOOT_SIZE_FIELD = 0x1C  # not-an-address: `t_size`, the word after it
BOOT_BASE = 0x80010000
"""Where `/SLPM_870.56` loads, read out of its own PS-EXE header.

The constant is what the header is checked AGAINST, the way `BASE` is checked
against `derive_base()`: a file offset of an address is
`BOOT_HEADER + address - BOOT_BASE`, and if the header ever says otherwise the
offsets below are pointing at the wrong bytes and the guard should say so.
"""

HELP_PAGE = (832, 256)
HELP_CLUT = (64, 496)
HELP_ICON_CLUT = (32, 498)
"""The VRAM page the help box's text is drawn from, and the two CLUTs its
sprites carry: the letters take the first, the button glyph `■` the second.
What puts the `■` on that second palette is NOT `HELP_ICON_CODES`: the `■` is
`0x81A1`, one of the four codes of `HELP_SPECIAL_SPAN`, drawn from a fixed
place in VRAM instead of rendered, and none of those four is in the table of
22.

Nothing on the disc holds this page's texels, and nothing can: the game writes
them from the console's character ROM, one 16x16 tile per character of the
string, every time the help text changes.
"""

HELP_TILE = 16
HELP_GLYPH_SIZE = (16, 15)
HELP_GLYPH_BYTES = 30
"""One character: a 16x15 bitmap of 30 bytes in the console's ROM, one bit a
pixel and each row a big-endian halfword, drawn into a 16x16 tile of the page.
"""

HELP_GLYPH_CALL = 0x800331B8
HELP_GLYPH_RETURN = 0x800331C0
"""The `jal` that asks for one character's bitmap, and the instruction the
answer comes back to -- the call's delay slot sits between them.

`s3` there is the walk over the Shift-JIS string (two bytes a letter, one for
a space), and `v0` on return is the address of the bitmap.
"""

HELP_GLYPH_LOOKUP = 0x8003BEEC
HELP_LOOKUP_WORDS = 40
"""The routine that call reaches, and how far into it the BIOS call is looked
for.  It range-checks the Shift-JIS code against three windows -- 895, 599 and
4052 codes wide -- and hands what survives to the stub below; a code outside
them all comes back as the code for a blank.
"""

HELP_SPECIAL_SPAN = (0x80033000, 0x80033130)
HELP_SPECIAL_COUNT = 4
"""The span of the renderer's dispatch that names the codes it does NOT ask
the ROM for, and how many there are.

Four of them, each an `ori v0, zero, <code>` inside the span: `0x819A`,
`0x819C`, `0x81A1` and `0x81A3`.  A code in the set is drawn from a fixed
place in VRAM rather than rendered, which is why the `■` of `Skin Colour   ■
Turn` is the one sprite of the box on `HELP_ICON_CLUT` -- and which is why
there are fourteen lookups for fifteen tiles.  Where ITS texels come from was
not measured.
"""

HELP_ICON_CODES = 0x800BCA58
HELP_ICON_COUNT = 22
"""A table of 22 halfwords the renderer compares every code against before it
draws, and which decides the palette: a code in it comes out on
`HELP_ICON_CLUT`.

It is NOT what puts the `■` of the box on that CLUT.  The `■` is `0x81A1`,
one of the four codes of `HELP_SPECIAL_SPAN`, which measured that -- and
none of `0x819A`, `0x819C`, `0x81A1`, `0x81A3` is among these 22.

Where the table comes from, measured on the disc 2026-09-23:
`/SELECT.BIN` + 253728, 22 little-endian halfwords (`0x9B89`, `0x9BBD`, ...
`0xE7E9`), and those 44 bytes occur exactly once in the file; LOOKS-TASK-39
matched them byte for byte against the RAM at the address above.  Right
after them, at `/SELECT.BIN` + 253772, come 22 blocks of 32 bytes that read
as 16x16 one-bit bitmaps -- rows as big-endian halfwords, the sixteenth row
blank in all 22, which is the 16x15 of `HELP_GLYPH_SIZE` padded -- and the
run stops at exactly 22: the 32 bytes after it are not a bitmap.

Recorded, not read: this cycle draws none of it.  That those bitmaps are the
glyphs of these codes is their adjacency and their count, not a measured
upload -- nothing here was watched being loaded or drawn.
"""

KROM_STUB = 0x8003873C
KROM_TABLE = 0xB0
KROM_FUNCTION = 0x51
"""The BIOS call the lookup ends in: `addiu t2, zero, 0xB0` / `jr t2` /
`addiu t1, zero, 0x51`, which is the kernel's B table, function 0x51 -- the
character-ROM lookup (`Krom2RawAdd` in the psx-spx notes).

What it answers is an address in `BIOS_ROM`, and that is the measurement this
cycle needed: the texels are the console's, not the disc's.
"""

HELP_IMAGE_LOAD = 0x8003A780
HELP_UPLOAD = 0x8003A950
HELP_COPY_COMMAND = 0xA0  # not-an-address: the GP0 code for a CPU-to-VRAM copy
"""The library routine that copies one tile into the page, and the address a
VRAM write watchpoint over that page reported in ONE run.

**`HELP_UPLOAD` is where the watch stopped, not who wrote, and it is not
stable** (pitfall 96): the copy is a DMA, so the program has moved on by the
time the GPU touches video memory.  The watch answered 0x8003A950 in two runs
and 0x8003F2F4 and 0x8010A910 in the two after those.  What it does assert is
the **rectangle**, and that the keypress caused it.

Who writes is read off the disc instead, and that is the measured half: at
0x8003A884 and 0x8003A8B8 of `/SLPM_870.56` -- the only two in the routine,
0x8003A780 through 0x8003A980 -- sits `lui a0,0xA000` (0x3C04A000), so `a0`
there is `0xA0000000`, the GP0 command that copies a rectangle from memory into
VRAM, and the rectangle is four halfwords by sixteen rows, which at four bits a
texel is exactly one 16x16 tile.
"""

BIOS_ROM = (0xBFC00000, 0x80000)
"""The console's ROM window: base and size.

A pointer inside it is not on the disc and never will be.  This is the whole
answer to "where do the help box's texels come from", and it is why the window
keeps drawing that box's text with a stand-in instead of with the game's own
glyphs.
"""

PLAYER_RAM = (0x8007DF60, 0x800E9450)
"""The two live copies of the twelve bytes of the player LOOKS SET edits.

Found by decoding every offset of RAM with `looks.decode` against what the
screen shows on both states -- three offsets matched -- and then pressing Right
on HEIG and on AGE: these two followed (175 to 176, 23 to 24) and the third,
0x800E9470, stayed where it was.  Both are read and required to agree; which
of the two the game draws from is not measured.
"""

ANIME_BASE = 0x8017EE00
"""Where `/BIN/ANIME.BIN` is loaded while the LOOKS SET screen runs.

**Measured by content, not derived**, on 2026-09-17 (LOOKS-TASK-24): a 64-byte
run from offset 1,000 of the file occurs exactly once in the two megabytes of
RAM, at 0x8017F1E8, and from that base the WHOLE file matches -- 396,804 of
396,804 bytes, on both save states.  It sits right after MODEL.BIN, which ends
at 0x8017E5E0.

**`derive_base()` does not derive it, and that is worth knowing before anyone
tries.**  Two things defeat the rule there.  The run of KSEG0 pointers is read
as "words with the top bit set", and this file's payload opens with
0x9000040A, which has it -- so the run does not stop at the header's end.  And
even with the run cut at 204 words, where the pointers really end, the rule's
second half fails: it assumes the lowest pointer aims just past the run, and
this file's lowest aims at offset 912, not 816.  So the base it WOULD compute
is 0x8017EE60, ninety-six bytes high; written by hand into a copy of the tree
it is the red control of `--pose`, where 279,034 of the 396,804 bytes differ
and not one of the 204 header entries is read.  Called on this file as it
stands, the function raises `WrongBase` -- the first reason fires first, and
nobody ever sees that base come out of it (CORR-LOOKS-059).

It is deliberately NOT in `BASE`: that dict is the model files', and `spans()`
and `verify_load()` walk it expecting a file `section.scan` can read.
"""

POSE_MATRIX = 0x80012168
POSE_MATRIX_SECOND = 0x8001229C
"""The two instructions that hand the GTE most of its rotation matrices here.

`ctc2` into control register 0, the matrix's first word.  Found on 2026-09-17
(LOOKS-TASK-24) by scanning RAM for every `ctc2` that writes that register --
**30** of them -- arming an execute breakpoint on all thirty at once and
letting the screen run: **five** ever run, and these two carry the traffic.
The split `oracle.py --pose` prints, on both slots of two runs a day apart
(2026-09-17 and 2026-09-18), is **18 and 18 of 40 stops**, against 2 for
0x8003C990 and 1 each for 0x80010E38 and 0x800407C0.  This said "18 and 17 ...
against 2, 2 and 1" until 2026-09-18 (CORR-LOOKS-058): that split sums to 40
too, and is not the one any run produces.

**One `continue` names the wrong thing.**  The emulator breaks on the first
hit and stays there, so a single run answers "which fired first": the same
thirty, armed the same way, named 0x80012168 in one run and 0x80010E38 in the
next.  Both were true and neither was the question.

**Which load is which, measured on 2026-09-18 (LOOKS-TASK-25).**  They are
not two of a kind: `POSE_MATRIX` hands the GTE the SAME rotation at every
stop of a draw pass while its translation walks the pieces -- the camera --
and `POSE_MATRIX_SECOND` hands a different rotation per piece, changing
every frame.  `POSE_PIECE_MATRIX` below is the name the pose capture uses,
so that nothing reads the pose off the camera by picking the wrong one.
"""

ANIME_UNPACK = 0x80011D48
ANIME_UNPACK_BASE = "s0"
"""The instruction that reads a piece's pair out of the ANIME.BIN frame.

`lw v0, 0x0(s0)`, and **`s0` is the pair itself** -- measured on 2026-09-18
(LOOKS-TASK-26): it walks the file eight bytes at a time, one pair per piece,
on both save states, and every value of it lands inside the file.

This is the bridge between a pose capture and the file, and it replaced a
worse one.  The animation state (`ANIME_STATE`) names a frame, and reading it
at each matrix load looked like enough: it is, for the outfield player, and it
is NOT for the goalkeeper, whose angles then matched nothing in 3952 frames.
A pointer that names where the game IS reading beats a pointer that names
where the game says it is playing.
"""

POSE_ANGLES = 0x1F800120
"""Scratchpad, where the three angles of the piece being drawn are unpacked.

Measured on 2026-09-18 (LOOKS-TASK-26): the code at 0x80011D48 reads the
piece's first word out of the ANIME.BIN frame and writes three halfwords here
-- `sll 22 / sra 18`, `sll 12 / sra 22 / sll 4`, `sll 2 / sra 22 / sll 4`, so
three SIGNED 10-bit fields at bits 9:0, 19:10 and 29:20, each shifted left by
four.  The routine at 0x8003D4BC is then called with this address and turns
them into the matrix.  It is the bridge between the pose capture and the file:
what ANIME.BIN stores of a pose is these numbers.
"""

POSE_PIECE_MATRIX = POSE_MATRIX_SECOND
POSE_PIECE_MATRIX_BASE = "v1"
POSE_MATRIX_BASE = "a0"
"""The per-piece matrix load, and the register each load reads it through.

The matrix is not in the instruction and not in the GTE yet: five `lw`/`ctc2`
pairs copy it from a 32-byte struct in memory, and the struct's address is in
this register when the first `ctc2` is about to run.  Reading the struct is
what makes the capture EXACT -- reading the GTE instead would take the
previous piece's matrix, because at the stop the load has not happened.

Both structs are the same shape: nine 4.12 halfwords of rotation at offsets 0
to 0x10, two of padding, then three 32-bit translations at 0x14, 0x18, 0x1C.
`POSE_MATRIX` reads its own through `a0`, which is `sp + 16` -- the camera on
the stack in scratchpad -- and `POSE_PIECE_MATRIX` reads the piece's through
`v1`.
"""

ANIME_STATE = 0x80076040
ANIME_STATE_LIST = 0x18
ANIME_STATE_FRAME = 0x1C
ANIME_STATE_INDEX = 0x329
"""The animation the screen is playing, as the game keeps it.

Measured on 2026-09-17 (LOOKS-TASK-24) by reading the code around the two
instructions a read watchpoint on `ANIME.BIN` caught:

    +0x18   the pointer the header entry gave -- the animation's frame list
    +0x1C   the frame being played, taken from that list
    +0x329  the index into the list, a byte, stepped every time and reset to
            zero when the word beside the entry says the list has ended

The list is walked at 0x80027838..0x8002787C: index, `lw` the entry, compare,
step or wrap, then `lw` the frame pointer and store it at +0x1C.  That wrap is
the walk cycle repeating, and it is why the figure keeps walking with nothing
pressed.
"""

ANIME_BUILD = 0x80011EF0
ANIME_BUILD_BASE = "s0"
"""The call that turns a pair's angles into a matrix, and the pair register.

`jal 0x8003D4BC` -- `RotMatrix` -- with the three angles already unpacked into
`POSE_ANGLES` and **`s0` still holding the pair they came out of**, after every
adjustment the unpack variant made to it.

**This is the stop to watch, and `ANIME_UNPACK` is not**, measured on
2026-09-23 (LOOKS-TASK-32).  Ten unpack variants share the dispatch at
`ANIME_VARIANT_DISPATCH`, and `ANIME_UNPACK` is one of them: a pass drawn by
another variant stops there for nobody, which is why half the pose captures of
LOOKS-TASK-26 carried no pair on any piece and were set aside.  Every variant
falls through to this one call, so a watch here names the pair of all twelve
pieces of every pass -- 480 of 480 stops over forty passes, against 132 of 480
at the unpack.
"""

ANIME_VARIANT_DISPATCH = 0x80011DA0
ANIME_VARIANT_TABLE = 0x80050634
ANIME_VARIANT_COUNT = 10
"""Where the game chooses HOW to unpack a pair, and how many ways there are.

`sltiu v0, v1, 10 / lw v0, 0x634(at) / jr v0`, with `v1` two less than the
byte the caller passed: a jump table of ten entries, entered only when the
flag byte just before `ANIME_BLEND_MODE`'s struct is not zero.  The entries
differ in two things and nothing else, and both are what the walk's second
half is made of (LOOKS-TASK-32): they move `s0` by a whole number of pairs
(`addiu s0, s0, 8` and `16`, falling through in pairs for 24) and they negate
or turn the angles as they store them -- `anime.WALK_RULES`.

Named here, and read by nothing: the rules are measured from the angles the
game left in the scratchpad, pair by pair, and the table is what says the
count of them is ten and not "some".
"""

ANIME_BLEND = 0x80011F90
ANIME_BLEND_MODE = 0x80075FF8
ANIME_BLEND_KEPT = 0x1A0
"""The averaging path, the byte that selects it, and where it keeps a matrix.

`lhu` the freshly built halfword, `lh` the kept one at `+0x1A0` of the piece's
record, `addu`, `sra 1`, `sh` it back: `(a + b) >> 1` over the nine halfwords
of the rotation and the three words of the place.  The byte at `0x0(s3)`
chooses -- 0 stores the fresh matrix into the record and draws it, 1 averages
and stores the average, 2 discards the fresh one and draws the kept one.

**The byte is 1 at 24 of the 408 loads of a cycle and 0 at the other 384**,
and 2 at none of them -- measured over both slots (LOOKS-TASK-32).  The 24 are
the visit that opens a side of the walk, one per piece, and the average there
is exact: the fresh matrix alone lands up to 202 units out.  So the averaging
is real and it is narrow, which is what `anime.WALK_BLEND_AT` models; what it
is NOT is the explanation of the whole of the walk's second half, and that is
what it was taken for until the mirror was measured.
"""

ANIME_SCREEN_ENTRY = 5
"""The header entry the LOOKS SET screen plays.

Measured on 2026-09-17 (LOOKS-TASK-24) with a read watchpoint over all 204 at
once: it is the only one the screen reads.  An index, not an address, and it
is here because `anime.py` must not choose an animation by its size.
"""

ANIME_HEADER_WORDS = 204
"""Pointer entries at the head of `ANIME.BIN`, each one an animation.

The screen plays entry 5: the game loads it from ANIME_BASE + 0x14 and keeps
the pointer in its animation state, which is what a read watchpoint over all
204 entries caught -- and only that entry is ever read on this screen.
"""

PLAYER_NATION = (0x800E7E0C, 0x800E946B)
"""The byte the `NAT` row of LOOKS SET writes: the player's nationality.

Not one of the twelve, which is the point -- `NAT` is a row of that screen and
not a field of the record (`looks.UNSTORED`).

**The byte is a nation CODE, and the code is not the row's position.** Values 1
to 54 hold 0 to 53, and from 55 on the code JUMPS 41: `Iceland`, the row's
value 55, holds 95, and the row ends at 119.  The rule and the two runs it is
made of are `looks.NATION_CODES` and `looks.nation_code`; whoever needs the
code asks them, and never arithmetic written here.

This said "it is stored as the row's index **minus one**" until 2026-09-17
(CORR-LOOKS-057), which is true of the first 54 values and false of the other
25.  It came from five samples that all landed under the jump -- the same
inference the walk that measured the row records as its own problem 2 -- and
the byte is plausible at any value, so nothing shows when it is wrong.

Found on 2026-09-17 (LOOKS-TASK-23) by two runs of the SAME number of presses
from one `load_state`, landing on different nations -- eleven Rights against
six Rights and five Lefts -- and keeping the bytes that differ.  **The equal
press count is the whole method:** the first attempt walked to three nations
with three different numbers of presses and turned up twenty-one bytes that
"stepped with the index", all of which were CLOCKS -- they kept counting when
nothing was pressed.

A third value confirmed these, and leaving the screen separated them from a
fourth (0x800E96C8) that the next screen reuses.  The second address is
0x800E9450 + 27, so the twelve-byte record this cycle reads sits inside a
larger player structure and the nationality is 27 bytes into it.

On a freshly loaded state, with the row showing `Unknown`, the two do not hold
a nation index and do not even agree (253 and 139); one press makes them agree.
What the screen shows for every other non-nation value is NOT measured.
"""

SELECT8_BASE = 0x800CB000
"""Where `/SELECT8.BIN` loads in RAM: the LOOKS SET screen's overlay.

Derived, not assumed: on 2026-09-18 (LOOKS-TASK-29) the stature code caught
writing the figure's scale ran at 0x800E5890, and its 48 bytes occur once on
the whole Japanese disc, at offset 0x1A890 of this file -- the table the code
reads, 0x800E8220 in RAM, sits at 0x1D220 of it, the same distance apart.
"""

STATURE_HEIGHT_BIAS = 0x800E589C
STATURE_HEIGHT_SHIFT = 0x800E58AC
STATURE_TABLE_LOAD = 0x800E58A8
STATURE_TABLE_EXTRA = 0x800E58B0
STATURE_MAGIC_HIGH = 0x800E58E4
STATURE_MAGIC_LOW = 0x800E591C
STATURE_MAGIC_SHIFT = 0x800E593C
STATURE_WIDTH_STORES = (0x800E58FC, 0x800E58F8)
STATURE_HEIGHT_STORE = 0x800E594C
"""The instructions that turn `HEIG` and `BODY` into the figure's scale.

Found on 2026-09-18 (LOOKS-TASK-29) by a write watchpoint on the scale vector
(`FIGURE_SCALE`) with `Right` pressed on `BODY`, and read in full:

    h = HEIG field + 148                       STATURE_HEIGHT_BIAS, addiu
    x = z = (h << 12) / (table[BODY] + 10)     SHIFT, TABLE_LOAD, TABLE_EXTRA
    y     = (h << 12) / 180                    MAGIC_HIGH/LOW, MAGIC_SHIFT

The `/ 180` is not a `div`: it is the compiler's multiply by the magic
0xB60B60B7 and a shift of 7, and `stature.rule` turns those two back into the
divisor instead of this file writing 180 down.  The two width stores go to
the x and z words, the height store to y -- which is what says WHICH axis the
height alone decides.  `stature.rule` reads every one of these out of the
file and refuses one that is not the instruction it is said to be.
"""

STATURE_TABLE = 0x800E8220
"""Eight bytes, one per `BODY` value A to H: the width divisor, less ten.

Read by `STATURE_TABLE_LOAD` as `lbu v1, -0x7DE0(at)` with `at` = 0x800F0000
+ BODY, so the address is also derived by `stature.rule` from the instruction
itself and compared with this one.
"""

FIGURE_SCALE = 0x80075CDC
FIGURE_ANGLES = 0x80075CD4
FIGURE_PLACE = 0x80075CB6
"""The figure's own transform, as the game keeps it between frames.

`FIGURE_SCALE` is three 32-bit words, x y z, in 4.12 -- (3258, 3982, 3258) on
both save states, at 175 cm and `A TYPE`.  `FIGURE_ANGLES` is three halfwords,
(0, 128, 0): the figure turned 11.25 degrees about y.  `FIGURE_PLACE` is three
halfwords, (-480, 32, 1056).  Measured on 2026-09-18 by reading the code that
builds the camera (`CAMERA_BUILD`), which loads the three from these.
"""

CAMERA_BUILD = 0x80010E38
CAMERA_VIEW_BASE = "s7"
"""Where the camera is composed, and the register that holds the view.

The code before this instruction builds `RotMatrix(FIGURE_ANGLES)` and scales
its COLUMNS by `FIGURE_SCALE`, truncating toward zero; this `ctc2` loads the
VIEW matrix through `s7` -- a 32-byte struct in scratchpad, the same shape as
the pose's -- and the GTE then multiplies the two.  The product is the matrix
`POSE_MATRIX` hands the GTE at every piece, and it is why a taller player is
drawn taller: the scale is inside the camera, not in the pose (LOOKS-TASK-29).
"""

SCENERY_SWEEP = (0x80000000, 0x200000, 0x20000)
"""(first byte, how much, per read) of the RAM the screen's furniture is
looked for in: all of main memory, a chunk at a time.

It has to be all of it.  The figure's own display list is in the two bands of
`oracle.BUFFER_BANDS`, and the screen's title band, plate and text are not --
a sweep of those two comes back with the panel, the help box and the row
stripes and nothing else (measured 2026-09-20, LOOKS-TASK-31).
"""

GPU_LIST_SUBMIT = 0x8003ACB8
GPU_LIST_HEAD = "a0"
"""The instruction that hands the GPU its display list, and the register
holding the list's first node.

`sw a0, 0x0(v0)` with `v0` = the DMA channel 2 address register -- found on
2026-09-21 (LOOKS-TASK-31) by a write watchpoint on that register, which
stopped only here.  Per frame it stores the head of a one-node list and the
head of the ordering table, which alternates between two buffers 0x4000 apart.
Walking the table from here gives the frame's whole list in DRAWING order --
which the band sweep of `SCENERY_SWEEP` could not: it found packets but not
which ones this frame drew, and missed every semi-transparent one because the
screen shows their blend and not their colour.
"""

ADDRESS_OWNER = "layout.py"
"""The one module of tools/looks/ allowed to carry an address (plan 3.3, rule 1)."""

# What the sweep calls an address.  Anchored, because by the time they are
# applied the candidate is already a whole NUMBER token from tokenize -- there
# is nothing around it to search.
#
# They are module constants and not locals so there is ONE definition of each
# to edit.  The tokenize rewrite left an unanchored pair behind in
# sweep_addresses() under these same two names, dead but readable, and whoever
# went to loosen or tighten the rule would have found those first, edited them,
# changed nothing, and watched the gate stay green (CORR-LOOKS-011).
_HEX_LITERAL = re.compile(r"\A0[xX][0-9a-fA-F]+\Z")
_BIG_DECIMAL = re.compile(r"\A\d{4,}\Z")


def sweep_addresses(root: str | None = None,
                    stats: dict | None = None) -> list[tuple[str, int, str]]:
    """Find addresses written outside this file.  Returns the offending lines.

    *stats*, if given, is filled with how much was actually read -- "files" and
    "lines".  A sweep that opened nothing and a sweep that read everything and
    found nothing print the same sentence otherwise, and that sentence is the
    one a reader takes for "rule 1 is being kept".  Same failure superpack_count
    had, closed the same way (CORR-LOOKS-003, CORR-LOOKS-009).

    Rule 1 of the plan is what lets an offset move later without being hunted
    through the tree, and a rule nobody sweeps is a rule that decays one
    commit at a time.

    What counts as an address: a hexadecimal literal, or a decimal literal of
    four digits or more, **written as code**.  The escape is one line:

    * a line carrying `# not-an-address: <why>` is exempt.  The marker is
      spelled as the claim it makes -- an earlier spelling, `# address:`, read
      as the opposite of what the annotator meant, and a tripwire whose
      escape hatch reads backwards will be used wrongly.

    Strings and comments are not code, so a sha256 in a message and a date in
    a docstring are not addresses.  **That reading comes from `tokenize` and
    not from scanning for quote characters.** The hand-rolled stripper this
    replaced could not see triple quotes, so every prose paragraph in a module
    was swept as if it were code: `section.py` arrived with four dates in
    docstrings and the gate went red on 2026-09-14 over the word "2026".
    Annotating prose with `# not-an-address:` would have been the wrong repair
    -- it would train the exemption on text that was never a candidate, and
    the exemption is supposed to be rare enough to read.

    The walk uses os.walk and not os.listdir: `ui/` is a directory, and the
    .mcr cycle left one of those outside its own sweep exactly this way.
    """
    if root is None:
        root = os.path.dirname(os.path.abspath(__file__))

    findings = []
    files = 0
    lines = 0

    for parent, _dirs, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".py"):
                continue
            path = os.path.join(parent, name)
            # The owner is exempt by its PATH, not by its name: os.walk
            # descends, so a tools/looks/ui/layout.py would otherwise be
            # excused for free -- a whole directory outside the rule, which is
            # how the .mcr cycle lost one.
            if os.path.relpath(path, root) == ADDRESS_OWNER:
                continue
            files += 1
            with open(path, encoding="utf-8") as handle:
                source = handle.read()
            source_lines = source.splitlines()
            lines += len(source_lines)
            exempt = {
                number for number, line in enumerate(source_lines, 1)
                if "# not-an-address:" in line
            }
            for number in _address_lines(source, path):
                if number in exempt:
                    continue
                text = source_lines[number - 1] if number <= len(source_lines) else ""
                findings.append((os.path.relpath(path, root), number, text.rstrip()))
    if stats is not None:
        stats["files"] = files
        stats["lines"] = lines
    return findings


def _address_lines(source: str, path: str) -> set:
    """Line numbers of *source* holding a numeric literal that looks like an address.

    Uses `tokenize`, so a number is only a candidate when Python itself calls
    it a NUMBER token: text inside a string and text after a `#` are other
    token kinds and never reach the test.

    A file that will not tokenize -- a syntax error mid-edit -- is reported as
    one finding on line 1 rather than skipped.  Skipping would mean the sweep
    quietly stops covering a file at the exact moment somebody is changing it.
    """
    found = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for kind, text, (row, _col), _end, _line in tokens:
            if kind != tokenize.NUMBER:
                continue
            body = text.replace("_", "")
            if _HEX_LITERAL.match(body) or _BIG_DECIMAL.match(body):
                found.add(row)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        found.add(1)
    return found


def _sweep(root: str | None = None) -> int:
    stats: dict = {}
    findings = sweep_addresses(root, stats)
    swept = " (%d file(s), %d line(s) swept)" % (stats["files"], stats["lines"])
    if not findings:
        print("layout --sweep: no address outside %s%s"
              % (ADDRESS_OWNER, swept))
        return 0
    for path, number, line in findings:
        print("  %s:%d: %s" % (path, number, line.strip()))
    print("layout --sweep: %d line(s) carrying an address outside %s%s"
          % (len(findings), ADDRESS_OWNER, swept))
    return 1


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        self_check()
        return 0
    if len(argv) == 2 and argv[1] == "--sweep":
        return _sweep()
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
