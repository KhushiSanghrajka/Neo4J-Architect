"""
This module implements a chat agent that interfaces with a Neo4j graph database and Tavily search through MCP server. It provides vector-based retrieval and search capabilities.
"""
import os
from agents import Agent
from agents.mcp.server import MCPServerStreamableHttp
from langchain.vectorstores import Neo4jVector
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")

from langchain.embeddings import OpenAIEmbeddings
embedding_model = OpenAIEmbeddings()

# Use Neo4jVector with correct index name
vectorstore = Neo4jVector.from_existing_index(
    index_name="index", # Replace with your actual index name
    embedding=embedding_model,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)

@tool
def fetch_from_neo4j(query: str) -> str:
    """Fetch data from Neo4j using the vector store."""
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        chain_type="stuff",
        retriever=retriever
    )
    response = qa_chain.invoke(query)
    return response

tavily_search_mcp = MCPServerStreamableHttp(
    name="Neo4J Search",
    params={
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_key}",
    })

chat_agent = Agent(
    name="Neo4J Chat Agent",
    instructions="""
    You are a helpful assistant that answers users queries with context from graph database.
    Your task is to analyze raw user questions and generate answers from the graph database.
    Use the 'fetch_from_neo4j' tool to query the Neo4j database.
    If the answer is not found, you can use the Tavily search engine to find relevant information. Only use the search engine if you cannot find relevant information in the graph database.
    Respond with I don't know if you cannot find relevant information in the graph database or the search engine.
    """,
    tools=[fetch_from_neo4j],
    mcp_servers=[tavily_search_mcp]
)
