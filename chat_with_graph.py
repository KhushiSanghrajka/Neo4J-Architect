"""
API endpoint for chatting with a Neo4j graph database using an AI agent.
"""
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import asyncio
from agents import Runner
from chat_agent import chat_agent
from openai import AsyncOpenAI
load_dotenv()

app = Flask(__name__)

client = AsyncOpenAI()

@app.route("/chat", methods=["POST"])
def chat_with_graph():
    data = request.json
    question = data.get("question")

    async def run_agents():
        question = await Runner.run(chat_agent, question)
        if question is None:
            raise ValueError("Chat agent requires a question...")
        return {
            "answer": chat_agent.final_output,
        }

    result = asyncio.run(run_agents())
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)