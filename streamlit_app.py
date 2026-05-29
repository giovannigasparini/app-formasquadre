import streamlit as st
import pandas as pd
from io import BytesIO
from make_teams import make_teams  # your existing function

st.title("Generatore di Squadre")
st.image("banner.png", use_container_width=True)

uploaded = st.file_uploader("Carica il file Excel", type=["xlsx"])

if uploaded:
    df_raw = pd.read_excel(uploaded, usecols=["Nome", "Cognome", "Tipologia biglietto"])
    df_result, teams, colors, sizes = make_teams(df_raw)

    st.dataframe(df_result)

    buf = BytesIO()
    df_result.to_excel(buf, index=False)
    st.download_button("📥 Scarica Excel con squadre", buf.getvalue(),
                       file_name="squadre.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")