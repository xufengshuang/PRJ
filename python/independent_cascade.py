import copy
import random
from typing import List,Tuple,Set
from python.graph import Graph

# The below reference is a python implementation of the IC model. It is reused for the implementation of this class.
# Hung-Hsuan Chen (19 nov 2016) independent_cascade.py source code [Source code]. https://github.com/hhchen1105/networkx_addon/blob/master/information_propagation/independent_cascade.py


class IndependentCascadeModel:
    """Independent Cascade model class

       Parameters
       ----------
       g : Graph
           graph on which IC is performed.

       seeds : List[str]
            list of seed nodes.

       act_prob : float
            probability of a node being influenced.
    """
    def __init__(self, g, seeds, act_prob):
        self.all_influenced_nodes = [[]]
        self.total_number_of_nodes = 0
        self.all_influenced_nodes, self.total_number_of_nodes = self.cascade(g, seeds, act_prob)

    def get_influenced_nodes(self) -> List[List[str]]:
        """Returns a list of all the influenced nodes after carrying out the diffusion process.

        Returns
        -------
        List[List[str]]
            list of influenced nodes.
        """
        return self.all_influenced_nodes

    def get_total_number_of_influenced_nodes(self) -> int:
        """Returns the total number of influenced nodes after carrying out the diffusion process.

        Returns
        -------
        int
            number of influenced nodes.
        """
        return self.total_number_of_nodes

    @staticmethod
    def prop_success(act_prob: float) -> bool:
        """Generates a random number and returns whether it is below `act_prob`.

        Parameters
        ----------
        act_prob : float
            probability of a node being influenced.

        Returns
        -------
        bool
            whether the generated random number is below `act_prob`.
        """
        # Rounds the number to 1 number after the decimal point.
        random_number = round(random.random(), 1)
        return random_number <= act_prob

    def diffuse_one_round(self, g: Graph, seed_nodes: List[str], tried_edges: Set[Tuple[str, str]], act_prob: float) -> Tuple[List[str],List[str],Set[Tuple[str,str]]]:
        """ Executes the diffusion process for one round.

        Parameters
        ----------
        g :  Graph
             graph on which IC is performed.

        seed_nodes : List[str]
            list of seed nodes.

        tried_edges : List[str]
            list of edges that have been visited so far.

        act_prob : float
             activation probability.

        Returns
        -------
        Tuple[List[str],List[str],Set[Tuple[str,str]]]
            the list of the new seed nodes, the list of the nodes that got influenced at the given round and the list of edges that got visited at the given round .
        """
        activated_nodes_of_this_round = set()
        tried_edges_of_this_round = set()
        for s in seed_nodes:
            nbs = g.successors(s)
            for nb in nbs:
                # Skips if one of the following happens:
                # nb is a seed node
                # the edge between s and nb has already been tried/explored before.
                if nb in seed_nodes or (s, nb) in tried_edges or (s, nb) in tried_edges_of_this_round:
                    continue
                if self.prop_success(act_prob):
                    activated_nodes_of_this_round.add(nb)
                tried_edges_of_this_round.add((s, nb))
        activated_nodes_of_this_round = list(activated_nodes_of_this_round)
        seed_nodes.extend(activated_nodes_of_this_round)
        return seed_nodes, activated_nodes_of_this_round, tried_edges_of_this_round

    def diffuse_all(self, g: Graph, seed_nodes: List[str], act_prob: float) -> Tuple[List[List[str]], int]:
        """ Executes the diffusion process until no more nodes can be influenced.

        Parameters
        ----------
        g :  Graph
            graph on which IC is performed.

        seed_nodes : List[str]
            list of seed nodes.

        act_prob : float
            activation probability.

        Returns
        -------
        Tuple[List[List[str]], int]
            list of lists of influenced nodes as well as the total number of influenced nodes.
        """
        tried_edges = set()
        # Each sublist at index i stores the nodes influenced at round i.
        # So initially, at round 0, the seed nodes are the only influenced nodes.
        layer_i_nodes = [[i for i in seed_nodes]]
        total_influenced_nodes = len(layer_i_nodes[0])
        while True:
            len_old = len(seed_nodes)
            (seed_nodes, activated_nodes_of_this_round, tried_edges_of_this_round) = \
                self.diffuse_one_round(g, seed_nodes, tried_edges, act_prob)
            layer_i_nodes.append(activated_nodes_of_this_round)
            total_influenced_nodes += len(activated_nodes_of_this_round)
            tried_edges = tried_edges.union(tried_edges_of_this_round)
            # If no more nodes have been influenced at the round that has just happened, the process halts.
            if len(seed_nodes) == len_old:
                break
        return layer_i_nodes,total_influenced_nodes

    def cascade(self, g, seeds, act_prob):
        """ Executes the IC diffusion process.

        Parameters
        ----------
        g :  Graph
            graph on which IC is performed.

        seeds : List[str]
            list of seed nodes.

        act_prob : float
            activation probability
        Returns
        -------
        Tuple[List[List[str]], int]
            list of lists of influenced nodes as well as the total number of influenced nodes.
        """
        for s in seeds:
            if s not in g.get_vertices():
                raise Exception("seed", s, "is not in graph")

        if act_prob > 1:
          raise Exception("edge activation probability cannot be larger than 1")

        # perform diffusion
        seed_nodes = copy.deepcopy(seeds)  # prevent side effect
        return self.diffuse_all(g, seed_nodes, act_prob)
