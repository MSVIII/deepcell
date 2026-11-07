"""Compose and render the game's music loops to app/src/main/res/raw/music_*.ogg.

Run from the project folder:
    python tools/audio/gen_music.py
Needs Python 3 with numpy and scipy, and ffmpeg (with libvorbis) on the PATH. Everything is
written here as notes and synthesised from oscillators and noise; no samples or recordings.

Three loops, each one seamless (the reverb and any note that runs past the end wrap around
to the start, so MediaPlayer can loop the file without a click):
    music_menu.ogg  "Down Below"      A minor, 70 BPM, slow pad, bell melody, wind
    music_game.ogg  "Hold the Hatch"  D minor, 112 BPM, bass, arpeggio, drums, lead
    music_boss.ogg  "Command Drone"   E minor, 140 BPM, driving bass, stabs, toms, siren lead

Notes are (beat, length in beats, MIDI number). Change them and re-run to rewrite a part.
"""
import os
import subprocess
import tempfile
import wave

import numpy as np
from scipy.signal import butter, lfilter

RATE = 32000
HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, "..", "..", "app", "src", "main", "res", "raw")
rng = np.random.default_rng(7)

# Music sits under the sound effects (gen_sfx.py normalises those to -13 dBFS RMS).
TARGET_DBFS = -15.0
# Phone speakers play almost nothing below ~150 Hz, so the mixes keep the melody, arpeggio and
# the upper harmonics of the bass up front, and the master cuts the sub-bass.
SUB_CUT_HZ = 70


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff, RATE * 0.45) / (RATE / 2), "low")
    return lfilter(b, a, x)


def hp(x, cutoff, order=2):
    b, a = butter(order, cutoff / (RATE / 2), "high")
    return lfilter(b, a, x)


def bp(x, lo, hi):
    b, a = butter(2, [lo / (RATE / 2), hi / (RATE / 2)], "band")
    return lfilter(b, a, x)


def env(n, a=0.005, d=0.1, s=0.7, r=0.1, gate=None):
    """ADSR over n samples; the release starts at gate (samples), default n - r."""
    t = np.arange(n) / RATE
    gate_t = (gate if gate is not None else max(n - int(r * RATE), 1)) / RATE
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4) * 3))
    rel = np.exp(-np.clip(t - gate_t, 0, None) / max(r, 1e-4) * 4)
    return e * np.where(t > gate_t, rel, 1.0)


def saw(f, n, phase=0.0):
    ph = (phase + np.cumsum(np.full(n, f) if np.isscalar(f) else f) / RATE) % 1.0
    return 2 * ph - 1


def square(f, n, duty=0.5):
    ph = (np.cumsum(np.full(n, f) if np.isscalar(f) else f) / RATE) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def sine(f, n):
    return np.sin(2 * np.pi * np.cumsum(np.full(n, f) if np.isscalar(f) else f) / RATE)


# ---------------- instruments ----------------

def pad(m, sec):
    n = int(sec * RATE) + int(1.5 * RATE)
    f = hz(m)
    x = sum(saw(f * d, n, rng.random()) for d in (0.996, 1.0, 1.004)) / 3
    x = lp(x, 1400) * env(n, a=0.9, d=1.0, s=0.85, r=1.4, gate=int(sec * RATE))
    return x


def bell(m, sec):
    n = int(sec * RATE) + int(2.0 * RATE)
    t = np.arange(n) / RATE
    f = hz(m)
    index = 2.2 * np.exp(-t * 3)
    x = np.sin(2 * np.pi * f * t + index * np.sin(2 * np.pi * f * 3.5 * t))
    x += 0.3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
    return x * np.exp(-t * 1.6) * np.clip(t / 0.004, 0, 1)


def pluck(m, sec, bright=2600):
    n = int(sec * RATE) + int(0.6 * RATE)
    t = np.arange(n) / RATE
    x = saw(hz(m), n) * 0.6 + square(hz(m), n, 0.3) * 0.4
    x = lp(x, bright) * np.exp(-t * 7) * np.clip(t / 0.003, 0, 1)
    return x


def bass(m, sec, cutoff=520, drive=1.0):
    n = int(sec * RATE) + int(0.08 * RATE)
    f = hz(m)
    x = saw(f, n) * 0.7 + sine(f / 2, n) * 0.5
    x = np.tanh(lp(x, cutoff) * (1.2 * drive)) * env(n, a=0.004, d=0.12, s=0.75, r=0.05,
                                                       gate=int(sec * RATE))
    return x


def lead(m, sec, bright=2800, detune=0.0):
    n = int(sec * RATE) + int(0.25 * RATE)
    t = np.arange(n) / RATE
    vib = 1 + 0.005 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) / 0.3, 0, 1)
    f = hz(m) * vib
    x = saw(f, n) * 0.55 + square(f * (1 + detune), n) * 0.45
    x = lp(x, bright) * env(n, a=0.012, d=0.25, s=0.7, r=0.18, gate=int(sec * RATE))
    return x


def kick(power=1.0):
    n = int(0.35 * RATE)
    t = np.arange(n) / RATE
    f = 45 + 95 * np.exp(-t * 28)
    x = sine(f, n) * np.exp(-t * 9) + 0.25 * np.exp(-t * 300) * rng.uniform(-1, 1, n)
    return np.tanh(x * 1.5 * power)


def snare():
    n = int(0.25 * RATE)
    t = np.arange(n) / RATE
    body = sine(185 * (1 + 0.3 * np.exp(-t * 40)), n) * np.exp(-t * 22)
    rattle = bp(rng.uniform(-1, 1, n), 1500, 7000) * np.exp(-t * 16)
    return 0.6 * body + 1.1 * rattle


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * RATE)
    t = np.arange(n) / RATE
    return hp(rng.uniform(-1, 1, n), 7000) * np.exp(-t * (14 if open_ else 70))


def tom(m):
    n = int(0.4 * RATE)
    t = np.arange(n) / RATE
    return sine(hz(m) * (1 + 0.5 * np.exp(-t * 25)), n) * np.exp(-t * 8)


def crash():
    n = int(1.8 * RATE)
    t = np.arange(n) / RATE
    return hp(rng.uniform(-1, 1, n), 4500) * np.exp(-t * 2.2)


# ---------------- arrangement helpers ----------------

class Track:
    """A loop of a fixed number of bars. Sounds past the end wrap round to the start."""

    def __init__(self, bpm, bars, beats_per_bar=4):
        self.spb = 60.0 / bpm
        self.length = int(round(bars * beats_per_bar * self.spb * RATE))
        self.dry = np.zeros((2, self.length))
        self.wet = np.zeros((2, self.length))

    def at(self, beat):
        return int(round(beat * self.spb * RATE))

    def add(self, beat, sig, gain=1.0, pan=0.0, send=0.0):
        start = self.at(beat) % self.length
        sig = np.asarray(sig) * gain
        left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        idx = (start + np.arange(len(sig))) % self.length
        for ch, g in ((0, left), (1, right)):
            np.add.at(self.dry[ch], idx, sig * g * 1.414)
            if send:
                np.add.at(self.wet[ch], idx, sig * g * 1.414 * send)

    def notes(self, part, voice, offset=0.0, gain=1.0, pan=0.0, send=0.0, transpose=0):
        for beat, length, m in part:
            self.add(offset + beat, voice(m + transpose, length * self.spb), gain, pan, send)

    def render(self, room=1.8):
        # Circular convolution: the reverb tail wraps to the start of the loop.
        n = self.length
        t = np.arange(int(room * RATE)) / RATE
        out = self.dry.copy()
        for ch in range(2):
            ir = rng.uniform(-1, 1, len(t)) * np.exp(-t * 6.9 / room)
            ir = lp(ir, 5000)
            ir[: int(0.012 * RATE)] *= np.linspace(0, 1, int(0.012 * RATE))
            ir /= np.sqrt(np.sum(ir ** 2))
            full = np.zeros(n)
            full[: min(len(ir), n)] = ir[:n]
            out[ch] += 0.5 * np.real(np.fft.ifft(np.fft.fft(self.wet[ch]) * np.fft.fft(full)))
        return out


def master(x):
    x = hp(x, SUB_CUT_HZ)
    rms = np.sqrt(np.mean(x ** 2))
    x = x * (10 ** (TARGET_DBFS / 20) / rms)
    return np.tanh(x * 1.1) / 1.1 * 0.95


def write_ogg(name, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).T.copy()
    tmp = os.path.join(tempfile.gettempdir(), name + ".wav")
    with wave.open(tmp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    out = os.path.join(DST, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis",
                    "-q:a", "3", out], check=True)
    os.remove(tmp)
    print(f"{name}: {x.shape[1] / RATE:.1f} s, {os.path.getsize(out) // 1024} KB")


def chord_part(chords, bar_beats=4, bars_each=1):
    """[(midis...)] -> sustained notes, one chord per bars_each bars."""
    part = []
    for i, ch in enumerate(chords):
        for m in ch:
            part.append((i * bars_each * bar_beats, bars_each * bar_beats, m))
    return part


# ---------------- Down Below (menu) ----------------

def menu():
    tr = Track(bpm=70, bars=16)
    am9, fmaj7, c_g, em7 = (57, 60, 64, 71), (53, 57, 60, 64), (55, 60, 64, 67), (52, 55, 59, 62)
    chords = [am9, fmaj7, c_g, em7] * 2
    tr.notes(chord_part(chords, bars_each=2), pad, gain=0.20, send=0.6)
    roots = [45, 41, 43, 40] * 2
    for i, r in enumerate(roots):          # low drone under each chord
        tr.add(i * 8, pad(r - 12, 8 * tr.spb), gain=0.22, send=0.2)
    phrase = [(0, 2, 76), (2, 1, 81), (3, 1, 79), (4, 4, 76),
              (8, 1, 72), (9, 1, 76), (10, 2, 77), (12, 4, 76),
              (16, 2, 79), (18, 1, 76), (19, 1, 72), (20, 4, 74),
              (24, 2, 71), (26, 2, 74), (28, 4, 71)]
    tr.notes(phrase, bell, gain=0.22, pan=0.25, send=0.8)
    answer = [(1, 1, 69), (2, 2, 72), (5, 3, 71),
              (9, 1, 65), (10, 2, 69), (13, 3, 67),
              (17, 1, 67), (18, 2, 72), (21, 3, 71),
              (25, 1, 64), (26, 2, 67), (29, 3, 66)]
    tr.notes(answer, bell, offset=32, gain=0.2, pan=-0.3, send=0.8)
    # Second half: a soft arpeggio walks through each chord.
    for i, ch in enumerate(chords[4:]):
        for k in range(8):
            m = ch[[0, 1, 2, 3, 2, 1, 2, 3][k]] + 12
            tr.add(32 + i * 8 + k, pluck(m, tr.spb, 1500), gain=0.07, pan=-0.4 + 0.1 * (k % 4), send=0.7)
    # Wind: slow-moving filtered noise.
    n = tr.length
    t = np.arange(n) / RATE
    wind = lp(rng.uniform(-1, 1, n), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * t / (n / RATE)))
    tr.add(0, wind, gain=0.05, pan=0.0, send=0.3)
    return tr.render(room=3.0)


# ---------------- Hold the Hatch (gameplay) ----------------

def game():
    tr = Track(bpm=112, bars=32)
    dm, bb, f, c = (62, 65, 69), (58, 62, 65), (60, 65, 69), (60, 64, 67)
    gm, a = (55, 58, 62), (57, 61, 64)
    a_prog = [dm, bb, f, c]
    b_prog = [gm, bb, dm, a]
    bass_root = {dm: 38, bb: 34, f: 41, c: 36, gm: 43, a: 45}
    # Sections: intro 4 | A 8 | B 8 | A' 8 | break 4
    bars = a_prog + a_prog * 2 + b_prog * 2 + a_prog * 2 + [dm, bb, c, a]
    for i, ch in enumerate(bars):
        bar = i * 4
        intro, brk = i < 4, i >= 28
        r = bass_root[ch]
        pattern = [r, r, r + 12, r, r, r + 7, r + 12, r + 7]
        if not brk:
            for k, m in enumerate(pattern):
                tr.add(bar + k * 0.5, bass(m, 0.45 * tr.spb, cutoff=1100, drive=1.6),
                       gain=0.34 if k % 2 == 0 else 0.26)
        else:
            tr.add(bar, bass(r, 3.8 * tr.spb, cutoff=380), gain=0.4)
        tr.add(bar, pad(ch[0], 4 * tr.spb), gain=0.07, pan=-0.3, send=0.5)
        tr.add(bar, pad(ch[2], 4 * tr.spb), gain=0.07, pan=0.3, send=0.5)
        if not intro and not brk:          # sixteenth arpeggio
            seq = [0, 1, 2, 1] * 4
            for k in range(16):
                m = ch[seq[k]] + (12 if k % 8 >= 4 else 0)
                tr.add(bar + k * 0.25, pluck(m, 0.22 * tr.spb, 2600), gain=0.15,
                       pan=0.35 if k % 2 else -0.35, send=0.3)
        # Drums
        for beat in range(4):
            if not brk or beat == 0:
                tr.add(bar + beat, kick(), gain=0.4 if beat in (0, 2) else 0.0)
            if not intro and not brk and beat in (1, 3):
                tr.add(bar + beat, snare(), gain=0.32, send=0.15)
            if intro and beat == 3:
                tr.add(bar + beat, snare(), gain=0.12, send=0.2)
            if not brk:
                tr.add(bar + beat, hat(), gain=0.10, pan=0.4)
                tr.add(bar + beat + 0.5, hat(beat == 3), gain=0.13, pan=0.4)
        if i in (4, 12, 20):
            tr.add(bar, crash(), gain=0.16, pan=-0.3, send=0.3)
        if i in (11, 19, 27):            # tom fill into the next section
            for k, m in enumerate((50, 47, 45, 43)):
                tr.add(bar + 3 + k * 0.25, tom(m), gain=0.3)
    melody_b = [(0, 1, 69), (1, 1, 74), (2, 1.5, 77), (3.5, 0.5, 76),
                (4, 3, 74), (7, 0.5, 72), (7.5, 0.5, 70),
                (8, 1, 69), (9, 1, 72), (10, 1, 77), (11, 1, 81),
                (12, 2, 79), (14, 1, 76), (15, 1, 72),
                (16, 1.5, 74), (17.5, 0.5, 70), (18, 1, 67), (19, 1, 70),
                (20, 1, 74), (21, 1, 77), (22, 2, 82),
                (24, 1.5, 81), (25.5, 0.5, 79), (26, 1, 77), (27, 1, 76),
                (28, 2, 76), (30, 1, 73), (31, 1, 69)]
    # The B melody fits Gm Bb Dm A; start it on bar 12, repeat it an octave down on bar 16.
    shifted = [(b, l, m) for b, l, m in melody_b]
    tr.notes(shifted, lead, offset=12 * 4, gain=0.25, send=0.35)
    tr.notes(shifted, lead, offset=16 * 4, gain=0.18, transpose=-12, send=0.35, pan=-0.2)
    melody_a = [(0, 1, 69), (1, 1, 74), (2, 1.5, 77), (3.5, 0.5, 76),
                (4, 3, 74), (7, 0.5, 72), (7.5, 0.5, 70),
                (8, 1, 69), (9, 1, 72), (10, 1, 77), (11, 1, 81),
                (12, 2, 79), (14, 1, 76), (15, 1, 72),
                (16, 1, 77), (17, 1, 76), (18, 1, 74), (19, 1, 69),
                (20, 2, 70), (22, 2, 74),
                (24, 1, 72), (25, 1, 77), (26, 1, 81), (27, 1, 79),
                (28, 3, 76), (31, 1, 72)]
    # The A melody also plays in the first section, so the tune starts after the 4-bar intro.
    tr.notes(melody_a, lead, offset=4 * 4, gain=0.2, send=0.35, pan=-0.1, transpose=-12)
    tr.notes(melody_a, lead, offset=20 * 4, gain=0.25, send=0.35, pan=0.15)
    return tr.render(room=1.6)


# ---------------- Command Drone (boss) ----------------

def boss():
    tr = Track(bpm=140, bars=32)
    em, fm, d, cm = (64, 67, 71), (65, 69, 72), (62, 66, 69), (60, 64, 67)
    prog_a = [em, fm, em, d]
    prog_b = [cm, d, em, fm]
    root = {em: 40, fm: 41, d: 38, cm: 36}
    bars = prog_a * 2 + prog_a * 2 + prog_b * 2 + prog_a + prog_b
    for i, ch in enumerate(bars):
        bar = i * 4
        intro = i < 4
        r = root[ch]
        # Sixteenth bass with octave jumps, driven hard.
        for k in range(16):
            m = r + (12 if k in (3, 6, 11, 14) else 0)
            tr.add(bar + k * 0.25, bass(m, 0.22 * tr.spb, cutoff=1500, drive=2.2),
                   gain=0.34 if k % 4 == 0 else 0.25)
        if not intro:                     # power-chord stabs on the off-beats
            for beat in (0.5, 1.5, 2.75, 3.5):
                for m in (ch[0] - 12, ch[0] - 5):
                    tr.add(bar + beat, lead(m, 0.2 * tr.spb, bright=3200, detune=0.006),
                           gain=0.13, pan=-0.3 if m == ch[0] - 12 else 0.3, send=0.2)
        tr.add(bar, pad(ch[1] - 12, 4 * tr.spb), gain=0.07, send=0.5)
        for beat in range(4):
            tr.add(bar + beat, kick(1.2), gain=0.45)
            if not intro and beat in (1, 3):
                tr.add(bar + beat, snare(), gain=0.36, send=0.15)
            for s in range(4 if not intro else 2):
                tr.add(bar + beat + s * (0.25 if not intro else 0.5), hat(s == 2 and beat == 3),
                       gain=0.09 if s % 2 else 0.12, pan=0.45)
        if i % 8 == 7:                    # tom roll at the end of each 8 bars
            for k, m in enumerate((52, 52, 49, 49, 47, 47, 43, 43)):
                tr.add(bar + 2 + k * 0.25, tom(m), gain=0.32)
        if i % 8 == 0:
            tr.add(bar, crash(), gain=0.2, pan=0.3, send=0.3)
    siren = [(0, 1, 76), (1, 1, 79), (2, 1, 83), (3, 0.5, 81), (3.5, 0.5, 79),
             (4, 2, 81), (6, 1, 79), (7, 1, 77),
             (8, 1, 76), (9, 0.5, 71), (9.5, 1, 76), (10.5, 1.5, 79),
             (12, 2, 78), (14, 2, 74),
             (16, 1, 76), (17, 1, 79), (18, 2, 84),
             (20, 1, 86), (21, 1, 84), (22, 2, 81),
             (24, 2, 83), (26, 1, 79), (27, 1, 76),
             (28, 4, 77)]
    tr.notes(siren, lead, offset=8 * 4, gain=0.23, send=0.3)
    tr.notes(siren, lead, offset=8 * 4, gain=0.1, transpose=-12, send=0.3, pan=-0.3)
    tr.notes(siren, lead, offset=24 * 4, gain=0.23, send=0.3, pan=0.15)
    return tr.render(room=1.3)


if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    for name, fn in (("music_menu", menu), ("music_game", game), ("music_boss", boss)):
        write_ogg(name, master(fn()))
