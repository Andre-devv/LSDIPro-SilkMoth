import unittest
from silkmoth.tokenizer import Tokenizer
from silkmoth.utils import jaccard_similarity


class TestTokenizer(unittest.TestCase):

    def setUp(self):
        self.tokenizer_jaccard = Tokenizer(sim_func=jaccard_similarity)
        self.tokenizer_unsupported = Tokenizer(sim_func=None)

    def test_unsupported_similarity_function(self):

        with self.assertRaises(ValueError):
            self.tokenizer_unsupported.tokenize("test string")

    def test_jaccard_tokenize_english(self):
        input_string = "77 Mass Ave Boston MA"
        expected_tokens = ["77", "Mass", "Ave", "Boston", "MA"]
        tokens = self.tokenizer_jaccard.tokenize(input_string)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_unicode(self):
        input_string = "こんにちは 世界 🌍"
        expected_tokens = ["こんにちは", "世界", "🌍"]
        tokens = self.tokenizer_jaccard.tokenize(input_string)
        self.assertEqual(tokens, expected_tokens)


if __name__ == "__main__":
    unittest.main()
