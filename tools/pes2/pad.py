#!/usr/bin/env python3
"""Send one pad action to an already-running DuckStation, and look at it.

`mcp_drive.py` runs a whole route and shuts the emulator down after it. This
is for the other way of working: the emulator stays up -- on the user's own
display, where they can see it -- and one action is sent at a time, with a
person deciding the next one. It is what the routes get written *from*.

    tools/pes2/fork.py launch <copy.cue>     # or start it by hand
    python3 tools/pes2/pad.py press cross
    python3 tools/pes2/pad.py press down down cross
    python3 tools/pes2/pad.py shot /tmp/a.png
    python3 tools/pes2/pad.py stats            # mean/sd, and the top band
    python3 tools/pes2/pad.py watch 20         # is anything moving?
    python3 tools/pes2/pad.py run 600          # fast forward, and
                                               # give every kickoff

Buttons are pad names -- cross, circle, square, triangle, start, select,
up, down, left, right, l1, l2, r1, r2, l3, r3.

**Ported from `xdotool` to MCP on 2026-09-03**, and three things went away
with it rather than being reimplemented:

* **The display stopped mattering.** This used to find the game window,
  then find the *client* inside it, because on a display with a window
  manager the search returns the frame and capturing that gives 894x785
  instead of 800x655 -- which silently invalidated every crop measured on
  the headless display. The emulator hands over its own frame buffer now,
  so there is no window to find and no frame to mistake for it. `:1` and
  `:98` are the same code path.
* **The key bindings stopped mattering.** They were read out of the user's
  `settings.ini` and translated from DuckStation's names to X keysyms,
  because declaring them had already failed once. `press_button` takes the
  pad button by name.
* **The press duration stopped being a guess.** A face button was held 1.0 s
  and a direction 0.15 s, both calibrated by trial against the game's own
  auto-repeat. `duration_frames` is counted by the emulator.

    PES2_MCP_PORT   the server's port, default 2346
"""

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import drive                                                  # noqa: E402
from mcp import Client, NotRunning                            # noqa: E402

BUTTONS = ("cross", "circle", "square", "triangle", "up", "down", "left",
           "right", "l1", "l2", "r1", "r2", "start", "select", "l3", "r3")

BAND = (0, 60, 800, 200)          # the strip that tells kickoff apart
CLOCK = (560, 90, 760, 130)       # the match clock

# Same numbers as the routes: three frames down, seventeen to act on it.
PRESS_FRAMES = 3
AFTER_FRAMES = 17


class Live:
    """An emulator someone else started, left running between commands."""

    def __init__(self, client):
        self.client = client

    def press(self, button, frames=PRESS_FRAMES, after=AFTER_FRAMES):
        """One button, held for an exact number of the game's own frames.

        Paused around the press so that the count means something; the
        caller resumes if it wants the game to carry on.
        """
        self.client.call("pause")
        self.client.call("press_button", button=button.capitalize(),
                         duration_frames=frames)
        for _ in range(frames + after):
            self.client.call("frame_step")

    def resume(self):
        self.client.call("continue")

    def capture(self, path=None):
        path = path or f"/tmp/pes2-live-{time.time():.3f}.png"
        self.client.call("take_screenshot", path=path)
        if not os.path.exists(path):
            raise SystemExit(f"the emulator reported a screenshot at {path} "
                             f"and there is no file there")
        return drive.Frame(path)

    def fast_forward(self, on):
        self.client.call("set_speed", fast_forward=bool(on))


def describe(frame):
    if frame.size != (800, 655):
        print(f"  aviso: quadro {frame.size[0]}x{frame.size[1]}, nao 800x655"
              f" -- os recortes do relogio e da faixa nao valem",
              file=sys.stderr)
    m, sd = frame.stats()
    bm, bsd = frame.stats(BAND)
    return (f"mean={m:.4f} sd={sd:.4f}   band mean={bm:.4f} sd={bsd:.4f}"
            f"   {'preto' if frame.is_black() else ''}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    try:
        client = Client()
        client.initialize()
    except NotRunning as e:
        print(f"{e}", file=sys.stderr)
        return 77

    live = Live(client)
    cmd, rest = argv[0], argv[1:]

    if cmd == "press":
        if not rest:
            raise SystemExit("press what? see --help for the button names")
        for button in rest:
            if button.lower() not in BUTTONS:
                raise SystemExit(f"unknown button {button!r}")
        for button in rest:
            live.press(button.lower())
        live.resume()
        time.sleep(0.5)
        print(describe(live.capture()))

    elif cmd == "shot":
        path = rest[0] if rest else "/tmp/pes2.png"
        frame = live.capture(os.path.abspath(path))
        print(f"{path}\n{describe(frame)}")

    elif cmd == "stats":
        print(describe(live.capture()))

    elif cmd == "watch":
        seconds = float(rest[0]) if rest else 10
        a = live.capture()
        time.sleep(seconds)
        b = live.capture()
        print(f"em {seconds:g}s:  tela {b.difference(a):.5f}   "
              f"relogio {b.difference(a, CLOCK):.5f}   "
              f"(relogio 0 = partida parada)")
        print(describe(b))

    elif cmd == "run":
        # Acelerar e esperar nao termina uma partida: **todo gol devolve um
        # saque que espera Cross**, e uma corrida que so segura o
        # fast-forward para no primeiro gol parecendo que a partida nao
        # acaba -- foi assim que um "onze minutos de fast-forward nao
        # terminaram a partida" entrou num documento. Medido em 2026-09-02
        # com o usuario olhando a tela, e o caso continua existindo aqui:
        # o que mudou e que o fast-forward agora e uma chamada e nao um
        # `keydown` que precisa de um `keyup` num `finally`.
        budget = float(rest[0]) if rest else 600
        t0 = time.time()
        passes = 0
        try:
            live.fast_forward(True)
            live.resume()
            previous = live.capture()
            while time.time() - t0 < budget:
                time.sleep(6)
                current = live.capture()
                m, sd = current.stats()
                elapsed = int(time.time() - t0)
                if not (0.20 < m < 0.36):
                    print(f"  {elapsed}s: saiu do gramado  mean={m:.4f} "
                          f"sd={sd:.4f}", flush=True)
                    break
                if current.difference(previous, CLOCK) < 0.001:
                    live.press("cross")
                    passes += 1
                    print(f"  {elapsed}s: congelado -> Cross ({passes})",
                          flush=True)
                    live.resume()
                    time.sleep(2)
                    current = live.capture()
                previous = current
            else:
                print(f"  ainda no gramado apos {int(budget)}s", flush=True)
        finally:
            live.fast_forward(False)
            live.resume()
        print(f"  {passes} saque(s) dado(s)")
        print(describe(live.capture()))

    else:
        raise SystemExit(f"unknown command {cmd!r}; see --help")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
