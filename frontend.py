from io import StringIO
import streamlit as st 
import pprint
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()


st.title("Chat With Pdf")
st.sidebar.title("Chats")
file = st.file_uploader("Choose your file",type="pdf")
embedder = OpenAIEmbeddings(model='text-embedding-3-large')

if "chat_disabled" not in st.session_state:
    st.session_state.chat_disabled = False

if "messages" not in st.session_state:
    st.session_state["messages"]= [{"role":"ai","content":"hello, how can i help you today?"}]



for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if not st.session_state.chat_disabled:
    user_query = st.chat_input("Type your question...")
else:
    user_query = None
    st.info("⏳ Please wait, processing your last query...")

if user_query is not None:
    st.session_state.chat_disabled = True

    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.getbuffer())
            temp_path = tmp.name

        loader = PyPDFLoader(file_path=temp_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
        split_docs = text_splitter.split_documents(documents=data)

        vector_store = QdrantVectorStore.from_documents(
            collection_name=file.name,
            embedding=embedder,
            documents=split_docs,
            url="http://localhost:6333",
        )

        pprint("Indexing done for the pdf")
    
    
    




