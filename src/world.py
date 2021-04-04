import agent_sybil
import agent_honest
import block
import history

class World() -> class:
    
    self.params: dict = {
        num_blocks: int = 100,      # number of simulated blocks
        num_agents: int = 1000,     # number of agents in simulation
        frac_sybils: float = 0.1,   # fraction of agents that are Sybils
    }

    def __init__(self):
        self.agents: list = init_agents()

        def init_agents() -> list(class):
            agents_honest = [AgentHonest() for i in range(num_agents * (1-frac_sybils))]
            agents_sybil = [AgentsSybil() for i in range(num_agents * frac_sybils)]

    
    def run(self):
        NotImplemented

    def save(self):
        NotImplemented
    
    def plot(self):
        NotImplemented