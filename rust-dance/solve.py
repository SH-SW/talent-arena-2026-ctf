#!/usr/bin/env python3
"""
Rust-Dance CTF Solver
Reverses the "dance" transformations applied to the input to find the unlock code.

The binary applies these transformations to the 19-byte input:
1. XOR bytes [0],[1],[2] with 0x42, 0x59, 0x70 then swap them to positions [18],[17],[16]
2. XOR bytes [3..18] with a 16-byte key (pxor at 0x3cf0)
3. Reverse the 16 bytes [0..15] using SIMD shuffles (punpcklbw/punpckhbw + pshufd/pshuflw/pshufhw)
4. ROL/ROR loop: for each byte i in [0..18], rotate based on i%7, i%5, and parity of i
5. ADD bytes [0..15] with paddb constant (0x3d10), bytes [16],[17],[18] with 0x43, 0xbc, 0x45
6. Nibble swap (shift left 4, shift right 4, OR) on bytes [0..15] and ROL 4 on [16],[17],[18]
7. Final comparison: XOR with expected values at 0x3b50, 0x3df0, 0x3d20, 0x3cb0 must all be 0
   Plus bytes [16],[17],[18] XOR with 0xc6, 0x28, 0x8a must be 0

So we reverse from the expected output back to the input.
"""

# Expected final values (from pxor comparisons - must XOR to zero)
# bytes[0:4]   XOR with data at 0x3b50 = 0
# bytes[4:8]   XOR with data at 0x3df0 = 0
# bytes[8:12]  XOR with data at 0x3d20 = 0
# bytes[12:16] XOR with data at 0x3cb0 = 0
# byte[16] XOR 0xc6 = 0 -> byte[16] = 0xc6
# byte[17] XOR 0x28 = 0 -> byte[17] = 0x28
# byte[18] XOR 0x8a = 0 -> byte[18] = 0x8a

expected = bytearray([
    0x0e, 0xac, 0x94, 0x46,  # from 0x3b50
    0xc6, 0x6f, 0xbe, 0x72,  # from 0x3df0
    0xb7, 0x5d, 0x79, 0xee,  # from 0x3d20
    0xe2, 0xd0, 0xed, 0xa2,  # from 0x3cb0
    0xc6,                     # XOR 0xc6 = 0
    0x28,                     # XOR 0x28 = 0
    0x8a,                     # XOR 0x8a = 0
])



data = bytearray(expected)
print(f"Step 0 (expected final): {data.hex()}")

# REVERSE STEP 6: nibble swap on all bytes (self-inverse)
for i in range(19):
    b = data[i]
    data[i] = ((b << 4) & 0xf0) | ((b >> 4) & 0x0f)
print(f"Step 1 (undo nibble swap): {data.hex()}")

# REVERSE STEP 5: subtract constants
paddb_const = bytes([0x33, 0xcc, 0x35, 0xca, 0x37, 0xc8, 0x39, 0xc6,
                     0x3b, 0xc4, 0x3d, 0xc2, 0x3f, 0xc0, 0x41, 0xbe])
for i in range(16):
    data[i] = (data[i] - paddb_const[i]) & 0xff
data[16] = (data[16] - 0x43) & 0xff
data[17] = (data[17] - 0xbc) & 0xff
data[18] = (data[18] - 0x45) & 0xff
print(f"Step 2 (undo add): {data.hex()}")

# REVERSE STEP 4: undo rotations (in reverse order)
for i in range(18, -1, -1):
    r8 = (i + 1) & 0xff
    if i % 2 == 0:  # even -> forward did ROL, undo with ROR
        q = i // 7
        rem = i - 7 * q
        shift = (r8 - 7 * q) & 0xff
        shift = shift % 8
        b = data[i]
        data[i] = ((b >> shift) | (b << (8 - shift))) & 0xff
    else:  # odd -> forward did ROR, undo with ROL
        q = i // 5
        shift = (r8 - 5 * q) & 0xff
        shift = shift % 8
        b = data[i]
        data[i] = ((b << shift) | (b >> (8 - shift))) & 0xff
print(f"Step 3 (undo rot): {data.hex()}")

# Now data[0:16] = reverse(XOR(input[3:19], key))
# data[16:19] = [input[2]^0x70, input[1]^0x59, input[0]^0x42]

# REVERSE STEP 3: undo reverse on [0:16]
data[0:16] = data[0:16][::-1]
print(f"Step 4 (undo reverse): {data.hex()}")

# Now data[0:16] = XOR(input[3:19], key)
# REVERSE STEP 2: undo XOR on [0:16] to get input[3:19]
xor_key = bytes([0x87, 0x9e, 0xb5, 0xcc, 0xe3, 0xfa, 0x11, 0x28,
                 0x3f, 0x56, 0x6d, 0x84, 0x9b, 0xb2, 0xc9, 0xe0])
for i in range(16):
    data[i] ^= xor_key[i]
print(f"Step 5 (undo xor): {data.hex()}")

# Now data[0:16] = input[3:19]
# REVERSE STEP 1: recover input[0:3] from data[16:19]
input_0 = data[18] ^ 0x42
input_1 = data[17] ^ 0x59
input_2 = data[16] ^ 0x70

# Reconstruct the full 19-byte input
original = bytearray(19)
original[0] = input_0
original[1] = input_1
original[2] = input_2
original[3:19] = data[0:16]

print(f"\nOriginal input bytes: {original.hex()}")
print(f"Original input (ASCII): {original.decode('ascii', errors='replace')}")
print(f"\nUnlock code: {original.decode('ascii', errors='replace')}")
