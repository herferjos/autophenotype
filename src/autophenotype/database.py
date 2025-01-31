import numpy as np
import faiss
import streamlit as st
import pickle
from sentence_transformers import SentenceTransformer

with open("./src/autophenotype/resources/texts.pkl", "rb") as f:
    texts_database = pickle.load(f)


@st.cache_resource
def load():
    # Load the model and index database
    model = SentenceTransformer("joseluhf11/symptom_encoder_v9")
    index_database = faiss.read_index("./src/autophenotype/resources/index.faiss")
    with open("./src/autophenotype/resources/texts.pkl", "rb") as f:
        texts_database = pickle.load(f)

    return model, index_database, texts_database


def search_database(query, k=20):

    model, index_database, texts_database = load()

    query_vector = model.encode(query)

    # Search for the most similar vectors to the query vector using faiss
    _, indices = index_database.search(np.array([query_vector]), k)

    # Get the IDs and texts corresponding to the found vectors with the highest similarity to the input text
    results = []
    for i in range(k):
        result = {
            "ID": texts_database[indices[0][i]]["id"],
            "Text": texts_database[indices[0][i]]["text"],
        }
        results.append(result)

    return results
