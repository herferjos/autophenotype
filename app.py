import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from hugchat import hugchat
from hugchat.login import Login



if 'index_database' not in st.session_state:
    # reconstruir_faiss()
    st.session_state['index_database'] = faiss.read_index("index.faiss")

if 'texts_database' not in st.session_state:
    with open('texts.pkl', 'rb') as f:
        st.session_state['texts_database'] = pickle.load(f)

if 'model' not in st.session_state:
    st.session_state['model'] = SentenceTransformer('joseluhf11/symptom_encoder_v9')

if 'chatbot' not in st.session_state:
    sign = Login(st.secrets['email'], st.secrets['password'])
    cookies = sign.login()
    st.session_state['chatbot'] = hugchat.ChatBot(cookies=cookies.get_dict())
