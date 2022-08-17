# defining POW verification:
from typing import Callable, List, Tuple
from utils import *
import dataset

WORD_BYTES = 4  # bytes in word
DATASET_BYTES_INIT = 2 ** 30  # bytes in dataset at genesis
DATASET_BYTES_GROWTH = 2 ** 23  # dataset growth per epoch
CACHE_BYTES_INIT = 2 ** 24  # bytes in cache at genesis
CACHE_BYTES_GROWTH = 2 ** 17  # cache growth per epoch
CACHE_MULTIPLIER = 1024  # Size of the DAG relative to the cache
EPOCH_LENGTH = 30000  # blocks per epoch
MIX_BYTES = 128  # width of mix
HASH_BYTES = 64  # hash length in bytes
DATASET_PARENTS = 256  # number of parents of each dataset element
CACHE_ROUNDS = 3  # number of rounds in cache production
ACCESSES = 64  # number of accesses in hashimoto loop


# hashimoto aggregates data from a dataset in order to produce our final
# value for a particular header hash and nonce.
# hashimoto(hash []byte, nonce uint64, size uint64, lookup func(index uint32) []uint32) ([]byte, []byte) {
def hashimoto(header, nonce, full_size, dataset_lookup):
    n = full_size // HASH_BYTES
    w = MIX_BYTES // WORD_BYTES
    mixhashes = MIX_BYTES // HASH_BYTES
    # combine header+nonce into a 64 byte seed
    seed = [*map(int, sha3_512_(header + nonce[::-1]))]  # todo, turn into list of uint8.
    # start the mix with replicated seed
    mix = []
    for _ in range(MIX_BYTES // HASH_BYTES):
        mix.extend(seed)

    # mix in random dataset nodes
    for i in range(ACCESSES):
        tmp = fnv(i ^ seed[0], mix[i % w])
        p = tmp % (n // mixhashes) * mixhashes
        newdata = []
        for j in range(MIX_BYTES // HASH_BYTES):
            newdata.extend(dataset_lookup(p + j))
        mix = [*map(fnv, mix, newdata)]
    # compress mix
    cmix = []
    for i in range(0, len(mix), 4):
        cmix.append(fnv(fnv(fnv(mix[i], mix[i + 1]), mix[i + 2]), mix[i + 3]))

    return {
        "mix digest": serialize_hash(cmix),
        "result": serialize_hash(sha3_256_(seed + cmix)),
    }


hashready = "123".encode("utf-8")


def hashimoto_tmp(full_size, _, header, nonce):
    return hashimoto(header, nonce, full_size, lambda x: sha3.keccak_512(hashready).digest())


def hashimoto_light(full_size, cache, header, nonce):
    return hashimoto(header, nonce, full_size, lambda x: dataset.generate_dataset_item(cache, x))


if __name__ == '__main__':
    round = 1
    cache_size = dataset.compute_cache_size(1)
    seedhash = dataset.seed_hash(round)
    print("Prepare cache...")
    cache = dataset.generate_cache(1024, seedhash)

    nonce = (67).to_bytes(8, byteorder="little", signed=False)
    o = hashimoto_light(cache_size, cache, nonce, nonce)
    print(o)
