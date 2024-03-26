# Run this script with sentence_transformers 2.2.2 and torch 1.13
# torch 2 is producing a different model format
# the output must contains pytorch_model.bin 
import sys
import os
from sentence_transformers import SentenceTransformer

assert sys.version_info >= (3, 8), "Use Python 3.8."
assert sys.version_info < (3, 9), "Use Python 3.8."


modelname = os.environ["MODEL_NAME"] if "MODEL_NAME" in os.environ else "all-MiniLM-L6-v2"
from sentence_transformers import SentenceTransformer

modelPath = "./model"
model = SentenceTransformer('all-MiniLM-L6-v2')
model.save(modelPath)
print(f"Model '{modelname}' saved to {modelPath} folder.")

