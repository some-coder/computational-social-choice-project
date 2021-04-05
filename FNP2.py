from collections import Counter
import random


class Agent:
    def __init__(self, preference, honest, number_of_votes_cast):
        self.preference = preference    # can be A or B
        self.utility = None     # initial utility is None
        self.honest = honest    # can be True or False
        self.number_of_votes_cast = number_of_votes_cast
        self.record = []    # records all votes cast by this agent and their cost.


class Voting:
    def __init__(self, true_state, sybil_state, cost):   # assuming uniform cost
        self.majority_outcome = self.find_majority_outcome(true_state)      # returns string A or B
        self.unanimity_outcome = self.find_unanimity_outcome(true_state)    # returns tuple A or B according to unanimity rule
        self.sybil_majority_outcome = self.find_majority_outcome(sybil_state)  # returns string A or B
        self.sybil_unanimity_outcome = self.find_unanimity_outcome(sybil_state)  # returns tuple A or B according to unanimity rule

        self.FNP2_PA = self.find_FNP2_PA(sybil_state, cost)  # probability of selecting A
        self.FNP2_PB = 1 - self.FNP2_PA     # probability of selecting B
        self.FNP2_outcome = "A" if self.FNP2_PA > self.FNP2_PB else "B"     # returns string A or B, whichever has the highest probability
        # edge case where P(A) == P(B) missing?

    def find_majority_outcome(self, state):
        return "A" if state["A"] > state["B"] else "B"

    def find_unanimity_outcome(self, state):
        if state["B"] > state["A"] == 0:
            return ("B", "true unanimous preference for B")
        elif state["A"] > state["B"] == 0:
            return ("A", "true unanimous preference for A")
        else:
            return (random.choice(["A", "B"]), "Random choice")

    def find_FNP2_PA(self, state, cost):
        if state["B"] > state["A"] == 0:
            return 0
        elif state["A"] > state["B"] == 0:
            return 1
        elif state["B"] > state["A"] > 0 or state["B"] == state["A"] == 0:
            return 1 - min(1, (1/2)+cost*(state["B"] - state["A"]))
        else:
            return min(1, (1 / 2) + cost * (state["A"] - state["B"]))

def get_list_of_agents(num_agents):
    '''
    insert specification on sybil behaviour here
    :return: a list containing all honest and sybil agents
    '''
    list_of_agents = []
    for x in range(0, num_agents):  # creating the agents
        # initialize preference randomly
        preference = random.choice(["A", "B"])

        # initialize honesty randomly
        honest = random.choice([True, False])

        number_of_votes_cast = 1
        if not honest:
            number_of_votes_cast = random.randint(1, 5)

        list_of_agents.append(Agent(preference, honest, number_of_votes_cast))

    return list_of_agents

def find_state(list_of_agents):
    true_preference_list = []
    sybil_preference_list = []
    for agent in list_of_agents:
        true_preference_list.append(agent.preference)
        sybil_preference_list.extend([agent.preference] * agent.number_of_votes_cast)    # add as many votes for A as an agent casts
    true_state = Counter(true_preference_list)
    sybil_state = Counter(sybil_preference_list)
    return true_state, sybil_state


'''
parameters - cost, and number of agents
'''
cost = 0.15
num_agents = 5
replicate_con = True

# create some agents:
agents = get_list_of_agents(num_agents)
# find the state (number of votes for each alternative A or B)
true_state, sybil_state = find_state(agents)

# replicate the Table of Connitzer
if replicate_con:
    print("FNP2, c = 0.15, replicating table\n")
    for voters_B in reversed(range(0, 6)):
        for voters_A in range(0, 6):
            state = Counter({'A': voters_A, 'B': voters_B})
            voting = Voting(dict(state), dict(state), cost)
            print(format(voting.FNP2_PA, '.2f'), end="\t")
        print("\n")
else:

    # voting takes as input the true state and the sybil state and calculates the outcome
    voting = Voting(dict(true_state), dict(sybil_state), cost)
    print("True Majority = {}\n"
          "Sybil Majority = {}\n"
          "True Unanimity = {}\n"
          "Sybil Unanimity = {}\n"
          "FNP2 = {} (probability A: {}, probability B: {})\n".format(voting.majority_outcome, voting.sybil_majority_outcome,
                                                                      voting.unanimity_outcome, voting.sybil_unanimity_outcome,
                                                                      voting.FNP2_outcome, voting.FNP2_PA, voting.FNP2_PB))