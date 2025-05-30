import unittest
from silkmoth.inverted_index import InvertedIndex
from silkmoth.candidate_selector import CandidateSelector
from silkmoth.utils import jaccard_similarity, contain, similar


class TestCandidateSelector(unittest.TestCase):

    def setUp(self):
        # Same example from Table 2
        t1 = "77"
        t2 = "Mass"
        t3 = "Ave"
        t4 = "5th"
        t5 = "St"
        t6 = "Boston"
        t7 = "02115"
        t8 = "MA"
        t9 = "Seattle"
        t10 = "WA"
        t11 = "Chicago"
        t12 = "IL"

        self.S1 = [[t2, t3, t5, t6, t7], [t1, t2, t4, t5, t6], [t1, t2, t3, t4, t7]]
        self.S2 = [[t1, t6, t8], [t1, t4, t5, t6, t7], [t1, t2, t3, t7, t9]]
        self.S3 = [[t1, t2, t3, t4, t6, t8], [t2, t3, t11, t12], [t1, t2, t3, t5]]
        self.S4 = [[t1, t2, t3, t8], [t4, t5, t7, t9, t10], [t1, t4, t5, t6, t9]]
        self.S = [self.S1, self.S2, self.S3, self.S4]

        self.R = [[t1, t2, t3, t6, t8], [t4, t5, t7, t9, t10], [t1, t4, t5, t11, t12]]

        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.t4 = t4
        self.t5 = t5
        self.t6 = t6
        self.t7 = t7
        self.t8 = t8
        self.t9 = t9
        self.t10 = t10
        self.t11 = t11
        self.t12 = t12

        self.K = {t8, t9, t10, t11, t12}

        self.inverted_index = InvertedIndex(self.S)
        self.selector = CandidateSelector(similarity_func=jaccard_similarity, sim_metric=contain, related_thresh=0.7)

    def test_single_token(self):
        signature = {"Chicago"}  # t11 (Chicago) only appears in S3
        candidates = self.selector.get_candidates(signature, self.inverted_index, 1)
        self.assertEqual(candidates, {2})

    def test_multiple_tokens(self):
        # t1 (77) appears in all sets except S1
        # t4 (5th) appears in all sets
        signature = {"77", "5th"}
        candidates = self.selector.get_candidates(signature, self.inverted_index, 1)
        self.assertEqual(candidates, {0, 1, 2, 3})

    def test_no_match(self):
        # Berlin does not appear in any set
        signature = {"Berlin"}
        candidates = self.selector.get_candidates(signature, self.inverted_index, 1)
        self.assertEqual(candidates, set())

    def test_mixed_tokens(self):
        # one known and one unknown token
        signature = {"Mass", "UnknownToken"}
        candidates = self.selector.get_candidates(signature, self.inverted_index, 1)
        self.assertEqual(candidates, {0, 1, 2, 3})  # from t2 = "Mass"

    def test_check_filter_table2(self):
        # Signature tokens as in example 6 from paper
        candidates = {0, 1, 2, 3}
        filtered = self.selector.check_filter(
            self.R, self.K, candidates, self.inverted_index
        )

        self.assertNotIn(1, filtered)  # S2 is filtered out
        self.assertIn(2, filtered)  # S3 should pass
        self.assertIn(3, filtered)  # S4 should pass

    def test_check_filter_empty_reference_set(self):
        empty_R = []
        candidates = {0, 1, 2, 3}
        filtered = self.selector.check_filter(
            empty_R, self.K, candidates, self.inverted_index
        )
        self.assertEqual(filtered, set())

    def test_check_filter_empty_signature(self):
        candidates = {0, 1, 2, 3}
        filtered = self.selector.check_filter(
            self.R, set(), candidates, self.inverted_index
        )
        self.assertEqual(filtered, set())

    def test_size_filter_contain(self):
        self.assertTrue(self.selector.verify_size(5, 5))
        self.assertTrue(self.selector.verify_size(2, 5))
        self.assertFalse(self.selector.verify_size(5, 2))

    def test_size_filter_similar(self):
        sel = CandidateSelector(similarity_func=jaccard_similarity, sim_metric=similar, related_thresh=0.7)
        self.assertFalse(sel.verify_size(5, 3))
        self.assertFalse(sel.verify_size(3, 5))
        self.assertTrue(sel.verify_size(5, 4))
        self.assertTrue(sel.verify_size(4, 5))
