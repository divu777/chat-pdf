from typing_extensions import TypedDict
from typing import Annotated
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain.schema import SystemMessage
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph ,END
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

class State(BaseModel):
    user_query:str
    uploaded_file:bool
    context:str| None
    messages: Annotated[list,add_messages]
    collection_name:str | None


llm = init_chat_model(model_provider='openai',model='gpt-4.1')
embedder = OpenAIEmbeddings(model='text-embedding-3-large') 

def chat_node(state:State):
    messages = state.messages
    print(state)
    last_20 = messages[-20:]


    response =  llm.invoke(last_20)

    return{
        "messages" : [response]
    }

def load_document(temp_path,file):
    loader = PyPDFLoader(file_path=temp_path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents=data)

    QdrantVectorStore.from_documents(
        collection_name=file.name,
        embedding=embedder,
        documents=split_docs,
        url="http://localhost:6333",
    )

    print("Indexing done for the pdf")
    



def rag_chat_node(state:State):
    messages  = state.messages
    context = state.context
    last_20 = messages[-20:]
    SYSTEM_PROMPT=f'''
    You are an intelligent RAG Agent that solves user query by providing them with short and concise answers.

    #Instruction
        - Before deriving any answer always read under the Context Heading to see what did the similarity search gave output for the user_query
        - After looking at the context derieve an output based on the context

    #Context
    {context}
    '''
    response = llm.invoke([SystemMessage(SYSTEM_PROMPT), *last_20])

    return {
        "messages":[response]
    }


def similarity_search(state:State):
    user_query = state.user_query
    collection_name = state.collection_name

    vector_store = QdrantVectorStore.from_existing_collection(
        collection_name=collection_name,
        url='http//localhost:6333',
        embedding=embedder
    )

    search_result = vector_store.similarity_search(query=user_query)

    context = "\n\n\n".join( [ f"Page content: {result.page_content}\n Page Number: {result.metadata['page_label']}\n File location: {result.metadata['source']}" for result in search_result])

    state.context=context

    return state 


def compile_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node('chat_node',chat_node)
    graph_builder.add_node('similarity_search',similarity_search)
    graph_builder.add_node('rag_chat_node',rag_chat_node)
    graph_builder.set_conditional_entry_point(
        lambda state:
        'rag' if state.collection_name else 'chat_node'
    ,{
        "rag":"similarity_search",
        "chat_node":"chat_node"
    })

    graph_builder.add_edge('similarity_search','rag_chat_node')
    graph_builder.add_edge('rag_chat_node',END)
    graph_builder.add_edge('chat_node',END)
    graph = graph_builder.compile()
    return graph


# user_input = input("-=======>")

# _state=State(
#     user_query=user_input,
#     uploaded_file=True,
#     context=None,
#     collection_name="consent-form",
#     messages=[{"role":"user","content":user_input}]
# )


# graph = compile_graph()
# for events in graph.stream(_state,stream_mode='values'):
#     if "messages" in events:
#         events["messages"][-1].pretty_print()








