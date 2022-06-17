import json
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)
Bootstrap(app)


@app.route("/", methods=["GET"])
def get_node_ui():
    return render_template("node.html")


@app.route("/network", methods=["GET"])
def get_network_ui():
    return render_template("network.html")


@app.route("/wallet", methods=["GET"])
def get_wallet():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
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


@app.route("/broadcast-transaction", methods=["POST"])
def broadcast_transaction():
    data = request.get_json()
    if not data:
        response = {"message": "No data found"}
        return jsonify(response=response), 400
    required = ["sender", "recipient", "amount", "signature"]
    if not all(key in data for key in required):
        response = {"message": "Malformed Transaction"}
        return jsonify(response=response), 400
    success = blockchain.add_transaction(
        data["signature"], data["recipient"], data["sender"], data["amount"], False
    )
    if success:
        response = {
            "message": "Successfully added transaction.",
            "transaction": {
                "sender": data["sender"],
                "recipient": data["recipient"],
                "amount": float(data["amount"]),
                "signature": data["signature"],
            },
        }
        return jsonify(response=response), 201
    else:
        response = {"message": "Creating a transaction failed."}
        return jsonify(response=response), 500


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
    success = blockchain.add_transaction(
        signature, data["recipient"], wallet.public_key, float(data["amount"])
    )
    if success:
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


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    serializable_transactions = [
        tx.to_ordered_dict() for tx in blockchain.open_transactions
    ]
    return jsonify(transactions=serializable_transactions), 200


@app.route("/broadcast-block", methods=["POST"])
def broadcast_block():
    data = request.get_json()
    if not data:
        response = {"message": "No data found"}
        return jsonify(response=response), 400
    required = ["block"]
    if not all(key in data for key in required):
        response = {"message": "Malformed Block"}
        return jsonify(response=response), 400
    block = data["block"]
    if block["index"] == blockchain.blockchain[-1].index + 1:
        if blockchain.add_block(block):
            response = {"message": "Block added successfully"}
            return jsonify(response=response), 201
        else:
            response = {"message": "Block not added. Invalid block."}
            return jsonify(response=response), 409
    elif block["index"] > blockchain.blockchain[-1].index:
        response = {"message": "Peer blockchain ahead of local. Block not added."}
        blockchain.resolve_conflicts = True
        return jsonify(response=response), 200
    else:
        response = {"message": "Peer blockchain behind local. Block not added."}
        return jsonify(response=response), 409


@app.route("/mine", methods=["POST"])
def mine():
    if blockchain.resolve_conflicts:
        response = {"message": "Resolve confilicts first, block not added!"}
        return jsonify(response=response), 400
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


@app.route("/resolve-conflicts", methods=["PATCH"])
def resolve_conflicts():
    blockchain_patched = blockchain.resolve()
    if blockchain_patched:
        response = {"message": "Local blockchain patched."}
    else:
        response = {"message": "Local blockchain OK."}
    return jsonify(response=response), 200


@app.route("/blockchain", methods=["GET"])
def get_blockchain():
    blockchain_snapshot = blockchain.blockchain
    serializable_blockchain_snapshot = [
        block.to_ordered_dict() for block in blockchain_snapshot
    ]
    return jsonify(blockchain=serializable_blockchain_snapshot), 200


@app.route("/node", methods=["POST"])
def add_node():
    data = request.get_json()
    if not data:
        response = {"message": "No data attached"}
        return jsonify(response=response), 400
    if "node" not in data:
        response = {"message": "No node data attached"}
        return jsonify(response=response), 400
    node_list = blockchain.peer_nodes
    node_list.add(data["node"])
    blockchain.peer_nodes = node_list
    response = {
        "message": "Node added successfully",
        "nodes": list(blockchain.peer_nodes),
    }
    return jsonify(response=response), 201


@app.route("/node/<string:node>", methods=["DELETE"])
def remove_node(node: str):
    node = node.strip()
    if not node or len(node) == 0 or node == None:
        response = {"message": "No node found."}
        return jsonify(response=response), 400
    node_list = blockchain.peer_nodes
    node_list.discard(node)
    blockchain.peer_nodes = node_list
    response = {
        "message": "Node removed successfully",
        "nodes": list(blockchain.peer_nodes),
    }
    return jsonify(response=response), 201


@app.route("/nodes", methods=["GET"])
def get_nodes():
    response = {"nodes": list(blockchain.peer_nodes)}
    return jsonify(response=response), 200


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    wallet.load_keys()
    blockchain = Blockchain(wallet.public_key, port)
    app.run(debug=True, port=port)
