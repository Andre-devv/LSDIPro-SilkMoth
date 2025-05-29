from .utils import *


def jaccard_tokenize(input_set: list) -> list:
    """
    Tokenizes the input using Jaccard similarity.

    Args:
        input_set: The input set to tokenize.

    Returns:
        list: A list of str tokens extracted from the input string.
    """
    tokens = []
    for element in input_set:
        if isinstance(element, (str, int, float, bool)):
            tokens.append(set(str(element).split()))
        elif isinstance(element, (list, tuple)):
            sub_tokens = set()
            for sub_element in element:
                if isinstance(sub_element, (str, int, float, bool)):
                    sub_tokens.update(str(sub_element).split())
                elif isinstance(sub_element, (list, tuple)):
                    for sub_sub_element in sub_element:
                        if isinstance(sub_sub_element, (str, int, float, bool)):
                            sub_tokens.update(str(sub_sub_element).split())
                        else:
                            raise ValueError(
                                f"Unsupported nested type: {type(sub_element)}"
                            )
                else:
                    raise ValueError(
                        f"Unsupported nested type: {type(sub_element)}"
                    )
            tokens.append(sub_tokens)
        else:
            raise ValueError(f"Unsupported element type: {type(element)}")
    return tokens


class Tokenizer:

    def __init__(self, sim_func):
        """
        Initialize the Tokenizer with a similarity function.

        Args:
            sim_func (callable): The similarity function that influences tokenization behavior.
        """
        self.sim_func = sim_func

    def tokenize(self, input_set: list) -> list:
        """
        Tokenizes the input based on the similarity function.

        Args:
            input_set: The input set to tokenize.

        Returns:
            list: A list of str tokens extracted from the input.

        """
        if self.sim_func == jaccard_similarity:
            tokens = jaccard_tokenize(input_set)
        else:
            raise ValueError("Unsupported similarity function")
        return tokens
