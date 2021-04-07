from typing import NewType
from agent import Agent

Transaction = NewType('Transaction', (Agent(), Agent(), float))    # source, destination, amount

class Block:
    """
    Each epoch is associated with one block.
    Each block stores the transactions between between users.
    """

    def __init__(self):
        self.transactions = []              # each block is initialized as empty list

    def get_num_transactions(self):
        return len(self.transactions)

    # append a single transaction to the block
    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)