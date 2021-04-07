import random

class Agent:

    # agent parameters applyign to all agents
    par = {
        'init_balance': 100,                # initial balance
        'init_balance_deviation': 10,       # deviation around initial balance
        'donate_prob': 0.01,                # normalized probability of an agent to trade per epoch
        'min_don_amount': 1,                # the minimum amount for a donation
        'max_frac_donated': 0.2,            # maximum fraction of current balance donated
    }

    # initialize an instance of an agent
    def __init__(self):
        rnd_dev = self.par['init_balance_deviation']                                          
        self.balance: float = self.par['init_balance'] + random.uniform(-rnd_dev, rnd_dev)    # initialize balance
    
    # evaluate the probability that an agent engages in a donation
    # True means trade, False means don't trade
    # donations are decided unilaterally, agents don't accept or reject a request to trade
    def donation_decision(self) -> bool:
        chance = random.uniform(0, 1) <= self.par['donate_prob']    # wether an agent donates is partially chance
        min_balance = self.balance >= self.par['min_don_amount']    # agent has enough balance to make minimum donation
        return True if min_balance and chance else False

    # find a partner to donate to
    def find_donation_partner(self, agents) -> object:
        agents = agents.copy()
        agents.remove(self)             # agent removes itself from list of agents
        return random.sample(agents, 1)[0]    # sample from the remaining list
    
    # determine amount to be donated
    def determine_amount(self) -> float:
        min_don = self.par['min_don_amount']                                        # minimum amount donated
        max_don = min(self.balance, self.balance * self.par['max_frac_donated'])    # maximum amount donated
        return random.uniform(min_don, max_don)
        
    # agent donates to another agent
    def donate(self, donation_recipient, amount):
        self.balance -= amount
        donation_recipient.balance += amount


    
    
