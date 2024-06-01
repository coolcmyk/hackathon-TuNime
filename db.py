import pymongo
import os
import asyncio

class tunimeDB:
    def __init__(self):
        self.connection_string = os.environ.get("CONNECTION_STRING")
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client.tunime
        self.collection = self.db.collect

    async def close(self):
        if self.client:
            self.client.close()

    async def insert_document(self, document):
        await self.collection.insert_one(document)

    async def find_document(self, query):
        return await self.collection.find_one(query)

# # Usage example
# async def main():
#     CONNECTION_STRING = os.environ.get("CONNECTION_STRING")
#     db_manager = tunimeDB(CONNECTION_STRING)
#     await db_manager.connect()

#     # Perform database operations
#     await db_manager.insert_document({"name": "John"})
#     result = await db_manager.find_document({"name": "John"})
#     print(result)

#     await db_manager.close()

# # Run the main function
# asyncio.run(main())
