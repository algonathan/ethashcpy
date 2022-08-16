from dataset import *
from utils import *


def go_ints_to_list_of_ints(strr):
    """
    takes a list of ints in go as a string : '[1 2 3 4 5 6 7 8 9]'
    :return: the string into a python int list: [1, 2, 3, 4, 5,...
    """
    return [*map(int, strr[1:-1].split(" "))]


def check_seed_hash():
    tst_cases = [
        {
            "epoch": 0,
            "result_in_go_code": "[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]"
        },
        {
            "epoch": 1,
            "result_in_go_code": "[41 13 236 217 84 139 98 168 214 3 69 169 136 56 111 200 75 166 188 149 72 64 8 246 54 47 147 22 14 243 229 99]"
        },
    ]
    for tst in tst_cases:
        round = tst["epoch"] * EPOCH_LENGTH + 1
        result = seed_hash(round)
        result_as_int_list = [x for x in result]
        if result_as_int_list == go_ints_to_list_of_ints(tst["result_in_go_code"]):
            continue
        raise Exception("Test failed", tst)


if __name__ == '__main__':
    check_seed_hash()
    # expectation = go_ints_to_list_of_ints(
    #     "[41 13 236 217 84 139 98 168 214 3 69 169 136 56 111 200 75 166 188 149 72 64 8 246 54 47 147 22 14 243 229 "
    #     "99]")
    # print(expectation)
    #
    # zeroseedhash = seed_hash(30001)
    # print([x for x in zeroseedhash])
