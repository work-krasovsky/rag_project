from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

milvus_host = os.environ.get("MILVUS_HOST", "localhost")
milvus_port = os.environ.get("MILVUS_PORT", "19530")

uri = f"http://{milvus_host}:{milvus_port}"

embeddings = OpenAIEmbeddings(
    model=os.environ.get("EMBEDDINGS_MODEL", "text-embedding-3-small"),
)

vector_store = Milvus(
    embedding_function=embeddings,
    connection_args={'uri': uri},
    auto_id=True,
)

top_k=int(os.environ.get("RETRIEVER_TOP_K", 5))
retriever = vector_store.as_retriever(search_kwargs={'k': top_k})

def add_text_file(file_path):
    doc_data = TextLoader(file_path, encoding='utf-8').load_and_split(
        RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    )
    vector_store.add_texts([doc.page_content for doc in doc_data])


def add_pdf_file(file_path):
    doc_data = PyPDFLoader(file_path).load_and_split(
        RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    )
    vector_store.add_texts([doc.page_content for doc in doc_data])
