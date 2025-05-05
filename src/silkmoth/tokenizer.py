from silkmoth.utils import *


class Tokenizer:

    def __init__(self, sim_func):
        """
        Initialize the Tokenizer with a similarity function.

        Args:
            sim_func (callable): The similarity function that influences tokenization behavior.
        """
        self.sim_func = sim_func

    def tokenize(self, set: str) -> list:
        """
        Tokenizes the input string based on the similarity function.

        Args:
            set (str): The input string to tokenize.

        Returns:
            list: A list of str tokens extracted from the input string.

        """
        tokens = []
        if self.sim_func == jaccard_similarity:
            tokens = self.jaccard_tokenize(set)
        else:
            raise ValueError("Unsupported similarity function")
        return tokens

    def jaccard_tokenize(self, set: str) -> list:
        """
        Tokenizes the input string using Jaccard similarity.

        Args:
            set (str): The input string to tokenize.

        Returns:
            list: A list of str tokens extracted from the input string.
        """
        tokens = set.split()
        return tokens
