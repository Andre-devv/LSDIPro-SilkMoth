import unittest
from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import contain, jaccard_similarity

class TestEngine(unittest.TestCase):

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

        self.S1 = [" ".join([t2, t3, t5, t6, t7]), " ".join([t1, t2, t4, t5, t6]),
                    " ".join([t1, t2, t3, t4, t7])]
        self.S2 = [" ".join([t1, t6, t8]), " ".join([t1, t4, t5, t6, t7]),
                    " ".join([t1, t2, t3, t7, t9])]
        self.S3 = [" ".join([t1, t2, t3, t4, t6, t8]), " ".join([t2, t3, t11, t12]),
                    " ".join([t1, t2, t3, t5])]
        self.S4 = [" ".join([t1, t2, t3, t8]), " ".join([t4, t5, t7, t9, t10]),
                    " ".join([t1, t4, t5, t6, t9])]
        self.S = [self.S1, self.S2, self.S3, self.S4]
        self.R = [" ".join([t1, t2, t3, t6, t8]), " ".join([t4, t5, t7, t9, t10]), 
                  " ".join([t1, t4, t5, t11, t12])]

    def test_pipeline_running_base_example(self):
        engine = SilkMothEngine(0.7, self.S, contain, jaccard_similarity)
        search_results = engine.search_sets(self.R)
        self.assertEqual(search_results, {3})

if __name__ == '__main__':
    unittest.main()