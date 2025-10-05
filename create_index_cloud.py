import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from google.cloud import storage
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Configurações
BUCKET_NAME = "microbiologyfarm-app-bucket"
SOURCE_FILE = "pmc_articles_html.jsonl"
DESTINATION_INDEX_FOLDER = "rag_index"

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """Faz o download de um arquivo do Google Cloud Storage."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        
        logging.info(f"Fazendo download do arquivo {source_blob_name} do bucket {bucket_name}...")
        blob.download_to_filename(destination_file_name)
        logging.info(f"Download de {destination_file_name} concluído.")
    except Exception as e:
        logging.error(f"Falha no download do arquivo {source_blob_name}: {e}")
        raise

def upload_to_gcs(bucket_name, source_folder, destination_blob_prefix):
    """Faz o upload de uma pasta para o Google Cloud Storage."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        for root, _, files in os.walk(source_folder):
            for file in files:
                local_path = os.path.join(root, file)
                gcs_path = os.path.join(destination_blob_prefix, os.path.relpath(local_path, source_folder))
                
                logging.info(f"Fazendo upload de {local_path} para {gcs_path} no bucket {bucket_name}...")
                blob = bucket.blob(gcs_path)
                blob.upload_from_filename(local_path)
                logging.info(f"Upload de {file} concluído.")
    except Exception as e:
        logging.error(f"Falha no upload da pasta {source_folder}: {e}")
        raise

def create_index_cloud():
    """
    Processo completo de indexação na nuvem:
    1. Faz download dos dados do GCS.
    2. Gera os embeddings e o índice FAISS.
    3. Faz upload do índice e do modelo de volta para o GCS.
    """
    # 1. Download dos dados
    os.makedirs("output", exist_ok=True)
    local_source_file = os.path.join("output", SOURCE_FILE)
    download_from_gcs(BUCKET_NAME, f"data/{SOURCE_FILE}", local_source_file)

    # 2. Lógica de indexação (similar ao script local)
    logging.info("Carregando dados do arquivo local...")
    data = []
    with open(local_source_file, 'r') as f:
        for line in f:
            data.append(json.loads(line))

    logging.info("Preparando textos...")
    texts = []
    for article in data:
        title = article.get('title', "")
        abstract = article.get('abstract', "")
        content = title + " " + abstract
        for section in article.get('sections', []):
            content += " " + section.get('text', "")
        texts.append(content)

    logging.info("Carregando modelo de embedding 'all-mpnet-base-v2'...")
    model = SentenceTransformer('all-mpnet-base-v2')

    logging.info("Gerando embeddings...")
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    embeddings = embeddings.cpu().numpy()

    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    logging.info("Salvando o índice e os textos localmente...")
    os.makedirs(DESTINATION_INDEX_FOLDER, exist_ok=True)
    faiss.write_index(index, os.path.join(DESTINATION_INDEX_FOLDER, 'articles.index'))
    
    with open(os.path.join(DESTINATION_INDEX_FOLDER, 'texts.json'), 'w') as f:
        json.dump(texts, f)

    logging.info("Salvando o modelo de embedding localmente...")
    model.save(os.path.join(DESTINATION_INDEX_FOLDER, 'model'))

    # 3. Upload do resultado para o GCS
    logging.info("Fazendo upload da pasta de índice para o GCS...")
    upload_to_gcs(BUCKET_NAME, DESTINATION_INDEX_FOLDER, DESTINATION_INDEX_FOLDER)

    logging.info("Processo de indexação na nuvem concluído com sucesso!")

if __name__ == "__main__":
    create_index_cloud()
