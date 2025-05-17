
class CandidateSelector:

    def __init__(self):
        pass

    def get_candidates(self, signature, inverted_index):
        """
        Retrieve candidate set indices using token signature lookup.

        Args:
            signature (set): Signature tokens for a reference set.
            inverted_index (InvertedIndex): Instance of the custom InvertedIndex class.

        Returns:
            set: Indices of candidate sets containing at least one signature token.
        """
        candidates = set()

        for token in signature:
            try:
                idx_list = inverted_index.get_indexes(token)
                for set_idx, _ in idx_list:
                    candidates.add(set_idx)
            except ValueError:
                # token not found in inverted index; safely ignore
                continue

        return candidates