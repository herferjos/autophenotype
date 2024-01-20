import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
import requests
import pandas as pd
import json
import os
import glob
import time
import shutil
import re
import concurrent.futures
from openai import OpenAI


@st.cache_resource
def load_model():
    return SentenceTransformer(st.secrets['model'])
    
def extractor(caso_clinico):
    
    prompt = '''
    CONDICIONES
    
    Usted es un asistente médico para ayudar a extraer síntomas y fenotipos de un caso clínico.
    Sea preciso y no alucine con la información.
    
    MISIÓN
    
    Generar un diccionario en python que recoja los síntomas clínicos mencionados.
    
    FORMATO RESPUESTA:
    
    python dictionary -> {"original_symptoms": [], "symptoms_english":[]}
    
    ¡Recuerda extraer los síntomas médicos de la descripcion clínica proporcionada anteriormente y SOLO contestar con el diccionario en python para lo síntomas, nada más! Ten en cuenta que la descripción clínica puede estar en varios idiomas pero tu debes siempre responder con un listado en inglés y en el idioma original
    '''
    
    messages = [
          {"role":"system", "content": prompt},
          {"role":"user", "content": f"""Esta es la descripción clínica proporcionada por el usuario: '{caso_clinico}'
            Recuerda contestar con un JSON con la clave 'original_symptoms' y 'symptoms_english':"""}
    ]
    
    response = st.session_state.client.chat.completions.create(
        ="gpt-3.5-turbo-1106",
        messages=messages,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def search_database(query):
    k = 20

    modelo = load_model()
    
    query_vector = modelo.encode(query)

    # Buscar los vectores más similares al vector de consulta usando faiss como antes
    distances, indices = st.session_state.index_database.search(np.array([query_vector]), k)

    # Obtener los ID y Texts correspondientes a los vectores encontrados con mayor similaridad al texto de input usando ids_texts como antes
    results = []
    for i in range(k):
        result = {"ID": st.session_state.texts_database[indices[0][i]]["id"], "Text": st.session_state.texts_database[indices[0][i]]["text"]}
        results.append(result)

    return results
    

def selector(respuesta_database, sintoma):

    prompt = """
    CONDICIONES

    Usted es un asistente médico para ayudar a elegir el síntoma correcto para cada caso.
    Sea preciso y no alucine con la información.

    MISIÓN

    Voy a hacer una búsqueda rápida de los síntomas posibles asociados a la descripción. Responde únicamente con el ID que mejor se ajuste al síntoma descrito

    FORMATO RESPUESTA:

    {"ID": ..., "Name": ...}

    """
    
    messages = [
          {"role":"system", "content": prompt},
          {"role":"user", "content": f"""Esta es la descripción del síntoma proporcionada: '{sintoma}'
            Esta son las posibilidades que he encontrado: {respuesta_database}
            ¡Recuerda SOLO contestar con el FORMATO de JSON en python, nada más! Recuerda contestar la columna "Name" en el idioma original del síntoma proporcionado:"""}
    ]
    
    response = st.session_state.client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
    

def orchest(description):
    diccionario = extractor(description)
    lista_sintomas_english = diccionario['symptoms_english']
    lista_sintomas_original = diccionario['original_symptoms']

    def process_sintoma(sintoma_en, sintoma_original):
        diccionario_sintoma = selector(search_database(sintoma_en), sintoma_original)
        codigo_sintoma = diccionario_sintoma["ID"]
        nombre_sintoma = diccionario_sintoma["Name"]
        return sintoma_original.capitalize(), codigo_sintoma, nombre_sintoma

    with concurrent.futures.ThreadPoolExecutor() as executor:
        resultados = list(executor.map(lambda args: process_sintoma(*args), zip(lista_sintomas_english, lista_sintomas_original)))

    lista_codigo_sintomas, lista_nombre_sintomas = zip(*resultados)

    df = pd.DataFrame({"Síntoma Original": lista_sintomas_original, "ID": lista_codigo_sintomas, "Nombre del ID": lista_nombre_sintomas})
    df['Síntoma Original'] = df['Síntoma Original'].str.capitalize()
    return df
