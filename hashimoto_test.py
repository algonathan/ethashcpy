#


#
import json
import os

import dataset
import hashimoto


def tst_hashimoto_light():
    print("tst_hashimoto_light")
    round = 1
    cache_size = dataset.compute_cache_size(round) // 4

    print("...generating cache")
    cache = dataset.generate_cache(cache_size, bytearray([0] * 32))

    header_hash = bytearray("0xc9149cc0386e689d789a1c2f3d5d169a61a6218ed30e74414dc736e442ef3d1f", "utf-8")
    nonce = bytearray([0] * 8)
    print("...running hashimoto_light")
    o = hashimoto.hashimoto_light(cache_size, cache, header_hash, nonce)
    print("...done; printing result:", o)
    print("...m:", [x for x in bytearray(o["mix digest"], "utf-8")])
    print("...n:", [x for x in bytearray(o["result"], "utf-8")])


if __name__ == '__main__':
    tst_hashimoto_light()
