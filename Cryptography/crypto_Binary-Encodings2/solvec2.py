solution = [1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1]

from solvec_params import *

def binarify(m):
    return int.from_bytes(bin(int.from_bytes(m, "big")).encode(), "big")

def binarify_b(m):
    return bin(int.from_bytes(m, "big")).encode()

def single_binary(c):
    return bin(c)[2:].rjust(8, "0").encode()

template = b"DDC{" + b"\0" * 13 + b"}"
res = binarify(template)
for m, i, b in zip(muls, possible_idxs, solution):
    if b:
        res |= 1 << (8 * i)
print(res)
b0 = res.to_bytes(len(binarify_b(template)), "big")
print(b0)
b1 = int(b0.decode()[2:], 2)
print(b1)
b2 = b1.to_bytes(18, "big")
print(b2)
