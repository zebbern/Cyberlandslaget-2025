# Binary-Encodings1 CTF Solution

## Overview

In this challenge, we’re given 32 pairs of \((p_i, f_i)\) values. Each \(p_i\) is a prime number, and each \(f_i\) represents a remainder when a secret integer (derived from the flag) is divided by \(p_i\). Our goal is to use these pairs to reconstruct the original flag. 

## How It Works

1. **Binarify**  
   The challenge’s code defines a function `binarify(flag_bytes)` which:
   - Interprets `flag_bytes` as a big integer, calls it \(M\).
   - Converts \(M\) to a binary string of the form `"0b101010..."`.
   - Converts that binary string to bytes and then once again to a big integer \(x\).
   Essentially, \(x\) = integer representation of the string `"0b" + (binary form of M)`.

2. **Congruences**  
   We know \(x \bmod p_i = f_i\). With 32 distinct primes \(p_i\), we have 32 modular equations:
   \[
   \begin{aligned}
   x &\equiv f_0 \pmod{p_0},\\
   x &\equiv f_1 \pmod{p_1},\\
   &\quad\vdots\\
   x &\equiv f_{31} \pmod{p_{31}}.
   \end{aligned}
   \]
   By the **Chinese Remainder Theorem** (CRT), these equations have a unique solution for \(x\) modulo the product of all primes.

3. **Reconstructing**  
   Once we find \(x\) via the CRT, we:
   - Convert \(x\) back to bytes to get the ASCII string `"0b1010..."`.
   - Strip off the `"0b"`.
   - Parse the remaining `"1010..."` as a binary number.
   - Convert that binary number into 31 bytes (since the original flag is 31 bytes).

## Step-by-Step

1. **Read the pairs**: Copy all \(p_i\) (primes) and \(f_i\) (remainders) from `output.txt`.
2. **Apply CRT**: Use a standard CRT function or implement it yourself:
   - Multiply all primes to get a large product \(P\).
   - Iteratively solve for \(x\) so it satisfies each congruence.
3. **Decode**:
   - Turn \(x\) into a byte string.  
   - Read that byte string as ASCII (it should start with `"0b"`).  
   - Remove `"0b"`, convert the rest of the string from binary to an integer.  
   - Convert that integer to a 31-byte sequence to get the flag.

## Example Code

Below is a condensed Python script that performs these steps:

```python
p_list = [...]  # list of 32 primes (p_0 through p_31)
f_list = [...]  # list of 32 remainders (f_0 through f_31)

def solve_crt(primes, remainders):
    x = remainders[0]
    M = primes[0]
    for i in range(1, len(primes)):
        p_i = primes[i]
        r_i = remainders[i]
        dx = (r_i - x) % p_i
        inv_M = pow(M, p_i - 2, p_i)  # Fermat's Little Theorem since p_i is prime
        x = (x + dx * M * inv_M) % (M * p_i)
        M *= p_i
    return x

x = solve_crt(p_list, f_list)

# Convert x to the ASCII string "0b1010..."
x_bytes = x.to_bytes((x.bit_length() + 7) // 8, 'big')
bin_string = x_bytes.decode('ascii')  # Should start with "0b"

# Strip "0b", convert binary -> integer
flag_int = int(bin_string[2:], 2)

# Convert that integer to 31 bytes (the original flag)
flag_bytes = flag_int.to_bytes(31, 'big')
print("Recovered flag:", flag_bytes)
```

## Final Flag

When the above code is run with our `p_list` and `f_list`, it prints:

```
DDC{crt_to_the_m0100010110001n}
```

That is the final flag for the challenge!
