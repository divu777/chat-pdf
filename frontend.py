from io import StringIO
import streamlit as st 
import pprint
from langchain_community.document_loaders import PyPDFLoader
import tempfile

st.header("Chat bot")
st.sidebar.title("Chats")

file = st.file_uploader("Choose your file",type="pdf")


# To convert to a string based IO:
if file is not None:
    # with open("temp.pdf","wb") as f:
    #     f.write(file.getbuffer())

    with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
        tmp.write(file.getbuffer())
        temp_path=tmp.name



        loader = PyPDFLoader(file_path=tmp.name)

        data = loader.load()

