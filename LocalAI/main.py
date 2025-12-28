from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import *

model = OllamaLLM(model="llama3.2")

template = """
You are an exeprt in answering questions about a pizza restaurant

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

VectorRetriever_instance = VectorRetriever()
VectorRetriever_instance.read_csv(
    csv_path            ="LocalAI/realistic_restaurant_reviews.csv",
    embeddings_model    ="mxbai-embed-large",
    db_location         ="./LocalAI/chrome_langchain_db"
)
VectorRetriever_instance.create_vector_store()

retriever = VectorRetriever_instance.retriever

while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")
    if question == "q":
        break
    
    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)