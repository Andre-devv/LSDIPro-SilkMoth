import os
import json
import random


class DataLoader:
    def __init__(self, data_path=os.getenv("SILKMOTH_DATA_PATH", None)):
        if data_path is None:
            raise ValueError("data_path must be set")

        if not os.path.exists(data_path):
            raise ValueError(f"data_path does not exist: {data_path}")

        self.data_path = data_path
        self.files = os.listdir(data_path)

    def load_webtable_schema_for_search(self, reference_set_num: int, source_sets_nums: list[int]) -> tuple[list, list]:
        if len(source_sets_nums) != 2:
            raise ValueError("source_sets_nums must contain exactly two elements: start_num and end_num")

        start_num, end_num = source_sets_nums
        if start_num < 0 or end_num < 0 or start_num > end_num:
            raise ValueError("source_sets_nums must be non-negative and start_num must be less than or equal to end_num")

        if start_num <= reference_set_num <= end_num:
            raise ValueError("reference_set_num must be outside the range of source_sets_nums")

        # Get schema for the reference set
        reference_set = self.load_webtable_schema(reference_set_num)
        if reference_set is []:
            raise ValueError("chosen reference_set is empty")

        source_sets = []
        for i in range(start_num, end_num + 1):
            source_set = self.load_webtable_schema(i)
            source_sets.append(source_set)


        return reference_set, source_sets

    def load_webtable_schema_for_search_randomized(self, source_set_amount: int) -> tuple[list, list]:
        if source_set_amount < 2:
            raise ValueError("source_set_amount must be at least 2")
        # Randomly select a reference set and source sets
        reference_set_num = random.randint(0, len(self.files) - 1)
        source_set_nums = random.sample(range(len(self.files)), source_set_amount)

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
