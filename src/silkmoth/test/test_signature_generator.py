import unittest

from silkmoth.inverted_index import InvertedIndex
from silkmoth.signature_generator import SignatureGenerator

class TestSignatureGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = SignatureGenerator()


    # Example 4 from Table 2 
    def test_valid_weighted_signature(self):
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

        R = [
            [t1,t2,t3,t6,t8],
            [t4,t5,t7,t9,t10],
            [t1,t4,t5,t11,t12],
        ]

        S1 = [[t2,t3,t5,t6,t7],[t1,t2,t4,t5,t6],[t1,t2,t3,t4,t7]]
        S2 = [[t1,t6,t8],[t1,t4,t5,t6,t7],[t1,t2,t3,t7,t9]]
        S3 = [[t1,t2,t3,t4,t6,t8],[t2,t3,t11,t12],[t1,t2,t3,t5]]
        S4 = [[t1,t2,t3,t8],[t4,t5,t7,t9,t10],[t1,t4,t5,t6,t9]]

        inverted_index = InvertedIndex([S1,S2,S3,S4])

        sig = set(self.generator.get_signature(R, inverted_index, 0.7))

        theta = 0.7 * len(R)
        total_loss = 0.0

        for elem in R:
            overlap = len(set(elem) & sig)
            loss = (len(elem) - overlap) / len(elem)
            total_loss += loss

        # instead of checking for exact tokens, use this condition (since many tokens possible)
        self.assertLess(total_loss, theta, "Signature does not satisfy weighted validity constraint")


    # Example from Table 2 with edge cases for delta = 0 and delta = 1
    def test_signature_deltas(self):
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

        R = [
            [t1,t2,t3,t6,t8],
            [t4,t5,t7,t9,t10],
            [t1,t4,t5,t11,t12],
        ]

        S1 = [[t2,t3,t5,t6,t7],[t1,t2,t4,t5,t6],[t1,t2,t3,t4,t7]]
        S2 = [[t1,t6,t8],[t1,t4,t5,t6,t7],[t1,t2,t3,t7,t9]]
        S3 = [[t1,t2,t3,t4,t6,t8],[t2,t3,t11,t12],[t1,t2,t3,t5]]
        S4 = [[t1,t2,t3,t8],[t4,t5,t7,t9,t10],[t1,t4,t5,t6,t9]]

        inverted_index = InvertedIndex([S1,S2,S3,S4])

        self.assertEqual(self.generator.get_signature(R, inverted_index, 0.0), [])

        delta_one_sig = self.generator.get_signature(R, inverted_index, 1.0)
        self.assertGreaterEqual(len(delta_one_sig), 1)


    # delta = 0 - no coverage is required 
    def test_sig_validity_for_delta_zero(self):
        R = [["A"], ["B"], ["C"]]
        dataset = [R]
        inverted_index = InvertedIndex(dataset)

        signatures = self.generator.get_signature(R, inverted_index, 0.0)
        self.assertEqual(signatures, [])  # No tokens needed


    # delta = 1 - total_loss < n required  
    def test_sig_validity_for_delta_one(self):
        R = [["A", "B"], ["C", "D"]]
        dataset = [R]
        index = InvertedIndex(dataset)

        signatures = self.generator.get_signature(R, index, 1.0)

        # one token suffices to achieve full coverage
        self.assertGreaterEqual(len(signatures), 1)


    def test_empty_reference_set(self):
        signatures = self.generator.get_signature([], InvertedIndex([]), 0.5)
        self.assertEqual(signatures, []) 


    def test_token_in_reference_and_not_in_index(self):
        R = [["A"]]
        dataset = [[["B"]]] 
        index = InvertedIndex(dataset)

        signatures = self.generator.get_signature(R, index, 0.5)

        self.assertEqual(signatures, []) # skip "A" since it's not in inverted index


    def test_one_token_covers_all(self):
        R = [["X"], ["X"]]   
        dataset = [[["X"], ["X"]]]
        index = InvertedIndex(dataset)

        signatures = self.generator.get_signature(R, index, 0.5)
        self.assertEqual(signatures, ["X"])  


    def test_duplicate_tokens(self):
        R = [["A", "A", "B"], ["B", "B", "C"]]  
        dataset = [R]
        index = InvertedIndex(dataset)

        signatures = self.generator.get_signature(R, index, 0.7)

        self.assertTrue(set(signatures).issubset({"A", "B", "C"}))




                
    

