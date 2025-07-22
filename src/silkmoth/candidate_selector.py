from .utils import contain, similar, edit_similarity, N_edit_similarity, jaccard_similarity, get_q_chunks, get_q_grams
from math import floor, ceil

class CandidateSelector:
    """
    The candidate selector executes the candidate selection step in the SilkMoth
    pipeline. After signature generation SilkMoth accesses the inverted index to 
    get all sets which contain a token in the signature to form an initial set 
    of candidates.

    The size of the candidate set can be reduced further by applying the check 
    or nearest neighbour filters in the refinement step of the SilkMoth pipeline.

    Examples
    --------
    ```
    >>> from silkmoth.candidate_selector import CandidateSelector
    >>> from silkmoth.utils import similar, jaccard_similarity
    >>> from silkmoth.inverted_index import InvertedIndex
    >>> S1 = [{"Apple", "Pear", "Car"}, {"Apple", "Sun", "Cat"}]
    >>> S2 = [{"Something", "Else"}]
    >>> S3 = [{"Apple", "Berlin", "Sun"}, {"Apple"}]
    >>> S = [S1, S2, S3]
    >>> signature = ["Apple", "Berlin"]
    >>> I = InvertedIndex(S)
    >>> cand_selector = CandidateSelector(jaccard_similarity, similar, 0.7)
    >>> cand_selector.get_candidates(signature, I, 2)
    {0, 2}
    ```
    """

    def __init__(self, similarity_func, sim_metric, related_thresh, sim_thresh=0.0, q = 3):
        """
        Initialize the candidate selector with some parameters.

        Args:
            similarity_func (callable): Similarity function phi(r, s) (e.g., Jaccard).
            sim_metric (callable): Similarity metric related(R, S) (e.g., contain).
            related_thresh (float): Relatedness threshold delta.
            sim_thresh (float): Similarity threshold alpha.
            q (int): q-chunk length for edit similarity.
        """
        self.similarity = similarity_func
        self.sim_metric = sim_metric
        self.delta = related_thresh
        self.alpha = sim_thresh
        self.q = q

    def get_candidates(self, signature, inverted_index, ref_size) -> set:
        """
        Retrieve candidate set indices using token signature lookup.

        Args:
            signature (list): Signature tokens for a reference set.
            inverted_index (InvertedIndex): Instance of the custom InvertedIndex class.
            ref_size (int): Size of set R.

        Returns:
            set: Indices of candidate sets containing at least one signature token.
        """
        candidates = set()

        for token in signature:
            try:
                idx_list = inverted_index.get_indexes(token)
                for set_idx, _ in idx_list:
                    src_size = len(inverted_index.get_set(set_idx))
                    if self.verify_size(ref_size, src_size):
                        candidates.add(set_idx)
            except ValueError:
                # token not found in inverted index; safely ignore
                continue

        return candidates
    
    def verify_size(self, ref_size, src_size) -> bool:
        """
        Checks if sets can be related based on their sizes. Set-Containment is 
        only defined for |R|<=|S|. For Set-Similarity we should compare only 
        similar size sets.

        Args:
            ref_size (int): Size of set R.
            src_size (int): Size of (possible) set S.
        
        Returns:
            bool: True if both sets could be related based on their size, False otherwise.
        """
        # case 1: Set-Containment
        if self.sim_metric == contain and ref_size > src_size:
            return False
        # case 2: Set-Similarity
        if self.sim_metric == similar:
            if min(ref_size, src_size) < self.delta * max(ref_size, src_size):
                return False
        return True   

    def check_filter(self, R, K, candidates, inverted_index) -> tuple:
        """
        Apply check filter to prune weak candidate sets.

        Args:
            R (list of list): Tokenized reference set.
            K (set): Flattened signature tokens.
            candidates (set): Candidate set indices from get_candidates().
            inverted_index (InvertedIndex): For retrieving sets.

        Returns:
            tuple:
                set: Candidate indices that pass the check filter.
                dict: c_idx -> dict{r_idx -> max_sim}.
        """
        filtered = set()
        match_map = dict()
        if self.similarity is jaccard_similarity:
            k_i_sets = [set(r_i).intersection(K) for r_i in R]
        elif self.similarity in (edit_similarity, N_edit_similarity):
            k_i_sets = [set(get_q_grams(r_i, self.q)).intersection(K) for r_i in R]
        else:
            raise ValueError("Unsupported similarity function.")

        for c_idx in candidates:
            matched = self.create_match_map(R, k_i_sets, c_idx, inverted_index)

            if matched:
                filtered.add(c_idx)
                match_map[c_idx] = matched

        return filtered, match_map

    def create_match_map(self, R, k_i_sets, c_idx, inverted_index) -> dict:
        """
        Create a match map for a specific candidate index.

        Args:
            R (list of list): Tokenized reference set.
            k_i_sets (list of sets): Unflattened signature.
            c_idx (int): Candidate set index.
            inverted_index (InvertedIndex): For retrieving sets.

        Returns:
            dict: r_idx -> max_sim for matched reference sets.
        """
        S = inverted_index.get_set(c_idx)
        matched = {}

        for r_idx, (r_i, k_i) in enumerate(zip(R, k_i_sets)):
            if not r_i or not k_i:
                continue

            if self.similarity in (edit_similarity, N_edit_similarity):
                r_i = get_q_grams(r_i, self.q)
                k_i = set(get_q_grams(k_i, self.q))
                denominator = len(r_i) + ceil(len(r_i) / self.q) - len(k_i)
                threshold = len(r_i) / denominator if denominator != 0 else 0.0
            else:
                denominator = len(r_i)
                threshold = (len(r_i) - len(k_i)) / denominator if denominator != 0 else 0.0

            r_set = set(r_i)
            max_sim = 0.0

            for token in k_i:
                try:
                    entries = inverted_index.get_indexes_binary(token, c_idx)
                    for s_idx, e_idx in entries:
                        if s_idx != c_idx:
                            continue
                        s = S[e_idx]
                        sim = self.similarity(r_set, set(s), self.alpha)
                        if sim >= threshold:
                            max_sim = max(max_sim, sim)
                except ValueError:
                    continue

            if max_sim >= threshold:
                matched[r_idx] = max_sim

        return matched

    def _nn_search(self, r_set, S, c_idx, inverted_index) -> float:
        """
        Find the maximum similarity between r and elements s ∈ S[C] that share at least one token with r using
        the inverted index for efficiency.

        Args:
            r_set (set): Reference element tokens.
            S (list of list): Elements of candidate set S[c_idx].
            c_idx (int): Index of candidate set in inverted index.
            inverted_index (InvertedIndex): For fetching token locations.

        Returns:
            float: Maximum similarity between r and any s ∈ S[c_idx].
        """
        # seen = set()
        max_sim = 0.0
        for token in r_set:
            try:
                entries = inverted_index.get_indexes_binary(token,c_idx)
                for s_idx, e_idx in entries:
                    if s_idx != c_idx:
                        continue
                    s = S[e_idx]
                    sim = self.similarity(r_set, set(s), self.alpha)
                    max_sim = max(max_sim, sim)
            except ValueError:
                continue
        return max_sim


    def nn_filter(self, R, K, candidates, inverted_index, threshold, match_map) -> set:
        """
        Nearest Neighbor Filter (Algorithm 2 from SilkMoth paper).

        Args:
            R (list of list): Tokenized reference set.
            K (set): Flattened signature tokens.
            candidates (set): Candidate indices from check filter.
            inverted_index (InvertedIndex): To retrieve sets and indexes.
            threshold (float): Relatedness threshold δ (between 0 and 1).
            match_map (dict): Maps candidate set index to matched rᵢ indices and their max sim (from check filter).

        Returns:
            set: Final filtered candidate indices that pass the NN filter.
        """
        n = len(R)
        theta = threshold * n

        if self.similarity is jaccard_similarity:
            k_i_sets = [set(r_i).intersection(K) for r_i in R]
            r_i_list = R
        elif self.similarity in (edit_similarity, N_edit_similarity):
            k_i_sets = [set(get_q_grams(r_i, self.q)).intersection(K) for r_i in R]
            r_i_list = [get_q_grams(r, self.q) for r in R]
        else:
            raise ValueError("Unsupported similarity function.")

        final_filtered = set()

        total_init = 0
        for r_idx, r_i in enumerate(R):
            if not r_i:
                continue
            k_i = k_i_sets[r_idx]
            base_loss = self.calc_base_loss(k_i, r_i)
            total_init += base_loss

        for c_idx in candidates:
            S = inverted_index.get_set(c_idx)
            if self.alpha > 0:
                S_tokens = set()
                for s in S:
                    S_tokens.update(s)

            # Check if match_map is provided, otherwise create it
            if match_map is None:
                matched = self.create_match_map(R, K, c_idx, inverted_index)
            else:
                matched = match_map.get(c_idx, {})

            # Step 1: initialize total estimate
            total = total_init

            # Step 2: for matched rᵢ, computational reuse of sim and adjust total
            if matched:
                for r_idx, sim in matched.items():
                    r_i = r_i_list[r_idx]
                    if not r_i:
                        continue
                    k_i = k_i_sets[r_idx]
                    base_loss = self.calc_base_loss(k_i, r_i)
                    total += sim - base_loss 

            # Step 3: for non-matched rᵢ, compute NN and adjust total
            for r_idx in set(range(n)) - matched.keys():
                r_i = r_i_list[r_idx]
                if not r_i:
                    continue
                k_i = k_i_sets[r_idx]
                base_loss = self.calc_base_loss(k_i, r_i)

                r_set = set(r_i)

                # Case alpha > 0
                if (self.alpha > 0 and len(k_i) >= floor((1 - self.alpha) * len(r_i)) + 1 
                    and k_i.isdisjoint(S_tokens)):
                    nn_sim = 0
                else:
                    nn_sim = self._nn_search(r_set, S, c_idx, inverted_index)
                
                total += nn_sim - base_loss
                if total < theta:
                    break

            if total >= theta:
                final_filtered.add(c_idx)

        return final_filtered

    def calc_base_loss(self, k_i, r_i):
        if self.similarity in (edit_similarity, N_edit_similarity):
            denominator = len(r_i) + ceil(len(r_i) / self.q) - len(k_i)
            B_i = len(r_i) / denominator if denominator != 0 else 0.0
            base_loss = 1.0 - B_i
        else:
            denominator = len(r_i)
            base_loss = (len(r_i) - len(k_i)) / denominator if denominator != 0 else 0.0
        return base_loss


