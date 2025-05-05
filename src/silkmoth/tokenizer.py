from silkmoth.utils import *


class Tokenizer:

    def __init__(self, sim_func):
        """
        Initialize the Tokenizer with a similarity function.

        Args:
            sim_func (callable): The similarity function that influences tokenization behavior.
        """
        self.sim_func = sim_func

    def tokenize(self, set: list) -> list:
        """
        Tokenizes the input based on the similarity function.

        Args:
            set: The input string to tokenize.

        Returns:
            list: A list of str tokens extracted from the input.

        """
        tokens = []
        if self.sim_func == jaccard_similarity:
            tokens = self.jaccard_tokenize(set)
        else:
            raise ValueError("Unsupported similarity function")
        return tokens

    def jaccard_tokenize(self, set: list) -> list:
        """
        Tokenizes the input using Jaccard similarity.

        Args:
            set: The input string to tokenize.

        Returns:
            list: A list of str tokens extracted from the input string.
        """
        tokens = []
        for element in set:
            if isinstance(element, (str, int, float, bool)):
                tokens.extend(str(element).split())
            elif isinstance(element, (list, tuple)):
                for sub_element in element:
                    if isinstance(sub_element, (str, int, float, bool)):
                        tokens.extend(str(sub_element).split())
                    else:
                        raise ValueError(
                            f"Unsupported nested type: {type(sub_element)}"
                        )
            else:
                raise ValueError(f"Unsupported element type: {type(element)}")
        return tokens
