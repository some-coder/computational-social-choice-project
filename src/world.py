import random

from agent_sybil import AgentSybil
from agent_honest import AgentHonest
from block import Block
from blockchain import Blockchain

class World():
    
    par: dict = {
        'num_epochs': 100,        # number of simulated epochs or blocks
        'num_agents': 1000,       # number of agents in simulation
        'frac_sybils': 0.1,       # fraction of agents that are Sybils
    }

    def __init__(self):
        self.agents: list = self.init_agents()
        self.blockchain: Blockchain = Blockchain()

    def init_agents(self) -> list:
        num_agents, frac_sybils = self.par['num_agents'], self.par['frac_sybils']
        agents_honest = [AgentHonest() for i in range(int(num_agents * (1-frac_sybils)))]
        agents_sybil = [AgentSybil() for i in range(int(num_agents * frac_sybils))]
        return agents_honest + agents_sybil

    # generate transaction history for a set number of epochs
    def run(self):
        for i in range(self.par['num_epochs']):

            block: Block = Block()              # each epoch creates a new block
            random.shuffle(self.agents)         # shuffle the agent list

            for agent in self.agents:
                if agent.donation_decision() == False: continue       # if agent chooses to want to donate
                
                partner = agent.find_donation_partner(self.agents)  # then it will try to find a partner to donate to
                amount = agent.determine_amount()                   # then it will determine an amount to donate
                agent.donate(partner, amount)                       # an amount is transferred to the partner unilaterally (without its agreement)
                
                transaction: Transaction = (agent, partner, amount) # bundle transaction
                block.add_transaction(transaction)                  # add transaction to block

            self.blockchain.add_block(block)                        # append block to blockchain

    def save(self):
        NotImplemented

    def plot(self):
        NotImplemented