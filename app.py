import os
import streamlit as st
from autophenotype import get_phenotypes

st.set_page_config(page_title="Symptoms", page_icon="😷", layout="wide")

st.markdown(
    "<h2 style='text-align: center;'>Human Phenotype Finder!</h2>",
    unsafe_allow_html=True,
)
st.write("### 1) Enter the symptoms you want to search for")
description = st.text_area(
    label=":blue[Clinical Description]", placeholder="Write here..."
)

openai_api_key = st.text_input("Enter your OpenAI API (optional):", type="password")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

if st.button(label="Extract Symptoms", type="primary"):
    st.session_state["description"] = description
    with st.spinner("We are processing your request, it may take a few minutes..."):
        st.session_state["symptoms"] = get_phenotypes(description)

st.write("---")
if "description" in st.session_state:
    st.write("#### Symptoms:")
    st.write(st.session_state.description)

if "symptoms" in st.session_state:
    st.write("### 2) Found Phenotypes")
    st.data_editor(
        st.session_state.symptoms,
        use_container_width=True,
        num_rows="dynamic",
        disabled=False,
        hide_index=True,
    )
