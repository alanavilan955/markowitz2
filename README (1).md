# Dashboard de eficiencia de producción

Aplicación en Streamlit para explorar la eficiencia de una planta de alimentos a partir de una base Excel. Incluye indicadores operativos, filtros, tendencias, matriz de correlación y regresión lineal exploratoria.

> Alcance: el proyecto **no contiene** código de frontera eficiente, Markowitz o Malkowitz, ni rutinas de optimización.

## Archivos

- `base_eficiencia_planta_alimentos.xlsx`: base sintética con 260 registros, diccionario, resumen y correlaciones.
- `app_eficiencia.py`: aplicación Streamlit.
- `requirements.txt`: dependencias.
- `README.md`: instrucciones.

## Variables principales

Volumen programado y producido, materia prima, horas disponibles y productivas, paros, personal, horas-hombre, energía, merma, yield, reproceso, rechazo, utilización, OEE, cumplimiento, eficiencia laboral y costos.

## Ejecución local

```bash
python -m venv .venv
```

Activación en Windows:

```bash
.venv\Scripts\activate
```

Activación en macOS/Linux:

```bash
source .venv/bin/activate
```

Instalación y ejecución:

```bash
pip install -r requirements.txt
streamlit run app_eficiencia.py
```

## Despliegue con GitHub y Streamlit Community Cloud

1. Crea un repositorio en GitHub.
2. Sube los cuatro archivos a la raíz del repositorio.
3. En Streamlit Community Cloud, conecta tu cuenta de GitHub.
4. Selecciona el repositorio, la rama y `app_eficiencia.py` como archivo principal.
5. Despliega la aplicación.

La documentación oficial indica que Community Cloud puede desplegar aplicaciones desde archivos guardados en repositorios de GitHub. Para repositorios privados se requieren permisos adicionales, y para desplegar se requieren permisos administrativos sobre el repositorio.

Documentación: https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account

## Sustitución por datos reales

Conserva los nombres de columnas de la hoja `Base_Datos`. Puedes reemplazar el archivo incluido o cargar otro `.xlsx` desde la barra lateral. Antes de usar resultados para decisiones financieras u operativas, valida unidades, definiciones y reglas de negocio de la planta.

## Nota metodológica

Las correlaciones y regresiones describen asociaciones en los datos. No prueban causalidad. La base incluida es sintética y sirve como plantilla técnica.
