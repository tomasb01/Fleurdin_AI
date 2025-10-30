from datasets import load_dataset, Dataset, DatasetDict
from huggingface_hub import login

# PRIHLASENI K HUGGINGFACE
# Nutne pro push_to_hub - spusti to jednou a zadej svuj token
# Token ziskas zde: https://huggingface.co/settings/tokens
print("Prihlasovani k HuggingFace...")
login()  # Interaktivne te vyzve k zadani tokenu

# NACTENI DATASETU
# Dataset je ve stejne slozce jako skript
dataset = load_dataset("json", data_files="EO_dataset_huggingface.json")
print(dataset)

# Get the number of rows
print(f"Pocet zaznamu: {len(dataset['train'])}")

# Get the first 2 rows
print("\nPrvni 2 zaznamy:")
print(dataset["train"][:2])


# MAP FUNCTION ------------------------------------------

# For each example, calculate the length of the text
def calculate_length(example):
    example["length"] = len(str(example["text"]))
    return example


newDataset = dataset.map(calculate_length)
print("\nDataset s delkou textu:")
print(newDataset["train"][:2])


# def change_length(example):
#     example["text"] = example["text"][:3]
#     return example


# newDataset = dataset.map(change_length)
# print(newDataset)
# print(newDataset["train"][:2])


# PANDAS ------------------------------------------

# # to pandas
# df_train = dataset["train"].to_pandas()
# print(df_train)

# # from pandas
# new_dataset = Dataset.from_pandas(df_train)
# new_datasets = DatasetDict({"train": new_dataset})

# print(new_datasets)
# print(new_datasets["train"])
# print(new_datasets["train"][:1])


# PUSH ------------------------------------------

# Push to HuggingFace
# POZOR: Uprav nazev repozitare na sve HuggingFace jmeno!
# Format: "tve_jmeno/nazev_datasetu"
print("\nNahravani datasetu na HuggingFace...")
dataset.push_to_hub("TomasBo/Fleurdin")

print("\nHOTOVO! Dataset byl nahrán.")
print("Zkontroluj ho na: https://huggingface.co/datasets/TomasBo/Fleurdin")
