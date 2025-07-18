from enum import Enum
from rapidfuzz.distance import Levenshtein
from ordered_set import OrderedSet

def jaccard_similarity(x: set, y: set, sim_thresh=0) -> float:
    """
    Gives the Jaccard similarity of two set-like objects. Jaccard similarity is
    defined as $Jac(x, y) = |x \cap y|/|x \cup y|$. 
    
    For some applications we may want to omit pairs with low similarity. 
    Therefore a similarity threshold α is provided. If the similarity score 
    does not exceed this threshold, this function returns zero.

    Examples
    --------
    ```
    >>> from silkmoth.utils import jaccard_similarity
    >>> x = {"a", "b", "c"}
    >>> y = {"a", "b", "c"}
    >>> jaccard_similarity(x, y)
    1.0
    >>> y.add("d")
    >>> jaccard_similarity(x, y)
    0.75
    >>> jaccard_similarity(x, y, 0.8)
    0.0
    ```

    Args:
        x (set): Input element x
        y (set): Input element y
        sim_thresh (float): Similarity threshold alpha

    Returns:
        float: Jaccard similarity score
    """
    if len(x) == 0 or len(y) == 0:
        return .0
    jac = len(x & y) / len(x | y)
    if jac >= sim_thresh:
        return jac
    return .0

def edit_similarity (x, y, sim_thresh=0) -> float:
    """
        Computes the edit similarity between two strings based on
        the formula given in the SILKMOTH paper:
        $Eds(x, y) = 1 - (2 * LD(x, y)) / (|x| + |y| + LD(x, y))$

        Args:
            x (str or set/list of str): First input
            y (str or set/list of str): Second input
            sim_thresh (float): Similarity threshold alpha (default is 0)

        Returns:
            float: Edit similarity score (0 if below threshold)
        """
    x_str = reverse_qgrams(x)
    y_str = reverse_qgrams(y)

    if not x_str or not y_str:
        return .0

    ld = Levenshtein.distance(x_str, y_str)
    eds = 1 - (2 * ld) / (len(x_str) + len(y_str) + ld)
    return eds if eds >= sim_thresh else .0

def N_edit_similarity(x, y, sim_thresh=0) -> float:
    """
    Computes the normalized edit similarity NEds between two strings or sets/lists of tokens:
    $NEds(x, y) = 1 - LD(x, y) / max(|x|, |y|)$

    Args:
        x (str or set/list of str): First input
        y (str or set/list of str): Second input
        sim_thresh (float): Similarity threshold (default: 0)

    Returns:
        float: Similarity score in [0, 1], or 0 if below threshold
    """
    x_str = reverse_qgrams(x)
    y_str = reverse_qgrams(y)

    if not x_str or not y_str:
        return .0

    ld = Levenshtein.distance(x_str, y_str)
    max_len = max(len(x_str), len(y_str))

    if max_len == 0:
        return 1.0 

    neds_score = 1 - (ld / max_len)
    return neds_score if neds_score >= sim_thresh else .0


def flatten_tokens(input_val):
    """
    Flattens a set, list of sets, or other nested iterable into a flat list of strings.
    """
    if isinstance(input_val, (set, list)):
        flat = []
        for elem in input_val:
            if isinstance(elem, (set, list)):
                flat.extend(elem)
            else:
                flat.append(elem)
        return " ".join(flat)
    return input_val  # assume it's already a string

def reverse_qgrams(input_val) -> str:
    """
    Reverse qgrams back to their original text.
    """
    if isinstance(input_val, (OrderedSet)):
        if len(input_val) == 0:
            return ""
        if len(input_val) == 1:
            return input_val[0]
        result = ""
        for gram in input_val[:-1]:
            result += gram[0]
        last_gram = input_val[-1]
        return result + last_gram
    return input_val # assume it's already a string



def similar(reference_set_size: int, source_set_size: int, mm_score: float) -> float:
    """
    Computes Set-Similarity metric which checks whether two sets R and S are approximately 
    equivalent. Set-Similarity is defined as $similar(R, S) = mm\_score / (|R| + |S| - mm\_score)$.

    Examples
    --------
    ```
    >>> from silkmoth.utils import similar
    >>> similar(3, 3, 3)
    1.0
    >>> similar(3, 3, 1.5)
    0.3333333333333333
    ```

    Args:
        reference_set_size: Size of set R
        source_set_size: Size of set S
        mm_score: Maximum matching score of R and S

    Returns:
        float: Set-Similarity
    """
    return mm_score / (reference_set_size + source_set_size - mm_score)

def contain(reference_set_size: int, source_set_size: int, mm_score: float) -> float:
    """
    Computes Set-Containment metric which checks whether one set S is approximately
    a superset of another set R. Set pairs (R, S) with $|R| > |S|$ should be filtered
    in advance. Set-Containment is defined as $contain(R, S) = mm\_score / |R|$.

    Examples
    --------
    ```
    >>> from silkmoth.utils contain
    >>> contain(2, 3, 2)
    1.0
    >>> contain(2, 3, 1.5)
    0.75
    ```

    Args:
        reference_set_size: Size of set R
        source_set_size: Size of set S
        mm_score: Maximum matching score of R and S

    Returns:
        float: Set-Containment
    """
    if reference_set_size > source_set_size:
        raise ValueError(f"Reference set too large")

    return mm_score / reference_set_size

class SigType(Enum):
    """
    Signature type enum.  
    """
    WEIGHTED = "weighted"
    SKYLINE = "skyline"
    DICHOTOMY = "dichotomy"

def get_q_chunks(tokens, q):
    joined = " ".join(tokens)
    chunks = [joined[j:j + q] for j in range(0, len(joined) - q + 1)]
    return chunks