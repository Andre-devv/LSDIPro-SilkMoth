from .utils import jaccard_similarity, N_edit_similarity, edit_similarity
from ordered_set import OrderedSet

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

def qgram_tokenize(input_set: list, q: int) -> list[list[str]]:
    """
    Tokenizes the input using q-gram tokenization.

    Args:
        input_set (list): Input set with strings or nested values.
        q (int): Length of q-gram.

    Returns:
        list[list[str]]: A list of lists, each containing ordered q-gram tokens.
    """

    def to_qgrams(s: str) -> list[str]:
        s = s.strip()
        if len(s) < q:
            return []
        return [s[i:i+q] for i in range(len(s) - q + 1)]

    def flatten(x):
        for el in x:
            if isinstance(el, (list, tuple)):
                yield from flatten(el)
            else:
                yield el

    tokens = []
    for element in input_set:
        if isinstance(element, (str, int, float, bool)):
            s = str(element)
        elif isinstance(element, (list, tuple)):
            # Flatten nested elements and join with space
            s = " ".join(str(x) for x in flatten(element))
        else:
            raise ValueError(f"Unsupported element type: {type(element)}")
        
        tokens.append(to_qgrams(s))  # generate q-grams for the full string

    return tokens



class Tokenizer:

    def __init__(self, sim_func, q=3):
        """
        Initialize the Tokenizer with a similarity function.

        Args:
            sim_func (callable): The similarity function that influences tokenization behavior.
            q (int): The q-gram size for tokenization, default is 3.
        """
        self.sim_func = sim_func
        self.q = q

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
        elif self.sim_func == edit_similarity or self.sim_func == N_edit_similarity:
            tokens = qgram_tokenize(input_set, self.q)
        else:
            raise ValueError("Unsupported similarity function")
        return tokens
