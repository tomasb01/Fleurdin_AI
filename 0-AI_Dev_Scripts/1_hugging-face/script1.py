from datasets import load_dataset


dataset_name = "lavita/ChatDoctor-HealthCareMagic-100k"

# https://huggingface.co/datasets/lavita/ChatDoctor-HealthCareMagic-100k


# ----------------------------
# Load dataset
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset)

# OUTPUT:
# DatasetDict(
#     {train: Dataset({features: ["instruction", "input", "output"], num_rows: 112165})}
# )

# ----------------------------
# Select one specific sub-dataset (property on the DatasetDict object)
# ----------------------------

# select train dataset (property on the DatasetDict object)
dataset = load_dataset(dataset_name, split="train")
print(dataset)

# OUTPUT:
# Dataset({features: ["instruction", "input", "output"], num_rows: 112165})

# ----------------------------
# Train test split
# ----------------------------
dataset = dataset.train_test_split(test_size=0.2)
print(dataset)

# OUTPUT:
# DatasetDict({
#     train: Dataset({
#         features: ['instruction', 'input', 'output'],
#         num_rows: 100948
#     })
#     test: Dataset({
#         features: ['instruction', 'input', 'output'],
#         num_rows: 11217
#     })
# })


# ----------------------------
# PRINT 2 ROWS IN DATASET
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset["train"][:2])

# OUTPUT:
# {
#     "instruction": [
#         "<SYSTEM_MESSAGE_1>",
#         "<SYSTEM_MESSAGE_2>",
#         "<SYSTEM_MESSAGE_3>",
#         "...",
#         "<SYSTEM_MESSAGE_100>",
#     ],
#     "input": ["<INPUT_1>", "<INPUT_2>", "<INPUT_3>", "...", "<INPUT_100>"],
#     "output": ["<OUTPUT_1>", "<OUTPUT_2>", "<OUTPUT_3>", "...", "<OUTPUT_100>"],
# }
