import random
import os
import pandas as pd

from utils import *


class DataLoader:
    def __init__(self, data_path):
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

    def load_webtable_schemas_randomized(self, set_amount: int) -> list:
        if set_amount < 2:
            raise ValueError("source_set_amount must be at least 2")
        # Random sequence of table numbers
        table_nums = random.sample(range(len(self.files)), len(self.files))

        schema_sets = []

        i = 0
        while len(schema_sets) < set_amount and i < len(table_nums):
            try:
                # Load the schema for the current table number
                schema = self.load_single_webtable_schema(table_nums[i])
                schema_sets.append(schema)
                print(f"Schema set number {len(schema_sets)} loaded")
                i += 1
            except ValueError as e:
                print(f"Skipping table number {table_nums[i]} due to error: {e}")
                i += 1

        return schema_sets

    def load_single_webtable_schema(self, reference_set_num: int) -> list:
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
                    if len(schema) == 0:
                        raise ValueError("Schema is empty")

                    if all(not is_convertible_to_number(col) for col in schema):
                        # remove "" empty strings from the schema
                        schema = [col for col in schema if len(col) > 0]
                        if len(schema) == 0:
                            raise ValueError("Schema contains only empty strings")
                        return schema
                    else:
                        raise ValueError("Schema contains numeric values or is empty")
                else:
                    raise ValueError("JSON does not contain a valid 'relation' key or it is not a list")
        except Exception as e:
            raise ValueError(f"Error loading JSON file: {e}")
        



    def load_dblp_titles(self, data_path: str) -> list:
        """
        Load DBLP paper titles from a CSV file.

        Args:
            data_path (str): Path to CSV file containing a column 'title'.

        Returns:
            list: A list of title strings.
        """

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"DBLP CSV file not found: {data_path}")
        
        df = pd.read_csv(data_path)
        if "title" not in df.columns:
            raise ValueError("CSV must contain a 'title' column")

        titles = df["title"].dropna().tolist()
        return titles

