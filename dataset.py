import copy
import time

from utils import *
from typing import List
import numpy as np


def generate_cache_bytes(size, seed, debug) -> bytearray:
    keccak512 = sha3.keccak_512
    rows = size // HASH_BYTES
    cache = bytearray(size)
    cache[0:HASH_BYTES] = keccak512(seed).digest()

    for offset in range(HASH_BYTES, size, HASH_BYTES):
        cache[offset:] = keccak512(cache[offset - HASH_BYTES:offset]).digest()
    if debug:
        print("first pass through the cache done.")

    for i in range(CACHE_ROUNDS):
        for j in range(rows):
            src_offset = ((j - 1 + rows) % rows) * HASH_BYTES
            dst_offset = j * HASH_BYTES
            xor_offset = (into_uint32(cache[dst_offset:dst_offset + 4]) % rows) * HASH_BYTES

            tmp = xor_bytes(cache[src_offset:src_offset + HASH_BYTES], cache[xor_offset:xor_offset + HASH_BYTES])
            cache[dst_offset:dst_offset + HASH_BYTES] = keccak512(tmp).digest()

        if debug:
            print(f"cache round {i + 1} out of {CACHE_ROUNDS} done.")
    return cache


def generate_cache(cache_size: int, seed: bytearray, debug=False) -> List[int]:
    cache = generate_cache_bytes(cache_size, seed, debug)
    if debug:
        print("turning byte_cache into ints")
    cache_as_ints = bytes_into_uint32(cache)
    if debug:
        print("...done")
    return cache_as_ints


def xor_bytes(a, b):
    return np.array(a) ^ np.array(b)


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
        mix = fnv_hash(mix, cache[parent * HASH_WORDS:parent * HASH_WORDS + len(mix)])

    # Flatten so we can digest it:
    flattened = into_bytearray(mix)
    return keccak512(flattened).digest()


