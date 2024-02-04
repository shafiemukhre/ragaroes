
import os
from dotenv import load_dotenv

from getpass import getpass

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
    StorageContext,
    download_loader,
    load_index_from_storage,
)
import cassio
from llama_index.vector_stores import CassandraVectorStore
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = os.environ.get("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_ID = os.environ.get("ASTRA_DB_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ASTRA_DB_KEYSPACE = os.environ.get("ASTRA_DB_KEYSPACE")

cassio.init(
    database_id=ASTRA_DB_ID,
    token=ASTRA_DB_APPLICATION_TOKEN,  
    keyspace=ASTRA_DB_KEYSPACE,
)
cassandra_store = CassandraVectorStore(
    table="All_Stock_Earnings", embedding_dimension=1536
)



# load documents


# tickers = ["Meta"]
# years = ["2021", "2022", "2023"]
# Quarters = ["First", "Second", 'Third', "Fourth"]

# for tick in tickers:
#     for y in years:
#         for q in Quarters:
#             collection_name = f"{tick}_{y}_Q{q}"

#             my_file_metadata = lambda x: {"ticker": tick, "year": y, "quarter": q}
#             md_document = SimpleDirectoryReader(input_files=[f"/Users/parthjain/Desktop/project/ragaroes/pdf_files/{tick}-{q}-Quarter-{y}.pdf"], file_metadata=my_file_metadata).load_data()
#             md_index = VectorStoreIndex.from_vector_store(vector_store= cassandra_store, document_store=md_document)


md_index = VectorStoreIndex.from_vector_store(vector_store= cassandra_store)

md_query_engine = md_index.as_query_engine(
    filters=MetadataFilters(
        filters=[ExactMatchFilter(key="ticker", value="Meta"), ExactMatchFilter(key="year", value="2021"), ExactMatchFilter(key="quarter", value="First")]
    )
)
response = md_query_engine.query("Earnings of Meta in this quarter")
print(response.response)

md_query_engine = md_index.as_query_engine(
    filters=MetadataFilters(
        filters=[ExactMatchFilter(key="ticker", value="Meta"), ExactMatchFilter(key="year", value="2022"), ExactMatchFilter(key="quarter", value="First")]
    )
)
response = md_query_engine.query("Earnings of Meta in this quarter")
print(response.response)


md_query_engine = md_index.as_query_engine(
    filters=MetadataFilters(
        filters=[ExactMatchFilter(key="ticker", value="Meta"), ExactMatchFilter(key="year", value="2023"), ExactMatchFilter(key="quarter", value="Fourth")]
    )
)
response = md_query_engine.query("Earnings of Meta in this quarter")
print(response.response)


        
















