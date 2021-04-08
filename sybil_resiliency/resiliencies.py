import numpy as np
import os
import pandas as pd
import time
from collections import Counter


from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class ConsensusProtocol(Enum):
	"""
	Stores symbols for referring to consensus protocols in cryptocurrencies and beyond.
	"""
	PROOF_OF_WORK = 'pow'
	PROOF_OF_STAKE = 'pos'
	PROOF_OF_ACTIVITY = 'poa'
	ALGORAND_PROOF = 'algorand'
	OUROBOROS = 'ouroboros'
	AVALANCHE = 'avalanche'
	FNP2 = 'fnp2'
	CONITZER_TWO_ALT = 'con_two'
	CONITZER_MANY_ALT = 'con_many'
	MAJORITY = 'majority'


class Network:
	"""
	An abstract model of a peer-to-peer cryptocurrency network containing honest users as well as sybils.
	"""

	SYBILS_PER_ADVERSARY_MIN_MAX: Tuple[int, int] = (10, 20)  # both ends inclusive
	COMPUTING_POWER_ALPHA: float = float(np.log(5) / np.log(4))  # to get close to the 80-20 rule
	ASSET_SIZE_ALPHA: float = float(np.log(5) / np.log(4))
	COST: float = float(0.01)  # Conitzer 0.15 cost

	class TwoAlternativeElection:

		ALTERNATIVES: Tuple[str, str] = ('a', 'b')

		def __init__(self, num_honest: int, num_adversary: int, n: int, rng: np.random.Generator) -> None:
			if num_adversary > 1:
				raise ValueError(
					'A two-alternative election requires at most one adversary (got %d).' %
					(num_adversary,))
			self._num_honest = num_honest
			self._num_adversary = num_adversary
			self._n = n
			self._rng = rng
			self.number_votes_a: int
			self.number_votes_b: int
			self.honest_majority_choice: str
			self.sybil_choice: str
			self._initialise_election()

		def _initialise_election(self) -> None:
			choices: np.ndarray = self._rng.choice(
				a=Network.TwoAlternativeElection.ALTERNATIVES, size=self._num_honest,
				replace=True)
			ctr = Counter(choices)
			if len(ctr) > 0:
				self.honest_majority_choice = max(ctr)
			else:
				# Just pick a when there are no honest nodes
				self.honest_majority_choice = 'a'

			num_sybils = self._n - self._num_honest
			self.sybil_choice: str = self._rng.choice(a=Network.TwoAlternativeElection.ALTERNATIVES)
			if self.sybil_choice == Network.TwoAlternativeElection.ALTERNATIVES[0]:
				self.number_votes_a = num_sybils + ctr[Network.TwoAlternativeElection.ALTERNATIVES[0]]
				self.number_votes_b = ctr[Network.TwoAlternativeElection.ALTERNATIVES[1]]
			else:  # preference of sybils for B
				self.number_votes_a = ctr[Network.TwoAlternativeElection.ALTERNATIVES[0]]
				self.number_votes_b = num_sybils + ctr[Network.TwoAlternativeElection.ALTERNATIVES[1]]

	def __init__(
			self,
			num_total: int,
			num_adversary: int,
			sybils_per_adversary: Optional[Tuple[int]] = None,
			rng: Optional[np.random.Generator] = None) -> None:
		"""
		Constructs a network.

		:param num_honest: The number of honest users.
		:param num_adversary: The number of adversaries. These are single users that possess one or more sybils.
		:param sybils_per_adversary: Optional. A listing of the number of sybils each adversary possesses.
		:param rng: Optional. A random number generator to generate the network with.
		"""
		self._num_total = num_total
		self._num_adversaries = num_adversary
		self._rng = rng if rng is not None else np.random.default_rng()
		if sybils_per_adversary is None:
			self._sybils_per_adversary: List[int] = list(self._rng.integers(
				low=Network.SYBILS_PER_ADVERSARY_MIN_MAX[0],
				high=Network.SYBILS_PER_ADVERSARY_MIN_MAX[1] + 1,
				size=self._num_adversaries))
		else:
			self._sybils_per_adversary = sybils_per_adversary

		self._num_honest = self._num_total - int(np.sum(self._sybils_per_adversary))	
		self.n: int = self._num_honest + int(np.sum(self._sybils_per_adversary))
		print("n = %d, honest = %d, sybil = %d" % (self.n, self._num_honest, int(np.sum(self._sybils_per_adversary))))
		self.computing_powers = self._user_computing_powers()
		self.asset_sizes = self._user_asset_sizes()

	def _distributed_across_sybils(
				self,
				adversary_index: int,
				distribution_fn: Callable,
				params: Dict[str, Any]) -> List[float]:
		"""
		Yields some asset of an adversary, spread out uniformly over their sybils.

		:param adversary_index: The index characterising the adversary.
		:param distribution_fn: The distribution function with which to generate the total amount of the asset.
		:param params: The parameters to supply to the distribution function.
		:return: A list containing, per sybil, their respective share of the asset.
		"""
		num_sybils: int = self._sybils_per_adversary[adversary_index]
		power: float = distribution_fn(**params)
		return num_sybils * [power / num_sybils]

	def _user_computing_powers(self) -> List[float]:
		"""
		Gives a list of the computing power each identity has.

		:return: The list.
		"""
		out: List[float] = [self._rng.pareto(a=Network.COMPUTING_POWER_ALPHA) for _ in range(self._num_honest)]
		for adversary_index in range(self._num_adversaries):
			# each adversary must spread out their total computing power over their sybils
			out += \
				self._distributed_across_sybils(adversary_index, self._rng.pareto, {'a': Network.COMPUTING_POWER_ALPHA})
		return out

	def _user_asset_sizes(self) -> List[float]:
		"""
		Gives a list which, for each identity, states the size of their cryptocurrency wallet.

		:return: The list.
		"""
		out: List[float] = [self._rng.pareto(a=Network.ASSET_SIZE_ALPHA) for _ in range(self._num_honest)]
		for adversary_index in range(self._num_adversaries):
			out += self._distributed_across_sybils(adversary_index, self._rng.pareto, {'a': Network.ASSET_SIZE_ALPHA})
		return out

	def is_sybil(self, identity_index: int) -> bool:
		"""
		Determines whether the identity associated with the supplied index is a sybil.

		:param identity_index: The index associated with the identity.
		:return: The question's answer.
		"""
		return identity_index >= self._num_honest

	def sybils_belong_to_same_user(self, identity_indices: List[int]) -> bool:
		"""
		Determines whether the identities associated with the supplied indices are sybils from one single adversary.

		This method also checks whether any of the supplied indices is not a sybil in the first place. If such a
		situation occurs, this method automatically returns with ``False``.

		:param identity_indices: The indices for the identities.
		:return: The question's answer.
		"""
		start_index: int = self._num_honest
		end_index: int  # itself exclusive
		for adv_num_syb in self._sybils_per_adversary:
			end_index = start_index + adv_num_syb
			all_correct: bool = True
			for ide in identity_indices:
				if ide < start_index or ide >= end_index:
					# identity is an honest user or a sybil from a different user
					all_correct = False
					break
			if all_correct:
				return True
			start_index += adv_num_syb  # Not correct? Continue to next set of sybils.
		return False

	def network_reached_unanimous_two_alternative_decision(self) -> bool:
		"""
		Determines whether the network voted unanimously for one alternative among two.

		Note that if a unanimous decision is reached, the sybils did not succeed in overthrowing the 'sybil-free'
		social choice, as this is what the honest users wanted as well.

		:return: The question's answer.
		"""
		choices: np.ndarray = self._rng.choice(a=[0, 1], size=self.n, replace=True)
		return choices.sum() in (0, self.n)  # everyone voted either False or True

	def sybils_win_fnp2(self) -> bool:
		"""
		Determines whether in FNP-2 the sybils won the consensus round.

		:return: The question's answer.
		"""
		elc = Network.TwoAlternativeElection(self._num_honest, self._num_adversaries, self.n, self._rng)
		if elc.number_votes_a >= elc.number_votes_b:
			probability_picking_a: float = \
				1.0 if elc.number_votes_a > elc.number_votes_b == 0 else \
				min(1.0, (1.0 / 2.0) + Network.COST * (elc.number_votes_a - elc.number_votes_b))
			probability_picking_b = 1 - probability_picking_a
		else:
			probability_picking_b: float = \
				1.0 if elc.number_votes_b > elc.number_votes_a == 0 else \
				min(1.0, (1.0 / 2.0) + Network.COST * (elc.number_votes_b - elc.number_votes_a))
			probability_picking_a = 1 - probability_picking_b
		pick: str = self._rng.choice(
			a=Network.TwoAlternativeElection.ALTERNATIVES,
			p=(probability_picking_a, probability_picking_b))
		return pick == elc.sybil_choice and pick != elc.honest_majority_choice

	def sybils_win_majority(self) -> bool:
		"""
		Determines whether in the majority consensus rule, the sybils won the round.

		:return: The question's answer.
		"""
		elc = Network.TwoAlternativeElection(self._num_honest, self._num_adversaries, self.n, self._rng)
		pick: str = Network.TwoAlternativeElection.ALTERNATIVES[0] if elc.number_votes_a > elc.number_votes_b else \
			Network.TwoAlternativeElection.ALTERNATIVES[1]
		return pick == elc.sybil_choice and pick != elc.honest_majority_choice


def sybils_win_consensus_round(
		net: Network,
		prt: ConsensusProtocol,
		coalition_size: Optional[int] = None,
		rng: Optional[np.random.Generator] = None) -> bool:
	"""
	Determines whether sybils (from one adversary) win a round of consensus in the specified consensus protocol.

	``ConsensusProtocol.PROOF_OF_ACTIVITY`` and ``ConsensusProtocol.ALGORAND_PROOF`` require ``coalition_size`` to
	be specified.

	:param net: The network to simulate with.
	:param prt: The protocol to run the consensus mechanism with.
	:param coalition_size: Only required for coalition-dependent protocols. The coalition's number of identities.
	:param rng: A random number generator to draw randomness from.
	:return: The question's answer.
	"""
	rng = rng if rng is not None else np.random.default_rng()
	computer_power_prob: List[float] = list(np.array(net.computing_powers) / np.array(net.computing_powers).sum())
	asset_size_prob: List[float] = list(np.array(net.asset_sizes) / np.array(net.asset_sizes).sum())
	if coalition_size is None and type(prt) in (ConsensusProtocol.PROOF_OF_ACTIVITY, ConsensusProtocol.ALGORAND_PROOF):
		raise ValueError('Protocol \'%s\' requires a coalition size!' % (prt.value,))
	if prt is ConsensusProtocol.PROOF_OF_WORK:
		return net.is_sybil(rng.choice(a=list(range(net.n)), p=computer_power_prob))
	elif prt is ConsensusProtocol.PROOF_OF_STAKE:
		return net.is_sybil(rng.choice(a=list(range(net.n)), p=asset_size_prob))
	elif prt is ConsensusProtocol.PROOF_OF_ACTIVITY:
		identities: List[int] = \
			[ide for ide in rng.choice(a=list(range(net.n)), size=coalition_size, p=asset_size_prob)]
		return net.sybils_belong_to_same_user(identities)
	elif prt is ConsensusProtocol.ALGORAND_PROOF:
		# in Algorand, we have a soft voting round and a certifying voting round
		return \
			sybils_win_consensus_round(net, ConsensusProtocol.PROOF_OF_ACTIVITY, coalition_size, rng) and \
			sybils_win_consensus_round(net, ConsensusProtocol.PROOF_OF_ACTIVITY, coalition_size, rng)
	elif prt is ConsensusProtocol.OUROBOROS:
		# Committee members are block leaders
		# There is one block leader per block, in this sense we have simple PoS
		# But persistence is achieved by longest chain which depends on the committee composition
		return \
			sybils_win_consensus_round(net, ConsensusProtocol.PROOF_OF_STAKE, coalition_size, rng) and \
			sybils_win_consensus_round(net, ConsensusProtocol.PROOF_OF_ACTIVITY, coalition_size, rng)
	elif prt is ConsensusProtocol.AVALANCHE:
		# assuming a fully connected graph the protocol approximates committee voting
		# 	with a committee size of all nodes
		return sybils_win_consensus_round(net, ConsensusProtocol.PROOF_OF_ACTIVITY, net.n, rng)
	elif prt is ConsensusProtocol.CONITZER_TWO_ALT:
		if net.network_reached_unanimous_two_alternative_decision():
			return False
		else:
			return net.is_sybil(rng.choice(a=list(range(net.n))))
	elif prt is ConsensusProtocol.CONITZER_MANY_ALT:
		identities: Tuple[int, int] = tuple(rng.choice(a=list(range(net.n)), size=2))  # with replacement for now
		if net.sybils_belong_to_same_user(list(identities)):
			return True
		elif not net.is_sybil(identities[0]) and not net.is_sybil(identities[1]):
			return False
		else:
			return sybils_win_consensus_round(net, ConsensusProtocol.CONITZER_TWO_ALT, coalition_size, rng)
	elif prt is ConsensusProtocol.FNP2:
		return net.sybils_win_fnp2()
	elif prt is ConsensusProtocol.MAJORITY:
		return net.sybils_win_majority()
	raise NotImplementedError('Consensus protocol \'%s\' is not implemented (yet).' % (prt.value,))


class SybilResiliencyExperiment:
	"""
	A simulation which tests how consensus protocols in cryptocurrency networks are influenced by sybils.
	"""

	LOG_FREQUENCY: int = int(1e2)  # once every hundred iterations
	SAVE_DIR_NAME: str = 'results'
	SAVE_FILE_NAME: str = 'syb_res_exp'

	def __init__(
			self,
			num_total: int,
			num_adversary: int,
			sybils_per_adversary: int,
			num_episodes: int,
			num_iterations: int,
			protocols: Tuple[ConsensusProtocol, ...] = tuple(ConsensusProtocol),
			coalition_size: Optional[int] = None,
			rng: Optional[np.random.Generator] = None) -> None:
		"""
		Constructs a sybil resiliency experiment.

		:param num_honest: The number of honest users.
		:param num_adversary: The number of adversaries. Each adversary has one or more sybils at their disposal.
		:param num_episodes: The number of episodes in this experiment.
		:param num_iterations: The number of consensus rounds per episode.
		:param protocols: The consensus protocols to involve in the experiment. At least one must be selected.
		:param coalition_size: Only required for coalition-dependent protocols. The coalition's number of identities.
		:param rng: A random number generator to draw randomness from.
		"""
		self._num_total = num_total
		self._num_adversary = num_adversary
		self._sybils_per_adversary = [sybils_per_adversary,]
		self._num_episodes = num_episodes
		self._num_iterations = num_iterations
		self._protocols = protocols
		self._coalition_size = coalition_size
		self._rng = rng if rng is not None else np.random.default_rng()
		self.sybil_wins: np.ndarray = \
			np.zeros(shape=(len(self._protocols), num_episodes, num_iterations), dtype=int)
		self._run_episodes()

	def _run_episodes(self) -> None:
		"""
		Run the experiment's episodes.
		"""
		for epi in range(self._num_episodes):
			if (epi + 1) % SybilResiliencyExperiment.LOG_FREQUENCY == 0:
				print('\t%d / %d' % (epi + 1, self._num_episodes))
			net = Network(self._num_total, self._num_adversary, self._sybils_per_adversary, rng=self._rng)
			for prt_index, prt in enumerate(self._protocols):
				for itr in range(self._num_iterations):
					self.sybil_wins[prt_index, epi, itr] = \
						sybils_win_consensus_round(net, prt, self._coalition_size, self._rng)

	def save(self, dir_name: str = SAVE_DIR_NAME, file_name: str = SAVE_FILE_NAME) -> None:
		"""
		Saves the experiment results to the current directory.

		:param dir_name: The name of the directory to save the results into.
		:param file_name: The name of the file to save the results to. Exclude the '.csv' extension.
		"""
		try:
			os.mkdir(dir_name)
		except FileExistsError:
			pass  # that's okay
		averages: np.ndarray = self.sybil_wins.mean(axis=2)  # average over iterations
		df: pd.DataFrame = pd.DataFrame(data=averages.T, columns=[prt.value for prt in self._protocols])
		df.to_csv(path_or_buf=dir_name + '/' + file_name + '.csv', index=False)


if __name__ == '__main__':
	num_eps: int = int(1e3)
	num_its: int = int(5e1)
	all_protocols: Tuple[ConsensusProtocol, ...] = tuple(ConsensusProtocol)  # include 'em all
	col_siz: int = int(5e0)
	t_start: float = time.time()
	for n_total in (100,):
		for n_adversary in (1,):
			for n_sybils in range(1,101):
				print('EXPERIMENT (total: %d, adversary: %d, sybils: %d).' % (n_total, n_adversary, n_sybils))
				t_start_exp: float = time.time()
				sre = SybilResiliencyExperiment(n_total, n_adversary, n_sybils, num_eps, num_its, all_protocols, col_siz)
				sre.save('results', 'exp-%d-tot-%d-syb' % (n_total, n_sybils))
				print('\tDone. Took %.1lf sec.' % (time.time() - t_start_exp))
	print('ALL EXPERIMENTS DONE. TOOK %.0lf min' % ((time.time() - t_start) / 60.0,))
