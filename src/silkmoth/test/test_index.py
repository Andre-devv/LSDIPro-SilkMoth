import unittest
from silkmoth.inverted_index import InvertedIndex

class TestInvertedIndex(unittest.TestCase):

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

        self.R = [[t1, t2, t3, t6, t8], [t4, t5, t7, t9, t10], 
                  [t1, t4, t5, t11, t12]]
        self.S1 = [[t2, t3, t5, t6, t7], [t1, t2, t4, t5, t6],
                    [t1, t2, t3, t4, t7]]
        self.S2 = [[t1, t6, t8], [t1, t4, t5, t6, t7], [t1, t2, t3, t7, t9]]
        self.S3 = [[t1, t2, t3, t4, t6, t8], [t2, t3, t11, t12], [t1, t2, t3, t5]]
        self.S4 = [[t1, t2, t3, t8], [t4, t5, t7, t9, t10], [t1, t4, t5, t6, t9]]
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

    def test_indexes(self):
        I = InvertedIndex(self.S)
        self.assertEqual(I.get_indexes("IL"), [(2, 1)]) 
        self.assertEqual(I.get_indexes("02115"), [(0, 0), (0, 2), (1, 1), (1, 2), (3, 1)])

    def test_keys(self):
        I = InvertedIndex(self.S)
        all_tokens = set(["77", "Mass", "Ave", "5th", "St", "Boston", "02115", 
                          "MA", "Seattle", "WA", "Chicago", "IL"])
        self.assertEqual(all_tokens, I.keys())

    def test_getitem(self):
        I = InvertedIndex(self.S)
        self.assertEqual(I["Chicago"], [(self.S3, self.S3[1])])
        self.assertEqual(I["MA"], [(self.S2, self.S2[0]), (self.S3, self.S3[0]), (self.S4, self.S4[0])])
        
    def test_unknown_token(self):
        I = InvertedIndex(self.S)
        with self.assertRaises(ValueError):
            I["Berlin"]
        with self.assertRaises(ValueError):
            I.get_indexes("Berlin")

    def test_get_set(self):
        I = InvertedIndex(self.S)
        index_list = I.get_indexes("IL")
        set_idx, _ = index_list[0]
        self.assertEqual(I.get_set(set_idx), self.S3)

    def test_invalid_id(self):
        I = InvertedIndex(self.S)
        with self.assertRaises(ValueError):
            I.get_set(-1)
        with self.assertRaises(ValueError):
            I.get_set(4)
        