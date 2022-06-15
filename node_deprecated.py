from blockchain import Blockchain
from uuid import uuid4
from utility.verification import Verification
from wallet import Wallet


class Node:
    def __init__(self):
        # self.node_id = str(uuid4())
        self.wallet = Wallet()
        self.wallet.load_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        tx_recipient = input("Enter the recipient of the transaction: ")
        tx_amount = float(input("Your transaction amount please: "))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        user_input = input("Your choice: ")
        return user_input

    def print_blockchain_elements(self):
        for block in self.blockchain.blockchain:
            print("Outputting Block")
            print(block)
        else:
            print("-" * 20)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print("Please choose")
            print("1: Add a new transaction value")
            print("2: Mine a new block")
            print("3: Output the blockchain blocks")
            print("4: Check transaction validity")
            print("5: Load wallet")
            print("q: Quit")
            print(
                f"Balance of {self.wallet.public_key[:10]}...: {self.blockchain.get_balance():6.2f}"
            )
            user_choice = self.get_user_choice()
            if user_choice == "1":
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                signature = self.wallet.sign_transaction(
                    recipient, self.wallet.public_key, amount
                )
                if self.blockchain.add_transaction(
                    signature, recipient, self.wallet.public_key, amount=amount
                ):
                    print("Added Transaction")
                else:
                    print("Transaction failed!")
                print(self.blockchain.open_transactions)
            elif user_choice == "2":
                if not self.blockchain.mine_block():
                    print("Mining error: Invalid blockchain/transactions.")
            elif user_choice == "3":
                self.print_blockchain_elements()
            elif user_choice == "4":
                if Verification.verify_transactions(
                    self.blockchain.open_transactions, self.blockchain.get_balance
                ):
                    print("All transactions are valid")
                else:
                    print("There are invalid transactions")
            elif user_choice == "5":
                self.wallet.load_keys()
                self.blockchain.node = self.wallet.public_key
            elif user_choice == "q":
                waiting_for_input = False
            else:
                print("Input was invalid, please pick a value form the list!")
            if not Verification.verify_chain(self.blockchain.blockchain):
                self.print_blockchain_elements()
                print("Invalid blockchain!")
                break
        else:
            print("User left!")


def main():
    Node().listen_for_input()


if __name__ == "__main__":
    main()
