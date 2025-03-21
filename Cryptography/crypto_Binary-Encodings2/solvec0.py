from sage.all import crt, matrix, ZZ
from sage.numerical.knapsack import knapsack
from tqdm import tqdm
from itertools import product
from multiprocessing import Pool

ps = []
qs = []
n = 1
with open("output.txt") as f:
    while True:
        l = f.readline().strip()
        if l == "":
            break
        ps.append(int(l.split()[-1]))
        l = f.readline().strip()
        qs.append(int(l.split()[-1]))
        n *= ps[-1]

base: int = crt(qs, ps)

def binarify(m):
    return int.from_bytes(bin(int.from_bytes(m, "big")).encode(), "big")

def binarify_b(m):
    return bin(int.from_bytes(m, "big")).encode()

def single_binary(c):
    return bin(c)[2:].rjust(8, "0").encode()

template = b"DDC{" + b"\0" * 13 + b"}"
assert len(template) == 18

bin_base = binarify(template) % n

possible_idxs = []
for i, c in enumerate(template[::-1]):
    if c != 0:
        continue
    for j in range(7):
        possible_idxs.append(i * 8 + j)
muls = [((ord('1') - ord('0')) << (i * 8)) % n for i in possible_idxs]

target = base - bin_base
#assert target + qk * n == r - bin_base

# These go in solvec_params.py
print(f"{n = }")
print(f"{target = }")
print(f"{muls = }")
print(f"{possible_idxs = }")
print(f"{bin_base = }")
print(f"{base = }")
