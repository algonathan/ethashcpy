#


import numpy as np
import sha3
from utils import *
import dataset
import hashimoto

header_hash = bytearray([83, 28, 70, 106, 195, 52, 23, 62, 95, 236, 120, 162, 252,
                         121, 18, 195, 19, 68, 164, 191, 83, 114, 54, 17, 53, 113,
                         137, 211, 65, 136, 221, 125])


def tst_hashimoto():
    np.random.randint(0, 255, 32)
    cache_size = dataset.compute_cache_size(1) // 4
    lookup = lambda _: [1, 2, 3, 4, 56, 78, 8, 9, 65, 32, 14, 43, 325, 6, 65, 56, 657, 45, 342, 231, 42, 745, 865]
    digest, mix = hashimoto.hashimoto(header_hash, np.uint64(0), cache_size, lookup)
    digest_ints = [x for x in digest]
    mix_ints = [x for x in mix]

    if digest_ints != go_ints_to_list_of_ints(
            "[195 61 228 238 81 26 11 227 177 123 123 16 93 106 116 143 195 61 228 238 81 26 11 227 177 123 123 16 93 "
            "106 116 143] "):
        raise Exception("hashimoto digest as ints not equal to same as go.")

    if mix_ints != go_ints_to_list_of_ints(
            "[234 24 136 64 152 155 18 5 40 76 134 220 35 75 100 194 160 84 151 68 134 231 202 28 80 245 163 111 99 "
            "175 81 222] "):
        raise Exception("hashimoto result as ints not equal to same as go.")


def tst_hashimoto_light():
    print("tst_hashimoto_light")
    round = 1
    cache_size = dataset.compute_cache_size(round)

    print("...generating cache")
    # using seed = 0 in cache generation:
    cache = dataset.generate_cache(cache_size, dataset.seed_hash(round))
    print(cache[len(cache) - 10:len(cache)])
    print("...running hashimoto_light")
    digest, mix = hashimoto.hashimoto_light(cache_size, cache, header_hash, 0)
    print(*(x for x in digest))
    print(*(x for x in mix))


if __name__ == '__main__':
    tst_hashimoto()
    tst_hashimoto_light()
