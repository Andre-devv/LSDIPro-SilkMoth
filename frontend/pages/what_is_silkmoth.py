import streamlit as st

st.title("What is SilkMoth?")
st.markdown("""
The **SilkMoth Engine** is a powerful framework designed for **efficiently discovering relationships and similarities among large collections of data sets.**

It operates by:

1.  **Treating each data collection as a "set"** comprised of unique "elements."
2.  **Applying advanced similarity metrics and optimized algorithms** to compare these sets.
3.  **Identifying "related" sets** based on a user-defined similarity threshold.

This enables the rapid identification of connections within vast amounts of data, making it crucial for tasks like data organization, integration, and uncovering hidden insights.
""")
st.divider()
st.title("🔁 Core Pipeline Steps")

st.image("docs/figures/Pipeline.png", caption="Figure 1: SILKMOTH Framework Overview. Source: Deng et al., 'SILKMOTH: An Efficient Method for Finding Related Sets with Maximum Matching Constraints', VLDB 2017. Licensed under CC BY-NC-ND 4.0.")

st.subheader("1. Tokenization")
st.markdown("""
Each element in every set is tokenized based on the selected similarity function:
- **Jaccard Similarity**: Elements are split into whitespace-delimited tokens.
- **Edit Similarity**: Elements are split into overlapping `q`-grams (e.g., 3-grams).
""")

st.subheader("2. Inverted Index Construction")
st.markdown("""
An **inverted index** is built from the reference set `R` to map each token to a list of `(set, element)` pairs in which it occurs. This allows fast lookup of candidate sets that share tokens with a query.
""")

st.subheader("3. Signature Generation")
st.markdown("""
A **signature** is a subset of tokens selected from each set such that:
- Any related set must share at least one signature token.
- Signature size is minimized to reduce candidate space.

**Signature selection heuristics** (e.g., cost/value greedy ranking) are used to approximate the optimal valid signature, which is NP-complete to compute exactly.
""")

st.subheader("4. Candidate Selection")
st.markdown("""
For each set `R`, we retrieve from the inverted index all sets `S` that share at least one token with `R`’s signature. These become the **candidate sets** for further evaluation.
""")

st.subheader("5. Refinement Filters")
st.markdown("""
Two filters reduce false positives among the candidates:

- **Check Filter**: Uses an upper bound on similarity to eliminate sets that cannot meet the threshold.
- **Nearest Neighbor Filter**: Approximates the maximum matching score using the nearest neighbor similarity for each element in `R`.
""")

st.subheader("6. Verification via Maximum Matching")
st.markdown("""
For the remaining candidates, we compute the **maximum weighted bipartite matching** between elements of `R` and `S`, using the chosen similarity function as edge weights.

Only sets whose matching score meets or exceeds a threshold `δ` are considered **related**.
""")

st.markdown("---")

st.subheader("🧪 Modes of Operation")
st.markdown("""
- **Discovery Mode**: Compare all pairs of sets to find all related set pairs.  
  **Use Case**: When you want to check which sets (e.g., columns in a database) are related to a specific reference set.
- **Search Mode**: Given a reference set, find all sets related to it.  
  **Use Case**: When you want to find all related set pairs in a dataset, for tasks like schema matching or entity deduplication.
""")

st.markdown("---")

st.subheader("📐 Supported Similarity Functions")
st.markdown("""
- **Jaccard Similarity**
- **Edit Similarity** (Levenshtein-based)
- Optional **minimum similarity threshold** `α` can be enforced on element comparisons.
""")