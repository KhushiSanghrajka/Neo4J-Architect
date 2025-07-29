"""
This module provides an example of how to use the Neo4jVector and RetrievalQA classes to chat with a Neo4j graph database.
"""
import os
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Neo4jVector

load_dotenv()

embedding_model = OpenAIEmbeddings()

# Use Neo4jVector with correct index name
vectorstore = Neo4jVector.from_existing_index(
    index_name="index",  # Replace with your actual index name
    embedding=embedding_model,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    chain_type="stuff",
    retriever=retriever
)

# Run query
query = "How do validations work in Pydantic AI?"
response = qa_chain.invoke(query)
print(response)