from enum import Enum
from rapidfuzz.distance import Levenshtein

def jaccard_similarity(x: set, y: set, sim_thresh=0) -> float:
    """
    Gives the Jaccard similarity of two set-like objects.

    Args:
        x (set): Input element x
        y (set): Input element y
        sim_thresh: Similarity threshold alpha

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
        
            Eds(x, y) = 1 - (2 * LD(x, y)) / (|x| + |y| + LD(x, y))

        Args:
            x (str or set/list of str): First input
            y (str or set/list of str): Second input
            sim_thresh (float): Similarity threshold alpha (default is 0)

        Returns:
            float: Edit similarity score (0 if below threshold)
        """
    x_str = flatten_tokens(x)
    y_str = flatten_tokens(y)

    if not x_str or not y_str:
        return .0

    ld = Levenshtein.distance(x_str, y_str)
    eds = 1 - (2 * ld) / (len(x_str) + len(y_str) + ld)
    return eds if eds >= sim_thresh else .0

def N_edit_similarity(x, y, sim_thresh=0) -> float:
    """
    Computes the normalized edit similarity NEds between two strings or sets/lists of tokens:
    
        NEds(x, y) = 1 - LD(x, y) / max(|x|, |y|)

    Args:
        x (str or set/list of str): First input
        y (str or set/list of str): Second input
        sim_thresh (float): Similarity threshold (default: 0)

    Returns:
        float: Similarity score in [0, 1], or 0 if below threshold
    """
    x_str = flatten_tokens(x)
    y_str = flatten_tokens(y)

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

def similar(reference_set_size: int, source_set_size: int, mm_score: float) -> float:
    """
    Computes Set-Similarity metric.

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
    Computes Set-Containment metric. Set pairs (R, S) with |R| > |S| should be 
    filtered in advance.

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
    WEIGHTED = "weighted"
    SKYLINE = "skyline"
    DICHOTOMY = "dichotomy"