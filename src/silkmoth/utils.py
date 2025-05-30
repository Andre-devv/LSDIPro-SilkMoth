

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