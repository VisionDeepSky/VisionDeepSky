from datasets import load_dataset, Image

dataset = load_dataset("AI-Lab-Makerere/beans", split="train")
dataset[0]["image"]