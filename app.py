import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from hugchat import hugchat
from hugchat.login import Login
from modules import orchest


if 'index_database' not in st.session_state:
    # reconstruir_faiss()
    st.session_state['index_database'] = faiss.read_index("index.faiss")

if 'texts_database' not in st.session_state:
    with open('texts.pkl', 'rb') as f:
        st.session_state['texts_database'] = pickle.load(f)

if 'model' not in st.session_state:
    st.session_state['model'] = SentenceTransformer(st.secrets['model'])

if 'chatbot' not in st.session_state:
    sign = Login(st.secrets['email'], st.secrets['password'])
    cookies = sign.login()
    st.session_state['chatbot'] = hugchat.ChatBot(cookies=cookies.get_dict())

st.write(st.session_state.model)

st.markdown("<h2 style='text-align: center;'>¡Buscador de Fenotipos Humanos!</h2>", unsafe_allow_html=True)
st.write("### 1) Introduce los síntomas que deseas buscar")
descripcion = st.text_area(label=":blue[Descripción clínica]", placeholder="Escribe aquí...")

if st.button(label = "Extraer Síntomas", type = "primary"):
    st.session_state['description'] = descripcion
    with st.spinner("Estamos procesando tu petición, puede tardar unos minutos..."):
        st.session_state['df_sintomas'] = orchest(descripcion)

st.write("---")
if 'description' in st.session_state:
    st.write("#### Síntomas:")
    st.write(st.session_state.description)
    
if 'df_sintomas' in st.session_state:
    st.write('### 2) Fenotipos encontrados')
    st.data_editor(st.session_state.df_sintomas, use_container_width=True, num_rows="dynamic", disabled=False, hide_index = True)
