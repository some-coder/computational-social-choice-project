from block import Block

class Blockchain:
    '''The blockchain constains the history of transactions as a series of Blocks.'''

    def  __init__(self):
        self.blocks: list = []

    # return the number of blocks on the blockchain
    def get_num_blocks(self):
        return len(self.blocks)

    # return the number of transations on the blockchain by summing over blocks
    def get_num_transaction(self):
        return sum([block.get_num_transactions() for block in self.blocks])

    # add a block to the blockchain after each epoch
    def add_block(self, block: Block):
        self.blocks.append(block)
    
    def __str__(self):
        return str([str(block) for block in self.blocks])
