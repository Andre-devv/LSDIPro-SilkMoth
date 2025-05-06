import unittest
from silkmoth.tokenizer import Tokenizer
from silkmoth.utils import jaccard_similarity
from io import StringIO
import csv


class TestTokenizer(unittest.TestCase):

    def setUp(self):
        self.tokenizer_jaccard = Tokenizer(sim_func=jaccard_similarity)
        self.tokenizer_unsupported = Tokenizer(sim_func=None)

    def test_unsupported_similarity_function(self):

        with self.assertRaises(ValueError):
            self.tokenizer_unsupported.tokenize("test string")

    def test_jaccard_tokenize_english(self):
        input_string = ["77 Mass Ave Boston MA"]
        expected_tokens = ["77", "Mass", "Ave", "Boston", "MA"]
        tokens = self.tokenizer_jaccard.tokenize(input_string)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_unicode(self):
        input_string = ["こんにちは 世界 🌍"]
        expected_tokens = ["こんにちは", "世界", "🌍"]
        tokens = self.tokenizer_jaccard.tokenize(input_string)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_numbers(self):
        input_data = [123, 45.67, True]
        expected_tokens = ["123", "45.67", "True"]
        tokens = self.tokenizer_jaccard.tokenize(input_data)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_nested_lists(self):
        input_data = [["77 Mass Ave", "Boston"], ["MA", 123]]
        expected_tokens = ["77", "Mass", "Ave", "Boston", "MA", "123"]
        tokens = self.tokenizer_jaccard.tokenize(input_data)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_unsupported_type(self):
        input_data = [{"key": "value"}]  # Dictionaries are unsupported
        with self.assertRaises(ValueError):
            self.tokenizer_jaccard.tokenize(input_data)

    def test_jaccard_tokenize_unsupported_nested_type(self):
        input_data = [["77 Mass Ave", {"key": "value"}]]  # Nested dict is unsupported
        with self.assertRaises(ValueError):
            self.tokenizer_jaccard.tokenize(input_data)

    def test_jaccard_tokenize_empty_list(self):
        input_data = []
        expected_tokens = []
        tokens = self.tokenizer_jaccard.tokenize(input_data)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_mixed_types(self):
        input_data = ["Hello World", 123, [True, 45.67]]
        expected_tokens = ["Hello", "World", "123", "True", "45.67"]
        tokens = self.tokenizer_jaccard.tokenize(input_data)
        self.assertEqual(tokens, expected_tokens)

    def test_jaccard_tokenize_csv_data(self):
        # Test on CSV data with mixed types
        csv_data = """Name,Age,Location,Score,Active
                        Alice,30,New York,85.5,True
                        Bob,25,Los Angeles,90.0,False"""

        reader = csv.reader(StringIO(csv_data))
        input_data = list(reader)

        expected_tokens = [
            "Name",
            "Age",
            "Location",
            "Score",
            "Active",
            "Alice",
            "30",
            "New",
            "York",
            "85.5",
            "True",
            "Bob",
            "25",
            "Los",
            "Angeles",
            "90.0",
            "False",
        ]
        tokens = self.tokenizer_jaccard.tokenize(input_data)

        self.assertEqual(tokens, expected_tokens)


if __name__ == "__main__":
    unittest.main()
