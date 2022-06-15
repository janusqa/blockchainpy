from collections import OrderedDict

from utility.printable import Printable


class Transaction(Printable):
    def __init__(self, signature, recipient, sender, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict(
            [
                ("signature", self.signature),
                ("sender", self.sender),
                ("recipient", self.recipient),
                ("amount", self.amount),
            ]
        )
