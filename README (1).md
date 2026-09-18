# Dashboard de eficiencia de produccion

Aplicacion Streamlit para analizar una planta de alimentos con indicadores, filtros, tendencias, correlaciones y regresion lineal exploratoria.

## Correccion aplicada

La aplicacion ya no importa `plotly`, `scikit-learn` ni `statsmodels`. La regresion lineal se calcula con NumPy y las graficas se muestran con componentes nativos de Streamlit. Esto elimina los errores `ModuleNotFoundError` observados durante el despliegue.

## Archivos requeridos en GitHub

Los siguientes cuatro archivos deben estar juntos en la raiz del repositorio:

- `app_eficiencia.py`
- `base_eficiencia_planta_alimentos.xlsx`
- `requirements.txt`
- `README.md`

El archivo debe llamarse exactamente `requirements.txt`. No uses `requirements_corregido.txt`, porque Streamlit Community Cloud busca el nombre estandar.

## Ejecucion local

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS o Linux:

```bash
source .venv/bin/activate
```

Instala y ejecuta:

```bash
pip install -r requirements.txt
streamlit run app_eficiencia.py
```

## Despliegue en Streamlit Community Cloud

1. Reemplaza en GitHub los archivos anteriores por los corregidos.
2. Confirma que `requirements.txt` está en la misma carpeta que `app_eficiencia.py`.
3. Configura `app_eficiencia.py` como archivo principal.
4. Reinicia la aplicacion desde la administracion de Streamlit Cloud.

## Alcance

El proyecto no contiene codigo de frontera eficiente, Markowitz/Malkowitz ni rutinas de optimizacion. Las correlaciones y regresiones son exploratorias y no demuestran causalidad. La base incluida es sintetica y debe sustituirse o validarse antes de tomar decisiones operativas o financieras.
