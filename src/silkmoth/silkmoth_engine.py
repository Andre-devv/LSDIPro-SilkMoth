from silkmoth.utils import *
from silkmoth.inverted_index import *
from silkmoth.tokenizer import *
from silkmoth.signature_generator import *
from silkmoth.candidate_selector import *
from silkmoth.verifier import *

class SilkMothEngine:
    
    def __init__(self, related_thresh, source_sets, sim_metric=similar, sim_func=jaccard_similarity, sim_thresh=0):
        self.related_thresh = related_thresh        # theta
        self.source_sets = source_sets              # S
        self.sim_metric = sim_metric                # related
        self.sim_func = sim_func                    # phi
        self.sim_thresh = sim_thresh                # alpha
        self.inverted_index = self.build_index(source_sets)
        self.tokenizer = Tokenizer(sim_func)
        self.signature_gen = SignatureGenerator()
        self.candidate_selector = CandidateSelector()
        self.verifier = Verifier()
        
    def build_index(source_sets):
        pass

    def search_sets(self, reference_set):
        r_tokens = self.tokenizer.tokenize(reference_set)
        signature = self.signature_gen.get_signature(r_tokens)
        candidates = self.candidate_selector.get_candidates(signature, self.inverted_index)
        return self.verifier.get_related_sets(candidates, r_tokens)

    def discover_sets(self, reference_sets):
        pass