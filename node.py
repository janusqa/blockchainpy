from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)
Bootstrap(app)

wallet = Wallet()
wallet.load_keys()
blockchain = Blockchain(wallet.public_key)


@app.route("/", methods=["GET"])
def get_ui():
    return render_template("node.html")


@app.route("/wallet", methods=["GET"])
def get_wallet():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "balance": blockchain.get_balance(),
        }
        return jsonify(response=response), 201
    else:
        response = {"message": "Wallet creation failed."}
        return jsonify(response=response), 500


@app.route("/balance", methods=["GET"])
def get_balance():
    return jsonify({"balance": blockchain.get_balance()}), 200


@app.route("/transaction", methods=["POST"])
def add_transaction():
    data = request.get_json()
    if not data:
        response = {"message": "Invalid data recieved."}
        return jsonify(response=response), 400
    required_fields = ["recipient", "amount"]
    if not all(field in data for field in required_fields):
        response = {"message": "Some required fields are missing from request."}
        return jsonify(response=response), 400
    signature = wallet.sign_transaction(
        data["recipient"], wallet.public_key, float(data["amount"])
    )
    if blockchain.add_transaction(
        signature, data["recipient"], wallet.public_key, float(data["amount"])
    ):
        response = {
            "message": "Successfully added transaction.",
            "transaction": {
                "sender": wallet.public_key,
                "recipient": data["recipient"],
                "amount": float(data["amount"]),
                "signature": signature,
            },
            "balance": blockchain.get_balance(),
        }
        return jsonify(response=response), 201
    else:
        response = {"message": "Creating a transaction failed."}
        return jsonify(response=response), 500


@app.route("/mine", methods=["POST"])
def mine():
    block = blockchain.mine_block()
    if block is not None:
        response = {
            "message": "Block added successfully",
            "block": block.to_ordered_dict(),
            "balance": blockchain.get_balance(),
        }
        return jsonify(response=response), 201
    else:
        response = {
            "message": "Mining failed.",
            "wallet_enabled": wallet.public_key != None,
        }
        return jsonify(response=response), 500


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    serializable_transactions = [
        tx.to_ordered_dict() for tx in blockchain.open_transactions
    ]
    return jsonify(transactions=serializable_transactions), 200


@app.route("/blockchain", methods=["GET"])
def get_blockchain():
    blockchain_snapshot = blockchain.blockchain
    serializable_blockchain_snapshot = [
        block.to_ordered_dict() for block in blockchain_snapshot
    ]
    return jsonify(blockchain=serializable_blockchain_snapshot), 200


if __name__ == "__main__":
    app.run(debug=True)
