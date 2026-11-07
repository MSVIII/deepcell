"""Synthesise the game's sound effects and write them to app/src/main/res/raw/*.ogg.

Run from the project folder:
    python tools/audio/gen_sfx.py
Needs Python 3 with numpy, and ffmpeg (with libvorbis) on the PATH. Every sound is made
here from noise and oscillators; no recordings or sample packs. Change a function and
re-run to retune a sound.
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

RATE = 22050
HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, "..", "..", "app", "src", "main", "res", "raw")
rng = np.random.default_rng(11)


def t(sec):
    return np.arange(int(RATE * sec)) / RATE


def env(n, attack=0.002, decay=0.2, curve=4.0):
    """Fast attack, exponential decay. Lengths in seconds."""
    x = np.arange(n) / RATE
    a = np.clip(x / max(attack, 1e-4), 0, 1)
    return a * np.exp(-curve * x / decay)


def noise(sec):
    return rng.uniform(-1, 1, int(RATE * sec))


def lowpass(x, cutoff):
    """One-pole low-pass. cutoff in Hz (scalar or array)."""
    a = np.exp(-2 * np.pi * np.asarray(cutoff, dtype=float) / RATE) * np.ones(len(x))
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def tone(freq, sec, shape="sine"):
    f = np.asarray(freq, dtype=float) * np.ones(int(RATE * sec))
    ph = 2 * np.pi * np.cumsum(f) / RATE
    if shape == "square":
        return np.sign(np.sin(ph))
    if shape == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    return np.sin(ph)


def pad(x, sec):
    return np.concatenate([x, np.zeros(int(RATE * sec))])


def mixdown(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def at(x, sec, total):
    out = np.zeros(int(RATE * total))
    s = int(RATE * sec)
    out[s:s + len(x)] += x[:len(out) - s]
    return out


# ---------------------------------------------------------------- sounds

def dig():
    """Pickaxe on scrap metal: a metallic clank plus a crunch of grit."""
    n = int(RATE * 0.35)
    ring = sum(np.sin(2 * np.pi * f * t(0.35)) * g for f, g in ((620, 1.0), (1480, 0.6), (2310, 0.35)))
    clank = ring * env(n, 0.001, 0.12, 5)
    grit = highpass(noise(0.35), 1500) * env(n, 0.001, 0.08, 5)
    thud = lowpass(noise(0.35), 300) * env(n, 0.001, 0.1, 5) * 2.5
    return 0.5 * clank + 0.35 * grit + 0.5 * thud


def harvest():
    """Mushroom pulled out: soft squelch, then a pop."""
    n = int(RATE * 0.3)
    squelch = lowpass(noise(0.3), np.linspace(400, 1800, n)) * env(n, 0.03, 0.12, 4) * 2.0
    pop = tone(np.linspace(520, 260, int(RATE * 0.08)), 0.08) * env(int(RATE * 0.08), 0.001, 0.05, 5)
    return 0.6 * squelch + 0.6 * at(pop, 0.12, 0.3)


def shot():
    """Rifle: noise crack with a low boom."""
    n = int(RATE * 0.4)
    crack = highpass(noise(0.4), 900) * env(n, 0.0005, 0.05, 6)
    boom = lowpass(noise(0.4), 220) * env(n, 0.001, 0.25, 5) * 4
    body = tone(np.linspace(160, 60, n), 0.4) * env(n, 0.001, 0.1, 5)
    return 0.6 * crack + 0.6 * boom + 0.4 * body


def turret():
    """Auto-Turret: shorter, higher, more mechanical burst of two shots."""
    one = highpass(noise(0.12), 1500) * env(int(RATE * 0.12), 0.0005, 0.03, 6)
    one += 0.4 * tone(np.linspace(900, 400, int(RATE * 0.12)), 0.12, "square") * env(int(RATE * 0.12), 0.0005, 0.02, 6)
    return 0.45 * mixdown(at(one, 0, 0.25), at(one * 0.8, 0.08, 0.25))


def hit():
    """Bullet on metal: short ping."""
    n = int(RATE * 0.18)
    ping = tone(2600, 0.18) * env(n, 0.0005, 0.06, 5) + 0.5 * tone(3900, 0.18) * env(n, 0.0005, 0.04, 5)
    tick = highpass(noise(0.18), 3000) * env(n, 0.0005, 0.01, 6)
    return 0.3 * ping + 0.4 * tick


def explode():
    """Enemy destroyed: noise burst through a falling low-pass, long rumble."""
    n = int(RATE * 1.1)
    burst = lowpass(noise(1.1), np.geomspace(5000, 150, n)) * env(n, 0.002, 0.5, 4) * 2.2
    rumble = lowpass(noise(1.1), 90) * env(n, 0.01, 0.8, 4) * 7
    crackle = highpass(noise(1.1), 2500) * (rng.uniform(0, 1, n) > 0.985) * env(n, 0.01, 0.4, 3) * 3
    return 0.55 * burst + 0.5 * rumble + 0.25 * crackle


def impact():
    """Something hits the hatch: heavy metal thump with a dull ring."""
    n = int(RATE * 0.7)
    thump = lowpass(noise(0.7), 180) * env(n, 0.001, 0.25, 5) * 6
    ring = (np.sin(2 * np.pi * 140 * t(0.7)) + 0.5 * np.sin(2 * np.pi * 377 * t(0.7))) * env(n, 0.001, 0.5, 5)
    rattle = highpass(noise(0.7), 1200) * env(n, 0.001, 0.08, 5)
    return 0.6 * thump + 0.35 * ring + 0.3 * rattle


def repair():
    """Wrench on the hatch: two ratchet clicks and a clank."""
    click = highpass(noise(0.04), 2000) * env(int(RATE * 0.04), 0.0005, 0.01, 6)
    clank = sum(np.sin(2 * np.pi * f * t(0.25)) * g for f, g in ((900, 1.0), (2100, 0.5))) * env(int(RATE * 0.25), 0.001, 0.08, 5)
    out = np.zeros(int(RATE * 0.4))
    for s in (0.0, 0.05, 0.1):
        out += at(click * 0.6, s, 0.4)
    return out + 0.35 * at(clank, 0.16, 0.4)


def buy():
    """Upgrade bought: coins of scrap and a rising two-note chime."""
    a = tone(660, 0.15, "square") * env(int(RATE * 0.15), 0.002, 0.08, 4)
    b = tone(990, 0.3, "square") * env(int(RATE * 0.3), 0.002, 0.15, 4)
    jingle = highpass(noise(0.2), 4000) * env(int(RATE * 0.2), 0.001, 0.05, 5)
    return 0.12 * mixdown(at(a, 0, 0.45), at(b, 0.09, 0.45)) + 0.2 * at(jingle, 0, 0.45)


def wave_clear():
    """Wave cleared: three rising notes."""
    out = np.zeros(int(RATE * 0.8))
    for k, f in enumerate((523, 659, 784)):
        n = tone(f, 0.4, "square") * env(int(RATE * 0.4), 0.003, 0.25, 4)
        n = lowpass(n, 3000)
        out += at(n, k * 0.11, 0.8)
    return 0.22 * out


def alarm():
    """Hatch breached: two-tone siren, twice."""
    sec = 1.2
    f = np.where((t(sec) * 4).astype(int) % 2 == 0, 620, 470)
    s = lowpass(tone(f, sec, "saw"), 2500)
    e = np.minimum(1, t(sec) / 0.02) * np.minimum(1, (sec - t(sec)) / 0.15)
    return 0.3 * s * e


def collect():
    """Collector picks up the pile: sack rustle and two coin-like clinks."""
    rustle = lowpass(noise(0.3), 2500) * env(int(RATE * 0.3), 0.02, 0.15, 4)
    clink = sum(np.sin(2 * np.pi * f * t(0.2)) * g for f, g in ((1800, 1.0), (2700, 0.5))) * env(int(RATE * 0.2), 0.001, 0.06, 5)
    return mixdown(0.5 * rustle, 0.4 * at(clink, 0.08, 0.35), 0.3 * at(clink * 0.8, 0.16, 0.35))


def tap():
    """UI button: short soft click."""
    n = int(RATE * 0.06)
    return 0.35 * tone(1200, 0.06) * env(n, 0.0005, 0.02, 6) + 0.2 * highpass(noise(0.06), 3000) * env(n, 0.0005, 0.008, 6)


SOUNDS = {
    "sfx_dig": dig, "sfx_harvest": harvest, "sfx_shot": shot, "sfx_turret": turret, "sfx_hit": hit,
    "sfx_explode": explode, "sfx_impact": impact, "sfx_repair": repair, "sfx_buy": buy,
    "sfx_wave": wave_clear, "sfx_alarm": alarm, "sfx_tap": tap, "sfx_collect": collect,
}


# Loudness: every sound is brought to the same RMS level, then a soft limiter (tanh) keeps
# the peaks under full scale. Without this the quiet ones (clicks, chimes) were 30 dB down
# and could not be heard on a phone speaker. Per-sound offsets in dB keep a sensible mix.
TARGET_DBFS = -13.0
MIX_DB = {"sfx_tap": -4, "sfx_hit": -3, "sfx_turret": -2, "sfx_buy": -1, "sfx_alarm": -2,
          "sfx_explode": 1, "sfx_impact": 1, "sfx_collect": -1}


def loud(x, name):
    x = np.asarray(x, dtype=float)
    rms = np.sqrt(np.mean(x ** 2)) or 1e-6
    gain = 10 ** ((TARGET_DBFS + MIX_DB.get(name, 0)) / 20) / rms
    return np.tanh(x * gain * 1.2) / np.tanh(1.2) * 0.9


def write_ogg(name, x):
    x = pad(loud(x, name), 0.02)
    pcm = (x * 32767).astype(np.int16)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, name + ".wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        out = os.path.join(DST, name + ".ogg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "4", out],
                       check=True)
    print(f"{name}.ogg {len(x) / RATE:.2f}s {os.path.getsize(out) // 1024} KB")


os.makedirs(DST, exist_ok=True)
for name, fn in SOUNDS.items():
    write_ogg(name, fn())
