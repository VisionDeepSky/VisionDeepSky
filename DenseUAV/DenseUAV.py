from datasets import load_dataset, Image
from itertools import islice

ds = load_dataset("layumi/university-1652", split="train", streaming=True)

ds.features