import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from hugchat import hugchat
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

if 'model' not in st.session_state:
    st.session_state['model'] = SentenceTransformer(st.secrets['model'])

def chatbot(prompt):
    max_intentos = 3
    intentos = 0
    while intentos < max_intentos:
        try:
            id = st.session_state.chatbot.new_conversation()
            st.session_state.chatbot.change_conversation(id)
            respuesta = st.session_state.chatbot.query(prompt)['text']
            return respuesta
        except StopIteration:
            # Manejo del error StopIteration
            intentos += 1
            if intentos < max_intentos:
                # Espera unos segundos antes de intentar de nuevo
                time.sleep(2)
            else:
                st.error("Se alcanzó el máximo número de intentos. No se pudo obtener una respuesta válida.")
                return None


def extractor(caso_clinico):

    prompt = f"""Esta es la descripción clínica proporcionada por el usuario: '{caso_clinico}'
    """

    prompt = prompt + '''
    CONDICIONES

    Usted es un asistente médico para ayudar a extraer síntomas y fenotipos de un caso clínico.
    Sea preciso y no alucine con la información.

    MISIÓN

    Generar un diccionario en python que recoja los síntomas clínicos mencionados.

    FORMATO RESPUESTA:

    python dictionary -> {"original_symptoms": [], "symptoms_english":[]}

    ¡Recuerda extraer los síntomas médicos de la descripcion clínica proporcionada anteriormente y SOLO contestar con el diccionario en python para lo síntomas, nada más! Ten en cuenta que la descripción clínica puede estar en varios idiomas pero tu debes siempre responder con un listado en inglés y en el idioma original
    '''
    
    return chatbot(prompt)


def search_database(query):
    k = 20
    query_vector = st.session_state.model.encode(query)

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

    prompt = prompt + f"""Esta es la descripción del síntoma proporcionada: '{sintoma}'

    Esta son las posibilidades que he encontrado: {respuesta_database}
    ¡Recuerda SOLO contestar con el FORMATO de JSON en python, nada más! Recuerda contestar la columna "Name" en el idioma original del síntoma proporcionado.
    """
    return chatbot(prompt)
    

def jsoner(respuesta, instrucciones):
    max_intentos=3
    intentos = 0
    while intentos < max_intentos:
        try:
            match = re.search(r'\{([^}]+)\}', respuesta)
            contenido_json = match.group(0)
            diccionario = json.loads(contenido_json)
            return diccionario
        except json.JSONDecodeError:
            if intentos < max_intentos - 1:
                prompt = """Responde únicamente con un diccionario json de python con la siguiente estructura:
                """
                prompt = prompt + f"""
                Instrucciones del JSON:
                {instrucciones}
                Respuesta mal formateada: {respuesta}"""
                respuesta = st.session_state.chatbot.query(prompt)['text']
            else:
                print("Se alcanzó el máximo número de intentos. La respuesta no se pudo convertir a JSON.")
                return None
        intentos += 1


def orchest(description):
    respuesta = extractor(description)
    diccionario = jsoner(respuesta, '{"original_symptoms": [], "symptoms_english":[]}')
    lista_sintomas_english = diccionario['symptoms_english']
    lista_sintomas_original = diccionario['original_symptoms']

    def process_sintoma(sintoma_en, sintoma_original):
        respuesta2 = selector(search_database(sintoma_en), sintoma_original)
        diccionario_sintoma = jsoner(respuesta2, '{"ID": ..., "Name": ...}')
        codigo_sintoma = diccionario_sintoma["ID"]
        nombre_sintoma = diccionario_sintoma["Name"]
        return sintoma_original.capitalize(), codigo_sintoma, nombre_sintoma

    with concurrent.futures.ThreadPoolExecutor() as executor:
        resultados = list(executor.map(lambda args: process_sintoma(*args), zip(lista_sintomas_english, lista_sintomas_original)))

    lista_codigo_sintomas, lista_nombre_sintomas = zip(*resultados)

    df = pd.DataFrame({"Síntoma Original": lista_sintomas_original, "ID": lista_codigo_sintomas, "Nombre del ID": lista_nombre_sintomas})
    df['Síntoma Original'] = df['Síntoma Original'].str.capitalize()
    return df
