from datasets import load_dataset


dataset_name = "Open-Orca/SlimOrca"

# https://huggingface.co/datasets/Open-Orca/SlimOrca

# ----------------------------
# Load dataset
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset)

# OUTPUT:
# DatasetDict({
#     train: Dataset({
#         features: ['conversations'],
#         num_rows: 517982
#     })
# })

# ----------------------------
# PRINT 100 ROWS IN DATASET
# ----------------------------
dataset = load_dataset(dataset_name)
print(dataset["train"][:2])

# OUTPUT:
# {
#     "conversations": [
#         [
#             {
#                 "from": "system",
#                 "value": "You are an AI assistant. You will be given a task. You must generate a detailed and long answer.",
#                 "weight": 0,
#             },
#             {
#                 "from": "human",
#                 "value": "Write an article based on this  man has been charged with murder and attempted murder after a woman and the man she was on a date with were stabbed at a restaurant in Sydney, Australia.",
#                 "weight": 0.0,
#             },
#             {
#                 "from": "gpt",
#                 "value": "Title: Tragedy Strikes in Sydney: Victims Stabbed during Dinner Date, Suspect Charged with Murder and Attempted Murder\n\nIntroduction\n\nA seemingly ordinary evening took a tragic turn in Sydney, Australia when a romantic dinner date at a local restaurant ended in bloodshed, as a man allegedly attacked a couple, stabbing both victims. Local authorities have charged the suspect with murder and attempted murder in connection with the horrific crime. In this article, we delve into the chilling incident, the suspect, and the impact it has had on the community.",
#                 "weight": 1.0,
#             },
#         ],
#         ...
#     ]
# }
