
import base64 as b64
from collections.abc import Mapping


def _atbash() -> Mapping[str, str]:
    _d = {}
    for (_start, _stop) in [("a", "z"), ("A", "Z")]:
        _d.update({chr(o): chr(ord(_start) + ord(_stop) - o) for o in range(ord(_start), ord(_stop))})
    return _d

def _caesar(shift=3) -> Mapping[str, str]:
    _d = {}
    for (_start, _stop) in [("a", "z"), ("A", "Z")]:
        _d.update({chr(o): chr(o + ord(_stop) - ord(_start) + 1 - shift) for o in range(ord(_start), ord(_start) + shift)})
        _d.update({chr(o): chr(o - shift) for o in range(ord(_start) + shift, ord(_stop) + 1)})
    return _d

_rev = lambda _d: {_v: _k for _k, _v in _d.items()}


def cipher(s: str, _d: Mapping[str, str]) -> str:
    return "".join([_d[char] if char in _d else char for char in s])

def atbash(s: str) -> str:
    return cipher(s, _d=_atbash())

def caesar(s: str, shift=3) -> str:
    return cipher(s, _d=_caesar(shift=shift))

def caesar_rev(s: str, shift=3) -> str:
    return cipher(s, _d=_rev(_caesar(shift=shift)))

# should span multiple lines for readability i.e. avoid list comprehension
def a1z26(s: str, char_sep="-", word_sep=" ") -> str:
    # sub-optimal iterating algorithm - could be further optimized
    chr_seq = [[str(ord(_chr) - 96) if _chr.isalpha() else _chr for _chr in word] for word in s.lower().split(word_sep)]
    enc_s = word_sep.join([char_sep.join(word) for word in chr_seq])   # assemble
    return enc_s.strip()

def a1z26_rev(s: str, char_sep="-", word_sep=" ") -> str:
    ord_seq = [i.split(char_sep) for i in s.split(word_sep)]
    dec_s = " ".join(["".join([chr(int(_ord) + 96) if _ord.isnumeric() else _ord for _ord in word]) for word in ord_seq])   # default to lowercase
    return dec_s.strip()

def base64(s: str) -> str:
    str_bytes = s.encode("ascii")
    b64_bytes = b64.b64encode(str_bytes)
    return b64_bytes.decode("ascii")

def base64_rev(s: str) -> str:
    b64_bytes = s.encode("ascii")
    str_bytes = b64.b64decode(b64_bytes)
    return str_bytes.decode("ascii")