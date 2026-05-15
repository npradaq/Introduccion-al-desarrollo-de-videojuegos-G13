import random as _random

_PERM: list[int] = []


def seed(s: int) -> None:
    global _PERM
    rng = _random.Random(s)
    p = list(range(256))
    rng.shuffle(p)
    _PERM = p + p


def _fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


def _grad1d(hash_val: int, x: float) -> float:
    return x if (hash_val & 1) == 0 else -x


def noise1d(x: float) -> float:
    xi = int(x) & 255
    xf = x - int(x)
    u = _fade(xf)
    a = _PERM[xi]
    b = _PERM[xi + 1]
    return _lerp(_grad1d(a, xf), _grad1d(b, xf - 1), u)


def octave_noise1d(x: float, octaves: int = 4, frequency: float = 1.0,
                   amplitude: float = 1.0, persistence: float = 0.5, lacunarity: float = 2.0,) -> float:

    value = 0.0
    freq = frequency
    amp = amplitude
    for _ in range(octaves):
        value += noise1d(x * freq) * amp
        freq *= lacunarity
        amp *= persistence
    return value
