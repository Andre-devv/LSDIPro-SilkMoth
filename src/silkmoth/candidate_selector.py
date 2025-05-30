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
            R (list of list): Tokenized reference set (each r_i is a list of tokens).
            K (set): Flattened signature (selected tokens).
            candidates (set): Indices of candidate sets from get_candidates().
            inverted_index (InvertedIndex): To access token positions and sets.

        Returns:
            set: Filtered candidate indices that pass the check filter.
        """
        filtered = set()
        # retrieve k_i elements from the signature
        k_i_sets = [set(r_i).intersection(K) for r_i in R]

        for c_idx in candidates:
            S = inverted_index.get_set(c_idx)
            valid = False

            for r_i, k_i in zip(R, k_i_sets):
                if not r_i or not k_i:
                    continue

                threshold = (len(r_i) - len(k_i)) / len(r_i)

                for token in k_i:
                    try:
                        entries = inverted_index.get_indexes(token)
                        for s_idx, e_idx in entries:
                            if s_idx == c_idx:
                                s = S[e_idx]
                                sim = self.similarity(set(r_i), set(s))
                                if sim >= threshold:
                                    valid = True
                                    break

                        if valid:
                            break

                    except ValueError:
                        continue

                if valid:
                    break

            if valid:
                filtered.add(c_idx)

        return filtered
