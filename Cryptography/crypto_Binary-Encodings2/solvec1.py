from tqdm import tqdm
from itertools import product
from multiprocessing import Pool

# https://github.com/Se-P3t/lattice_study/blob/master/pylattice/attacks/subset_sum.py
from pylattice.attacks.subset_sum import SSP
from solvec_params import *
import random


def solve_subset(vals, t):
    ssp = SSP(vals, t)
    ssp.construct_matrix()
    ssp.LLL()
    ssp.BKZ(block_size=20)
    res = ssp.extract_solution()
    if res is not None:
        return list(res)

def try_solve_mod(target, vals, n):
    sv = sum(vals)
    for k in range(15, len(vals) + 1):
        #k = qk
        t = target + n * k
        if t < 0:
            continue
        if sv < t:
            return None
        
        res = solve_subset(vals, t)
        if res is not None:
            return res

    return None
# base + k * n = bin_base + [differences]
# every added difference adds < n to the total -> k is bounded
c = len(muls)
from math import log

print(f"{c = }")
print("d:", c / log(max(muls), 2))

BRUTE_C = 17
print("d1:", (c - BRUTE_C) / log(max(muls), 2))

def binarify(m):
    return int.from_bytes(bin(int.from_bytes(m, "big")).encode(), "big")

def binarify_b(m):
    return bin(int.from_bytes(m, "big")).encode()

def single_binary(c):
    return bin(c)[2:].rjust(8, "0").encode()

'''
"""
Check (debug flag)
"""
know = b"DDC{fakeFaKE1031-}"
k_bits = binarify_b(know)[2:][::-1]
r = bin_base
for i, m in zip(possible_idxs, muls):
    if k_bits[i] == ord("1"):
        r += m
r2 = r - base
qk = r2 // n
assert r2 - qk * n == 0

print(f"{qk = }")
#'''

#check_bits = [1 if k_bits[x] == ord("1") else 0 for x in possible_idxs[:BRUTE_C]]
def solve_guess(g):
    sg = sum(x * m for x, m in zip(g, muls))
    res = try_solve_mod(target - sg, muls[BRUTE_C:], n)
    if res is not None:
        return list(g) + list(res)
    return None

#print(solve_guess(check_bits))

guesses = list(product([0, 1], repeat=BRUTE_C))
random.shuffle(guesses)

ok = None
with Pool(11) as p:
    for res in tqdm(p.imap_unordered(solve_guess, guesses), total=2**BRUTE_C):
        if res is not None:
            ok = res
            break

print(ok)
