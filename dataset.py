import copy

from utils import *
from typing import List
import numpy as np


def generate_cache_bytes(size, seed):
    keccak512 = sha3.keccak_512
    rows = size // HASH_BYTES
    cache = bytearray(size)
    cache[0:HASH_BYTES] = keccak512(seed).digest()

    for offset in range(HASH_BYTES, size, HASH_BYTES):
        cache[offset:] = bytearray(keccak512(cache[offset - HASH_BYTES:offset]).digest())

    tmp = bytearray(HASH_BYTES)
    for _ in range(CACHE_ROUNDS):
        for j in range(rows):
            src_offset = ((j - 1 + rows) % rows) * HASH_BYTES
            dst_offset = j * HASH_BYTES
            xor_offset = (into_uint32(cache[dst_offset:]) % rows) * HASH_BYTES

            safeXORBytes(tmp, cache[src_offset:src_offset + HASH_BYTES], cache[xor_offset:xor_offset + HASH_BYTES])
            cache[dst_offset:dst_offset + HASH_BYTES] = bytearray(keccak512(tmp).digest())
    return cache


def bytes_into_uint32(inp):
    cache = []
    for i in range(0, len(inp), 4):
        cache.append(into_uint32(inp[i:]))
    return cache


def generate_cache(size, seed):
    return bytes_into_uint32(generate_cache_bytes(size, seed))


def into_uint32(b):
    return int(b[0]) | int(b[1]) << 8 | int(b[2]) << 16 | int(b[3]) << 24


def safeXORBytes(dst, a, b):
    n = len(a)
    if len(b) < n:
        n = len(b)
    for i in range(n):
        dst[i] = a[i] ^ b[i]
    return n


def compute_cache_size(block_number):
    sz = CACHE_BYTES_INIT + CACHE_BYTES_GROWTH * (block_number // EPOCH_LENGTH)
    sz -= HASH_BYTES
    while not isprime(sz / HASH_BYTES):
        sz -= 2 * HASH_BYTES
    return sz


def seed_hash(block_num: int) -> bytearray:
    seed = bytearray(32)
    if block_num < EPOCH_LENGTH:
        return seed

    keccak256 = sha3.keccak_256
    for i in range(block_num // EPOCH_LENGTH):
        seed = keccak256(seed).digest()

    return seed


keccak512 = sha3.keccak_512


def byte(v):
    return v & 0xff


def uint32_to_byte(v: int) -> bytearray:
    b = bytearray(4)
    b[0] = byte(v)
    b[1] = byte(v >> 8)
    b[2] = byte(v >> 16)
    b[3] = byte(v >> 24)

    return b


def generate_dataset_item(cache: List[int], index: int) -> bytearray:
    rows = len(cache) // HASH_WORDS
    mix = bytearray(HASH_BYTES)

    # binary.LittleEndian.PutUint32(mix, cache[(index%rows)*hashWords]^index)
    mix[0:4] = uint32_to_byte(cache[(index % rows) * HASH_WORDS] ^ index)
    for i in range(1, HASH_WORDS):
        mix[i * 4:(i * 4) + 4] = uint32_to_byte(cache[(index % rows) * HASH_WORDS + i])

    mix = keccak512(mix).digest()
    # Convert the mix to uint32s to avoid constant bit shifting
    mix = bytes_into_uint32(mix)
    for i in range(DATASET_PARENTS):
        parent = fnv(index ^ i, mix[i % HASH_WORDS]) % rows
        mix = fnv_hash(mix, cache[parent * HASH_WORDS:])

    # Flatten so we can digest it:
    flattened = bytearray((byt for sublist in map(uint32_to_byte, mix) for byt in sublist))
    retval = keccak512(flattened).digest()
    return retval
