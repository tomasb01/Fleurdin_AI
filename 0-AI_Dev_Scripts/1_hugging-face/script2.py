from datasets import load_dataset


dataset_name = "mosaicml/instruct-v3"

# https://huggingface.co/datasets/mosaicml/instruct-v3

# ----------------------------
# Load dataset
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset)

# OUTPUT:
# DatasetDict({
#     train: Dataset({
#         features: ['prompt', 'response', 'source'],
#         num_rows: 56167
#     })
#     test: Dataset({
#         features: ['prompt', 'response', 'source'],
#         num_rows: 6807
#     })
# })

# ----------------------------
# PRINT 100 ROWS IN DATASET
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset["train"][:100])

# OUTPUT:
# {
#     "prompt": [
#         "<PROMPT_1>",
#         "<PROMPT_2>",
#         "<PROMPT_3>",
#         "...",
#         "<PROMPT_100>",
#     ],
#     "response": ["<RESPONSE_1>", "<RESPONSE_2>", "<RESPONSE_3>", "...", "<RESPONSE_100>"],
#     "source": ["<SOURCE_1>", "<SOURCE_2>", "<SOURCE_3>", "...", "<SOURCE_100>"],
# }
