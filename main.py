import json
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = FastAPI()

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class Answer(BaseModel):
    answer: str
    context: str

# --- Carregamento dos modelos e dados ---
@app.on_event("startup")
async def startup_event():
    """
    Carrega todos os modelos e dados necessários na inicialização do servidor.
    """
    print("Configurando a API do Google Gemini...")
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        genai.configure(api_key=api_key)
        app.state.gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        print("Modelo Gemini configurado com sucesso: gemini-2.0-flash-lite")
    except Exception as e:
        print(f"Erro ao configurar o Gemini: {e}")
        app.state.gemini_model = None

    print("Carregando textos para RAG...")
    try:
        with open('rag_index/texts.json', 'r') as f:
            app.state.texts = json.load(f)
    except FileNotFoundError:
        print("Arquivo texts.json não encontrado. Execute create_index.py primeiro.")
        app.state.texts = []

    print("Carregando índice FAISS...")
    try:
        app.state.index = faiss.read_index('rag_index/articles.index')
    except RuntimeError:
        print("Arquivo articles.index não encontrado. Execute create_index.py primeiro.")
        app.state.index = None

    print("Carregando modelo de embedding...")
    app.state.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("--- Modelos e dados carregados com sucesso! ---")


# --- Endpoints da API ---
@app.post("/ask", response_model=Answer)
def ask(request: QueryRequest):
    question = request.question
    top_k = request.top_k

    if not all([app.state.model, app.state.index, app.state.texts, app.state.gemini_model]):
        return Answer(
            answer="Erro: Um ou mais componentes (modelo, índice, textos, Gemini) não foram carregados corretamente.",
            context=""
        )

    # 1. Encode the user's question
    question_embedding = app.state.model.encode(question, convert_to_tensor=True)

    # 2. Search the FAISS index
    distances, indices = app.state.index.search(question_embedding.cpu().numpy().reshape(1, -1), top_k)

    # 3. Retrieve and refine context
    retrieved_texts = [app.state.texts[i] for i in indices[0]]
    paragraphs = []
    for text in retrieved_texts:
        paragraphs.extend(text.split('\n\n'))
    
    paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 100]

    if not paragraphs:
        return Answer(answer="Não foi possível encontrar um contexto relevante para a pergunta.", context="")

    paragraph_embeddings = app.state.model.encode(paragraphs, convert_to_tensor=True)
    similarities = util.cos_sim(question_embedding, paragraph_embeddings)[0]
    top_para_indices = similarities.argsort(descending=True)[:3]
    final_context = "\n\n".join([paragraphs[i] for i in top_para_indices])

    # 4. Generate answer with Gemini
    prompt = f"""
    Com base no contexto científico abaixo, responda à pergunta do usuário.
    Se a resposta não estiver no contexto, diga "A informação não foi encontrada no contexto fornecido".
    Seja claro e direto.

    Contexto:
    ---
    {final_context}
    ---

    Pergunta: {question}

    Resposta:
    """

    try:
        response = app.state.gemini_model.generate_content(prompt)
        gemini_answer = response.text
    except Exception as e:
        gemini_answer = f"Erro ao gerar resposta com o Gemini: {e}"

    return Answer(answer=gemini_answer, context=final_context)

