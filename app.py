import streamlit as st
from src.autophenotype import get_phenotypes

st.set_page_config(page_title="Síntomas", page_icon="😷", layout="wide")

st.markdown(
    "<h2 style='text-align: center;'>¡Buscador de Fenotipos Humanos!</h2>",
    unsafe_allow_html=True,
)
st.write("### 1) Introduce los síntomas que deseas buscar")
descripcion = st.text_area(
    label=":blue[Descripción clínica]", placeholder="Escribe aquí..."
)

if st.button(label="Extraer Síntomas", type="primary"):
    st.session_state["description"] = descripcion
    with st.spinner("Estamos procesando tu petición, puede tardar unos minutos..."):
        st.session_state["symptoms"] = get_phenotypes(descripcion)

st.write("---")
if "description" in st.session_state:
    st.write("#### Síntomas:")
    st.write(st.session_state.description)

if "symptoms" in st.session_state:
    st.write("### 2) Fenotipos encontrados")
    st.data_editor(
        st.session_state.df_sintomas,
        use_container_width=True,
        num_rows="dynamic",
        disabled=False,
        hide_index=True,
    )
