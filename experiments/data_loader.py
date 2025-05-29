import random
import os

from utils import *


class DataLoader:
    def __init__(self, data_path):
        if data_path is None:
            raise ValueError("data_path must be set")

        if not os.path.exists(data_path):
            raise ValueError(f"data_path does not exist: {data_path}")

        self.data_path = data_path
        self.files = os.listdir(data_path)

    def load_webtable_columns_randomized(self, reference_set_amount: int, source_set_amount: int) -> tuple[list, list]:
        """
        Get randomized reference sets and source sets of webtable columns.
        Reference sets are subsets of the source sets.
        Only columns with 4 or more different elements are considered.
        Only considering columns with non-numeric values.

        Args:
            reference_set_amount (int): Number of reference sets to return.
            source_set_amount (int): Number of source sets to return.
        Returns:
            tuple: A tuple containing a list of reference sets and a list of source sets.
        """
        # Basic validation of input parameters
        if reference_set_amount < 1 or source_set_amount < 2:
            raise ValueError("reference_set_amount must be at least 1 and source_set_amount must be at least 2")
        if reference_set_amount >= source_set_amount:
            raise ValueError("reference_set_amount must be smaller than source_set_amount")
        if reference_set_amount > len(self.files):
            raise ValueError("reference_set_amount must be smaller than the number of files in data_path")
        if source_set_amount > len(self.files):
            raise ValueError("source_set_amount must be smaller than the number of files in data_path")
        if len(self.files) == 0:
            raise ValueError("data_path does not contain any files")


        # Randomly select a reference set and source sets
        source_set_nums = random.sample(range(len(self.files)), source_set_amount)

        # Pick source_set_amount of columns which have at least 4 different elements
        source_sets = []
        while len(source_sets) < source_set_amount:
            # Pick a random number from the source_set_nums
            source_set_num = random.choice(source_set_nums)
            file_path = os.path.join(self.data_path, self.files[source_set_num])

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                    if "relation" in json_data and isinstance(json_data["relation"], list):
                        # pick random column
                        col = random.randint(0, len(json_data["relation"]) - 1)
                        col = json_data["relation"][col]

                        # Check if the column has at least 4 different elements and contains no numeric values
                        if len(set(col)) >= 4:
                            if all(not is_convertible_to_number(value) and len(value) > 0 for value in col):
                                # Add the column to the source sets
                                source_sets.append(col)
                            print(f"Source set number {len(source_sets)} loaded")

            except Exception as e:
                raise ValueError(f"Error loading JSON file: {e}")

        # Randomly select reference sets from the source sets
        reference_sets = random.sample(source_sets, reference_set_amount)
        return reference_sets, source_sets

    def load_webtable_schemas_randomized(self, source_set_amount: int) -> tuple[list, list]:
        if source_set_amount < 2:
            raise ValueError("source_set_amount must be at least 2")
        # Randomly select a reference set and source sets
        reference_set_num = random.randint(0, len(self.files) - 1)
        source_set_nums = random.sample(range(len(self.files)), source_set_amount)

        # Make sure that reference_set differs from source_sets
        while reference_set_num in source_set_nums:
            reference_set_num = random.randint(0, len(self.files) - 1)

        # Get schema for the reference set
        reference_set = self.load_webtable_schema(reference_set_num)
        if reference_set is []:
            raise ValueError("chosen reference_set is empty")

        source_sets = []
        for i in source_set_nums:
            source_set = self.load_webtable_schema(i)
            source_sets.append(source_set)

        return reference_set, source_sets

    def load_webtable_schema(self, reference_set_num: int) -> list:
        # Load the webtable schema for the given reference set number
        if reference_set_num < 0 or reference_set_num >= len(self.files):
            raise IndexError("reference_set_num is out of range")

        # Get the file at the specified position
        file_path = os.path.join(self.data_path, self.files[reference_set_num])

        # Load and return the JSON content
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                if "relation" in json_data and isinstance(json_data["relation"], list):
                    schema = [relation[0] for relation in json_data["relation"]]
                    return schema
                else:
                    return []
        except Exception as e:
            raise ValueError(f"Error loading JSON file: {e}")
