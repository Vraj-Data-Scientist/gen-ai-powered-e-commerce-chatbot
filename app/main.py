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

st.title("🛒 E-commerce Chatbot")

# Add multiple expanders with emojis and colorful formatting
st.markdown("**Get to Know Your Chatbot!** 🎉 Click the sections below to explore what I can do!")

with st.expander("✨ What Can I Do?", expanded=True):
    st.markdown("""
    **I'm your Flipkart shopping buddy!** 🛍️ I can answer:
    - **FAQs** about shopping policies (returns, payments, etc.).
    - **Product Questions** about Flipkart items (prices, ratings, discounts).
    
    Trained on **Flipkart data**, I'm here to make your shopping easy and fun! 🚀
    Just type your question below, and I'll respond in a snap! ⚡
    """)

with st.expander("❓ FAQs I Can Answer"):
    st.markdown("""
    **Got a question about shopping?** Here’s what I can help with:
    - 🛡️ What is the return policy of the products?
    - 💳 Do I get a discount with the HDFC credit card?
    - 📍 How can I track my order?
    - 💸 What payment methods are accepted?
    - ⏰ How long does it take to process a refund?
    - 🔧 Is there a refund for defective products?
    - 🛠️ What is your policy on defective products?
    - 🔄 Can I return a defective item?
    - 💵 Do you accept cash as a payment option?
    
    Ask any of these, and I’ll have an answer ready! 😊
    """)

with st.expander("🔍 Product Questions I Can Handle"):
    st.markdown("""
    **Looking for the perfect product?** Try these examples:
    - 🏆 "Show me top 3 shoes in descending order of rating"
    - 💰 "Are there any Puma shoes under Rs. 3000?"
    - 👟 "What is the price of Nike running shoes?"
    - 🌸 "Pink Puma shoes in price range 1000 to 5000"
    
    I’ll search Flipkart’s product data and list the best matches! 🕵️‍♂️
    """)

with st.expander("⚠️ Things to Know"):
    st.markdown("""
    **A few heads-ups to ensure a smooth experience:**
    - ✍️ **Spelling Matters**: I don’t handle typos yet, so please use correct spelling.
    - 📏 **Result Limits**: Product searches are capped at 10 items to keep things speedy.
    - 🛒 **Flipkart Only**: I’m trained on Flipkart data, so I can’t help with other platforms.
    - 🌐 **API Hiccups**: If my API (Groq) is down, I’ll retry or let you know to try later.
    - ❓ **Supported Queries**: Stick to the FAQs or product questions above for best results.
    
    Keep these in mind, and we’ll have a blast shopping together! 😎
    """)

if "faq_initialized" not in st.session_state:
    ingest_faq_data(faqs_path)
    st.session_state["faq_initialized"] = True

query = st.chat_input("💬 Type your query here (e.g., 'What is the return policy?' or 'Show me top 3 shoes')")

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
        st.error(f"Oops! An error occurred: {str(e)} 😓")
