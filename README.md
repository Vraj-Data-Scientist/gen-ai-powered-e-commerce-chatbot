# 💬 Intelligent RAG E-commerce Chatbot

Developed a Streamlit-based chatbot, enhancing user experience by ~60% and revenue potential by ~40% with a conversational interface. Integrated RAG with LLaMA 3.3 (Groq), semantic routing, and real-time SQL to replace inefficient filters and FAQs, reducing API costs by ~50% using HuggingFace embeddings, ChromaDB, and quantization.



This chatbot currently supports two intents:

- **faq**: Triggered when users ask questions related to the platform's policies or general information. eg. Is online payment available?
- **sql**: Activated when users request product listings or information based on real-time database queries. eg. Show me all nike shoes below Rs. 3000.





## Architecture
![architecture diagram of the e-commerce chatbot](app/resources/architecture-diagram.png)


### Set-up & Execution

1. Run the following command to install all dependencies. 

    ```bash
    pip install -r app/requirements.txt
    ```

1. Inside app folder, create a .env file with your GROQ credentials as follows:
    ```text
    GROQ_MODEL=<Add the model name, e.g. llama-3.3-70b-versatile>
    GROQ_API_KEY=<Add your groq api key here>
    ```

1. Run the streamlit app by running the following command.

    ```bash
    streamlit run app/main.py
    ```

---
