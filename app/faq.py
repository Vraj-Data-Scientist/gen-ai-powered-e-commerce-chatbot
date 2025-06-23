import os
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
from chromadb.utils import embedding_functions
from chromadb.errors import NotFoundError
from groq import Groq, APIStatusError
import pandas
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)
faqs_path = Path(__file__).parent / "resources/faq_data.csv"
chroma_client = chromadb.PersistentClient(path="./chroma_db")
groq_client = Groq()
collection_name_faq = 'faqs'
collection_initialized = False
faq_collection = None  # Cache collection object

def ingest_faq_data(path):
    global collection_initialized, faq_collection
    if collection_initialized:
        print(f"Collection: {collection_name_faq} already exists (cached)")
        return
    
    try:
        faq_collection = chroma_client.get_collection(name=collection_name_faq, embedding_function=ef)
        print(f"Collection: {collection_name_faq} already exists")
        collection_initialized = True
    except NotFoundError:
        print("Ingesting FAQ data into Chromadb...")
        try:
            faq_collection = chroma_client.create_collection(
                name=collection_name_faq,
                embedding_function=ef
            )
            df = pandas.read_csv(path)
            docs = df['question'].to_list()
            metadata = [{'answer': ans} for ans in df['answer'].to_list()]
            ids = [f"id_{i}" for i in range(len(docs))]
            faq_collection.add(
                documents=docs,
                metadatas=metadata,
                ids=ids
            )
            print(f"FAQ Data successfully ingested into Chroma collection: {collection_name_faq}")
            collection_initialized = True
        except FileNotFoundError:
            print(f"Error: FAQ data file not found at {path}")
            raise
        except Exception as e:
            print(f"Error during FAQ ingestion: {type(e).__name__} - {str(e)}")
            raise

def get_relevant_qa(query):
    global faq_collection
    if faq_collection is None:
        faq_collection = chroma_client.get_collection(
            name=collection_name_faq,
            embedding_function=ef
        )
    result = faq_collection.query(
        query_texts=[query],
        n_results=2
    )
    return result

def generate_answer(query, context, max_retries=3, retry_delay=1):
    prompt = f'''Given the following context and question or statement, generate answer based on this context only.
    If the answer is not found in the context, kindly state "Can you please ask relevant questions either FAQs or questions about products". Don't try to make up an answer.
    
    CONTEXT: {context}
    
    QUESTION: {query}
    '''
    for attempt in range(max_retries):
        try:
            completion = groq_client.chat.completions.create(
                model=os.environ['GROQ_MODEL'],
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=512
            )
            return completion.choices[0].message.content
        except APIStatusError as e:
            if e.status_code == 503:
                if attempt < max_retries - 1:
                    print(f"503 error on attempt {attempt + 1}, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return "Sorry, the FAQ service is temporarily unavailable. Please try again later."
            else:
                raise e
    return "Sorry, the FAQ service is temporarily unavailable. Please try again later."

def faq_chain(query):
    result = get_relevant_qa(query)
    context = "".join([r.get('answer', '') for r in result['metadatas'][0]])
    if not context:
        return "Can you please ask relevant questions either FAQs or questions about products?"
    print("Context:", context)
    answer = generate_answer(query, context)
    return answer

if __name__ == '__main__':
    ingest_faq_data(faqs_path)
    query = "Do you accept cash as a payment option?"
    result = get_relevant_qa(query)
    answer = faq_chain(query)
    print("Answer:", answer)
