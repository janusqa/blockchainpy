from functools import reduce
from collections import OrderedDict
import json
import pickle

from hash_util import hash_string_256, hash_block
from block import Block
from transaction import Transaction

blockchain = []
open_transactions = []
owner = "Max"
participants = set(["Max"])
MINING_REWARD = 10


def save_data():
    try:
        with open("./blockchain.txt", mode="w") as f:
            saveable_chain = [block.to_ordered_dict() for block in blockchain]
            f.write(json.dumps(saveable_chain))
            f.write("\n")
            saveable_transactions = [tx.to_ordered_dict() for tx in open_transactions]
            f.write(json.dumps(saveable_transactions))

        # we can also use pickel to write data to binary file instead of json
        # pickle can serialze objects to strings and unseralize those stings back to python objects
        # remember to set file mode correctly. In this case "wb"
        # with open("./blockchain.p", mode="wb") as f:
        # save_data_dump = {"bc": blockchain, "ot": open_transactions}
        # f.write(pickle.dumps(save_data_dump))
    except IOError:
        print("Saving failed!")


def load_data():
    global blockchain, open_transactions
    try:
        with open("./blockchain.txt", mode="r") as f:
            file_content = f.readlines()
        # with open("./blockchain.p", mode="rb") as f:
        #     file_content = pickle.loads(f.read())
        blockchain = json.loads(file_content[0][:-1])  # skip \n at end
        # blockchain = file_content["bc"]
    except (FileNotFoundError, IndexError):
        genesis_block = Block(0, "", [], 100, 0)
        # genesis_block = OrderedDict(
        #     [
        #         ("previous_hash", ""),
        #         ("index", 0),
        #         ("transactions", []),
        #         ("proof", 100),
        #     ]
        # )
        blockchain = [genesis_block]
        open_transactions = []
    else:
        updated_blockchain = []
        for block in blockchain:
            updated_block = Block(
                block["index"],
                block["previous_hash"],
                [
                    # OrderedDict(
                    #     [
                    #         ("sender", tx["sender"]),
                    #         ("recipient", tx["recipient"]),
                    #         ("amount", tx["amount"]),
                    #     ]
                    # )
                    Transaction(tx["sender"], tx["recipient"], tx["amount"])
                    for tx in block["transactions"]
                ],
                block["proof"],
                block["timestamp"],
            )
            # updated_block = OrderedDict(
            #     [
            #         ("previous_hash", block["previous_hash"]),
            #         ("index", block["index"]),
            #         ("proof", block["proof"]),
            #         (
            #             "transactions",
            #             [
            #                 OrderedDict(
            #                     [
            #                         ("sender", tx["sender"]),
            #                         ("recipient", tx["recipient"]),
            #                         ("amount", tx["amount"]),
            #                     ]
            #                 )
            #                 for tx in block["transactions"]
            #             ],
            #         ),
            #     ]
            # )
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain
        ot = json.loads(file_content[1])
        # ot = file_content["ot"]
        open_transactions = [
            # OrderedDict(
            #     [
            #         ("sender", tx["sender"]),
            #         ("recipient", tx["recipient"]),
            #         ("amount", tx["amount"]),
            #     ]
            # )
            Transaction(tx["sender"], tx["recipient"], tx["amount"])
            for tx in ot
        ]


def valid_proof(transactions, last_hash, proof):
    guess = (
        f"{[tx.to_ordered_dict() for tx in transactions]}{last_hash}{proof}".encode()
    )
    guess_hash = hash_string_256(guess)
    return guess_hash[:2] == "00"


def proof_of_work():
    last_block = get_last_blockchain_value()
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    tx_sender = [
        [tx.amount for tx in block.transactions if tx.sender == participant]
        for block in blockchain
    ]
    open_tx_sender = [tx.amount for tx in open_transactions if tx.sender == participant]
    tx_recipient = [
        [tx.amount for tx in block.transactions if tx.recipient == participant]
        for block in blockchain
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
    amount_sent += reduce(lambda accumulator, el: accumulator + el, open_tx_sender, 0)
    amount_received += reduce(
        lambda accumulator, el: accumulator + sum(el)
        if len(el) > 0
        else accumulator + 0,
        tx_recipient,
        0,
    )
    return amount_received - amount_sent


def get_last_blockchain_value():
    if len(blockchain) > 0:
        return blockchain[-1]
    return None


def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount


def add_transaction(recipient, sender=owner, amount=1.0):
    # transaction = {
    #     "sender": sender,
    #     "recipient": recipient,
    #     "amount": amount,
    # }
    # transaction = OrderedDict(
    #     [
    #         ("sender", sender),
    #         ("recipient", recipient),
    #         ("amount", amount),
    #     ]
    # )
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block():
    hashed_block = hash_block(get_last_blockchain_value())
    # print(hashed_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     "sender": "MINING",
    #     "recipient": owner,
    #     "amount": MINING_REWARD,
    # }
    # reward_transaction = OrderedDict(
    #     [
    #         ("sender", "MINING"),
    #         ("recipient", owner),
    #         ("amount", MINING_REWARD),
    #     ]
    # )
    reward_transaction = Transaction("MINING", owner, MINING_REWARD)
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    # we use sort_keys when dumping blocks to json but
    # what the hey, lets use orderddict here as well
    # block = {
    #     "previous_hash": hashed_block,
    #     "index": len(blockchain),
    #     "transactions": copied_transactions,
    #     "proof": proof,
    # }
    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    # block = OrderedDict(
    #     [
    #         ("previous_hash", hashed_block),
    #         ("index", len(blockchain)),
    #         ("transactions", copied_transactions),
    #         ("proof", proof),
    #     ]
    # )
    blockchain.append(block)
    # save_data()
    return True


def get_transaction_value():
    tx_recipient = input("Enter the recipient of the transaction: ")
    tx_amount = float(input("Your transaction amount please: "))
    return (tx_recipient, tx_amount)


def get_user_choice():
    user_input = input("Your choice: ")
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print("Outputting Block")
        print(block)
    else:
        print("-" * 20)


def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            print("Previous hash is invalid.")
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print("Proof of work is invalid.")
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


def main():
    load_data()
    waiting_for_input = True

    while waiting_for_input:
        print("Please choose")
        print("1: Add a new transaction value")
        print("2: Mine a new block")
        print("3: Output the blockchain blocks")
        # print("4: Output participants")
        print("4: Check transaction validity")
        # print("h: Manipulate the chain")
        print("q: Quit")
        user_choice = get_user_choice()
        if user_choice == "1":
            tx_data = get_transaction_value()
            recipient, amount = tx_data
            if add_transaction(recipient, amount=amount):
                print("Added Transaction")
            else:
                print("Transaction failed!")
            global open_transactions
            print(open_transactions)
        elif user_choice == "2":
            if mine_block():
                open_transactions = []
        elif user_choice == "3":
            print_blockchain_elements()
        elif user_choice == "4":
            print(participants)
        elif user_choice == "5":
            if verify_transactions():
                print("All transactions are valid")
            else:
                print("There are invalid transactions")
        # elif user_choice == "h":
        #     if len(blockchain) >= 1:
        #         blockchain[0] = {
        #             "previous_hash": "",
        #             "index": 0,
        #             "transactions": [
        #                 {"sender": "Max", "recipient": "Manuel", "amount": 8.2}
        #             ],
        #         }
        elif user_choice == "q":
            waiting_for_input = False
        else:
            print("Input was invalid, please pick a value form the list!")
        if not verify_chain():
            print_blockchain_elements()
            print("Invalid blockchain!")
            break
        else:
            if user_choice == "1" or user_choice == "2":
                save_data()
        print(f"Balance of {'Max'}: {get_balance('Max'):6.2f}")
    else:
        print("User left!")


if __name__ == "__main__":
    main()
