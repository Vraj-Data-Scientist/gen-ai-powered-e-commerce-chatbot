import streamlit as st
from faq import ingest_faq_data, faq_chain
from sql import sql_chain
from pathlib import Path
from router import router

faqs_path = Path(__file__).parent / "resources/faq_data.csv"

def ask(query):
    route = router(query).name
    if route == 'faq':
        return faq_chain(query)
    elif route == 'sql':
        return sql_chain(query)
    else:
        return f"Ask either FAQs or product-related questions about this platform."

st.title("E-commerce Chatbot")

# Add an expander with chatbot information
with st.expander("About This Chatbot", expanded=False):
    st.markdown("""
    ### Chatbot Capabilities and Limitations

    This chatbot is designed to assist with e-commerce queries using data trained on Flipkart product information. It can answer two types of questions:

    #### 1. FAQs (Frequently Asked Questions)
    The chatbot can respond to the following FAQs:
    - What is the return policy of the products?
    - Do I get discount with the HDFC credit card?
    - How can I track my order?
    - What payment methods are accepted?
    - How long does it take to process a refund?
    - Is refund for defective products?
    - What is your policy on defective products?
    - Can I return a defective item?
    - Do you accept cash as a payment option?

    #### 2. SQL Queries (Product-Related Questions)
    The chatbot can answer product-related questions about Flipkart data, such as price, brand, ratings, and discounts. Examples include:
    - "Show me top 3 shoes in descending order of rating"
    - "Are there any Puma shoes under Rs. 3000?"
    - "What is the price of Nike running shoes?"
    - "Pink Puma shoes in price range 1000 to 5000"

    #### Limitations
    - **Spelling Sensitivity**: The chatbot does not currently handle spelling mistakes. Please use correct spelling for accurate responses.
    - **Token Limit**: For product queries, results are limited to 10 records to stay within API token limits. Large datasets may trigger an error message.
    - **Query Scope**: Only FAQs listed above and product-related questions about Flipkart data are supported. Other questions may return a generic response.
    - **API Availability**: Occasionally, the Groq API may be unavailable (e.g., 503 errors), causing temporary failures. The chatbot will retry or display an error message.
    - **Training Data**: The chatbot is trained exclusively on Flipkart product data, so it cannot answer questions about other platforms or non-product topics.

    For best results, ensure your query matches the FAQ list or follows the SQL query examples above.
    """)

if "faq_initialized" not in st.session_state:
    ingest_faq_data(faqs_path)
    st.session_state["faq_initialized"] = True

query = st.chat_input("Write your query")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role":"user", "content":query})

    try:
        response = ask(query)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
