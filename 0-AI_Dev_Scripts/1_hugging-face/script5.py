from datasets import load_dataset


dataset_name = "OpenAssistant/oasst2"

# https://huggingface.co/datasets/OpenAssistant/oasst2

# ----------------------------
# Load dataset
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset)

# OUTPUT:
# DatasetDict({
#     train: Dataset({
#         features: ['message_id', 'parent_id', 'user_id', 'created_date', 'text', 'role', 'lang', 'review_count', 'review_result', 'deleted', 'rank', 'synthetic', 'model_name', 'detoxify', 'message_tree_id', 'tree_state', 'emojis', 'labels'],
#         num_rows: 128575
#     })
#     validation: Dataset({
#         features: ['message_id', 'parent_id', 'user_id', 'created_date', 'text', 'role', 'lang', 'review_count', 'review_result', 'deleted', 'rank', 'synthetic', 'model_name', 'detoxify', 'message_tree_id', 'tree_state', 'emojis', 'labels'],
#         num_rows: 6599
#     })
# })

# ----------------------------
# PRINT 100 ROWS IN DATASET
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset["train"][:2])

# OUTPUT:
# {
#     "message_id": [
#         "<MESSAGE_ID_1>",
#         "<MESSAGE_ID_2>",
#     ],
#     "parent_id": [
#         "<PARENT_ID_1>",
#         "<PARENT_ID_2>",
#     ],
#     ...
#     "labels": [
#         ...
#     ],
# }
