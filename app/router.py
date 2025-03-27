from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "Is refund for defective products?",
        "What is your policy on defective products?",
        "Can I return a defective item?",
        "Do you accept cash as a payment option?",
        "What is the return policy of the products",
        "Do I get discount with the HDFC credit card",
        "How can I track my order",
        "What payment methods are accepted",
        "How long does it take to process a refund",
        "Is refund for defective products",
        "What is your policy on defective products",
        "Can I return a defective item",
        "Do you accept cash as a payment option"
    ]
)

sql = Route(
    name='sql',
    utterances=[
        "I want to buy nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of puma running shoes?",
        "Pink Puma shoes in price range 5000 to 1000",
        "Show me Puma shoes between 1000 and 5000",
        "Show me top 3 shoes in descending order of rating"
    ]
)

router = SemanticRouter(routes=[faq, sql], encoder=encoder)  # Add threshold=0.5 if supported

# Manually prepare utterances and embeddings with route association
all_utterances = faq.utterances + sql.utterances
all_embeddings = encoder(all_utterances)
route_map = [faq.name] * len(faq.utterances) + [sql.name] * len(sql.utterances)

# Add to index
router.index.add(routes=route_map, embeddings=all_embeddings, utterances=all_utterances)

if __name__ == "__main__":
    test_queries = [
        "Show me top 3 shoes in descending order of rating",
        "What is your policy on defective product?",
        "Pink Puma shoes in price range 5000 to 1000",
        "Do you accept cash as a payment option?"
    ]

    for query in test_queries:
        route_decision = router(query)
        print(f"Query: {query}")
        print(f"Route: {route_decision.name}")
        print("---")
