import unittest
from silkmoth.verifier import Verifier, reduce_sets
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
        self.assertEqual(result, [(0, 1.0)])

    def test_jaccard_contain_any(self):
        verifier = Verifier(0.0, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.S1, {0, 1, 2, 3}, self.ii)
        idxs = [i for i, _ in result]
        self.assertEqual(set(idxs), {0, 1, 2, 3})

    def test_jaccard_contain_approximate(self):
        verifier = Verifier(0.7, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.R, {0, 1, 2, 3}, self.ii)
        i, sim = result[0]
        self.assertEqual(len(result), 1)
        self.assertEqual(i, 3)
        self.assertGreaterEqual(sim, 0.7)

    def test_jaccard_not_contain_approximate(self):
        verifier = Verifier(0.8, contain, jaccard_similarity)
        result = verifier.get_related_sets(self.R, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, [])

    def test_jaccard_contain_exact_reduced(self):
        verifier = Verifier(1.0, contain, jaccard_similarity, reduction=True)
        result = verifier.get_related_sets(self.S1, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, [(0, 1.0)])

    def test_jaccard_contain_any_reduced(self):
        verifier = Verifier(0.0, contain, jaccard_similarity, reduction=True)
        result = verifier.get_related_sets(self.S1, {0, 1, 2, 3}, self.ii)
        idxs = [i for i, _ in result]
        self.assertEqual(set(idxs), {0, 1, 2, 3})

    def test_jaccard_contain_approximate_reduced(self):
        verifier = Verifier(0.7, contain, jaccard_similarity, reduction=True)
        result = verifier.get_related_sets(self.R, {0, 1, 2, 3}, self.ii)
        i, sim = result[0]
        self.assertEqual(len(result), 1)
        self.assertEqual(i, 3)
        self.assertGreaterEqual(sim, 0.7)

    def test_jaccard_not_contain_approximate_reduced(self):
        verifier = Verifier(0.8, contain, jaccard_similarity, reduction=True)
        result = verifier.get_related_sets(self.R, {0, 1, 2, 3}, self.ii)
        self.assertEqual(result, [])

    def test_reduce_nothing(self):
        r_reduced, s_reduced, count = reduce_sets(self.R, self.S1)
        self.assertEqual(r_reduced, self.R)
        self.assertEqual(s_reduced, self.S1)
        self.assertEqual(count, 0)

    def test_reduce_all(self):
        r_reduced, s_reduced, count = reduce_sets(self.R, self.R)
        self.assertEqual(r_reduced, [])
        self.assertEqual(s_reduced, [])
        self.assertEqual(count, len(self.R))

    def test_reduce_duplicates(self):
        ref = [{"0", "1"}, {"0", "1"}, {"2"}, {"3"}, {"1"}]
        src = [{"2"}, {"2"}, {"3"}, {"1", "0"}]
        r_reduced, s_reduced, count = reduce_sets(ref, src)
        self.assertEqual(r_reduced, [{"0", "1"}, {"1"}])
        self.assertEqual(s_reduced, [{"2"}])
        self.assertEqual(count, 3)

    def test_mm_score(self):
        verifier = Verifier(0.7, contain, jaccard_similarity)
        mm_score = verifier.get_mm_score(self.R, self.S4)
        self.assertEqual(round(mm_score, 3), 2.229)