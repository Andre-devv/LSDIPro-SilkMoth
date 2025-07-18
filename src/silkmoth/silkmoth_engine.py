from .utils import jaccard_similarity, similar, SigType
from .inverted_index import InvertedIndex
from .tokenizer import Tokenizer
from .signature_generator import SignatureGenerator
from .candidate_selector import CandidateSelector
from .verifier import Verifier
import warnings

class SilkMothEngine:
    """
    The SilkMothEngine is the system's main component. It brings all the SilkMoth
    components together, enabling users to easily vary the system's setup and
    explore the relationships between their input sets.

    Examples
    --------
    ```
    >>> from silkmoth.silkmoth_engine import SilkMothEngine
    >>> from silkmoth.utils import contain
    >>> S = [
    ...     ['Mass Ave St Boston 02115', '77 Mass 5th St Boston', '77 Mass Ave 5th 02115'],
    ...     ['77 Boston MA', '77 5th St Boston 02115', '77 Mass Ave 02115 Seattle'],
    ...     ['77 Mass Ave 5th Boston MA', 'Mass Ave Chicago IL', '77 Mass Ave St'],
    ...     ['77 Mass Ave MA', '5th St 02115 Seattle WA', '77 5th St Boston Seattle']
    ... ]
    >>> R = ['77 Mass Ave Boston MA', '5th St 02115 Seattle WA', '77 5th St Chicago IL']
    >>> engine = SilkMothEngine(0.7, S, contain)
    >>> results, _, _ = engine.search_sets(R)
    >>> results
    [(3, 0.7428571428571429)]
    >>> engine.set_related_threshold(0.3)
    >>> results, _, _ = engine.search_sets(R)
    >>> results
    [(0, 0.36904761904761907), (1, 0.4261904761904762), (2, 0.4146825396825397), (3, 0.7428571428571429)]
    ```
    """
    
    def __init__(self, related_thresh, source_sets, sim_metric=similar, sim_func=jaccard_similarity, sim_thresh=0, reduction=False, sig_type=SigType.WEIGHTED, is_check_filter=False, is_nn_filter=False, q=3):
        """
        Initialize the SilkMothEngine with all the necessary parameters.
        
        Args:
            related_thresh (float): Relatedness threshold delta
            source_sets (list): Collection of source sets
            sim_metric (callable): Similarity metric similar(...)/contain(...)
            sim_func (callable): Similarity function phi
            sim_thresh (float): Similarity threshold alpha
            reduction (bool): Flag to activate/deactivate triangle inequality reduction
            sig_type (SigType): Type of signature.
            is_check_filter (bool): Flag to activate/deactivate check filter
            is_nn_filter (bool): Flag to activate/deactivate nearest neighbor filter
            q (int): The q-gram size for tokenization
        """
        self.related_thresh = related_thresh        # delta
        self.source_sets = source_sets              # S
        self.sim_metric = sim_metric                # related
        self.sim_func = sim_func                    # phi
        self.sim_thresh = sim_thresh                # alpha
        self.q = q                                  # q-gram size
        self.reduction = reduction
        self.signature_type = sig_type
        self.tokenizer = Tokenizer(sim_func, q)
        self.is_check_filter = is_check_filter
        self.is_nn_filter = is_nn_filter
        self.signature_gen = SignatureGenerator()
        self.candidate_selector = self._create_candidate_selector()
        self.verifier = self._create_verifier()
        self.inverted_index = self.build_index(source_sets)
        
    def build_index(self, source_sets) -> InvertedIndex:
        """
        Tokenizes all source sets and creates the inverted index.

        Args:
            source_sets (list): Collection of "raw" source sets
        
        Returns:
            InvertedIndex: Inverted index
        """
        token_sets = [self.tokenizer.tokenize(s) for s in source_sets]
        return InvertedIndex(token_sets)
        
    def search_sets(self, reference_set) -> tuple[list, int, int]:
        """
        Search mode, where, given a reference set, we search for all related sets
        in the dataset.

        Args:
            reference_set (list): "Raw" reference set

        Returns:
            list:   Pairs of indices of all related sets from the candidates and 
                    their relatedness with the reference set.
            int:    Number of candidates before applying filters.
            int:    Number of candidates after applying filters. 
        """
        r_tokens = self.tokenizer.tokenize(reference_set)
        signature = self.signature_gen.get_signature(r_tokens, self.inverted_index, self.related_thresh, self.sim_thresh, self.signature_type, self.sim_func, self.q)
        candidates = self.candidate_selector.get_candidates(signature, self.inverted_index, len(r_tokens))

        # Count how many candidates are removed by the filters
        candidates_start = len(candidates)

        # Apply check filter if enabled
        if self.is_check_filter:
            candidates, match_map = self.candidate_selector.check_filter(
                r_tokens, set(signature), candidates, self.inverted_index
            )
        else:
            match_map = None

        # Apply nearest neighbor filter if enabled
        if self.is_nn_filter:
            candidates= self.candidate_selector.nn_filter(
                r_tokens, set(signature), candidates, self.inverted_index, self.related_thresh, match_map
            )

        return self.verifier.get_related_sets(r_tokens, candidates, self.inverted_index), candidates_start , len(candidates)


    def discover_sets(self, reference_sets) -> list:
        """
        Discovery mode, where we search for all pairs of related sets within a 
        collection of reference sets.

        Args:
            reference_sets (list): Collection of "raw" reference set
        
        Returns:
            list:   Tuples (i, j, sim) of all related sets with reference index i,
                    source set index j and the computed similarity score sim.
        """
        #related_pairs = []

        for i, reference_set in enumerate(reference_sets):
            sets, _, _ = self.search_sets(reference_set)
            #related_pairs.extend([(i, j, sim) for j, sim in sets])

        #return related_pairs

    def set_related_threshold(self, related_thresh):
        """
        Updates the relatedness threshold.

        Args:
            related_thresh (float): Relatedness threshold delta
        """
        self.related_thresh = related_thresh
        self.verifier = self._create_verifier()
        self.candidate_selector = self._create_candidate_selector()

    def set_signature_type(self, sig_type):
        """
        Updates the signature type.

        Args:
            sig_type (SigType): Signature type
        """
        self.signature_type = sig_type

    def set_check_filter(self, is_check_filter):
        """
        Updates the check filter flag.

        Args:
            is_check_filter (bool): Flag to activate/deactivate check filter
        """
        self.is_check_filter = is_check_filter

    def set_nn_filter(self, is_nn_filter):
        """
        Updates the nearest neighbor filter flag.

        Args:
            is_nn_filter (bool): Flag to activate/deactivate nearest neighbor filter
        """
        self.is_nn_filter = is_nn_filter

    def set_alpha(self, sim_thresh):
        """
        Updates the similarity threshold.

        Args:
            sim_thresh (float): Similarity threshold alpha
        """
        self.sim_thresh = sim_thresh
        self.verifier = self._create_verifier()
        self.candidate_selector = self._create_candidate_selector()

    def set_reduction(self, reduction):
        """
        Updates the reduction flag.

        Args:
            reduction (bool): Flag to activate/deactivate reduction
        """
        self.reduction = reduction
        self.verifier = self._create_verifier()

    def _create_verifier(self):
        if self.reduction and self.sim_thresh > 0:
            self.reduction = False
            warnings.warn(""""Reduction-based verification does not work when the 
                          similarity threshold alpha is greater than zero. 
                          Reduction is disabled for now.""")
        return Verifier(
            self.related_thresh,
            self.sim_metric,
            self.sim_func,
            self.sim_thresh,
            self.reduction
        )

    def _create_candidate_selector(self):
        return CandidateSelector(
            self.sim_func,
            self.sim_metric,
            self.related_thresh,
            self.sim_thresh
        )

    def set_q(self, q):
        """
        Updates q-gram size.

        Args:
            q (int): The q-gram size for tokenization
        """
        self.q = q
        self.tokenizer = Tokenizer(self.sim_func, q)
        self.inverted_index = self.build_index(self.source_sets)
        self.signature_gen = SignatureGenerator()
        self.candidate_selector = self._create_candidate_selector()
        self.verifier = self._create_verifier()



