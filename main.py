import json
import asyncio
from flask import Flask, render_template, request, Response
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

app = Flask(__name__)

# Initialize OpenAI client
client = AsyncOpenAI()


class ChatRequest:
    def __init__(self, model="gpt-4.1", temperature=0.7):
        self.model = model
        self.temperature = temperature


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    model = data.get("model", "gpt-4.1")
    temperature = data.get("temperature", 0.7)

    # Create chat request object
    chat_request = ChatRequest(model=model, temperature=temperature)

    # Prepare messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_message},
    ]

    return Response(
        stream_response(chat_request, messages),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )


async def stream_llm_response(chat_request, messages):
    """Stream response from OpenAI API"""
    try:
        # Create streaming response
        stream = await client.responses.create(
            model=chat_request.model,
            instructions="You are a helpful assistant. Please provide clear and concise responses.",
            input=messages,
            temperature=chat_request.temperature,
            tools=None,  # Add tools here if needed
            stream=True,
        )

        # Yield each chunk as it comes
        async for event in stream:
            if event.type == "response.output_text.delta":
                # Format the chunk as JSON for the client
                chunk_data = {"type": "content", "content": event.delta}
                yield f"data: {json.dumps(chunk_data)}\n\n"

    except Exception as e:
        # Send error message to client
        error_data = {"type": "error", "content": f"Error: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"

    # Send completion signal
    completion_data = {"type": "done", "content": ""}
    yield f"data: {json.dumps(completion_data)}\n\n"


def stream_response(chat_request, messages):
    """Synchronous wrapper for async streaming"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        async_gen = stream_llm_response(chat_request, messages)
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
