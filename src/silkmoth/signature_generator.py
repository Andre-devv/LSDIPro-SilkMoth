import heapq
from collections import defaultdict
import warnings
from .utils import SigType,jaccard_similarity,edit_similarity,N_edit_similarity
from math import floor
from .inverted_index import *

class SignatureGenerator:

    def get_signature(self, reference_set, inverted_index, delta, alpha=0, sig_type=SigType.WEIGHTED, sim_fun = jaccard_similarity, q=3):
        """
        Compute a signature for a reference set according to the chosen signature type.

        Args:
            reference_set: Tokenized reference set.
            inverted_index (InvertedIndex): Index to evaluate token cost.
            delta (float): Relatedness threshold factor.
            alpha (float): Similarity threshold factor.
            sig_type (SigType): Type of signature.
            sim_fun (callable): Similarity function (phi) to use.
            q (int): Length of each q-chunk for edit similarity.

        Returns:
            list: A list of str for selected tokens forming the signature.
        """
        if sim_fun in (edit_similarity, N_edit_similarity):
            # If q is too large, no valid weighted signature exists
            q_bound = delta / (1 - delta)

            if q >= q_bound:
                warnings.warn(
                    f"q={q} is too large for delta = {delta:.3f}; "
                    "no valid weighted signature exists -> falling back to brute-force."
                )
                # returning all non-overlapping q-chunks so nothing is pruned
                all_chunks = []
                for elem in reference_set:
                    joined = " ".join(elem)
                    all_chunks += [
                        joined[i:i+q]
                        for i in range(0, len(joined) - q + 1, q)
                    ]
                return all_chunks

        match sig_type:
            case SigType.WEIGHTED:
                if sim_fun == edit_similarity or sim_fun == N_edit_similarity:
                    return self._generate_weighted_signature_edit_similarity(reference_set, inverted_index, delta, q)
                else:
                    return self._generate_weighted_signature(reference_set, inverted_index, delta)
            case SigType.SKYLINE:
                if sim_fun in (edit_similarity, N_edit_similarity) and alpha > 0:
                    return self._generate_simthresh_signature_edit_similarity(reference_set, inverted_index, delta, alpha, q)
                else:
                    return self._generate_skyline_signature(reference_set, inverted_index, delta, alpha)
            case SigType.DICHOTOMY:
                if sim_fun in (edit_similarity, N_edit_similarity) and alpha > 0:
                    return self._generate_simthresh_signature_edit_similarity(reference_set, inverted_index, delta, alpha, q)
                else:
                    return self._generate_dichotomy_signature(reference_set, inverted_index, delta, alpha)
            case _:
                raise ValueError(f"Unknown signature type") 
            

    def _generate_simthresh_signature_edit_similarity(self, reference_set, inverted_index, delta, alpha, q):
        """
        Builds a similarity-threshold signature for edit similarity as described in the SILKMOTH Paper in 
        Section 7.2.

        For each element r_i in the reference set, it ensures that the signature contains at least 
        m_i = floor((1 - alpha)/alpha * |q_chunks(r_i)|) + 1 q-chunks, so that any element 
        sharing fewer than m_i chunks cannot achieve Eds ≥ alpha.        
        """

        weighted_sig_edit_sim = set(self._generate_weighted_signature_edit_similarity(reference_set, inverted_index, delta, q))
        simthresh_sig = set(weighted_sig_edit_sim)

        for elem_tokens in reference_set:
            # compute all q-chunks of each element
            joined = " ".join(elem_tokens)
            chunks = [joined[j:j+q] for j in range(0, len(joined) - q + 1)]
            r = set(chunks)
            m_i = floor((1 - alpha) / alpha * len(r)) + 1

            # determine how many base chunks from this element are already in weighted signature
            k_i = list(weighted_sig_edit_sim & r)
            if len(k_i) < m_i:
                # need cheapest additional chunks -> sort all chunks by cost = inverted_index size
                sorted_chunks = sorted(
                    r,
                    key=lambda t: len(inverted_index.get_indexes(t)) if t in inverted_index.lookup_table else float('inf')
                )
                # add cheapest chunks up to m_i
                for chunk in sorted_chunks:
                    if len(simthresh_sig & r) >= m_i:
                        break
                    simthresh_sig.add(chunk)

        return list(simthresh_sig)    
            
    
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
    
    # Following the same logic of _generate_weighted_signature
    def _generate_weighted_signature_edit_similarity(self, reference_set, inverted_index, delta, q):
        if delta <= 0.0:
            return []

        n = len(reference_set)
        theta = delta * n  

        token_to_elems = defaultdict(list)   # map q-chunk -> list of element indexes
        token_value = {}                     # map q-chunk -> accumulated value

        r_sizes = []        # number of q-chunks per element
        element_chunks = [] # list of q-chunks per element

        # Step 1: Build q-chunks and token values
        for i, elem_tokens in enumerate(reference_set):
            if not elem_tokens:
                warnings.warn(f"Element at index {i} is empty and will be skipped.")
                r_sizes.append(0)
                element_chunks.append([])
                continue

            # Join the list of tokens into a string
            joined = " ".join(elem_tokens)

            # Extract non-overlapping q-chunks
            chunks = [joined[j:j+q] for j in range(0, len(joined) - q + 1, q)]
            chunk_set = set(chunks)
            element_chunks.append(chunks)

            num_chunks = len(chunk_set)
            r_sizes.append(num_chunks)

            if num_chunks == 0:
                continue

            weight = 1.0 / num_chunks
            for chunk in chunk_set:
                token_to_elems[chunk].append(i)
                token_value[chunk] = token_value.get(chunk, 0.0) + weight # value = sum of weights (for each chunk)

        # Step 2: Build heap (cost/value, token)
        heap = []
        for chunk, val in token_value.items():
            if val <= 0:
                continue
            try:
                cost = len(inverted_index.get_indexes(chunk))  # number of sets where chunk appears
            except ValueError:
                cost = float('inf')
            heapq.heappush(heap, (cost / val, chunk))

        # Step 3: Greedy selection
        selected_sig = set()
        current_k_counts = [0] * n
        total_score = 0.0  

        while heap and total_score < theta:
            ratio, chunk = heapq.heappop(heap)
            if chunk in selected_sig:
                continue
            if ratio == float('inf'):
                break

            selected_sig.add(chunk)

            for i in range(n):
                if r_sizes[i] == 0:
                    continue
                if chunk in element_chunks[i]:
                    current_k_counts[i] += 1

            total_score = sum(
                r_sizes[i] / (r_sizes[i] + current_k_counts[i])
                for i in range(n) if r_sizes[i] > 0
            )

        return list(selected_sig)