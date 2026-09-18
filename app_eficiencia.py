from pathlib import Path
import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Eficiencia de Produccion",
    page_icon="🏭",
    layout="wide",
)

st.title("Eficiencia de Produccion | Planta de Alimentos")
st.caption(
    "Analisis descriptivo, correlacion y regresion lineal exploratoria. "
    "No incluye frontera eficiente, Markowitz/Malkowitz ni optimizacion."
)

BASE = Path(__file__).with_name("base_eficiencia_planta_alimentos.xlsx")


@st.cache_data
def cargar_excel(origen):
    return pd.read_excel(origen, sheet_name="Base_Datos", engine="openpyxl")


def regresion_numpy(datos, x_col, y_col):
    """Regresion lineal simple sin librerias externas de modelado."""
    muestra = datos[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(muestra) < 3 or muestra[x_col].nunique() < 2:
        return None

    x = muestra[x_col].to_numpy(dtype=float)
    y = muestra[y_col].to_numpy(dtype=float)
    pendiente, intercepto = np.polyfit(x, y, 1)
    estimado = pendiente * x + intercepto
    residuo = y - estimado
    ss_res = float(np.sum(residuo ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    mae = float(np.mean(np.abs(residuo)))

    grafica = muestra.copy()
    grafica["Valor_estimado"] = pendiente * grafica[x_col] + intercepto
    grafica = grafica.sort_values(x_col)
    return pendiente, intercepto, r2, mae, grafica


archivo = st.sidebar.file_uploader("Cargar archivo Excel", type=["xlsx"])
if archivo is not None:
    origen = archivo
    nombre_origen = archivo.name
elif BASE.exists():
    origen = BASE
    nombre_origen = BASE.name
else:
    st.error(
        "No se encontro base_eficiencia_planta_alimentos.xlsx. "
        "Sube el archivo desde la barra lateral."
    )
    st.stop()

try:
    df = cargar_excel(origen)
except Exception as error:
    st.error(f"No fue posible abrir la hoja Base_Datos: {error}")
    st.stop()

columnas_requeridas = {
    "Fecha", "Linea", "Turno", "Volumen_Producido_t", "Yield_pct",
    "OEE_pct", "Horas_Mano_Obra", "Costo_Total_MXN"
}
faltantes = sorted(columnas_requeridas.difference(df.columns))
if faltantes:
    st.error("Faltan columnas requeridas: " + ", ".join(faltantes))
    st.stop()

st.sidebar.caption(f"Fuente: {nombre_origen}")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["Turno"] = df["Turno"].astype(str)

st.sidebar.header("Filtros")
lineas_disponibles = sorted(df["Linea"].dropna().astype(str).unique())
turnos_disponibles = sorted(df["Turno"].dropna().unique())
lineas = st.sidebar.multiselect("Linea", lineas_disponibles, default=lineas_disponibles)
turnos = st.sidebar.multiselect("Turno", turnos_disponibles, default=turnos_disponibles)

fechas_validas = df["Fecha"].dropna()
if fechas_validas.empty:
    st.error("La columna Fecha no contiene fechas validas.")
    st.stop()

fecha_min = fechas_validas.min().date()
fecha_max = fechas_validas.max().date()
rango = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)

if isinstance(rango, (tuple, list)) and len(rango) == 2:
    inicio, fin = pd.Timestamp(rango[0]), pd.Timestamp(rango[1])
else:
    inicio = fin = pd.Timestamp(rango[0] if isinstance(rango, (tuple, list)) else rango)

filtrado = df[
    df["Linea"].astype(str).isin(lineas)
    & df["Turno"].isin(turnos)
    & df["Fecha"].between(inicio, fin)
].copy()

if filtrado.empty:
    st.warning("No hay registros para los filtros seleccionados.")
    st.stop()

volumen = filtrado["Volumen_Producido_t"].sum()
horas_mo = filtrado["Horas_Mano_Obra"].sum()
costo_total = filtrado["Costo_Total_MXN"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Volumen producido (t)", f"{volumen:,.0f}")
col2.metric("Yield promedio", f"{filtrado['Yield_pct'].mean():.1%}")
col3.metric("OEE promedio", f"{filtrado['OEE_pct'].mean():.1%}")
col4.metric("Eficiencia (t/hh)", f"{volumen / horas_mo:.3f}" if horas_mo else "N/D")
col5.metric("Costo por t (MXN)", f"${costo_total / volumen:,.0f}" if volumen else "N/D")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Tendencias", "Correlacion", "Regresion", "Base de datos"]
)

with tab1:
    diario = (
        filtrado.groupby("Fecha", as_index=False)
        .agg(
            Volumen_Producido_t=("Volumen_Producido_t", "sum"),
            OEE_pct=("OEE_pct", "mean"),
            Yield_pct=("Yield_pct", "mean"),
        )
        .set_index("Fecha")
    )
    st.subheader("OEE y Yield por dia")
    st.line_chart(diario[["OEE_pct", "Yield_pct"]])
    st.subheader("Volumen producido por dia")
    st.bar_chart(diario[["Volumen_Producido_t"]])

with tab2:
    numericas = filtrado.select_dtypes(include=np.number).columns.tolist()
    predeterminadas = [
        campo for campo in [
            "Volumen_Producido_t", "Paros_min", "Horas_Mano_Obra",
            "Energia_kWh", "Merma_pct", "Yield_pct", "OEE_pct",
            "Costo_por_t_MXN"
        ] if campo in numericas
    ]
    seleccion = st.multiselect(
        "Variables para la matriz",
        numericas,
        default=predeterminadas,
        key="variables_correlacion",
    )
    if len(seleccion) >= 2:
        matriz = filtrado[seleccion].corr(numeric_only=True).round(3)
        st.dataframe(matriz, use_container_width=True)
        objetivo = st.selectbox("Variable objetivo", seleccion, key="objetivo_corr")
        relaciones = matriz[objetivo].drop(index=objetivo).sort_values()
        st.subheader(f"Correlaciones con {objetivo}")
        st.bar_chart(relaciones)
    else:
        st.info("Selecciona al menos dos variables numericas.")

with tab3:
    numericas = filtrado.select_dtypes(include=np.number).columns.tolist()
    indice_x = numericas.index("Paros_min") if "Paros_min" in numericas else 0
    indice_y = numericas.index("Volumen_Producido_t") if "Volumen_Producido_t" in numericas else min(1, len(numericas) - 1)
    x_var = st.selectbox("Variable explicativa (X)", numericas, index=indice_x)
    y_var = st.selectbox("Variable objetivo (Y)", numericas, index=indice_y)
    resultado = regresion_numpy(filtrado, x_var, y_var)

    if resultado is None:
        st.info("No hay suficientes datos variables para calcular la regresion.")
    else:
        pendiente, intercepto, r2, mae, grafica = resultado
        met1, met2, met3, met4 = st.columns(4)
        met1.metric("R cuadrada", f"{r2:.3f}")
        met2.metric("MAE", f"{mae:,.3f}")
        met3.metric("Pendiente", f"{pendiente:,.4f}")
        met4.metric("Intercepto", f"{intercepto:,.4f}")
        st.caption(
            f"Ecuacion estimada: {y_var} = {intercepto:.4f} + "
            f"({pendiente:.4f} x {x_var})"
        )
        st.subheader("Dispersion observada")
        st.scatter_chart(grafica, x=x_var, y=y_var)
        st.subheader("Linea de regresion estimada")
        st.line_chart(grafica.set_index(x_var)[["Valor_estimado"]])
        st.caption("El resultado muestra asociacion estadistica exploratoria, no causalidad.")

with tab4:
    st.dataframe(filtrado, use_container_width=True, hide_index=True)
    salida = io.BytesIO()
    filtrado.to_excel(salida, index=False, engine="openpyxl")
    st.download_button(
        "Descargar seleccion en Excel",
        data=salida.getvalue(),
        file_name="eficiencia_filtrada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
