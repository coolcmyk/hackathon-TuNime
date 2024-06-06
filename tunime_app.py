# Imports
from openai import AsyncAzureOpenAI
import os
import asyncio
import json
from typing import List
import pymongo
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores.azure_cosmos_db import AzureCosmosDBVectorSearch
from langchain.schema.document import Document
from langchain.agents import Tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.tools import StructuredTool
from langchain_core.messages import SystemMessage
import requests
from bs4 import BeautifulSoup

# Endpoint and API_KEY From the env
ENDPOINT = "https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1"
API_KEY = os.environ.get("API_KEY")
CONNECTION_STRING = os.environ.get("CONNECTION_STRING")
# Basic Stuff
API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-4-vision"



class tunimeAssistant:
    def __init__(self, session_id: str) -> None:
        client = AsyncAzureOpenAI(
            azure_endpoint=ENDPOINT,
            api_key=API_KEY,
            api_version=API_VERSION,
        )
        self.embedding_model = AzureOpenAIEmbeddings(
            api_version = API_VERSION,
            azure_endpoint = ENDPOINT,
            api_key = API_KEY,
            chunk_size=10
        )
        system_message = SystemMessage(
            content = """
                You are a helpful, Study Assistant named Nyanko

                Your name is Nyanko, an anime cat that loves her.

                You     
            """
        )
        self.agent_executor = create_conversational_retrieval_agent(
                client,
                self.__create_agent_tools(),
                system_message = system_message,
                memory_key=session_id,
                verbose=True
        )

        def run(self, prompt: str) -> str:
            """
            Run Nyanko.
            """
            result = self.agent_executor({"input": prompt})
            return result["output"]
        
        def __create_nyanko_vector_store_retriever(
                self,
                collection_name: str,
                top_k: int = 3
            ):
            """
            Returns a vector store retriever for the given collection.
            """
            vector_store =  AzureCosmosDBVectorSearch.from_connection_string(
                connection_string = CONNECTION_STRING,
                namespace = f"nyanko.{collection_name}",
                embedding = self.embedding_model,
                index_name = "VectorSearchIndex",
                embedding_key = "contentVector",
                text_key = "_id"
            )
            return vector_store.as_retriever(search_kwargs={"k": top_k})
        
        def __create_nyanko_tools(self) -> List[Tool]:
            """
            Returns a list of tools / functions that nyanko can use.
            """
            summary_retriever = self.__create_nyanko_vector_store_retriever("summary")
            formula_retriever = self.__create_nyanko_vector_store_retriever("formulas")
            reference_retriever = self.__create_nyanko_vector_store_retriever("study_references")

            # create a chain on the retriever to format the documents as JSON
            products_retriever_chain = summary_retriever | format_docs
            formulas_retriever_chain = formula_retriever | format_docs
            reference_retriever_chain = reference_retriever | format_docs

            tools = [
                Tool(
                    name = "vector_search_summary",
                    func = products_retriever_chain.invoke,
                    description = """
                        Searches lecture's materials summary on internet / files based 
                        on the question. Returns the lectures information in JSON format.
                        """
                ),
                Tool(
                    name = "vector_search_formulas",
                    func = formulas_retriever_chain.invoke,
                    description = """
                        Searches lecture's important and relevant formulas based 
                        on the question. Returns the lectures information in JSON format.
                        """
                ),
                Tool(
                    name = "vector_search_reference",
                    func = reference_retriever_chain.invoke,
                    description = """
                        Searches lecture's important and relevant references file pages / website based 
                        on the question. Returns the lectures information in JSON format.
                        """
                ),
                StructuredTool.from_function(vector_search_summary),
                StructuredTool.from_function(get_formula),
                StructuredTool.from_function(get_reference)
            ]
            return tools
        


def format_docs(docs:List[Document]) -> str:
    """
    Prepares the product list for the system prompt.
    """
    str_docs = []
    for doc in docs:
        # Build the product document without the contentVector
        doc_dict = {"_id": doc.page_content}
        doc_dict.update(doc.metadata)
        if "contentVector" in doc_dict:
            del doc_dict["contentVector"]
        str_docs.append(json.dumps(doc_dict, default=str))
    # Return a single string containing each product JSON representation
    # separated by two newlines
    return "\n\n".join(str_docs)


def vector_search_summary(question: str) -> dict:
    """
    Searches lecture's materials summary on internet / files based on the question.
    Returns the lectures information in JSON format.
    
    Args:
        question (str): The question to search summaries for.
    
    Returns:
        dict: JSON formatted lecture summary information.
    """
    # Simulated retrieval process
    base_url = "https://en.wikipedia.org/wiki/Special:Search"
    params = {"search": question}

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Example parsing logic (depends on actual website structure)
        first_paragraph = soup.find('p')
        summary_text = first_paragraph.get_text(strip=True) if first_paragraph else "No summary found."

        summary_info = {
            "question": question,
            "summary": summary_text
        }
    else:
        summary_info = {
            "question": question,
            "error": f"Failed to retrieve data. Status code: {response.status_code}"
        }

    return summary_info



def get_product_by_id(product_id: str) -> str:
    """
    Retrieves a product by its ID.    
    """
    doc = db.products.find_one({"_id": product_id})
    if "contentVector" in doc:
        del doc["contentVector"]
    return json.dumps(doc)

def get_product_by_sku(sku: str) -> str:
    """
    Retrieves a product by its sku.
    """
    doc = db.products.find_one({"sku": sku})
    if "contentVector" in doc:
        del doc["contentVector"]
    return json.dumps(doc, default=str)

def get_sales_by_id(sales_id: str) -> str:
    """
    Retrieves a sales order by its ID.
    """
    doc = db.sales.find_one({"_id": sales_id})
    if "contentVector" in doc:
        del doc["contentVector"]
    return json.dumps(doc, default=str)