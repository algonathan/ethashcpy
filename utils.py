import binascii
from typing import List

import numpy as np
import sha3

WORD_BYTES = 4  # bytes in word
DATASET_BYTES_INIT = 2 ** 30  # bytes in dataset at genesis
DATASET_BYTES_GROWTH = 2 ** 23  # dataset growth per epoch
CACHE_BYTES_INIT = 2 ** 24  # bytes in cache at genesis
CACHE_BYTES_GROWTH = 2 ** 17  # cache growth per epoch
CACHE_MULTIPLIER = 1024  # Size of the DAG relative to the cache
EPOCH_LENGTH = 30000  # blocks per epoch
MAX_EPOCH = 2048
MIX_BYTES = 128  # width of mix
HASH_BYTES = 64  # hash length in bytes
DATASET_PARENTS = 256  # number of parents of each dataset element
CACHE_ROUNDS = 3  # number of rounds in cache production
ACCESSES = 64  # number of accesses in hashimoto loop
HASH_WORDS = 16  # Number of 32 bit ints in a hash

FNV_PRIME = 0x01000193


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


# TODO: find a way to avoid using numpy for this. it throws a runtime warning on wanted overflow.
def fnv(a, b):
    return (np.uint32(a) * np.uint32(0x01000193)) ^ np.uint32(b)


def fnv_hash(mix: List[int], data: List[int]):
    mix = np.array(mix, dtype="uint32")
    data = np.array(data, dtype="uint32")
    # using numpy to run in a loop fast:
    mix = (mix * 0x01000193) ^ data[:len(mix)]
    return mix.tolist()


def byte(v):
    return v & 0xff


def uint32_to_byte(v: int) -> bytearray:
    b = bytearray(4)
    b[0] = byte(v)
    b[1] = byte(v >> 8)
    b[2] = byte(v >> 16)
    b[3] = byte(v >> 24)

    return b


def bytes_into_uint32(inp: bytearray) -> List[int]:
    cache = []
    for i in range(0, len(inp), 4):
        cache.append(into_uint32(inp[i:i + 4]))
    return cache


def into_uint32(b):
    return int(b[0]) | int(b[1]) << 8 | int(b[2]) << 16 | int(b[3]) << 24


def into_bytearray(mix):
    return bytearray((byt for sublist in map(uint32_to_byte, mix) for byt in sublist))

def go_ints_to_list_of_ints(strr):
    """
    takes a list of ints in go as a string : '[1 2 3 4 5 6 7 8 9]'
    :return: the string into a python int list: [1, 2, 3, 4, 5,...
    """
    if "\n" in strr:
        strr = ' '.join(line.strip() for line in strr.split("\n"))
        strr = strr.strip()

    return [*map(int, strr.strip()[1:-1].split(" "))]
