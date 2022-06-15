from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()
        try:
            with open("./wallet.txt", mode="w") as f:
                f.write(self.public_key)
                f.write("\n")
                f.write(self.private_key)
        except (IOError, IndexError):
            print("Saving wallet failed.")
            return False
        else:
            return True

    def load_keys(self):
        try:
            with open("./wallet.txt", mode="r") as f:
                file_content = f.readlines()
            self.public_key = file_content[0][:-1]
        except (FileNotFoundError, IndexError):
            if self.create_keys():
                return True
            return False
        else:
            self.private_key = file_content[1]
            return True

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (
            binascii.hexlify(private_key.exportKey(format="DER")).decode("ascii"),
            binascii.hexlify(public_key.exportKey(format="DER")).decode("ascii"),
        )

    def sign_transaction(self, recipient, sender, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        payload_hash = SHA256.new(f"{sender}{recipient}{amount}".encode("utf8"))
        signature = signer.sign(payload_hash)
        return binascii.hexlify(signature).decode("ascii")

    @staticmethod
    def verify_transaction(transaction):
        if transaction.sender == "MINING":
            return True
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        payload_hash = SHA256.new(
            f"{transaction.sender}{transaction.recipient}{transaction.amount}".encode(
                "utf8"
            )
        )
        return verifier.verify(payload_hash, binascii.unhexlify(transaction.signature))
