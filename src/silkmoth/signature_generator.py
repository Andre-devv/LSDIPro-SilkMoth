import heapq
from collections import defaultdict
import warnings
from .utils import SigType
from math import floor
from .inverted_index import InvertedIndex

class SignatureGenerator:

    def get_signature(self, reference_set, inverted_index, delta, alpha=0, sig_type=SigType.WEIGHTED) -> list:
        """
        Compute a signature for a reference set given a signature type. Uses 
        weighted signature scheme by default.

        Args:
            reference_set (list): Tokenized reference set.
            inverted_index (InvertedIndex): Index to evaluate token cost.
            delta (float): Relatedness threshold factor.
            alpha (float): Similarity threshold factor.
            sig_type (SigType): Type of signature.

        Returns:
            list: A list of str for selected tokens forming the signature.
        """
        match sig_type:
            case SigType.WEIGHTED:
                return self._generate_weighted_signature(reference_set, inverted_index, delta)
            case SigType.SKYLINE:
                return self._generate_skyline_signature(reference_set, inverted_index, delta, alpha)
            case SigType.DICHOTOMY:
                return self._generate_dichotomy_signature(reference_set, inverted_index, delta, alpha)
            case _:
                raise ValueError(f"Unknown signature type") 
            
    
    def _generate_skyline_signature(self, reference_set, inverted_index: InvertedIndex, delta, alpha):
        weighted = set(self._generate_weighted_signature(reference_set, inverted_index, delta))
        unflattened = [weighted & set(r_i) for r_i in reference_set]
        skyline = set()
        for i, k in enumerate(unflattened):
            rhs = floor((1 - alpha) * len(reference_set[i])) + 1
            if len(k) < rhs:
                skyline |= k
            else:
                # add tokens with minimum |I[t]|
                tokens = list(k)
                tokens.sort(key=lambda t: len(inverted_index.get_indexes(t)))
                skyline = skyline.union(tokens[:rhs])
        return list(skyline)

    def _generate_dichotomy_signature(self, reference_set, inverted_index: InvertedIndex, delta, alpha):
        """
        Generates a signature using the Dichotomy Scheme as described in the SILKMOTH paper.

        For each element r_i, it chooses between its weighted signature part (k_i) and
        all its tokens (r_i) based on whether k_i is a subset of an optimal
        sim-thresh signature (m_i).
        """
        # 1. First, generate the optimal weighted signature, K.
        weighted_signature_K = set(self._generate_weighted_signature(reference_set, inverted_index, delta))

        final_dichotomy_sig = set()

        # 2. For each element r_i, decide whether to use its k_i or the full r_i.
        for r_i_list in reference_set:
            r_i = set(r_i_list)
            if not r_i:
                continue

            # 3. Determine k_i: the part of the weighted signature in this element.
            k_i = weighted_signature_K.intersection(r_i)

            # 4. Determine m_i: the optimal sim-thresh signature for this element.

            # 4a. Calculate the required size for the sim-thresh signature.
            m_i_size = floor((1 - alpha) * len(r_i)) + 1

            # 4b. Get all tokens from the original element r_i and sort by cost.
            element_tokens = list(r_i)

            # Sort tokens by the length of their inverted index list (cost).
            # Handle cases where a token might not be in the index.
            def get_token_cost(token):
                try:
                    return len(inverted_index.get_indexes(token))
                except ValueError:
                    return float('inf')  # Assign a high cost if not found

            element_tokens.sort(key=get_token_cost)

            # 4c. The optimal m_i consists of the cheapest tokens.
            m_i = set(element_tokens[:m_i_size])

            # 5. The Decision: Apply the paper's condition.
            # Can we get away with the cheaper weighted signature part (k_i)?
            # Yes, if k_i is already a subset of the optimal sim-thresh signature (m_i).
            if k_i.issubset(m_i):
                # Decision: Use the cheaper weighted signature tokens.
                final_dichotomy_sig.update(k_i)
            else:
                # Decision: Fall back to the safe, more expensive option.
                final_dichotomy_sig.update(r_i)

        return list(final_dichotomy_sig)


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
