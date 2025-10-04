import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

def create_index():
    """
    Lê os artigos, gera embeddings para o conteúdo e salva um índice FAISS
    e os textos correspondentes.
    """
    print("Carregando dados...")
    data = []
    with open('output/pmc_articles_html.jsonl', 'r') as f:
        for line in f:
            data.append(json.loads(line))

    print("Preparando textos...")
    texts = []
    for article in data:
        # Combinar título, resumo e seções em um único texto por artigo
        title = article.get('title') or ""
        abstract = article.get('abstract') or ""
        content = title + " " + abstract
        for section in article.get('sections', []):
            content += " " + (section.get('text') or "")
        texts.append(content)

    print("Carregando modelo de embedding...")
    # Usaremos um modelo pré-treinado para gerar os embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Gerando embeddings...")
    # Gera os embeddings para todos os textos
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().numpy()

    # Normalizar embeddings para busca de similaridade de cosseno
    faiss.normalize_L2(embeddings)

    # Criar o índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension) # IP = Inner Product (similaridade de cosseno em vetores normalizados)
    index.add(embeddings)

    print("Salvando o índice e os textos...")
    # Criar diretório se não existir
    os.makedirs('rag_index', exist_ok=True)
    
    # Salvar o índice FAISS
    faiss.write_index(index, 'rag_index/articles.index')

    # Salvar os textos para referência futura
    with open('rag_index/texts.json', 'w') as f:
        json.dump(texts, f)

    print("Indexação concluída!")

if __name__ == "__main__":
    create_index()
