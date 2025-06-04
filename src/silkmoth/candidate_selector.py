from .utils import *

class CandidateSelector:

    def __init__(self, similarity_func, sim_metric, related_thresh):
        """
        Args:
            similarity_func (callable): Similarity function phi(r, s) (e.g., Jaccard).
            sim_metric (callable): Similarity metric related(R, S) (e.g., contain).
            related_thresh (float): Relatedness threshold delta.
        """
        self.similarity = similarity_func
        self.sim_metric = sim_metric
        self.delta = related_thresh

    def get_candidates(self, signature, inverted_index, ref_size):
        """
        Retrieve candidate set indices using token signature lookup.

        Args:
            signature (set): Signature tokens for a reference set.
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
            bool: True if both sets could be related based on their size, False
            otherwise.
        """
        # case 1: Set-Containment
        if self.sim_metric == contain and ref_size > src_size:
            return False
        # case 2: Set-Similarity
        if self.sim_metric == similar:
            if min(ref_size, src_size) < self.delta * max(ref_size, src_size):
                return False
        return True   

    def check_filter(self, R, K, candidates, inverted_index):
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
        k_i_sets = [set(r_i).intersection(K) for r_i in R]

        for c_idx in candidates:
            S = inverted_index.get_set(c_idx)
            matched = dict()

            for r_idx, (r_i, k_i) in enumerate(zip(R, k_i_sets)):
                if not r_i or not k_i:
                    continue

                threshold = (len(r_i) - len(k_i)) / len(r_i)
                r_set = set(r_i)
                max_sim = 0.0

                for token in k_i:
                    try:
                        entries = inverted_index.get_indexes_binary(token,c_idx)
                        for s_idx, e_idx in entries:
                            if s_idx != c_idx:
                                continue
                            s = S[e_idx]
                            sim = self.similarity(r_set, set(s))                                    
                            if sim >= threshold:
                                max_sim = max(max_sim, sim)  

                    except ValueError:
                        continue

                if max_sim >= threshold:
                    matched[r_idx] = max_sim

            if matched:
                filtered.add(c_idx)
                match_map[c_idx] = matched

        return filtered, match_map

    def _nn_search(self, r_set, S, c_idx, inverted_index):
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
                    sim = self.similarity(r_set, set(s))
                    max_sim = max(max_sim, sim)
            except ValueError:
                continue
        return max_sim


    def nn_filter(self, R, K, candidates, inverted_index, threshold, match_map):
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
        k_i_sets = [set(r_i).intersection(K) for r_i in R]
        final_filtered = set()

        total_init = 0
        for r_idx, r_i in enumerate(R):
                if not r_i:
                    continue
                base_loss = (len(r_i) - len(k_i_sets[r_idx])) / len(r_i)
                total_init += base_loss

        for c_idx in candidates:
            S = inverted_index.get_set(c_idx)
            matched = match_map.get(c_idx, {})
            # Step 1: initialize total estimate
            total = total_init

            # Step 2: for matched rᵢ, computational reuse of sim and adjust total
            for r_idx, sim in matched.items():
                r_i = R[r_idx]
                if not r_i:
                    continue
                k_i = k_i_sets[r_idx]
                base_loss = (len(r_i) - len(k_i)) / len(r_i)
                total += sim - base_loss

            # Step 3: for non-matched rᵢ, compute NN and adjust total
            for r_idx in set(range(n)) - matched.keys():
                r_i = R[r_idx]
                if not r_i:
                    continue
                k_i = k_i_sets[r_idx]
                base_loss = (len(r_i) - len(k_i)) / len(r_i)

                r_set = set(r_i)
                nn_sim = self._nn_search(r_set, S, c_idx, inverted_index)
                total += nn_sim - base_loss
                if total < theta:
                    break

            if total >= theta:
                final_filtered.add(c_idx)

        return final_filtered


