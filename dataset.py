import copy

from utils import *
from typing import List


def create_cache(cache_size, seed):
    rows = cache_size // HASH_BYTES

    # Sequentially produce the initial dataset
    o = [sha3_512_(seed)]
    for i in range(1, rows):
        o.append(sha3_512_(o[-1]))

    # Use a low-round version of randmemohash
    for _ in range(CACHE_ROUNDS):
        for i in range(rows):
            v = o[i][0] % rows
            o[i] = sha3_512_([*map(xor, o[(i - 1 + rows) % rows], o[v])])

    return o


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

    print(f"in: {block_num} out: {seed}\n", block_num, seed)
    return seed


def calc_dataset_item(cache, i):
    n = len(cache)
    r = HASH_BYTES // WORD_BYTES
    # initialize the mix
    mix = copy.copy(cache[i % n])
    mix[0] ^= i
    mix = sha3_512_(mix)
    # fnv it with a lot of random cache nodes based on i
    for j in range(DATASET_PARENTS):
        cache_index = fnv(i ^ j, mix[j % r])
        mix = [*map(fnv, mix, cache[cache_index % n])]
    return sha3_512_(mix)
