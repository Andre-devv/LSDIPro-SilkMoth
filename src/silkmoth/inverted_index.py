import bisect
from silkmoth.utils import jaccard_similarity, edit_similarity, N_edit_similarity

class InvertedIndex:
    """
    The inverted index

    - allows to lookup all appearances of a token in a collection of tokenized sets
    - returns inverted lists consisting of (set, element) tuples
    - supports full sets/elements and positional indexes of them
    - stores source sets in [SilkMothEngine](silkmoth_engine.md)

    The inverted list
    
    - is sorted first by the order of the sets and then by the order of the elements.

    Examples
    --------
    ```
    >>> from silkmoth.inverted_index import InvertedIndex
    >>> S1 = [{"Apple", "Pear", "Car"}, {"Apple", "Sun", "Cat"}]
    >>> S2 = [{"Apple", "Berlin", "Sun"}, {"Apple"}]
    >>> S = [S1, S2]
    >>> I = InvertedIndex(S)
    >>> I.get_indexes("Sun")
    [(0, 1), (1, 0)]
    >>> I["Berlin"]
    [([{'Sun', 'Apple', 'Berlin'}, {'Apple'}], {'Sun', 'Apple', 'Berlin'})]
    ```

    ![SilkMoth Inverted Index](../figures/InvertedIndex.png)

    *SilkMoth Inverted Index. Source: Deng et al., "SILKMOTH: An Efficient Method for Finding Related Sets with Maximum Matching Constraints", VLDB 2017.  
    Licensed under CC BY-NC-ND 4.0.*
    """

    def __init__(self, token_sets: list):
        """
        Initialize the inverted index.

        Args:
            token_sets (list): Collection of tokenized sets
            sim_func (function): Similarity function
        """
        #self.sim_func = sim_func
        self.token_sets = []
        self.lookup_table = dict()

        # if sim_func in (edit_similarity, N_edit_similarity):
        #     # Treat entire token list as a single flat element (preserving order + duplicates)
        #     for set_idx, token_list in enumerate(token_sets):
        #         self.token_sets.append(token_list)
        #         for _, token in enumerate(token_list):
        #             key = (set_idx, 0)  # Only one "element"
        #             if token not in self.lookup_table:
        #                 self.lookup_table[token] = [key]
        #             elif self.lookup_table[token][-1] != key:
        #                 self.lookup_table[token].append(key)

        # elif sim_func == jaccard_similarity:
        #     # Standard Jaccard logic — token_sets is a list of sets of sets
        for set_idx, token_set in enumerate(token_sets):
            self.token_sets.append(token_set)
            for element_idx, tokens in enumerate(token_set):
                for token in tokens:
                    key = (set_idx, element_idx)
                    if token not in self.lookup_table:
                        self.lookup_table[token] = [key]
                    elif self.lookup_table[token][-1] != key:
                        self.lookup_table[token].append(key)
        # else:
        #     raise ValueError("Unsupported similarity function")

    def keys(self):
        """
        Gives all tokens similar like dict.keys().

        Returns:
            set (set): A set-like object providing all keys
        """
        return self.lookup_table.keys()

    def __getitem__(self, token) -> list:
        """
        Access inverted list from inverted index using square brackets.

        Args:
            token (str): Input token

        Returns:
            list:   A list of all (set, element) tuples which contain the input 
                    token.
        """
        idx_list = self.get_indexes(token)
        return [(self.get_set(s), self.get_set(s)[e]) for s, e in idx_list]

    def get_indexes(self, token) -> list:
        """
        Access inverted list of indexes. For some tasks retrieving the full set
        and element pairs might not be necessary and their indexes are 
        sufficient.

        Args:
            token (str): Input token
        
        Returns:
            list:   A list of all (set index, element index) tuples for (set, 
                    element) tuples which contain the input tuple
        """
        if not token in self.lookup_table:
            raise ValueError(f"Unknown token") 
        return self.lookup_table[token] 
    
    def get_set(self, set_id: int) -> list:
        """
        Access (tokenized) set from set ID.

        Args:
            set_id: Set ID

        Returns:
            list: Tokenized set
        """
        if set_id < 0 or set_id >= len(self.token_sets):
            raise ValueError(f"Invalid id")
        return self.token_sets[set_id]
    
    def get_indexes_binary(self, token, set_idx) -> list:
        """
        Uses binary search to get all (set_idx, element_idx) pairs for a token
        where set_idx matches the given set_idx.

        Args:
            token (str): The token to search in the inverted index.
            set_idx (int): The ID of the set we want the element indexes for.

        Returns:
            list: All (set_idx, element_idx) tuples where the token appears in the given set.
        """
        if token not in self.lookup_table:
            raise ValueError("Unknown token")

        index_list = self.lookup_table[token]

        # Using bisect to find the range of entries where set_idx matches
        left = bisect.bisect_left(index_list, (set_idx, -1))
        right = bisect.bisect_right(index_list, (set_idx, float('inf')))
        return index_list[left:right]
    
    def print_index(self):
        """
        Prints the inverted index in a readable format.
        """
        print("=== Inverted Index ===")
        for token, locations in self.lookup_table.items():
            print(f"Token: {token} → Locations: {locations}")