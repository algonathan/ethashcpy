import copy

from utils import *


def create_cache(cache_size, seed):
    n = cache_size // HASH_BYTES

    # Sequentially produce the initial dataset
    o = [sha3_512_(seed)]
    for i in range(1, n):
        o.append(sha3_512_(o[-1]))

    # Use a low-round version of randmemohash
    for _ in range(CACHE_ROUNDS):
        for i in range(n):
            v = o[i][0] % n
            o[i] = sha3_512_([*map(xor, o[(i - 1 + n) % n], o[v])])

    return o


def compute_cache_size(block_number):
    sz = CACHE_BYTES_INIT + CACHE_BYTES_GROWTH * (block_number // EPOCH_LENGTH)
    sz -= HASH_BYTES
    while not isprime(sz / HASH_BYTES):
        sz -= 2 * HASH_BYTES
    return sz


def get_seedhash(blocknumber):
    s = '\x00' * 32
    s = s.encode("utf-8")
    for i in range(blocknumber // EPOCH_LENGTH):
        s = sha3_256_(s)
    return s


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
