
# fde-bootloader

**Challenge Prompt:**

> I’ve found this ancient disk in a computer during a recent search, but I haven’t found the password yet…  
> Did they even have full disk encryption back then?

**Files provided:**  
- `hda.img`  
- `mem.dump`  
- `run-qemu.sh`  

If you would like to just read the steps to get the flag, then scroll to the bottom of the page to the **“TLDR”** section.

---

## 🧐 First look — Gather Information

Started by running common forensics commands:

```bash
strings file.ext > file.ext.txt
binwalk -e file.ext
```

Found that `mem.dump` is a QEMU memory dump with a FreeDOS kernel (MS-DOS based):

```
FreeDOS kernel (build 1933 or prior)
FreeDOS kernel version %d.%d.%d
```

`strings` on `hda.img` only revealed `error!` and some junk.

---

## 🖥️ Running the Emulator

Executed the QEMU script:

```bash
./run-qemu.sh
```

Output:

```
SeaBIOS (version .)
IPXE (http://ipxe.org) .
Booting from Hard Disk...
Enter decryption key: _
```

So it’s a bootloader that decrypts the disk.

---

## 🕳️ Rabbit Holes — Reverse Engineering the Bootloader

Tried reverse engineering the bootloader, but it’s 16-bit. Tools like IDA don’t decompile 16-bit code well.

Tried dynamic analysis using `ltrace`, `strace`, and QEMU memory dumps. Found an easter egg:

```
Copyright (C) 2024 Segphault Heavy Industries...
```

Looked into Segphault — related to Danish CTFs like NC3, but nothing helpful found.

---

## 📚 Research & Key Discovery

Discovered the tool `AESKeyFind` through this writeup:  
https://g0blin.co.uk/hack-lu-ctf-2015-dr-bob-writeup/

Ran it on the memory dump and got two AES keys:

```
30e7ce9231c822e37065aa3044c0793d
c6dea73a7b053b85e1782aa720ae61dd
```

Tried using them in CyberChef — saw entropy drop from 7.9 to 5.5 → indicates successful partial decryption.

Suspected ESSIV (Encrypted Salt-Sector Initialization Vector) encryption.

---

## 🧪 Decryption using ESSIV

Found this repo implementing `aes-cbc-essiv`:  
https://github.com/trounce1/Android-AES/blob/master/android_aes.py

Used the two keys:

- Encryption key: `30e7ce9231c822e37065aa3044c0793d`
- ESSIV key: `c6dea73a7b053b85e1782aa720ae61dd`

Notes:
- First 512 bytes of `hda.img` is the header → skip in decryption.
- Block numbers should start at 1, not 0.
- After decryption, re-add the header before writing the decrypted disk.

---

## ❌ Another Rabbit Hole

Mounted the decrypted image:

```bash
mount -t msdos -o loop,offset=32256 hda-decrypted.img /mnt/dos
```

Found two games: **Doom** and **Skyroads**

Assumed flag was hidden in sprites or mods — incorrect. Both games were original and unmodified.

---

## 🏁 Finding the Flag

Copied the decrypted image to a Windows VM and opened in **Autopsy**.

Autopsy found a hidden file: `_lag.txt`

Contents:

```
DDDDD DDDDD CCCCC {{ 1 EEEEEEE RRRRRR SSSSS TTTTTTT AAA ...
...
DDC{1._ERSTAT_BOOTLOADER_2._KRYPTER_DISK_3._????_4._PROFIT}
```

ASCII art format made it hard to read and submit the flag correctly.

### Issues Faced:
- Missed dots in flag
- Mixed up zeroes and O's
- Unsure of formatting rules

Eventually, the correct flag format was:

```
DDC{1._ERSTAT_BOOTLOADER_2._KRYPTER_DISK_3._????_4._PROFIT}
```

Translated:

1. Replace bootloader  
2. Encrypt disk  
3. ????  
4. Profit

---

## 💬 Final Thoughts

- Enjoyed the challenge, especially learning about MS-DOS and disk encryption.
- Slight frustration around flag format and lack of offline verification.
- Confirmed via support ticket that ASCII art was intentional — designed to avoid simple `grep` extraction.
- ASCII art made things harder for screen readers, but still a cool learning opportunity.

---

## ✅ TLDR

- Use `AESKeyFind` on `mem.dump` to extract two AES keys.
- Research AES-CBC-ESSIV — use https://github.com/trounce1/Android-AES/blob/master/android_aes.py
- Skip the first 512 bytes of the disk image when decrypting.
- Start sector decryption from block 1.
- Re-add the header and write out the full decrypted image.
- Mount or open with Autopsy and extract `_lag.txt`
- Parse ASCII art and decipher flag:
  ```
  DDC{1._ERSTAT_BOOTLOADER_2._KRYPTER_DISK_3._????_4._PROFIT}
  ```
