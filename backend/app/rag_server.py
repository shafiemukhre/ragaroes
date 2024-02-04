from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from typing import List

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI

import logging

from llama_index.response_synthesizers import (
    get_response_synthesizer,
    BaseSynthesizer,
)
from llama_index.query_engine import CustomQueryEngine
from llama_index.query_engine import PandasQueryEngine
from llama_index.tools import QueryEngineTool, ToolMetadata
import pandas as pd
import cassio
from llama_index.vector_stores import CassandraVectorStore
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.agent import ReActAgent
from llama_index.llms import OpenAI

# from dotenv import load_dotenv
from pydantic import BaseModel, Field
from llama_index.llms.openai_utils import to_openai_function
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
import os


from app.utils import logger

# load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ASTRA_DB_ID = os.environ.get("ASTRA_DB_ID")
ASTRA_DB_APPLICATION_TOKEN = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE = os.environ.get("ASTRA_DB_KEYSPACE")
tickers = ["META"]
class extract(BaseModel):
    """
    Given the query extrcat the year and quarter of the year
    """
    year: str = Field("2023",description="The year of the earnings from  year choices: ['2023','2022', '2021', '2020', '2019']")
    quater: str = Field("Fourth", description="The quarter of the earnings from quarter choices: ['First', 'Second', 'Third', 'Fourth']")

def extract_year_quater(query):
    model = ChatOpenAI(model = "gpt-3.5-turbo-0613")
    parser = PydanticOutputParser(pydantic_object=extract)
    prompt = PromptTemplate(
        template="Extract the year and quarter of the year from the given query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser

    resp = chain.invoke({"query": query})
    print(resp)
    return resp.year, resp.quater 
   # Print the response

cassio.init(
    database_id=ASTRA_DB_ID,
    token=ASTRA_DB_APPLICATION_TOKEN,  
    keyspace=ASTRA_DB_KEYSPACE,
)
cassandra_store = CassandraVectorStore(
    table="All_Stock_Earnings", embedding_dimension=1536
)

def load_pdfs():
    for tick in tickers:
        #TODO: Setup step. Read from folder, index n write to Astra
        docs = SimpleDirectoryReader(
            input_files=[f'app/data/pdf/{tick}.pdf']
        ).load_data()
        logger.info('load_pdf')
        pdf_index = VectorStoreIndex.from_documents(docs)
        pdf_index.storage_context.persist(persist_dir=f"app/data/storaged/{tick}_index")


def get_index(ticker:str, year:str="2021", quarter:str="Second"):
    '''
    Retrieves the relevant index from Astra based on the provided ticker, year, and quarter.

    Args:
        ticker (str): The ticker symbol of the stock.
        year (str): The year of the earnings report.
        quarter (str): The quarter of the earnings report.

    Returns:
        md_query_engine: The query engine for the relevant index.

    Raises:
        Exception: If the index is not found.
    '''
    try:
        #TODO: Get relevant from Astra -> Achieved
        md_index = VectorStoreIndex.from_vector_store(vector_store= cassandra_store)
        md_query_engine = md_index.as_query_engine(
        # filters=MetadataFilters(
        #     filters=[ExactMatchFilter(key="ticker", value=ticker)]
        # ),
        similarity_top_k=3
    )
        logger.info('engine_pdf')
        return md_query_engine
    except:
        logger.error(f'Index not found')


def load_csv(ticker):
    docs = pd.read_csv(f"app/data/csv/{ticker}.csv")
    engine = PandasQueryEngine(df=docs, verbose=True, streaming=True)
    return engine

def get_engine_tools(ticker, year, quarter):
    query_engine_tools = [
        QueryEngineTool(
            query_engine=get_index(ticker),
            metadata=ToolMetadata(
                name="earnings",
                description=(
                    "Provides information about earnings report of the company Given the year and quarter and Ticker"
                    "The engine has these parameters: ticker, year, quarter"

                    "Use detailed plain text question as input to the tool."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=load_csv(ticker),
            metadata=ToolMetadata(
                name="stocks",
                description=(
                    "Provides information about stockprices of the company. The csv is already loaded in dataframe."
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ),
    ]
    return query_engine_tools

def setup_agent(ticker, year, quater):
    llm = OpenAI(model="gpt-3.5-turbo-0613")
    agent = ReActAgent.from_tools(
        get_engine_tools(ticker, year, quater),
        llm=llm,
        verbose=True,
        # context=context  
    )
    return agent

async def ask_stream_chat(content, ticker_id):
    #TODO: Pending
    agent = setup_agent(ticker_id)
    response =  agent.stream_chat(content)
    for token in response:
        yield token
    # return response


def ask_chat(content, ticker_id):
    year, quater = extract_year_quater(content)
    agent = setup_agent(ticker_id, year, quater)
    response = agent.chat(content)
    return response

# #TODO: Make Tickr, year, quarter dynamic
# def main():
#     ask_chat('What is the quaterly earning of Meta in year 2021 and quater 2', 'META')

# if __name__ == "__main__":
#     main()