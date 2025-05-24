import heapq
from collections import defaultdict
import warnings

class SignatureGenerator:

    def get_signature(self, reference_set, inverted_index, delta):
        """
        Compute the weighted signature for a reference set.

        Args:
            reference_set: Tokenized reference set.
            inverted_index (InvertedIndex): Index to evaluate token cost.
            delta (float): Relatedness threshold factor.

        Returns:
            list: A list of str for selected tokens forming the signature.
        """
        return self._generate_weighted_signature(reference_set, inverted_index, delta)

    def _generate_weighted_signature(self, reference_set, inverted_index, delta):
        if delta <= 0.0:
            return []

        n = len(reference_set)
        theta = delta * n  # required covered fraction ,  delta * |R| in paper

        # 1) Build token: elements map and aggregate token values
        token_to_elems = defaultdict(list)
        token_value = {}

        for i, elem in enumerate(reference_set): 
            if not elem:
                warnings.warn(f"Element at index {i} is empty and will be skipped.")
                continue
            unique_tokens = set(elem) # remove duplicate tokens inside each element
            weight = 1.0 / len(unique_tokens)

            for t in unique_tokens: 
                token_to_elems[t].append(i) 
                token_value[t] = token_value.get(t, 0.0) + weight # value = sum of weights (for each token)

        # 2) Build min-heap of (cost/value, token)
        heap = []
        for t, val in token_value.items():
            if val <= 0:
                continue
            try:
                cost = len(inverted_index.get_indexes(t)) # look up each token in inverted index to count in how many sets it is = cost
            except ValueError:
                # Token not in index: assign infinite cost to deprioritize
                cost = float('inf')
            heapq.heappush(heap, (cost / val, t)) # goal small ratio: cost/value

        # 3) Selection with greedy algorithm
        selected_sig = set()
        r_sizes = [len(set(elem)) if elem else 0 for elem in reference_set]
        total_loss = float(n)
        current_k_counts = [0] * n

        # while heap and total_loss >= theta:
        while heap and total_loss >= theta:
            # 1.
            ratio, t = heapq.heappop(heap)  # pull best token with lowest cost/value from heap
            if t in selected_sig:
                continue
            if ratio == float('inf'):
                break

            # 2.
            selected_sig.add(t)

            # 3.
            for i in range(n):
                if r_sizes[i] == 0:
                    continue

                # Calculate |k_i|: number of tokens from reference_set[i] also in selected_sig
                current_k_counts[i] = len(set(reference_set[i]).intersection(selected_sig))

            # 4.
            total_loss = sum(
                (r_sizes[i] - current_k_counts[i]) / r_sizes[i]
                for i in range(n) if r_sizes[i] > 0
            )

        return list(selected_sig)
