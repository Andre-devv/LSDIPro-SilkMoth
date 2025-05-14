import unittest
from silkmoth.inverted_index import InvertedIndex
from silkmoth.candidate_selector import CandidateSelector

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

        self.inverted_index = InvertedIndex(self.S)
        self.selector = CandidateSelector()

    def test_single_token(self):
        signature = {"Chicago"} # t11 (Chicago) only appears in S3
        candidates = self.selector.get_candidates(signature, self.inverted_index)
        self.assertEqual(candidates, {2})

    def test_multiple_tokens(self):
        # t1 (77) appears in all sets except S1
        # t4 (5th) appears in all sets
        signature = {"77", "5th"}
        candidates = self.selector.get_candidates(signature, self.inverted_index)
        self.assertEqual(candidates, {0, 1, 2, 3})

    def test_no_match(self):
        # Berlin does not appear in any set
        signature = {"Berlin"}
        candidates = self.selector.get_candidates(signature, self.inverted_index)
        self.assertEqual(candidates, set())

    def test_mixed_tokens(self):
        # one known and one unknown token
        signature = {"Mass", "UnknownToken"}
        candidates = self.selector.get_candidates(signature, self.inverted_index)
        self.assertEqual(candidates, {0, 1, 2, 3})  # from t2 = "Mass"