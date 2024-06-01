# Imports
from openai import AsyncAzureOpenAI
import os
import asyncio
from db import tunimeDB


# Basic DB init
db = tunimeDB()

# Endpoint and API_KEY From the env
ENDPOINT = "https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1"
API_KEY = os.environ.get("API_KEY")

# Basic Stuff
API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-4-vision"

async def main():
    await db.connect()
    client = AsyncAzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION,
    )

    while True:
        user_input = input("Enter your message: ")
        response = await client.embeddings.create(
            input=user_input,
            model="text-embedding-3-small",
        )
        print(response.data[0].embedding)
        MESSAGES = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ]

        completion = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=MESSAGES,
        )

        print(completion.model_dump_json(indent=2))

# Run the main function asynchronously
asyncio.run(main())
