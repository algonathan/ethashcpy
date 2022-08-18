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
    """
    	hash := []byte{83, 28, 70, 106, 195, 52, 23, 62, 95, 236, 120, 162, 252,
		121, 18, 195, 19, 68, 164, 191, 83, 114, 54, 17, 53, 113,
		137, 211, 65, 136, 221, 125}

	cache := make([]uint32, cacheSize(1))
	generateCache(cache, 0, seedHash(1))
	fmt.Println(cache[len(cache)-10 : len(cache)])
	digest, mix := hashimoto(hash, 0, uint64(len(cache)), func(i uint32) []uint32 {
		return []uint32{1, 2, 3, 4, 56, 78, 8, 9, 65, 32, 14, 43, 325, 6, 65, 56, 657, 45, 342, 231, 42, 745, 865}
	})
    """
    print("testing hashimoto")
    np.random.randint(0, 255, 32)
    cache_size = dataset.compute_cache_size_as_uints(1) // 4
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
    print("...hashimoto test passed")


def tst_hashimoto_light():
    """
    Go code that produce the expected results:
    hash := []byte{83, 28, 70, 106, 195, 52, 23, 62, 95, 236, 120, 162, 252,
		121, 18, 195, 19, 68, 164, 191, 83, 114, 54, 17, 53, 113,
		137, 211, 65, 136, 221, 125}

	cache := make([]uint32, cacheSize(1))
	generateCache(cache, 0, seedHash(1))
	fmt.Println(cache[len(cache)-10 : len(cache)])
	digest, mix := hashimotoLight(uint64(len(cache)), cache, hash, 0)
    """
    print("tst_hashimoto_light")
    round = 1
    cache_size = dataset.compute_cache_size(round)

    print("...generating cache")
    cache = dataset.generate_cache(cache_size, bytearray([0] * 32))

    print("...running hashimoto_light")
    digest, mix = hashimoto.hashimoto_light(len(cache), cache, header_hash, 0)
    digest = [x for x in digest]
    mix = [x for x in mix]

    go_digest = "[130 32 71 89 1 254 121 151 117 30 89 92 62 201 171 5 246 182 196 162 115 246 143 185 233 95 240 232 38 163 79 133]"
    go_mix = "[113 201 40 25 189 79 36 107 179 67 198 83 252 230 74 108 198 160 148 216 91 195 34 236 0 0 155 126 21 215 215 46]"

    if digest != go_ints_to_list_of_ints(go_digest):
        raise Exception("hashimoto_light digest not equal to same as go.")
    if mix != go_ints_to_list_of_ints(go_mix):
        raise Exception("hashimoto_light mix not equal to same as go.")
    print("...hashimoto_light test passed")


if __name__ == '__main__':
    tst_hashimoto()
    tst_hashimoto_light()
