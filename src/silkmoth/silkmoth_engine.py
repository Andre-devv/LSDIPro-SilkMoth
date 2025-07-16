from .utils import jaccard_similarity, similar, SigType
from .inverted_index import InvertedIndex
from .tokenizer import Tokenizer
from .signature_generator import SignatureGenerator
from .candidate_selector import CandidateSelector
from .verifier import Verifier
import warnings

class SilkMothEngine:
    
    def __init__(self, related_thresh, source_sets, sim_metric=similar, sim_func=jaccard_similarity, sim_thresh=0, reduction=False, sig_type=SigType.WEIGHTED, is_check_filter=False, is_nn_filter=False, q=3):
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
        
    def build_index(self, source_sets):
        token_sets = [self.tokenizer.tokenize(s) for s in source_sets]
        return InvertedIndex(token_sets)
        
    def search_sets(self, reference_set):
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


    def discover_sets(self, reference_sets):
        
        #related_pairs = []

        for i, reference_set in enumerate(reference_sets):
            sets, _, _ = self.search_sets(reference_set)
            #related_pairs.extend([(i, j, sim) for j, sim in sets])

        #return related_pairs

    def set_related_threshold(self, related_thresh):
        self.related_thresh = related_thresh
        self.verifier = self._create_verifier()
        self.candidate_selector = self._create_candidate_selector()

    def set_signature_type(self, sig_type):
        self.signature_type = sig_type

    def set_check_filter(self, is_check_filter):
        self.is_check_filter = is_check_filter

    def set_nn_filter(self, is_nn_filter):
        self.is_nn_filter = is_nn_filter

    def set_alpha(self, sim_thresh):
        self.sim_thresh = sim_thresh
        self.verifier = self._create_verifier()
        self.candidate_selector = self._create_candidate_selector()

    def set_reduction(self, reduction):
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
        self.q = q
        self.tokenizer = Tokenizer(self.sim_func, q)
        self.inverted_index = self.build_index(self.source_sets)
        self.signature_gen = SignatureGenerator()
        self.candidate_selector = self._create_candidate_selector()
        self.verifier = self._create_verifier()



