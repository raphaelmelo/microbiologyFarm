import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

def create_index():
    """
    Lê os artigos, gera embeddings para o conteúdo e salva um índice FAISS
    e os textos correspondentes, processando um artigo de cada vez para
    economizar memória.
    """
    print("Carregando modelo de embedding...")
    model = SentenceTransformer('all-mpnet-base-v2')
    dimension = model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatIP(dimension)
    
    all_texts = []
    
    print("Iniciando processamento de artigos em modo streaming...")
    with open('output/pmc_articles_html.jsonl', 'r') as f:
        for i, line in enumerate(f):
            article = json.loads(line)
            
            # Combinar título, resumo e seções em um único texto por artigo
            title = article.get('title') or ""
            abstract = article.get('abstract') or ""
            content = title + " " + abstract
            for section in article.get('sections', []):
                content += " " + (section.get('text') or "")
            
            all_texts.append(content)
            
            # Gerar embedding para o artigo atual
            print(f"Processando artigo {i+1}...")
            embedding = model.encode([content], convert_to_tensor=True, show_progress_bar=False)
            embedding = embedding.cpu().numpy()
            
            # Normalizar e adicionar ao índice
            faiss.normalize_L2(embedding)
            index.add(embedding)

    print("Salvando o índice e os textos...")
    os.makedirs('rag_index', exist_ok=True)
    faiss.write_index(index, 'rag_index/articles.index')

    print("Salvando o modelo de embedding localmente...")
    model.save('rag_index/model')

    with open('rag_index/texts.json', 'w') as f:
        json.dump(all_texts, f)

    print("Indexação concluída!")

if __name__ == "__main__":
    create_index()
