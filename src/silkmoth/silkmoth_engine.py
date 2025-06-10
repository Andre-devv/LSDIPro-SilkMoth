from .utils import *
from .inverted_index import *
from .tokenizer import *
from .signature_generator import *
from .candidate_selector import *
from .verifier import *
import sys

class SilkMothEngine:
    
    def __init__(self, related_thresh, source_sets, sim_metric=similar, sim_func=jaccard_similarity, sim_thresh=0, reduction=False):
        self.related_thresh = related_thresh        # delta
        self.source_sets = source_sets              # S
        self.sim_metric = sim_metric                # related
        self.sim_func = sim_func                    # phi
        self.sim_thresh = sim_thresh                # alpha
        self.reduction = reduction
        self.tokenizer = Tokenizer(sim_func)
        self.signature_gen = SignatureGenerator()
        self.candidate_selector = CandidateSelector(similarity_func=self.sim_func, sim_metric=self.sim_metric, related_thresh=self.related_thresh)
        self.verifier = Verifier(related_thresh, sim_metric, sim_func, sim_thresh, reduction)
        self.inverted_index = self.build_index(source_sets)
        
    def build_index(self, source_sets):
        token_sets = [self.tokenizer.tokenize(s) for s in source_sets]
        return InvertedIndex(token_sets)
        
    def search_sets(self, reference_set):
        r_tokens = self.tokenizer.tokenize(reference_set)
        signature = self.signature_gen.get_signature(r_tokens, self.inverted_index, self.related_thresh)
        candidates = self.candidate_selector.get_candidates(signature, self.inverted_index, len(r_tokens))
        filtered_candidates = self.candidate_selector.check_filter(
        r_tokens, set(signature), candidates, self.inverted_index
        )
        return self.verifier.get_related_sets(r_tokens, filtered_candidates, self.inverted_index)


    def discover_sets(self, reference_sets):
        
        related_pairs = []

        for i, reference_set in enumerate(reference_sets):
            sets = self.search_sets(reference_set)
            related_pairs.extend([(i, j, sim) for j, sim in sets])

        return related_pairs