from enum import Enum

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
    WEIGHTED = "weighted"
    SKYLINE = "skyline"
    DICHOTOMY = "dichotomy"