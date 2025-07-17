import unittest
from silkmoth.utils import *

class TestUtils(unittest.TestCase):

    def setUp(self):
        # Example from Table 2 in SilkMoth paper
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

        self.R = [{t1, t2, t3, t6, t8}, {t4, t5, t7, t9, t10}, 
                  {t1, t4, t5, t11, t12}]
        self.S1 = [{t2, t3, t5, t6, t7}, {t1, t2, t4, t5, t6},
                    {t1, t2, t3, t4, t7}]
        self.S2 = [{t1, t6, t8}, {t1, t4, t5, t6, t7}, {t1, t2, t3, t7, t9}]
        self.S3 = [{t1, t2, t3, t4, t6, t8}, {t2, t3, t11, t12}, {t1, t2, t3, t5}]
        self.S4 = [{t1, t2, t3, t8}, {t4, t5, t7, t9, t10}, {t1, t4, t5, t6, t9}]
        self.S = [self.S1, self.S2, self.S3, self.S4]
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

    def test_jaccard_sim(self):
        self.assertEqual(jaccard_similarity(self.R[0], self.S4[0]), 0.8)
        self.assertEqual(jaccard_similarity(self.R[1], self.S4[1]), 1)
        self.assertEqual(round(jaccard_similarity(self.R[2], self.S4[2]), 3), 0.429)
    
    def test_jaccard_zero(self):
        self.assertEqual(jaccard_similarity({}, {"a", "b"}), 0)
        self.assertEqual(jaccard_similarity({"a", "b"}, {}), 0)

    def test_jaccard_alpha(self):
        self.assertEqual(jaccard_similarity(self.R[0], self.S4[0], 0.7), 0.8)
        self.assertEqual(jaccard_similarity(self.R[1], self.S4[1], 0.7), 1)
        self.assertEqual(jaccard_similarity(self.R[2], self.S4[2], 0.7), 0)

    def test_contain(self):
        self.assertEqual(round(contain(3, 3, 2.229), 3), 0.743)

    def test_contain_error(self):
        with self.assertRaises(ValueError):
            contain(4, 3, 3)

    def test_similar(self):
        self.assertEqual(round(similar(3, 3, 2.229), 3), 0.591)
    
    def test_edit_sim(self):
        x = "50 Vassar St MA"
        y = "50 Vassar Street MA"
        self.assertEqual(edit_similarity(x,y),15/19)

    def test_edit_zero(self):
        self.assertEqual(edit_similarity({}, {"a", "b"}), 0)
        self.assertEqual(edit_similarity({"a", "b"}, {}), 0)

    def test_N_edit_sim(self):
        x = "50 Vassar St MA"
        y = "50 Vassar Street MA"
        self.assertEqual(N_edit_similarity(x,y),15/19)


    