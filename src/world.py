
from agent_sybil import AgentSybil
from agent_honest import AgentHonest
from block import Block
from history import History

class World():
    
    self.params: dict = {
        'num_blocks': 100,        # number of simulated blocks
        'num_agents': 1000,       # number of agents in simulation
        'frac_sybils': 0.1,       # fraction of agents that are Sybils
    }

    def __init__(self):
        self.agents: list = init_agents()

        def init_agents() -> list[object]:
            num_agents, frac_sybils = self.params['num_agents'], self.params['frac_sybils']
            agents_honest = [AgentHonest() for i in range(num_agents * (1-frac_sybils))]
            agents_sybil = [AgentSybil() for i in range(num_agents * frac_sybils)]

    
    def run(self):
        NotImplemented

    def save(self):
        NotImplemented

    def plot(self):
        NotImplemented