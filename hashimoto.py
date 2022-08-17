# defining POW verification:
from typing import Callable

import sha3

from utils import *
import dataset


# hashimoto aggregates data from a dataset in order to produce our final
# value for a particular header hash and nonce.
# hashimoto(hash []byte, nonce uint64, size uint64, lookup func(index uint32) []uint32) ([]byte, []byte) {
def hashimoto(hash: bytearray, nonce: np.uint64, size: np.uint64, lookup: Callable[[np.uint32], List[np.uint32]]):
    # pass
    rows = size // MIX_BYTES
    seed = hash + bytearray(x for x in (int(nonce)).to_bytes(8, "little"))
    seed = bytearray(sha3.keccak_512(seed).digest())

    seedhead = into_uint32(seed[0:4])

    # Start the mix with replicated seed:
    mix = []
    for i in range(MIX_BYTES // 4):
        pos = (i % 16) * 4
        mix.append(into_uint32(seed[pos:pos + 4]))

    tmp = [0] * len(mix)  # make([]uint32, len(mix))
    for i in range(ACCESSES):
        parent = fnv(np.uint32(i) ^ seedhead, mix[i % len(mix)]) % rows
        for j in range(MIX_BYTES // HASH_BYTES):
            tmp[j * HASH_WORDS:] = lookup(2 * parent + j)
        mix = fnv_hash(mix, tmp)

    # compress mix stage:
    for i in range(0, len(mix), 4):
        mix[i // 4] = fnv(fnv(fnv(mix[i], mix[i + 1]), mix[i + 2]), mix[i + 3])
    mix = mix[:len(mix) // 4]

    digest = into_bytearray(mix)
    return digest, sha3.keccak_256(seed + digest).digest()


# TODO: the look up function is not in the correct types.
def hashimoto_light(full_size, cache, header, nonce):
    return hashimoto(header, nonce, full_size, lambda x: bytes_into_uint32(dataset.generate_dataset_item(cache, x)))
