from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

st.set_page_config(page_title='Eficiencia de Producción', page_icon='🏭', layout='wide')
st.title('Eficiencia de Producción | Planta de Alimentos')
st.caption('Análisis descriptivo, correlación y regresión. No incluye optimización Markowitz/Malkowitz.')

BASE = Path(__file__).with_name('base_eficiencia_planta_alimentos.xlsx')
upload = st.sidebar.file_uploader('Cargar archivo Excel', type=['xlsx'])
source = upload if upload is not None else BASE

@st.cache_data
def cargar_excel(archivo):
    return pd.read_excel(archivo, sheet_name='Base_Datos', engine='openpyxl')

df = cargar_excel(source)
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

st.sidebar.header('Filtros')
lineas = st.sidebar.multiselect('Línea', sorted(df['Linea'].dropna().unique()), default=sorted(df['Linea'].dropna().unique()))
turnos = st.sidebar.multiselect('Turno', sorted(df['Turno'].astype(str).dropna().unique()), default=sorted(df['Turno'].astype(str).dropna().unique()))
min_f, max_f = df['Fecha'].min().date(), df['Fecha'].max().date()
rango = st.sidebar.date_input('Rango de fechas', value=(min_f, max_f), min_value=min_f, max_value=max_f)
if len(rango) == 2:
    ini, fin = pd.Timestamp(rango[0]), pd.Timestamp(rango[1])
else:
    ini = fin = pd.Timestamp(rango[0])
flt = df[df['Linea'].isin(lineas) & df['Turno'].astype(str).isin(turnos) & df['Fecha'].between(ini, fin)].copy()

if flt.empty:
    st.warning('No hay registros para los filtros seleccionados.')
    st.stop()

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric('Volumen (t)', f"{flt['Volumen_Producido_t'].sum():,.0f}")
c2.metric('Yield', f"{flt['Yield_pct'].mean():.1%}")
c3.metric('OEE', f"{flt['OEE_pct'].mean():.1%}")
c4.metric('Eficiencia t/hh', f"{flt['Volumen_Producido_t'].sum()/flt['Horas_Mano_Obra'].sum():.3f}")
c5.metric('Costo por t', f"${flt['Costo_Total_MXN'].sum()/flt['Volumen_Producido_t'].sum():,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(['Tendencias','Correlación','Regresión','Base de datos'])
with tab1:
    diario = flt.groupby('Fecha', as_index=False).agg(Volumen_Producido_t=('Volumen_Producido_t','sum'), OEE_pct=('OEE_pct','mean'), Yield_pct=('Yield_pct','mean'))
    st.plotly_chart(px.line(diario, x='Fecha', y=['OEE_pct','Yield_pct'], title='OEE y Yield por día'), use_container_width=True)
    st.plotly_chart(px.bar(flt.groupby('Linea',as_index=False)['Volumen_Producido_t'].sum(), x='Linea', y='Volumen_Producido_t', title='Volumen por línea'), use_container_width=True)
with tab2:
    numericas = flt.select_dtypes(include=np.number).columns.tolist()
    del_default = [c for c in ['Volumen_Producido_t','Paros_min','Horas_Mano_Obra','Energia_kWh','Merma_pct','Yield_pct','OEE_pct','Costo_por_t_MXN'] if c in numericas]
    seleccion = st.multiselect('Variables', numericas, default=del_default)
    if len(seleccion) >= 2:
        corr = flt[seleccion].corr(numeric_only=True)
        fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdYlGn', zmin=-1, zmax=1, aspect='auto', title='Matriz de correlación')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Selecciona al menos dos variables.')
with tab3:
    numericas = flt.select_dtypes(include=np.number).columns.tolist()
    xvar = st.selectbox('Variable explicativa (X)', numericas, index=numericas.index('Paros_min') if 'Paros_min' in numericas else 0)
    yvar = st.selectbox('Variable objetivo (Y)', numericas, index=numericas.index('Volumen_Producido_t') if 'Volumen_Producido_t' in numericas else 1)
    reg = flt[[xvar,yvar]].replace([np.inf,-np.inf],np.nan).dropna()
    if len(reg) >= 3 and reg[xvar].nunique() > 1:
        X=reg[[xvar]].to_numpy(); y=reg[yvar].to_numpy(); model=LinearRegression().fit(X,y); pred=model.predict(X)
        a,b,c = st.columns(3); a.metric('R²',f'{r2_score(y,pred):.3f}'); b.metric('MAE',f'{mean_absolute_error(y,pred):,.3f}'); c.metric('Pendiente',f'{model.coef_[0]:,.4f}')
        fig=px.scatter(reg,x=xvar,y=yvar,trendline='ols',title=f'Regresión lineal: {yvar} vs {xvar}')
        st.plotly_chart(fig,use_container_width=True)
        st.caption('La regresión muestra asociación estadística exploratoria, no causalidad.')
    else:
        st.info('No hay suficientes datos variables para ajustar la regresión.')
with tab4:
    st.dataframe(flt, use_container_width=True, hide_index=True)
    buffer=io.BytesIO(); flt.to_excel(buffer,index=False,engine='openpyxl')
    st.download_button('Descargar selección en Excel',data=buffer.getvalue(),file_name='eficiencia_filtrada.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
