from silkmoth.inverted_index import InvertedIndex
import networkx as nx

class Verifier:

    def __init__(self, related_thresh, sim_metric, sim_func, sim_thresh=0, reduction=False):
        """
        Initialize the verifier with some parameters.

        Args:
            related_thresh: Relatedness threshold delta
            sim_metric (callable): Similarity metric similar(...)/contain(...)
            sim_func (callable): Similarity function phi
            sim_thresh: Similarity threshold alpha
            reduction (bool): Flag to activate/deactivate triangle inequality reduction
        """
        self.related_thresh = related_thresh
        self.sim_metric = sim_metric
        self.sim_func = sim_func
        self.sim_thresh = sim_thresh
        self.reduction = reduction

    def _verify(self, reference_set, source_set) -> bool:
        """
        Checks if two sets are related or not by computing the maximum weighted
        bipartite matching.

        Args:
            reference_set: Tokenized reference set R
            source_set: Tokenized source set S

        Returns:
            bool: True if relatedness threshold is reached, False otherwise
        """
        r_size = len(reference_set)
        s_size = len(source_set)
        G = nx.Graph()
        for r_idx, r_elem in enumerate(reference_set):
            for s_idx, s_elem in enumerate(source_set):
                w = self.sim_func(r_elem, s_elem, self.sim_thresh)
                G.add_edge(r_idx, s_idx + r_size, weight=w)
        
        matching = nx.max_weight_matching(G)

        mm_score = sum(G[u][v]['weight'] for u, v in matching)
        relatedness = self.sim_metric(r_size, s_size, mm_score)
        return relatedness >= self.related_thresh


    def get_related_sets(self, reference_set: list, candidates: set, inverted_index: InvertedIndex) -> list:
        """
        Gives all candidate sets that are related to the reference set.

        Args:
            reference_set (list): Tokeinized reference set R
            candidates (set): Collection of indices of candidate sets
            inverted_index (InvertedIndex): Inverted index instance

        Returns:
            set: Indices of all related sets from the candidates
        """
        related_sets = set()
        for c in candidates:
            source_set = inverted_index.get_set(c)
            if self._verify(reference_set, source_set):
                related_sets.add(c)
        return related_sets
