# Run this script with sentence_transformers 2.2.2 and torch 1.13
# torch 2 is producing a different model format
# the output must contains pytorch_model.bin 
from sentence_transformers import SentenceTransformer


modelPath = "./model"
model = SentenceTransformer('all-MiniLM-L6-v2')
model.save(modelPath)

