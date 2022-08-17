# defining POW verification:

from utils import *
import dataset


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


def hashimoto_light(full_size, cache, header, nonce):
    return hashimoto(header, nonce, full_size, lambda x: dataset.generate_dataset_item(cache, x))
