import streamlit as st 
import tempfile
from graph import load_document,State,compile_graph
from langchain.schema import AIMessage
st.title("Chatbot")
file = st.file_uploader(type=['pdf'], label='upload your files')


if 'messages' not in st.session_state:
    st.session_state.messages = [{"role":"ai","content":"Hello dear how can i help you?"}]

if 'chat_disbaled' not in st.session_state:
    st.session_state.chat_disabled = False

if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

if 'file_processing' not in st.session_state:
    st.session_state.file_processing = False

if 'collection_name' not in st.session_state:
    st.session_state.collection_name = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])



if file is not None and not st.session_state.file_uploaded and not st.session_state.file_processing:
        st.session_state.file_processing = True
        st.info("Procesing info")
        with tempfile.NamedTemporaryFile(suffix=".pdf",delete=True) as temp:
            temp.write(file.getbuffer())
            tempPath = temp.name
            load_document(temp_path=tempPath,file=file)

        st.session_state.collection_name = file.name
        st.session_state.file_uploaded = True
        st.session_state.file_processing = False

if st.session_state.chat_disabled:
    user_query = None
    st.info("Old query being processed")
elif st.session_state.file_processing:
    user_query = None
    st.info("Your file is still being processed, please wait...")
else:
    user_query=st.chat_input("write something");

if user_query is not None:
    st.session_state.chat_disabled = True
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)
    if st.session_state.file_uploaded:
        _state = State(
            collection_name=st.session_state.collection_name,
            user_query=user_query,
            messages=st.session_state["messages"],
            uploaded_file=True,
            context=None
        )
    else:
        _state = State(
            collection_name=None,
            context=None,
            user_query=user_query,
            uploaded_file=False,
            messages=st.session_state.messages
        )
            
    graph = compile_graph()

    for events in graph.stream(_state,stream_mode='values'):
        if 'messages' in events:
            last_msg = events['messages'][-1]

            if isinstance(last_msg,AIMessage):
                st.session_state.messages.append({"role":"ai","content":last_msg.content})
                st.chat_message("ai").write(last_msg.content)
    
    st.session_state.chat_disabled = False

