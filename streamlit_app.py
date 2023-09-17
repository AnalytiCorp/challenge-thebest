import streamlit as st

from streamlit_gallery import apps, components
from streamlit_gallery.utils.page import page_group

def main():
    page = page_group("p")

    with st.sidebar:
        st.title("🎈 Sumario")

        with st.expander("✨ INTRO", True):
            page.item("Explicação das Analises", apps.gallery, default=True)

        with st.expander("🧩 ANALISE DESCRITIVA", True):
            page.item("1. Vendas e Receita", components.salesrevenue_01)

    page.show()

if __name__ == "__main__":
    st.set_page_config(page_title="Streamlit Gallery by Okld", page_icon="🎈", layout="wide")
    main()
