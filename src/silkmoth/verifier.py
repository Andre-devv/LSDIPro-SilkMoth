from .inverted_index import InvertedIndex
import networkx as nx

def reduce_sets(reference_set: list, source_set: list) -> tuple:
    """
    Applies the triangle inequality reduction by removing every element from 
    both sets that has an identical match in the other set. 

    Args:
        reference_set: Tokenized reference set R
        source_set: Tokenized source set S

    Returns:
        (list, list, int):  Reduced reference set, reduced source set and number
                            of identical elements.
    """
    r_reduced = reference_set[:]
    s_reduced = source_set[:]
    count = 0
    for elem in reference_set:
        if elem in s_reduced:
            s_reduced.remove(elem)
            r_reduced.remove(elem)
            count += 1
    return (r_reduced, s_reduced, count)


class Verifier:
    """
    The verifier component executes the final verification step in the SilkMoth
    pipeline. During verification SilkMoth performs the maximum matching between
    every candidate set and the reference set R. The sets whose maximum matching
    score surpass the relatedness threshold δ are the verified related sets to R.

    For maximum matching computation we treat every element of the two sets as 
    vertices of a bipartite graph and the weights of each edge determined by the 
    similarity function. The maximum weighted matching is computed using the existing
    graph library [NetworkX](https://networkx.org/).

    Optionally, a triangle inequality-based reduction can be applied to further 
    improve performance.

    Examples
    --------
    ```
    >>> from silkmoth.inverted_index import InvertedIndex
    >>> from silkmoth.utils import similar, jaccard_similarity
    >>> from silkmoth.verifier import Verifier
    >>> S1 = [{"Apple", "Pear", "Car"}, {"Apple", "Sun", "Cat"}]
    >>> S2 = [{"Apple", "Berlin", "Sun"}, {"Apple"}]
    >>> S = [S1, S2]
    >>> I = InvertedIndex(S)
    >>> R = [{"Apple"}, {"Berlin", "Sun"}]
    >>> verifier = Verifier(0.1, similar, jaccard_similarity)
    >>> verifier.get_related_sets(R, {0, 1}, I)
    [(0, 0.17073170731707313), (1, 0.7142857142857142)]
    >>> verifier = Verifier(0.7, similar, jaccard_similarity)
    >>> verifier.get_related_sets(R, {0, 1}, I)
    [(1, 0.7142857142857142)]
    ```
    """

    def __init__(self, related_thresh, sim_metric, sim_func, sim_thresh=0, reduction=False):
        """
        Initialize the verifier with some parameters.

        Args:
            related_thresh (float): Relatedness threshold delta
            sim_metric (callable): Similarity metric similar(...)/contain(...)
            sim_func (callable): Similarity function phi
            sim_thresh (float): Similarity threshold alpha
            reduction (bool): Flag to activate/deactivate triangle inequality reduction
        """
        self.related_thresh = related_thresh
        self.sim_metric = sim_metric
        self.sim_func = sim_func
        self.sim_thresh = sim_thresh
        self.reduction = reduction

    def get_mm_score(self, reference_set, source_set) -> float:
        """
        Helper function that computes the maximum weighted bipartite matching score, where elements 
        correspond to nodes and the edges are weighted using the similarity 
        function.

        Args:
            reference_set (list): Tokenized reference set R
            source_set (list): Tokenized source set S
        
        Returns:
            float:  Maximum matching score (sum of weights of edges in the 
                    matching)
        """
        G = nx.Graph()
        for r_idx, r_elem in enumerate(reference_set):
            for s_idx, s_elem in enumerate(source_set):
                w = self.sim_func(r_elem, s_elem, self.sim_thresh)
                G.add_edge(r_idx, s_idx + len(reference_set), weight=w)
        
        matching = nx.max_weight_matching(G)
        return sum(G[u][v]['weight'] for u, v in matching)
    


    def get_relatedness(self, reference_set, source_set) -> float:
        """
        Helper function that gives the relatedness score by computing the maximum weighted
        bipartite matching.

        Args:
            reference_set (list): Tokenized reference set R
            source_set (list): Tokenized source set S

        Returns:
            float: Relatedness score of R and S
        """
        r_size = len(reference_set)
        s_size = len(source_set)
        exact_matches = 0
        if self.reduction:
            reference_set, source_set, exact_matches = reduce_sets(reference_set, source_set)

        mm_score = self.get_mm_score(reference_set, source_set) + exact_matches
        relatedness = self.sim_metric(r_size, s_size, mm_score)
        return relatedness


    def get_related_sets(self, reference_set: list, candidates: set, inverted_index: InvertedIndex) -> list:
        """
        Gives all candidate sets that are related to the reference set.

        Args:
            reference_set (list): Tokeinized reference set R
            candidates (set): Collection of indices of candidate sets
            inverted_index (InvertedIndex): Inverted index instance

        Returns:
            list: Pairs of indices of all related sets from the candidates and 
            their relatedness with the reference set.
        """
        related_sets = []
        for c in candidates:
            source_set = inverted_index.get_set(c)
            relatedness = self.get_relatedness(reference_set, source_set)
            if relatedness >= self.related_thresh:
                related_sets.append((c, relatedness))
        return related_sets
