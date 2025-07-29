"""
This script converts a PDF file into a graph database with sequential chunks and relationships, not semantic.
"""
import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Neo4jVector
from langchain.chains import RetrievalQA
from neo4j import GraphDatabase
import json

# Load API keys and secrets
load_dotenv()

# Config
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD") # put this in .env file
PDF_PATH = "pdfs/pytest-guide.pdf"

# 1. Load and split the PDF
loader = PyPDFLoader(PDF_PATH)
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(pages)
print(f"Total documents created: {len(docs)}")

# # 2. Generate embeddings
embedding = OpenAIEmbeddings()
texts = [doc.page_content for doc in docs]
metas = [doc.metadata for doc in docs]
embeddings = embedding.embed_documents(texts)

# 3. Store chunks and relationships in Neo4j
driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as session:
    # Clear old chunks
    session.run("MATCH (n:Chunk) DETACH DELETE n")

    prev_id = None
    for i, (text, meta, emb) in enumerate(zip(texts, metas, embeddings)):
        result = session.run("""
            CREATE (c:Chunk {
                content: $text,
                page: $page,
                embedding: $embedding
            }) RETURN id(c) AS cid
        """, {
            "text": text,
            "page": meta.get("page", -1),
            "embedding": emb
        })
        curr_id = result.single()["cid"]

        if prev_id is not None:
            session.run("""
                MATCH (a:Chunk), (b:Chunk)
                WHERE id(a) = $prev_id AND id(b) = $curr_id
                CREATE (a)-[:NEXT]->(b)
            """, {
                "prev_id": prev_id,
                "curr_id": curr_id
            })

        prev_id = curr_id

# 4. Setup Neo4j VectorStore and QA chain
vectorstore = Neo4jVector(
    embedding=embedding,
    url=NEO4J_URL,
    username=NEO4J_USER,
    password=NEO4J_PASSWORD,
    database="neo4j",
    index_name="pdf_rag_index",
    node_label="Chunk",
    text_node_property="content",
    embedding_node_property="embedding"
)

retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    chain_type="stuff",
    retriever=retriever
)

# 5. Ask a question
query = "What does the document say about usage of pytest coverage?"
response = qa.run(query)
print("Answer:", response)
