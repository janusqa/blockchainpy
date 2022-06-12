from time import time
from collections import OrderedDict
from printable import Printable
from transaction import Transaction
from typing import List


class Block(Printable):
    def __init__(
        self,
        index,
        previous_hash,
        transactions: List[Transaction],
        proof,
        timestamp=None,
    ) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time() if timestamp is None else timestamp

    def to_ordered_dict(self):
        return OrderedDict(
            [
                ("index", self.index),
                ("previous_hash", self.previous_hash),
                ("transactions", [tx.to_ordered_dict() for tx in self.transactions]),
                ("proof", self.proof),
                ("timestamp", self.timestamp),
            ]
        )
