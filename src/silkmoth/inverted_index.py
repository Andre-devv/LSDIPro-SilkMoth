
class InvertedIndex:

    def __init__(self, token_sets: list):
        """
        Initialize the inverted index.

        Args:
            token_sets (list): Collection of (tokenized) sets
        """
        self.token_sets = token_sets
        self.lookup_table = dict()
        for set_idx, token_set in enumerate(self.token_sets):
            for element_idx, tokens in enumerate(token_set):
                for token in tokens:
                    if not token in self.lookup_table:
                        self.lookup_table[token] = [(set_idx, element_idx)]
                    # avoid duplicates in inverted list
                    elif self.lookup_table[token][-1] != (set_idx, element_idx):
                        self.lookup_table[token].append((set_idx, element_idx))

    def keys(self):
        """
        Gives all tokens similar like dict.keys().

        Returns:
            set: A set-like object providing all keys
        """
        return self.lookup_table.keys()

    def __getitem__(self, token) -> list:
        """
        Access inverted list from inverted index using square brackets.

        Args:
            token: Input token

        Returns:
            list: A list of all (set, element) tuples which contain the input 
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
            token: Input token
        
        Returns:
            list: A list of all (set index, element index) tuples for (set, 
            element) tuples which contain the input tuple
        """
        if not token in self.lookup_table:
            raise ValueError(f"Unknown token") 
        return self.lookup_table[token] 
    
    def get_set(self, set_id: int) -> list:
        """
        Access (tokenized) set from set id.

        Args:
            set_id: Set id

        Returns:
            list: Tokenized set
        """
        if set_id < 0 or set_id >= len(self.token_sets):
            raise ValueError(f"Invalid id")
        return self.token_sets[set_id]
    
    
