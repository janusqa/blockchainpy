import hashlib
import json
from typing import Hashable


def hash_block(block):
    # use encode to convert string retuned from json to utf-8
    # binary string to be used by sha256
    # Additionally lets sort the keys of the dict we are dumping to
    # json to guarnetee that the order of the keys is always the same.
    # Recall that dict is an unordered data structure where the order
    # of the keys can change at any moment for any reason.
    # Our hashing DEPENDS on the fact that the keys should be in
    # same exact order when dumping to json so that when we recaulate
    # hashes we are confident its always on the same string
    # NOTE: we could have used an ordered dict from the collections library
    # but just want to showcase sort_keys of json.dumps.  We will
    # use orderedDict with the transaction dictionaries to ensure
    # that they too are ordered as they will have the same problem
    # if we try to strinify or hash them and there is the possibility
    # of the keys in the dict changing order
    hashable_block = block.to_ordered_dict()
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()
