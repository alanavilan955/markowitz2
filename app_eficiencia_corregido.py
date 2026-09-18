from pathlib import Path
import io
import numpy as np
import pandas as pd
import streamlit as st

# Plotly opcional para evitar ModuleNotFoundError
PLOTLY_AVAILABLE = True
try:
    import plotly.express as px
except Exception:
    PLOTLY_AVAILABLE = False

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

st.set_page_config(page_title="Eficiencia de Producción", layout="wide")
st.title("Eficiencia de Producción | Planta de Alimentos")

BASE = Path(__file__).with_name("base_eficiencia_planta_alimentos.xlsx")
source = BASE
if BASE.exists():
    df = pd.read_excel(BASE, sheet_name="Base_Datos", engine="openpyxl")
else:
    st.error("No se encontró base_eficiencia_planta_alimentos.xlsx")
    st.stop()

if PLOTLY_AVAILABLE:
    st.success("Plotly cargado correctamente")
else:
    st.warning("Plotly no está instalado. Se mostrarán tablas y métricas sin gráficas Plotly.")

st.dataframe(df.head())
