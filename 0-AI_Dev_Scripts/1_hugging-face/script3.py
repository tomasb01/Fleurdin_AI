from datasets import load_dataset


dataset_name = "mlabonne/guanaco-llama2-1k"

# https://huggingface.co/datasets/mlabonne/guanaco-llama2-1k

# ----------------------------
# Load dataset
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset)

print(dataset["train"])

dataset = load_dataset(dataset_name, split="train")
print(dataset)

# OUTPUT:
# DatasetDict({
#     train: Dataset({
#         features: ['text'],
#         num_rows: 1000
#     })
# })

# ----------------------------
# Train test split
# ----------------------------
dataset = dataset["train"].train_test_split(test_size=0.2)
print(dataset)

# ----------------------------
# PRINT 100 ROWS IN DATASET
# ----------------------------
print(dataset["train"][:2])

# OUTPUT:
# {
#     "text": [
#         "<TEXT_1>",
#         "<TEXT_2>",
#         "<TEXT_3>",
#         "...",
#         "<TEXT_100>",
#     ],
# }
