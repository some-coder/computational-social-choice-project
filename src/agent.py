import random

class Agent:

    # agent parameters applyign to all agents
    self.par = {
        'init_balance': 100,                # initial balance
        'init_balance_deviation': 10,       # deviation around initial balance
        'trade_prob': 0.01                  # normalized probability of an agent to trade per epoch
    }

    # initialize an instance of an agent
    def __init__(self):
        rnd_dev = self.par['init_balance_deviation']                                          
        self.balance: float = self.par['init_balance'] + random.uniform(-rnd_dev, rnd_dev)    # initialize balance
    
    # evaluate the probability that an agent engages in a trade
    # True means trade, False means don't trade
    # trades are decided unilaterally, agents don't accept or reject a request to trade
    def trade_decision(self) -> bool:
        return True if random.uniform(0, 1) <= self.par['trade_prob'] else False

    # agent does a transaction with another agent with some probability
    def trade(self, other_agent):
        if self.trade_decision() == False: return
    
    
