from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

filePath = Path(__file__).parent /"CONSENT.pdf"

document_loader = PyPDFLoader(file_path=filePath)

docs = document_loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=50,chunk_overlap=20)

split_docs = text_splitter.split_documents(documents=docs)

embedder = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = QdrantVectorStore.from_documents(
    url="http://localhost:6333",
    embedding=embedder,
    documents=split_docs,
    collection_name='consent-forever77'
)



