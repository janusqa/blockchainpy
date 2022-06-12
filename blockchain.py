from functools import reduce
import json
import pickle
from typing import List

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

owner = "Max"
participants = set(["Max"])
MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, "", [], 100, 0)
        self.blockchain = [genesis_block]
        self.open_transactions = []
        self.node = hosting_node_id
        self.load_data()

    @property
    def blockchain(self):
        return self.__blockchain[:]

    @blockchain.setter
    def blockchain(self, blockchain):
        self.__blockchain = blockchain

    @property
    def open_transactions(self):
        return self.__open_transactions[:]

    @open_transactions.setter
    def open_transactions(self, transactions):
        self.__open_transactions = transactions

    def save_data(self):
        try:
            with open("./blockchain.txt", mode="w") as f:
                saveable_chain = [
                    block.to_ordered_dict() for block in self.__blockchain
                ]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_transactions = [
                    tx.to_ordered_dict() for tx in self.__open_transactions
                ]
                f.write(json.dumps(saveable_transactions))
        except IOError:
            print("Saving failed!")

    def load_data(self):
        try:
            with open("./blockchain.txt", mode="r") as f:
                file_content = f.readlines()
            loaded_blockchain = json.loads(file_content[0][:-1])  # skip \n at end
        except (FileNotFoundError, IndexError):
            # genesis_block = Block(0, "", [], 100, 0)
            # self.__blockchain = [genesis_block]
            # self.__open_transactions = []
            print("File load error. Falling back to defaults.")
        else:
            updated_blockchain = []
            for block in loaded_blockchain:
                updated_block = Block(
                    block["index"],
                    block["previous_hash"],
                    [
                        Transaction(tx["sender"], tx["recipient"], tx["amount"])
                        for tx in block["transactions"]
                    ],
                    block["proof"],
                    block["timestamp"],
                )
                updated_blockchain.append(updated_block)
            self.blockchain = updated_blockchain  # using setter here
            ot = json.loads(file_content[1])
            self.open_transactions = [
                Transaction(tx["sender"], tx["recipient"], tx["amount"]) for tx in ot
            ]  # using setter

    def proof_of_work(self):
        last_block = self.get_last_blockchain_value()
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.node
        tx_sender = [
            [tx.amount for tx in block.transactions if tx.sender == participant]
            for block in self.__blockchain
        ]
        open_tx_sender = [
            tx.amount for tx in self.__open_transactions if tx.sender == participant
        ]
        tx_recipient = [
            [tx.amount for tx in block.transactions if tx.recipient == participant]
            for block in self.__blockchain
        ]
        amount_sent = 0
        amount_received = 0
        amount_sent += reduce(
            lambda accumulator, el: accumulator + sum(el)
            if len(el) > 0
            else accumulator + 0,
            tx_sender,
            0,
        )
        amount_sent += reduce(
            lambda accumulator, el: accumulator + el, open_tx_sender, 0
        )
        amount_received += reduce(
            lambda accumulator, el: accumulator + sum(el)
            if len(el) > 0
            else accumulator + 0,
            tx_recipient,
            0,
        )
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        if len(self.__blockchain) > 0:
            return self.__blockchain[-1]
        return None

    def add_transaction(self, recipient, sender, amount=1.0):
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        hashed_block = hash_block(self.get_last_blockchain_value())
        # print(hashed_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction("MINING", self.node, MINING_REWARD)
        copied_transactions = self.open_transactions  # using getter to return a copy
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__blockchain), hashed_block, copied_transactions, proof)
        self.__blockchain.append(block)
        self.open_transactions = []  # using setter
        if Verification.verify_chain(self.__blockchain):
            self.save_data()
        return True
