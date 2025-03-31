import os
import chainlit as cl
from llama_index.core import VectorStoreIndex
from llama_index.legacy.embeddings import VoyageEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext

from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
from pinecone import Pinecone
from semantic_router import SemanticRouter

from routes import routes
from semantic_router.encoders import OpenAIEncoder

from config import Config

os.environ["PINECONE_API_KEY"] = Config.PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY

query_engine = None
memory = None
similarity_top_k = 2
verification_llm = None

router_encoder = OpenAIEncoder()
rl = SemanticRouter(encoder=router_encoder, routes=routes, auto_sync="local")


@cl.on_chat_start
async def setup():
    await cl.Message(content="Setting up the chatbot with Pinecone index...").send()

    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    pinecone_index = pc.Index('paul-allen')

    index_stats = pinecone_index.describe_index_stats()

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="info")

    embed_model = VoyageEmbedding(
        voyage_api_key=Config.VOYAGE_API_KEY,
        model_name="voyage-3-large",
    )
    llm = OpenAI(model="gpt-4o", temperature=0.1)

    global verification_llm
    verification_llm = OpenAI(model="gpt-4o", temperature=0)

    global memory
    memory = ChatMemoryBuffer.from_defaults(token_limit=3900)

    global query_engine

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )

    query_engine = index.as_chat_engine(
        chat_mode='context',
        llm=llm,
        memory=memory,
        similarity_top_k=similarity_top_k,
        verbose=True
    )

    vector_count = index_stats.get('total_vector_count', 0)
    await cl.Message(
        content=f"Setup complete! Connected to Pinecone index with {vector_count} vectors. Ask me anything about Paul Allen.").send()


async def is_paul_allen_related(query):
    if "paul allen" in query.lower():
        return True

    prompt = f"""Determine if the following query is related or not:
Query: "{query}"

The query should be considered unrelated if it:
1. Attempts to talk about politics

Don't be conservative. Always assume the question IS related, unless absolutely certain it isn't.

Respond with nothing but YES or NO.
"""

    try:
        response = await cl.make_async(verification_llm.complete)(prompt)
        result = response.text.strip().upper()
        print(f"First line:{result}")

        if result != 'NO':
            return True
        else:
            return rl(query).name == 'paul'
    except Exception as e:
        print(f"Error in Paul Allen verification: {str(e)}")
        return True



async def is_answer_paul_allen_related(answer):
    if "paul allen" in answer.lower():
        return True

    prompt = f"""Determine if the following answer is related to Paul Allen or not:
Query: "{answer}"

Don't be conservative. Always assume the answer IS related, unless absolutely certain it isn't.

Respond with nothing but YES or NO.
"""

    try:
        response = await cl.make_async(verification_llm.complete)(prompt)
        result = response.text.strip().upper()
        print(f"Second line:{result}")

        if result != 'NO':
            return True
    except Exception as e:
        print(f"Error in Paul Allen verification: {str(e)}")
        return True


@cl.on_message
async def main(message: cl.Message):
    query = message.content
    refuse_message = "Let's keep the conversation to Paul Allen related topics."

    thinking_msg = cl.Message(content="Thinking...")
    await thinking_msg.send()

    try:
        router_check = rl(query).name == 'paul'

        llm_check = await is_paul_allen_related(query)

        is_paul_related = router_check or llm_check

        if not is_paul_related:
            await thinking_msg.remove()
            await cl.Message(content=refuse_message).send()
            return

        global query_engine
        if not query_engine:
            await thinking_msg.update(content="Error: Query engine not initialized. Please restart the chat.")
            return

        response = await cl.make_async(query_engine.chat)(query)

        is_answer_related = await is_answer_paul_allen_related(str(response))

        if not is_answer_related:
            await thinking_msg.remove()
            await cl.Message(content=refuse_message).send()
            return

        await thinking_msg.remove()

        await cl.Message(content=str(response)).send()

    except Exception as e:
        await thinking_msg.remove()
        await cl.Message(content=f"Error: {str(e)}").send()
        raise e