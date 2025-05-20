import unittest
from silkmoth.verifier import Verifier
from silkmoth.inverted_index import InvertedIndex
from silkmoth.utils import *

class TestVerifier(unittest.TestCase):

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

        self.S1 = [{t2, t3, t5, t6, t7}, {t1, t2, t4, t5, t6}, {t1, t2, t3, t4, t7}]
        self.S2 = [{t1, t6, t8}, {t1, t4, t5, t6, t7}, {t1, t2, t3, t7, t9}]
        self.S3 = [{t1, t2, t3, t4, t6, t8}, {t2, t3, t11, t12}, {t1, t2, t3, t5}]
        self.S4 = [{t1, t2, t3, t8}, {t4, t5, t7, t9, t10}, {t1, t4, t5, t6, t9}]
        self.S = [self.S1, self.S2, self.S3, self.S4]
        self.R = [{t1, t2, t3, t6, t8}, {t4, t5, t7, t9, t10}, 
                  {t1, t4, t5, t11, t12}]

        self.ii = InvertedIndex(self.S)

    def test_jaccard_contain_exact(self):
        verifier = Verifier(1.0, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.S1, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, {0})

    def test_jaccard_contain_any(self):
        verifier = Verifier(0.0, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.S1, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, {0, 1, 2, 3})

    def test_jaccard_contain_approximate(self):
        verifier = Verifier(0.7, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.R, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, {3})

    def test_jaccard_not_contain_approximate(self):
        verifier = Verifier(0.8, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.R, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, set())