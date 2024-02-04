from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
import logging


from llama_index.query_engine import PandasQueryEngine
from llama_index.tools import QueryEngineTool, ToolMetadata
import pandas as pd

from llama_index.agent import ReActAgent
from llama_index.llms import OpenAI
import openai

logger = logging.getLogger(__name__)


tickers = ['META']
openai.api_key = "" #TODO: Update when running on local


def load_pdfs():

    
    for tick in tickers:

        #TODO: Setup step. Read from folder, index n write to Astra
        docs = SimpleDirectoryReader(
            input_files=[f'app/data/pdf/{tick}.pdf']
        ).load_data()
        logger.info('load_pdf')
        pdf_index = VectorStoreIndex.from_documents(docs)
        pdf_index.storage_context.persist(persist_dir=f"app/data/storaged/{tick}_index")


def get_index(ticker):

    try:
        #TODO: Get relevant from Astra
        storage_context = StorageContext.from_defaults(
            persist_dir=f"app/data/storaged/{ticker}_index"
        )
        index = load_index_from_storage(storage_context)
        engine = index.as_query_engine(similarity_top_k=3)
        logger.info('engine_pdf')
        return engine

    except:
        logger.error(f'Index not found')


def load_csv(ticker):

    docs = pd.read_csv(f'app/data/csv/{ticker}.csv')
    engine = PandasQueryEngine(df=docs, verbose=True)
    return engine

def get_engine_tools(ticker):

    query_engine_tools = [
        QueryEngineTool(
            query_engine=get_index(ticker),
            metadata=ToolMetadata(
                name="pdf",
                description=(
                    "Provides information about earnings report of the company "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=load_csv(ticker),
            metadata=ToolMetadata(
                name="csv",
                description=(
                    "Provides information about stockprices of the company "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ),
    ]
    return query_engine_tools

def setup_agent(ticker):
    llm = OpenAI(model="gpt-3.5-turbo-0613")

    agent = ReActAgent.from_tools(
        get_engine_tools(ticker),
        llm=llm,
        verbose=True,
        # context=context  
    )
    return agent

def ask_stream_chat(content, ticker_id):
    #TODO: Pending
    agent = setup_agent(ticker_id)
    response = agent.chat(content)
    return response


def ask_chat(content, ticker_id):
    agent = setup_agent(ticker_id)
    response = agent.chat(content)
    return response
