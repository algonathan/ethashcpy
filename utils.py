import binascii

import sha3, copy

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


# Assumes little endian bit ordering (same as Intel architectures)
def decode_int(s):
    return int(binascii.hexlify(s), 16)
    # s = '%s' % s
    # return int(s[::-1].encode('hex'), 16) if s else 0


# encode_int taken from eth code.
def encode_int(int_list):
    a = "%x" % int_list
    return '' if int_list == 0 else ('0' * (len(a) % 2) + a)[::-1]


def zpad(s, length):
    """
    :param s: hexstring
    :param length: the wanted length for each 'int'
    :return: returns a padded hexstring.
    """
    return s + '\x00' * max(0, length - len(s))


def serialize_hash(h):
    hexified = map(encode_int, h)
    padded_ints = map(lambda x: zpad(x, 4), hexified)
    return ''.join(padded_ints)


def deserialize_hash(h):
    return [decode_int(h[i:i + WORD_BYTES]) for i in range(0, len(h), WORD_BYTES)]


def hash_words(h, sz, x):
    if isinstance(x, list):
        x = serialize_hash(x)
        if isinstance(x, str):  # TODO: not certain about this: but otherwise can't make it work...
            x = x.encode("utf-8")
    y = h(x)
    return deserialize_hash(y)


def serialize_cache(ds):
    return ''.join([serialize_hash(h) for h in ds])


serialize_dataset = serialize_cache


# sha3 hash function, outputs 64 bytes
def sha3_512_(x):
    return hash_words(lambda v: sha3.sha3_512(v).digest(), 64, x)


def sha3_256_(x):
    return hash_words(lambda v: sha3.sha3_256(v).digest(), 32, x)


def xor(a, b):
    return a ^ b


def isprime(x):
    for i in range(2, int(x ** 0.5)):
        if x % i == 0:
            return False
    return True


def fnv(v1, v2):
    fnv_prime = 0x01000193
    return ((v1 * fnv_prime) ^ v2) % 2 ** 32
