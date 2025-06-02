import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Seguiment intervencions", layout="centered")
st.title("🛠️ Seguiment d'intervencions tècniques (estat i prioritat)")

uploaded_file = st.file_uploader("📎 Pujar Excel d'intervencions", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("👀 Vista prèvia:")
    st.dataframe(df.head())

    if "Obs. Tècniques" not in df.columns:
        st.error("❌ Falta la columna 'Obs. Tècniques'")
    else:
        def detectar_estat(obs):
            text = str(obs).lower()

            if re.search(r"reparat|resolt|tancat", text):
                return "Possiblement resolt"
            elif re.search(r"signatura|acceptat|tramitaci[oó]|ok", text):
                return "Tramitació iniciada"
            elif re.search(r"pressupost rebut|adjunt|import|aprovació", text):
                return "Pressupost rebut"
            elif re.search(r"pressupost|esperant|pendent", text):
                return "Esperant pressupost"
            elif re.search(r"garantia|manteniment|sense cost", text):
                return "En garantia / manteniment"
            elif re.search(r"externalitzat|enviat|portat", text):
                return "Externalitzat"
            elif len(text.strip()) == 0:
                return "Sense informació"
            else:
                return "No classificat"

        def assignar_prioritat(estat):
            if estat in ["Esperant pressupost", "Externalitzat"]:
                return "🔴 Alta"
            elif estat in ["Pressupost rebut"]:
                return "🟠 Mitjana"
            elif estat in ["Tramitació iniciada", "En garantia / manteniment"]:
                return "🟢 Baixa"
            else:
                return "⚪ Revisar"

        df["Estat actual"] = df["Obs. Tècniques"].apply(detectar_estat)
        df["Prioritat seguiment"] = df["Estat actual"].apply(assignar_prioritat)

        st.success("✅ Fitxer analitzat. Estat i prioritat afegits.")
        st.dataframe(df[["Obs. Tècniques", "Estat actual", "Prioritat seguiment"]].head(10))

        @st.cache_data
        def convert_df(df):
            return df.to_excel(index=False, engine="openpyxl")

        output = convert_df(df)

        st.download_button(
            label="📥 Descarregar Excel processat",
            data=output,
            file_name="seguiment_intervencions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
