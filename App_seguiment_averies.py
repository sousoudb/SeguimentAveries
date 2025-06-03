import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Seguiment d'intervencions", layout="centered")
st.title("Seguiment de reparacions EMD VH (estat i prioritat)")

uploaded_file = st.file_uploader("Pujar Excel d'intervencions", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine="xlrd")
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        
        st.write("Columnes carregades:", df.columns.tolist())

        if "#Ordre Treball" not in df.columns or "Obs. Tècniques" not in df.columns:
            st.error("L'arxiu no conté les columnes requerides: 'ordre_treball' i/o 'obs._tecniques'")
        else:
            st.write(f"Total de files carregades: {len(df)}")

            df_grouped = df.groupby("#Ordre Treball", as_index=False).agg({
                "Obs. Tècniques": lambda x: " ".join(str(i) for i in x if pd.notna(i))
            })

            def detectar_estat(text):
                text = str(text).lower()
                if not text.strip():
                    return "Sense informació"
                if re.search(r"reparat|resolt|tancat|cerrado", text):
                    return "Possiblement resolt"
                elif re.search(r"signatura|acceptat|tramitaci[oó]|ok", text):
                    return "Tramitació iniciada"
                elif re.search(r"pressupost rebut|adjunt|import|recibido.*presupuesto", text):
                    return "Pressupost rebut"
                elif re.search(r"pressupost|esperant|pendent|solicita.*presupuesto|reclama", text):
                    return "Esperant pressupost"
                elif re.search(r"garantia|manteniment|sin coste|en garantia", text):
                    return "En garantia / manteniment"
                elif re.search(r"externalitzat|enviat|portat|lo lleva|dhl|nacex", text):
                    return "Externalitzat"
                else:
                    return "No classificat"

            def assignar_prioritat(estat):
                if estat in ["Esperant pressupost", "Externalitzat"]:
                    return "Alta"
                elif estat in ["Pressupost rebut"]:
                    return "Mitjana"
                elif estat in ["Tramitació iniciada", "En garantia / manteniment"]:
                    return "Baixa"
                else:
                    return "Revisar"

            df_grouped["estat_actual"] = df_grouped["Obs. Tècniques"].apply(detectar_estat)

            df_grouped["prioritat"] = df_grouped["estat_actual"].apply(assignar_prioritat)
            

            st.subheader("Resum d'estats")
            st.dataframe(df_grouped["estat_actual"].value_counts().rename_axis("Estat").reset_index(name="Comptador"))

            st.subheader("Resum de prioritats")
            st.dataframe(df_grouped["prioritat"].value_counts().rename_axis("Prioritat").reset_index(name="Comptador"))

            st.subheader("Mostra de resultats")
            st.dataframe(df_grouped.head(15))

            def convertir_a_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultat')
                return output.getvalue()

            excel_output = convertir_a_excel(df_grouped)

            st.download_button(
                label="Descarregar resultat Excel",
                data=excel_output,
                file_name="resultat_intervencions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error en carregar o processar l'arxiu: {e}")
