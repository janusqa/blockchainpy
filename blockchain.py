from functools import reduce
import json
import pickle
import copy
from urllib.error import HTTPError
import requests

from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet


class Blockchain:

    MINING_REWARD = 10

    def __init__(self, public_key, port):
        genesis_block = Block(0, "", [], 100, 0)
        self.blockchain = [genesis_block]
        self.open_transactions = []
        self.peer_nodes = set()
        self.node = public_key
        self.node_port = port
        self.resolve_conflicts = False
        self.load_data()

    @property
    def blockchain(self):
        return copy.deepcopy(self.__blockchain)

    @blockchain.setter
    def blockchain(self, blockchain):
        self.__blockchain = blockchain

    @property
    def open_transactions(self):
        return copy.deepcopy(self.__open_transactions)

    @open_transactions.setter
    def open_transactions(self, transactions):
        self.__open_transactions = transactions

    @property
    def peer_nodes(self):
        return copy.copy(self.__peer_nodes)

    @peer_nodes.setter
    def peer_nodes(self, node_list):
        self.__peer_nodes = node_list
        if len(self.__peer_nodes) > 0:
            self.save_data()

    def save_data(self):
        try:
            with open(f"./blockchain_{self.node_port}.txt", mode="w") as f:
                saveable_chain = [
                    block.to_ordered_dict() for block in self.__blockchain
                ]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_transactions = [
                    tx.to_ordered_dict() for tx in self.__open_transactions
                ]
                f.write(json.dumps(saveable_transactions))
                f.write("\n")
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print("Saving failed!")

    def load_data(self):
        try:
            with open(f"./blockchain_{self.node_port}.txt", mode="r") as f:
                file_content = f.readlines()
            loaded_blockchain = json.loads(file_content[0][:-1])  # skip \n at end
        except (FileNotFoundError, IndexError):
            print(f"./blockchain_{self.node_port}.txt")
            # genesis_block = Block(0, "", [], 100, 0)
            # self.__blockchain = [genesis_block]
            # self.__open_transactions = []
            print("No blockchain file found. Initilizing blockchain file.")
            self.save_data()
        else:
            updated_blockchain = []
            for block in loaded_blockchain:
                updated_block = Block(
                    block["index"],
                    block["previous_hash"],
                    [
                        Transaction(
                            tx["signature"], tx["recipient"], tx["sender"], tx["amount"]
                        )
                        for tx in block["transactions"]
                    ],
                    block["proof"],
                    block["timestamp"],
                )
                updated_blockchain.append(updated_block)
            self.blockchain = updated_blockchain  # using setter here
            ot = json.loads(file_content[1][:-1])
            self.open_transactions = [
                Transaction(
                    tx["signature"], tx["recipient"], tx["sender"], tx["amount"]
                )
                for tx in ot
            ]  # using setter
            self.peer_nodes = set(json.loads(file_content[2]))

    def proof_of_work(self):
        last_block = self.get_last_blockchain_value()
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        if sender == None:
            participant = self.node
        else:
            participant = sender
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

    def add_transaction(self, signature, recipient, sender, amount=1.0, broadcast=True):
        transaction = Transaction(signature, recipient, sender, amount)
        if not Verification.verify_transaction(transaction, self.get_balance):
            return False
        self.__open_transactions.append(transaction)
        self.save_data()
        if broadcast:
            for node in self.__peer_nodes:
                url = f"http://{node}/broadcast-transaction"
                try:
                    response = requests.post(
                        url,
                        json=transaction.to_ordered_dict(),
                    )
                    response.raise_for_status()
                except requests.exceptions.ConnectionError:
                    continue
                except:
                    print("Transaction declined, needs resolving.")
                    return False
        return True

    def mine_block(self):
        hashed_block = hash_block(self.get_last_blockchain_value())
        # print(hashed_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction(
            "", self.node, "MINING", Blockchain.MINING_REWARD
        )
        copied_transactions = self.open_transactions  # using getter to return a copy
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__blockchain), hashed_block, copied_transactions, proof)
        self.__blockchain.append(block)
        self.open_transactions = []  # using setter
        if not Verification.verify_chain(self.__blockchain):
            return None
        self.save_data()
        for node in self.__peer_nodes:
            url = f"http://{node}/broadcast-block"
            try:
                response = requests.post(
                    url,
                    json={"block": block.to_ordered_dict()},
                )
                response.raise_for_status()
            except requests.exceptions.ConnectionError:
                continue
            except:
                print("Block declined, needs resolving.")
                if response.status_code == 409:
                    self.resolve_conflicts = True
                # return False
        return block

    def add_block(self, block):
        transactions = [
            Transaction(tx["signature"], tx["recipient"], tx["sender"], tx["amount"])
            for tx in block["transactions"]
        ]
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block["previous_hash"], block["proof"]
        )
        hashes_match = (
            hash_block(self.get_last_blockchain_value()) == block["previous_hash"]
        )
        if not (proof_is_valid and hashes_match):
            return False
        self.__blockchain.append(
            Block(
                block["index"],
                block["previous_hash"],
                transactions,
                block["proof"],
                block["timestamp"],
            )
        )
        stored_transactions = self.open_transactions
        for brodcasted_tx in transactions:
            for local_open_tx in stored_transactions:
                if brodcasted_tx.signature == local_open_tx.signature:
                    try:
                        stored_transactions.remove(local_open_tx)
                        self.open_transactions = stored_transactions
                    except ValueError:
                        print("Item already removed")
                    break
        self.save_data()
        return True

    def resolve(self):
        resolved_blockchain = self.blockchain
        local_blockchain_patched = False
        for node in self.peer_nodes:
            url = f"http://{node}/blockchain"
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                continue
            else:
                peer_blockchain = response.json()["blockchain"]
                peer_blockchain = [
                    Block(
                        blk["index"],
                        blk["previous_hash"],
                        [
                            Transaction(
                                tx["signature"],
                                tx["recipient"],
                                tx["sender"],
                                tx["amount"],
                            )
                            for tx in blk["transactions"]
                        ],
                        blk["proof"],
                        blk["timestamp"],
                    )
                    for blk in peer_blockchain
                ]
                if (
                    len(peer_blockchain) > len(resolved_blockchain)
                ) and Verification.verify_chain(peer_blockchain):
                    resolved_blockchain = peer_blockchain
                    local_blockchain_patched = True
            self.resolve_conflicts = True
            self.blockchain = resolved_blockchain
            if local_blockchain_patched:
                self.open_transactions = []
            self.save_data()
            return local_blockchain_patched
