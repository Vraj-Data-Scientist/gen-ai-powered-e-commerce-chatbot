import os
import sys

try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import chromadb
from chromadb.utils import embedding_functions
from groq import Groq, APIStatusError
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import time
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

faqs_path = Path(__file__).parent / "resources" / "faq_data.csv"

chroma_client = chromadb.PersistentClient(path="./chroma_db")
groq_client = Groq()

collection_name_faq = "faqs"
collection_initialized = False
faq_collection = None


def ingest_faq_data(path, collection_name="faqs"):
    global collection_initialized, faq_collection

    if collection_initialized:
        logging.info(f"Collection '{collection_name}' already initialized.")
        return True, faq_collection

    try:
        # Check if collection already exists
        existing_collections = [
            c.name for c in chroma_client.list_collections()
        ]

        if collection_name in existing_collections:
            faq_collection = chroma_client.get_collection(
                name=collection_name,
                embedding_function=ef
            )
            logging.info(f"Collection '{collection_name}' already exists.")
            collection_initialized = True
            return True, faq_collection

        # Create new collection
        logging.info(f"Creating collection '{collection_name}'...")

        faq_collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=ef
        )

        if not os.path.exists(path):
            raise FileNotFoundError(f"FAQ file not found: {path}")

        df = pd.read_csv(path)

        docs = df["question"].tolist()
        metadata = [{"answer": ans} for ans in df["answer"].tolist()]
        ids = [f"id_{i}" for i in range(len(docs))]

        faq_collection.add(
            documents=docs,
            metadatas=metadata,
            ids=ids
        )

        logging.info("FAQ data successfully ingested.")

        collection_initialized = True
        return True, faq_collection

    except Exception as e:
        logging.error(f"FAQ ingestion failed: {e}")
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
    prompt = f"""
Given the following context and question, answer ONLY from the context.

If the answer is not present, reply exactly:

Can you please ask relevant questions either FAQs or questions about products.

CONTEXT:
{context}

QUESTION:
{query}
"""

    for attempt in range(max_retries):
        try:
            completion = groq_client.chat.completions.create(
                model=os.environ["GROQ_MODEL"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=512
            )

            return completion.choices[0].message.content

        except APIStatusError as e:
            if e.status_code == 503:
                if attempt < max_retries - 1:
                    logging.warning(
                        f"503 received. Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return "Sorry, the FAQ service is temporarily unavailable. Please try again later."
            else:
                raise

    return "Sorry, the FAQ service is temporarily unavailable. Please try again later."


def faq_chain(query):
    result = get_relevant_qa(query)

    context = "".join(
        [item.get("answer", "") for item in result["metadatas"][0]]
    )

    if not context:
        return "Can you please ask relevant questions either FAQs or questions about products."

    print("Context:", context)

    answer = generate_answer(query, context)

    return answer


if __name__ == "__main__":
    ingest_faq_data(faqs_path, chroma_client, ef)

    query = "Do you accept cash as a payment option?"

    answer = faq_chain(query)

    print(answer)
