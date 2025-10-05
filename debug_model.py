import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from sentence_transformers import SentenceTransformer

try:
    print("Carregando o modelo 'all-mpnet-base-v2'...")
    model = SentenceTransformer('all-mpnet-base-v2')
    print("Modelo carregado com sucesso.")

    print("Codificando uma frase de teste...")
    sentence = ["Esta é uma frase de teste."]
    embedding = model.encode(sentence)
    print("Frase codificada com sucesso.")
    print("Vetor de embedding:", embedding)

    print("\nO ambiente parece ser capaz de lidar com o modelo.")

except Exception as e:
    print(f"\nOcorreu um erro: {e}")

