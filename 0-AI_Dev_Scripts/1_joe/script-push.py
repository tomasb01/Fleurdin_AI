from datasets import load_dataset, Dataset, DatasetDict

dataset = load_dataset("json", data_files="data/all.json")
print(dataset)

# Get the number of rows
# print(len(dataset["train"]))

# Get the first 2 rows
# print(dataset["train"][:2])


# MAP FUNCTION ------------------------------------------

# For each example, calculate the length of the text
def calculate_length(example):
    example["length"] = len(example["text"])
    return example


newDataset = dataset.map(calculate_length)
print(newDataset["train"][:5]["length"])


# def change_length(example):
#     example["text"] = example["text"][:10]
#     return example


# newDataset = dataset.map(change_length)
# print(newDataset)
# print(newDataset["train"][:2])


# PANDAS ------------------------------------------

# # to pandas
# df_train = newDataset["train"].to_pandas()
# print(df_train)

# # from pandas
# new_dataset = Dataset.from_pandas(df_train)
# new_datasets = DatasetDict({"train": new_dataset})

# print(new_datasets)
# print(new_datasets["train"])
# print(new_datasets["train"][:1])


# PUSH ------------------------------------------

# Push to HuggingFace1
newDataset.push_to_hub("lukaskellerstein/joe-small")
